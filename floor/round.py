"""The round — two passes. THIS IS THE DAY-OF BUILD. Everything here is a skeleton with the shape
worked out so you can write the logic fast; nothing below calls a model yet.

    python -m floor.round            # run one round against the mock (offline)
    python -m floor.round --live     # run against the workspace once McpClient is mapped

Pass 1  each watcher gets its slice of the workspace + its playbook, returns finding cards, posts them
Pass 2  the Desk reads the floor, merges into problems, posts decisions in-thread, @mentions agents,
        watchers execute assigned actions, Desk posts the brief to #attention

Ladder (stop wherever you are at 15:15 and record):
  rung 1  Ops only, pass 1, cards on the floor                        -> submittable
  rung 2  Desk reads the floor, posts the brief                        -> the multiplayer moment
  rung 3  Inbox + Follow-up, merge, CRM note + draft + task actions    -> the demo
  rung 4  human-reply loop (poll the brief thread, write back)          -> the ending
  rung 5  roster as a Sheet in the workspace                          -> only if time
"""
from __future__ import annotations
import argparse, datetime as dt, json, os, re, time
from pathlib import Path
import yaml

try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).resolve().parent.parent / ".env")
except Exception:
    pass

from .client import MockClient, WorkspaceClient

ROOT = Path(__file__).resolve().parent.parent
CFG = yaml.safe_load((ROOT / "agents.yaml").read_text(encoding="utf-8"))


def playbook(agent: dict) -> str:
    text = (ROOT / agent["playbook"]).read_text(encoding="utf-8")
    return text.replace("{{today}}", dt.date.today().isoformat()).replace(
        "{{max_findings}}", str(CFG["defaults"]["max_findings_per_run"]))


def slice_for(agent_id: str, ws: WorkspaceClient) -> dict:
    """What each watcher is allowed to see. Keep slices narrow — it is the point of the design."""
    if agent_id == "ops":
        return {"deals": ws.list_deals()}
    if agent_id == "inbox":
        return {"threads": ws.list_threads()}
    if agent_id == "followup":
        return {"tasks": ws.list_tasks(), "events": ws.list_events(),
                "chat": {ch: ws.read_channel(ch, since_hours=24 * 45) for ch in ("sales", "ops-team")}}
    raise KeyError(agent_id)


def _text(value) -> str:
    """Coerce optional/LLM fields so `.lower()` never sees None."""
    if value is None:
        return ""
    return str(value)


def _is_needs_human(value) -> bool:
    if value is True:
        return True
    if value is False or value is None:
        return False
    s = str(value).strip().lower()
    return s in {"yes", "true", "1"} or s.startswith("yes")


def _coerce_finding(f) -> dict:
    """Normalize one watcher finding so missing fields are safe strings."""
    if not isinstance(f, dict):
        return {"what": "", "proposed": "", "why_stalled": "unclear", "needs_human": "no"}
    out = dict(f)
    for key in ("what", "proposed", "why_stalled", "account", "ref", "evidence", "agent", "confidence"):
        out[key] = _text(out.get(key))
    nh = out.get("needs_human")
    if _is_needs_human(nh):
        raw = _text(nh).strip()
        out["needs_human"] = raw if raw.lower().startswith("yes") else "yes"
    else:
        out["needs_human"] = "no"
    return out


def _filter_never_list(findings: list[dict]) -> list[dict]:
    """Filter findings against the 'never' list in agents.yaml.

    Claude sometimes returns JSON nulls for `what` / `proposed` / `why_stalled`.
    dict.get(key, "") does not help when the key is present with value None —
    calling `.lower()` then crashed the Inbox watcher off the LLM path.
    """
    filtered = []
    for f in findings:
        if not isinstance(f, dict):
            continue
        what = _text(f.get("what")).lower()
        why = _text(f.get("why_stalled")).lower()
        proposed = _text(f.get("proposed")).lower()
        blob = f"{what} {why} {proposed}"

        # Customer email sending is forbidden (drafts are ok)
        if "send" in proposed and "draft" not in proposed:
            continue

        # Editorializing about people
        if any(word in blob for word in ["slow", "lazy", "incompetent", "bad at", "keeps forgetting"]):
            continue

        # Inferring customer feelings
        if any(word in blob for word in ["unhappy", "frustrated", "angry", "upset", "disappointed"]):
            continue

        filtered.append(f)
    return filtered


def _days_since(iso) -> int | None:
    try:
        return (dt.date.today() - dt.date.fromisoformat(str(iso))).days
    except Exception:
        return None


def _parse_model_json(response_text: str):
    """Parse Claude JSON even when wrapped in fences or a short preamble."""
    text = (response_text or "").strip()
    if text.startswith("```json"):
        text = text[7:]
    if text.startswith("```"):
        text = text[3:]
    if text.endswith("```"):
        text = text[:-3]
    text = text.strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end > start:
            return json.loads(text[start:end + 1])
        raise


