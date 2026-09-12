# The Floor: Ambiguous-only two-minute shot list

One take. Your voice. Exactly 2:00. Two browser tabs and nothing else: `#agents-floor` and `#attention` in the Ambiguous workspace. The take scrolls through a round that already ran. No terminal, no source, no mock transcript.

Every claim in this file agrees with [claim_sheet.md](claim_sheet.md). If you are unsure whether to say something, check the sheet.

## What the recording proves

The Tier 1 protocol is visible as posts in `#agents-floor`: Desk `ASSIGN`, then
`VERIFIER · approved | refused`, then worker `DONE | BLOCKED`, followed by a
clean three-item brief in `#attention`. The Verifier is a code gate whose
verdict appears from Desk. There is no Verifier or Closer seat.

## Pre-roll checklist, in this order

Do not run another round. Open `#agents-floor` and find:

`—— Round 2026-09-12 15:22 · pass 1 ——`

Confirm these labels below it:

- 7 `FINDING · Ops` and 8 `FINDING · Follow-up` cards; Inbox is empty
- `PROBLEM · … · rank 1`. On the fallback path a card whose finding had no account name is titled by its raw deal id, a UUID. If you see one, choose a beat 2 card with an account name.
- `—— Refusal theater · unsafe asks (must not execute) ——`
- `ASSIGN · Inbox → send email to customer`, then `VERIFIER · refused`, then `BLOCKED · Inbox · send email to customer`
- `ASSIGN · Ops → set_field`, then `VERIFIER · refused`, then `BLOCKED · Ops · set_field`
- At least one approved chain. Live-shaped, that is `ASSIGN · Follow-up → assign task`, then `VERIFIER · approved`, then `DONE · Follow-up · assign_task`. An `add_note` chain appears only if an Ops finding did.
- `—— Work done this round ——`

Then open `#attention` and find the newest brief, message
`d9aff913-9c63-48bf-895b-9ccc6021cd04`. It contains Ember Grill, Pine & Salt,
and Copper Kettle Group, with no stale `Ready:` or reply-promise lines.

The take scrolls through this existing round. Do not rerun or edit it.
`LIVE_ROUND_REPORT.md` is the evidence index.

### The honest Inbox expectation

The live inbox is empty. Ambiguous has no tool to inject inbound customer mail. Expect the `FINDING · Inbox` block to be empty or absent, and expect every `ASSIGN · Inbox → draft reply` chain to end in `BLOCKED · Inbox · draft` with a reason beginning `could not resolve mail id for ref=`, not `DONE · Inbox · draft`. That is fail-closed behaviour and it is fine on camera.

If a judge asks, or if you need to say it on the take, say exactly this and move on:

> "The live inbox is empty, so the Inbox lane has nothing to read today. Every Inbox draft stops at BLOCKED instead of guessing. That is the gate working."

Do not say Inbox posted findings unless you can see a `FINDING · Inbox` card on screen. The three drafts in Mail were placed during seeding and are not agent output. Do not open Mail.

### 5. Mute and window hygiene

macOS Do Not Disturb on. Quit Mail, Slack and Messages. Phone silent and face down. One browser window, two tabs, `#agents-floor` first, `#attention` second, zoom set so one full card fits without wrapping. Close every other tab. Capture at 1080p. Hard stop coding at 15:15 and record.

## Do not show

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
| 0:00–0:17 | `#agents-floor` | The `—— Round 2026-09-12 15:22 · pass 1 ——` header, then move through one `FINDING · Ops` and one `FINDING · Follow-up` card. Rest on a `ref:` line. | "This is Brightline Payroll. One stuck customer can leave signals in different tools. Three lanes inspect separate slices: Ops reads CRM, Inbox reads mail, and Follow-up reads tasks, calendar, and selected chat. This live round found evidence across two lanes." |
| 0:17–0:33 | `#agents-floor` | The `—— Round … · pass 2 · Desk merge ——` header and the first two `PROBLEM · … · rank` cards. Rest the cursor on a `merges:` line. | "Pass two. The Desk reads the whole floor and merges same-account cards into one ranked problem. Each problem card carries its evidence ids, so you can trace the merge back to the cards above it." |
| 0:33–0:52 | `#agents-floor` | The `—— Refusal theater ——` header. Land on `ASSIGN · Inbox → send email to customer`, then `VERIFIER · refused`, then `BLOCKED · Inbox`. Then `ASSIGN · Ops → set_field`, `VERIFIER · refused`, `BLOCKED · Ops`. | "In this safety demo, the Desk posts two deliberately unsafe asks. Send an email to a customer. Move a deal's stage. The verifier gate refuses both, and both end BLOCKED. These are synthetic tests, not customer work." |
| 0:52–1:10 | `#agents-floor` | Scroll through one complete approved task chain in order: `ASSIGN · Follow-up → assign task`, `VERIFIER · approved`, `DONE · Follow-up · assign_task`. Pause briefly on each label; they need not fit together. | "Now the real work. Every assignment is one bounded step. The Desk posts ASSIGN. The gate posts its verdict: approved or refused. The worker posts DONE or BLOCKED. Nothing writes until the floor shows approved." |
| 1:10–1:27 | `#agents-floor` | Slow scroll through the remaining chains toward `—— Work done this round ——`. If a `BLOCKED · Inbox · draft` post is there, let it pass through frame without stopping. | "Every step is on the floor as a post: the ask, the verdict, the receipt. Anyone can read the audit trail without a terminal. A BLOCKED receipt is not hidden. It means the worker stopped instead of guessing." |
| 1:27–1:50 | `#attention` | Show the newest clean brief. Move through the three owner lines and their evidence, then stop on `Handled without you`. | "Humans get one brief in attention, capped at three items in code. This round routes Ember Grill to Theo, Pine and Salt to Dana, and Copper Kettle to Priya, each with evidence attached. Nothing was sent. No stage changed." |
| 1:50–2:00 | `#agents-floor` | Switch back to the saved floor position showing a `VERIFIER · approved` immediately followed by `DONE`. Stop scrolling before you speak. Let the recording run out after the line. | "Attention is a team sport. Most of the team does not have to be human." |

## Word counts

| Time | Length | Words | Spoken at 2.5 w/s | Slack |
|---|---|---|---|---|
| 0:00–0:17 | 17s | 40 | 16.0s | 1.0s |
| 0:17–0:33 | 16s | 35 | 14.0s | 2.0s |
| 0:33–0:52 | 19s | 37 | 14.8s | 4.2s |
| 0:52–1:10 | 18s | 35 | 14.0s | 4.0s |
| 1:10–1:27 | 17s | 38 | 15.2s | 1.8s |
| 1:27–1:50 | 23s | 39 | 15.6s | 7.4s |
| 1:50–2:00 | 10s | 15 | 6.0s | 4.0s |
| **Total** | **120s** | **239** | **95.6s** | **24.4s** |

Timecodes are contiguous and end at 2:00. The closing line has a 10 second slot; say it, stop, and let the recording run out.

## Why the opener is worded that way

The first Say line names three lanes because the lanes are code and always true. It does not say three watchers posted, because live the Inbox lane may post nothing. If a `FINDING · Inbox` card is on screen, the line is still true. If none is, the line is still true. Do not add "and here are Inbox's cards" unless you can see one.

## If a judge asks what is not shown

"The live recording shows the Tier 1 handoff and its two demo-only refusal tests. The reply handler and account timeline are implemented, opt-in, and not demonstrated."

For the diagram, use [architecture.md](architecture.md). For the long-form answers, use [judge_qa.md](judge_qa.md). For what changed and why, use [honesty_changelog.md](honesty_changelog.md).
