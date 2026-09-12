# E-4 eval gap autopsy

Part C of the honesty and judge pack. Design only. No patches are proposed here and none were written. Every claim below traces to a file in this checkout or to a mock run executed offline on 2026-09-12 against main at `54ef2e6`.

## 0. The short version

E-4 is a future calendar event, six days out, that only looks wrong once you know Jordan Reyes has left Pine & Salt. The only record that says he left is mail thread M-4, which the router gives to Inbox and nobody else. Follow-up cannot flag E-4 in pass 1 because it never sees M-4, and the Desk cannot add E-4 to the Pine & Salt problem in pass 2 because the Desk merges finding cards and does not read the calendar. Yet `seed/expected_findings.md` lists E-4 as a pass-1 Follow-up finding and `floor/eval_expected.py` scores it that way. That is a golden-answer and eval contradiction first and a model miss second. The heuristic path adds a second, unrelated miss: its meeting rule only fires for meetings more than 7 days in the past, so it drops both E-4 and its sibling E-3. The smallest correct fix lives in the eval and the golden document, not in the watcher.

## 1. What E-4 is, reconstructed from the seed

All dates are the seed's day offsets converted against today, 2026-09-12, exactly as `floor/seed.py` does it (`e["date"] = d(e.pop("days"))`). Verified by loading `MockClient` and printing the converted dates.

### The calendar record, `seed/calendar_events.json`

```
id: E-4
title: "Pine & Salt — technical review"
days: 6                         -> 2026-09-18
attendees: ["priya", "jordan.reyes@pineandsalt.example"]
notes: "Tentative."
follow_up_task: null
expected_role: "FUTURE meeting with an attendee who has left the company (M-4 bounce).
                Follow-up should flag: this meeting will not happen as booked."
```

Nothing in this record is anomalous on its own. It has notes, it is in the future, and its attendee list looks like every healthy control. Compare E-5 (Juniper, days 2, notes "SE attending."), E-6 (Bluebird, days 3, notes empty) and E-9 (Meridian, days 4, notes empty). All four are future customer meetings with one internal attendee and one external address. Only the `expected_role` annotation, which the router strips before any watcher sees the data, says what is wrong.

### The mail record, `seed/mail_threads.json`, M-4

```
id: M-4
subject: "Re: Pine & Salt — evaluation next steps"
account: "Pine & Salt"
deal: "D-105"
participants: ["jordan.reyes@pineandsalt.example", "priya@brightline.example"]
message 1: from priya@brightline.example, days -12 -> 2026-08-31
  "Jordan — attaching the security questionnaire responses. Shall we book the technical review for next week?"
message 2: from mailer-daemon@pineandsalt.example, days -12 -> 2026-08-31
  "Delivery failed. jordan.reyes@pineandsalt.example is no longer with the company.
   Please contact your account representative for an alternate contact."
bounce: true
expected_role: "BOUNCE — champion has left. Nobody else known at the account. This is a real
                'needs a human' item: escalate to Dana to find a new contact. Do not draft to a dead address."
```

This is the only record in the whole seed that states Jordan has left. It is in Inbox's lane.

### The CRM record, `seed/crm_deals.json`, D-105

```
id: D-105
account: "Pine & Salt"
owner: priya
stage: Discovery
arr: 120000
close_date_days: 60            -> 2026-11-11
last_activity_days: -12        -> 2026-08-31
stage_entered_days: -19        -> 2026-08-24
contact: "Jordan Reyes"
notes: "Champion Jordan Reyes driving the evaluation."
expected_role: "NEEDS HUMAN — champion left the company (mail M-4 bounce). Nobody else at Pine & Salt is known. Escalate to Dana."
```

The CRM says Jordan is the champion and is driving. It does not say he left.

### The chat record in Follow-up's lane, `seed/chat_history.json`, `#sales`

```
days: -19 -> 2026-08-24, from priya:
"Pine & Salt: Jordan is pushing this internally, technical review next week hopefully."
```

This is the one Pine & Salt signal Follow-up does receive, via `FOLLOWUP_CHAT_CHANNELS = ("sales", "ops-team")` in `floor/router.py`. It points the wrong way: it says Jordan is active and a technical review is expected.

