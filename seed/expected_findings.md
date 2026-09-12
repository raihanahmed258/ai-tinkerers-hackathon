# Expected findings — the "golden" answer for testing

Use this to check whether your agents are reading the seed correctly. If a run produces roughly this, the logic works; if it flags the controls, the prompts are too trigger-happy.

## What each watcher should post to #agents-floor (first pass)

**Ops (CRM)** — 6 findings, in roughly this order of confidence:
1. D-101 Copper Kettle — 23 days in Contract, notes say we owe a quote. *Waiting on us.*
2. D-102 Marigold — Closed Won 31 days, no kickoff date, 18 days quiet. *Never started.*
3. D-105 Pine & Salt — 12 days quiet on a $120K Discovery deal. (Ops alone can't see the bounce — that's Inbox's job; the merge happens at the Desk.)
4. D-104 Harbor Fish — close date 92 days in the past, still open. *Zombie date.*
5. D-112 Northgate — 27 days quiet in Discovery, notes say waiting on their ops director. *Unclear whose move.*
6. D-116 Fig & Thistle — implementation quiet 30 days, notes say customer hasn't sent roster. *Waiting on customer, known reason.*
Borderline / low-confidence at most: D-118 Prairie Table (11 days quiet, late stage), D-103 Sunset Taco (35 days quiet — but see M-6).
**Must NOT flag:** D-106 Bluebird, D-108 Juniper, D-110 Saffron, D-111 Dockside, D-114 Meridian, D-117 Cobalt, D-119 Wren, D-115 Gold Leaf (1-day slip), D-113 (closed lost), D-107/D-120 (live customers, quiet is fine).

**Inbox (Mail)** — 5 findings:
1. M-3 Ember Grill — compliance question unanswered 4 days, penalty deadline. *Urgent, existing customer.*
2. M-1 Copper Kettle — unanswered 9 days, chased twice, board deadline. *We owe them.*
3. M-2 Marigold — unanswered 6 days, contract ends Oct 31. *We owe them.*
4. M-4 Pine & Salt — champion's address bounced: "no longer with the company." *Contact lost.*
5. M-9 Fig & Thistle — customer promised roster "next week" 23 days ago. *Waiting on customer.*
Low: M-11 Harbor Fish — quiet 40 days after a non-answer.
**Must NOT flag:** M-7 (vendor spam), M-8 (HR candidate — not a customer item; route quietly if at all), M-5, M-6, M-10, M-12 (answered).

**Follow-up (Calendar + Tasks + chat promises)** — 6 findings:
1. T-4 — Theo's "confirm all Q3 filings" task 8 days overdue (ties to M-3).
2. T-1 / E-1 / E-7 / #sales — Priya promised the Copper Kettle quote twice (−26, −21); task 19 days overdue; pricing meeting 3 weeks ago with no notes or follow-up.
3. T-2 / E-2 / E-7 / #ops-team — Marcus promised the Marigold kickoff twice (−30, −10); task 23 days overdue; discovery notes record the Oct 31 deadline.
4. E-4 — future "Pine & Salt technical review" is booked with an attendee who has left (needs M-4 from Inbox to know that — Desk merge).
5. T-3 — Harbor Fish close-date update 25 days overdue.
6. E-3 — Ember Grill check-in yesterday, no notes, no follow-up (context for M-3).
Minor: T-8 Northgate chase 2 days overdue.
**Must NOT flag:** T-5, T-6 (done), T-7, T-9 (not due), E-5, E-6, E-8, E-9 (healthy future meetings).

## What the Desk should do (second pass)

**Merge into problems** (this is the whole point — three apps, one problem):
- **P1 · Copper Kettle** = D-101 + M-1 + T-1 + E-1 + E-7 + #sales promises. Cause: *we owe a quote Priya promised twice.* Action: Inbox drafts the reply (apology + quote ETA), Ops attaches reason "waiting on our revised quote" to D-101. Human: @Priya in #agents-floor / #attention — quote is 19 days late and the customer's board meets soon.
- **P2 · Marigold** = D-102 + M-2 + T-2 + E-2 + E-7 + #ops-team promises. Cause: *kickoff never scheduled; hard deadline Oct 31.* Action: Follow-up proposes three kickoff slots, Inbox drafts the reply with them, Ops sets a placeholder kickoff date pending confirmation. Human: @Marcus to confirm a slot.
- **P3 · Ember Grill** = M-3 + T-4 + E-3 + #ops-team. Cause: *filing confirmation never done; customer facing penalties.* Action: NONE automated beyond an acknowledgement draft. **Escalate to Theo — top of the brief.**
- **P4 · Pine & Salt** = D-105 + M-4 + E-4. Cause: *champion left; no other contact known.* Action: cancel/flag E-4; do not draft to the dead address. **Escalate to Dana — needs a human to find a new contact.**
- **P5 · Harbor Fish** = D-104 + T-3 + M-11. Cause: *stale close date, customer non-committal.* Action: Ops asks Priya to update or close; optional light check-in draft. Low.
- **P6 · Fig & Thistle** = D-116 + M-9 + T-5. Cause: *waiting on customer roster, known.* Action: Inbox drafts a friendly third nudge. No escalation.
- **P7 · Northgate** = D-112 + T-8 + #sales. Cause: unclear. Action: one-line question to Priya. No escalation.
- **Sunset Taco** = D-103 + M-6 → *customer-paused until October.* Action: note revisit date on D-103. Not in the brief. (Tests judgment.)

**#attention brief (one post):** three items for humans, ranked —
1. **Theo** — Ember Grill's Q3 state withholding: customer says it didn't go out, penalties after the 15th, your filing-confirmation task is 8 days overdue. Please confirm today.
2. **Dana** — Pine & Salt ($120K): our champion Jordan Reyes has left; we have no other contact and a technical review booked for next week that won't happen. Who do we know there?
3. **Priya** — Copper Kettle ($84K): the revised quote promised on two occasions is 19 days late; the customer has chased twice and mentions a board meeting. Draft reply is ready — approve / decide (agents never send).

Everything else: handled on the floor (drafts prepared, reasons attached, nudges proposed, one question to Priya on Northgate, Marigold slots proposed to Marcus).

## The reply loop (the demo ending)
Human replies in the #attention thread — e.g. Dana: "Try Maya Brooks, their ops director." → Desk records the new contact on D-105, re-points E-4, and posts a one-line confirmation on the floor.

## Counts to sanity-check a run
Findings posted: ~17. Problems after merge: 7 (+1 paused). Human items: 3. Controls flagged: 0.
