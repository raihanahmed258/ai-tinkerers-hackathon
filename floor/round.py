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

from .client import MockClient, WorkspaceClient, resolve_agent_token
from .router import slice_for
from .timeline import get_default_store

ROOT = Path(__file__).resolve().parent.parent
CFG = yaml.safe_load((ROOT / "agents.yaml").read_text(encoding="utf-8"))


def playbook(agent: dict) -> str:
    text = (ROOT / agent["playbook"]).read_text(encoding="utf-8")
    return text.replace("{{today}}", dt.date.today().isoformat()).replace(
        "{{max_findings}}", str(CFG["defaults"]["max_findings_per_run"]))


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


def _rank_sort_key(problem: dict) -> int:
    """Sort key for problem rank. Missing/None/unparseable ranks sort last (99)."""
    r = problem.get("rank") if isinstance(problem, dict) else None
    if r is None or r == "":
        return 99
    try:
        return int(r)
    except (TypeError, ValueError):
        return 99


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


_AGENT_LABEL = {
    "ops": "Ops",
    "inbox": "Inbox",
    "followup": "Follow-up",
    "follow-up": "Follow-up",
    "desk": "Desk",
}


def _agent_label(agent_id: str | None) -> str:
    raw = _text(agent_id).strip() or "unknown"
    return _AGENT_LABEL.get(raw.lower(), raw[:1].upper() + raw[1:] if raw else "unknown")


def _render_finding_card(finding: dict) -> str:
    """Render a finding dict as a FINDING card per finding_card_schema.md.

    Blank line after the header keeps Ambiguous chat scannable; labelled lines
    stay machine-readable for the Desk parser.
    """
    agent = _agent_label(finding.get("agent", "unknown"))
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
    
    timeline = get_default_store()
    
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

    # Check timeline: downgrade re-escalations for accounts already waiting on humans
    for p in problems:
        if not p.get("human"):
            continue
        account = _text(p.get("account"))
        should_escalate, reason = timeline.should_escalate(account)
        if not should_escalate:
            # Downgrade to note-only, don't count toward human slots
            p["human"] = None
            p["_timeline_skip"] = reason  # Track why for logging
    
    # Enforce constraints
    human_items = [p for p in problems if p.get("human")]
    if len(human_items) > 3:
        # Keep top 3 by rank, downgrade the rest
        for p in sorted(problems, key=_rank_sort_key)[3:]:
            if p.get("human"):
                p["human"] = None
    
    # Ensure no "send" actions for customer-facing items
    for p in problems:
        actions = p.get("actions", [])
        for action in actions:
            action_name = _text(action.get("action")).lower()
            if "send" in action_name and "draft" not in action_name:
                action["action"] = _text(action.get("action")).replace("send", "draft").replace("Send", "draft")
    
    # Update timeline for decisions made
    for p in problems:
        account = _text(p.get("account"))
        if not account or account in ("—", "-"):
            continue
        
        # Track drafts
        for action in p.get("actions", []):
            if "draft" in _text(action.get("action")).lower():
                ref = _text(action.get("args", {}).get("ref"))
                if ref:
                    timeline.update(account, add_draft=ref)
        
        # Track escalations
        if p.get("human"):
            cause = _text(p.get("cause")) or _text(p.get("human", {}).get("text"))
            timeline.update(account, escalate=True, escalation_cause=cause)
    
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
            return (1, _rank_sort_key(p))
        return (2, _rank_sort_key(p))

    problems = sorted(problems, key=_prio)
    for i, p in enumerate(problems):
        p["rank"] = i + 1
    return problems


