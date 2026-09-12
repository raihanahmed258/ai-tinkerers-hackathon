# The Floor: Ambiguous-only two-minute shot list

One take. Your voice. Exactly 2:00. Two browser tabs and nothing else: `#agents-floor` and `#attention` in the Ambiguous workspace. The take scrolls through a round that already ran. No terminal, no source, no mock transcript.

Every claim in this file agrees with [claim_sheet.md](claim_sheet.md). If you are unsure whether to say something, check the sheet.

## What the recording proves

The Tier 1 protocol is visible as posts in `#agents-floor`: Desk `ASSIGN`, then `VERIFIER · approved | refused | needs_rewrite`, then worker `DONE | BLOCKED`, then one brief in `#attention` with at most three items. The Verifier is a code gate in `floor/round.py` `_verify_action`. Its verdict posts as Desk once `AMBIGUOUS_TOKEN_DESK` is set, which is pre-roll item 2. Without that token the round fails closed. There is no Verifier seat and no Closer seat in the workspace. Say that plainly if asked.

## Pre-roll checklist, in this order

Work top to bottom. Items 1 and 2 are blockers. Do not start recording with either unresolved.

### 1. ANTHROPIC_API_KEY loaded

There is no `.env` on this machine as of this writing. Create `/Users/raihanahmed/Desktop/the-floor/.env` with `ANTHROPIC_API_KEY=` and your key, then confirm it loads the same way `floor/round.py` loads it:

```bash
cd /Users/raihanahmed/Desktop/the-floor && .venv/bin/python -c "import os,dotenv; dotenv.load_dotenv('.env'); print('key loaded:', bool(os.environ.get('ANTHROPIC_API_KEY')))"
```

You want `key loaded: True`. Without the key the code silently falls back to heuristic rules and the brief is wrong: Ember Grill for @theo vanishes and item 3 renders as a bare `T-1` assigned to @dana. There is no error. The eval scores that run AMBER. Do not `cat .env` or echo the key while recording.

### 2. AMBIGUOUS_TOKEN_DESK exported

Put `AMBIGUOUS_TOKEN_DESK=` and the Desk agent token in the same `.env`, or export it in the shell that runs the round. Confirm:

```bash
cd /Users/raihanahmed/Desktop/the-floor && .venv/bin/python -c "import os,dotenv; dotenv.load_dotenv('.env'); print('desk token:', bool(os.environ.get('AMBIGUOUS_TOKEN_DESK')))"
```

You want `desk token: True`. Without it, `python -m floor.round --live` posts the watcher findings and then raises `PermissionError` at the first VERIFIER post inside refusal theater. The round stops there, the floor is left half posted, and the recording dies. This is by design: `McpClient.as_agent("verifier")` in `floor/client.py` refuses to fall back to the default token. The `--live` entry point only reads `AMBIGUOUS_API_KEY` or `AMBIGUOUS_TOKEN`, so the Desk token must be set separately. "VERIFIER posts as Desk" is only true after this step.

Simulated offline against a live-shaped client: without the token the last thing on the floor is one `ASSIGN · Inbox → send email to customer`, then nothing. The system announces an unsafe request and goes silent. There is no flag to run pass 2 alone, so the recovery is to set the token and re-run the whole round, which posts a second `—— Round … · pass 1 ——` block above the good one. Scroll to the second header for the take.

Authorship: with only the Desk token, every post on the floor, watcher cards included, is signed by the Desk seat. Cards appear under their own seats only if `AMBIGUOUS_TOKEN_OPS`, `AMBIGUOUS_TOKEN_INBOX` and `AMBIGUOUS_TOKEN_FOLLOWUP` are also set. Decide before the warm round which of the two you are showing, and do not say "each watcher posts its own card" unless the seat names are on screen.

### 2b. Enable only the recording behavior

Run the recording round with `--safety-demo` so the two synthetic refusal chains are visible. Leave `--timeline` and `FLOOR_REPLY_LOOP` off; neither optional behavior is part of this take. Use `--no-model` for rehearsals that must not spend Anthropic credits, but not when claiming a model-backed take.

