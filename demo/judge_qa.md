# Judge Q&A: The Floor

Every answer here agrees with [claim_sheet.md](claim_sheet.md). Numbers come from the offline mock on the heuristic path, run on current `main` (HEAD `54ef2e6`), or from a named file and line. Golden answer: `seed/expected_findings.md`.

## The 30-second opener

- One stuck customer leaves evidence in four tools. The Floor gives each tool a watcher with a hard lane, enforced in code, and the watchers post fact-and-id cards to an agent-only channel.
- The Desk merges same-account cards into ranked problems and posts them on the floor.
- Every action then crosses a visible gate: `ASSIGN`, `VERIFIER · approved | refused | needs_rewrite`, `DONE | BLOCKED`. Nothing writes until the floor shows approved.
- Before any worker acts, every round runs two fake unsafe asks, send a customer email and move a stage, and refuses both in public.
- Humans get one brief with at most three items. The client cannot send mail, move a stage, or touch a calendar.

## The five strongest questions

### 1. Has the current protocol ever been validated with a real model?

**Headline:** No. The only model-backed validation artifact predates the protocol, and no end-to-end live run exists yet.

`MOCK_ROUND_VALIDATE3.txt` was committed at 15:43 UTC and the `ASSIGN`, `VERIFIER`, `DONE`, `BLOCKED` protocol landed at 16:54 UTC; the file contains none of those labels. What we have verified is the current code on the offline mock without a key: 20 findings, 5 problem cards, 2 refusals, 7 notes, 5 drafts, 6 tasks, 1 ask, 94 floor posts plus 1 brief, zero healthy controls flagged, golden recall 14 of 17. The live recording is the first end-to-end run of this protocol against the workspace, and the pre-roll in `demo/script.md` says how to confirm it before the take. Any doc that cites the old validation as proof of the current protocol is wrong (H1).

### 2. Is the Verifier a real agent, and what happens without its token?

**Headline:** The Verifier is a code gate; its verdict posts as Desk, and without a Desk token the live round dies by design.

`_verify_action` at `floor/round.py` line 1160 returns `approved`, `refused` or `needs_rewrite`, and `execute_actions` at line 1288 posts that verdict as `VERIFIER` before any worker acts. There is no Verifier seat and no Closer seat in the workspace; seats are Ops, Inbox, Follow-up and Desk. `McpClient.as_agent("verifier")` at `floor/client.py` line 321 tries `AMBIGUOUS_TOKEN_VERIFIER`, then `AMBIGUOUS_TOKEN_DESK`, and raises `PermissionError` if neither is set, so a live round with only the default token posts the watcher findings and then stops at the first VERIFIER post. We confirmed that offline. `MCP_MAPPING.md` line 40 claims a fallback to the default token; the code refuses it and the doc line is wrong (H2).

### 3. Why is the Inbox lane empty live, and what does that do to the demo?

**Headline:** Ambiguous has no tool to inject inbound customer mail, so live Inbox posts nothing and every Inbox draft ends `BLOCKED`.

The MCP exposes `list_inbox`, `create_draft_email` and `send_email`, and nothing that creates an inbound thread. On the mock with `threads=[]`, Inbox posts 0 cards, the Desk emits no draft actions, and the round creates 0 drafts, in 73 floor posts with 14 finding cards. When a draft action does carry a mail ref the inbox cannot resolve, as it will live, the chain ends `BLOCKED · Inbox · draft` with a reason beginning `could not resolve mail id for ref=`. We forced that path offline and every such chain blocked; none wrote. That is fail-closed and it stays on screen. The workspace holds a `[SEED MAIL]` summary in `#ops-team` covering M-1, M-2, M-3, M-4 and M-9, plus three drafts placed during seeding that are not agent output. `send_email` has never been called (H3).

### 4. How much of the brief is the model's judgment?

**Headline:** Findings and merge are derived; the top three slots and their owners are a hand-written playbook prior.