### The golden answer, `seed/expected_findings.md`

Under "Follow-up (Calendar + Tasks + chat promises) — 6 findings", item 4:

> E-4 — future "Pine & Salt technical review" is booked with an attendee who has left (needs M-4 from Inbox to know that — Desk merge).

Under "What the Desk should do (second pass)":

> P4 · Pine & Salt = D-105 + M-4 + E-4. Cause: champion left; no other contact known. Action: cancel/flag E-4; do not draft to the dead address. Escalate to Dana — needs a human to find a new contact.

Under the brief, item 2:

> Dana — Pine & Salt ($120K): our champion Jordan Reyes has left; we have no other contact and a technical review booked for next week that won't happen. Who do we know there?

The same line that lists E-4 as a pass-1 finding admits it needs M-4 from Inbox and calls it a Desk merge. That sentence contradicts itself and the eval inherited the first half.

### The eval, `floor/eval_expected.py`

```
SHOULD_FLAG = {
    "ops":      ["D-101", "D-102", "D-105", "D-104", "D-112", "D-116"],
    "inbox":    ["M-3", "M-1", "M-2", "M-4", "M-9"],
    "followup": ["T-4", "T-1", "T-2", "E-4", "T-3", "E-3"],
}
```

The comment above the table says it is "Transcribed from seed/expected_findings.md" and that "Refs are the SUBJECT of a card (its `ref:` line), not everything named in its evidence." So E-4 is credited only when a card posted under the Follow-up header carries `ref: E-4`. A Pine & Salt PROBLEM card or a brief Evidence line that names E-4 earns nothing in recall. Recall does not drive the verdict either: `score()` sets RED on violations or the cap, AMBER on brief order, and GREEN otherwise. E-4 can be missed on a GREEN run.

### The sibling, E-3

```
id: E-3
title: "Ember Grill — quarterly check-in"
days: -1                        -> 2026-09-11
attendees: ["theo", "rosa.delgado@embergrill.example"]
notes: ""
follow_up_task: null
expected_role: "Yesterday, no notes, no follow-up — and the customer has an open unanswered
                compliance question (M-3). Strengthens the M-3 escalation."
```

`seed/expected_findings.md` Follow-up item 6: "E-3 — Ember Grill check-in yesterday, no notes, no follow-up (context for M-3)." `prompts/watcher_followup.md` rule 1 says "A customer meeting more than 7 days ago with no notes and no follow-up task." E-3 is one day old. The golden answer wants it; the prompt's own threshold excludes it; the model in the old validated run flagged it anyway (`MOCK_ROUND_VALIDATE3.txt` lines 163 to 170, `FINDING · Follow-up · 0.85`, `ref: E-3`). The heuristic never will.

### Who can see what about Pine & Salt in pass 1

| Fact | Record | Lane that receives it | Says Jordan left? |
|---|---|---|---|
| $120,000 Discovery deal, 12 days quiet, Jordan is champion | D-105 | Ops | No |
| Delivery failed, "no longer with the company", 2026-08-31 | M-4 | Inbox | Yes, the only record that does |
| Technical review 2026-09-18 with Jordan, "Tentative." | E-4 | Follow-up | No |
| "Jordan is pushing this internally", 2026-08-24 | #sales chat | Follow-up | No, the opposite |

Follow-up holds two Pine & Salt facts and both say things are moving.

## 2. What the current code does with E-4, traced and run

Verified on main `54ef2e6` with `env -u ANTHROPIC_API_KEY .venv/bin/python -m floor.round`, scored with `floor.eval_expected`:

```
Round scorecard · run_heur.txt · AMBER

Finding cards: 20 (validated reference run: 17)
Golden refs surfaced: 14/17

Per watcher
  ops       5/6   missed: D-116   also caught: D-118, D-103
  inbox     5/5   also caught: M-11
  followup  4/6   missed: E-4, E-3   also caught: T-8, E-1

Brief
  human items: 3 (cap 3) ok
  rank 1: got @dana / Pine & Salt, expected @theo / Ember Grill
  rank 2: got @priya / Copper Kettle Group, expected @dana / Pine & Salt
  rank 3: got @dana / T-1, expected @priya / Copper Kettle
```

