# The Floor, for judges who read code

**Thesis.** For an attention system, narrow watchers plus one Desk merge plus a visible verifier gate beats a free-form multi-agent swarm. A swarm optimises for agents talking. An attention system has to optimise for the one scarce thing, a human's next ten minutes. Every design choice below follows from that. The recording uses the completed live round indexed in `LIVE_ROUND_REPORT.md`.

## 1. Information asymmetry is the design, and it has a cost

The router is code, not a persona. `floor/router.py` `slice_for` hands Ops the deals and nothing else, Inbox the threads and nothing else, and Follow-up tasks, events, and chat from `#sales` and `#ops-team` only. If a lane returns a key outside its allowlist the function raises `RuntimeError`. No watcher sees `#agents-floor` or another watcher's cards in pass 1.

The cost shows up at E-4. That calendar event is a future Pine & Salt technical review on 2026-09-18 with attendee jordan.reyes. The only evidence that Jordan has left is mail M-4, the mailer-daemon bounce twelve days ago, and M-4 lives in Inbox's lane. `prompts/watcher_followup.md` tells Follow-up to flag a future meeting whose attendee is known from another finding to have left. Follow-up cannot know that, because the router never shows it the floor. `seed/expected_findings.md` lists E-4 under Follow-up's pass-1 findings and in the same line admits it needs M-4 from Inbox. The golden answer contradicts the router, and `floor/eval_expected.py` inherits the contradiction. So the 4/6 Follow-up score is partly a scoring error and partly a real miss: E-3, the Ember Grill check-in one day ago, is not caught either because the heuristic rule only fires on meetings more than seven days past. The Desk merge is the only seat that can put D-105, M-4, and E-4 together, and today E-4 reaches the P4 evidence only if some card mentions it.

## 2. Tool allowlists, four layers deep

A swarm's safety story is a prompt. The Floor's is four checks a judge can trace.

1. `_normalize_action_type` (`floor/round.py` line 1072) returns `refused` for any action string containing send without draft, stage, close_date, propose, or slot.
2. `_verify_action` (line 1160) approves only `add_note`, `draft`, `assign_task`, `ask`, and `flag_event`. `set_field` is not in that tuple (line 1176), so `set_field` can never be approved for any field, including amount, arr, probability, and contact_id. I tested those. Nothing was written.
3. `execute_actions` (line 1360) re-checks the field name even if a verdict somehow slipped through.
4. `McpClient.set_deal_field` (`floor/client.py` line 457) raises `PermissionError` for stage, stage_id, close_date, pipeline, pipeline_id, owner_id, and status.

Underneath all four, `WorkspaceClient` exposes `create_draft` and `list_events` and has no send method and no calendar write. The live MCP server does offer `send_email`. This code never calls it.

## 3. Auditability: the floor is a readable protocol

Every round writes the same ordered label chain to `#agents-floor`. Pass 1 posts FINDING cards, 8 Ops, 6 Inbox, 6 Follow-up on the mock. Pass 2 posts five PROBLEM cards ranked 1 to 5. Then the refusal block. Then for every action: `ASSIGN · <worker> → <action>`, `VERIFIER · approved | refused | needs_rewrite`, and `DONE` or `BLOCKED`. On the mock that is 7 Ops notes, 5 Inbox drafts, 6 Follow-up tasks, and 1 Desk ask, each as a three-post chain. A worker never executes a refused assignment, because the verdict is posted before the worker acts. A judge can read the channel top to bottom and reconstruct who decided what, in what order, with no log file. That is the audit boundary a swarm cannot give you, because in a swarm the ordering is emergent.

## 4. Refusal theater versus real refusal

With `--safety-demo`, `_refusal_theater` runs before productive work. It builds two fake requests, "send email to customer" and `set_field` with field stage, and pushes them through the same gates real actions use. Both post `VERIFIER · refused` and then `BLOCKED`. The requests are explicitly fake; normal rounds omit them. A genuine send or protected field change still dies at the same code gates.

## 5. The brief is the scarce resource, and its order is a prior

`post_brief` (line 1434) sorts human items by rank and slices `[:3]` in code. Three is not a prompt suggestion. Then the honest part. `_stabilize_brief` (line 792) forces Ember Grill, Pine & Salt, and Copper Kettle into ranks 1 to 3 with owners theo, dana, and priya when they exist as problems. It holds a hardcoded `_NEVER_BRIEF` list (Bluebird, Meridian, Juniper, Saffron, Dockside, Wren, Gold Leaf, Cobalt, Two Forks, Alder Street) and a `_FLOOR_ONLY` list (Sunset Taco, Harbor Fish, Marigold, Fig & Thistle, Northgate, Prairie Table, plus the generic labels "all customers" and "pipeline review") out of the human slots. `_ensure_golden_problems` (line 747) will synthesise any of the three with canned cause text if the Desk drops it. `prompts/desk.md` spells out the expected merges and the required order by name.