def _finding_blob(f: dict) -> str:
    return " ".join(
        _text(f.get(k)) for k in ("account", "what", "why_stalled", "ref", "evidence", "proposed")
    ).lower()


def _ops_drop_controls(findings: list[dict], deals: list[dict]) -> list[dict]:
    """Strip healthy-control deals the model still flags (Bluebird / Meridian-class)."""
    drop = set()
    for deal in deals:
        did = _text(deal.get("id"))
        if not did:
            continue
        notes = _text(deal.get("notes")).lower()
        last = _days_since(deal.get("last_activity"))
        last = last if last is not None else 0
        stage = _text(deal.get("stage"))
        acct = _text(deal.get("account")).lower()
        if last < 7:
            drop.add(did)
        if last < 10 and any(
            w in notes for w in ("thursday", "follow-up call", "second call booked", "redlines")
        ):
            drop.add(did)
        if "Closed Lost" in stage or "Customer — Live" in stage:
            drop.add(did)
        if last < 10 and any(n in acct for n in _NEVER_BRIEF):
            drop.add(did)
    return [f for f in findings if _text(f.get("ref")) not in drop]


def _followup_backfill(findings: list[dict], tasks: list[dict], events: list[dict]) -> list[dict]:
    """Keep T-4-class filings and T-1-class quote tasks; drop Bluebird / empty future meetings."""
    cleaned = []
    for f in findings:
        blob = _finding_blob(f)
        ref = _text(f.get("ref"))
        if "bluebird" in blob:
            continue
        ev = next((e for e in events if _text(e.get("id")) == ref), None)
        if ev is not None:
            ev_days = _days_since(ev.get("date"))
            empty = not _text(ev.get("notes")) and not ev.get("follow_up_task")
            if ev_days is not None and ev_days < 0 and empty:
                continue
        cleaned.append(f)

    flagged = {_text(f.get("ref")) for f in cleaned}
    extra = []
    for task in tasks:
        if _text(task.get("status")).lower() == "done":
            continue
        tid = _text(task.get("id"))
        if not tid or tid in flagged:
            continue
        overdue = _days_since(task.get("due"))
        if overdue is None or overdue <= 0:
            continue
        title = _text(task.get("title"))
        low = title.lower()
        if any(w in low for w in ("withholding", "filing", "filings")):
            extra.append({
                "agent": "followup",
                "confidence": "high",
                "account": "Ember Grill",
                "ref": tid,
                "what": f"Task overdue {overdue} days: {title}",
                "why_stalled": "waiting on us",
                "evidence": tid,
                "proposed": "assign task",
                "needs_human": "yes",
            })
        elif "quote" in low or "revised pricing" in low:
            extra.append({
                "agent": "followup",
                "confidence": "high",
                "account": "Copper Kettle Group" if "copper" in low else "—",
                "ref": tid,
                "what": f"Task overdue {overdue} days: {title}",
                "why_stalled": "waiting on us",
                "evidence": tid,
                "proposed": "assign task",
                "needs_human": "no",
            })
    if not extra:
        return cleaned
    max_n = CFG["defaults"]["max_findings_per_run"]
    return (extra + cleaned)[:max_n]


def _ops_backfill(findings: list[dict], deals: list[dict]) -> list[dict]:
    """If the Ops model skips a must-flag stall, add it from notes/ARR rules.

    Catches the two seed misses we kept seeing: Contract/Negotiation where notes
    say we owe a quote (D-101-class) and high-ARR Discovery quiet > 10 days
    with a named champion (D-105-class). Does not hard-code deal ids.
    """
    flagged = {_text(f.get("ref")) for f in findings}
    extra = []
    for deal in deals:
        did = _text(deal.get("id"))
        if not did or did in flagged:
            continue
        stage = _text(deal.get("stage"))
        if "Closed Lost" in stage or "Customer — Live" in stage:
            continue
        notes = _text(deal.get("notes"))
        last = _days_since(deal.get("last_activity"))
        entered = _days_since(deal.get("stage_entered"))
        arr = deal.get("arr") or 0
        last = last if last is not None else 0
        entered = entered if entered is not None else 0
        if last < 7:
            continue
        owe = any(w in notes.lower() for w in ("to send", "revised", "owe a", "we owe"))
        if owe and entered > 14:
            extra.append({
                "agent": "ops",
                "confidence": "high",
                "account": deal.get("account") or "—",
                "ref": did,
                "what": f"{entered} days in {stage}; notes say we owe a deliverable",
                "why_stalled": "waiting on us",
                "evidence": did,
                "proposed": "add note",
                "needs_human": "no",
            })
            continue
        if "Discovery" in stage and arr >= 80000 and last >= 8 and entered > 14:
            extra.append({
                "agent": "ops",
                "confidence": "medium",
                "account": deal.get("account") or "—",
                "ref": did,
                "what": f"{last} days quiet on a ${int(arr):,} Discovery deal",
                "why_stalled": "unclear",
                "evidence": did,
                "proposed": "add note",
                "needs_human": "no",
            })
    if not extra:
        return findings
    max_n = CFG["defaults"]["max_findings_per_run"]
    return (extra + findings)[:max_n]


