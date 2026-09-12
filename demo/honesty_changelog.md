# Honesty changelog: demo/ pack

Date: 2026-09-12. Files rewritten: `demo/submission.md`, `demo/script.md`, `demo/judge_qa.md`. Files created: `demo/claim_sheet.md`, `demo/honesty_changelog.md`. Baseline for "before" wording: the versions on `main` at HEAD `54ef2e6`, and where noted the older full versions at commit `832fb4a`. Each entry names the H-number that drove it.

## demo/script.md

1. **Removed (H3).** Before: "Three watcher findings. Look for the watcher labels and the source facts: Ops/CRM, Inbox/Mail, Follow-up/Tasks–Calendar–selected chat." After: the opener names three lanes as design and says "The cards on screen are facts and ids." It no longer asserts three watchers posted, because live Inbox may post nothing.
2. **Removed (H2).** Before: "If a dedicated Verifier or Closer seat is unavailable, its floor post may appear from the Desk or a human-controlled identity." After: "There is no Verifier seat and no Closer seat in the workspace. Its verdict posts as Desk," plus pre-roll item 2 stating the round raises `PermissionError` without `AMBIGUOUS_TOKEN_DESK`.
3. **Added (H6).** Before: absent from the current file, which had no key check at all. After: pre-roll item 1, `ANTHROPIC_API_KEY` loaded, with the one-line dotenv check and the exact wrong-brief symptoms.
4. **Added (H2).** Before: absent from the current file. After: pre-roll item 2, `AMBIGUOUS_TOKEN_DESK` exported, with the check command and the statement that without it pass 2 dies at the first VERIFIER post inside refusal theater.
5. **Added (H3).** Before: absent from the current file. After: pre-roll item 4, the Inbox block may be empty live and every Inbox draft chain may end `BLOCKED · Inbox · draft`, with the exact sentence to say.
6. **Re-cut (timing).** Before: closing row 1:55–2:00, 15 words in a 5 second slot, which is 6.0 seconds spoken. After: 1:50–2:00, 10 second slot. All seven rows now carry word counts and fit at 2.5 words per second; total 257 words in 120 seconds.
7. **Corrected (mock run).** Before: refusal asks named `send customer email` and `move stage`. After: the exact floor labels `ASSIGN · Inbox → send email to customer` and `ASSIGN · Ops → set_field`, read off a mock round on current `main`.
8. **Removed (H5).** Before: "Do not show a reply loop ... unless it is actually visible and working." After: the closing line is named in the do-not-show list as not a working feature; "implemented behind `FLOOR_REPLY_LOOP`, off by default, not demonstrated."
9. **Added (H4).** Before: absent from the current file. After: a do-not-show entry for the `Ready:` line, with the reason: it prints planned actions, and a BLOCKed draft still reads `Ready: draft reply`.
10. **Added (H11).** Do-not-show entry for the timeline: "in open PR #4, not on `main`." Before: "designed and coding in parallel."
11. **Softened (code).** Before: on-screen instruction "The matching `VERIFIER · approved` or `VERIFIER · needs_rewrite` post." After: the approved chain only. `needs_rewrite` is a real verdict in `_verify_action` but was not observed on the mock, so it stays in the spoken list of verdicts and out of the shot instructions.
12. **Added (H14).** Before: absent from the current file. After: pre-roll item 3 restores the warm-round label check from the `832fb4a` structure, now listing the current protocol labels instead of the old card count.

## demo/submission.md

