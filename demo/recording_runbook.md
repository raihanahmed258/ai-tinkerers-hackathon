# The Floor · recording runbook

One take, one voice, exactly 2:00, entirely inside the Ambiguous workspace. Record at 15:15. Submit by 16:00.

**Where this choreography comes from.** No model-backed live run of the current protocol is committed. `MOCK_ROUND_VALIDATE3.txt` predates the `ASSIGN`, `VERIFIER`, `DONE`, `BLOCKED` labels. Rehearse for free with `python -m floor.round --no-model --safety-demo`; the live floor should show the same protocol headers, not necessarily the same cards or counts.

**Three pre-roll blockers.** Clear all three before the warm round. Each one has a section 3 entry if it bites during the take.

1. `ANTHROPIC_API_KEY` loaded. Without it the code silently falls back to heuristic rules and the brief is wrong: rank 1 is not Ember Grill and item 3 is a bare task id. Confirm with the boolean command in section 3, case D. The model when the key is present is `claude-sonnet-4-5`.
2. `AMBIGUOUS_TOKEN_DESK` exported in the shell that runs the round. `McpClient.as_agent("verifier")` tries `AMBIGUOUS_TOKEN_VERIFIER`, then `AMBIGUOUS_TOKEN_DESK`, and raises `PermissionError` if neither is set. The `--live` entry point reads only `AMBIGUOUS_API_KEY` or `AMBIGUOUS_TOKEN`, so with the default token alone the round dies at the first `VERIFIER` post. Confirm with the boolean command in section 3, case C.
3. One warm round finished on the live floor, run with `--live --safety-demo` and with `--timeline` omitted. It ends with `—— Round … · done ——` in `#agents-floor` and a new brief in `#attention`. The historical demo produced roughly 100 writes, so avoid speculative live retries.

Browser setup: one window, two tabs, `#agents-floor` first and `#attention` second. Nothing else open. Zoom the browser until one `FINDING` card fills roughly a third of the frame; that zoom is what lets the brief's last two lines fall below the fold in beat 6. Do Not Disturb on. Quit Mail, Slack, and Messages.

---

## 1. Scroll choreography

Seven beats, contiguous, the last one ends at 2:00. The beats match the seven rows of the shot list in `demo/script.md`. Scroll direction is downward for the whole take except one short upward scroll in beat 7. Start the take with the most recent `—— Round <stamp> · pass 1 ——` header at the top of the frame and never scroll above it. Older rounds and any dead partial round sit above that line and stay out of shot.

Label text below is exactly what the code posts. `<stamp>` is the round's date and time, for example `2026-09-12 15:05`. Live deal refs may print as UUIDs instead of `D-105`; do not read refs aloud in any beat.

### Beat 1 · 0:00–0:17 · Pass one · `#agents-floor`

| Time | Scroll to | Hold | Cursor rests on |
|---|---|---|---|
| 0:00–0:03 | `—— Round <stamp> · pass 1 ——` | 3 s | the second line, `Watchers posting FINDING cards here.` |
| 0:03–0:10 | the first `FINDING · Ops · …` card, then drift down through the Ops block | 7 s total, 2 s on the first card | the `ref:` line of the first Ops card; in the mock that is `ref: D-101`, account `Copper Kettle Group` |
| 0:10–0:17 | the first `FINDING · Follow-up · …` card, then drift to the last Follow-up card | 7 s total, 2 s on the first card | the `ref:` line of the first Follow-up card; in the mock that is `ref: T-1`, and its `what:` line reads `Task overdue 19 days: Send Copper Kettle revised quote (3-location discount)` |

If a `FINDING · Inbox · …` block sits between Ops and Follow-up, use the split in section 3, case B2. In the mock the blocks are 8 Ops, 6 Inbox, 6 Follow-up. Live, expect Ops and Follow-up only. The words do not change either way; the beat 1 Say cell names the three lanes, which are code, and says nothing about how many cards each lane posted.

### Beat 2 · 0:17–0:33 · Pass two · `#agents-floor`

| Time | Scroll to | Hold | Cursor rests on |
|---|---|---|---|
| 0:17–0:20 | `—— Round <stamp> · pass 2 · Desk merge ——` | 3 s | the second line, `Merged N findings → M problem(s).` |
| 0:20–0:33 | `PROBLEM · <account> · rank 1` and `PROBLEM · <account> · rank 2`, both cards in frame | 13 s | the `merges:` line of the rank 1 card for 7 s, then the `merges:` line of the rank 2 card for 6 s |