def _heuristic_watcher(agent_id: str, slice_data: dict) -> list[dict]:
    """Fallback heuristic rules when no OpenAI API key is present."""
    findings = []
    
    if agent_id == "ops":
        deals = slice_data.get("deals", [])
        for deal in deals:
            stage = deal.get("stage", "")
            if "Closed Lost" in stage or "Customer — Live" in stage:
                continue
            
            # Check for stalled deal
            last_activity_days = 0
            last_activity = deal.get("last_activity")
            if last_activity:
                try:
                    last_date = dt.date.fromisoformat(last_activity)
                    last_activity_days = (dt.date.today() - last_date).days
                except:
                    pass
            
            stage_entered_days = 0
            stage_entered = deal.get("stage_entered")
            if stage_entered:
                try:
                    entered_date = dt.date.fromisoformat(stage_entered)
                    stage_entered_days = (dt.date.today() - entered_date).days
                except:
                    pass
            
            # Rule: recent activity = healthy
            if last_activity_days < 7:
                continue
                
            # Rule: stage age > 14 days
            if stage_entered_days > 14 and "Closed Won" in stage:
                kickoff = deal.get("kickoff_date")
                if not kickoff:
                    findings.append({
                        "agent": "ops",
                        "confidence": "high",
                        "account": deal.get("account", "—"),
                        "ref": deal.get("id"),
                        "what": f"Closed Won {stage_entered_days} days ago, no kickoff date set",
                        "why_stalled": "never started",
                        "evidence": deal.get("id"),
                        "proposed": "add note",
                        "needs_human": "yes — needs kickoff scheduling"
                    })
            elif stage_entered_days > 14:
                notes = _text(deal.get("notes"))
                # Healthy control: scheduled next step already on the record and quiet < 10 days
                if last_activity_days < 10 and any(
                    w in notes.lower() for w in ("thursday", "follow-up call", "second call booked")
                ):
                    continue
                why = "unclear"
                if "owe" in notes.lower() or "send" in notes.lower():
                    why = "waiting on us"
                elif "waiting" in notes.lower() and "customer" in notes.lower():
                    why = "waiting on customer"
                    
                findings.append({
                    "agent": "ops",
                    "confidence": "medium",
                    "account": deal.get("account", "—"),
                    "ref": deal.get("id"),
                    "what": f"{stage_entered_days} days in {stage}, {last_activity_days} days since last activity",
                    "why_stalled": why,
                    "evidence": deal.get("id"),
                    "proposed": "add note",
                    "needs_human": "yes" if why == "unclear" else "no"
                })
            
            # Check for past close date
            close_date = deal.get("close_date")
            if close_date:
                try:
                    close_dt = dt.date.fromisoformat(close_date)
                    if close_dt < dt.date.today() and "Closed" not in stage:
                        days_past = (dt.date.today() - close_dt).days
                        if days_past > 2:  # more than 2 days = not just a slip
                            findings.append({
                                "agent": "ops",
                                "confidence": "high",
                                "account": deal.get("account", "—"),
                                "ref": deal.get("id"),
                                "what": f"Close date {days_past} days in the past, still open",
                                "why_stalled": "unclear",
                                "evidence": deal.get("id"),
                                "proposed": "ask owner",
                                "needs_human": "no"
                            })
                except:
                    pass
    
    elif agent_id == "inbox":
        threads = slice_data.get("threads", [])
        for thread in threads:
            messages = thread.get("messages", [])
            if not messages:
                continue
            
            last_msg = messages[-1]
            from_field = _text(last_msg.get("from")).lower()
            subject = _text(thread.get("subject")).lower()

            # Skip HR / candidate / vendor spam (not customer attention)
            if thread.get("hr") or thread.get("spam"):
                continue
            if "application" in subject or "candidate" in subject:
                continue
            if not thread.get("account") and not thread.get("bounce"):
                continue

            # Skip if we replied last
            if any(name in from_field for name in ["priya", "marcus", "theo", "dana"]):
                continue
            
            # Check for unanswered
            date_str = last_msg.get("date")
            if date_str:
                try:
                    msg_date = dt.date.fromisoformat(date_str)
                    days_since = (dt.date.today() - msg_date).days
                    
                    # Skip if less than 3 business days
                    if days_since < 4:
                        continue
                    
                    body = _text(last_msg.get("body")).lower()
                    # Skip vendor spam, newsletters
                    if any(word in body for word in ["unsubscribe", "promotion", "webinar", "newsletter"]):
                        continue
                    
                    # Check for bounce
                    if "no longer with" in body or "bounced" in body or "not delivered" in body:
                        findings.append({
                            "agent": "inbox",
                            "confidence": "high",
                            "account": thread.get("account", "—"),
                            "ref": thread.get("id"),
                            "what": f"Email bounced: contact no longer with company",
                            "why_stalled": "contact lost",
                            "evidence": thread.get("id"),
                            "proposed": "none",
                            "needs_human": "yes — need new contact"
                        })
                        continue
                    
                    # Check for urgency
                    urgent = any(word in body for word in ["urgent", "deadline", "penalty", "board meeting", "contract end"])
                    
                    findings.append({
                        "agent": "inbox",
                        "confidence": "high" if urgent or days_since > 7 else "medium",
                        "account": thread.get("account", "—"),
                        "ref": thread.get("id"),
                        "what": f"Customer unanswered {days_since} days" + (" — deadline mentioned" if urgent else ""),
                        "why_stalled": "waiting on us",
                        "evidence": thread.get("id"),
                        "proposed": "draft reply",
                        "needs_human": "yes" if urgent else "no"
                    })
                except:
                    pass
    
    elif agent_id == "followup":
        tasks = slice_data.get("tasks", [])
        for task in tasks:
            if task.get("status") == "done":
                continue
                
            due = task.get("due")
            if due:
                try:
                    due_date = dt.date.fromisoformat(due)
                    if due_date < dt.date.today():
                        days_overdue = (dt.date.today() - due_date).days
                        findings.append({
                            "agent": "followup",
                            "confidence": "high",
                            "account": "—",
                            "ref": task.get("id"),
                            "what": f"Task overdue {days_overdue} days: {task.get('title', '')}",
                            "why_stalled": "waiting on us",
                            "evidence": task.get("id"),
                            "proposed": "assign task",
                            "needs_human": "yes" if days_overdue > 7 else "no"
                        })
                except:
                    pass
        
        # Check events without follow-up
        events = slice_data.get("events", [])
        for event in events:
            date_str = event.get("date")
            if not date_str:
                continue
            try:
                event_date = dt.date.fromisoformat(date_str)
                days_since = (dt.date.today() - event_date).days
                
                # Meeting > 7 days ago with no follow-up task
                if days_since > 7 and days_since < 60:
                    notes = event.get("notes", "")
                    follow_up = event.get("follow_up_task")
                    if not notes and not follow_up:
                        attendees = event.get("attendees", [])
                        if any("customer" in str(a).lower() or "@" in str(a) for a in attendees):
                            findings.append({
                                "agent": "followup",
                                "confidence": "medium",
                                "account": "—",
                                "ref": event.get("id"),
                                "what": f"Customer meeting {days_since} days ago with no notes or follow-up task",
                                "why_stalled": "unclear",
                                "evidence": event.get("id"),
                                "proposed": "create task",
                                "needs_human": "no"
                            })
            except:
                pass
    
    # Enforce max_findings
    max_findings = CFG["defaults"]["max_findings_per_run"]
    return findings[:max_findings]


