# Judge Q&A — The Floor

> **Why this deserves to win:** Most agent demos hand a human one more thing to read, and The Floor is four agents whose whole job is to take things away: in one recorded run it read 20 deals, 12 mail threads, 9 tasks, 9 calendar events and 26 chat messages, posted 21 messages to an agent-only channel, and gave people exactly three named items, and the full audit trail is in `MOCK_ROUND_VALIDATE3.txt`.

Source of truth for every number below: `MOCK_ROUND_VALIDATE3.txt` (mock mode, real `ANTHROPIC_API_KEY`, `claude-sonnet-4-5`). Golden answer: `seed/expected_findings.md`. Scorer: `python -m floor.eval_expected run.txt` grades a log against the golden refs and exits non-zero on amber or red. Ablation: `python -m floor.eval_unpinned --trace` re-runs the round with the four stabilisers replaced by identity functions and diffs the result.

---

## 1. Why four agents instead of one big agent?

**Say first:** Because no single agent had enough context to solve the biggest item, and the merge is what made it solvable.

Pine & Salt is the proof of the design, and I will be precise about which half is the model. Nothing in the CRM explains the stall, so the D-105 card reads `why_stalled: unclear`. In this log that card is deterministic. `_ops_backfill` in `floor/round.py` posts D-101 and D-105 when the Ops model skips a must-flag stall, and that is why their evidence line is just the bare ref. Inbox, reading only mail, found the bounce from 2026-08-31 and quoted the mailer-daemon verbatim. That half is model-written, and it is the card Ops could never write from the CRM. Neither card is actionable alone. The Desk merged them into brief item 2 with `Evidence: D-105, M-4`, and you can check that the Desk wrote it rather than the backstop: `_ensure_golden_problems` has a hardcoded cause string for Pine & Salt, and the brief says something different, naming the bounced address and the date.

**If pushed:** Ember Grill is the same shape across the other two watchers. Inbox caught the customer's line about penalties after Sept 15 in M-3, Follow-up caught T-4 eight days overdue and the E-3 check-in with no notes, and the merge made it brief item 1 for @theo. The narrow slice is why no watcher can see outside its lane. That is `slice_for` in `floor/round.py:41`: Ops gets deals, Inbox gets threads, Follow-up gets tasks, events and two chat channels. It is not what kept the healthy controls quiet. Bluebird and Meridian sit inside Ops' own slice, which is all 20 deals. Answer 3 covers what actually held them back.

---

## 2. What is it actually allowed to write, and how do you know it cannot go rogue?

**Say first:** Six verbs, enforced in code, only four of which write into an app, and the client interface physically has no way to send an email.

`ALLOWED_ACTIONS` in `execute_actions` (`floor/round.py:963`) normalises to six verbs: `add_note`, `set_field`, `draft`, `assign_task`, `ask` and `flag_event`. The literal set on that line is longer than six because it also carries spelling aliases and `none`, and they all normalise down to those six. Anything outside it is printed as `REFUSED` and skipped. Only the first four touch an app. `ask` and `flag_event` just post a line to the floor. Separately, the `WorkspaceClient` interface in `floor/client.py` exposes ten methods and not one of them sends mail: there is `create_draft` and no send-mail method anywhere in the interface. The only thing named send in that file is `send_message`, which is the chat post tool. Two more chokepoints sit in front of the client and they work differently. `_filter_never_list` drops any finding whose proposed action says send without saying draft (`floor/round.py:102`). The end of `run_desk_merge` rewrites `send` to `draft` in any surviving action name (`floor/round.py:699`). Drop, then rewrite.

**Concede before they find it:** no refusal fires in a normal round, so I cannot demo one. It is a code-level guarantee I can show you in the source, not a scene in the video. In that run the only writes were 3 tasks and 4 one-line questions to @priya. Zero stages changed, zero close dates, zero calendars, zero emails sent.

---

## 3. How do you know the findings are correct and not just plausible?

**Say first:** I wrote the golden answer before I ran the agents, and the interesting result is what it caught me getting wrong.