1. **Corrected (FACTS, stack).** Before: "Stack: Ambiguous workspace channels and the project's orchestration code." After: "Claude, model `claude-sonnet-4-5`, via the Anthropic API ... Ambiguous AI workspace and its MCP server, Streamable HTTP ... Python round runner with `MockClient` offline and `McpClient` live." The current file had dropped Claude entirely.
2. **Removed (H2).** Before: "A Verifier does not need a dedicated workspace seat; when seats are limited, the code gate can post its verdict through the Desk or a human-controlled identity." After: "A code gate posts `VERIFIER · approved`, `refused` or `needs_rewrite`." No seat claim in the portal text.
3. **Added (H1).** Before: absent from the current file. After: "On the offline mock, one round posts 20 findings, 5 problem cards and 2 refusals, writes 7 CRM notes, 5 drafts and 6 tasks, and asks one question, in 94 floor posts plus one brief." No count is attributed to a validated model run.
4. **Added (H3).** Before: absent from the current file. After: "The live inbox is empty, so the Inbox lane has nothing to read live and its drafts end `BLOCKED`."
5. **Added (H7).** Before: absent from the current file. After: "The top three brief slots and their owners are a hand-written playbook prior, not model ranking."
6. **Corrected (mock run).** Before: safety tests named `send customer email` and `move stage`. After: "send an email to a customer and move a deal's stage," matching the `send email to customer` and `set_field` labels.
7. **Softened (H5, H10, H11).** Before: "A persistent account timeline and a human-reply handler are designed and coding in parallel." After: a "Next, not claimed" section: reply handler "wired behind `FLOOR_REPLY_LOOP=1`, off by default, not demonstrated"; timeline and `_rank_sort_key` "in open PR #4, not on `main`."
8. **Removed (H1, from `832fb4a`).** The social post and one-liner no longer say "17 findings in, 3 items out" or cite the validated run.
9. **Changed (H8).** Title before: "always-on teammates that protect human attention." After: "agent teammates that protect human attention." No schedule is running, so "always-on" was dropped. The stack line says the schedule is designed, not running.
10. **Added (sponsor rule).** Before: absent from the current file. After: the social post tags only `@AnthropicAI` and `@AmbiguousAI`, with an instruction to confirm both handles against the event sponsor list and never guess another.
11. **Removed (hard blocks, from `832fb4a` `demo/submission.md` line 78).** Before, in that older file: "The allowlist is wider than the prompts ... `set_deal_field` ... has a branch that writes `stage_id`." After: not revived. On current `main`, `_verify_action` refuses `set_field` for every field and `set_deal_field` raises `PermissionError` for stage fields, so the concession no longer describes the code.

## demo/judge_qa.md

1. **Removed (H2).** Before: "Is Verifier a separate Ambiguous agent? Not necessarily ... that verdict can post through the Desk or a human-controlled identity." After: question 2 states there is no Verifier or Closer seat, the verdict posts as Desk only when `AMBIGUOUS_TOKEN_DESK` is set, and the round fails closed otherwise, citing `floor/client.py` line 321.
2. **Removed (H1).** Before: "Is the demo live? Yes: the recording stays in Ambiguous and shows live channel artifacts." After: question 1 concedes no validated run of the current protocol exists and the recording is the first end-to-end run, citing the 15:43 UTC versus 16:54 UTC timestamps.
3. **Corrected (H3).** Before: "The live workspace has an inbound-mail gap." After: the MCP exposes `list_inbox`, `create_draft_email`, `send_email` and no inbound-inject tool; live Inbox posts 0 cards; drafts end `BLOCKED · Inbox · draft` with a reason beginning `could not resolve mail id for ref=`; `send_email` never called.
4. **Added (H4).** Before: absent from the current file. After: the `Ready:` line prints `problem.actions`, not executed work.
5. **Corrected (H5).** Before: "A persistent account timeline and a human-reply handler are designed and coding in parallel." After: "implemented behind `FLOOR_REPLY_LOOP`, off by default, not demonstrated," citing `floor/reply_handler.py`, 633 lines, `SAFE_FIELDS` and `BLOCKED_FIELDS`.
6. **Added (H7).** Before: absent from the current file. After: question 4 names `_stabilize_brief` line 792, `_ensure_golden_problems` line 747, the `_NEVER_BRIEF` and `_FLOOR_ONLY` lists, the `prompts/desk.md` ordering, and the ablation result.
7. **Added (H8).** Before: absent from the current file. After: a pocket answer, about 113 writes plus 4 model calls per round; `AUTOMATIONS.md` is stale; a weekday schedule exhausts a 1,000-action tier in under two weeks.
8. **Added (H9).** Before: absent from the current file. After: a pocket answer, all six tasks go to dana, due in two days.
9. **Added (H10, H11, H12).** Before: absent from the current file. After: a pocket answer naming PR #4, #7 and #6 as in flight and none on `main`.
10. **Added (H13).** Before: absent from the current file. After: a pocket answer on E-4, a future meeting whose only evidence is M-4 in Inbox's lane, so Follow-up cannot know in pass 1.
11. **Corrected (mock run).** `move stage` replaced with the actual `set_field` label throughout.