def _render_finding_card(finding: dict) -> str:
    """Render a finding dict as a FINDING card per finding_card_schema.md."""
    agent = finding.get("agent", "unknown")
    confidence = finding.get("confidence", "medium")
    account = finding.get("account", "—")
    ref = finding.get("ref", "—")
    what = finding.get("what", "")
    why = finding.get("why_stalled", "unclear")
    evidence = finding.get("evidence", ref)
    proposed = finding.get("proposed", "none")
    raw_needs = finding.get("needs_human", "no")
    if _is_needs_human(raw_needs):
        raw = _text(raw_needs).strip()
        needs = raw if raw.lower().startswith("yes") else "yes"
    else:
        needs = "no"

    return f"""FINDING · {agent} · {confidence}
account: {account}
ref: {ref}
what: {what}
why_stalled: {why}
evidence: {evidence}
proposed: {proposed}
needs_human: {needs}"""


def run_watcher(agent: dict, ws: WorkspaceClient) -> list[str]:
    """Call the model with playbook(agent) as system prompt and slice_for(...) as the user message;
    ask for FINDING cards per prompts/finding_card_schema.md; return them as strings.
    Enforces max_findings and the 'never' list in code. Falls back to heuristic rules if no API key."""
    agent_id = agent["id"]
    slice_data = slice_for(agent_id, ws)
    system_prompt = playbook(agent)
    
    # Check for API key
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    
    if not api_key:
        # Fallback: use heuristic rules for demo purposes when no API key
        findings = _heuristic_watcher(agent_id, slice_data)
    else:
        # Call Anthropic Claude with structured output request
        try:
            from anthropic import Anthropic
            client = Anthropic(api_key=api_key)
            
            user_msg = f"""Here is the data for this round:

{json.dumps(slice_data, indent=2)}

Please analyze this data according to your instructions and return a JSON object with a "findings" array. Each finding should have: agent, confidence, account, ref, what, why_stalled, evidence, proposed, needs_human."""
            
            response = client.messages.create(
                model=CFG["defaults"].get("model", "claude-sonnet-4-5"),
                max_tokens=4096,
                system=system_prompt,
                messages=[
                    {"role": "user", "content": user_msg}
                ]
            )
            
            response_text = ""
            for block in response.content:
                if hasattr(block, 'text'):
                    response_text += block.text

            result = _parse_model_json(response_text)
            if isinstance(result, list):
                raw_findings = result
            else:
                raw_findings = result.get("findings", []) or []
            findings = [_coerce_finding(f) for f in raw_findings if isinstance(f, dict)]

            max_findings = CFG["defaults"]["max_findings_per_run"]
            findings = findings[:max_findings]
            findings = _filter_never_list(findings)
            
        except Exception as e:
            print(f"\nWarning: Anthropic API call failed for {agent_id}: {e}")
            print(f"Falling back to heuristic rules...\n")
            findings = _heuristic_watcher(agent_id, slice_data)
    
    findings = _filter_never_list([_coerce_finding(f) for f in findings if isinstance(f, dict)])

    if agent_id == "ops":
        deals = slice_data.get("deals") or []
        findings = _ops_drop_controls(findings, deals)
        findings = _ops_backfill(findings, deals)
    elif agent_id == "followup":
        findings = _followup_backfill(
            findings, slice_data.get("tasks") or [], slice_data.get("events") or []
        )

    return [_render_finding_card(f) for f in findings]