With the key loaded, rank 1 should be `PROBLEM · Ember Grill · rank 1`. If it is anything else, stop and go to section 3, case D. Do not read the rank number aloud. Do not rest the cursor on the `human:` line or the `actions:` line. The `merges:` ids are the receipt for "trace the merge back to the cards above it"; they are the same ids as the `ref:` lines in beat 1.

### Beat 3 · 0:33–0:52 · Refusal theater · `#agents-floor`

| Time | Scroll to | Hold | Cursor rests on |
|---|---|---|---|
| 0:33–0:35 | `—— Refusal theater · unsafe asks (must not execute) ——` | 2 s | the second line, `Desk received two out-of-policy requests. Verifier must refuse both.` |
| 0:35–0:37 | `ASSIGN · Inbox → send email to customer` | 2 s | the `cause:` line, `Would email <account> the revised quote without human approval` |
| 0:37–0:40 | `VERIFIER · refused` | 3 s | the `reason:` line, `customer send is forbidden; draft only` |
| 0:40–0:42 | `BLOCKED · Inbox · send email to customer` | 2 s | the label line |
| 0:42–0:44 | `ASSIGN · Ops → set_field` | 2 s | the `cause:` line, `Would move <account> to Closed Won without a human decision` |
| 0:44–0:47 | `VERIFIER · refused` | 3 s | the `reason:` line, `field 'stage' is blocked (safety)` |
| 0:47–0:52 | `BLOCKED · Ops · set_field` | 5 s | the `reason:` line |

Both fake requests name the account of the first ranked problem that has an account name (`_refusal_theater`, `floor/round.py`). The ref is that problem's first deal ref, or its first merge if it has none. The cause text is canned. In the mock that is Pine & Salt; live with the key loaded and Ember Grill at rank 1 it will be Ember Grill, and the first cause line will still say "the revised quote". Do not say the account name in this beat.

Word cue: use this beat's slack as one pause after "Send an email to a customer." so that "Move a deal's stage." lands as the cursor reaches `ASSIGN · Ops → set_field` at 0:42, and "refuses both" lands on the second `VERIFIER · refused`.

### Beat 4 · 0:52–1:10 · One approved chain · `#agents-floor`

Use the first chain after refusal theater that ends in `DONE`. In the mock it is Ops on Pine & Salt.

| Time | Scroll to | Hold | Cursor rests on |
|---|---|---|---|
| 0:52–0:56 | `ASSIGN · Ops → add note` | 4 s | the `rule:` line, `wait for VERIFIER · approved before write` |
| 0:56–1:02 | `VERIFIER · approved` | 6 s | the `reason:` line, `allowlist + safety checks passed` |
| 1:02–1:10 | `DONE · Ops · add_note` | 8 s | the `result:` line, `note on deal <ref>` |

Keep all three posts in frame together for the whole beat. If the first chain after refusal theater ends in `BLOCKED`, skip forward to the first chain that ends in `DONE`. If no chain ends in `DONE`, use section 3, case A2.

### Beat 5 · 1:10–1:27 · Remaining chains to work done · `#agents-floor`

| Time | Scroll to | Hold | Cursor rests on |
|---|---|---|---|
| 1:10–1:22 | a steady downward scroll through the remaining `ASSIGN`, `VERIFIER`, `DONE` chains | 12 s of scrolling | nothing; keep the cursor at the right edge of the frame while scrolling |
| 1:22–1:27 | `—— Work done this round ——` with its first bullets in frame | 5 s | the first bullet, `• Ops note · <account>` |

The chains are not meant to be read; the repeating labels are the point. Set the scroll speed so the header arrives at 1:22. In the mock there are 22 chains between refusal theater and the header; live expect about 14. If a `BLOCKED · Inbox · draft` post passes through frame, let it pass without stopping; it is a receipt for "A BLOCKED receipt is not hidden" and it needs no cursor. From 1:22 keep the cursor on the first bullet and do not track down the list. Bullets of the form `• task → @dana · T-1` carry the owner routing, and that routing is weak; every task in a round goes to dana with a due date of today plus two days. Do not point at it. A `• flagged event · <account>` bullet is a floor post, not a calendar write. If the block reads `• none (all actions blocked or empty)`, use section 3, case A2.

