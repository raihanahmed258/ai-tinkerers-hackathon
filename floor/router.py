"""Router-as-code: each watcher sees only its lane.

    Ops        → CRM deals
    Inbox      → mail threads
    Follow-up  → tasks + calendar + selected chat (#sales, #ops-team)

Desk merge is the only place those lanes meet. This module does not
execute actions, post to the floor, or read #agents-floor / #attention.
"""
from __future__ import annotations

# Human channels Follow-up may read. Floor + attention stay off-slice.
FOLLOWUP_CHAT_CHANNELS = ("sales", "ops-team")

# Canonical watcher ids. Aliases normalize before the lane table.
_ALIASES = {
    "ops": "ops",
    "inbox": "inbox",
    "followup": "followup",
    "follow-up": "followup",
    "follow_up": "followup",
}

# Keys each lane is allowed to return. Anything else is a leak.
LANE_KEYS = {
    "ops": frozenset({"deals"}),
    "inbox": frozenset({"threads"}),
    "followup": frozenset({"tasks", "events", "chat"}),
}


def _norm_agent(agent_id: str) -> str:
    key = (agent_id or "").strip().lower().replace(" ", "")
    if key in _ALIASES:
        return _ALIASES[key]
    raise KeyError(agent_id)


def _clean(obj):
    """Drop seed annotations (expected_*) so they never reach a watcher."""
    if isinstance(obj, dict):
        return {
            k: _clean(v)
            for k, v in obj.items()
            if not str(k).startswith("expected") and not str(k).startswith("_")
        }
    if isinstance(obj, list):
        return [_clean(x) for x in obj]
    return obj


def slice_for(agent_id: str, ws) -> dict:
    """What each watcher is allowed to see. Narrow slices are the design.

    Ops: CRM only. Inbox: mail only. Follow-up: tasks, calendar, selected chat.
    """
    lane = _norm_agent(agent_id)
    if lane == "ops":
        out = {"deals": _clean(ws.list_deals())}
    elif lane == "inbox":
        out = {"threads": _clean(ws.list_threads())}
    elif lane == "followup":
        chat = {
            ch: _clean(ws.read_channel(ch, since_hours=24 * 45))
            for ch in FOLLOWUP_CHAT_CHANNELS
        }
        out = {
            "tasks": _clean(ws.list_tasks()),
            "events": _clean(ws.list_events()),
            "chat": chat,
        }
    else:
        raise KeyError(agent_id)

    extra = set(out) - LANE_KEYS[lane]
    if extra:
        raise RuntimeError(f"slice_for({lane}) leaked keys: {sorted(extra)}")
    return out