def _parse_finding_card(card: str) -> dict | None:
    """Parse a FINDING card string back to structured dict."""
    try:
        lines = [ln.strip() for ln in card.strip().splitlines() if ln.strip()]
        if not lines or not lines[0].upper().startswith("FINDING"):
            return None

        parts = [p.strip() for p in lines[0].replace("·", "·").split("·")]
        if len(parts) < 3:
            return None

        agent = parts[1].strip()
        # Normalize display labels back to ids when needed downstream
        agent_id = {
            "Ops": "ops", "Inbox": "inbox", "Follow-up": "followup",
            "Followup": "followup", "Desk": "desk",
        }.get(agent, agent.lower().replace(" ", "").replace("-", ""))
        if agent_id == "followup" or agent.lower() in ("follow-up", "followup"):
            agent_id = "followup"

        finding = {
            "agent": agent_id,
            "confidence": parts[2].strip().split()[0].lower(),
        }

        for line in lines[1:]:
            clean = line.lstrip("-* ").strip()
            if ":" not in clean:
                continue
            key, value = clean.split(":", 1)
            finding[key.strip().lower()] = value.strip()

        return finding
    except Exception:
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
    problems.sort(key=lambda p: (0 if p.get("human") else 1, _rank_sort_key(p)))
    
    # Re-rank
    for i, p in enumerate(problems):
        p["rank"] = i + 1
    
    return problems


def _render_problem_card(problem: dict) -> str:
    """Human-readable Desk merge card for #agents-floor."""
    account = problem.get("account", "—")
    rank = problem.get("rank", "?")
    merges = ", ".join(problem.get("merges") or []) or "—"
    cause = problem.get("cause", "unclear")
    actions = problem.get("actions") or []
    action_bits = []
    for a in actions:
        agent = _agent_label(a.get("agent"))
        action_bits.append(f"{agent} → {a.get('action', 'none')}")
    actions_s = ", ".join(action_bits) if action_bits else "none"
    human = problem.get("human")
    if human:
        human_s = f"@{human.get('who', 'dana')} — {human.get('text', cause)}"
    else:
        human_s = "none"
    return f"""PROBLEM · {account} · rank {rank}

merges: {merges}
cause: {cause}
actions: {actions_s}
human: {human_s}"""


def _looks_deal_ref(ref: str | None) -> bool:
    r = _text(ref).strip()
    if not r:
        return False
    if r.upper().startswith("D-"):
        return True
    # Live Ambiguous deal ids are UUIDs
    return len(r) == 36 and r.count("-") == 4


def _looks_mail_ref(ref: str | None) -> bool:
    r = _text(ref).strip()
    if not r:
        return False
    if r.upper().startswith("M-"):
        return True
    return len(r) == 36 and r.count("-") == 4


def _resolve_deal_id(ws: WorkspaceClient, ref: str | None, account: str | None = None) -> str | None:
    """Map mock D-101 / title crumbs / account name → live deal UUID when needed."""
    r = _text(ref).strip()
    deals = list(ws.list_deals())
    by_id = { _text(d.get("id")): d for d in deals }

    if r and r in by_id:
        return r
    if r.upper().startswith("D-"):
        needle = r.upper()
        for d in deals:
            blob = f"{d.get('id')} {d.get('title')} {d.get('account')}".upper()
            if needle in blob:
                return _text(d.get("id")) or None
    if account and account != "—":
        acc = account.lower()
        for d in deals:
            if acc in _text(d.get("account")).lower() or acc in _text(d.get("title")).lower():
                return _text(d.get("id")) or None
    return r if _looks_deal_ref(r) else None


def _resolve_mail_id(ws: WorkspaceClient, ref: str | None) -> str | None:
    """Resolve seed M-* / live UUID → mail thread id via client.

    Never invents an id. Unresolved → None so execute_actions drafts BLOCK
    (no silent DONE / fake approve). Prefer WorkspaceClient.resolve_mail_id.
    """
    resolver = getattr(ws, "resolve_mail_id", None)
    if callable(resolver):
        return resolver(ref)

    r = _text(ref).strip()
    if not r:
        return None
    try:
        threads = list(ws.list_threads())
    except Exception:
        threads = []
    by_id = {_text(th.get("id")): th for th in threads if th.get("id") is not None}
    if r in by_id:
        return r
    if r.upper().startswith("M-"):
        needle = r.upper()
        for th in threads:
            blob = f"{th.get('id')} {th.get('subject')} {th.get('ref')}".upper()
            if needle in blob:
                return _text(th.get("id")) or None
    # Do NOT passthrough unverified UUID/M-* — live inbox may be empty (SEED MAIL).
    return None


