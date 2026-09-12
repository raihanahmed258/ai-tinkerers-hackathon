# The Floor · two-minute screen recording script

One take. Your voice. Exactly 2:00.

**What is on screen:** two surfaces and nothing else. A browser on the Ambiguous workspace for the opening shot, then a terminal for the rest. The round runs on `MockClient`, so the terminal transcript of `#agents-floor` and `#attention` is the floor. This is the honest path and the script says so out loud at 0:31.

**What this script will not do:** it does not cut to a Mail draft, it does not show a CRM note appearing, it does not claim the Desk replies inside each finding's thread, and it does not stage a human reply loop. None of those happened in the validated run. The brief's own printed last line still advertises a reply loop, so checklist item 6 tells you how to keep it out of shot. See the internal notes at the bottom for what was cut and why.

## Optional architecture card — after the timed take, not inside it

If a judge asks what comes after the MVP, open [`architecture.md`](architecture.md). It shows the intended small-org handoff: **Desk → workers → Verifier → brief**. Say: "The current run has the watchers, Desk, closed action set, and brief. Verifier and Closer are the next safety handoff; they are designed, not demoed." Do not place this card inside the 2:00 recording or imply the validated run exercised it.

---

## 1. Pre-record checklist

Work top to bottom. Item 1 is a blocker. Do not start recording with it unresolved.

### 1. The model key. This is the blocker.

As of writing this script there is **no `.env` file at the repo root** and no `ANTHROPIC_API_KEY` in the shell. If you record in that state, `run_watcher` falls back to heuristic rules silently, and the brief comes out visibly wrong: the Ember Grill item at rank 1 disappears completely, and item 3 degenerates into a bare task id with the account rendered as `T-1` assigned to dana. There is no error message. The round just looks finished.

Create `/Users/raihanahmed/Desktop/the-floor/.env` with one line:

```
ANTHROPIC_API_KEY=sk-ant-...
```

Then confirm it actually loads, the same way `round.py` loads it:

```bash
cd /Users/raihanahmed/Desktop/the-floor && .venv/bin/python -c "import os,dotenv; dotenv.load_dotenv('.env'); print('key loaded:', bool(os.environ.get('ANTHROPIC_API_KEY')))"
```

You want `key loaded: True`. That command prints a boolean and never the key itself. Do not `cat .env`, do not `echo $ANTHROPIC_API_KEY`, and do not open `.env` in an editor while recording.

The second confirmation is the one that matters, and you get it from the dry run in section 2. **Brief item 1 must read `@theo — Ember Grill`.** If item 1 is anything else, the key did not load, and nothing else on this list is worth doing yet.

### 2. Dry run and score it

Mock mode reseeds itself on every run, because `MockClient.__post_init__` loads the seed into a fresh in-memory workspace. There is no manual reseed step for the terminal path. Confirm the seed still loads clean:

```bash
cd /Users/raihanahmed/Desktop/the-floor && .venv/bin/python -m floor.seed
```

Expect `20 deals, 12 threads, 9 tasks, 9 events, 26 chat messages`.

Then run section 2's measure command, and score the captured log:

```bash
cd /Users/raihanahmed/Desktop/the-floor && .venv/bin/python -m floor.eval_expected run.txt
```

Read two lines off the scorecard. `GREEN` on the header line, and `Finding cards: 17`. If the card count is not 17, use the number you actually see in the narration at 0:31 and 1:14. Do not say seventeen if the screen says sixteen.

### 3. Tabs, exactly these

Browser, four tabs, in this left-to-right order:

1. CRM, Brightline Sales pipeline, board view, all 20 deals visible.
2. Tasks, the 9 seeded tasks.
3. Calendar, showing the seeded events.
4. `#ops-team` chat.

No Mail tab. Live inbound mail is zero, so a Mail tab on camera is an empty promise.

Terminal, one window, maximized, font around 18pt, sized so a full FINDING card fits without line wrapping. Clear the scrollback, then in variant B run the section 2 measure command immediately, so the invocation line is the first line in the buffer. Never clear the scrollback after the round has run. In variant B that output is the recording.

