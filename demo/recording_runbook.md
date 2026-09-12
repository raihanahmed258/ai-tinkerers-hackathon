# The Floor · recording runbook

One take, one voice, exactly 2:00, entirely inside the Ambiguous workspace. Record at 15:15. Submit by 16:00.

**Where this choreography comes from.** Use the completed 17:13–17:18 UTC live round documented in `LIVE_ROUND_REPORT.md`. It contains the full protocol and a one-item Ember Grill brief. Its channel posts do not prove model provenance. `MOCK_ROUND_VALIDATE3.txt` is model-backed but predates the protocol.

**Pre-roll blocker.** Open the existing 17:13 UTC round. Confirm it ends
with `—— Round 2026-09-12 17:13 · done ——` and links brief
`3c3d3750-29fc-4aed-9930-015caa11731c`. Do not spend credits or workspace
writes on a warm rerun. API keys and agent tokens are irrelevant when recording
an already completed round.

Browser setup: one window, two tabs, `#agents-floor` first and `#attention` second. Nothing else open. Zoom the browser until one `FINDING` card fills roughly a third of the frame; that zoom is what lets the brief's last two lines fall below the fold in beat 6. Do Not Disturb on. Quit Mail, Slack, and Messages.

---

## 1. Scroll choreography

Seven beats, contiguous, the last one ends at 2:00. The beats match the seven rows of the shot list in `demo/script.md`. Scroll direction is downward for the whole take except one short upward scroll in beat 7. Start the take with the most recent `—— Round <stamp> · pass 1 ——` header at the top of the frame and never scroll above it. Older rounds and any dead partial round sit above that line and stay out of shot.

Label text below is exactly what the code posts. `<stamp>` is the round's date and time, for example `2026-09-12 15:05`. Live deal refs may print as UUIDs instead of `D-105`; do not read refs aloud in any beat.

### Beat 1 · 0:00–0:17 · Pass one · `#agents-floor`

| Time | Scroll to | Hold | Cursor rests on |
|---|---|---|---|
| 0:00–0:03 | `—— Round <stamp> · pass 1 ——` | 3 s | the second line, `Watchers posting FINDING cards here.` |
| 0:03–0:17 | drift down through the eight `FINDING · Follow-up · …` cards | 14 s total, 2 s on the first card | one visible `ref:` line |

The observed round has no Ops or Inbox findings. Do not pause on older cards
from another round and do not claim that all three lanes found something.

### Beat 2 · 0:17–0:33 · Pass two · `#agents-floor`

| Time | Scroll to | Hold | Cursor rests on |
|---|---|---|---|
| 0:17–0:20 | `—— Round <stamp> · pass 2 · Desk merge ——` | 3 s | the second line, `Merged N findings → M problem(s).` |
| 0:20–0:33 | `PROBLEM · <account> · rank 1` and `PROBLEM · <account> · rank 2`, both cards in frame | 13 s | the `merges:` line of the rank 1 card for 7 s, then the `merges:` line of the rank 2 card for 6 s |

The observed rank 1 card is `PROBLEM · Ember Grill · rank 1`, followed by
Copper Kettle Group. Do not rest the cursor on the `human:` or `actions:` line.
The `merges:` ids trace back to the cards in beat 1.

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

Use the first Follow-up task chain after refusal theater that ends in `DONE`.

| Time | Scroll to | Hold | Cursor rests on |
|---|---|---|---|
| 0:52–0:56 | `ASSIGN · Follow-up → assign task` | 4 s | the `rule:` line, `wait for VERIFIER · approved before write` |
| 0:56–1:02 | `VERIFIER · approved` | 6 s | the `reason:` line, `allowlist + safety checks passed` |
| 1:02–1:10 | `DONE · Follow-up · assign_task` | 8 s | the `result:` line |

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
| 1:28–1:31 | `Attention brief · <date>` at the top of the frame | 3 s | the second line, `1 item(s) need a person · everything else handled on the floor` |
| 1:31–1:40 | `1. @theo — Ember Grill` | 9 s | the item's first line |
| 1:40–1:46 | the Ember Grill evidence | 6 s | its `Evidence:` line |
| 1:46–1:50 | no scroll | 4 s | `Handled without you: …` |

