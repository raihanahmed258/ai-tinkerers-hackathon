# The Floor — always-on agent teammates that do the attention job

Built at **AI Tinkerers Ottawa — Agents, Everywhere** (September 2026).

Three narrow watchers, one Desk that merges and decides, an agent-only channel where they coordinate, and a three-item brief for humans.

> **Tier 1 live demo:** The visible handoff is `ASSIGN → VERIFIER · approved | refused | needs_rewrite → DONE | BLOCKED`. The Ambiguous-only shot list is [`demo/script.md`](demo/script.md); it is the source of truth for what the live recording claims.

**The problem.** At a small company one stuck customer does not arrive as one alert. It arrives as four weak signals nobody connects: a deal gone quiet in the CRM, an email nobody answered, an overdue task, and a promise someone made in chat and never kept. No human's job is to read all four every morning, so things slip. The quote never goes out. The kickoff never gets booked. The champion leaves. The filing deadline passes.

**The shape of the fix.** A small floor of always-on agents that each watch one slice, post what they see to a channel of their own, and let one of them merge the pieces back into single problems. Humans get at most three of them a day.

Nothing here is from any real company. Brightline Payroll, its people and its customers are invented.

---

## How a round works

A round is exactly two passes. It cannot loop.

**Pass 1 — the watchers sweep.** Each one sees only its own slice and posts short FINDING cards to `#agents-floor`: account, ref, what, why it is stalled, evidence, and whether a human is needed. Facts and dates only, never opinions about people.

| Agent | Watches | Looking for |
|---|---|---|
| **Ops** | CRM | stalled stages, zombie close dates, Closed Won with no kickoff |
| **Inbox** | Mail | unanswered customer threads, bounces, deadline and penalty language |
| **Follow-up** | Calendar, Tasks, chat promises | overdue tasks, meetings with no follow-up, promises never kept |

**Pass 2 — the Desk decides.** The Desk watches no app. It reads the floor, merges findings that are the same problem seen from different tools, and posts a bounded `ASSIGN`. A Verifier gate emits `approved`, `refused`, or `needs_rewrite`; an approved worker reports `DONE` or `BLOCKED` on the floor. The Desk posts one ranked brief to `#attention` with at most three human items.

The merge is the point. Copper Kettle is one problem with four fingerprints (`D-101` in the CRM, `M-1` in Mail, `T-1` overdue in Tasks, `E-1` a meeting that went nowhere), not four notifications.

## Safety by construction

Two different strengths of guarantee here, and they are worth keeping apart. Some things the agents *cannot* do because the capability does not exist in the client. Others they *do not* do because the prompts forbid it. Both matter. Only the first kind survives a bad model day.

**Structural. The method does not exist.**

- **Nothing is ever sent to a customer.** `WorkspaceClient` exposes `create_draft` and no send of any kind. There is no code path from an agent to a customer's inbox, so `send_email` cannot be called by mistake.
- **No calendar is ever modified.** The client can `list_events` and nothing else. No create, no update, no delete.
- **Nothing is ever deleted.** No delete method exists anywhere on the interface.
- **Two passes.** The round is a fixed sequence, not a loop with an exit condition, so it cannot run long.
- **At most three human items.** The cap is applied in code after the Desk decides, not requested of the model.

**Enforced by prompt and honoured in practice, but the capability is there.**

- **Stage and close-date changes.** The Tier 1 Verifier refuses moves to either field before a worker can act. Each round visibly tests that boundary with a fake `move stage` request; no real stage or close-date change is made.
- **Facts and dates, never opinions about people.** The "never" list in `agents.yaml`, reinforced in every playbook, plus a filter in code that drops findings containing feeling-words about customers or judgements about colleagues.

**Read-heavy, write-light either way.** Tier 1 keeps the visible worker surface to bounded internal work and floor messages; it never sends customer mail or moves stages or close dates. The Verifier refuses and logs work outside that boundary.

---