### Beat 6 · 1:27–1:50 · The brief · `#attention`

| Time | Scroll to | Hold | Cursor rests on |
|---|---|---|---|
| 1:27–1:28 | click the `#attention` tab | 1 s | nothing; hands off the mouse during the switch |
| 1:28–1:31 | `Attention brief · <date>` at the top of the frame | 3 s | the second line, `3 item(s) need a person · everything else handled on the floor` |
| 1:31–1:36 | `1. @theo — Ember Grill` | 5 s | the item's first line |
| 1:36–1:41 | `2. @dana — Pine & Salt ($120,000)` | 5 s | the item's first line |
| 1:41–1:46 | `3. @priya — Copper Kettle Group ($84,000)` | 5 s | the item's first line |
| 1:46–1:50 | no scroll | 4 s | item 3's `Evidence:` line, with `Handled without you: …` as the last visible line of the frame |

Every item prints an owner-and-account line and a cause line, then `Evidence:` when the merge carries refs and `Ready:` when the problem carries actions. A problem backfilled by `_ensure_golden_problems` has no actions and no `Ready:` line. If item 3 has no `Evidence:` line, rest on its cause line for 1:46–1:50 instead. Never rest the cursor on a `Ready:` line: it prints planned actions, not execution receipts. With `FLOOR_REPLY_LOOP` off, the brief does not print a reply-handling promise.

The beat 6 Say cell names no account, no owner, and no dollar amount. Do not add them. The cursor on the owner lines is the receipt for "Each item names an owner".

### Beat 7 · 1:50–2:00 · Tagline · `#agents-floor`

| Time | Scroll to | Hold | Cursor rests on |
|---|---|---|---|
| 1:50–1:51 | click the `#agents-floor` tab | 1 s | nothing |
| 1:51–2:00 | the last chain that ends in `DONE` immediately above `—— Work done this round ——`, with `ASSIGN`, `VERIFIER · approved`, `DONE` all in frame | 9 s | the `VERIFIER · approved` label, cursor still |

The tab keeps the beat 5 scroll position, so this chain is one short upward scroll from the `—— Work done this round ——` header. Do not go back to the beat 4 chain; it is many chains higher. In the mock the last chain is Follow-up: `ASSIGN · Follow-up → create task`, `VERIFIER · approved`, `DONE · Follow-up · assign_task`. Live it may be Ops or Follow-up. Any chain ending in `DONE` is a valid receipt for the tagline. Stop scrolling before you speak. Say the line, stop, let the recording run out. Add nothing after it.

---

## 2. Voice-over script

Rate: 2.5 words per second. Cap: 300 words. Comfortable: 240 to 270. This script is 257 words, 102.8 seconds spoken inside 120 seconds, with 17.2 seconds of slack for scrolling and tab switches.

**Source of truth.** The Say cells below are copied word for word from the seven rows of `demo/script.md` in the working tree at reconciliation time. If Part A's review changes that file, change this section to match and re-run the counts. One label caution: `demo/script.md` writes the blocked draft post as `BLOCKED · Inbox · draft reply`; the code prints `BLOCKED · Inbox · draft`, because `execute_actions` passes the action type `draft` to `_post_blocked`. The `ASSIGN` label is `ASSIGN · Inbox → draft reply`. This runbook uses the labels the code prints.

| Beat | Range | Length | Words | Spoken | Slack |
|---|---|---|---|---|---|
| 1 · Pass one | 0:00–0:17 | 17 s | 38 | 15.2 s | 1.8 s |
| 2 · Pass two | 0:17–0:33 | 16 s | 35 | 14.0 s | 2.0 s |
| 3 · Refusal theater | 0:33–0:52 | 19 s | 43 | 17.2 s | 1.8 s |
| 4 · One approved chain | 0:52–1:10 | 18 s | 37 | 14.8 s | 3.2 s |
| 5 · Remaining chains to work done | 1:10–1:27 | 17 s | 38 | 15.2 s | 1.8 s |
| 6 · The brief | 1:27–1:50 | 23 s | 51 | 20.4 s | 2.6 s |
| 7 · Tagline | 1:50–2:00 | 10 s | 15 | 6.0 s | 4.0 s |
| **Total** | **0:00–2:00** | **120 s** | **257** | **102.8 s** | **17.2 s** |