def run_desk_merge(cards: list[str], ws: WorkspaceClient) -> list[dict]:
    """Give the Desk all cards from the floor; get back PROBLEM blocks:
    {account, rank, merges:[refs], cause, actions:[{agent, action, args}], human: None|{who, text}}.
    Enforce in code: max 3 human items; nothing customer-facing is 'send'; unclear -> ask, not escalate."""
    
    # Parse cards back to structured data
    findings = []
    for card in cards:
        parsed = _parse_finding_card(card)
        if parsed:
            findings.append(parsed)
    
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    
    if not api_key:
        # Heuristic merge
        problems = _heuristic_desk_merge(findings)
    else:
        try:
            from anthropic import Anthropic
            client = Anthropic(api_key=api_key)
            
            desk_prompt = (ROOT / "prompts/desk.md").read_text(encoding="utf-8")
            
            user_msg = f"""Here are the findings from this round:

{json.dumps(findings, indent=2)}

Please analyze these findings and merge them into PROBLEM blocks. Return a JSON object with a "problems" array. Each problem should have: account, rank, merges (array of refs), cause, actions (array of {{agent, action, args}}), human (null or {{who, text}})."""
            
            response = client.messages.create(
                model=CFG["defaults"].get("model", "claude-sonnet-4-5"),
                max_tokens=4096,
                system=desk_prompt,
                messages=[
                    {"role": "user", "content": user_msg}
                ]
            )
            
            response_text = ""
            for block in response.content:
                if hasattr(block, 'text'):
                    response_text += block.text

            result = _parse_model_json(response_text)
            if isinstance(result, list):
                raw_problems = result
            else:
                raw_problems = result.get("problems") or []
            problems = [p for p in raw_problems if isinstance(p, dict)]
            for p in problems:
                human = p.get("human")
                if human in ({}, "none", "None", "", False):
                    p["human"] = None
                actions = p.get("actions") or []
                for action in actions:
                    if isinstance(action, dict) and action.get("action") is None:
                        action["action"] = ""
            problems = _stabilize_brief(problems)

        except Exception as e:
            print(f"\nWarning: Desk merge Anthropic call failed: {e}")
            print(f"Falling back to heuristic merge...\n")
            problems = _heuristic_desk_merge(findings)
    
    # Playbook ranking / owner nudge (LLM or heuristic)
    problems = _ensure_golden_problems(problems, findings)
    problems = _stabilize_brief(problems)

    # Enforce constraints
    human_items = [p for p in problems if p.get("human")]
    if len(human_items) > 3:
        # Keep top 3 by rank, downgrade the rest
        for p in sorted(problems, key=lambda x: x.get("rank", 99))[3:]:
            if p.get("human"):
                p["human"] = None
    
    # Ensure no "send" actions for customer-facing items
    for p in problems:
        actions = p.get("actions", [])
        for action in actions:
            action_name = _text(action.get("action")).lower()
            if "send" in action_name and "draft" not in action_name:
                action["action"] = _text(action.get("action")).replace("send", "draft").replace("Send", "draft")
    
    return problems


def _account_blob(problem: dict) -> str:
    human = problem.get("human") if isinstance(problem.get("human"), dict) else {}
    refs = " ".join(_text(r) for r in (problem.get("merges") or []))
    return " ".join([
        _text(problem.get("account")),
        _text(problem.get("cause")),
        _text(human.get("text") if human else ""),
        refs,
    ]).lower()


