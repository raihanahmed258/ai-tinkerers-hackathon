"""Rung 4 — human reply handler for the #attention brief thread.

Poll/extract EXPLICIT decisions only (contact name, date, approval yes/no).
Safe write-backs via WorkspaceClient allowlist; confirm on #agents-floor.
Never guess when ambiguous — ask one clarifying question in the attention thread.
"""
from __future__ import annotations

import datetime as dt
import os
import re
from typing import Any

# Lazy CFG load so this module stays importable without round.py side effects.
def _cfg() -> dict:
    from pathlib import Path
    import yaml
    root = Path(__file__).resolve().parent.parent
    return yaml.safe_load((root / "agents.yaml").read_text(encoding="utf-8"))


# ---- safety ---------------------------------------------------------------

SAFE_FIELDS = frozenset({
    "contact", "contact_name", "notes", "note",
    "kickoff_date", "revisit_date", "reason", "why_stalled",
})
BLOCKED_FIELDS = frozenset({
    "stage", "stage_id", "close_date", "pipeline", "pipeline_id",
    "owner_id", "status", "owner",
})

HUMAN_IDS = frozenset({"dana", "priya", "marcus", "theo"})
AGENT_FROM = frozenset({"agent", "ops", "inbox", "followup", "follow-up", "desk", "verifier", "closer"})

# Demo / common account → deal mapping when brief evidence is thin
ACCOUNT_DEAL_HINTS = {
    "pine & salt": "D-105",
    "pine and salt": "D-105",
    "copper kettle": "D-101",
    "marigold": "D-102",
    "ember grill": "D-107",
    "harbor fish": "D-104",
    "northgate": "D-112",
    "fig & thistle": "D-116",
    "sunset taco": "D-103",
}


# ---- extraction heuristics ------------------------------------------------

_CONTACT_PATTERNS = [
    # "Try Maya Brooks, their ops director."
    re.compile(
        r"(?i)\b(?:try|reach(?:\s+out\s+to)?|contact|use|speak\s+(?:to|with)|"
        r"talk\s+to|call|email|new\s+contact(?:\s+is)?|alternate(?:\s+contact)?(?:\s+is)?|"
        r"go\s+with|suggest(?:ing)?)\s+"
        r"([A-Z][a-z]+(?:\s+[A-Z][a-z]+){0,3})"
    ),
    # "contact: Maya Brooks" / "contact is Maya Brooks"
    re.compile(
        r"(?i)\bcontact(?:\s+name)?\s*(?:is|:|=)\s*"
        r"([A-Z][a-z]+(?:\s+[A-Z][a-z]+){0,3})"
    ),
    # trailing name + role: "Maya Brooks, their ops director"
    re.compile(
        r"\b([A-Z][a-z]+\s+[A-Z][a-z]+)\s*,\s*(?:their|our|the)\s+"
        r"(?:ops|operations|account|sales|tech|technical)?\s*(?:director|manager|lead|contact|champion)"
    ),
]

_APPROVE_YES = re.compile(
    r"(?i)^\s*(?:yes|yep|yeah|approved?|ok(?:ay)?|go\s+ahead|send\s+it|"
    r"ship\s+it|lgtm|do\s+it|confirmed?|sounds?\s+good)\b"
)
_APPROVE_NO = re.compile(
    r"(?i)^\s*(?:no|nope|not\s+yet|hold|don't|do\s+not|reject(?:ed)?|deny|denied)\b"
)

_DATE_PATTERNS = [
    re.compile(r"\b(20\d{2}-\d{2}-\d{2})\b"),  # ISO
    re.compile(
        r"(?i)\b(?:on|by|for|kickoff(?:\s+on)?|slot|date)\s*"
        r"((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec)[a-z]*\.?\s+\d{1,2}"
        r"(?:,?\s*20\d{2})?|\d{1,2}/\d{1,2}(?:/\d{2,4})?)\b"
    ),
]

_DEAL_RE = re.compile(r"\b(D-\d{3})\b", re.I)
_ACCOUNT_RE = re.compile(
    r"(?i)\b(Pine\s*&\s*Salt|Pine\s+and\s+Salt|Copper\s+Kettle|Marigold|"
    r"Ember\s+Grill|Harbor\s+Fish|Northgate(?:\s+Brewing)?|Fig\s*&\s*Thistle|"
    r"Sunset\s+Taco|Bluebird(?:\s+Bakeries)?)\b"
)