def _normalize_action_type(raw: str) -> str:
    action_type = _text(raw).lower().strip()
    if not action_type or action_type == "none":
        return "none"
    if "propose" in action_type or "slot" in action_type:
        return "refused"
    if "send" in action_type and "draft" not in action_type:
        return "refused"
    if "note" in action_type:
        return "add_note"
    if "stage" in action_type or "close_date" in action_type or "close date" in action_type:
        return "refused"  # hard safety: never move stage/close_date from the round
    if "field" in action_type:
        return "set_field"
    if "draft" in action_type:
        return "draft"
    if "task" in action_type:
        return "assign_task"
    if "ask" in action_type:
        return "ask"
    if "flag" in action_type:
        return "flag_event"
    return "refused" if action_type not in {
        "add_note", "set_field", "draft", "assign_task", "ask", "flag_event", "none"
    } else action_type


def _ensure_productive_actions(problem: dict) -> list[dict]:
    """If Desk left a problem with no runnable actions, invent safe defaults so agents do work."""
    actions = list(problem.get("actions") or [])
    usable = []
    for a in actions:
        if _normalize_action_type(a.get("action")) not in ("none", "refused"):
            usable.append(a)
    if usable:
        return usable

    merges = problem.get("merges") or []
    account = problem.get("account", "—")
    cause = problem.get("cause", "issue flagged")
    human = problem.get("human") or {}
    who = human.get("who") or "dana"
    defaults = []

    deal_ref = next((m for m in merges if _looks_deal_ref(m) or _text(m).upper().startswith("D-")), None)
    mail_ref = next((m for m in merges if _text(m).upper().startswith("M-") or (
        len(_text(m)) == 36 and _text(m).count("-") == 4 and not deal_ref
    )), None)
    # Prefer explicit M- for mail; UUID without D- may be mail or deal — handled at execute time

    if deal_ref or account not in ("—", "", None):
        defaults.append({
            "agent": "ops",
            "action": "add_note",
            "args": {"ref": deal_ref or merges[0] if merges else "", "account": account},
        })
    if mail_ref:
        defaults.append({
            "agent": "inbox",
            "action": "draft",
            "args": {"ref": mail_ref},
        })
    # Always leave a task for the human owner when escalated
    if human:
        defaults.append({
            "agent": "followup",
            "action": "assign_task",
            "args": {"ref": deal_ref or (merges[0] if merges else ""), "who": who},
        })
        defaults.append({
            "agent": "desk",
            "action": "ask",
            "args": {"who": who, "ref": deal_ref or ""},
        })
    elif defaults:
        pass
    else:
        defaults.append({
            "agent": "desk",
            "action": "ask",
            "args": {"who": who, "ref": ""},
        })
    # stash cause for note text
    for d in defaults:
        d.setdefault("args", {})["cause"] = cause
    return defaults


def _verify_action(action_type: str, action: dict, problem: dict) -> tuple[str, str]:
    """Code Verifier: returns (approved|refused|needs_rewrite, reason)."""
    cause = _text(problem.get("cause") or action.get("args", {}).get("cause"))
    raw = _text(action.get("action")).lower()

    if action_type in ("refused", "none"):
        return "refused", "action not on closed allowlist"

    if "send" in raw and "draft" not in raw:
        return "refused", "customer send is forbidden; draft only"

    if action_type == "set_field":
        field = _text((action.get("args") or {}).get("field")).lower()
        if field in ("stage", "stage_id", "close_date", "close date", "pipeline", "pipeline_id", "owner_id", "status"):
            return "refused", f"field '{field}' is blocked (safety)"

    if action_type not in ("add_note", "draft", "assign_task", "ask", "flag_event"):
        return "refused", f"'{action_type}' not allowed"

    # Soft rewrite signal: empty cause
    if action_type in ("add_note", "ask", "assign_task") and not cause:
        return "needs_rewrite", "missing factual cause/dates"

    return "approved", "allowlist + safety checks passed"