## demo/claim_sheet.md (new)

Twelve bullets, seven WILL CLAIM LIVE with channel and label, five WILL NOT CLAIM covering H1, H3, H4, H5, H7, H8, H10, H11. Every other demo doc is required to agree with it.

## Review corrections, same day

Two independent reviewers audited the pack against `main` at `54ef2e6`. Every correction below was re-verified by reading the code or running the mock offline.

1. **Corrected (code, all five files).** Before: the fail-closed draft label was written `BLOCKED · Inbox · draft reply` with reason `could not resolve mail id`. After: `BLOCKED · Inbox · draft` with a reason beginning `could not resolve mail id for ref=`. `_post_blocked` at `floor/round.py` line 1223 prints the normalized action type, `draft`, and the reason string is built at line 1378.
2. **Corrected (mock run, submission and judge_qa).** Before: "in 95 floor posts" and "95 floor posts, 1 brief". After: "94 floor posts plus one brief". `floor.eval_expected` on the mock log prints `floor posts 94`; the 95th post is the brief in `#attention`. The 113-write figure is unchanged: 94 + 1 + 7 + 5 + 6.
3. **Corrected (mock run, judge_qa question 3).** Before: "the round creates 0 drafts, and each draft action ends BLOCKED". After: with `threads=[]` the heuristic Desk emits no draft actions at all, 73 floor posts and 14 finding cards; the BLOCKED path was forced separately and every such chain blocked. The old sentence described a chain the mock does not show.
4. **Corrected (code, judge_qa and this file).** Line citations: `as_agent` is at `floor/client.py` line 321 with the raise at 348, not 320; `set_deal_field` is at line 456 with the raise at 459. `_FLOOR_ONLY` at `floor/round.py` line 729 has eight entries, not six.
5. **Corrected (mock order, submission and judge_qa).** Before: "Every round opens with two deliberately unsafe asks." After: "Before any worker acts, every round runs two deliberately unsafe asks." A round opens with pass 1 findings; refusal theater runs after the PROBLEM cards and before `execute_actions`.
6. **Softened (code, claim sheet).** Before: "Five cards per round" and "each card carrying one seed id". After: "Up to five cards per round, sliced in code; five on the mock", because `run_round` slices `[:5]` at line 1541; and a Follow-up chat-promise card may cite a chat message rather than a seed id, per `prompts/watcher_followup.md` line 8.
7. **Corrected (H2, script).** Before: "Its verdict posts as Desk." After: "posts as Desk once `AMBIGUOUS_TOKEN_DESK` is set ... Without that token the round fails closed."
8. **Condensed (judge_qa question 5).** Eight sentences cut to four with the same facts and line numbers.
9. **Moved (this file).** The `832fb4a` allowlist concession entry moved from the judge_qa section to the submission section, now attributed to `demo/submission.md` line 78 at that commit and to the hard blocks, not H2.
10. **Prose rule (all five files).** Titles no longer use an em-dash connector.

## Live-shaped simulation and post-merge state, same day (H15 to H20)

After the pack was drafted, a `McpClient` was run offline with its MCP transport stubbed and live-shaped payloads: UUID ids, titles beginning `D-101`, `updated_at` in place of a stage date, an empty inbox. Separately, GitHub `main` moved past the recording checkout. Each item below was reproduced, not inferred.