def _norm_from(msg: dict) -> str:
    raw = str(msg.get("from") or msg.get("author") or msg.get("user") or "").strip().lower()
    # "Dana Whitfield" → dana; "@dana" → dana
    raw = raw.lstrip("@")
    if " " in raw:
        raw = raw.split()[0]
    return raw


def _is_human_reply(msg: dict) -> bool:
    who = _norm_from(msg)
    if who in AGENT_FROM or who.startswith("agent"):
        return False
    if who in HUMAN_IDS:
        return True
    # Explicit human flag or non-agent author with text
    if msg.get("human") is True:
        return True
    # Mock posts default from=agent; anything else with text counts as human if not agent
    if who and who not in AGENT_FROM:
        return True
    return False


def _parse_brief_items(brief_text: str) -> list[dict]:
    """Pull ranked items from the Desk brief for context mapping."""
    items: list[dict] = []
    # "1. @dana — Pine & Salt ($120,000)"
    item_re = re.compile(
        r"(?m)^(\d+)\.\s*@?(\w+)\s*[—\-–]\s*([^\n(]+?)(?:\s*\([^)]*\))?\s*$"
    )
    lines = brief_text.splitlines()
    for i, line in enumerate(lines):
        m = item_re.match(line.strip())
        if not m:
            continue
        who = m.group(2).lower()
        account = m.group(1) and m.group(3).strip()
        account = m.group(3).strip()
        block = [line]
        for nxt in lines[i + 1 :]:
            if re.match(r"^\d+\.\s*@", nxt.strip()) or nxt.strip().startswith("Handled"):
                break
            if nxt.strip().startswith("Reply in this thread"):
                break
            block.append(nxt)
        block_text = "\n".join(block)
        deals = _DEAL_RE.findall(block_text)
        deal_id = deals[0].upper() if deals else ACCOUNT_DEAL_HINTS.get(account.lower())
        items.append({
            "rank": int(m.group(1)),
            "who": who,
            "account": account,
            "deal_id": deal_id,
            "text": block_text,
        })
    return items


def _match_brief_item(msg: dict, brief_items: list[dict]) -> dict | None:
    text = str(msg.get("text") or "")
    author = _norm_from(msg)

    # Explicit deal / account in the reply
    deals = _DEAL_RE.findall(text)
    if deals:
        want = deals[0].upper()
        for it in brief_items:
            if it.get("deal_id") == want:
                return it
    acc = _ACCOUNT_RE.search(text)
    if acc:
        key = re.sub(r"\s+", " ", acc.group(1).lower().replace(" and ", " & "))
        for it in brief_items:
            if key in (it.get("account") or "").lower():
                return it
        # fall through to hint
        deal = ACCOUNT_DEAL_HINTS.get(key) or ACCOUNT_DEAL_HINTS.get(
            key.replace(" brewing", "")
        )
        if deal:
            return {"who": author, "account": acc.group(1), "deal_id": deal, "text": text}

    # Author matches the brief's @who (e.g. Dana → Pine & Salt)
    for it in brief_items:
        if it.get("who") == author:
            return it

    if len(brief_items) == 1:
        return brief_items[0]
    return None


def _extract_contact(text: str) -> str | None:
    for pat in _CONTACT_PATTERNS:
        m = pat.search(text)
        if not m:
            continue
        name = m.group(1).strip().rstrip(".,;:")
        # Reject if it's a known human teammate being addressed, not a contact
        first = name.split()[0].lower()
        if first in HUMAN_IDS:
            continue
        if name.lower() in {"the", "their", "our", "a", "an", "someone", "anybody"}:
            continue
        # Prefer multi-word names
        if " " in name or len(name) > 2:
            return name
    return None


def _extract_approval(text: str) -> bool | None:
    t = text.strip()
    if _APPROVE_YES.search(t):
        return True
    if _APPROVE_NO.search(t):
        return False
    return None


def _extract_date(text: str) -> str | None:
    for pat in _DATE_PATTERNS:
        m = pat.search(text)
        if m:
            return m.group(1).strip()
    return None