This brief has one item. One is valid because the cap is **at most** three.
Execution status appears only in the floor's `DONE` and `BLOCKED` receipts.

The beat 6 Say cell names no account, no owner, and no dollar amount. Do not add them. The cursor on the owner lines is the receipt for "Each item names an owner".

### Beat 7 · 1:50–2:00 · Tagline · `#agents-floor`

| Time | Scroll to | Hold | Cursor rests on |
|---|---|---|---|
| 1:50–1:51 | click the `#agents-floor` tab | 1 s | nothing |
| 1:51–2:00 | the last chain that ends in `DONE` immediately above `—— Work done this round ——`, with `ASSIGN`, `VERIFIER · approved`, `DONE` all in frame | 9 s | the `VERIFIER · approved` label, cursor still |

The tab keeps the beat 5 scroll position, so this chain is one short upward scroll from the `—— Work done this round ——` header. Do not go back to the beat 4 chain; it is many chains higher. In the mock the last chain is Follow-up: `ASSIGN · Follow-up → create task`, `VERIFIER · approved`, `DONE · Follow-up · assign_task`. Live it may be Ops or Follow-up. Any chain ending in `DONE` is a valid receipt for the tagline. Stop scrolling before you speak. Say the line, stop, let the recording run out. Add nothing after it.

---

## 2. Voice-over script

Rate: 2.5 words per second. Cap: 300 words. This script is 240 words,
96 seconds spoken inside 120 seconds, with 24 seconds of slack for scrolling
and tab switches.

**Source of truth.** The Say cells below are copied word for word from the seven rows of `demo/script.md` in the working tree at reconciliation time. If Part A's review changes that file, change this section to match and re-run the counts. One label caution: `demo/script.md` writes the blocked draft post as `BLOCKED · Inbox · draft reply`; the code prints `BLOCKED · Inbox · draft`, because `execute_actions` passes the action type `draft` to `_post_blocked`. The `ASSIGN` label is `ASSIGN · Inbox → draft reply`. This runbook uses the labels the code prints.

| Beat | Range | Length | Words | Spoken | Slack |
|---|---|---|---|---|---|
| 1 · Pass one | 0:00–0:17 | 17 s | 38 | 15.2 s | 1.8 s |
| 2 · Pass two | 0:17–0:33 | 16 s | 35 | 14.0 s | 2.0 s |
| 3 · Refusal theater | 0:33–0:52 | 19 s | 37 | 14.8 s | 4.2 s |
| 4 · One approved chain | 0:52–1:10 | 18 s | 35 | 14.0 s | 4.0 s |
| 5 · Remaining chains to work done | 1:10–1:27 | 17 s | 38 | 15.2 s | 1.8 s |
| 6 · The brief | 1:27–1:50 | 23 s | 42 | 16.8 s | 6.2 s |
| 7 · Tagline | 1:50–2:00 | 10 s | 15 | 6.0 s | 4.0 s |
| **Total** | **0:00–2:00** | **120 s** | **240** | **96.0 s** | **24.0 s** |

Beat 6 is the one to rehearse twice. It is the longest cell, the cursor has to land on three item lines, and the last four sentences are the ones a judge will test.

### Beat 1 · 0:00–0:17 · 38 words

> This is Brightline Payroll. One stuck customer can leave signals in different tools. Three lanes inspect separate slices: Ops reads CRM, Inbox reads mail, and Follow-up reads tasks, calendar, and selected chat. This live round found follow-up evidence.

The three lanes are code in `floor/router.py`. Only Follow-up produced findings
in this round, and the narration says that explicitly.

### Beat 2 · 0:17–0:33 · 35 words