Beat 6 is the one to rehearse twice. It is the longest cell, the cursor has to land on three item lines, and the last four sentences are the ones a judge will test.

### Beat 1 · 0:00–0:17 · 38 words

> This is Brightline Payroll. One stuck customer leaves signals in different tools. Three watchers, each with one lane: Ops reads the CRM, Inbox reads mail, Follow-up reads tasks and calendar. The cards on screen are facts and ids.

The three lanes are code in `floor/router.py` and are true whether or not Inbox posted a card. Do not add that Inbox posted anything unless a `FINDING · Inbox` card is on screen.

### Beat 2 · 0:17–0:33 · 35 words

> Pass two. The Desk reads the whole floor and merges same-account cards into one ranked problem. Each problem card carries its evidence ids, so you can trace the merge back to the cards above it.

### Beat 3 · 0:33–0:52 · 43 words

> Before any worker acts, the Desk posts two deliberately unsafe asks. Send an email to a customer. Move a deal's stage. The verifier gate refuses both, and both end BLOCKED. These are safety tests, not customer work. The round runs them every time.

"The round runs them every time" is true in code: `execute_actions` calls `_refusal_theater` unconditionally before any productive chain. A single-round take shows it once. See section 5, row 11.

### Beat 4 · 0:52–1:10 · 37 words

> Now the real work. Every assignment is one bounded step. The Desk posts ASSIGN. The gate posts its verdict: approved, refused, or needs rewrite. The worker posts DONE or BLOCKED. Nothing writes until the floor shows approved.

"The gate posts its verdict" is the honest wording. There is no Verifier seat and no Closer seat in the workspace. The verdict posts as Desk when `AMBIGUOUS_TOKEN_DESK` is set. Do not say "the Verifier agent". The `needs_rewrite` verdict never posts in this round; see section 5, row 14.

### Beat 5 · 1:10–1:27 · 38 words

> Every step is on the floor as a post: the ask, the verdict, the receipt. Anyone can read the audit trail without a terminal. A BLOCKED receipt is not hidden. It means the worker stopped instead of guessing.

This cell claims nothing about what got done, so it stands unchanged under section 3, case A2. The receipt for "A BLOCKED receipt is not hidden" is any `BLOCKED · …` post that has been in frame in the take: the two refusal-theater posts in beat 3, and live, any `BLOCKED · Inbox · draft` that passes through in this beat.

### Beat 6 · 1:27–1:50 · 51 words

> Humans get one brief in attention, capped at three items in code. Each item names an owner and the evidence ids behind it. Everything else stayed on the floor, handled or blocked. Nothing was sent to a customer. No stage changed. No calendar was touched. The client cannot do those things.

The cell does not name Ember Grill, Theo, or a dollar amount, and it does not say the order is derived. The pinned ranking is still there: `_stabilize_brief` forces Ember Grill, Pine & Salt, and Copper Kettle into ranks 1 to 3 with owners theo, dana, and priya. The findings and the merge are derived; the priority order is a hand-written prior. If a judge asks about the order, say that. The receipts for the last four sentences are earlier in the take and in code; see section 5, rows 23 to 26, and decide before submitting whether "The client cannot do those things." stays.

### Beat 7 · 1:50–2:00 · 15 words

> Attention is a team sport. Most of the team does not have to be human.

---

## 3. Contingency takes

Each case names the symptom, the alternate sentence if the words change, and where the cursor goes. Word counts are measured at 2.5 words per second.

### Case A · BLOCKED where DONE was expected

**A1 · Inbox draft chains end in BLOCKED.** Live, the inbox is empty, so any `ASSIGN · Inbox → draft reply` resolves no thread and the worker posts `BLOCKED · Inbox · draft` with the reason `could not resolve mail id for ref=… (empty inbox / SEED MAIL only / bad ref) — no draft`. This is the gate failing closed, and it is correct. On the heuristic path with an empty inbox, no draft chain is assigned at all, because no Inbox finding proposes one; with the model Desk a draft chain can still be planned from the `[SEED MAIL]` chat summary and then BLOCK. Either way, do not use a draft chain for beat 4. Pick an Ops `add_note` chain or a Follow-up `assign_task` chain that ends in `DONE`. Beat 5's `—— Work done this round ——` lists only executed work, so a BLOCKED draft never appears there; it can pass through frame during the beat 5 scroll, and that is fine. Do not say the word "draft" anywhere in the take, including the case A2 alternate.

