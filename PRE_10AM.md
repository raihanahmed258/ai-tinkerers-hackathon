# Pre-10:00 checklist — The Floor (2026-09-12)

> **Historical.** This was the pre-event checklist. The build has since happened, so where this file and the README disagree, the README is current.

America/Toronto. Event build starts 11:15. Do not fill `floor/round.py` TODOs before then.

## Done

- [x] Mock seed: **20 deals, 12 threads, 9 tasks, 9 events, 26 chat messages** across 4 channels
- [x] `python -m floor.round` still raises `NotImplementedError` at `run_watcher` (correct)
- [x] `McpClient` implemented in `floor/client.py` (Streamable HTTP via the `mcp` package)
- [x] Live smoke: `list_deals()` → **20 deals** including `D-101` Copper Kettle / `D-102` Marigold / `D-105` Pine & Salt / `D-107` Ember Grill; `read_channel("agents-floor")` → **0** (channel left clean for the demo)
- [x] Workspace already seeded — see `SEED_REPORT.md`. `#agents-floor` / `#attention` left clean

## Intentionally left for 11:15

Five functions in `floor/round.py` **must stay `raise NotImplementedError`** until the day-of build:

1. `run_watcher` — rung 1 (Ops cards on the floor)
2. `run_desk_merge` — rung 2/3
3. `execute_actions` — rung 3 (closed action set; refuse anything else)
4. `post_brief` — rung 2 (`#attention`, ≤3 human items)
5. `reply_loop` — rung 4

## Run mock (offline, no token)

System Python is PEP 668 — use the kit venv:

```bash
cd /workspace/the-floor/floor-kit
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt   # first time
.venv/bin/python -m floor.seed          # 20 / 12 / 9 / 9 / 26
.venv/bin/python -m floor.round         # NotImplementedError at run_watcher — expected
```

## Run live (workspace, not a full round)

Token: process env `AMBIGUOUS_API_KEY` or `AMBIGUOUS_TOKEN` (McpClient also reads box-secrets if env is unset).  
Default URL: `https://app.ambiguous.ai/mcp` (`AMBIGUOUS_MCP_URL` overrides).

```bash
cd /workspace/the-floor/floor-kit
.venv/bin/python -m floor.client        # smoke: deal count + agents-floor count; no secrets
.venv/bin/python -m floor.round --live  # still stops at run_watcher until 11:15
```

`--live` accepts `AMBIGUOUS_API_KEY` as a token alias.

## Mail limitation (Inbox watcher)

Ambiguous MCP has **no tool to inject fictional inbound customer threads**. Live inbox is empty.

Already mitigated in the workspace:

- `[SEED MAIL]` summary in `#ops-team` (M-1, M-2, M-3, M-4 bounce, M-9)
- Three **drafts only** (Copper Kettle / Marigold / Ember Grill) — **`send_email` was never called**

At 11:15: run Inbox against the mock, or teach it to read `#ops-team` SEED MAIL + drafts. Never send.

## Model key reminder

**Resolved during the build, kept here so the record is straight.** This
paragraph used to say the model was `gpt-5.1` and to set `OPENAI_API_KEY`. The
build runs on Claude. `agents.yaml` › `defaults.model` is `claude-sonnet-5` and
the key is `ANTHROPIC_API_KEY`, read from `.env` at the repo root.

Without that key the mock still runs, but it silently falls back to heuristic rules and the brief comes out wrong: the top item disappears and one item degrades to a bare task id. Treat a missing key as a hard failure rather than a degraded mode. Confirm it loaded before recording:

```bash
.venv/bin/python -c "import os,dotenv; dotenv.load_dotenv('.env'); print('key loaded:', bool(os.environ.get('ANTHROPIC_API_KEY')))"
```

## Do not

- Implement the five `round.py` TODOs before 11:15
- Contact Project 1 bots
- Call `send_email` or post customer-facing mail