Leave `#agents-floor` and `#attention` in the browser closed. They were never touched during live seeding and they are empty. The floor you point at is the terminal.

### 4. Mute everything

macOS Do Not Disturb on. Quit Mail, Slack and Messages. Phone face down and silent. Close any editor with an unsaved-changes badge that might toast mid-take.

### 5. The honest line about Inbox

Say it once, exactly as written in beat 3, and then move on:

> "This round runs on our offline mock, because the live workspace cannot hold fictional inbound mail."

That is the whole concession. It costs six seconds, it is already inside the 2:00 budget, and it buys you every other claim in the video. Do not apologize for it twice and do not expand on it.

### 6. Three things not to ad-lib

Brief item 3 prints the line `Ready: draft_reply, assign_task` on screen. Those are capability names. **No draft object exists in this run.** Do not read that line aloud and do not say a draft is waiting in Mail.

**The brief's last printed line reads `Reply in this thread and I'll record it.`** It is appended unconditionally at `floor/round.py` line 1083, and `prompts/desk.md` line 41 asks the Desk to end that way, so it prints in every run with a key and without one. Nothing is listening. `reply_loop` is a print stub at `floor/round.py` line 1093 and its call is commented out of `run_round` at line 1128. Frame it out of shot in beats 5 and 6, never point the cursor at it, and never read it aloud. If a judge reads it off the recording, concede it in the same words `demo/judge_qa.md` uses: it is the designed ending and right now nothing is listening.

Card labels alternate between `followup` and `Follow-up`, and confidence prints as a word on some cards and a number on others. Leave it alone. It is cosmetic, no narration line depends on it, and `floor/round.py` belongs to someone else right now.

### 7. Capture

1080p. One take is fine, two is plenty. Hard stop coding at 15:15 and record.

---

## 2. Measure the round before you choose a variant

The wall clock for a round with real model calls has never been measured. There are four sequential Claude calls in a round. The heuristic no-key path finishes in about 0.2 seconds and tells you nothing about the real one. So measure it.

**Run this one command:**

```bash
cd /Users/raihanahmed/Desktop/the-floor && time .venv/bin/python -m floor.round | tee run.txt
```

Read the `real` line at the bottom. That is your number. The captured `run.txt` is what you feed the scorer in checklist item 2.

**Then pick:**

- **25 seconds or less: variant A is available.** Trigger the round live on camera.
- **More than 25 seconds: variant B.** Non-negotiable.

**Variant B is the default recommendation.** Take variant A only if the measured number genuinely comes in at or under 25 seconds. Three reasons B wins. The trigger beat is 21 seconds long, so a live round has to finish inside it or you are narrating dead air. Variant B lets you pre-scroll the terminal to the top of the floor, which turns beat 4 into one smooth downward scroll instead of a hunt. And in variant B the card count on screen is the same run you already scored GREEN, so the numbers you say cannot drift.

Both variants use the identical narration and the identical timecodes. Only your hands change. The total stays at 2:00 either way.

---

## 3. The timed script

| Beat | Range | Length | Words | Spoken at 2.5 w/s | Slack |
|---|---|---|---|---|---|
| 1 · The problem | 0:00-0:18 | 18s | 41 | 16.4s | 1.6s |
| 2 · The shape | 0:18-0:31 | 13s | 29 | 11.6s | 1.4s |
| 3 · Pass one | 0:31-0:52 | 21s | 46 | 18.4s | 2.6s |
| 4 · Three cards, one customer | 0:52-1:14 | 22s | 43 | 17.2s | 4.8s |
| 5 · The brief and the merge | 1:14-1:39 | 25s | 49 | 19.6s | 5.4s |
| 6 · What it is not allowed to do | 1:39-1:52 | 13s | 30 | 12.0s | 1.0s |
| 7 · Tagline | 1:52-2:00 | 8s | 15 | 6.0s | 2.0s |
| **Total** | **0:00-2:00** | **120s** | **253** | **101.2s** | **18.8s** |

Ranges are contiguous and the last one ends at 2:00. The 18.8 seconds of slack is deliberate breathing room.

Beat 5 looks like the roomiest beat in the table and it is not. The table counts `D-101, T-1, E-1` as three words. Read aloud it is nine: "D-one-oh-one, T-one, E-one". That makes beat 5 fifty-five spoken words, 22.0 seconds in a 25 second window, and about 3 seconds of real slack. That slack is exactly what you spend saying the three ids slowly. The tightest beats on paper are beat 6 at 1.0 seconds and beat 2 at 1.4 seconds. Rehearse beat 5 twice before the take, because it is the one beat where the written count understates the read.

---

### Beat 1 · 0:00-0:18 · The problem

**On screen:** browser. Start on the CRM board and hold about six seconds. Then about four seconds each on Tasks, Calendar and `#ops-team`, no clicking into records. That is six plus four plus four plus four, exactly the 18 seconds of the beat.