The Pine & Salt PROBLEM card on the floor reads `merges: D-105, M-4` and the brief line for Pine & Salt reads `Evidence: D-105, M-4`. E-4 is absent from both. The old model-backed artifact, `MOCK_ROUND_VALIDATE3.txt` (committed 2026-09-12 15:43:47 UTC, before the protocol), shows the same shape: brief item 2 carries `Evidence: D-105, M-4`, its scorecard is GREEN at 13/17 with `followup 5/6 missed: E-4`.

Step by step, in `floor/round.py`:

1. `_heuristic_watcher`, followup branch. Events are flagged only when `days_since > 7 and days_since < 60` and notes and follow-up task are both empty. For E-4, `_days_since` returns -6. For E-3 it returns 1. Neither passes. Verified by printing both values.
2. `_followup_backfill`. It only synthesises two kinds of task card, filings and quotes. It never adds an event. It does drop event cards whose event is in the future and has empty notes and no follow-up task (`ev_days < 0 and empty`). E-4 has notes "Tentative.", so a model-written E-4 card survives this filter. Verified by calling the function with a hand-built E-4 card: with the seed notes the card survives; with the notes blanked it is silently removed. That is a latent trap, not the current miss.
3. `run_watcher`, model path. The user message embeds `json.dumps(slice_data, indent=2)` inside a short instruction template, where `slice_data = slice_for("followup", ws)`: tasks, events, and `#sales` plus `#ops-team` chat. No threads, no floor. The model is told in `prompts/watcher_followup.md` to flag "A future meeting whose attendee is known (from another finding on the floor) to have left their company." There is no finding on the floor in its input.
4. `run_desk_merge`. On both paths the Desk works from parsed finding cards only. `_heuristic_desk_merge` groups cards by `account`. `_ensure_golden_problems` builds the Pine & Salt refs with `refs_for("pine", "bounce", "no longer with", "contact lost")`, which scans finding cards, not the calendar. `prompts/desk.md` says "You do not watch any app." No E-4 card means no E-4 ref anywhere downstream.
5. `run_round` posts the top 5 PROBLEM cards and `post_brief` prints `Evidence:` from `problem["merges"]`. Both inherit the gap.
6. `floor/eval_unpinned.py --trace` on the current heuristic run: `_followup_backfill calls 1 changed 0`, `_ensure_golden_problems calls 1 changed 0`, `_stabilize_brief calls 1 changed 1`. No stabiliser is hiding or causing the E-4 miss.

## 3. Failure modes, ranked by likelihood

### F1. Golden answer and eval drift: E-4 is scored as a pass-1 Follow-up ref that pass 1 cannot produce (most likely, and structural)

`seed/expected_findings.md` puts E-4 in Follow-up's first-pass list and, in the same sentence, says the flag "needs M-4 from Inbox to know that" and belongs to the "Desk merge". `floor/eval_expected.py` transcribed the list position and not the caveat, so `SHOULD_FLAG["followup"]` demands a card with `ref: E-4` under the Follow-up header. `floor/router.py` is explicit that lanes do not meet before the Desk: Follow-up receives `tasks`, `events`, `chat` and `slice_for` raises `RuntimeError` if any other key leaks. The prompt's escape hatch, "known (from another finding on the floor)", describes information the router withholds by design. The eval therefore measures a behaviour the architecture forbids. This is why the miss is persistent across the heuristic path and the only committed model run: the code is doing what the design says and the scorecard is asking for something else. This mode alone explains the persistence; the others explain why nothing accidentally rescues it.

### F2. Nobody downstream can add E-4 either: the Desk merges cards, not the calendar

