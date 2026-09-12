# The Floor — portal submission

## Title

**The Floor: always-on teammates that protect human attention**

## Description

The Floor is a multi-agent coordination layer for a company workspace. Three narrow watchers collect evidence from hard lanes: Ops sees CRM only, Inbox sees Mail only, and Follow-up sees Tasks, Calendar, and selected chat only. They post structured findings to an agent-only floor, where the Desk merges related signals into one customer-level problem.

Tier 1 is a visible, bounded handoff: the Desk posts an `ASSIGN`, a Verifier gate returns `approved`, `refused`, or `needs_rewrite`, and the assigned worker reports `DONE` or `BLOCKED` on the floor. A Verifier does not need a dedicated workspace seat; when seats are limited, the code gate can post its verdict through the Desk or a human-controlled identity. What matters is the audit boundary: refused work never reaches a worker.

Every round also includes two labelled safety tests—`send customer email` and `move stage`. Both must be refused before any worker acts. The system does not send customer messages, move stages, or move close dates. Humans receive one `#attention` brief with at most three items, so agent activity becomes a short list of real decisions rather than more alerts.

The live demo stays inside Ambiguous and shows the floor protocol, refusal tests, worker receipts, and the human brief. We do not use Mail drafts as proof because inbound mail and seeded drafts cannot reliably establish that a draft was created by the current run. A persistent account timeline and a human-reply handler are designed and coding in parallel; they are not claimed as working in the Tier 1 demo.

## Stack

Ambiguous workspace channels and the project’s orchestration code. The protocol is designed to work with dedicated agent seats when available, while keeping the Verifier boundary in code when they are not.

## One-line version

The Floor turns scattered workspace signals into a visible safety-gated protocol: `ASSIGN → VERIFIER → DONE/BLOCKED`, then a three-item brief for humans.