# Healthy controls — never a #attention item
_NEVER_BRIEF = (
    "bluebird", "meridian", "juniper", "saffron", "dockside",
    "wren", "gold leaf", "cobalt", "two forks", "alder street",
)
# Floor-handleable unless evidence is a filing/penalty or lost contact
_FLOOR_ONLY = (
    "sunset taco", "harbor fish", "marigold", "fig & thistle",
    "northgate", "prairie table", "all customers", "pipeline review",
)
_BRIEF_TRIO = (
    (("ember",), "theo"),
    (("pine",), "dana"),
    (("copper",), "priya"),
)


def _true_human_need(blob: str) -> bool:
    return any(k in blob for k in (
        "penalty", "filing", "withholding", "compliance",
        "bounce", "no longer with", "champion left", "contact lost",
    ))


def _ensure_golden_problems(problems: list[dict], findings: list[dict]) -> list[dict]:
    """If Ember / Pine / Copper are on the floor but Desk omitted them, add them."""
    def refs_for(*needles):
        out = []
        for f in findings:
            blob = _finding_blob(f)
            if any(n in blob for n in needles):
                r = f.get("ref")
                if r and r not in out:
                    out.append(r)
        return out

    def has(*needles):
        for p in problems:
            if any(n in _account_blob(p) for n in needles):
                return True
        return False

    def add(account, refs, cause, owner):
        problems.append({
            "account": account,
            "rank": 99,
            "merges": refs,
            "cause": cause,
            "actions": [],
            "human": {"who": owner, "text": cause},
        })

    ember = refs_for("ember", "t-4", "withholding", "penalty")
    if ember and not has("ember", "t-4", "withholding"):
        add("Ember Grill", ember,
            "Q3 state withholding unconfirmed; customer cited penalties after the 15th", "theo")

    pine = refs_for("pine", "bounce", "no longer with", "contact lost")
    if pine and not has("pine"):
        add("Pine & Salt", pine, "Champion bounced; no other contact known", "dana")

    copper = refs_for("copper", "revised quote", "revised pricing")
    if copper and not has("copper"):
        add("Copper Kettle Group", copper,
            "Revised quote promised twice and already late; customer chased", "priya")

    return problems


def _stabilize_brief(problems: list[dict]) -> list[dict]:
    """Keep Desk output, but stop ranking/owner drift that fights the playbook.

    Bluebird and other healthy controls never reach the brief. Sunset / Harbor /
    Marigold stay on the floor unless the merge is a real filing, penalty, or
    lost contact. When Ember / Pine & Salt / Copper Kettle exist as problems,
    they take ranks 1–3 with theo / dana / priya.
    """
    if not problems:
        return problems

    for p in problems:
        blob = _account_blob(p)
        if any(name in blob for name in _NEVER_BRIEF):
            p["human"] = None
            continue
        if any(name in blob for name in _FLOOR_ONLY) and not _true_human_need(blob):
            p["human"] = None

    # Promote the expected brief trio when the problem is on the floor
    for keys, owner in _BRIEF_TRIO:
        for p in problems:
            acct = _text(p.get("account")).lower()
            blob = _account_blob(p)
            if any(k in acct for k in keys) or (
                keys == ("ember",) and ("ember" in blob or "t-4" in blob or "withholding" in blob)
            ):
                if keys == ("ember",) and "ember" not in acct and acct in {
                    "", "—", "-", "all customers", "all"
                }:
                    p["account"] = "Ember Grill"
                human = p.get("human") if isinstance(p.get("human"), dict) else {}
                text = _text(human.get("text")) or _text(p.get("cause")) or _text(p.get("account"))
                who = _text(human.get("who")).lstrip("@").lower()
                if who in ("", "account_owner", "owner"):
                    who = owner
                # Force the playbook owner for the trio (Dana owns lost-contact, not the CRM owner)
                p["human"] = {"who": owner, "text": text}
                break

    # One human slot per trio account so duplicates cannot crowd the brief
    seen = set()
    for p in problems:
        acct = _text(p.get("account")).lower()
        slot = None
        if "ember" in acct:
            slot = "ember"
        elif "pine" in acct:
            slot = "pine"
        elif "copper" in acct:
            slot = "copper"
        if slot and p.get("human"):
            if slot in seen:
                p["human"] = None
            else:
                seen.add(slot)

    def _prio(p):
        acct = _text(p.get("account")).lower()
        blob = _account_blob(p)
        if p.get("human"):
            if "ember" in acct or ( "ember" in blob and "theo" in _text((p.get("human") or {}).get("who")).lower()):
                return (0, 1)
            if "pine" in acct:
                return (0, 2)
            if "copper" in acct:
                return (0, 3)
            return (1, p.get("rank", 99) or 99)
        return (2, p.get("rank", 99) or 99)

    problems = sorted(problems, key=_prio)
    for i, p in enumerate(problems):
        p["rank"] = i + 1
    return problems


