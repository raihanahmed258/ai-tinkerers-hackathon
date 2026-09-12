"""Tool surface for the agents.

Two implementations share one interface:
  * MockClient  — runs entirely on the seed JSON, in memory. Use it to build and test the round
                  logic tonight/tomorrow morning with zero network. Every "post" is printed and kept.
  * McpClient   — live Ambiguous workspace via Streamable HTTP MCP (see MCP_MAPPING.md).

Keep the interface tiny. Eight calls are enough for the whole demo.
"""
from __future__ import annotations
import json, os, asyncio, datetime as dt
from dataclasses import dataclass, field
from pathlib import Path
from typing import Protocol

SEED_DIR = Path(__file__).resolve().parent.parent / "seed"


def today() -> dt.date:
    return dt.date.today()


def d(days: int | None) -> str | None:
    """Offset-in-days -> ISO date, relative to today. None stays None (e.g. missing kickoff date)."""
    return None if days is None else (today() + dt.timedelta(days=days)).isoformat()


class WorkspaceClient(Protocol):
    # chat
    def read_channel(self, channel: str, since_hours: int = 48) -> list[dict]: ...
    def post(self, channel: str, text: str, thread_id: str | None = None) -> str: ...
    # crm
    def list_deals(self) -> list[dict]: ...
    def add_deal_note(self, deal_id: str, note: str) -> None: ...
    def set_deal_field(self, deal_id: str, field: str, value) -> None: ...
    # mail
    def list_threads(self) -> list[dict]: ...
    def create_draft(self, thread_id: str, body: str) -> str: ...
    def resolve_mail_id(self, ref: str | None) -> str | None: ...
    # tasks + calendar
    def list_tasks(self) -> list[dict]: ...
    def create_task(self, title: str, owner: str, due: str, linked: str | None = None) -> str: ...
    def list_events(self, days_back: int = 45, days_forward: int = 30) -> list[dict]: ...


@dataclass
class MockClient:
    """In-memory workspace built from the seed. Deterministic, offline, instant."""
    verbose: bool = True
    channels: dict[str, list[dict]] = field(default_factory=dict)
    deals: list[dict] = field(default_factory=list)
    threads: list[dict] = field(default_factory=list)
    tasks: list[dict] = field(default_factory=list)
    events: list[dict] = field(default_factory=list)
    drafts: list[dict] = field(default_factory=list)
    _n: int = 0

    def __post_init__(self):
        from .seed import load_seed_into  # local import avoids a cycle
        load_seed_into(self)

    # ---- chat ----
    def read_channel(self, channel: str, since_hours: int = 48) -> list[dict]:
        return list(self.channels.get(channel, []))

    def post(self, channel: str, text: str, thread_id: str | None = None) -> str:
        self._n += 1
        msg_id = f"msg-{self._n:04d}"
        self.channels.setdefault(channel, []).append(
            {"id": msg_id, "channel": channel, "thread_id": thread_id, "from": "agent", "text": text,
             "at": dt.datetime.now().isoformat(timespec="seconds")})
        if self.verbose:
            where = f"#{channel}" + (f" (thread {thread_id})" if thread_id else "")
            print(f"\n──── POST → {where} ────\n{text}")
        return msg_id

    # ---- crm ----
    def list_deals(self) -> list[dict]:
        return [dict(x) for x in self.deals]

    def add_deal_note(self, deal_id: str, note: str) -> None:
        for x in self.deals:
            if x["id"] == deal_id:
                x["notes"] = (x.get("notes") or "") + f"\n[{today().isoformat()} · agent] {note}"
                if self.verbose: print(f"\n──── CRM NOTE → {deal_id} ────\n{note}")
                return
        raise KeyError(deal_id)

    def set_deal_field(self, deal_id: str, field_: str, value) -> None:
        for x in self.deals:
            if x["id"] == deal_id:
                x[field_] = value
                if self.verbose: print(f"\n──── CRM FIELD → {deal_id}.{field_} = {value!r}")
                return
        raise KeyError(deal_id)

    # ---- mail ----
    def list_threads(self) -> list[dict]:
        return [dict(x) for x in self.threads]

    def create_draft(self, thread_id: str, body: str) -> str:
        self._n += 1
        draft_id = f"draft-{self._n:04d}"
        self.drafts.append({"id": draft_id, "thread_id": thread_id, "body": body})
        if self.verbose: print(f"\n──── DRAFT (not sent) → {thread_id} ────\n{body}")
        return draft_id

    def resolve_mail_id(self, ref: str | None) -> str | None:
        """Map seed M-* / exact id → thread id. None if unresolved (caller must BLOCK, not invent)."""
        r = (ref or "").strip()
        if not r:
            return None
        by_id = {str(th.get("id")): th for th in self.threads if th.get("id") is not None}
        if r in by_id:
            return r
        if r.upper().startswith("M-"):
            needle = r.upper()
            for th in self.threads:
                blob = f"{th.get('id')} {th.get('subject')} {th.get('ref')}".upper()
                if needle in blob:
                    tid = th.get("id")
                    return str(tid) if tid is not None else None
        return None  # never passthrough unverified UUID / junk

    # ---- tasks + calendar ----
    def list_tasks(self) -> list[dict]:
        return [dict(x) for x in self.tasks]

    def create_task(self, title: str, owner: str, due: str, linked: str | None = None) -> str:
        self._n += 1
        tid = f"T-new-{self._n:04d}"
        self.tasks.append({"id": tid, "title": title, "owner": owner, "due": due, "status": "open", "linked_deal": linked})
        if self.verbose: print(f"\n──── TASK → {owner}: {title} (due {due})")
        return tid

    def list_events(self, days_back: int = 45, days_forward: int = 30) -> list[dict]:
        return [dict(x) for x in self.events]

    def as_agent(self, agent_id=None):
        from contextlib import nullcontext
        return nullcontext()