## Run it

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python -m floor.seed     # 20 deals, 12 threads, 9 tasks, 9 events, 26 chat messages
.venv/bin/python -m floor.round    # one full round against the in-memory mock
```

The mock path runs on **Python 3.9 or newer**, which is what macOS ships, so the offline round works on a stock Mac with nothing installed. The live path additionally needs **Python 3.10 or newer** and the `mcp` package, which is commented out of `requirements.txt` for exactly that reason:

```bash
.venv/bin/pip install "mcp>=1.0"   # only for --live
```

### Mock vs live

| Mode | Command | What it talks to |
|---|---|---|
| **Mock** (default) | `python -m floor.round` | `MockClient`, entirely offline and in memory. Every post, draft, note and task prints to the terminal. |
| **Live** | `python -m floor.round --live` | `McpClient` against an Ambiguous workspace over MCP (Streamable HTTP). Needs `AMBIGUOUS_API_KEY` or `AMBIGUOUS_TOKEN`; URL defaults to `https://app.ambiguous.ai/mcp` and `AMBIGUOUS_MCP_URL` overrides it. |

Tool-by-tool mapping from this repo's `WorkspaceClient` interface to the real Ambiguous tool names is in [`MCP_MAPPING.md`](MCP_MAPPING.md). What got seeded into the live workspace, and with which ids, is in [`SEED_REPORT.md`](SEED_REPORT.md).

### The model key is not optional

Set `ANTHROPIC_API_KEY` (in `.env` or the environment) before you trust a run. The model is `claude-sonnet-4-5`, set in `agents.yaml › defaults.model`.

There is a heuristic fallback that runs when the key is missing or a model call throws, so the round always produces output. **It is a smoke test, not the product.** Without the key the brief comes out materially wrong: the highest-priority item disappears and one item degenerates into a bare task id. If you are recording, demoing, or judging this, confirm the key is loaded first.

```bash
.venv/bin/python -c "import os,dotenv; dotenv.load_dotenv('.env'); print('key loaded:', bool(os.environ.get('ANTHROPIC_API_KEY')))"
```

### Scoring a run

For the short evaluation flow and the meaning of `GREEN`, `AMBER`, and `RED`, see [`demo/evals.md`](demo/evals.md). Keep evaluations outside the Ambiguous-only recording.

The seed was built so a good round is checkable rather than a matter of taste, and [`seed/expected_findings.md`](seed/expected_findings.md) is the golden answer. `floor/eval_expected.py` scores a captured round against it:

```bash
.venv/bin/python -m floor.round | tee run.txt
.venv/bin/python -m floor.eval_expected run.txt
```

It reports per-watcher recall against the golden refs, every healthy control that got flagged when it should have stayed silent, whether the brief respects the three-item cap, whether the three items came out in the expected order, and whether anything resembling a customer send appears in the log. It exits 0 on green, 1 on amber, 2 on red, so it can gate a commit.

Amber is the interesting state. It means nothing forbidden happened but the brief is not in golden order, which is the difference between a run that demos and a run that quietly drops its lead item. Scoring the validated reference log gives:

```
Round scorecard · MOCK_ROUND_VALIDATE3.txt · GREEN
Finding cards: 17     Golden refs surfaced: 13/17
  ops       6/6
  inbox     2/5   missed: M-1, M-2, M-9
  followup  5/6   missed: E-4
  rank 1: @theo / Ember Grill ✓
  rank 2: @dana / Pine & Salt ✓
  rank 3: @priya / Copper Kettle Group ✓
Violations: none. No control flagged, cap respected, nothing sent.
```

Ops is at ceiling and the brief lands in the right order. Inbox recall is the known weak spot and the honest number to quote. If Bluebird (`D-106`) ever shows up flagged, the logic has gone too eager, and the healthy controls are in the seed to catch exactly that.

---

## What works today, and what does not

A validated mock round with the real model key on 2026-09-12 produced: **17 finding cards** on the floor (8 Ops, 3 Inbox, 6 Follow-up), **21 floor posts** in total, **3 tasks** created, and **one brief with exactly 3 human items** ranked Ember Grill, then Pine & Salt, then Copper Kettle. Every healthy control stayed unflagged. The raw log is [`MOCK_ROUND_VALIDATE3.txt`](MOCK_ROUND_VALIDATE3.txt) and the scorecard is [`MOCK_VALIDATE_REPORT3.md`](MOCK_VALIDATE_REPORT3.md).

Being straight about the edges, because a demo that overclaims is worse than one that concedes:

