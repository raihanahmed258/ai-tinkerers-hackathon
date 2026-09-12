# Judge Q&A: The Floor

Every answer here agrees with [claim_sheet.md](claim_sheet.md). Historical counts come from the named offline mock run; use current code rather than stale line numbers as the source of truth. Golden answer: `seed/expected_findings.md`.

## The 30-second opener

- One stuck customer leaves evidence in four tools. The Floor gives each tool a watcher with a hard lane, enforced in code, and the watchers post fact-and-id cards to an agent-only channel.
- The Desk merges same-account cards into ranked problems and posts them on the floor.
- Every action then crosses a visible gate: `ASSIGN`, `VERIFIER · approved | refused | needs_rewrite`, `DONE | BLOCKED`. Nothing writes until the floor shows approved.
- In recording mode, `--safety-demo` runs two fake unsafe asks and refuses both in public.
- Humans get one brief with at most three items. The client cannot send mail, move a stage, or touch a calendar.

## The five strongest questions

### 1. Has the current protocol ever been validated with a real model?

**Headline:** The current protocol completed live with the Sonnet 5
configuration.

The final 15:22–15:27 EDT Ambiguous round ran from commit `fd63f58`, configured
for `claude-sonnet-5`, with no fallback warning. It posted 15 findings, merged
them into six problems, ran both safety refusals, completed approved work, and
linked a clean three-item brief. `LIVE_ROUND_REPORT.md` records its message ids.

### 2. Is the Verifier a real agent, and what happens without its token?

**Headline:** The Verifier is a code gate; its verdict posts as Desk, and without a Desk token the live round dies by design.

`_verify_action` returns `approved`, `refused` or `needs_rewrite`, and `execute_actions` posts that verdict before a worker acts. There is no Verifier or Closer seat in the workspace. `McpClient.as_agent("verifier")` tries the dedicated token, then Desk, and raises `PermissionError` if neither is set; it never falls back to a human/default token.

### 3. Why is the Inbox lane empty live, and what does that do to the demo?

**Headline:** Ambiguous has no tool to inject inbound customer mail, so live Inbox posts nothing and every Inbox draft ends `BLOCKED`.

The MCP exposes `list_inbox`, `create_draft_email` and `send_email`, and nothing that creates an inbound thread. On the mock with `threads=[]`, Inbox posts 0 cards, the Desk emits no draft actions, and the round creates 0 drafts, in 73 floor posts with 14 finding cards. When a draft action does carry a mail ref the inbox cannot resolve, as it will live, the chain ends `BLOCKED · Inbox · draft` with a reason beginning `could not resolve mail id for ref=`. We forced that path offline and every such chain blocked; none wrote. That is fail-closed and it stays on screen. The workspace holds a `[SEED MAIL]` summary in `#ops-team` covering M-1, M-2, M-3, M-4 and M-9, plus three drafts placed during seeding that are not agent output. `send_email` has never been called (H3).

### 4. How much of the brief is the model's judgment?

**Headline:** Findings and merge are derived; the top three slots and their owners are a hand-written playbook prior.

`_stabilize_brief` forces Ember Grill, Pine & Salt and Copper Kettle into ranks 1 to 3 with owners theo, dana and priya, and `_ensure_golden_problems` can synthesize them if the Desk drops them. `prompts/desk.md` also names the required order. `floor.eval_unpinned --trace` measures how much those stabilizers carry. The brief only shows evidence and only invites replies when `FLOOR_REPLY_LOOP` is enabled; execution truth stays in the floor receipts.

### 5. What can it write, and what does the reply handler do?

**Headline:** Notes, drafts, tasks and floor questions only; the reply handler is implemented behind `FLOOR_REPLY_LOOP`, off by default, not demonstrated.

Four layers refuse the dangerous writes: `_normalize_action_type` at `floor/round.py` line 1072 rejects any action string naming send-without-draft, stage, close_date, propose or slot; `_verify_action` at line 1176 refuses `set_field` for every field; `execute_actions` re-checks the field at line 1360; and `McpClient.set_deal_field` at `floor/client.py` line 456 raises `PermissionError` at line 459 for stage, stage_id, close_date, pipeline, pipeline_id, owner_id and status. The client exposes `create_draft` and `list_events` and has no send method and no calendar write, and an approved-looking `set_field` on amount, arr, probability or contact_id is refused with nothing written. The reply handler in `floor/reply_handler.py`, 633 lines with `SAFE_FIELDS` and `BLOCKED_FIELDS` allowlists, runs only when `FLOOR_REPLY_LOOP=1` (H5).

## Pocket answers

| If they ask | Say |
|---|---|
| Why at most 3 items? | Attention is the scarce resource, and `post_brief` at `floor/round.py` line 1434 slices to three in code. |
| Is the router an LLM? | No. `floor/router.py` `slice_for` gives Ops deals, Inbox threads, Follow-up tasks, events and two channels, and raises if a lane leaks a key. |
| Which model? | Claude Sonnet 5 (`claude-sonnet-5`) via the Anthropic API, set in `agents.yaml`. Without the key the code uses heuristic rules and the brief is wrong. |
| What does a round cost? | The historical safety-demo mock produced roughly 113 writes plus four model-call slots. Normal mode omits seven synthetic posts, but measure one deliberate live run before scheduling. |
| Who owns the tasks? | All six go to dana, due in two days. Owner routing is weak and it is on the floor as DONE receipts. |
| What about the E-4 miss? | E-4 is a future meeting whose only "attendee left" evidence is mail M-4 in Inbox's lane, so Follow-up cannot know in pass 1. The golden answer says so in the same line. It is a Desk-merge item, and the heuristic Follow-up never emits it. |
| Is timeline state active? | No. It is opt-in with `--timeline` and writes ignored runtime state under `.floor/`, not tracked seed data. |
| Why is Ops quiet, or why is a card titled by an id? | The live CRM has no stage-entered date; the fallback Ops rules need one. A task card with no account name is keyed by its live id at the merge. Client mapping gap, owned in `floor/client.py`. |
| Is any of this real customer data? | None. Brightline Payroll and everyone in it are invented, and the whole world is in `seed/`. |

## Do not say

- Do not claim the older 17:13 UTC round used Claude. Use the final 15:22 EDT
  Sonnet 5 round.
- Do not say VERIFIER posts as Desk as a given. Say: "It posts as Desk when the Desk token is set; without it the round fails closed" (H2).
- Do not say Inbox posted findings unless one is on screen, and do not show a seeded Mail draft as agent output (H3).
- Do not say the reply loop works. Say: "Implemented behind a flag, off by default, not demonstrated" (H5).
- Do not say the brief order is the model's ranking. Say: "A playbook prior in `_stabilize_brief`; findings and merge are derived" (H7).
- Do not present a historical write count as a live billing guarantee.
- Do not say the optional timeline or reply handler was demonstrated.
- Do not claim a dedicated Verifier or Closer seat.
- Do not call it Grok Bot. It is The Floor.