def extract_decisions(
    messages: list[dict],
    *,
    brief_text: str | None = None,
    brief_items: list[dict] | None = None,
) -> list[dict]:
    """Extract EXPLICIT decisions only from human replies. Never guess.

    Each decision dict:
      kind: contact | approval | date | ambiguous
      deal_id, account, who, contact, approved, date, source_msg_id, raw_text
      action hints for apply_safe_writeback
    """
    items = brief_items if brief_items is not None else _parse_brief_items(brief_text or "")
    decisions: list[dict] = []

    for msg in messages:
        if not _is_human_reply(msg):
            continue
        text = str(msg.get("text") or "").strip()
        if not text:
            continue

        matched = _match_brief_item(msg, items)
        contact = _extract_contact(text)
        approval = _extract_approval(text)
        date_val = _extract_date(text)

        base = {
            "source_msg_id": msg.get("id"),
            "who": _norm_from(msg),
            "raw_text": text,
            "deal_id": (matched or {}).get("deal_id"),
            "account": (matched or {}).get("account"),
            "brief_who": (matched or {}).get("who"),
        }

        # Prefer contact (demo case: Dana → Maya Brooks on Pine & Salt)
        if contact:
            if not base["deal_id"] and not base["account"]:
                decisions.append({**base, "kind": "ambiguous", "reason": "contact named but no deal/account context"})
                continue
            decisions.append({
                **base,
                "kind": "contact",
                "contact": contact,
                "field": "contact",
            })
            continue

        if approval is not None:
            if not base["deal_id"] and not base["account"]:
                decisions.append({**base, "kind": "ambiguous", "reason": "approval without deal/account context"})
                continue
            decisions.append({
                **base,
                "kind": "approval",
                "approved": approval,
            })
            continue

        if date_val:
            if not base["deal_id"] and not base["account"]:
                decisions.append({**base, "kind": "ambiguous", "reason": "date without deal/account context"})
                continue
            decisions.append({
                **base,
                "kind": "date",
                "date": date_val,
                "field": "kickoff_date",
            })
            continue

        # No explicit signal
        decisions.append({
            **base,
            "kind": "ambiguous",
            "reason": "no explicit contact, approval, or date found",
        })

    return decisions


# ---- write-back -----------------------------------------------------------

def _resolve_deal_id(decision: dict, ws) -> str | None:
    deal_id = decision.get("deal_id")
    if deal_id:
        return str(deal_id).upper()
    account = (decision.get("account") or "").strip().lower()
    if not account:
        return None
    hint = ACCOUNT_DEAL_HINTS.get(account)
    if hint:
        return hint
    # Scan CRM
    try:
        for d in ws.list_deals():
            if (d.get("account") or "").strip().lower() == account:
                return d.get("id")
    except Exception:
        pass
    return None


def apply_safe_writeback(decision: dict, ws) -> tuple[bool, str]:
    """Apply a single explicit decision via allowlisted WorkspaceClient methods.

    Returns (ok, summary). On ambiguity or blocked action returns (False, reason).
    Never sends email, never changes stage/close_date, never edits calendar.
    """
    kind = decision.get("kind")
    if kind == "ambiguous" or not kind:
        return False, decision.get("reason") or "ambiguous — no write"

    deal_id = _resolve_deal_id(decision, ws)
    if not deal_id and kind in ("contact", "date", "approval"):
        return False, "could not resolve deal id for write-back"

    as_agent = getattr(ws, "as_agent", None)

    def _run(fn):
        if as_agent:
            with ws.as_agent("desk"):
                return fn()
        return fn()

    if kind == "contact":
        name = decision.get("contact")
        if not name:
            return False, "missing contact name"
        note = (
            f"Human reply ({decision.get('who') or 'human'}): "
            f"new contact for {decision.get('account') or deal_id} is {name}. "
            f"Quote: {decision.get('raw_text')!r}"
        )

        def do():
            # Prefer set contact field + note (note is the durable audit)
            try:
                ws.set_deal_field(deal_id, "contact", name)
            except PermissionError:
                pass
            except Exception:
                # Mock/live may only support notes — still record
                pass
            ws.add_deal_note(deal_id, note)
            # Optional follow-up task: re-point calendar (we never edit the event ourselves)
            try:
                due = (dt.date.today() + dt.timedelta(days=2)).isoformat()
                ws.create_task(
                    f"Re-point calendar invite to {name} ({decision.get('account') or deal_id})",
                    decision.get("who") or "dana",
                    due,
                    deal_id,
                )
            except Exception:
                pass

        _run(do)
        return True, f"Recorded contact {name} on {deal_id} ({decision.get('account') or '—'})"

    if kind == "approval":
        approved = decision.get("approved")
        verb = "approved" if approved else "declined"
        note = (
            f"Human reply ({decision.get('who') or 'human'}): {verb}. "
            f"Quote: {decision.get('raw_text')!r}"
        )

        def do():
            ws.add_deal_note(deal_id, note)

        _run(do)
        return True, f"Recorded {verb} on {deal_id} ({decision.get('account') or '—'})"

    if kind == "date":
        date_val = decision.get("date")
        field = decision.get("field") or "kickoff_date"
        if field.lower() in BLOCKED_FIELDS or field.lower() not in SAFE_FIELDS:
            return False, f"field '{field}' not on safe allowlist"
        note = (
            f"Human reply ({decision.get('who') or 'human'}): set {field}={date_val}. "
            f"Quote: {decision.get('raw_text')!r}"
        )

        def do():
            try:
                ws.set_deal_field(deal_id, field, date_val)
            except PermissionError as e:
                raise
            except Exception:
                pass
            ws.add_deal_note(deal_id, note)

        try:
            _run(do)
        except PermissionError as e:
            return False, str(e)
        return True, f"Recorded {field}={date_val} on {deal_id}"

    return False, f"unknown decision kind: {kind}"