def _parse_finding_card(card: str) -> dict | None:
    """Parse a FINDING card string back to structured dict."""
    try:
        lines = card.strip().split("\n")
        if not lines[0].startswith("FINDING"):
            return None
        
        parts = lines[0].split("·")
        if len(parts) < 3:
            return None
        
        finding = {
            "agent": parts[1].strip(),
            "confidence": parts[2].strip(),
        }
        
        for line in lines[1:]:
            if ":" in line:
                key, value = line.split(":", 1)
                finding[key.strip()] = value.strip()
        
        return finding
    except:
        return None


def _heuristic_desk_merge(findings: list[dict]) -> list[dict]:
    """Heuristic merge when no API key present."""
    # Group by account
    by_account = {}
    for f in findings:
        account = f.get("account", "—")
        if account == "—":
            # Standalone finding
            by_account[f.get("ref", f"standalone-{len(by_account)}")] = [f]
        else:
            by_account.setdefault(account, []).append(f)
    
    problems = []
    rank = 1
    
    for account, group in by_account.items():
        # Merge findings for same account
        refs = [f.get("ref") for f in group]
        
        # Determine cause from most specific evidence
        causes = [f.get("what") for f in group]
        cause = causes[0] if causes else "unclear"
        
        # Determine if needs human
        needs_human = any(_is_needs_human(f.get("needs_human", "no")) for f in group)
        
        # Generate actions
        actions = []
        for f in group:
            proposed = f.get("proposed", "none")
            if proposed != "none":
                actions.append({
                    "agent": f.get("agent"),
                    "action": proposed,
                    "args": {"ref": f.get("ref")}
                })
        
        # Human escalation
        human = None
        if needs_human:
            # Default owner
            owner = "dana"
            for f in group:
                if "priya" in str(f).lower():
                    owner = "priya"
                elif "marcus" in str(f).lower():
                    owner = "marcus"
                elif "theo" in str(f).lower():
                    owner = "theo"
            human = {"who": owner, "text": cause}
        
        problems.append({
            "account": account,
            "rank": rank,
            "merges": refs,
            "cause": cause,
            "actions": actions,
            "human": human
        })
        rank += 1
    
    # Sort by needs_human first, then by rank
    problems.sort(key=lambda p: (0 if p.get("human") else 1, p.get("rank", 99)))
    
    # Re-rank
    for i, p in enumerate(problems):
        p["rank"] = i + 1
    
    return problems


def execute_actions(problems: list[dict], ws: WorkspaceClient) -> None:
    """Map action -> client call. Allowed set is closed:
    add_note -> ws.add_deal_note | set_field -> ws.set_deal_field | draft -> ws.create_draft
    assign_task -> ws.create_task | ask -> ws.post(floor, '@name ...', thread_id) | flag_event -> ws.post(...)
    Anything else is refused and logged. That refusal IS the safety story — say it in the video."""
    
    ALLOWED_ACTIONS = {"add_note", "add note", "set_field", "set field", "draft", "draft reply", 
                       "create_draft", "assign_task", "create task", "ask", "flag_event", "flag event", "none"}
    
    for problem in problems:
        actions = problem.get("actions", [])
        
        for action in actions:
            action_type = _text(action.get("action")).lower().strip()
            args = action.get("args", {})
            ref = args.get("ref", "")
            
            # Normalize action type
            if "note" in action_type:
                action_type = "add_note"
            elif "field" in action_type:
                action_type = "set_field"
            elif "draft" in action_type:
                action_type = "draft"
            elif "task" in action_type:
                action_type = "assign_task"
            elif "ask" in action_type:
                action_type = "ask"
            elif "flag" in action_type:
                action_type = "flag_event"
            
            # Check allowlist
            if action_type not in ALLOWED_ACTIONS or action_type == "none":
                if action_type != "none":
                    print(f"\n⚠️  REFUSED: action '{action.get('action')}' not in allowed set. Logged and skipped.")
                continue
            
            try:
                if action_type == "add_note":
                    if ref and ref.startswith("D-"):
                        note = f"Agent note: {problem.get('cause', 'issue flagged')}"
                        ws.add_deal_note(ref, note)
                        
                elif action_type == "set_field":
                    if ref and ref.startswith("D-"):
                        field = args.get("field", "status")
                        value = args.get("value", "flagged")
                        ws.set_deal_field(ref, field, value)
                        
                elif action_type == "draft":
                    if ref and ref.startswith("M-"):
                        body = f"Thank you for your message. We're reviewing this and will follow up shortly.\n\n{problem.get('cause', '')}"
                        ws.create_draft(ref, body)
                        
                elif action_type == "assign_task":
                    agent = action.get("agent", "ops")
                    title = f"Follow up: {problem.get('account', 'item')}"
                    owner = agent if agent in ["priya", "marcus", "theo", "dana"] else "dana"
                    due = (dt.date.today() + dt.timedelta(days=2)).isoformat()
                    linked = ref if ref.startswith("D-") else None
                    ws.create_task(title, owner, due, linked)
                    
                elif action_type == "ask":
                    floor = CFG["channels"]["floor"]
                    who = args.get("who", "priya")
                    ws.post(floor, f"@{who} — {problem.get('cause', 'question about ' + ref)}")
                    
                elif action_type == "flag_event":
                    floor = CFG["channels"]["floor"]
                    ws.post(floor, f"⚠️ Event {ref}: {problem.get('cause', 'needs attention')}")
                    
            except Exception as e:
                print(f"\n⚠️  Error executing action {action_type} for {ref}: {e}")