`_stabilize_brief` at `floor/round.py` line 792 forces Ember Grill, Pine & Salt and Copper Kettle into ranks 1 to 3 with owners theo, dana and priya, holds a `_NEVER_BRIEF` list of ten healthy accounts and a `_FLOOR_ONLY` list of eight entries, six accounts plus two generic labels, out of the human slots, and `_ensure_golden_problems` at line 747 synthesises any of the three with canned cause text if the Desk drops it. `prompts/desk.md` also names the expected merges and the required order. On the heuristic path with the stabilisers off, the brief becomes Marigold, Sunset Taco, Harbor Fish; with them on it is Pine & Salt, Copper Kettle, T-1, and the trace shows only `_stabilize_brief` changed the order. `floor/eval_unpinned.py --trace` measures it (H7). Two more things on that brief: the `Ready:` line prints planned actions from `problem.actions`, not executed ones, so a draft that BLOCKed still reads `Ready: draft reply` (H4); and the closing line `Reply in this thread and I'll record it.` is appended unconditionally in `post_brief` (H5).

### 5. What can it write, and what does the reply handler do?

**Headline:** Notes, drafts, tasks and floor questions only; the reply handler is implemented behind `FLOOR_REPLY_LOOP`, off by default, not demonstrated.

Four layers refuse the dangerous writes: `_normalize_action_type` at `floor/round.py` line 1072 rejects any action string naming send-without-draft, stage, close_date, propose or slot; `_verify_action` at line 1176 refuses `set_field` for every field; `execute_actions` re-checks the field at line 1360; and `McpClient.set_deal_field` at `floor/client.py` line 456 raises `PermissionError` at line 459 for stage, stage_id, close_date, pipeline, pipeline_id, owner_id and status. The client exposes `create_draft` and `list_events` and has no send method and no calendar write, and an approved-looking `set_field` on amount, arr, probability or contact_id is refused with nothing written. The reply handler in `floor/reply_handler.py`, 633 lines with `SAFE_FIELDS` and `BLOCKED_FIELDS` allowlists, runs only when `FLOOR_REPLY_LOOP=1` (H5).

## Pocket answers

| If they ask | Say |
|---|---|
| Why at most 3 items? | Attention is the scarce resource, and `post_brief` at `floor/round.py` line 1434 slices to three in code. |
| Is the router an LLM? | No. `floor/router.py` `slice_for` gives Ops deals, Inbox threads, Follow-up tasks, events and two channels, and raises if a lane leaks a key. |
| Which model? | `claude-sonnet-4-5` via the Anthropic API, set in `agents.yaml`. Without the key the code uses heuristic rules and the brief is wrong. |
| What does a round cost? | About 113 workspace writes plus 4 model calls. `AUTOMATIONS.md` says 25 writes; that is stale. A weekday schedule would exhaust a 1,000-action tier in under two weeks. |
| Who owns the tasks? | All six go to dana, due in two days. Owner routing is weak and it is on the floor as DONE receipts. |
| What about the E-4 miss? | E-4 is a future meeting whose only "attendee left" evidence is mail M-4 in Inbox's lane, so Follow-up cannot know in pass 1. The golden answer says so in the same line. It is a Desk-merge item, and the heuristic Follow-up never emits it. |
| What is in flight? | PR #4 timeline and `rank=None` fix merged to GitHub `main` after the recording checkout and are not in what you are watching; on that code the seeded timeline zeroes the brief. PR #6 authorship docs open, PR #7 closed unmerged. |
| Why is Ops quiet, or why is a card titled by an id? | The live CRM has no stage-entered date; the fallback Ops rules need one. A task card with no account name is keyed by its live id at the merge. Client mapping gap, owned in `floor/client.py`. |
| Is any of this real customer data? | None. Brightline Payroll and everyone in it are invented, and the whole world is in `seed/`. |

## Do not say

- Do not say the current protocol has a validated model run. Say: "The validation artifact predates the protocol; the live recording is the first end-to-end run" (H1).
- Do not say VERIFIER posts as Desk as a given. Say: "It posts as Desk when the Desk token is set; without it the round fails closed" (H2).
- Do not say Inbox posted findings unless one is on screen, and do not show a seeded Mail draft as agent output (H3).
- Do not read the `Ready:` line or point at it (H4).
- Do not say the reply loop works. Say: "Implemented behind a flag, off by default, not demonstrated" (H5).
- Do not say the brief order is the model's ranking. Say: "A playbook prior in `_stabilize_brief`; findings and merge are derived" (H7).
- Do not quote `AUTOMATIONS.md` budget numbers (H8).
- Do not say the `rank=None` crash is fixed or that the timeline is on `main` (H10, H11).
- Do not claim a dedicated Verifier or Closer seat.
- Do not call it Grok Bot. It is The Floor.
