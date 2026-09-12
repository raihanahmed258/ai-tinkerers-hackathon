# The Floor, for judges who read code

**Thesis.** For an attention system, narrow watchers plus one Desk merge plus a visible verifier gate beats a free-form multi-agent swarm. A swarm optimises for agents talking. An attention system has to optimise for the one scarce thing, a human's next ten minutes. Every design choice below follows from that, and every claim points at a file in this repo at commit 54ef2e6, the checkout the recording runs from.

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

Two more things about the brief. Without `ANTHROPIC_API_KEY` the round silently uses heuristic rules and the brief is wrong: Ember Grill vanishes and item 3 is the bare task id T-1. `eval_expected` scores that AMBER. Loading the key is pre-roll blocker one. And the `Ready:` line prints planned actions from `problem.actions`, not executed ones, so a draft that BLOCKed still reads as ready. That is a bug.

## 6. Verifier-as-Desk is a seat constraint, not a cheat

There is no Verifier seat and no Closer seat in the workspace. The VERIFIER verdict posts as Desk. The identity that carries the verdict is `as_agent("verifier")` (`floor/client.py` line 321). It tries `AMBIGUOUS_TOKEN_VERIFIER`, then `AMBIGUOUS_TOKEN_DESK`, and if neither is set it raises `PermissionError`. It never falls back to the default human token. `MCP_MAPPING.md` line 40 claims a fallback the code refuses; that line is wrong and PR #6 is in flight to fix the authorship docs.

The consequence is that `python -m floor.round --live` with only the default token reads `AMBIGUOUS_API_KEY` or `AMBIGUOUS_TOKEN` (line 1570), posts the watcher findings, and dies at the first VERIFIER post inside refusal theater. Confirmed offline. Exporting `AMBIGUOUS_TOKEN_DESK` is a pre-roll blocker. Making the verifier a real seat requires exactly one thing: an Ambiguous agent named Verifier and its token in `AMBIGUOUS_TOKEN_VERIFIER`. `_worker_for_action` already routes notes to a Closer seat when `AMBIGUOUS_TOKEN_CLOSER` resolves. The seat is a token away, and fail-closed means the code will not pretend otherwise.

## 7. Tier 2 timeline: on main, not in the recording

PR #4 (`cursor/tier2-timeline-64b1`) merged to origin/main at 17:06 UTC today as 76be8d5, after the recording checkout. It adds `floor/timeline.py`: `TimelineStore`, JSON-backed, with per-account `last_decision`, `drafts_prepared`, `waiting_on`, `escalated_at`, `escalation_count`, and `should_escalate(account)`, which returns False when the account was escalated to `#attention` within the past 3 days and is waiting on a human. `run_desk_merge` then downgrades that problem to floor-only and `post_brief` logs `[Timeline] Skipped re-escalation: <account>`. It also carries `_rank_sort_key`, the fix for the rank=None crash in the ablation. That fix is therefore on origin/main but not in 54ef2e6.

I ran the merged tree on the mock from a scratch copy. The committed `seed/timeline.json` records Pine & Salt escalated 2026-09-10 and Copper Kettle, T-1, and T-4 escalated today, all waiting on human. The result is an Attention brief with zero human items. The store also saves back into `seed/timeline.json`, so a round mutates a seed file. The idea is right: an unresolved issue must not become a brand-new alert every day. The shipped state is not demo-safe and it is not behind a flag. So it is not claimed today, and the recording stays at 54ef2e6.

## 8. Non-goals

No sends. No stage moves. No close-date or calendar edits. No autonomous business decisions. No cross-round memory in the recording. No LLM router. The reply handler is implemented and only runs when `FLOOR_REPLY_LOOP=1`; while it is off, the brief makes no reply-handling promise. Live, the inbox is empty, so expect no Inbox findings and unresolved draft chains to end BLOCKED. The `[SEED MAIL]` summary and seeded drafts are not agent output. The historical safety-demo mock produced roughly 113 workspace writes; normal mode omits the seven synthetic refusal posts, and `AUTOMATIONS.md` now requires measuring the live configuration before scheduling. All six tasks in that historical run went to dana with due date today plus two.

## If we had 48 more hours

**Hours 0 to 2.** Export `AMBIGUOUS_TOKEN_DESK` and `ANTHROPIC_API_KEY`, run one live round, capture the channel. Demoable: the first end-to-end run of the current protocol against the real workspace, with VERIFIER posting as Desk.

**Hours 2 to 6.** Gate the merged timeline behind `FLOOR_TIMELINE=1`, move the store out of `seed/` into a state directory, and reset the seed so only Pine & Salt is waiting. Demoable: two mock rounds back to back, the second printing `[Timeline] Skipped re-escalation: Pine & Salt` while Ember and Copper stay in the brief.

**Hours 6 to 10.** Move E-4 from Follow-up's `SHOULD_FLAG` to a Desk-merge expectation in `eval_expected`, and add E-3 to the heuristic rule. Demoable: Follow-up scores against what it can actually see, and the eval turns GREEN on the model path.

**Hours 10 to 16.** Fix the `Ready:` line to print executed actions only. Demoable: a BLOCKed draft never appears as ready in `#attention`.

**Hours 16 to 24.** Run with `FLOOR_REPLY_LOOP=1` and a scripted reply from dana naming a new Pine & Salt contact. Demoable: the reply resolves D-105 in `apply_safe_writeback`, writes `contact` on it through `set_deal_field` (a field none of the four layers block; `SAFE_FIELDS` is only consulted for date fields), records a durable CRM note, and `confirm_on_floor` posts `Recorded: …` to the floor as Desk.

**Hours 24 to 36.** Create Verifier and Closer seats in Ambiguous, export their tokens, and remove the Desk fallback for verdicts. Demoable: `VERIFIER · refused` posted by an identity that can post nothing else.

**Hours 36 to 48.** Refresh `AUTOMATIONS.md` with the real write count, pick a twice-weekly schedule that fits the tier, and re-record. Demoable: a scheduled live round with a GREEN scorecard attached.

Word count: 1,854