If a judge asks about a BLOCKED draft on the recording, the sentence is: "The live inbox holds no inbound mail, so the gate refused to fake a draft. BLOCKED is the receipt."

**A2 · Every chain ends in BLOCKED and the work-done block reads `• none (all actions blocked or empty)`.** This means live ref resolution failed for notes and tasks as well. Do not hunt for a DONE. Beat 4 alternate, 38 words, 15.2 seconds inside 18:

> Real work goes through the same gate. The Desk posts ASSIGN. A code gate posts the VERIFIER verdict. This worker posts BLOCKED: no live record it could resolve, so it wrote nothing. The floor is the audit trail.

Prefer an Ops `add_note` chain whose `BLOCKED` reason is `could not resolve deal id`. A Follow-up chain blocks only on a raised error and prints that error text as its reason; use it second. Use an Inbox chain only if no other BLOCKED chain exists; it puts `BLOCKED · Inbox · draft` under the cursor for the whole beat and will trip post-record check 3, so note that before submitting. Cursor rests on the `reason:` line of the `BLOCKED` post for the last 8 seconds of the beat.

Beat 5 keeps its words. Its cell claims nothing was done. Choreography change: scroll through the BLOCKED chains 1:10–1:22, then rest the cursor on the `• none (all actions blocked or empty)` line 1:22–1:27.

Beat 7 has no `DONE` chain to return to. Use the last chain above `—— Work done this round ——` and rest on its `VERIFIER · approved` label, which is still true: the gate approved, the worker could not resolve the object, the worker said so.

### Case B · The Inbox FINDING block

**B1 · The Inbox block is empty or absent.** This is the expected live state. No change to words or choreography. Do not pause where the block would have been.

**B2 · Inbox cards are on screen.** No change to words; the beat 1 Say cell names lanes, not card counts. Split the beat this way instead of the section 1 table: 0:00–0:03 on the pass 1 header, 0:03–0:09 through the Ops block with 2 s on the first Ops card's `ref:` line, 0:09–0:12 through the Inbox block with 2 s on the first Inbox card's `ref:` line, 0:12–0:17 through the Follow-up block with 2 s on the first Follow-up card's `ref:` line. Do not describe what the Inbox card says. The three seeded drafts in the live Mail are not agent output, and any Inbox card that cites them is a card about seed data.

### Case C · Pass 2 never appears, or the floor stops mid-round

**Symptom.** With only the default token, the round posts the pass 1 header, the watcher cards, the pass 2 header, the `PROBLEM` cards, the refusal-theater header, and one `ASSIGN · Inbox → send email to customer`. Then nothing: no `VERIFIER · refused`, no `BLOCKED`, no `—— Work done this round ——`, no `—— Round … · done ——`, and no new brief in `#attention`. The terminal that ran the round shows a line beginning `──── SAFETY · as_agent('verifier'): no verifier token and no Desk token`. This is `McpClient.as_agent` failing closed by design.

**What to do in the next 5 minutes.**

1. Minute 0. Stop the recording. Do not scroll the dead round; it stays above the next round's pass 1 header and out of frame.
2. Minute 1. Put the Desk agent's token into the environment that runs the round, either as `AMBIGUOUS_TOKEN_DESK=…` on one line in `/Users/raihanahmed/Desktop/the-floor/.env`, which `round.py` loads at import, or as an export in the same shell. The token comes from the Ambiguous workspace where per-agent tokens are issued. Never paste it on camera and never print it.
3. Minute 2. Confirm it loads without printing it:

   ```bash
   cd /Users/raihanahmed/Desktop/the-floor && .venv/bin/python -c "import os,dotenv; dotenv.load_dotenv('.env'); print('desk or verifier token:', bool(os.environ.get('AMBIGUOUS_TOKEN_DESK') or os.environ.get('AMBIGUOUS_TOKEN_VERIFIER')))"
   ```

   You want `desk or verifier token: True`.
4. Minute 3. Run one fresh live round from that shell. Wait for `—— Round <stamp> · done ——` on the floor and a new brief in `#attention`.
5. Minute 4. Scroll `#agents-floor` so the new round's `—— Round <stamp> · pass 1 ——` is the top of frame. Confirm you can see `VERIFIER · refused` twice and at least one `DONE`. Confirm rank 1 of the new brief is Ember Grill. Start the take again from beat 1.

