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
| 0:00–0:17 | `#agents-floor` | The `—— Round 2026-09-12 15:22 · pass 1 ——` header, then move through one `FINDING · Ops` and one `FINDING · Follow-up` card. Rest on a `ref:` line. | "A customer problem rarely lives in one place. The email is in one app, the overdue task in another, and the promise is buried in chat. The Floor gives each source a watcher and brings the evidence together here in Ambiguous." |
| 0:17–0:33 | `#agents-floor` | The `—— Round … · pass 2 · Desk merge ——` header and the first two `PROBLEM · … · rank` cards. Rest the cursor on a `merges:` line. | "Then the Desk connects the dots. Instead of giving the team five separate alerts, it merges evidence about the same customer into one ranked problem. The original IDs stay attached, so anyone can check the reasoning." |
| 0:33–0:52 | `#agents-floor` | The `—— Refusal theater ——` header. Land on `ASSIGN · Inbox → send email to customer`, then `VERIFIER · refused`, then `BLOCKED · Inbox`. Then `ASSIGN · Ops → set_field`, `VERIFIER · refused`, `BLOCKED · Ops`. | "Before anything happens, every action crosses a hard safety gate. Here I deliberately ask it to email a customer and change a deal stage. Both requests are refused and logged as blocked. The model cannot talk its way around the rule." |
| 0:52–1:10 | `#agents-floor` | Scroll through one complete approved task chain in order: `ASSIGN · Follow-up → assign task`, `VERIFIER · approved`, `DONE · Follow-up · assign_task`. Pause briefly on each label; they need not fit together. | "Safe work follows the same path. The Desk assigns one small action, the gate approves it, and the worker reports what happened. If execution fails, it says blocked instead of pretending the job is done." |
| 1:10–1:27 | `#agents-floor` | Slow scroll through the remaining chains toward `—— Work done this round ——`. If a `BLOCKED · Inbox · draft` post is there, let it pass through frame without stopping. | "This channel is the audit trail. You can see the request, the decision, and the receipt in order. The agents handle routine follow-up here, while only decisions that genuinely need a person move to attention." |
| 1:27–1:50 | `#attention` | Show the newest clean brief. Move through the three owner lines and their evidence, then stop on `Handled without you`. | "And this is what the human sees: not another dashboard, just today's three decisions. Theo handles Ember Grill's filing risk, Dana finds Pine and Salt's new contact, and Priya closes the loop on Copper Kettle's quote. Every item carries its evidence." |
| 1:50–2:00 | `#agents-floor` | Switch back to the saved floor position showing a `VERIFIER · approved` immediately followed by `DONE`. Stop scrolling before you speak. Let the recording run out after the line. | "The goal isn't more notifications. It's giving people back their attention." |

## Word counts

| Time | Length | Words | Spoken at 2.5 w/s | Slack |
|---|---|---|---|---|
| 0:00–0:17 | 17s | 41 | 16.4s | 0.6s |
| 0:17–0:33 | 16s | 36 | 14.4s | 1.6s |
| 0:33–0:52 | 19s | 41 | 16.4s | 2.6s |
| 0:52–1:10 | 18s | 35 | 14.0s | 4.0s |
| 1:10–1:27 | 17s | 35 | 14.0s | 3.0s |
| 1:27–1:50 | 23s | 41 | 16.4s | 6.6s |
| 1:50–2:00 | 10s | 11 | 4.4s | 5.6s |
| **Total** | **120s** | **240** | **96.0s** | **24.0s** |

Timecodes are contiguous and end at 2:00. The closing line has a 10 second slot; say it, stop, and let the recording run out.

## Why the opener is worded that way

The first Say line names three lanes because the lanes are code and always true. It does not say three watchers posted, because live the Inbox lane may post nothing. If a `FINDING · Inbox` card is on screen, the line is still true. If none is, the line is still true. Do not add "and here are Inbox's cards" unless you can see one.

## If a judge asks what is not shown

"The live recording shows the Tier 1 handoff and its two demo-only refusal tests. The reply handler and account timeline are implemented, opt-in, and not demonstrated."

For the diagram, use [architecture.md](architecture.md). For the long-form answers, use [judge_qa.md](judge_qa.md). For what changed and why, use [honesty_changelog.md](honesty_changelog.md).