def confirm_on_floor(ws, summary: str, *, channels: dict | None = None) -> str:
    """Post one-line confirmation to #agents-floor (CFG channels floor)."""
    cfg = channels or _cfg().get("channels") or {}
    floor = cfg.get("floor", "agents-floor")
    text = f"Recorded: {summary}" if not str(summary).lower().startswith("recorded") else str(summary)

    def do():
        return ws.post(floor, text)

    as_agent = getattr(ws, "as_agent", None)
    if as_agent:
        with ws.as_agent("desk"):
            return do()
    return do()


def ask_clarifying(ws, brief_msg_id: str, question: str, *, channels: dict | None = None) -> str:
    """Ask one clarifying question in the attention brief thread."""
    cfg = channels or _cfg().get("channels") or {}
    attention = cfg.get("humans", "attention")
    text = question if question.strip().endswith("?") else question.rstrip() + "?"

    def do():
        return ws.post(attention, text, thread_id=brief_msg_id)

    as_agent = getattr(ws, "as_agent", None)
    if as_agent:
        with ws.as_agent("desk"):
            return do()
    return do()


# ---- orchestration --------------------------------------------------------

def _thread_replies(ws, attention: str, brief_msg_id: str) -> tuple[str, list[dict]]:
    """Return (brief_text, human+agent replies in thread)."""
    msgs = ws.read_channel(attention, since_hours=24 * 14)
    brief_text = ""
    replies: list[dict] = []
    for m in msgs:
        mid = str(m.get("id") or "")
        tid = m.get("thread_id")
        if mid == str(brief_msg_id) and not tid:
            brief_text = str(m.get("text") or "")
            continue
        if mid == str(brief_msg_id):
            # some clients nest the root with thread_id=self
            brief_text = brief_text or str(m.get("text") or "")
            continue
        if tid is not None and str(tid) == str(brief_msg_id):
            replies.append(m)
    # If brief text missing, try root message lookup by id only
    if not brief_text:
        for m in msgs:
            if str(m.get("id") or "") == str(brief_msg_id):
                brief_text = str(m.get("text") or "")
                break
    return brief_text, replies