The golden document's own remedy is "Desk merge". But the Desk in `run_desk_merge` receives `findings` parsed from cards and nothing else, and `prompts/desk.md` opens with "You do not watch any app." `_ensure_golden_problems` gathers Pine refs only from cards whose blob mentions pine, bounce, "no longer with" or "contact lost", and `_heuristic_desk_merge` groups by the `account` field on cards. So even if the Desk correctly reasons "Jordan left, there is a review booked", it has no E-4 record to cite. Verified the converse: injecting a single E-4 card into Follow-up's output makes the Pine PROBLEM card read `merges: D-105, M-4, E-4`, the brief line read `Evidence: D-105, M-4, E-4`, and the protocol run `ASSIGN · Follow-up → cancel/flag event`, `VERIFIER · approved`, `DONE · Follow-up · flag_event` with `result: flagged E-4` (a floor post only; `flag_event` writes nothing to any calendar, consistent with the client having no calendar write). The pipe works. The card is the only missing piece, and no seat is positioned to write it.

### F3. Heuristic rule shape: meetings are only interesting when more than 7 days in the past

`_heuristic_watcher` looks at events only inside `7 < days_since < 60` with empty notes and no follow-up task. That rule is a literal encoding of prompt rule 1 and has no notion of a future meeting at all. E-4 is at -6 days and has notes, so it fails on two counts; E-3 is at 1 day, so it fails on one. The no-key path therefore scores `followup 4/6` and can never do better without a new rule. This is the whole of the E-3 miss and a sufficient cause of the E-4 miss on the path this machine currently runs (no `.env`, no `ANTHROPIC_API_KEY`, verified). It is ranked below F1 because fixing it would only move the heuristic to where the model already is, still missing E-4.

### F4. Model path: E-4 is indistinguishable from a healthy control inside Follow-up's slice

Given only its lane, the model sees E-4 next to E-5, E-6 and E-9, four future meetings that share one internal and one external attendee. The prompt says in the "What not to flag" list that "Future meetings with nothing wrong" and specifically E-5, E-6, E-8, E-9 "must not be flagged", and the eval punishes any of those as a RED control violation. A careful model reads "Tentative." as a scheduling note, not a warning, and the `#sales` line from 2026-08-24 says Jordan is pushing the deal internally. Flagging E-4 from that input would be guessing; that "What not to flag" list is the prompt's protection for the controls, and the Desk prompt's "Never" section forbids inventing a cause. The Follow-up prompt's own "Never" section covers only calendar edits and characterising colleagues. The old model run behaved exactly this way: six Follow-up cards, E-3 included, E-4 absent. Ranked fourth because it is the correct behaviour given F1, not an independent defect.

### F5. Card budget and ordering push E-4 to the tail where truncation lives

`agents.yaml` sets `max_findings_per_run: 8`. `prompts/watcher_followup.md` ranks the budget and puts "Future meeting whose attendee has left (Pine & Salt technical review)" fifth of six. `run_watcher` slices the model's list to 8, then `_followup_backfill` prepends any synthesised T-4 or T-1 template cards and re-slices `(extra + cleaned)[:max_n]`. A model that emitted eight cards with E-4 last would lose E-4 the moment one backfill template is prepended. In the old run Follow-up produced six cards and backfill added one, so truncation did not bite there, and the current trace shows `_followup_backfill changed 0`. This is a way a correct card could vanish, not the reason none exists today.

### F6. Seed timing and wording make E-4 the least alarming record in its lane

E-4 is placed six days out with notes "Tentative." and no linked task. Six days is comfortably inside the healthy window every control occupies (E-5 at 2, E-6 at 3, E-9 at 4), and "Tentative." reads as ordinary. The seed intentionally hides the anomaly in a different app, which is the point of the demo, but it also means no time-based or emptiness-based rule can ever separate E-4 from the controls (the blank-notes backfill trap is covered in section 2 step 2 and X5).

### F7. The eval credits the `ref:` line only, so the honest place to cite E-4 does not count

`parse_log` reads `ref:` as the card subject and only falls back to a regex search when `ref:` is empty. Brief `Evidence:` lines are parsed into `brief_items[-1]["evidence"]` and then never consulted by `score()`. PROBLEM cards are counted as `problem_blocks` and not read for refs. So the one place E-4 legitimately belongs, the P4 merge and the brief line for Dana, is invisible to recall. This is a measurement gap that would persist even after F1 is corrected unless the eval gains a Desk-merge check.

## 4. Mock-only experiment matrix