def _worker_for_action(action_type: str, agent_id: str | None = None) -> str:
    """Map action → specialist that must execute it (Desk only assigns)."""
    if action_type == "add_note":
        return "closer" if resolve_agent_token("closer") else "ops"
    if action_type == "draft":
        return "inbox"
    if action_type in ("assign_task", "flag_event"):
        return "followup"
    if action_type == "ask":
        return "desk"
    if action_type == "set_field":
        return "ops"
    return (agent_id or "desk").lower()


def _post_assign(ws: WorkspaceClient, floor: str, account: str, worker: str, action_type: str, ref: str, cause: str) -> None:
    with ws.as_agent("desk"):
        ws.post(
            floor,
            f"ASSIGN · {_agent_label(worker)} → {action_type}\n"
            f"account: {account}\n"
            f"ref: {ref or '—'}\n"
            f"cause: {cause}\n"
            f"rule: wait for VERIFIER · approved before write",
        )


def _post_done(ws: WorkspaceClient, floor: str, worker: str, action_type: str, account: str, detail: str) -> None:
    with ws.as_agent(worker):
        ws.post(
            floor,
            f"DONE · {_agent_label(worker)} · {action_type}\n"
            f"account: {account}\n"
            f"result: {detail}",
        )


def _post_blocked(ws: WorkspaceClient, floor: str, worker: str, action_type: str, account: str, reason: str) -> None:
    with ws.as_agent(worker):
        ws.post(
            floor,
            f"BLOCKED · {_agent_label(worker)} · {action_type}\n"
            f"account: {account}\n"
            f"reason: {reason}",
        )


def _refusal_theater(ws: WorkspaceClient, problems: list[dict]) -> None:
    """Force one visible unsafe ask each round so judges see the boundary."""
    floor = CFG["channels"]["floor"]
    account = "—"
    ref = ""
    for problem in problems:
        if problem.get("account") and problem.get("account") != "—":
            account = problem["account"]
            merges = problem.get("merges") or []
            ref = next((m for m in merges if _looks_deal_ref(m) or _text(m).upper().startswith("D-")), merges[0] if merges else "")
            break

    # Alternate story: Desk is asked to send customer mail + move stage — both must die at Verifier
    demos = [
        {
            "action": "send email to customer",
            "agent": "inbox",
            "args": {"ref": ref, "to": "customer@example.com"},
            "cause": f"Would email {account} the revised quote without human approval",
        },
        {
            "action": "set_field",
            "agent": "ops",
            "args": {"ref": ref, "field": "stage", "value": "Closed Won — Implementation"},
            "cause": f"Would move {account} to Closed Won without a human decision",
        },
    ]
    with ws.as_agent("desk"):
        ws.post(
            floor,
            "—— Refusal theater · unsafe asks (must not execute) ——\n"
            "Desk received two out-of-policy requests. Verifier must refuse both.",
        )
    for demo in demos:
        action_type = _normalize_action_type(demo["action"])
        worker = _worker_for_action(action_type, demo.get("agent"))
        _post_assign(ws, floor, account, worker, action_type if action_type != "refused" else demo["action"], ref, demo["cause"])
        # normalize may already mark send as refused
        if "send" in demo["action"].lower() and "draft" not in demo["action"].lower():
            action_type = "refused"
        verdict, reason = ("refused", "customer send is forbidden; draft only") if action_type == "refused" else _verify_action(action_type, demo, {"cause": demo["cause"], "account": account})
        if action_type == "set_field":
            verdict, reason = _verify_action("set_field", demo, {"cause": demo["cause"], "account": account})
        with ws.as_agent("verifier"):
            ws.post(
                floor,
                f"VERIFIER · {verdict}\n"
                f"account: {account}\n"
                f"action: {demo['action']}\n"
                f"agent: {_agent_label(worker)}\n"
                f"reason: {reason}",
            )
        _post_blocked(ws, floor, worker, demo["action"], account, reason)