`seed/expected_findings.md` lists what each watcher should find and, more importantly, what must **not** flag. No control reached the brief: D-106 Bluebird, D-114 Meridian, Juniper, Saffron, Dockside, Wren, Gold Leaf, Cobalt, event E-6 and thread M-8 (an HR candidate) were all left alone. How, precisely, is less flattering and you should have it. Those eight account names are a hardcoded `_NEVER_BRIEF` tuple in `floor/round.py:716`. `_ops_drop_controls` uses that list to strip a flagged deal that still has recent activity, `_followup_backfill` drops anything mentioning Bluebird by name, and `_stabilize_brief` nulls the human slot for any account in the list. So if the model had flagged Bluebird, code would have caught it. That is a guardrail I wrote, not judgment the model earned. E-6 and M-8 the watchers never flagged at all.

Sunset Taco is the judgment test in the seed. M-6 has the customer pausing until October, so D-103 should be noted and not escalated. It did stay off the brief, and I did not pass it for the right reason. Inbox never posted M-6 this run, the floor even carries a question reading "no customer signal of pause", and D-103 stayed out of the brief because `sunset taco` is in the hardcoded `_FLOOR_ONLY` list at `floor/round.py:721`. Right outcome, wrong mechanism. Getting Inbox to earn that is on the fix list.

**Concede before they find it:** Inbox underperformed. It posted 3 cards, but only 2 of the golden 5. The third, M-11 Harbor Fish, is a low-priority extra in the seed and not one of the five. It dropped M-1, M-2 and M-9. `floor/eval_expected.py` prints that as `inbox 2/5` and that is the number I will quote. Copper Kettle still reached the brief through D-101 and T-1, which is the merge covering for a weak watcher, but it is a miss and it is written up in `MOCK_VALIDATE_REPORT3.md`.

**The stabilisers, all four of them:** there are four in `round.py`, not two, and you should have all of them. `_ops_backfill` and `_followup_backfill` add expected findings the watcher model skipped. `_ensure_golden_problems` synthesises the Ember, Pine and Copper problems outright, hardcoded cause and owner included, if the Desk dropped them. `_stabilize_brief` pins whatever exists to ranks 1 to 3 with theo, dana and priya, and it also holds the `_NEVER_BRIEF` and `_FLOOR_ONLY` accounts out of the human slots. Ranking and owner routing are mine, not the model's. Three of the 17 cards in this log are backfill templates, and you can spot them because their evidence line is a bare ref id: D-101, D-105 and T-1. The other 14 are model-written and checkable against the seed line by line. M-4 quotes the mailer-daemon text verbatim and T-4 quotes Theo's 2026-09-04 message in `#ops-team`. I shipped `floor/eval_unpinned.py` to measure exactly how much the pins are carrying, because I would rather know that number than have you find it.

---

## 4. Is this running live, or is it a mock?

**Say first:** What you are watching is mock mode with real Claude calls, and the reason is one missing tool on the live side, not missing code.

`McpClient` is implemented in `floor/client.py` against Ambiguous over Streamable HTTP, and `python3 -m floor.round --live` is a real switch. The blocker is that the live workspace has zero inbound mail and its MCP exposes `list_inbox`, `create_draft_email` and `send_email` with no tool to inject fictional inbound customer threads. So the Inbox watcher has nothing to read live, and a demo that hid that would be a lie.

**What is real in the live workspace:** a `[SEED MAIL]` summary posted in `#ops-team` covering M-1, M-2, M-3, M-4 and M-9, plus three actual draft emails sitting in Mail for Copper Kettle, Marigold and Ember Grill. `send_email` was never called. The model calls in the recorded run are real API calls to `claude-sonnet-4-5`, so the reasoning you are reading is not canned, only the workspace is.

---

## 5. What is genuinely unfinished, and what breaks at real scale?

**Say first:** The reply loop is designed and stubbed but not wired, and Ops is already sitting on its own 8-finding cap at 20 deals.

`reply_loop` in `floor/round.py` is a print stub, and the call to it is commented out of `run_round`. The ending where Dana replies "Try Maya Brooks" and the Desk writes the new contact back to D-105 is a roadmap item, not behaviour I can show you today. The brief does print "Reply in this thread and I'll record it," and right now nothing is listening.

**On scale:** `max_findings_per_run` is 8 in `agents.yaml` and it is enforced as a hard slice in code, twice. Ops landed on exactly 8 cards against just 20 deals, so the demo already sits on the ceiling. Be careful with what that does and does not prove. Those 8 are 6 model cards (D-102, D-104, D-103, D-112, D-116, D-118) plus the 2 deterministic backfills (D-101, D-105), and `_ops_backfill` prepends the backfills before truncating to the cap, so the total lands on 8 by construction. I cannot show you a card the cap actually ate. The ordering is the real bug: backfill goes in front, so the cap would drop the model's lowest-ranked cards first. At a few thousand deals the slice stops fitting in a prompt and that truncation starts throwing away real findings, so you need a deterministic pre-filter before the model ever sees it. There is also no state between rounds, so tomorrow's run reposts the same Copper Kettle finding. And the round is four sequential model calls whose live wall-clock I have not measured, so I will not quote you a number.