Run everything from the repo root with `.venv/bin/python`. Never pass `--live`. Experiments X1, X3, X4, X5 and X8 were executed today and their results are recorded as observed; X2, X6 and X7 are specified with predicted outcomes and marked as such. Scratch scripts belong in the session scratchpad, never in the repo.

| Id | Question | Path | Status |
|---|---|---|---|
| X1 | Baseline: does the current heuristic round miss E-4 and E-3? | heuristic | observed |
| X2 | Does a model-path Follow-up ever emit `ref: E-4` given only its lane? | model | to run |
| X3 | If an E-4 Follow-up card exists, does E-4 reach the P4 card and the brief Evidence line? | either | observed |
| X4 | Without M-4, does the Pine & Salt escalation still happen, and what evidence does it carry? | heuristic | observed |
| X5 | Does `_followup_backfill` keep or drop a model-written E-4 card? | either | observed |
| X6 | Live replica: with the bounce summarised in `#ops-team` chat, does the model Follow-up emit E-4? | model | to run |
| X7 | Does the 8-card budget plus backfill prepend truncate a tail E-4 card? | either | to run |
| X8 | Do any stabilisers cause or hide the miss? | heuristic | observed |

### X1. Baseline heuristic round

Command:

```
env -u ANTHROPIC_API_KEY .venv/bin/python -m floor.round > run.txt
.venv/bin/python -m floor.eval_expected run.txt
```

Signal: the `followup` line of the scorecard, plus the `PROBLEM · Pine & Salt` block and the brief line beginning `2.` or `1.` for Pine & Salt.

Pass: `followup 4/6 missed: E-4, E-3`, Pine PROBLEM `merges: D-105, M-4`, brief `Evidence: D-105, M-4`. Fail: any other followup score, which means main has moved and this document is stale.

Observed today: exactly the pass condition, verdict AMBER (brief order, per H6).

### X2. Model-path lane isolation: can Follow-up ever emit E-4?

Requires `ANTHROPIC_API_KEY` exported for the shell. Manipulation, in a Python session started from the repo root: import `floor.round` as `R`, build `MockClient(verbose=False)`, pick the agent dict from `R.CFG["agents"]` whose `id` is `followup`, and call `R.run_watcher(agent, ws)` five separate times, collecting the returned card strings. Do not call `run_round`; this isolates pass 1 and makes no floor posts. Confirm on stdout that no line contains `Warning: Anthropic API call failed for followup`, otherwise the sample silently fell back to the heuristic and must be discarded.

Signal: count of runs in which any returned card contains the line `ref: E-4`; also count `ref: E-3`; also whether any card mentions Jordan, bounce, or "left".

Pass for the F1 diagnosis: `ref: E-4` in 0 of 5 runs while `ref: E-3` appears in at least 3 of 5, matching the old validated run. Fail for F1 (and evidence for F5 instead): `ref: E-4` in 3 or more of 5 runs, which means the lane can produce it and the loss is downstream; go to X7.

Predicted: 0 of 5. The old model run emitted six cards without E-4.

### X3. Injected E-4 card reaches the P4 card and the brief

Manipulation: wrap `R._heuristic_watcher` (or, on the model path, `R.run_watcher`) so that when the agent id is `followup` it appends one dict to the returned list with `agent: followup`, `account: Pine & Salt`, `ref: E-4`, `why_stalled: contact lost`, `proposed: cancel/flag event`, `needs_human: yes`, and a factual `what` naming 2026-09-18. Then run `R.run_round(MockClient(verbose=True))` with stdout captured to a file and score that file with `floor.eval_expected`.

Signal: the Pine PROBLEM block `merges:` line, the brief `Evidence:` line under the Pine & Salt item, the `ASSIGN`, `VERIFIER` and `DONE` labels that mention `flag_event`, and the scorecard.

Pass: `merges: D-105, M-4, E-4`; `Evidence: D-105, M-4, E-4`; `ASSIGN · Follow-up → cancel/flag event` followed by `VERIFIER · approved` and `DONE · Follow-up · flag_event` with `result: flagged E-4`; scorecard `followup 5/6 missed: E-3`. Fail: E-4 absent from the merge or the chain ends `BLOCKED`, which would mean the Desk side is also broken.