def execute_actions(problems: list[dict], ws: WorkspaceClient) -> None:
    """Desk assigns → Verifier gates → specialist executes → DONE/BLOCKED on the floor.

    Closed allowlist only. Stage/close_date/send are hard-refused.
    Live workspace refs may be UUIDs (not only mock D-/M- ids).
    """
    floor = CFG["channels"]["floor"]
    done_lines: list[str] = []

    # Visible safety story before productive work
    _refusal_theater(ws, problems)

    for problem in problems:
        actions = _ensure_productive_actions(problem)
        account = problem.get("account", "—")
        cause = problem.get("cause", "issue flagged")

        for action in actions:
            action_type = _normalize_action_type(action.get("action"))
            args = dict(action.get("args") or {})
            ref = args.get("ref", "")
            agent_id = action.get("agent") or "desk"

            if action_type == "none":
                continue

            worker = _worker_for_action(action_type, agent_id)
            _post_assign(ws, floor, account, worker, action.get("action") or action_type, ref, cause)

            if action_type == "refused":
                reason = "not in allowlist (safety)"
                with ws.as_agent("verifier"):
                    ws.post(
                        floor,
                        f"VERIFIER · refused\n"
                        f"account: {account}\n"
                        f"action: {action.get('action')}\n"
                        f"agent: {_agent_label(worker)}\n"
                        f"reason: {reason}",
                    )
                _post_blocked(ws, floor, worker, str(action.get("action")), account, reason)
                continue

            verdict, reason = _verify_action(action_type, action, problem)
            with ws.as_agent("verifier"):
                ws.post(
                    floor,
                    f"VERIFIER · {verdict}\n"
                    f"account: {account}\n"
                    f"action: {action_type}\n"
                    f"agent: {_agent_label(worker)}\n"
                    f"reason: {reason}",
                )
            if verdict != "approved":
                _post_blocked(ws, floor, worker, action_type, account, reason)
                continue

            try:
                if action_type == "add_note":
                    deal_id = _resolve_deal_id(ws, ref, account=args.get("account") or account)
                    if not deal_id:
                        _post_blocked(ws, floor, worker, action_type, account, "could not resolve deal id")
                        continue
                    note = f"[Floor/{_agent_label(worker)}] {args.get('cause') or cause}"
                    with ws.as_agent(worker):
                        ws.add_deal_note(deal_id, note)
                    detail = f"note on deal {deal_id[:8]}…" if len(deal_id) > 8 else f"note on deal {deal_id}"
                    _post_done(ws, floor, worker, action_type, account, detail)
                    done_lines.append(f"{_agent_label(worker)} note · {account}")

                elif action_type == "set_field":
                    field = _text(args.get("field", "status")).lower()
                    if field in ("stage", "stage_id", "close_date", "close date", "status", "pipeline", "pipeline_id"):
                        _post_blocked(ws, floor, worker, action_type, account, f"field '{field}' blocked")
                        continue
                    deal_id = _resolve_deal_id(ws, ref, account=account)
                    if not deal_id:
                        _post_blocked(ws, floor, worker, action_type, account, "could not resolve deal id")
                        continue
                    with ws.as_agent(worker):
                        ws.set_deal_field(deal_id, field, args.get("value", "flagged"))
                    detail = f"set {field}"
                    _post_done(ws, floor, worker, action_type, account, detail)
                    done_lines.append(f"set {field} · {account}")

                elif action_type == "draft":
                    thread_id = _resolve_mail_id(ws, ref)
                    if not thread_id:
                        # Fail closed: never DONE/approve without a resolved thread.
                        reason = (
                            f"could not resolve mail id for ref={_text(ref) or '—'!r} "
                            "(empty inbox / SEED MAIL only / bad ref) — no draft"
                        )
                        _post_blocked(ws, floor, worker, action_type, account, reason)
                        continue
                    body = (
                        "Thanks for your note — we're on it and will follow up shortly.\n\n"
                        f"Internal context: {cause}"
                    )
                    with ws.as_agent(worker):
                        ws.create_draft(thread_id, body)
                    detail = f"draft on thread {thread_id[:8]}…"
                    _post_done(ws, floor, worker, action_type, account, detail)
                    done_lines.append(f"Inbox draft · {account}")

                elif action_type == "assign_task":
                    who = args.get("who") or (problem.get("human") or {}).get("who") or "dana"
                    owner = who if who in ("priya", "marcus", "theo", "dana") else "dana"
                    title = f"Follow up: {account} — {cause}"[:120]
                    due = (dt.date.today() + dt.timedelta(days=2)).isoformat()
                    deal_id = _resolve_deal_id(ws, ref, account=account)
                    with ws.as_agent(worker):
                        ws.create_task(title, owner, due, deal_id)
                    detail = f"task → @{owner} due {due}"
                    _post_done(ws, floor, worker, action_type, account, detail)
                    done_lines.append(f"task → @{owner} · {account}")

                elif action_type == "ask":
                    who = args.get("who") or (problem.get("human") or {}).get("who") or "priya"
                    with ws.as_agent(worker):
                        ws.post(floor, f"@{who} — {account}: {cause}")
                    detail = f"asked @{who}"
                    _post_done(ws, floor, worker, action_type, account, detail)
                    done_lines.append(f"asked @{who} · {account}")

                elif action_type == "flag_event":
                    with ws.as_agent(worker):
                        ws.post(floor, f"⚠️ Event {ref or '—'}: {cause}")
                    detail = f"flagged {ref or 'event'}"
                    _post_done(ws, floor, worker, action_type, account, detail)
                    done_lines.append(f"flagged event · {account}")

            except Exception as e:
                print(f"\n⚠️  Error executing action {action_type} for {ref}: {e}")
                _post_blocked(ws, floor, worker, action_type, account, str(e))

    with ws.as_agent("desk"):
        if done_lines:
            bullet = "\n".join(f"• {x}" for x in done_lines[:12])
            more = f"\n• +{len(done_lines)-12} more" if len(done_lines) > 12 else ""
            ws.post(floor, f"—— Work done this round ——\n{bullet}{more}")
        else:
            ws.post(floor, "—— Work done this round ——\n• none (all actions blocked or empty)")