**Say:**

> "This is Brightline Payroll. Twenty deals in the CRM, nine tasks, nine meetings, and a chat channel full of promises. One customer is waiting on a quote we promised three weeks ago. Nobody knows. Nobody's job is to read all four."

**41 words, 16.4 seconds spoken in an 18 second beat.** The 1.6 seconds of slack goes on the pause before "Nobody knows."

---

### Beat 2 · 0:18-0:31 · The shape

**On screen:** switch to the terminal. Cleared. In variant A the command is typed but not yet run. In variant B scroll to the very top of the round output so the invocation line is what sits on screen.

**Say:**

> "So we staffed it. Three narrow agents, each watching one slice. They post to an agent-only channel. A fourth, the Desk, is the only one that talks to humans."

**29 words, 11.6 seconds spoken in a 13 second beat.**

---

### Beat 3 · 0:31-0:52 · Pass one

**Say, both variants:**

> "This round runs on our offline mock, because the live workspace cannot hold fictional inbound mail. Pass one. Ops reads the CRM, Inbox reads mail, Follow-up reads tasks, the calendar, and promises in chat. Seventeen findings hit the floor. Facts and dates, never opinions about people."

**46 words, 18.4 seconds spoken in a 21 second beat.**

**Variant A staging, only if your measured round is 25 seconds or less.** Press Return on camera at 0:31 and keep talking. The cards land in watcher order in three bursts, not a continuous stream: eight Ops cards at once when the first model call returns, then three Inbox, then six Follow-up. `run_round` posts each watcher's cards only after that watcher's single model call comes back, so there is dead air between the bursts. Keep talking through the gaps. A 25 second round also overruns this beat by four seconds, and beat 4's opening slack is already budgeted for two scrolls, so in variant A you spend that slack on the overrun and scroll while narrating instead. If your measured number is over 21 seconds, take variant B. Do not narrate faster to catch up.

**Variant B staging, the default.** The round already ran. The output is on screen from beat 2 and you scroll slowly down through the cards while you say the words, landing on the last Follow-up card at about 0:50. Proof that it is real code and not a saved text file: the invocation line `.venv/bin/python -m floor.round` sits at the top of the scrollback. Hold it for one second at 0:31 before you start scrolling. One second is enough. Do not linger on it and do not narrate it. The `real` timing is not up there. `time` prints it only after the pipeline exits, so it sits at the very bottom of the buffer, below the brief. Do not promise it in this beat and do not hunt for it mid-take.

---

### Beat 4 · 0:52-1:14 · Three cards, one customer