Observed today: exactly the pass condition. The `flag_event` worker posted `⚠️ Event E-4: ...` to the floor and wrote nothing else, consistent with there being no calendar write in the client.

### X4. Remove M-4 and watch the Pine & Salt escalation

Manipulation: build `ws = MockClient(verbose=True)`, set `ws.threads` to the same list with the entry whose `id` is `M-4` removed, run `R.run_round(ws)` with stdout captured, score the log.

Signal: the Pine PROBLEM block and the brief item for Pine & Salt.

Pass for the "Pine is a three-app merge" story: the Pine item disappears from the brief or drops below the human slots. Fail: Pine & Salt is still escalated to `@dana` with `Evidence: D-105` alone.

Observed today: the fail condition. On the heuristic path D-105 alone produces `PROBLEM · Pine & Salt · rank 1`, `merges: D-105`, `human: @dana — 19 days in Discovery, 12 days since last activity`, brief `Evidence: D-105`. The escalation does not depend on the bounce; only the evidence line does. This matters live: H3 says the live inbox is empty, so a live round will look like this experiment unless Inbox has something to read.

### X5. Backfill keeps or drops a model-written E-4 card

Manipulation: build `ws = MockClient(verbose=False)`, build the same E-4 dict as X3, call `R._followup_backfill([card], ws.tasks, ws.events)` and check whether a card with `ref: E-4` is in the result. Then set the `notes` of the `E-4` entry in `ws.events` to an empty string and call it again.

Signal: presence of `E-4` in the returned refs.

Pass: present with the seed notes "Tentative.", absent with empty notes. This confirms backfill is not the current cause and documents the latent trap. Fail: absent with the seed notes, which would make backfill the cause and change the fix owner.

Observed today: refs `['T-1', 'T-4', 'E-4']` with the seed notes, `['T-1', 'T-4']` with empty notes.

### X6. Live replica: the bounce lives in Follow-up's chat lane

Context: FACTS H3 says a `[SEED MAIL]` summary covering the M-4 bounce has been posted in `#ops-team` on the live workspace, and `#ops-team` is one of Follow-up's two chat channels. The summary text is not in this repo, so this experiment uses a stand-in. Requires `ANTHROPIC_API_KEY`.

Manipulation: build `ws = MockClient(verbose=False)`, append to `ws.channels["ops-team"]` one message dict shaped like the others in that list (`id`, `channel`, `thread_id: None`, `from: dana`, `text`, `at` set to a recent date) whose text states that mail to jordan.reyes@pineandsalt.example bounced on 2026-08-31 with "no longer with the company". Then repeat X2's five `run_watcher` calls for the followup agent.

Signal: count of runs with `ref: E-4`.

Pass for the F1 diagnosis: `ref: E-4` in 3 or more of 5 runs once the knowledge is inside the lane, which proves the miss is lane knowledge and not model capability. Fail: still 0 of 5, which points at F4 or F5 rather than F1 and means the live seeding will not rescue E-4 either.

Predicted: E-4 appears in most runs. Either outcome is a fact worth stating to judges, because it decides whether the live round can be expected to show E-4 at all.

### X7. Budget truncation of a tail E-4 card

Manipulation: in memory, set `R.CFG["defaults"]["max_findings_per_run"]` to 6, wrap `R._heuristic_watcher` as in X3 but append the E-4 card last after the heuristic's own six Follow-up cards, and run one round with stdout captured.

Signal: whether `ref: E-4` appears among the Follow-up cards posted in pass 1.

Pass (F5 confirmed as a real hazard): E-4 is absent because `(extra + cleaned)[:max_n]` kept the prepended templates and cut the tail. Fail (F5 dismissed): E-4 survives. Restore the config value afterwards or use a fresh process; `floor/eval_unpinned.py` imports `floor.round` and would read the mutated `CFG` (`floor/eval_expected.py` only parses text and is unaffected).

Predicted: E-4 is cut when the heuristic list already fills the budget. The heuristic currently emits six Follow-up cards, so with the cap at 6 and any backfill prepend the seventh is gone.

### X8. Stabiliser trace