The findings and the merge are derived. The priority order is a hand-written playbook prior. `floor/eval_unpinned.py --trace` measures it. On the heuristic path, with the stabilisers off the brief is Marigold, Sunset Taco, Harbor Fish. With them on it is Pine & Salt, Copper Kettle, T-1. Nothing was invented and backfill did not fire. Only the order changed. I defend the prior as what an ops lead would write down on day one: penalties and lost champions beat quiet deals. I do not defend it as learned behaviour.

One more thing about the brief. Without `ANTHROPIC_API_KEY` the round uses heuristic rules and the brief is wrong: Ember Grill vanishes and item 3 is the bare task id T-1. `eval_expected` scores that AMBER. Loading the key is pre-roll blocker one. The old misleading `Ready:` line has been removed; execution truth stays in `DONE` and `BLOCKED` floor receipts.

## 6. Verifier-as-Desk is a seat constraint, not a cheat

There is no Verifier seat and no Closer seat in the workspace. The VERIFIER verdict posts as Desk. The identity that carries the verdict is `as_agent("verifier")` (`floor/client.py` line 321). It tries `AMBIGUOUS_TOKEN_VERIFIER`, then `AMBIGUOUS_TOKEN_DESK`, and if neither is set it raises `PermissionError`. It never falls back to the default human token. `MCP_MAPPING.md` line 40 claims a fallback the code refuses; that line is wrong and PR #6 is in flight to fix the authorship docs.

`python -m floor.round --live` now preflights the default workspace token, Desk-or-Verifier token, and optional MCP dependency before posting anything. Exporting `AMBIGUOUS_TOKEN_DESK` remains a pre-roll blocker. A dedicated Verifier seat can instead use `AMBIGUOUS_TOKEN_VERIFIER`; fail-closed means the code will not pretend a human/default identity is that role.

## 7. Tier 2 timeline: opt-in, not in the recording

`floor/timeline.py` provides JSON-backed cross-round state and can suppress a
repeat escalation while an account is waiting on a human. It now runs only with
`--timeline` and stores runtime state under ignored `.floor/` by default, rather
than mutating tracked seed data. The behavior is not shown in the live round,
so do not claim it in the demo.

## 8. Non-goals

No sends. No stage moves. No close-date or calendar edits. No autonomous business decisions. No cross-round memory in the recording. No LLM router. The reply handler is implemented and only runs when `FLOOR_REPLY_LOOP=1`; while it is off, the brief makes no reply-handling promise. Live, the inbox is empty, so expect no Inbox findings and unresolved draft chains to end BLOCKED. The `[SEED MAIL]` summary and seeded drafts are not agent output. The historical safety-demo mock produced roughly 113 workspace writes; normal mode omits the seven synthetic refusal posts, and `AUTOMATIONS.md` now requires measuring the live configuration before scheduling. All six tasks in that historical run went to dana with due date today plus two.

## If we had 48 more hours

**First.** Capture a runner log alongside a deliberate live round so model
provenance and created workspace objects can be matched independently.

**Next.** Exercise the opt-in timeline with two mock rounds back to back, the
second printing `[Timeline] Skipped re-escalation: Pine & Salt` while other
eligible accounts remain in the brief.

**Hours 6 to 10.** Move E-4 from Follow-up's `SHOULD_FLAG` to a Desk-merge expectation in `eval_expected`, and add E-3 to the heuristic rule. Demoable: Follow-up scores against what it can actually see, and the eval turns GREEN on the model path.

**Later, only if needed.** Run with `FLOOR_REPLY_LOOP=1` and a scripted reply from dana naming a new Pine & Salt contact. Demoable: the reply resolves D-105, records a durable CRM note, and confirms on the floor as Desk.

**Hours 24 to 36.** Create Verifier and Closer seats in Ambiguous, export their tokens, and remove the Desk fallback for verdicts. Demoable: `VERIFIER · refused` posted by an identity that can post nothing else.

**Hours 36 to 48.** Refresh `AUTOMATIONS.md` with the real write count, pick a twice-weekly schedule that fits the tier, and re-record. Demoable: a scheduled live round with a GREEN scorecard attached.

Word count: 1,854
