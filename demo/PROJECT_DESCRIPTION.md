# The Floor — project description

**Title:** The Floor — always-on teammates that do the attention job  
**Repo:** https://github.com/raihanahmed258/the-floor  
**Event:** AI Tinkerers Ottawa — Agents, Everywhere (Sept 2026)

---

## The problem

Small teams don’t lose customers because nobody cares. They lose them because **one stuck customer is scattered across four tools** — CRM, inbox, calendar, and chat — and **no one’s job is to read all four every day**.

A deal sitting in Contract for three weeks, an email chased twice, an overdue “send the quote” task, and a chat promise from last month are usually **one problem**, not four alerts. Humans notice in month three — after the board meeting, the champion leaves, or the filing deadline passes.

That’s an **attention** problem. Attention is scarce. Most copilots wait for a human to open the right tab. The job that needs doing is the opposite: **watch the workspace and decide what deserves a person**.

---

## How we’re solving it

**The Floor** is a small multiplayer crew of always-on agents inside an Ambiguous AI workspace (Chat, CRM, Mail, Tasks, Calendar). They run a bounded morning round and do the attention job.

### Architecture

1. **Three narrow watchers**, each one slice  
   - **Ops** — CRM (stalled deals, zombie close dates, missing kickoffs)  
   - **Inbox** — Mail (unanswered threads, bounces, deadlines)  
   - **Follow-up** — Calendar, Tasks, and promises in chat  

2. They post short **finding cards** (facts, dates, evidence — never opinions about people) to an **agent-only channel** (`#agents-floor`). That channel is the audit trail.

3. **The Desk** reads the floor, **merges** same-account findings into one problem, then either does the safe work (CRM note, email **draft**, task, one-line question to a teammate) or escalates to a human.

4. Humans get **one ranked brief** in `#attention`: **≤3 items**, each with who / what / why / evidence / what agents already prepared. A reply in that thread is written back into CRM or Tasks and confirmed on the floor.

### Safety by construction

- **Read-heavy, write-light** — notes, drafts, tasks only  
- **Never sends** to a customer; never changes stages or calendars  
- **Closed action set** — anything else is refused and logged (the refusal is part of the product)  
- **Exactly two passes** — no agent loops  
- **≤3 human items** — everything else is handled and logged on the floor  

### Why this shape

Narrow agents beat one broad agent: each sees a slice; the Desk merges so Copper Kettle is **one** problem (deal + mail + task + chat), not four notifications. Human attention stays the scarce resource; agents do the watching.

### Demo world

Fictional **Brightline Payroll** (restaurant payroll software): seeded deals, mail, calendar, tasks, and chat, with a golden answer in `seed/expected_findings.md`. Controls (e.g. healthy deals like Bluebird) must **not** flag — judgment over eagerness.

### Stack

- **Claude (Anthropic)** — watcher + Desk extraction / decisions  
- **Ambiguous AI** — workspace + MCP (Chat, CRM, Mail, Tasks, Calendar)  
- **Python** — round runner (`MockClient` offline / `McpClient` live)  
- **Automations / schedule** — morning run (Ambiguous Automations or Trigger.dev)

Prep (roster, seed, MCP map, mock client) landed before the event. Day build is `floor/round.py`: watchers → Desk merge → actions → brief.

---

## One-liner

Always-on agent teammates for a workspace: three watchers, one desk, an agent-only channel, and a three-item brief for humans — seventeen findings in, three decisions out.

---

## Portal-ready short paste (≈150–200 words)

**The Floor** turns workspace attention into a multiplayer agent job.

**Problem:** One stuck customer usually shows up as four weak signals — a quiet CRM deal, an unanswered email, an overdue task, a forgotten chat promise — and nobody is staffed to reconnect them every morning.

**Solution:** Three narrow watchers (CRM, Mail, Calendar/Tasks/chat) post fact-and-date cards to an agent-only floor. A Desk merges same-account findings into one problem, prepares safe work (notes, drafts, tasks — never sends), and posts a ranked brief with **at most three** human items. Thread replies write back into the CRM or task list.

**Why it matters:** Narrow agents plus Desk merge beat one broad agent; the agent channel is an audit trail; human attention stays scarce by design. Safety is structural: **closed write set**, two-pass rounds, no customer sends.

Built at AI Tinkerers Ottawa (Agents, Everywhere) on Ambiguous AI + Claude, with an offline mock so the multiplayer merge demos even when live adapters are thin.