DEFAULT_MCP_URL = "https://app.ambiguous.ai/mcp"



_SECRET_PATHS = (
    Path("/home/box/agent-data/box-secrets.json"),
    Path("/home/box/sand-data/box-secrets.json"),
)
AGENT_TOKEN_ENV = {
    "ops": ("AMBIGUOUS_TOKEN_OPS", "AMBIGUOUS_API_KEY_OPS"),
    "inbox": ("AMBIGUOUS_TOKEN_INBOX", "AMBIGUOUS_API_KEY_INBOX"),
    "followup": ("AMBIGUOUS_TOKEN_FOLLOWUP", "AMBIGUOUS_API_KEY_FOLLOWUP", "AMBIGUOUS_TOKEN_FOLLOW_UP"),
    "desk": ("AMBIGUOUS_TOKEN_DESK", "AMBIGUOUS_API_KEY_DESK"),
    "verifier": ("AMBIGUOUS_TOKEN_VERIFIER", "AMBIGUOUS_API_KEY_VERIFIER"),
    "closer": ("AMBIGUOUS_TOKEN_CLOSER", "AMBIGUOUS_API_KEY_CLOSER"),
}


def resolve_agent_token(agent_id: str | None) -> str | None:
    """Optional per-agent Ambiguous API key so posts appear as Ops/Inbox/Follow-up/Desk.

    Checks env, then box-secrets.json `card` (secret-request lands there).
    Never print the value.
    """
    if not agent_id:
        return None
    key = agent_id.strip().lower().replace("-", "_")
    if key in ("follow_up", "follow-up"):
        key = "followup"
    names = AGENT_TOKEN_ENV.get(key, ())
    for name in names:
        val = (os.environ.get(name) or "").strip()
        if val:
            return val
    for path in _SECRET_PATHS:
        try:
            blob = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        card = blob.get("card") if isinstance(blob, dict) else None
        if not isinstance(card, dict):
            continue
        for name in names:
            val = card.get(name)
            if isinstance(val, str) and val.strip():
                return val.strip()
    return None

CHANNEL_IDS = {
    "agents-floor": "6606389e-0977-415a-987e-599001037834",
    "attention": "8db08df8-60fe-4366-beef-fb13163d73ef",
    "sales": "b0781716-0fd8-4b5a-b110-0842cc6f294e",
    "ops-team": "52661440-bb72-4207-8199-1c31857d6c45",
    "general": "9e6b988f-0f23-43d9-909e-0330fe59d8c2",
    "admin-alerts": "81254594-e1c5-41e7-a253-ded65e6d4662",
}
STAGE_IDS = {
    "Discovery": "9c1eaf8b-ac91-4564-8461-b8b26c31d2e6",
    "Proposal": "fb09debb-abf5-4768-8198-a29f63e4f77f",
    "Negotiation": "8d8ddffa-073b-4fd2-a2a2-4602a5fed3b7",
    "Contract": "61d3e818-7859-4ac5-8a86-c3607f5ca5ed",
    "Closed Won — Implementation": "7aae85e6-f173-4d87-97e6-dbe50b0051ab",
    "Customer — Live": "1e54820b-cada-4eab-8711-6e06348fcff7",
    "Closed Lost": "f5d6b4f2-2a96-4f2c-96f0-5a54ca519233",
}
_UUID_CHARS = set("0123456789abcdefABCDEF-")