---

## Pocket answers

| If they ask | Say |
|---|---|
| Why at most 3 items? | Human attention is the scarce resource, and `post_brief` slices to `[:3]` in code, not by asking the model nicely. |
| Why exactly two passes? | Bounded by construction in `run_round`: watchers post, Desk merges, done. No loop can run away. |
| How much did the run cost? | Four Claude calls per round, and `agents.yaml` caps findings at 8 per watcher to protect the action budget. |
| Which model? | `claude-sonnet-4-5` via `ANTHROPIC_API_KEY`, set in `agents.yaml › defaults.model`. |
| Where is the audit trail? | `#agents-floor`: 17 finding cards plus 4 questions, all readable by humans after the fact. |
| How much of this is hardcoded? | Four stabilisers in `round.py`, two name lists, and the rank-and-owner pinning. 14 of the 17 cards are model-written; the 3 with a bare ref as their evidence line are not. `floor/eval_unpinned.py` measures it. |
| Who owns the 3 tasks it created? | All three went to dana with generic titles due 2026-09-14. Owner routing is weak and that is a known bug. |
| Is any of this real customer data? | None. Brightline Payroll and everyone in it are invented, and the whole world is in `seed/`. |
| What would you build next hour? | Wire `reply_loop`, then delete `_stabilize_brief` and make the Desk earn its own ranking. |

---

## Do not say

- **Do not say a draft is waiting in Mail for Copper Kettle from this run.** Zero drafts were created in the validated run. Say: "the brief lists `draft_reply` as prepared work, and the draft object is not built yet. There are three real drafts sitting in the live workspace, and they were put there during setup, not by this round."
- **Do not click through to a draft on camera.** This run created nothing to open, and the three drafts in the live workspace were placed by hand before the demo. Opening one implies the round produced it. Stay in the terminal output.
- **Do not say the Desk posts PROBLEM blocks in each finding's thread.** It does not. Say: "the merge is visible as the Evidence line inside the brief, like `Evidence: D-101, T-1, E-1`. In-thread PROBLEM blocks are the next iteration."
- **Do not say the agents wrote CRM notes.** Zero CRM notes were written. Say: "`add_note` is in the allowlist and wired to the client, and this run only exercised `assign_task` and `ask`."
- **Do not say the reply loop runs.** It is a stub and it is commented out. Say: "designed, stubbed, not wired. That is rung 4 and I stopped at rung 3."
- **Do not offer to show the refusal live.** Nothing trips the allowlist in a normal round. Say: "I can show you the allowlist and the refusal branch in `execute_actions`. It is a guarantee in the code, and a normal round never trips it."
- **Do not claim a round time in seconds.** The live number is unmeasured. Say: "the heuristic no-key path finishes in about 0.2 seconds, and I have not timed the four live model calls."
- **Do not imply the brief ranking is the model's judgment.** Say: "the top three and their owners are pinned in `_stabilize_brief` for recording stability, and `_ensure_golden_problems` will synthesise one of those three if the Desk drops it. The evidence in the 14 model-written cards is the model's work."
- **Do not say every card is model-written.** Three are backfill templates. Say: "14 of the 17. The three with a bare ref as their whole evidence line are `_ops_backfill` and `_followup_backfill` output."
- **Do not call it Grok Bot.** It is The Floor.

---

## Before you stand up

1. Confirm `ANTHROPIC_API_KEY` is loaded from `.env`. Without it the code silently falls back to heuristic rules, the Ember Grill item disappears from the brief entirely, and item 3 degrades to a bare `T-1` assigned to dana. This is a blocker, not a nicety.
2. Have `MOCK_ROUND_VALIDATE3.txt` and `seed/expected_findings.md` open in two tabs. Every claim above points at one of them.
3. Run `.venv/bin/python -m floor.eval_unpinned --trace` once and read the unpinned result. If a judge asks how much the pins are carrying, quote that number instead of estimating. Answer 3 promises the harness exists, so know what it says.