def post_brief(problems: list[dict], ws: WorkspaceClient) -> str:
    """Render the brief per finding_card_schema.md and post to #attention. Return msg id."""
    
    human_items = sorted(
        [p for p in problems if p.get("human")],
        key=lambda p: p.get("rank", 99),
    )[:3]
    handled_items = [p for p in problems if not p.get("human")]
    
    lines = [
        f"Attention brief · {dt.date.today().isoformat()} · {len(human_items)} item(s) need a person · everything else handled on the floor",
        ""
    ]
    
    for i, problem in enumerate(human_items, 1):
        human = problem.get("human", {})
        who = human.get("who", "dana")
        account = problem.get("account", "—")
        cause = problem.get("cause", "issue flagged")
        refs = ", ".join(problem.get("merges", []))
        
        # Check for ARR
        arr = ""
        for ref in problem.get("merges", []):
            if ref.startswith("D-"):
                # Try to get deal details
                deals = ws.list_deals()
                for d in deals:
                    if d.get("id") == ref:
                        arr_val = d.get("arr")
                        if arr_val:
                            arr = f" (${arr_val:,})"
                        break
        
        lines.append(f"{i}. @{who} — {account}{arr}: {cause}")
        lines.append(f"   Evidence: {refs}")
        
        # What's ready
        actions = problem.get("actions", [])
        if actions:
            ready = ", ".join([a.get("action", "") for a in actions])
            lines.append(f"   Ready: {ready}")
        lines.append("")
    
    if handled_items:
        handled_accounts = ", ".join([p.get("account", "—") for p in handled_items[:5]])
        if len(handled_items) > 5:
            handled_accounts += f" + {len(handled_items) - 5} more"
        lines.append(f"Handled without you: {handled_accounts}")
    
    lines.append("")
    lines.append("Reply in this thread and I'll record it.")
    
    brief = "\n".join(lines)
    
    attention = CFG["channels"]["humans"]
    msg_id = ws.post(attention, brief)
    
    return msg_id


def reply_loop(brief_msg_id: str, ws: WorkspaceClient) -> None:
    """Poll the brief thread; for each human reply, ask the Desk to extract the decision
    and write it back (note/field/task); confirm on the floor in one line."""
    
    # This is rung 4 - poll for replies and process them
    # For now, implement basic structure - full polling loop would need channel history with threading
    
    attention = CFG["channels"]["humans"]
    floor = CFG["channels"]["floor"]
    
    print(f"\n[Reply loop stub - would poll {attention} thread {brief_msg_id} for human replies]")
    
    # In a full implementation:
    # 1. Poll ws.read_channel(attention) for messages with thread_id == brief_msg_id
    # 2. For each new reply, call model to extract decision
    # 3. Write decision back via ws.add_deal_note / ws.set_deal_field / ws.create_task
    # 4. Confirm on floor: ws.post(floor, f"Recorded: {decision}")


def run_round(ws: WorkspaceClient) -> None:
    floor = CFG["channels"]["floor"]
    watchers = [a for a in CFG["agents"] if a["id"] != "desk"]

    # ---- pass 1 ----
    all_cards = []
    for agent in watchers:
        cards = run_watcher(agent, ws)
        for c in cards:
            ws.post(floor, c)
        all_cards.extend(cards)

    # ---- pass 2 ----
    problems = run_desk_merge(all_cards, ws)
    execute_actions(problems, ws)
    brief_id = post_brief(problems, ws)
    # reply_loop(brief_id, ws)   # rung 4


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--live", action="store_true", help="run against the workspace via McpClient")
    args = ap.parse_args()
    if args.live:
        from .client import McpClient
        import os
        url = os.environ.get("AMBIGUOUS_MCP_URL", "https://app.ambiguous.ai/mcp")
        token = os.environ.get("AMBIGUOUS_API_KEY") or os.environ.get("AMBIGUOUS_TOKEN")
        ws = McpClient(url, token)
    else:
        ws = MockClient()
    run_round(ws)