def resolve_ambiguous_token(explicit: str | None = None) -> str:
    """Env first (AMBIGUOUS_API_KEY / AMBIGUOUS_TOKEN), then box-secrets.json. Never print the value."""
    if explicit:
        return explicit
    for key in ("AMBIGUOUS_API_KEY", "AMBIGUOUS_TOKEN"):
        val = os.environ.get(key)
        if val:
            return val
    for path in _SECRET_PATHS:
        try:
            blob = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        card = blob.get("card") if isinstance(blob, dict) else None
        if isinstance(card, dict):
            val = card.get("AMBIGUOUS_API_KEY") or card.get("AMBIGUOUS_TOKEN")
            if val:
                return val
    raise RuntimeError("No Ambiguous token: set AMBIGUOUS_API_KEY or AMBIGUOUS_TOKEN")


def _looks_uuid(value: str | None) -> bool:
    if not value or len(value) != 36 or value.count("-") != 4:
        return False
    return all(ch in _UUID_CHARS for ch in value)


def _iso_date(value) -> str | None:
    if value is None:
        return None
    if isinstance(value, (dt.date, dt.datetime)):
        return value.date().isoformat() if isinstance(value, dt.datetime) else value.isoformat()
    text = str(value).strip()
    if not text:
        return None
    return text[:10]


def _name_of(obj, *keys: str) -> str | None:
    if isinstance(obj, str):
        return obj
    if isinstance(obj, dict):
        for k in keys or ("display_name", "name", "email", "primary_email"):
            if obj.get(k):
                return str(obj[k])
    return None


def _rows(payload) -> list[dict]:
    if payload is None:
        return []
    if isinstance(payload, list):
        return [x for x in payload if isinstance(x, dict)]
    if isinstance(payload, dict):
        for key in ("data", "items", "results", "deals", "messages", "tasks", "events", "threads", "emails"):
            val = payload.get(key)
            if isinstance(val, list):
                return [x for x in val if isinstance(x, dict)]
    return []


def _unwrap_tool_result(result):
    if getattr(result, "is_error", False):
        bits = []
        for block in getattr(result, "content", None) or []:
            t = getattr(block, "text", None)
            if t:
                bits.append(t)
        raise RuntimeError(bits[0] if bits else "Ambiguous MCP tool error")
    structured = getattr(result, "structuredContent", None) or getattr(result, "structured_content", None)
    if structured is not None:
        return structured
    texts = []
    for block in getattr(result, "content", None) or []:
        t = getattr(block, "text", None)
        if t is not None:
            texts.append(t)
    if not texts:
        return None
    raw = texts[0]
    try:
        return json.loads(raw)
    except (TypeError, json.JSONDecodeError):
        return raw


def _run(coro):
    try:
        asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.run(coro)
    import concurrent.futures
    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
        return pool.submit(asyncio.run, coro).result()