### 3. Warm live round before the take, labels confirmed

Run one live round from the shell with both items above in place. Then open `#agents-floor`, find the newest `—— Round … · pass 1 ——` header, and confirm each of these labels is present below it:

- `FINDING · Follow-up`
- `FINDING · Ops`, if present. The live CRM has no stage-entered date, and on the fallback path every Ops rule needs one, so the Ops block can be empty live. With the model key Claude may still flag from notes and titles. Read what is there; do not assume.
- `PROBLEM · … · rank 1`. On the fallback path a card whose finding had no account name is titled by its raw deal id, a UUID. If you see one, choose a beat 2 card with an account name.
- `—— Refusal theater · unsafe asks (must not execute) ——`
- `ASSIGN · Inbox → send email to customer`, then `VERIFIER · refused`, then `BLOCKED · Inbox · send email to customer`
- `ASSIGN · Ops → set_field`, then `VERIFIER · refused`, then `BLOCKED · Ops · set_field`
- At least one approved chain. Live-shaped, that is `ASSIGN · Follow-up → assign task`, then `VERIFIER · approved`, then `DONE · Follow-up · assign_task`. An `add_note` chain appears only if an Ops finding did.
- `—— Work done this round ——`

Then open `#attention` and confirm one post headed `Attention brief` with `item(s) need a person` and three or fewer items, item 1 reading `@theo — Ember Grill`. If item 1 is anything else, go back to item 1 of this checklist.

The take scrolls through this round. If any label is missing, fix and rerun before recording. Do not record a round you have not read.

### 4. The honest Inbox expectation

The live inbox is empty. Ambiguous has no tool to inject inbound customer mail. Expect the `FINDING · Inbox` block to be empty or absent, and expect every `ASSIGN · Inbox → draft reply` chain to end in `BLOCKED · Inbox · draft` with a reason beginning `could not resolve mail id for ref=`, not `DONE · Inbox · draft`. That is fail-closed behaviour and it is fine on camera.

If a judge asks, or if you need to say it on the take, say exactly this and move on:

> "The live inbox is empty, so the Inbox lane has nothing to read today. Every Inbox draft stops at BLOCKED instead of guessing. That is the gate working."

Do not say Inbox posted findings unless you can see a `FINDING · Inbox` card on screen. The three drafts in Mail were placed during seeding and are not agent output. Do not open Mail.

### 5. Mute and window hygiene

macOS Do Not Disturb on. Quit Mail, Slack and Messages. Phone silent and face down. One browser window, two tabs, `#agents-floor` first, `#attention` second, zoom set so one full card fits without wrapping. Close every other tab. Capture at 1080p. Hard stop coding at 15:15 and record.

## Do not show

- The `Ready:` line in the brief. It prints planned actions, not executed ones. A draft that BLOCKed still reads `Ready: draft reply`. Do not read it aloud and do not point at it (H4).
- The reply handler as a working feature. It is off by default and the brief does not print a reply promise while it is off.
- Any seeded Mail draft as agent output (H3).
- A terminal.
- Source code.
- A mock transcript.
- The Router as an LLM. It is code in `floor/router.py`.
- A dedicated Verifier or Closer identity. Neither exists in the workspace.
- The account timeline. It is opt-in with `--timeline`; leave it off and do not demo it.
- Any `PROBLEM` card or brief item whose account reads as a UUID. It is a real live id, not a name, and it reads as a bug on camera (H17).

## Timed shot list

Speaking rate is 2.5 words per second. Each Say cell fits its slot. Word counts are in the table below the shot list.