> Pass two. The Desk reads the whole floor and merges same-account cards into one ranked problem. Each problem card carries its evidence ids, so you can trace the merge back to the cards above it.

### Beat 3 · 0:33–0:52 · 37 words

> In this safety demo, the Desk posts two deliberately unsafe asks. Send an email to a customer. Move a deal's stage. The verifier gate refuses both, and both end BLOCKED. These are synthetic tests, not customer work.

This block appears only because the recording command includes `--safety-demo`.

### Beat 4 · 0:52–1:10 · 35 words

> Now the real work. Every assignment is one bounded step. The Desk posts ASSIGN. The gate posts its verdict: approved or refused. The worker posts DONE or BLOCKED. Nothing writes until the floor shows approved.

"The gate posts its verdict" is the honest wording. There is no Verifier seat
and no Closer seat in the workspace. Do not say "the Verifier agent." The
recording shows approved and refused, so those are the only verdicts named.

### Beat 5 · 1:10–1:27 · 38 words

> Every step is on the floor as a post: the ask, the verdict, the receipt. Anyone can read the audit trail without a terminal. A BLOCKED receipt is not hidden. It means the worker stopped instead of guessing.

This cell claims nothing about what got done, so it stands unchanged under section 3, case A2. The receipt for "A BLOCKED receipt is not hidden" is any `BLOCKED · …` post that has been in frame in the take: the two refusal-theater posts in beat 3, and live, any `BLOCKED · Inbox · draft` that passes through in this beat.

### Beat 6 · 1:27–1:50 · 42 words

> Humans get one brief in attention, capped at three items in code. This round needs one human: Theo, for Ember Grill, with evidence ids attached. Everything else stayed on the floor, handled or blocked. Nothing was sent. No stage or calendar changed.

The cell names exactly what is on screen: Theo, Ember Grill, and evidence ids.
It says the brief is capped at three, not that three items must appear. The
receipts for the final safety sentence appeared earlier in the take.

### Beat 7 · 1:50–2:00 · 15 words

> Attention is a team sport. Most of the team does not have to be human.

---

## 3. Archived rerun contingencies — do not use for this recording

The cases below exist only to diagnose a future deliberate live run. They are
not recording instructions. If the existing 17:13 round cannot be found, use
the message ids in `LIVE_ROUND_REPORT.md`; do not start a replacement round.

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
2. Minute 1. Put the Desk agent's token into the repo-root `.env` as `AMBIGUOUS_TOKEN_DESK=…`, or export it in the same shell. The token comes from the Ambiguous workspace where per-agent tokens are issued. Never paste it on camera and never print it.
3. Minute 2. Confirm it loads without printing it:

   ```bash
   cd /path/to/the-floor && .venv/bin/python -c "import os,dotenv; dotenv.load_dotenv('.env'); print('desk or verifier token:', bool(os.environ.get('AMBIGUOUS_TOKEN_DESK') or os.environ.get('AMBIGUOUS_TOKEN_VERIFIER')))"
   ```

   You want `desk or verifier token: True`.
4. For a future engineering validation only, run one deliberate live round and
   wait for its done marker. Do not do this for the current recording.
5. Validate that future round separately; keep the recording on the proven
   17:13 round.

This retry spends one of the two retries in the round budget. If the second attempt also stops at the first `VERIFIER` post, the token is not reaching the process; check that the shell running the round is the shell where you exported it, and that `.env` is at the repo root and not inside `floor/`.

### Case D · The brief's rank 1 is not Ember Grill

**Symptom.** Item 1 reads `1. @dana — Pine & Salt ($120,000)` and item 3 reads `3. @dana — T-1` with a bare task id. The `PROBLEM · … · rank 1` card on the floor is Pine & Salt. This is the heuristic path: `ANTHROPIC_API_KEY` did not load, and the eval scores that run AMBER. Do not record it.

**What to do.**

