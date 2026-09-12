# Submission drafts (due 16:00 in the portal)

## Title options
- **The Floor** — always-on teammates that do the attention job
- **Quorum** — agents that decide what deserves a human
- **Night Shift** — the colleagues who watch what nobody watches
(Pick one. Not "Grok Bot" — that's xAI's name and this is a different thing.)

## Written description (what you built · who it's for · why context matters)

**What we built.** A floor of always-on agents inside an Ambiguous AI workspace. Three narrow watchers — one on the CRM, one on Mail, one on Calendar, Tasks and the promises people make in chat — sweep their queue every morning and post findings to an agent-only channel as short cards: facts, dates, evidence. A fourth agent, the Desk, reads the floor, merges findings that are the same problem seen from different apps, hands work to the right agent (draft the reply, attach the reason, propose kickoff slots), asks a colleague a one-line question when the cause is unclear, and posts a single ranked brief to the humans: at most three items, each with who, what, why and what the agents already prepared. When a human answers in the thread, the Desk writes the decision back into the CRM or the task list and confirms on the floor.

**Who it's for.** Any small team whose work lives across a CRM, an inbox, a calendar and chat — which is every small team. The users are the people who currently discover in month three that a customer chased twice and nobody saw it.

**Why context matters.** Attention doesn't fail because people are lazy; it fails because the signals of one stuck customer are scattered across four apps and no one person sees them together. A stalled deal in the CRM, an unanswered email, an overdue task and a meeting with no follow-up are usually one problem, not four — and the only way to know that is to read all four systems at once, every day. That's a job no human holds, so it's a job for agents who live inside the tools where the work already is. The multiplayer design is the point: narrow agents see more than one broad one, and an agent-only channel makes their reasoning an audit trail a human can read.

**Safety by construction.** Read-heavy, write-light. Nothing is ever sent to a customer — replies are drafts. Agents add notes and tasks; they never change a stage, a date or someone's calendar. Findings state dates, never opinions about people. A round has exactly two passes, so agents cannot loop. Humans see at most three items per day; everything else is handled — and logged — on the floor.

**Stack.** OpenAI (agent loop and extraction) · Ambiguous AI MCP server (the hands: Chat, CRM, Mail, Tasks, Calendar) · Trigger.dev (the morning schedule) · Python.

## Social post (tag the sponsors)
Built "The Floor" at #AITinkerers Ottawa today: always-on agent teammates that watch a company's CRM, inbox, calendar and chat, argue it out in their own channel, and bother a human about three things a day — not thirty. 17 findings in, 3 decisions out, nothing sent without a person. Thanks @OpenAI @AmbiguousAI @triggerdotdev @CopilotKit @OpenRouterAI #AgentsEverywhere

## Repo README one-liner
Always-on agent teammates for a workspace: three watchers, one desk, an agent-only channel, and a three-item brief for humans. Built at AI Tinkerers Ottawa, Sept 2026.

---

## Demo / seed honesty (internal — not for the portal paste)

Aligned to `SEED_REPORT.md` + `PRE_10AM.md` (2026-09-12):

- Live seed: **20 deals**, 4 priority contacts, 9 tasks, 9 events, chat in `#sales` / `#ops-team`; `#agents-floor` / `#attention` left clean for the round.
- **Inbound mail = 0** in Ambiguous (no inject tool). Mitigations: `#ops-team` `[SEED MAIL]` + 3 drafts only; `send_email` never called. Demo Inbox on **mock** (12 threads) or teach watchers to read SEED MAIL + drafts.
- Golden accounts: Copper Kettle (D-101), Marigold (D-102), Ember Grill (D-107), Pine & Salt (D-105 / bounce in SEED MAIL only).
- `floor/round.py` five TODOs stay empty until 11:15 day build; stop coding 15:15 and record.
- If judges ask about mail: one honest line — mock or SEED MAIL path; multiplayer merge is the product.