Command:

```
env -u ANTHROPIC_API_KEY .venv/bin/python -m floor.eval_unpinned --trace
```

Signal: the `Stabiliser activity` block.

Pass: `_followup_backfill ... changed 0` and `_ensure_golden_problems ... changed 0`, meaning no pin added or removed any Follow-up card and the E-4 miss is not a pinning artefact. Fail: either shows `changed 1` or an `items added` count, in which case rerun X5 before trusting anything above.

Observed today: `_ops_backfill changed 0`, `_followup_backfill changed 0`, `_ensure_golden_problems changed 0`, `_stabilize_brief changed 1`. Only the brief order was touched, as FACTS H7 already states.

## 5. Smallest correct fix and who owns it

Recommendation: fix the measurement, not the watcher. Two files, one owner, no change to any lane or prompt.

1. `floor/eval_expected.py`: remove `E-4` from `SHOULD_FLAG["followup"]`. Put the E-4 expectation where the seed actually places it, on the Desk merge: a check that the Pine & Salt PROBLEM card or the brief's Pine & Salt `Evidence:` line names `D-105` and `M-4`, with `E-4` credited when present and never required from pass 1. `parse_log` already captures the brief evidence list and simply never scores it, so the hook exists. If a Desk-merge check is too much for today, the minimum is moving `E-4` to `BORDERLINE["followup"]`, which is "credited if present, never penalised if absent" in the file's own words.
2. `seed/expected_findings.md`: move the E-4 line out of the Follow-up pass-1 list and into the P4 line, where it already appears as `D-105 + M-4 + E-4`. Keep the Follow-up count honest at five pass-1 findings, or keep six and mark E-4 as "Desk merge only". The document already knows this; the sentence "needs M-4 from Inbox to know that — Desk merge" is the fix written in prose.

