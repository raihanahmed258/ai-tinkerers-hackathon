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


def _filter_never_list(findings: list[dict]) -> list[dict]:
    """Filter findings against the 'never' list in agents.yaml."""
    never_rules = CFG["defaults"]["never"]
    filtered = []
    for f in findings:
        # Check if finding violates any never rule
        what = f.get("what", "").lower()
        reason = f.get("why_stalled", "").lower()
        
        # Check for customer email sending (drafts are ok)
        if "send" in f.get("proposed", "").lower() and "draft" not in f.get("proposed", "").lower():
            continue
            
        # Check for editorializing about people
        if any(word in what for word in ["slow", "lazy", "incompetent", "bad at", "keeps forgetting"]):
            continue
            
        # Check for customer happiness inference
        if any(word in what for word in ["unhappy", "frustrated", "angry", "upset", "disappointed"]):
            continue
            
        filtered.append(f)
    return filtered


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
                notes = deal.get("notes", "")
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
            from_field = last_msg.get("from", "").lower()
            
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
                    
                    body = last_msg.get("body", "").lower()
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
    needs = finding.get("needs_human", "no")
    
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
                model=CFG["defaults"].get("model", "claude-3-5-sonnet-20241022"),
                max_tokens=4096,
                temperature=0.3,
                system=system_prompt,
                messages=[
                    {"role": "user", "content": user_msg}
                ]
            )
            
            # Extract text from response
            response_text = ""
            for block in response.content:
                if hasattr(block, 'text'):
                    response_text += block.text
            
            # Try to parse JSON from the response
            # Claude might wrap JSON in markdown code blocks
            response_text = response_text.strip()
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            if response_text.startswith("```"):
                response_text = response_text[3:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]
            response_text = response_text.strip()
            
            result = json.loads(response_text)
            findings = result.get("findings", [])
            
            # Enforce max_findings
            max_findings = CFG["defaults"]["max_findings_per_run"]
            findings = findings[:max_findings]
            
            # Filter against "never" list
            findings = _filter_never_list(findings)
            
        except Exception as e:
            print(f"\nWarning: Anthropic API call failed for {agent_id}: {e}")
            print(f"Falling back to heuristic rules...\n")
            findings = _heuristic_watcher(agent_id, slice_data)
    
    # Render as strings
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
                model=CFG["defaults"].get("model", "claude-3-5-sonnet-20241022"),
                max_tokens=4096,
                temperature=0.3,
                system=desk_prompt,
                messages=[
                    {"role": "user", "content": user_msg}
                ]
            )
            
            # Extract text from response
            response_text = ""
            for block in response.content:
                if hasattr(block, 'text'):
                    response_text += block.text
            
            # Try to parse JSON from the response
            response_text = response_text.strip()
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            if response_text.startswith("```"):
                response_text = response_text[3:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]
            response_text = response_text.strip()
            
            result = json.loads(response_text)
            problems = result.get("problems", [])
            
        except Exception as e:
            print(f"\nWarning: Desk merge Anthropic call failed: {e}")
            print(f"Falling back to heuristic merge...\n")
            problems = _heuristic_desk_merge(findings)
    
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
            if "send" in action.get("action", "").lower() and "draft" not in action.get("action", "").lower():
                action["action"] = action["action"].replace("send", "draft")
    
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
        needs_human = any(f.get("needs_human", "no").lower().startswith("yes") for f in group)
        
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
            action_type = action.get("action", "").lower().strip()
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
    
    human_items = [p for p in problems if p.get("human")][:3]
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