**On screen:** three FINDING cards for Copper Kettle. In the validated run they are card 1 (`ref: D-101`, agent `ops`), card 12 (`ref: T-1`, agent `followup`) and card 16 (`ref: E-1`, agent `Follow-up`). Scroll to each in turn and rest the cursor on the `ref:` line. Card order is model-written and can shift between runs, so re-locate all three in your dry run output before the take. Note that the `E-1` card writes the account as `Copper Kettle` while the other two write `Copper Kettle Group`. Same customer. Do not stumble on it. Note also that the `E-1` card's own evidence line ends "Related to overdue task T-1", and Follow-up wrote both that card and the `T-1` card. So do not say the watchers cannot tell it is one customer. The narration below is worded to survive a judge reading that card aloud.

**Say:**

> "Watch these three cards. Ops saw a deal stuck in Contract for twenty-three days. Follow-up saw the quote task nineteen days overdue, and a pricing review three weeks ago with no notes. Two watchers, three apps. Nobody has turned it into one ask."

**43 words, 17.2 seconds spoken in a 22 second beat.** The 4.8 seconds of slack pays for two scrolls, unless you are in variant A and already spent it on the round overrun. This is the setup for the payoff in beat 5, so land "one ask" and then stop talking for a moment. No watcher produced a ranked human item. The join into a single ask exists only in the Desk's brief, which is what beat 5 shows.

---

### Beat 5 · 1:14-1:39 · The brief and the merge

**On screen:** scroll to `POST → #attention`. Track the cursor down the three items as you name them, then rest it on the `Evidence: D-101, T-1, E-1` line under item 3 and leave it there. Finish with the cursor on the `Handled without you` footer, and stop scrolling so that footer is the last visible line in the frame. The footer needs no narration. It reads itself.

Two lines below the footer the brief prints `Reply in this thread and I'll record it.` Nothing is listening. Keep that line below the bottom of the frame, never point the cursor at it, and never read it aloud. Checklist item 6 has the full reason and the concession to use if a judge reads it off the recording.

**Say:**

> "Pass two. The Desk merges same-account findings. Theo: a filing the customer says never went out, penalties after the fifteenth. Dana: a champion who left, a hundred and twenty thousand dollar deal gone quiet. Priya: the quote. The evidence line. D-101, T-1, E-1. Seventeen findings in, three decisions out."

**49 words, 19.6 seconds spoken in a 25 second beat.** The three ids read aloud as nine words, not three, so the real figure is 55 spoken words and 22.0 seconds. That leaves about 3 seconds, and all 3 go on saying the ids slowly while the cursor confirms each one. The three refs on the Evidence line are the exact three cards you pointed at in beat 4, which is why beat 4 exists. That pairing is the whole demo.

---

### Beat 6 · 1:39-1:52 · What it is not allowed to do

**On screen:** stay on the brief. Cursor up to the header, which reads `3 item(s) need a person`, then back down. Keep the frame where beat 5 left it, with the `Handled without you` footer as the last visible line. No window switching in this beat. Do not cut to source.

**Say:**

> "Nothing was sent to a customer. No stage changed. No calendar touched. Two passes, no loops. The cap of three is enforced in code. The floor is the audit trail."

**30 words, 12.0 seconds spoken in a 13 second beat.** Every clause is true of the run on screen.

---

### Beat 7 · 1:52-2:00 · Tagline

**On screen:** scroll back up so the floor fills the frame. Stop scrolling before you speak.

**Say:**

> "Attention is a team sport. Most of the team does not have to be human."

**15 words, 6.0 seconds spoken in an 8 second beat.** The 2 seconds of slack is the landing. Say the line, stop, let the recording run out. Do not add anything after it.

---

## 4. If a judge asks during the recording

Not part of the 2:00. Do not answer any of this on camera. `demo/judge_qa.md` has the long-form answers. These four are the ones the video itself invites.

**"Where is the draft you prepared?"** There isn't one in this run. The brief prints `Ready: draft_reply, assign_task` as capability, and in this round the Desk chose three tasks and four one-line questions instead. `create_draft` is implemented. It did not fire here.

**"Show me the refusal."** Cannot, from a round. Nothing in a normal round trips the allowlist. It is `ALLOWED_ACTIONS` in `execute_actions` in `floor/round.py`, and it is a code-level guarantee you read rather than a scene you watch.

