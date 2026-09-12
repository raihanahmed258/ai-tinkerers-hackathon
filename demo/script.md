# Two-minute demo — one take, screen recording, your voice

**Setup before recording:** workspace open with four tabs ready — `#agents-floor` (clean), `#attention`, CRM (Copper Kettle / D-101 visible), and either **mock Mail** with the Copper Kettle thread **or** live `#ops-team` with the `[SEED MAIL]` summary + the three drafts (Copper Kettle / Marigold / Ember Grill). Terminal on the side. Seed loaded fresh. Round not yet run. `floor/round.py` is day-of only — do not record until those TODOs are filled (build after 11:15; stop coding 15:15, then record).

---

**0:00 – 0:20 · The problem**
*Show the CRM and Mail (or SEED MAIL) tabs, quiet.*
"This is Brightline, a payroll company. Twenty deals, a dozen customer threads, a calendar, a task list. Somewhere in here a customer has chased us twice for a quote we promised three weeks ago, another one is asking whether their tax filing went out, and a $120K prospect's champion just left the company. Nobody knows, because nobody's job is to look at all of it. That's not a people problem. It's an attention problem."

**0:20 – 0:30 · The idea**
*Cut to #agents-floor, empty.*
"So we gave the company a floor of agents. Each one watches one thing. They talk to each other here. And only one of them is allowed to talk to humans."

**0:30 – 0:55 · Pass 1**
*Run the round. Cards appear.*
"Ops watches the CRM. Inbox watches mail. Follow-up watches the calendar, the task list, and the promises people make in chat. In twenty seconds they've posted seventeen findings — each one facts and dates, no opinions."
*Point at two cards for the same account.*
"Notice these three: a stalled deal, an unanswered email, an overdue task. Different apps. Same customer."

**0:55 – 1:20 · Pass 2 — the multiplayer moment**
*Desk replies appear in threads; @mentions.*
"Now the Desk reads the floor. It merges those three into one problem — Copper Kettle is waiting on a quote we promised twice — and hands out the work: Inbox, draft the reply. Ops, attach the reason to the record."
*Cut to Mail/drafts: draft appears. Cut to CRM: note appears.*
"Draft, not sent. Note, not a stage change. Everything customer-facing waits for a person."

**1:20 – 1:40 · The brief**
*Cut to #attention.*
"Then one post to the humans. Three things. Ranked. Theo — a customer's tax filing, penalties after the 15th. Dana — a champion left, we have no contact. Priya — the quote, 19 days late, draft ready. Everything else was handled on the floor. Seventeen findings in, three decisions out."

**1:40 – 1:55 · The loop closes**
*Type a reply as Dana in the thread: "Try Maya Brooks, their ops director." Desk confirms; CRM updates.*
"Dana answers in the thread. The Desk records it on the deal and re-points next week's meeting. Nobody opened the CRM."

**1:55 – 2:00 · Tagline**
*Back to #agents-floor.*
"Attention is a team sport. Most of the team doesn't have to be human."

---

## Honest demo notes (from SEED_REPORT / PRE_10AM)

- **Inbound mail cannot be seeded in Ambiguous** — live `list_inbox` is empty. Prefer the **mock** for Inbox (12 threads), or point judges at `#ops-team` `[SEED MAIL]` + the three **drafts only**. Never call `send_email`.
- Priority stories that must land: Copper Kettle (D-101), Marigold (D-102), Ember Grill (D-107), Pine & Salt (D-105 / M-4 bounce in SEED MAIL — no inbound message).
- `#agents-floor` and `#attention` stay clean until the round runs; seed chat lives in `#sales` / `#ops-team`.
- If live MCP is thin on mail, say it once: "We're on MockClient for Inbox; multiplayer merge is real." Working beats wired.

## Recording tips
- Run the round once *before* recording so the model responses are warm and you know the cards look right; then reseed and record.
- Keep the terminal visible for one second when you trigger the round — judges like seeing it's real.
- If a watcher misfires on a control (flags Bluebird), fix the prompt, don't explain it in the video.
- Record at 1080p, mute notifications, one take is fine; two is plenty.
- Hard stop coding **15:15**, then record — do not keep polishing watchers into the take window.
