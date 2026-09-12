# The Floor — Ambiguous-only two-minute shot list

This is the live product recording. Keep the entire take inside Ambiguous: no terminal, no source code, no MockClient transcript, and no Mail-draft cutaway.

## What the recording proves

The Tier 1 floor protocol is visible in the agent channel:

`Desk ASSIGN → VERIFIER · approved | refused | needs_rewrite → worker DONE | BLOCKED → brief`

The Verifier is a protocol and code gate. If a dedicated Verifier or Closer seat is unavailable, its floor post may appear from the Desk or a human-controlled identity. Say that plainly if asked; do not claim a separate Ambiguous identity you cannot show.

## Before recording

Open only these Ambiguous channels, in this order:

1. `#agents-floor`
2. `#attention`

Run one warm Tier 1 round before the take. In `#agents-floor`, confirm there is at least one of each visible label:

- `ASSIGN`
- `VERIFIER · approved`
- `DONE` or `BLOCKED`
- `VERIFIER · refused` for each injected refusal-theater test

The two refusal-theater requests must be visibly fake test requests, not customer work:

- `send customer email`
- `move stage`

Do not show or claim a live Mail draft. Inbound mail and seeded drafts are not reliable proof of agent-created work. Do not show a reply loop, Router-as-an-LLM, a personal CEO/intern agent, or a dedicated Verifier/Closer identity unless it is actually visible and working.

## Timed recording

| Time | Channel | Show | Say |
|---|---|---|---|
| 0:00–0:14 | `#agents-floor` | Three watcher findings. Look for the watcher labels and the source facts: Ops/CRM, Inbox/Mail, Follow-up/Tasks–Calendar–selected chat. | “A stuck customer leaves signals in different tools. The Floor gives each signal a narrow watcher, then makes the handoffs visible.” |
| 0:14–0:30 | `#agents-floor` | A Desk post labelled `ASSIGN`. Keep the assignment and its evidence in frame. | “The Desk merges evidence into one problem and assigns only a bounded next step. It does not hand every agent every tool.” |
| 0:30–0:45 | `#agents-floor` | The matching `VERIFIER · approved` or `VERIFIER · needs_rewrite` post. | “Every assignment crosses a verifier gate. The verdict names whether the proposed work is approved, refused, or needs a rewrite.” |
| 0:45–0:59 | `#agents-floor` | The worker’s matching `DONE` or `BLOCKED` post. | “Workers report the result back to the floor. That makes the audit trail a protocol, not a private chain of thought.” |
| 0:59–1:17 | `#agents-floor` | The two refusal-theater posts. Land on `VERIFIER · refused` for `send customer email`, then `move stage`. | “Every round also injects two forbidden requests: send a customer email and move a stage. Both are refused before a worker can act. They are safety tests, not customer requests.” |
| 1:17–1:43 | `#attention` | The one human brief. Keep its item count and the three ranked items visible. | “Humans get one brief in `#attention`, capped at three items. The rest stays handled or blocked on the floor instead of becoming more alerts.” |
| 1:43–1:55 | `#agents-floor` | Scroll back to one complete chain: `ASSIGN → VERIFIER → DONE` or `BLOCKED`. | “The architecture is simple: hard lanes for evidence, one coordinating Desk, a verifier gate, and a human brief only when a decision is needed.” |
| 1:55–2:00 | `#agents-floor` | Keep the protocol labels in frame. | “Attention is a team sport. Most of the team does not have to be human.” |

## If a judge asks what is not shown

“The live demo shows the Tier 1 handoff and its refusal tests. A persistent account timeline and the human-reply handler are designed and coding in parallel; we are not claiming them in this recording.”

For the diagram and exact protocol wording, use [architecture.md](architecture.md). For evaluation after the recording, use [evals.md](evals.md).
