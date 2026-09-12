# Ambiguous MCP ↔ WorkspaceClient map

Connected as Cursor MCP server `user-ambiguous` (`https://app.ambiguous.ai/mcp`).
API key scopes: `chat.*,crm.*,mail.*,tasks.*,calendar.*`.

The key is still named `grokbot` in the Ambiguous console, which is a leftover from an earlier working name and not what this project is called. Rename it there before anyone browses the workspace. The project is The Floor.

| WorkspaceClient method | Ambiguous tool | Notes |
|---|---|---|
| `read_channel(channel, since_hours)` | `list_channels` → resolve name to id; then `get_channel_messages` | Channel IDs are UUIDs. Filter by timestamp client-side for `since_hours`. |
| `post(channel, text, thread_id)` | `send_message` | Args: `channel_id`, `content` (Markdown), optional `thread_id`. |
| `list_deals()` | `list_deals` | Filter pipeline/stage/status as needed. |
| `add_deal_note(deal_id, note)` | `log_activity` | Activity type = note on the deal timeline. |
| `set_deal_field(deal_id, field, value)` | `update_deal` | Pass only fields to change (stage, amount, custom props, etc.). |
| `list_threads()` | `list_inbox` (+ `get_mail_thread` for body) | Kit “threads” ≈ inbox + thread fetch. |
| `create_draft(thread_id, body)` | `create_draft_email` | Drafts only — never `send_email` in the demo. |
| `list_tasks()` | `list_tasks` | |
| `create_task(title, owner, due, linked)` | `create_task` | Map `owner` → `assignee_id`; link deal if the schema allows. |
| `list_events(days_back, days_forward)` | `list_events` | Pass date-range filters. |

## Channel IDs (hackathon-aitinkerers, 2026-09-12)

| name | id |
|---|---|
| agents-floor | `6606389e-0977-415a-987e-599001037834` |
| attention | `8db08df8-60fe-4366-beef-fb13163d73ef` |
| sales | `b0781716-0fd8-4b5a-b110-0842cc6f294e` |
| ops-team | `52661440-bb72-4207-8199-1c31857d6c45` |
| general | `9e6b988f-0f23-43d9-909e-0330fe59d8c2` |
| admin-alerts | `81254594-e1c5-41e7-a253-ded65e6d4662` |

## Client

`floor/client.py` `McpClient` is implemented (Streamable HTTP via the `mcp` package). Return shapes stay close to `MockClient`.

## Agent tokens / Verifier identity

`McpClient.as_agent(agent_id)` switches to `AMBIGUOUS_TOKEN_<AGENT>` / `AMBIGUOUS_API_KEY_<AGENT>` when set (see `AGENT_TOKEN_ENV` in `floor/client.py`).

Without a dedicated Verifier or Closer token, those roles fall back to the **Desk** token. They never fall back to the human/default token; if Desk is also unset, `as_agent` raises `PermissionError`. Ops, Inbox, and Follow-up may use the default token when neither their own token nor Desk is configured. See `.env.example`.

## Mail id resolution (live UUID / seed M-*)

`WorkspaceClient.resolve_mail_id(ref)` (Mock + Mcp) maps seed `M-*` or a live thread UUID → a real inbox thread id. It **never invents** an id. Unresolved refs (empty live inbox / SEED MAIL chat-only / junk) return `None`; `execute_actions` draft branch must **BLOCKED** with a clear reason — no silent DONE / fake approve. Live `create_draft` requires a UUID after resolve (or empty for a standalone draft); never pass raw `M-*` to MCP.