This retry spends one of the two retries in the round budget. If the second attempt also stops at the first `VERIFIER` post, the token is not reaching the process; check that the shell running the round is the shell where you exported it, and that `.env` is at the repo root and not inside `floor/`.

### Case D · The brief's rank 1 is not Ember Grill

**Symptom.** Item 1 reads `1. @dana — Pine & Salt ($120,000)` and item 3 reads `3. @dana — T-1` with a bare task id. The `PROBLEM · … · rank 1` card on the floor is Pine & Salt. This is the heuristic path: `ANTHROPIC_API_KEY` did not load, and the eval scores that run AMBER. Do not record it.

**What to do.**

1. Create or fix `/Users/raihanahmed/Desktop/the-floor/.env` with one line, `ANTHROPIC_API_KEY=…`. Do not `cat` it, do not `echo` the variable, and do not open it in an editor on camera.
2. Confirm it loads without printing it:

   ```bash
   cd /Users/raihanahmed/Desktop/the-floor && .venv/bin/python -c "import os,dotenv; dotenv.load_dotenv('.env'); print('key loaded:', bool(os.environ.get('ANTHROPIC_API_KEY')))"
   ```

   You want `key loaded: True`.
3. Run one fresh live round. Check the new brief. Item 1 must read `1. @theo — Ember Grill`.

**If the key is loaded and rank 1 is still not Ember Grill.** The stabiliser promotes to rank 1 only a problem whose account or evidence text contains "Ember" (`_stabilize_brief`, `floor/round.py`). A problem that only mentions T-4 or withholding gets owner theo but sorts after Pine & Salt and Copper Kettle and is cut by the three-item cap, which is what happens to `PROBLEM · T-4` in the mock. The backfill (`_ensure_golden_problems`) synthesises an Ember problem only when a pass 1 card mentions Ember, T-4, withholding, or penalty and no problem already mentions Ember, T-4, or withholding. If neither happened live, do not spend a second retry on it. The beat 6 Say cell names no account, owner, or dollar amount, so the words do not change. Record beat 6 with the section 1 choreography as written, resting on whichever three items the round produced, and keep the cursor off every `Ready:` line.

### Case E · The Ops FINDING block is empty, or a PROBLEM card is titled by a UUID

**Symptom.** Pass 1 shows `FINDING · Follow-up` cards and no `FINDING · Ops`, and the first `PROBLEM` card reads `PROBLEM · <36-character id> · rank 1`. Reproduced offline on a live-shaped client: the live CRM has no stage-entered date, every fallback Ops rule requires one, and a deal with no `updated_at` is treated as active today. Follow-up task cards then carry no account name, so the merge keys them by their live id.

**What to do.** No retry fixes this on the fallback path; it is a data-shape gap in `floor/client.py`, owned elsewhere. With `ANTHROPIC_API_KEY` loaded the model path can still name accounts from titles and notes, so confirm the key first (Case D). Then choreograph around it: beat 1 rests on a Follow-up card's `ref:` line, beat 2 rests on the first `PROBLEM` card that has an account name, and beat 4 uses a Follow-up `assign_task` chain. The Say cells name lanes and the gate, not card counts or account names, so no words change. If every `PROBLEM` card is a UUID, rest beat 2 on the `merges:` line, which still shows the evidence ids, and keep the cursor off the title.

If a judge asks why Ops is quiet: "The live CRM does not record when a deal entered its stage, and Ops keys on that. The mock has it, the live seed cannot. That is a client mapping to fix, not a watcher failure."

**Authorship.** With only the Desk token set, every post in the round is signed by the Desk seat. If the take is meant to show watcher seats, `AMBIGUOUS_TOKEN_OPS`, `AMBIGUOUS_TOKEN_INBOX` and `AMBIGUOUS_TOKEN_FOLLOWUP` must be set before the warm round. Otherwise do not say "each watcher posts its own card"; say "each lane posts its own card".

---

## 4. B-roll ban list

None of these appears in the take, in a cutaway, or in a still. Each one either proves nothing about the current code or proves something the code does not do.

