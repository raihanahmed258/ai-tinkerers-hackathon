# The Floor — project description

## The problem

One stuck customer becomes scattered evidence: a CRM record, a Mail thread, a calendar event, an overdue task, and a promise in chat. No person owns the daily job of reconnecting those signals, so teams get four alerts or none at all.

## The Tier 1 solution

The Floor gives each source a hard watcher lane: Ops reads CRM only, Inbox reads Mail only, and Follow-up reads Tasks, Calendar, and selected chat only. Their fact-and-evidence findings land in `#agents-floor`, where the Desk merges them into one bounded assignment.

The visible protocol is:

`ASSIGN → VERIFIER · approved | refused | needs_rewrite → DONE | BLOCKED`

The Verifier is a code gate and visible audit boundary. It does not require a dedicated Ambiguous agent seat; without one, its verdict posts through the Desk token and fails closed if Desk is unavailable. A refused request never reaches a worker.

Humans receive one `#attention` brief with at most three items. The system does not send customer messages, move stages, or move close dates.

## Live proof and honest boundaries

The two-minute demo stays inside Ambiguous and shows the watcher lanes, Desk assignments, Verifier verdicts, worker receipts, two injected refusal tests, and the human brief. The injected tests are fake `send customer email` and `move stage` requests; both must be refused before any worker acts.

The demo does not claim a Mail draft when inbound Mail or seed data cannot prove one was created by the current round. A persistent account timeline and a human-reply handler are designed and coding in parallel, not shown as working Tier 1 behavior.

See [script.md](script.md) for the shot list and [architecture.md](architecture.md) for the protocol diagram.