1. Create or fix the repo-root `.env` with `ANTHROPIC_API_KEY=…`. Do not `cat` it, echo the variable, or open it on camera.
2. Confirm it loads without printing it:

   ```bash
   cd /path/to/the-floor && .venv/bin/python -c "import os,dotenv; dotenv.load_dotenv('.env'); print('key loaded:', bool(os.environ.get('ANTHROPIC_API_KEY')))"
   ```

   You want `key loaded: True`.
3. For a future engineering validation only, run one deliberate live round.
   Do not do this for the current recording.

**If the key is loaded and rank 1 is still not Ember Grill.** The stabiliser promotes to rank 1 only a problem whose account or evidence text contains "Ember" (`_stabilize_brief`, `floor/round.py`). A problem that only mentions T-4 or withholding gets owner theo but sorts after Pine & Salt and Copper Kettle and is cut by the three-item cap, which is what happens to `PROBLEM · T-4` in the mock. The backfill (`_ensure_golden_problems`) synthesises an Ember problem only when a pass 1 card mentions Ember, T-4, withholding, or penalty and no problem already mentions Ember, T-4, or withholding. If neither happened live, do not spend a second retry on it. The beat 6 words name no account, owner, or dollar amount, so they do not change.

### Case E · The Ops FINDING block is empty, or a PROBLEM card is titled by a UUID

**Symptom.** Pass 1 shows `FINDING · Follow-up` cards and no `FINDING · Ops`, and the first `PROBLEM` card reads `PROBLEM · <36-character id> · rank 1`. Reproduced offline on a live-shaped client: the live CRM has no stage-entered date, every fallback Ops rule requires one, and a deal with no `updated_at` is treated as active today. Follow-up task cards then carry no account name, so the merge keys them by their live id.

**What to do.** No retry fixes this on the fallback path; it is a data-shape gap in `floor/client.py`, owned elsewhere. With `ANTHROPIC_API_KEY` loaded the model path can still name accounts from titles and notes, so confirm the key first (Case D). Then choreograph around it: beat 1 rests on a Follow-up card's `ref:` line, beat 2 rests on the first `PROBLEM` card that has an account name, and beat 4 uses a Follow-up `assign_task` chain. The Say cells name lanes and the gate, not card counts or account names, so no words change. If every `PROBLEM` card is a UUID, rest beat 2 on the `merges:` line, which still shows the evidence ids, and keep the cursor off the title.

If a judge asks why Ops is quiet: "The live CRM does not record when a deal entered its stage, and Ops keys on that. The mock has it, the live seed cannot. That is a client mapping to fix, not a watcher failure."

**Authorship.** The existing round visibly includes Desk, Follow-up, Inbox, and
Ops authorship. Do not infer token configuration beyond what appears on screen.

---

## 4. B-roll ban list

None of these appears in the take, in a cutaway, or in a still. Each one either proves nothing about the current code or proves something the code does not do.