| Banned | Why |
|---|---|
| Terminal | The proof is the live floor. A terminal invites the question of whether the floor is real. |
| Source code, any file | The take is a product recording. Source belongs in the judge Q&A, not on screen. |
| Mock transcript, including `MOCK_ROUND_VALIDATE3.txt` and any `run.txt` | No mock output is evidence of the live protocol, and the only committed validation predates the protocol entirely. |
| Mail drafts, the Mail tab, any draft object | The three drafts in the live Mail were placed during seeding and are not agent output. Live agent drafts BLOCK on the empty inbox. |
| The `Ready:` line under any brief item | It prints planned actions, not executed ones. Live it can read `draft reply` for a draft that never existed. |
| Reply handling | Implemented behind `FLOOR_REPLY_LOOP=1`, off for this recording. The brief makes no reply promise while off. |
| Timeline or any `[Timeline] Skipped re-escalation` line | Optional behind `--timeline`, off for this recording. Runtime state is outside tracked seed data. |
| Any file under `prompts/` | `prompts/desk.md` names the expected merges and the required brief order. On screen it turns the derived merge into a script. |
| Any dashboard, board, or console outside the Ambiguous workspace | Only Ambiguous channels are the demo surface. |
| The `human:` line on a `PROBLEM` card and any `• task → @dana` bullet | Task owner routing defaults every task to dana. True, on the floor, and not a strength. |

---

## 5. Post-record checklist

Fill the timestamp column from the finished recording. Every spoken claim needs one receipt on screen at the moment it is said, or, where the row says so, earlier in the same take. A claim with no receipt is cut from the voice-over before submission, not defended in Q&A. Three rows below have no on-screen receipt; each one names the cut.

