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
import argparse, datetime as dt
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


def run_watcher(agent: dict, ws: WorkspaceClient) -> list[str]:
    """TODO (rung 1): call the model with playbook(agent) as system prompt and slice_for(...) as the
    user message; ask for FINDING cards per prompts/finding_card_schema.md; return them as strings.
    Tip: ask the model for a JSON list of cards and render the text yourself — merging is easier
    with structured data, and you can enforce max_findings and the 'never' list in code."""
    raise NotImplementedError


def run_desk_merge(cards: list[dict], ws: WorkspaceClient) -> list[dict]:
    """TODO (rung 2/3): give the Desk all cards from the floor; get back PROBLEM blocks:
    {account, rank, merges:[refs], cause, actions:[{agent, action, args}], human: None|{who, text}}.
    Enforce in code: max 3 human items; nothing customer-facing is 'send'; unclear -> ask, not escalate."""
    raise NotImplementedError


def execute_actions(problems: list[dict], ws: WorkspaceClient) -> None:
    """TODO (rung 3): map action -> client call. Allowed set is closed:
    add_note -> ws.add_deal_note | set_field -> ws.set_deal_field | draft -> ws.create_draft
    assign_task -> ws.create_task | ask -> ws.post(floor, '@name ...', thread_id) | flag_event -> ws.post(...)
    Anything else is refused and logged. That refusal IS the safety story — say it in the video."""
    raise NotImplementedError


def post_brief(problems: list[dict], ws: WorkspaceClient) -> str:
    """TODO (rung 2): render the brief per finding_card_schema.md and post to #attention. Return msg id."""
    raise NotImplementedError


def reply_loop(brief_msg_id: str, ws: WorkspaceClient) -> None:
    """TODO (rung 4): poll the brief thread; for each human reply, ask the Desk to extract the decision
    and write it back (note/field/task); confirm on the floor in one line."""
    raise NotImplementedError


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
