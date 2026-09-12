"""Load the fictional company (seed/*.json) into a client.

Works against MockClient (in memory) and, once McpClient exists, against the live workspace —
same function, so you seed the real workspace with one command when MCP is ready.

Dates in the seed are day offsets; this converts them to real dates relative to today so the demo is
fresh whenever you run it. The `expected_role` fields are test annotations and are stripped before
loading — the agents must never see them.
"""
from __future__ import annotations
import json
from pathlib import Path
from .client import SEED_DIR, d


def _load(name: str):
    return json.loads((SEED_DIR / name).read_text(encoding="utf-8"))


def _strip(obj):
    if isinstance(obj, dict):
        return {k: _strip(v) for k, v in obj.items() if not k.startswith("expected") and not k.startswith("_")}
    if isinstance(obj, list):
        return [_strip(x) for x in obj]
    return obj


def load_seed_into(client) -> None:
    company = _load("company.json")

    # CRM
    deals = []
    for x in _strip(_load("crm_deals.json")):
        x["close_date"] = d(x.pop("close_date_days"))
        x["last_activity"] = d(x.pop("last_activity_days"))
        x["stage_entered"] = d(x.pop("stage_entered_days"))
        if "kickoff_date_days" in x:
            x["kickoff_date"] = d(x.pop("kickoff_date_days"))
        deals.append(x)

    # Mail
    threads = []
    for t in _strip(_load("mail_threads.json")):
        for m in t["messages"]:
            m["date"] = d(m.pop("days"))
        threads.append(t)

    # Tasks
    tasks = []
    for t in _strip(_load("tasks.json")):
        t["due"] = d(t.pop("due_days")); tasks.append(t)

    # Calendar
    events = []
    for e in _strip(_load("calendar_events.json")):
        e["date"] = d(e.pop("days")); events.append(e)

    # Chat history
    chat = _strip(_load("chat_history.json"))
    channels = {}
    for ch, msgs in chat.items():
        channels[ch] = [{"id": f"{ch}-{i}", "channel": ch, "thread_id": None, "from": m["from"],
                         "text": m["text"], "at": d(m["days"])} for i, m in enumerate(msgs)]
    for ch in company["channels"]:
        channels.setdefault(ch["name"], [])

    # Hand over — MockClient stores in memory; a live client would call its create_* methods here.
    if hasattr(client, "deals"):
        client.deals, client.threads, client.tasks, client.events, client.channels = deals, threads, tasks, events, channels
    else:
        raise NotImplementedError("Live seeding: call the client's create_* methods for each record here.")


if __name__ == "__main__":
    from .client import MockClient
    c = MockClient(verbose=False)
    print(f"seeded: {len(c.deals)} deals, {len(c.threads)} threads, {len(c.tasks)} tasks, {len(c.events)} events, "
          f"{sum(len(v) for v in c.channels.values())} chat messages across {len(c.channels)} channels")