| # | Spoken claim | Channel | Label to find it under | Timestamp |
|---|---|---|---|---|
| 1 | This is Brightline Payroll. One stuck customer leaves signals in different tools | `#agents-floor` | the same account name under a `FINDING · Ops` card and a `FINDING · Follow-up` card; in the mock, Copper Kettle Group at `ref: D-101` and in the `what:` line of `ref: T-1` | __:__ |
| 2 | Three watchers, each with one lane | `#agents-floor` | `FINDING · Ops · …` and `FINDING · Follow-up · …` blocks with distinct labels; the lanes themselves are code in `floor/router.py` | __:__ |
| 3 | Ops reads the CRM | `#agents-floor` | every `FINDING · Ops` card's `ref:` is a deal ref | __:__ |
| 4 | Inbox reads mail | `#agents-floor` | a `FINDING · Inbox` card's `ref:` is a mail ref if one is in frame; with no Inbox card the claim is about the lane, which is code, and posts nothing to read | __:__ |
| 5 | Follow-up reads tasks and calendar | `#agents-floor` | every `FINDING · Follow-up` card's `ref:` is a task or event ref | __:__ |
| 6 | The cards on screen are facts and ids | `#agents-floor` | the `ref:` and `what:` lines of the cards under the cursor | __:__ |
| 7 | Pass two. The Desk reads the whole floor and merges same-account cards into one ranked problem | `#agents-floor` | `—— Round <stamp> · pass 2 · Desk merge ——`, line `Merged N findings → M problem(s).`, then `PROBLEM · <account> · rank 1` | __:__ |
| 8 | Each problem card carries its evidence ids, so you can trace the merge back to the cards above it | `#agents-floor` | the `merges:` line on the rank 1 and rank 2 cards; the ids match `ref:` lines from beat 1 | __:__ |
| 9 | Before any worker acts, the Desk posts two deliberately unsafe asks | `#agents-floor` | `—— Refusal theater · unsafe asks (must not execute) ——`, placed before the first approved chain; `ASSIGN · Inbox → send email to customer` and `ASSIGN · Ops → set_field` | __:__ |
| 10 | Send an email to a customer. Move a deal's stage. The verifier gate refuses both, and both end BLOCKED | `#agents-floor` | `VERIFIER · refused` with reason `customer send is forbidden; draft only`, then `BLOCKED · Inbox · send email to customer`; `VERIFIER · refused` with reason `field 'stage' is blocked (safety)`, then `BLOCKED · Ops · set_field` | __:__ |
| 11 | These are safety tests, not customer work. The round runs them every time | `#agents-floor` | header line `Desk received two out-of-policy requests. Verifier must refuse both.`; "every time" has no on-screen receipt in a single-round take: it is the unconditional `_refusal_theater` call at the top of `execute_actions`, answered in Q&A, or cut that sentence from the Say cell before submitting | __:__ |
| 12 | Every assignment is one bounded step | `#agents-floor` | `ASSIGN · Ops → add note` carries one action, one account, one ref | __:__ |
| 13 | The Desk posts ASSIGN | `#agents-floor` | `ASSIGN · Ops → add note`, line `rule: wait for VERIFIER · approved before write` | __:__ |
| 14 | The gate posts its verdict: approved, refused, or needs rewrite | `#agents-floor` | `VERIFIER · approved`, reason `allowlist + safety checks passed`; `refused` receipts are row 10; `needs_rewrite` has no on-screen receipt in this round and is answered from `_verify_action` in Q&A, or cut those two words from the Say cell before submitting | __:__ |
| 15 | The worker posts DONE or BLOCKED | `#agents-floor` | `DONE · Ops · add_note`, line `result: note on deal <ref>`; `BLOCKED` receipts are row 10 | __:__ |
| 16 | Nothing writes until the floor shows approved | `#agents-floor` | `VERIFIER · approved` sits above `DONE` in the same frame; the `rule:` line on `ASSIGN` | __:__ |
| 17 | Every step is on the floor as a post: the ask, the verdict, the receipt | `#agents-floor` | the repeating `ASSIGN`, `VERIFIER`, `DONE` labels during the beat 5 scroll | __:__ |
| 18 | Anyone can read the audit trail without a terminal | `#agents-floor` | the frame is an Ambiguous channel and nothing else is in the take (section 4) | __:__ |
| 19 | A BLOCKED receipt is not hidden. It means the worker stopped instead of guessing | `#agents-floor` | any `BLOCKED · …` post with its `reason:` line that has been in frame: the two refusal-theater posts from row 10, and live, any `BLOCKED · Inbox · draft` that passed through in beat 5 | __:__ |
| 20 | Humans get one brief in attention, capped at three items in code | `#attention` | `Attention brief · <date>`, line `3 item(s) need a person · everything else handled on the floor` | __:__ |
| 21 | Each item names an owner and the evidence ids behind it | `#attention` | `1. @… — …`, `2. @… — …`, `3. @… — …` and their `Evidence:` lines; if an item has no `Evidence:` line, note it here | __:__ |
| 22 | Everything else stayed on the floor, handled or blocked | `#attention` | `Handled without you: …` as the last visible line | __:__ |
| 23 | Nothing was sent to a customer | earlier in the take | no `send` bullet under `—— Work done this round ——` in beat 5; `BLOCKED · Inbox · send email to customer` from row 10; nothing in `#attention` shows it | __:__ |
| 24 | No stage changed | earlier in the take | `BLOCKED · Ops · set_field` from row 10; no `set stage` bullet under `—— Work done this round ——` | __:__ |
| 25 | No calendar was touched | earlier in the take | no calendar bullet under `—— Work done this round ——`; a `• flagged event · …` bullet is a floor post, not a calendar write | __:__ |
| 26 | The client cannot do those things | none | no on-screen receipt: `WorkspaceClient` in `floor/client.py` has no send method and no calendar write, and `set_deal_field` raises `PermissionError` for stage; that is code, not a post. Answer it from `floor/client.py` in Q&A, or cut this sentence from the Say cell before submitting | __:__ |
| 27 | Attention is a team sport. Most of the team does not have to be human | `#agents-floor` | the last `DONE` chain above `—— Work done this round ——`, cursor on `VERIFIER · approved` | __:__ |

Three checks after the table is full.

1. Rows 11, 14, and 26 each carry a spoken claim with no on-screen receipt. Before submitting, decide each one the same way: either the sentence stays and the Q&A answer named in the row is ready, or the sentence is cut from `demo/script.md` and re-recorded. Write the decision here: __ / __ / __
2. Search the recording for `Ready:` lines. If one is legible, note the timestamp here and re-record beat 6 with more zoom: __:__
3. Search the recording for the word "draft" in the audio; it should not be there. Then search the frames for `DONE · Inbox · draft` and for any `BLOCKED · Inbox · draft` that the cursor rested on. A `BLOCKED · Inbox · draft` that only passed through during the beat 5 scroll is expected and is a receipt for row 19. A `DONE · Inbox · draft` should not exist live, because the inbox is empty. If either flagged case is there, decide whether to cut the beat before submitting, because it will get the question in section 3, case A1.