class McpClient:
    """Live Ambiguous workspace via Streamable HTTP MCP (`mcp` package).

    Method → tool map is in MCP_MAPPING.md. Return shapes stay close to MockClient
    so round.py can treat either client the same.
    """

    def __init__(self, server_url: str | None = None, token: str | None = None):
        self.server_url = (server_url or os.environ.get("AMBIGUOUS_MCP_URL") or DEFAULT_MCP_URL).rstrip("/")
        self.token = resolve_ambiguous_token(token)
        self._default_token = self.token
        self._channels: dict[str, str] = dict(CHANNEL_IDS)

    def as_agent(self, agent_id: str | None):
        """Context manager: temporarily authenticate as a named agent when its token is set.

        Specialists without their own token fall back to Desk. Verifier/Closer never fall
        back to the human/default token (fail closed with a loud error) — GAP A / Safety.
        Other specialists may still use the default token if Desk is also unset.
        """
        from contextlib import contextmanager

        @contextmanager
        def _cm():
            key = ""
            if agent_id:
                key = agent_id.strip().lower().replace("-", "_")
                if key in ("follow_up", "follow-up"):
                    key = "followup"
            tok = resolve_agent_token(agent_id)
            if not tok and key in AGENT_TOKEN_ENV and key != "desk":
                tok = resolve_agent_token("desk")
            if not tok:
                if key in ("verifier", "closer"):
                    msg = (
                        f"as_agent({key!r}): no {key} token and no Desk token — "
                        f"refusing human/default fallback (set AMBIGUOUS_TOKEN_{key.upper()} "
                        f"or AMBIGUOUS_TOKEN_DESK)"
                    )
                    print("\n──── SAFETY · " + msg)
                    raise PermissionError(msg)
                tok = self._default_token
            prev = self.token
            self.token = tok
            try:
                yield self
            finally:
                self.token = prev

        return _cm()

    # ---- transport ----
    async def _acall(self, name: str, arguments: dict | None = None):
        from mcp import Client
        from mcp.client.streamable_http import streamable_http_client
        from mcp.shared._httpx_utils import create_mcp_http_client

        http = create_mcp_http_client(headers={"Authorization": f"Bearer {self.token}"})
        async with http:
            transport = streamable_http_client(self.server_url, http_client=http)
            async with Client(transport) as client:
                result = await client.call_tool(name, arguments or {})
                return _unwrap_tool_result(result)

    def _tool(self, name: str, arguments: dict | None = None):
        return _run(self._acall(name, arguments))

    def _paged(self, name: str, arguments: dict | None = None, cap: int = 500) -> list[dict]:
        args = dict(arguments or {})
        args.setdefault("limit", 100)
        out: list[dict] = []
        cursor = None
        while True:
            page_args = dict(args)
            if cursor:
                page_args["cursor"] = cursor
            payload = self._tool(name, page_args)
            rows = _rows(payload)
            out.extend(rows)
            more = isinstance(payload, dict) and payload.get("has_more") and payload.get("next_cursor")
            if not more or len(out) >= cap:
                break
            cursor = payload["next_cursor"]
        return out

    def _channel_id(self, channel: str) -> str:
        name = (channel or "").lstrip("#").strip()
        if _looks_uuid(name):
            return name
        if name in self._channels:
            return self._channels[name]
        payload = self._tool("list_channels", {})
        for ch in _rows(payload):
            n = (ch.get("name") or "").lstrip("#")
            cid = ch.get("id")
            if n and cid:
                self._channels[n] = cid
        if name in self._channels:
            return self._channels[name]
        raise KeyError(f"unknown channel: {channel}")

    # ---- chat ----
    def read_channel(self, channel: str, since_hours: int = 48) -> list[dict]:
        cid = self._channel_id(channel)
        raw = self._paged("get_channel_messages", {"channel_id": cid, "limit": "100"})
        cutoff = None
        if since_hours is not None:
            cutoff = dt.datetime.now(dt.timezone.utc) - dt.timedelta(hours=since_hours)
        out = []
        for m in raw:
            at = m.get("created_at") or m.get("at") or m.get("timestamp")
            if cutoff and at:
                try:
                    ts = dt.datetime.fromisoformat(str(at).replace("Z", "+00:00"))
                    if ts.tzinfo is None:
                        ts = ts.replace(tzinfo=dt.timezone.utc)
                    if ts < cutoff:
                        continue
                except ValueError:
                    pass
            author = m.get("author") or m.get("user") or {}
            out.append({
                "id": m.get("id"),
                "channel": channel.lstrip("#"),
                "thread_id": m.get("thread_id"),
                "from": _name_of(author) or m.get("from") or "unknown",
                "text": m.get("content") or m.get("text") or m.get("body") or "",
                "at": at,
            })
        out.reverse()  # live API is newest-first; mock is chronological
        return out

    def post(self, channel: str, text: str, thread_id: str | None = None) -> str:
        args = {"channel_id": self._channel_id(channel), "content": text}
        if thread_id:
            args["thread_id"] = thread_id
        created = self._tool("send_message", args)
        if isinstance(created, dict):
            return str(created.get("id") or created.get("message_id") or "")
        return str(created or "")

    # ---- crm ----
    def list_deals(self) -> list[dict]:
        return [_norm_deal(x) for x in self._paged("list_deals", {"limit": 100})]

    def add_deal_note(self, deal_id: str, note: str) -> None:
        self._tool("log_activity", {"type": "note", "deal_id": deal_id, "body": note, "subject": "agent note"})

    def set_deal_field(self, deal_id: str, field: str, value) -> None:
        blocked = {"stage", "stage_id", "close_date", "pipeline", "pipeline_id", "owner_id", "status"}
        if str(field).lower() in blocked:
            raise PermissionError(f"refused set_deal_field({field}): blocked by Floor safety policy")
        if field in ("notes", "note"):
            self.add_deal_note(deal_id, str(value))
            return
        key = {"arr": "amount", "amount": "amount", "title": "title", "status": "status",
               "close_date": "close_date", "currency": "currency", "probability": "probability",
               "lost_reason": "lost_reason", "pipeline_id": "pipeline_id", "owner_id": "owner_id",
               "company_id": "company_id", "contact_id": "contact_id", "stage_id": "stage_id"}.get(field)
        payload = {"id": deal_id}
        if field in ("stage", "stage_id"):
            if _looks_uuid(str(value)):
                payload["stage_id"] = str(value)
            elif str(value) in STAGE_IDS:
                payload["stage_id"] = STAGE_IDS[str(value)]
            else:
                payload["custom_properties"] = {"stage": value}
        elif key:
            payload[key] = value
        elif field == "custom_properties" and isinstance(value, dict):
            payload["custom_properties"] = value
        else:
            payload["custom_properties"] = {field: value}
        self._tool("update_deal", payload)

    # ---- mail ----
    def list_threads(self) -> list[dict]:
        items = self._paged("list_inbox", {"limit": 50, "detail": "full"})
        threads: list[dict] = []
        for item in items:
            tid = item.get("thread_id") or item.get("id")
            messages = item.get("messages")
            if not messages and tid:
                full = self._tool("get_mail_thread", {"thread_id": tid})
                if isinstance(full, dict):
                    messages = full.get("messages") or full.get("emails") or full.get("data")
                    item = {**full, **item}
            msgs = []
            for m in messages or []:
                if not isinstance(m, dict):
                    continue
                sender = m.get("from") or m.get("sender") or {}
                msgs.append({
                    "from": _name_of(sender, "email", "name", "display_name") or str(sender),
                    "date": _iso_date(m.get("sent_at") or m.get("date") or m.get("created_at")),
                    "body": m.get("body_text") or m.get("body_markdown") or m.get("preview") or m.get("snippet") or "",
                })
            if not msgs and (item.get("preview") or item.get("subject")):
                sender = item.get("from") or item.get("sender") or {}
                msgs.append({
                    "from": _name_of(sender, "email", "name", "display_name") or str(sender),
                    "date": _iso_date(item.get("sent_at") or item.get("date")),
                    "body": item.get("preview") or item.get("snippet") or "",
                })
            threads.append({
                "id": tid,
                "subject": item.get("subject") or "",
                "account": item.get("account"),
                "deal": item.get("deal_id"),
                "participants": item.get("participants") or [],
                "messages": msgs,
                "last_from_customer": None,
                "unanswered_days": None,
            })
        return threads

    def resolve_mail_id(self, ref: str | None) -> str | None:
        """Live UUID or seed M-* → inbox thread id. Never invent; empty inbox → None (SEED MAIL path)."""
        r = (ref or "").strip()
        if not r:
            return None
        try:
            threads = self.list_threads()
        except Exception:
            threads = []
        by_id = {str(th.get("id")): th for th in threads if th.get("id")}
        if r in by_id:
            return r
        if r.upper().startswith("M-"):
            needle = r.upper()
            for th in threads:
                blob = f"{th.get('id')} {th.get('subject')} {th.get('ref')} {th.get('account')}".upper()
                if needle in blob:
                    tid = th.get("id")
                    return str(tid) if tid else None
            return None  # live inbox gap / SEED MAIL chat-only — do not invent a UUID
        if _looks_uuid(r):
            if r in by_id:
                return r
            try:
                full = self._tool("get_mail_thread", {"thread_id": r})
            except Exception:
                return None
            if isinstance(full, dict) and (
                full.get("id") or full.get("thread_id") or full.get("messages") or full.get("emails")
            ):
                return str(full.get("thread_id") or full.get("id") or r)
            return None
        return None

    def create_draft(self, thread_id: str, body: str) -> str:
        """Draft only. Requires a resolved live thread UUID, or empty → standalone draft (no send)."""
        args = {"body_markdown": body, "body_text": body}
        tid = (thread_id or "").strip()
        if tid:
            if not _looks_uuid(tid):
                raise ValueError(
                    f"create_draft requires a live thread UUID after resolve_mail_id "
                    f"(got {tid[:40]!r}); BLOCK instead of inventing"
                )
            args["thread_id"] = tid
        created = self._tool("create_draft_email", args)
        if isinstance(created, dict):
            return str(created.get("id") or created.get("draft_id") or "")
        return str(created or "")

    # ---- tasks + calendar ----
    def list_tasks(self) -> list[dict]:
        return [_norm_task(x) for x in self._paged("list_tasks", {"limit": 100})]

    def create_task(self, title: str, owner: str, due: str, linked: str | None = None) -> str:
        args: dict = {"title": title, "due_date": _iso_date(due) or due}
        if _looks_uuid(owner):
            args["assignee_id"] = owner
        elif owner:
            args["description"] = f"owner: {owner}"
        if linked:
            if _looks_uuid(linked):
                args["deal_id"] = linked
            else:
                args["description"] = ((args.get("description") or "") + f"\nlinked_deal: {linked}").strip()
        created = self._tool("create_task", args)
        if isinstance(created, dict):
            return str(created.get("id") or "")
        return str(created or "")

    def list_events(self, days_back: int = 45, days_forward: int = 30) -> list[dict]:
        start = (today() - dt.timedelta(days=days_back)).isoformat()
        end = (today() + dt.timedelta(days=days_forward + 1)).isoformat()
        raw = self._paged("list_events", {"start": start, "end": end, "limit": 100})
        return [_norm_event(x) for x in raw]