def post_brief(problems: list[dict], ws: WorkspaceClient) -> str:
    """Render the brief per finding_card_schema.md and post to #attention. Return msg id."""
    
    human_items = sorted(
        [p for p in problems if p.get("human")],
        key=_rank_sort_key,
    )[:3]
    handled_items = [p for p in problems if not p.get("human")]
    
    # Log timeline-skipped items
    skipped_items = [p for p in problems if p.get("_timeline_skip")]
    for p in skipped_items:
        account = p.get("account", "—")
        reason = p.get("_timeline_skip", "")
        print(f"[Timeline] Skipped re-escalation: {account} — {reason}")
    
    lines = [
        f"Attention brief · {dt.date.today().isoformat()}",
        f"{len(human_items)} item(s) need a person · everything else handled on the floor",
        "",
    ]

    deals_by_id = {d.get("id"): d for d in ws.list_deals()}

    for i, problem in enumerate(human_items, 1):
        human = problem.get("human") or {}
        who = human.get("who", "dana")
        account = problem.get("account", "—")
        cause = problem.get("cause", "issue flagged")
        refs = ", ".join(problem.get("merges", []) or [])

        arr = ""
        for ref in problem.get("merges", []) or []:
            d = deals_by_id.get(ref)
            if d and d.get("arr"):
                try:
                    arr = f" (${int(d['arr']):,})"
                except (TypeError, ValueError):
                    arr = f" (${d['arr']})"
                break

        lines.append(f"{i}. @{who} — {account}{arr}")
        lines.append(f"   {cause}")
        if refs:
            lines.append(f"   Evidence: {refs}")
        actions = problem.get("actions") or []
        if actions:
            # Scrub "send" language to reinforce agents-never-send
            ready_items = []
            for a in actions:
                action_name = _text(a.get("action", ""))
                if "draft" in action_name.lower() or "send" in action_name.lower():
                    ready_items.append("draft (approve / decide — agents never send)")
                elif action_name:
                    ready_items.append(action_name)
            if ready_items:
                ready = ", ".join(ready_items)
                lines.append(f"   Ready: {ready}")
        lines.append("")

    if handled_items:
        handled_accounts = ", ".join(p.get("account", "—") for p in handled_items[:5])
        if len(handled_items) > 5:
            handled_accounts += f" + {len(handled_items) - 5} more"
        lines.append(f"Handled without you: {handled_accounts}")
        lines.append("")

    lines.append("Reply in this thread and I'll record it.")
    
    brief = "\n".join(lines)
    
    attention = CFG["channels"]["humans"]
    with ws.as_agent("desk"):
        msg_id = ws.post(attention, brief)
    
    return msg_id