| Banned | Why |
|---|---|
| Terminal | The proof is the live floor. A terminal invites the question of whether the floor is real. |
| Source code, any file | The take is a product recording. Source belongs in the judge Q&A, not on screen. |
| Mock transcript, including `MOCK_ROUND_VALIDATE3.txt` and any `run.txt` | No mock output is evidence of the live protocol, and the only committed validation predates the protocol entirely. |
| Mail drafts, the Mail tab, any draft object | The three drafts in the live Mail were placed during seeding and are not agent output. Live agent drafts BLOCK on the empty inbox. |
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
| 1 | This is Brightline Payroll | `#agents-floor` | the round's fictional customer data | __:__ |
| 2 | Three lanes inspect separate slices | `#agents-floor` | Follow-up's distinct label on every live finding; lane boundaries are code | __:__ |
| 3 | This live round found follow-up evidence | `#agents-floor` | eight `FINDING · Follow-up` cards | __:__ |
| 7 | Pass two. The Desk reads the whole floor and merges same-account cards into one ranked problem | `#agents-floor` | `—— Round <stamp> · pass 2 · Desk merge ——`, line `Merged N findings → M problem(s).`, then `PROBLEM · <account> · rank 1` | __:__ |
| 8 | Each problem card carries its evidence ids, so you can trace the merge back to the cards above it | `#agents-floor` | the `merges:` line on the rank 1 and rank 2 cards; the ids match `ref:` lines from beat 1 | __:__ |
| 9 | In this safety demo, the Desk posts two deliberately unsafe asks | `#agents-floor` | `—— Refusal theater · unsafe asks (must not execute) ——`, placed before the first approved chain; `ASSIGN · Inbox → send email to customer` and `ASSIGN · Ops → set_field` | __:__ |
| 10 | Send an email to a customer. Move a deal's stage. The verifier gate refuses both, and both end BLOCKED | `#agents-floor` | `VERIFIER · refused` with reason `customer send is forbidden; draft only`, then `BLOCKED · Inbox · send email to customer`; `VERIFIER · refused` with reason `field 'stage' is blocked (safety)`, then `BLOCKED · Ops · set_field` | __:__ |
| 11 | These are synthetic tests, not customer work | `#agents-floor` | header line `Desk received two out-of-policy requests. Verifier must refuse both.` | __:__ |
| 12 | Every assignment is one bounded step | `#agents-floor` | `ASSIGN · Follow-up → assign task` carries one action and one ref | __:__ |
| 13 | The Desk posts ASSIGN | `#agents-floor` | `ASSIGN · Follow-up → assign task`, line `rule: wait for VERIFIER · approved before write` | __:__ |
| 14 | The gate posts approved or refused | `#agents-floor` | `VERIFIER · approved`; refused receipts are row 10 | __:__ |
| 15 | The worker posts DONE or BLOCKED | `#agents-floor` | `DONE · Ops · add_note`, line `result: note on deal <ref>`; `BLOCKED` receipts are row 10 | __:__ |
| 16 | Nothing writes until the floor shows approved | `#agents-floor` | `VERIFIER · approved` sits above `DONE` in the same frame; the `rule:` line on `ASSIGN` | __:__ |
| 17 | Every step is on the floor as a post: the ask, the verdict, the receipt | `#agents-floor` | the repeating `ASSIGN`, `VERIFIER`, `DONE` labels during the beat 5 scroll | __:__ |
| 18 | Anyone can read the audit trail without a terminal | `#agents-floor` | the frame is an Ambiguous channel and nothing else is in the take (section 4) | __:__ |
| 19 | A BLOCKED receipt is not hidden. It means the worker stopped instead of guessing | `#agents-floor` | any `BLOCKED · …` post with its `reason:` line that has been in frame: the two refusal-theater posts from row 10, and live, any `BLOCKED · Inbox · draft` that passed through in beat 5 | __:__ |
| 20 | Humans get one brief in attention, capped at three items in code | `#attention` | `Attention brief · <date>`, line `1 item(s) need a person · everything else handled on the floor` | __:__ |
| 21 | This round needs Theo for Ember Grill, with evidence ids | `#attention` | `1. @theo — Ember Grill` and its `Evidence:` line | __:__ |
| 22 | Everything else stayed on the floor, handled or blocked | `#attention` | `Handled without you: …` as the last visible line | __:__ |
| 23 | Nothing was sent | earlier in the take | `BLOCKED · Inbox · send email to customer` from row 10 | __:__ |
| 24 | No stage or calendar changed | earlier in the take | `BLOCKED · Ops · set_field`; no calendar action appears in the work summary | __:__ |
| 27 | Attention is a team sport. Most of the team does not have to be human | `#agents-floor` | the last `DONE` chain above `—— Work done this round ——`, cursor on `VERIFIER · approved` | __:__ |

Two checks after the table is full.

1. Confirm every completion claim has a visible `DONE` receipt.
2. A `BLOCKED · Inbox · draft` may pass through the frame, but do not stop on
   it. A `DONE · Inbox · draft` should not exist because the live inbox is empty.
