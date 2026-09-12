# Judge pitch — The Floor

## 30 seconds

Attention fails when the evidence for one stuck customer is scattered across a CRM, inbox, calendar, tasks, and chat. The Floor gives each source a narrow watcher, then has one Desk merge the evidence into a bounded assignment.

The key is the visible protocol: `ASSIGN → VERIFIER → DONE or BLOCKED`. The Verifier is a code gate, not a promise that every workspace has another agent seat. Every round also runs two fake unsafe requests—send a customer email and move a stage—and visibly refuses both. Humans receive one `#attention` brief with at most three decisions.

## Two-minute walkthrough

1. Start in `#agents-floor` with the hard lanes: Ops is CRM only, Inbox is Mail only, and Follow-up is Tasks, Calendar, and selected chat.
2. Show the Desk’s `ASSIGN` message linking a merged problem to a bounded worker action.
3. Show the matching `VERIFIER · approved`, `needs_rewrite`, or `refused` post.
4. Show the worker’s `DONE` or `BLOCKED` receipt.
5. Show both injected refusal-theater tests: `send customer email` and `move stage`, each ending in `VERIFIER · refused`.
6. Move to `#attention` and show the one brief with no more than three human items.
7. Close with: “Attention is a team sport. Most of the team does not have to be human.”

## Honest boundaries

- The live proof is the Ambiguous floor protocol, not a terminal run.
- Do not claim a dedicated Verifier or Closer Ambiguous seat when the code gate posted the verdict.
- Do not show or claim a Mail draft when live inbound mail or seed data cannot prove the draft came from this round.
- The account timeline and reply handler are designed and coding in parallel, not part of the demo claim.