**"What happens when Dana replies in the thread?"** Nothing yet, and this is the answer to use if a judge reads the brief's last line off the recording. The brief does print `Reply in this thread and I'll record it.` `reply_loop` is a print stub at `floor/round.py` line 1093 and its call is commented out of `run_round` at line 1128, so nothing polls the thread. That line is the designed ending and nothing is listening yet. It is the next piece of work, not a claim for today.

**"Is this live?"** Mock, and the script says so at 0:31. The live workspace is seeded and the MCP client is implemented, but Ambiguous has no way to inject fictional inbound mail, so the Inbox watcher has nothing to read against it. The merge you just watched is real either way.

---
---

## Internal notes: what was cut from the earlier draft, and why

Deliberate. Each cut traces to a verified gap in the validated run (`MOCK_ROUND_VALIDATE3.txt`). The earlier draft promised eight things the recording cannot show, across seven verified gaps: G1 through G5, G7 and G8.

1. **Cut the Mail cut-away and "Inbox, draft the reply" (G2).** Zero email drafts were created in that run. There are no `DRAFT (not sent)` lines in the log at all. The old draft cut to Mail and said a draft appears. It does not. Also cut "draft ready" from the Priya line in the brief beat, for the same reason.

2. **Cut the CRM note appearing and "Ops, attach the reason to the record" (G1).** Zero CRM notes were written. There are no `CRM NOTE` lines in the log. The old beat at 0:55 cut to the CRM to watch a note land.

3. **Cut "Desk replies appear in threads" (G3).** No `PROBLEM` blocks were posted to the floor. The merge is visible only as the `Evidence:` line inside the brief. This is why beats 4 and 5 were rebuilt around the two artifacts that are genuinely on screen: the three watcher cards for Copper Kettle sitting on the floor, and the `Evidence: D-101, T-1, E-1` line that joins a deal id, a task id and an event id for that same account. That pairing is now the emotional core, and it is real.

4. **Cut the entire 1:40-1:55 reply-loop ending (G5).** Dana replying "Try Maya Brooks" and the Desk writing it back to the CRM cannot be recorded. `reply_loop` is a print stub and it is commented out of `run_round`. The 15 seconds it used to occupy became beat 6, the safety beat, now 13 seconds, which is entirely true of the run on screen. What could not be cut is the brief's own printed last line, `Reply in this thread and I'll record it.` It is appended in code and it prints every run, so the script frames it out of shot instead. Checklist item 6 covers it.

5. **Cut "in twenty seconds" from the pass-one beat (G8).** Round wall clock with real model calls has never been measured. Section 2 now tells you to measure it yourself and pick a variant from the number. "Seventeen findings" survived the cut because it is measured.

6. **Cut "Draft, not sent. Note, not a stage change." (G1, G2).** Both halves referred to objects that do not exist in this run. Replaced with claims that hold: nothing sent, no stage changed, no calendar touched, cap of three enforced in code.

7. **Cut "show the refusal" (G4).** Carried over from the README and the judge pitch. Nothing in a normal round trips the allowlist, so there is nothing to show. Moved to section 4 as a source-level answer.

8. **Cut the Mail tab from the opening four-tab pan (G7).** Live inbound mail is zero. The opening now pans CRM, Tasks, Calendar and `#ops-team`, all of which are genuinely populated, and the mock is disclosed in the first sentence of beat 3.

### Kept from the earlier draft

The closing tagline, with `doesn't` expanded to `does not` for the read. That expansion is why beat 7 counts 15 words and not 14. "Seventeen findings in, three decisions out", which is verified. The opening problem framing, compressed from 20 seconds to 18. "Facts and dates, never opinions about people." The one-second terminal hold as proof of realness, now assigned specifically to variant B and narrowed to the invocation line alone. The seed check, now a count confirmation rather than a reseed, because mock mode reseeds itself on every run. Mute notifications and say the mock line once. All of those are promoted into the checklist where they cannot be skipped.