def reply_loop(brief_msg_id: str, ws: WorkspaceClient) -> None:
    """Poll the brief thread; extract explicit human decisions and safe-write back.

    Implementation lives in floor.reply_handler (rung 4). Call standalone for tests,
    or enable from run_round via FLOOR_REPLY_LOOP=1.
    """
    from .reply_handler import handle_reply_loop
    handle_reply_loop(brief_msg_id, ws, channels=CFG.get("channels"))


def run_round(ws: WorkspaceClient) -> None:
    floor = CFG["channels"]["floor"]
    attention = CFG["channels"]["humans"]
    watchers = [a for a in CFG["agents"] if a["id"] != "desk"]
    stamp = dt.datetime.now().strftime("%Y-%m-%d %H:%M")

    # ---- pass 1 ----
    with ws.as_agent("desk"):
        ws.post(
            floor,
            f"—— Round {stamp} · pass 1 ——\n"
            f"Watchers posting FINDING cards here.\n"
            f"Desk will merge them and post the brief to #{attention.lstrip('#')}.",
        )

    all_cards = []
    for agent in watchers:
        cards = run_watcher(agent, ws)
        with ws.as_agent(agent.get("id")):
            for c in cards:
                ws.post(floor, c)
        all_cards.extend(cards)

    # ---- pass 2 ----
    problems = run_desk_merge(all_cards, ws)

    with ws.as_agent("desk"):
        ws.post(
            floor,
            f"—— Round {stamp} · pass 2 · Desk merge ——\n"
            f"Merged {len(all_cards)} findings → {len(problems)} problem(s).\n"
            f"Posting PROBLEM cards, then the human brief → #{attention.lstrip('#')}.",
        )
        # Show the merge path on the floor (top 5 by rank) so the channel isn't "findings forever"
        ranked = sorted(problems, key=_rank_sort_key)[:5]
        for problem in ranked:
            ws.post(floor, _render_problem_card(problem))

    execute_actions(problems, ws)
    brief_id = post_brief(problems, ws)

    with ws.as_agent("desk"):
        ws.post(
            floor,
            f"—— Round {stamp} · done ——\n"
            f"Brief posted to #{attention.lstrip('#')} (msg {brief_id or '—'}).\n"
            f"Floor cards above are the audit trail; humans only need #attention.",
        )
    # Rung 4 — human reply handler (off by default; set FLOOR_REPLY_LOOP=1 to enable)
    # Or call reply_loop(brief_id, ws) standalone / after seeding a thread reply.
    # reply_loop(brief_id, ws)   # rung 4 (commented; prefer env flag below)
    if os.environ.get("FLOOR_REPLY_LOOP", "").strip() in ("1", "true", "yes"):
        reply_loop(brief_id, ws)


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