def process_attention_replies(
    brief_msg_id: str,
    ws,
    *,
    channels: dict | None = None,
    processed_ids: set[str] | None = None,
) -> list[dict]:
    """Poll #attention thread for brief_msg_id; extract, write back, confirm.

    Returns list of result dicts: {decision, ok, summary}.
    """
    cfg_channels = channels or _cfg().get("channels") or {}
    attention = cfg_channels.get("humans", "attention")
    seen = processed_ids if processed_ids is not None else set()

    brief_text, replies = _thread_replies(ws, attention, brief_msg_id)
    brief_items = _parse_brief_items(brief_text)
    decisions = extract_decisions(replies, brief_text=brief_text, brief_items=brief_items)

    results: list[dict] = []
    for dec in decisions:
        sid = str(dec.get("source_msg_id") or "")
        if sid and sid in seen:
            continue
        if sid:
            seen.add(sid)

        if dec.get("kind") == "ambiguous":
            who = dec.get("who") or "there"
            acct = dec.get("account") or "which account"
            q = (
                f"@{who} — got your reply, but I'm not sure what to record for {acct}. "
                f"Please confirm: a contact name, a yes/no approval, or a date"
            )
            ask_clarifying(ws, brief_msg_id, q, channels=cfg_channels)
            results.append({"decision": dec, "ok": False, "summary": "asked clarifying question"})
            continue

        ok, summary = apply_safe_writeback(dec, ws)
        if ok:
            confirm_on_floor(ws, summary, channels=cfg_channels)
        else:
            # Soft fail: clarify rather than write
            ask_clarifying(
                ws,
                brief_msg_id,
                f"@{dec.get('who') or 'there'} — couldn't record that ({summary}). "
                f"Please restate the contact, approval, or date",
                channels=cfg_channels,
            )
        results.append({"decision": dec, "ok": ok, "summary": summary})

    return results


def handle_reply_loop(
    brief_msg_id: str,
    ws,
    *,
    poll_once: bool = True,
    channels: dict | None = None,
) -> list[dict]:
    """Entry used by round.reply_loop. Single-pass by default (demo/mock friendly)."""
    print(f"\n[Reply loop] polling attention thread {brief_msg_id} for human replies")
    return process_attention_replies(brief_msg_id, ws, channels=channels)


# ---- mock test helpers ----------------------------------------------------

def inject_attention_reply(
    ws,
    brief_msg_id: str,
    author: str,
    text: str,
    *,
    channels: dict | None = None,
) -> str:
    """Seed a synthetic human reply into MockClient's attention thread. Returns msg id."""
    cfg_channels = channels or _cfg().get("channels") or {}
    attention = cfg_channels.get("humans", "attention")
    # MockClient.post always sets from=agent — patch after post for human author
    msg_id = ws.post(attention, text, thread_id=brief_msg_id)
    for m in ws.channels.get(attention, []):
        if m.get("id") == msg_id:
            m["from"] = author
            m["human"] = True
            break
    return msg_id


def ensure_brief_for_demo(ws, *, channels: dict | None = None) -> str:
    """Post a minimal Pine & Salt brief if none exists; return brief msg id."""
    cfg_channels = channels or _cfg().get("channels") or {}
    attention = cfg_channels.get("humans", "attention")
    brief = (
        f"Attention brief · {dt.date.today().isoformat()}\n"
        "1 item(s) need a person · everything else handled on the floor\n"
        "\n"
        "1. @dana — Pine & Salt ($120,000)\n"
        "   Champion bounced; no other contact known\n"
        "   Evidence: D-105, M-4, E-4\n"
        "\n"
        "Reply in this thread and I'll record it."
    )
    return ws.post(attention, brief)


def run_mock_demo(
    *,
    reply_text: str = "Try Maya Brooks, their ops director.",
    author: str = "dana",
    verbose: bool = True,
) -> dict[str, Any]:
    """Self-test: inject Dana reply → note on D-105 → confirm on agents-floor.

    Usage from kit root:
      python -c "from floor.reply_handler import run_mock_demo; run_mock_demo()"
    """
    from .client import MockClient

    ws = MockClient(verbose=verbose)
    brief_id = ensure_brief_for_demo(ws)
    inject_attention_reply(ws, brief_id, author, reply_text)
    results = process_attention_replies(brief_id, ws)

    # Snapshot CRM note for report
    deal = next((d for d in ws.deals if d["id"] == "D-105"), None)
    floor_msgs = [m for m in ws.channels.get("agents-floor", []) if "Recorded" in (m.get("text") or "")]
    out = {
        "brief_id": brief_id,
        "results": results,
        "d105_contact": (deal or {}).get("contact"),
        "d105_notes_tail": ((deal or {}).get("notes") or "")[-200:],
        "floor_confirmations": [m.get("text") for m in floor_msgs],
    }
    if verbose:
        print("\n—— mock demo result ——")
        print(f"D-105 contact: {out['d105_contact']}")
        print(f"floor: {out['floor_confirmations']}")
        print(f"ok: {all(r.get('ok') for r in results) if results else False}")
    return out


if __name__ == "__main__":
    run_mock_demo()