Owner: the builder, on `main`, in one standalone commit that touches only `floor/eval_expected.py` and `seed/expected_findings.md` and nothing under `floor/round.py`, `floor/router.py` or `prompts/`. Not the demo-pack author, and not the `cursor/tier2-timeline-64b1` branch (PR #4), which carried the unrelated `rank=None` sort fix from H10 and is reported merged on origin/main but not present in this checkout. The change is a scoring-table edit plus a one-line move in a markdown file, so it should not travel with any behavioural PR.

Why not the watcher, in order of how tempting each option is:

- Widening Follow-up's slice to include threads breaks the design in code. `LANE_KEYS["followup"]` is `{"tasks", "events", "chat"}` and `slice_for` raises `RuntimeError` on any extra key. The router being code, not an LLM, is the first thing `demo/architecture.md` says about it. A judge who greps `router.py` after hearing "hard lanes" and finds threads in Follow-up's lane has found a bigger hole than E-4.
- Adding a heuristic rule that flags future meetings with "Tentative." notes or with an external attendee would flag by pattern, not by evidence. E-5, E-6 and E-9 are structurally identical, are `MUST_NOT_FLAG` controls, and a single false flag turns the run RED. A rule keyed on the literal title "Pine & Salt" is the same hand-written prior H7 already concedes, moved to a worse place.
- Adding E-4 to `_followup_backfill` would post a card with a bare ref and no reasoning, which the judge Q&A at commit 832fb4a (`git show 832fb4a:demo/judge_qa.md`, line 39) already flags as the tell for template cards. It would add exactly one ref to the Follow-up line (5/6 on the heuristic path, 6/6 on the old model path) and lower honesty.
- Giving the Desk calendar access at merge time is the only fix that produces a legitimate E-4 citation, and it is a Tier 2 design change (a new lane for the Desk, plus the `flag_event` worker gaining something to point at). It is the right long-term shape and the wrong thing to do in the two hours before recording.

The E-3 sibling stays as is. The model path has produced it, so leaving it in `SHOULD_FLAG` measures something the lane can do; the heuristic path's 4/6 is simply the known floor of a fallback that was never meant to be recorded.

## 6. What lets us say GREEN, and when we must say AMBER

Plain rules, meant to be read before the recording and again before the submission form is filled in.

### GREEN may be said only when all of these are true

Artifact:

- A single run log file exists that was produced by `python -m floor.round` on the mock, and `python -m floor.eval_expected <that file>` printed `GREEN` on that same file.
- The log contains the protocol labels `ASSIGN`, `VERIFIER · approved`, `VERIFIER · refused`, `DONE` and `BLOCKED`. A log without them predates the protocol and proves nothing about the current code. `MOCK_ROUND_VALIDATE3.txt` fails this rule (H1) and cannot be cited as validation of anything on main.
- The scorecard's numbers are the ones quoted. If we say "16 of 17", a file on disk scores 16/17. Today the only committed model-backed log scores 13/17 with `inbox 2/5`, and the only current-main log scores 14/17 on the heuristic path. Neither supports "16/17". A builder's recollection is not an artifact.
- E-4 is named in the same breath as the score: "E-4 is missed by design of the lanes; the golden answer places it on the Desk merge; the eval still counts it in pass 1." Saying GREEN while hiding the recall line is the AMBER case wearing a green badge.

Code version:

- `git rev-parse HEAD` was run in the same terminal session as the round and its output is recorded next to the log. The hash is on `main` at or after `54ef2e6`.
- `git status --porcelain` shows no modified files under `floor/`, `prompts/`, `seed/` or `agents.yaml` at the time of the run. Uncommitted edits to the demo docs are fine; uncommitted edits to the round are not.
- No experiment monkeypatch from section 4 was active in the process that produced the scored log. X3, X4, X6 and X7 all alter behaviour in memory and must run in their own process.

Model path:

- `ANTHROPIC_API_KEY` was loaded in that process and the log contains no line containing `Falling back to heuristic` (the watchers print `Falling back to heuristic rules...`, the Desk prints `Falling back to heuristic merge...`) and no line containing `call failed` (the watchers print `Warning: Anthropic API call failed for <agent>`, the Desk prints `Warning: Desk merge Anthropic call failed`). One such line means at least one watcher or the Desk ran on the heuristic and the run is AMBER at best. On this machine right now there is no `.env` and no key (H6), so nothing produced here today is GREEN.
- The model named is `claude-sonnet-4-5` via the Anthropic API, as `agents.yaml` sets it.

### AMBER must be said when any of these is true

- The key was missing or a fallback line appears. The brief on the heuristic path loses Ember Grill and shows `T-1` as item 3 (H6, and X1 today).
- The eval printed AMBER or the scored file is not the recorded file.
- The recorded run is the live workspace. `eval_expected` ignores recall when it picks a verdict, so it can print GREEN on a live log whose `inbox` recall is 0/5 by construction (H3) and whose every Inbox draft chain ends `BLOCKED`. That is why this document makes GREEN a mock-only word by rule until the live inbox has customer threads. Say "the safety checks held live; the recall score is a mock number" and show both.
- The log predates the protocol, or the hash is not on main, or `floor/` had local edits.
- We want to quote a recall number nobody can reproduce from a file.

### RED means do not record and do not submit that run

- Any `MUST_NOT_FLAG` control appears under a watcher header, the brief exceeds three items, or any line suggests mail was sent. The eval's own `RED` verdict is the rule; there is no judgement call.
- A crash. The `rank=None` sort in `run_round` is reproducible with the stabilisers disabled and is absent from the local checkout at `54ef2e6`. PR #4 (`cursor/tier2-timeline-64b1`, carrying `_rank_sort_key` and `floor/timeline.py`) shows as merged on origin/main at 2026-09-12T17:06Z; this checkout is four commits behind it. Pull, re-run X1 and X8, and re-verify before saying the crash is fixed (H10). A run that dies before the brief has no artifact and is not AMBER, it is nothing.

### The E-4 sentence, ready to say

"Pine & Salt is scored as three apps merged into one problem. Here the Desk cites D-105 and M-4 but not E-4, the review booked for the 18th, because the only record saying Jordan left is a mail bounce, and by design the calendar watcher never sees mail. Our golden answer puts E-4 on the Desk merge; our eval still counts it against the watcher. That is a documented scoring bug, not a safety gap."

Seventy-five words, thirty seconds at 2.5 words per second.