| Time | Channel | On screen | Say |
|---|---|---|---|
| 0:00–0:17 | `#agents-floor` | The newest `—— Round … · pass 1 ——` header, then slow scroll down through `FINDING · Ops` cards into `FINDING · Follow-up` cards. Rest the cursor on one `ref:` line. If a `FINDING · Inbox` card is there, pass through it; if not, do not pause where it would be. | "This is Brightline Payroll. One stuck customer leaves signals in different tools. Three watchers, each with one lane: Ops reads the CRM, Inbox reads mail, Follow-up reads tasks and calendar. The cards on screen are facts and ids." |
| 0:17–0:33 | `#agents-floor` | The `—— Round … · pass 2 · Desk merge ——` header and the first two `PROBLEM · … · rank` cards. Rest the cursor on a `merges:` line. | "Pass two. The Desk reads the whole floor and merges same-account cards into one ranked problem. Each problem card carries its evidence ids, so you can trace the merge back to the cards above it." |
| 0:33–0:52 | `#agents-floor` | The `—— Refusal theater ——` header. Land on `ASSIGN · Inbox → send email to customer`, then `VERIFIER · refused`, then `BLOCKED · Inbox`. Then `ASSIGN · Ops → set_field`, `VERIFIER · refused`, `BLOCKED · Ops`. | "Before any worker acts, the Desk posts two deliberately unsafe asks. Send an email to a customer. Move a deal's stage. The verifier gate refuses both, and both end BLOCKED. These are safety tests, not customer work. The round runs them every time." |
| 0:52–1:10 | `#agents-floor` | One complete approved chain: `ASSIGN · Ops → add note`, `VERIFIER · approved`, `DONE · Ops · add_note`. Keep all three posts in frame together. | "Now the real work. Every assignment is one bounded step. The Desk posts ASSIGN. The gate posts its verdict: approved, refused, or needs rewrite. The worker posts DONE or BLOCKED. Nothing writes until the floor shows approved." |
| 1:10–1:27 | `#agents-floor` | Slow scroll through the remaining chains toward `—— Work done this round ——`. If a `BLOCKED · Inbox · draft` post is there, let it pass through frame without stopping. | "Every step is on the floor as a post: the ask, the verdict, the receipt. Anyone can read the audit trail without a terminal. A BLOCKED receipt is not hidden. It means the worker stopped instead of guessing." |
| 1:27–1:50 | `#attention` | Switch tabs. The one brief. Cursor on `item(s) need a person`, then down the owner names and `Evidence:` lines. Skip every `Ready:` line and stop scrolling above the last line of the post. | "Humans get one brief in attention, capped at three items in code. Each item names an owner and the evidence ids behind it. Everything else stayed on the floor, handled or blocked. Nothing was sent to a customer. No stage changed. No calendar was touched. The client cannot do those things." |
| 1:50–2:00 | `#agents-floor` | Switch back. One complete chain `ASSIGN`, `VERIFIER · approved`, `DONE` filling the frame. Stop scrolling before you speak. Let the recording run out after the line. | "Attention is a team sport. Most of the team does not have to be human." |

## Word counts

| Time | Length | Words | Spoken at 2.5 w/s | Slack |
|---|---|---|---|---|
| 0:00–0:17 | 17s | 38 | 15.2s | 1.8s |
| 0:17–0:33 | 16s | 35 | 14.0s | 2.0s |
| 0:33–0:52 | 19s | 43 | 17.2s | 1.8s |
| 0:52–1:10 | 18s | 37 | 14.8s | 3.2s |
| 1:10–1:27 | 17s | 38 | 15.2s | 1.8s |
| 1:27–1:50 | 23s | 51 | 20.4s | 2.6s |
| 1:50–2:00 | 10s | 15 | 6.0s | 4.0s |
| **Total** | **120s** | **257** | **102.8s** | **17.2s** |

Timecodes are contiguous and end at 2:00. The closing line has a 10 second slot; say it, stop, and let the recording run out.

## Why the opener is worded that way

The first Say line names three lanes because the lanes are code and always true. It does not say three watchers posted, because live the Inbox lane may post nothing. If a `FINDING · Inbox` card is on screen, the line is still true. If none is, the line is still true. Do not add "and here are Inbox's cards" unless you can see one.

## If a judge asks what is not shown

"The live recording shows the Tier 1 handoff and its two demo-only refusal tests. The reply handler and account timeline are implemented, opt-in, and not demonstrated."

For the diagram, use [architecture.md](architecture.md). For the long-form answers, use [judge_qa.md](judge_qa.md). For what changed and why, use [honesty_changelog.md](honesty_changelog.md).
