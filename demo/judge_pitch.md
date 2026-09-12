# Judge pitch outlines — The Floor

Source of truth: kit README § Design decisions, `seed/expected_findings.md`, `demo/script.md`.
No Project 1 / Ottawa Mosque talk.

---

## 30-second (elevator)

**Hook:** Attention fails because one stuck customer is scattered across CRM, mail, calendar, and chat — so nobody sees the whole problem.

**What we built:** Three narrow watchers (Ops / Inbox / Follow-up) each own one slice. They post facts-and-dates cards to an agent-only floor. The Desk merges the same customer into one problem, does the safe work (drafts, notes, tasks), and escalates at most **three** items to humans.

**Why it wins:** Narrow agents + Desk merge beat one broad agent. Human attention is the scarce resource. Writes are a **closed set** — drafts never send, no stage/calendar changes — and we can show the refusal. If live MCP is thin, we demo on MockClient and say so: working beats wired.

**Close:** Seventeen findings in, three decisions out. Attention is a team sport; most of the team doesn't have to be human.

---

## 2-minute (judge Q&A / walkthrough talking points)

### 0:00–0:25 · Problem
Brightline (fictional payroll): 20 deals, 12 threads, calendar + tasks. Copper Kettle chased twice for a quote we promised weeks ago; Ember Grill may face filing penalties; Pine & Salt's champion left. Nobody's job is to look at all of it. That's an **attention** problem, not a people problem.

### 0:25–0:45 · Architecture (say the design decisions out loud)
- **Narrow agents beat one broad one** — each sees a slice; merge happens at the Desk. Same customer → one problem, not four alerts.
- **Agent channel = audit trail** — every decision is a readable message.
- **Human attention is scarce** — max three items in `#attention`; everything else handled and logged on the floor.
- **Two passes, no loops** — bounded by construction.
- **Read-heavy, write-light** — notes, drafts, tasks only; closed action set refuses send / stage / calendar. Show the refusal if asked.
- **Facts and dates, never opinions about people** — the never-list in `agents.yaml`.

### 0:45–1:20 · The golden story (from expected_findings)
Point at the merge, not the model:
1. **Copper Kettle (P1)** — deal + unanswered mail + overdue task + chat promises → we owe a quote; draft ready; @Priya.
2. **Ember Grill (P3)** — compliance mail + overdue filing task → **top of brief @Theo** (penalties).
3. **Pine & Salt (P4)** — quiet deal + bounce ("no longer with company") + meeting with departed attendee → **@Dana** find a new contact; do not draft to the dead address.

Controls matter: Bluebird and friends must **not** flag — judgment, not eagerness.

### 1:20–1:45 · Safety + honesty
Closed write set: draft ≠ send. Reply loop: human answers in thread → Desk writes back to CRM → confirms on floor.  
**Mock-vs-live:** If Ambiguous MCP gaps (e.g. inbound mail quirks), run the demo on MockClient with the terminal as the floor — fully honest: "adapter is the next hour; multiplayer merge is real today."

### 1:45–2:00 · Tagline
"Attention is a team sport. Most of the team doesn't have to be human."  
Point judges at `seed/expected_findings.md` and README design decisions if they want the receipts.

---

## Pocket answers (if judges poke)

| Question | Answer |
|---|---|
| Why not one mega-agent? | Slice visibility + Desk merge; one broad agent either floods or misses cross-app links. |
| What can it write? | Notes, drafts, tasks only. Never sends, never changes stages/calendars. Refusal is intentional. |
| Why ≤3? | Scarce human attention; rest is handled on the floor with an audit trail. |
| How do you know it's right? | Golden answer in expected_findings; controls (Bluebird etc.) catch over-eager prompts. |
| Live workspace broken? | MockClient demo is valid; say the adapter is next. Working beats wired. |