- **The Desk's merge is visible in the brief, not on the floor.** Merged evidence shows up as the brief's `Evidence:` line joining a deal, a task and an event for one account. The Desk does not currently post a per-finding `PROBLEM` block in each card's thread.
- **Notes and drafts are wired but did not fire in the validated run.** `add_deal_note` and `create_draft` are implemented and exercised by the heuristic path. In the validated model run the Desk chose tasks and questions instead, so that log contains no CRM note and no draft.
- **The refusal is real code, not a visible demo moment.** Nothing in a normal round trips the allowlist, so you prove it by reading `execute_actions`, not by watching it happen.
- **The allowlist is wider than the playbooks.** `set_field` is in it and the live client can write a stage or a close date, so the no-stage-change guarantee is a prompt, not a wall. Nothing exercised it in the validated run. Better to say that than to claim a wall that is not there.
- **The human reply loop is designed and stubbed, not wired.** `reply_loop` exists with the intended shape and is commented out of `run_round`. A human answering in the brief thread and the Desk writing it back to the CRM is the next piece of work, not a thing to claim today.
- **Live Mail has no inbound.** Ambiguous exposes `list_inbox`, `create_draft_email` and `send_email` but nothing to inject fictional inbound customer mail, so the Inbox watcher has nothing to read against the live workspace. Mitigated by a `[SEED MAIL]` summary in `#ops-team` covering `M-1`, `M-2`, `M-3`, the `M-4` bounce and `M-9`, plus three draft emails. `send_email` was never called. The honest path for Inbox is the mock, and saying so out loud costs nothing.

---

## Layout

```
agents.yaml                  the roster: who watches what, allowed tools, the "never" list, round shape
seed/                        the fictional company (day-offset dates → always fresh)
  company.json               people, channels
  crm_deals.json             20 deals — 6 stalled for different reasons, the rest controls
  mail_threads.json          12 threads — 5 unanswered incl. a bounce, plus spam/HR distractors
  chat_history.json          #sales and #ops-team with promises that were never kept
  calendar_events.json       orphaned customer meetings, a meeting with a departed attendee
  tasks.json                 overdue tasks tied to the same problems
  expected_findings.md       the golden answer: cards, merges, the 3 human items
prompts/                     system prompts for Ops, Inbox, Follow-up, Desk + the card/brief format
floor/
  client.py                  WorkspaceClient interface · MockClient (offline) · McpClient (live, over MCP)
  seed.py                    loads the seed into any client
  round.py                   the two-pass round: watchers → Desk merge → actions → brief
  eval_expected.py           scores a captured round against the golden answer
demo/
  script.md                  the two-minute video, timed
  submission.md              title, written description, social post
  judge_qa.md                answers to the questions judges actually ask
  PROJECT_DESCRIPTION.md     the long-form writeup
  judge_pitch.md             30-second and 2-minute pitch outlines
AUTOMATIONS.md               running the round on a weekday schedule, with the budget math
MCP_MAPPING.md               WorkspaceClient → real Ambiguous tool names
SEED_REPORT.md               what got seeded live, with ids
MOCK_ROUND_VALIDATE3.txt     raw log of the validated round
MOCK_VALIDATE_REPORT3.md     scorecard for that round, control by control
```

## Prep versus build

Judges are owed the line between the two, so here it is. Prepared before the event: the fictional company and its seed, the roster in `agents.yaml`, the prompt drafts, `MockClient` so the logic could be developed offline, the MCP mapping, and the demo and submission text. Built during the event: the round itself in `floor/round.py`, meaning the watcher calls, the Desk merge, the closed action set, and the brief.

## Design decisions worth saying out loud

- **Narrow agents beat one broad one.** Each sees a slice and the merge happens at the Desk, which is why one customer arrives as one problem instead of four alerts.
- **The agent channel is the audit trail.** Every decision is a message a human can read afterwards.
- **Human attention is the scarce resource.** Three items, ranked. Everything else is handled and logged.
- **Two passes, no loops.** The round is bounded by construction.
- **Read-heavy, write-light.** Notes, drafts and tasks, with a closed allowlist behind them.
- **Facts and dates, never opinions about people.**

## If the live workspace fights you

Run the whole thing on `MockClient` with the terminal as the floor. It still shows the multiplayer merge and the brief, it is fully honest, and the workspace adapter is an hour of work you can name out loud. Working beats wired.