def _norm_deal(x: dict) -> dict:
    title = x.get("title") or ""
    seed_id = title.split()[0] if title.startswith("D-") else None
    company = x.get("company") if isinstance(x.get("company"), dict) else {}
    stage = x.get("stage") if isinstance(x.get("stage"), dict) else {}
    owner = x.get("owner") if isinstance(x.get("owner"), dict) else {}
    out = dict(x)
    out["account"] = company.get("name") or x.get("account")
    out["arr"] = x.get("amount")
    out["stage"] = stage.get("name") or x.get("stage")
    out["stage_id"] = stage.get("id") or x.get("stage_id")
    out["owner"] = owner.get("display_name") or x.get("owner")
    out["close_date"] = _iso_date(x.get("close_date"))
    out.setdefault("notes", "")
    out.setdefault("last_activity", _iso_date(x.get("updated_at")))
    out.setdefault("stage_entered", None)
    if seed_id:
        out["seed_id"] = seed_id
    return out


def _norm_task(x: dict) -> dict:
    assignee = x.get("assignee") if isinstance(x.get("assignee"), dict) else {}
    out = dict(x)
    out["owner"] = assignee.get("display_name") or x.get("assignee_id") or x.get("owner")
    out["due"] = _iso_date(x.get("due_date") or x.get("due"))
    out["linked_deal"] = x.get("deal_id") or x.get("linked_deal")
    out.setdefault("status", x.get("status") or "open")
    return out


def _norm_event(x: dict) -> dict:
    attendees = x.get("attendees") or []
    names = []
    for a in attendees:
        if isinstance(a, dict):
            names.append(_name_of(a, "email", "display_name", "name") or "")
        else:
            names.append(str(a))
    out = dict(x)
    start = x.get("start") or x.get("starts_at") or x.get("date")
    if isinstance(start, dict):
        start = start.get("date_time") or start.get("date")
    out["date"] = _iso_date(start)
    out["attendees"] = [n for n in names if n]
    out["notes"] = x.get("description") or x.get("notes") or ""
    out.setdefault("follow_up_task", None)
    return out


if __name__ == "__main__":
    ws = McpClient()
    deals = ws.list_deals()
    msgs = ws.read_channel("agents-floor")
    def _is_bright(d):
        blob = f"{d.get('title') or ''} {d.get('seed_id') or ''}"
        return any(f"D-{n}" in blob for n in range(101, 121))
    bright = sum(1 for d in deals if _is_bright(d))
    print(f"live smoke: {len(deals)} deals ({bright} Brightline D-101..D-120 titles), {len(msgs)} agents-floor messages")