1. **Added (H15, script and runbook Case C).** Without `AMBIGUOUS_TOKEN_DESK` the live floor ends on exactly one `ASSIGN · Inbox → send email to customer` after 10 posts, with no `VERIFIER · refused`, no `BLOCKED` and no brief. Before: "the floor is left half posted". After: the exact last label, and that the system appears to announce an unsafe request and go silent.
2. **Added (H20, script and runbook Case C).** There is no pass-2-only flag. Recovery re-runs the whole round and posts a second pass 1 block above the good pass 2; the take scrolls to the second header. `round.py` loads `.env` at import so a `.env` entry works; `python -m floor.client` does not load `.env`.
3. **Softened (H16, script, claim sheet, runbook Case E).** Before: `FINDING · Ops` listed as a required label. After: claimed only if on screen. `_norm_deal` sets `stage_entered` to `None`, every fallback Ops rule and both backfill rules require it, and a deal with no `updated_at` is treated as active today and skipped. Backdating that one field makes the rules fire.
4. **Added (H17, script do-not-show, runbook Case E).** On the fallback path a Follow-up task card carries no account name, the merge keys it by its live id, and the `PROBLEM` card and the brief item are titled by a UUID.
5. **Corrected (H18, claim sheet).** Before: the handoff example was an Ops `add_note` chain and the fail-closed receipt was `BLOCKED · Inbox · draft`. After: live-shaped, the only approved chains were three Follow-up `assign_task` chains and no draft was planned at all, so neither the `add_note` chain nor that receipt can be promised. A live-shaped round is about 27 posts, not 95; the mock inflates the count because its seed carries stage and activity dates the live CRM lacks.
6. **Added (H19, script, claim sheet, runbook Case E).** With only the Desk token, every post including watcher cards is signed by the Desk seat. Seat names appear only with the three watcher tokens set. The VERIFIER verdict signs as Desk unless a Verifier token exists.
7. **Corrected (H10, H11, script, claim sheet, runbook ban list, judge_qa, submission).** Before: "open PR #4, not on `main`". After: PR #4 merged to GitHub `main` at `76be8d5` after the recording checkout `54ef2e6`; PRs #10, #11 and #12 merged after it; the checkout is not pulled. On the merged tip the committed `seed/timeline.json` marks the golden accounts as already waiting on a human, the brief reads `0 item(s) need a person`, the scorer reports all three ranks missing, and the store writes back to that tracked file on every run. Verified on an isolated copy of the merged tip.

## Errors in files this pack may not edit, for their owners

- **`MCP_MAPPING.md` line 40 (H2).** The line says Verifier posts "fall back to the Desk agent token (then the default token only if Desk is also unset)." The code in `as_agent` at `floor/client.py` line 321, with the raise at line 348, raises `PermissionError` for `verifier` and `closer` when no Verifier or Desk token is set, and never uses the default token for them. The doc line is wrong and the demo pack now states the fail-closed behaviour instead.
- **`seed/timeline.json` and `floor/timeline.py` on GitHub `main` (H11).** The committed seed marks Pine & Salt, Copper Kettle Group, T-1 and T-4 as already waiting on a human, so a fresh round on the merged tip escalates nothing, and `TimelineStore._save` rewrites the tracked seed file on every run. Either gate the store behind a flag with the seed empty by default, or move the store out of `seed/`. Until then the merged tip cannot produce the three-item brief the demo is built on.
- **`floor/client.py` `_norm_deal` (H16).** `stage_entered` is hard-set to `None` and a missing `updated_at` becomes `last_activity=None`, which the Ops rules treat as activity today. Map a real stage timestamp if the Ambiguous deal object carries one; otherwise the Ops rules must key on `last_activity` alone and must not default a missing date to today.
- **`AUTOMATIONS.md` lines 58 to 69 (H8).** The budget table says 25 workspace writes per round and about 525 per month. A round on current `main` writes about 113 workspace objects (94 floor posts, 1 brief, 7 notes, 5 drafts, 6 tasks) plus 4 model calls. Against a 1,000-action monthly tier that is roughly 9 rounds, so a weekday schedule exhausts the tier in under two weeks. The demo pack does not quote the old figures.
