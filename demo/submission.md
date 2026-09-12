# The Floor: portal submission (paste-ready)

Event: AI Tinkerers Ottawa, theme Agents Everywhere, Saturday 2026-09-12
Repo: https://github.com/raihanahmed258/ai-tinkerers-hackathon
Submit by 16:00. Every claim below agrees with [claim_sheet.md](claim_sheet.md).

---

## 1. Title (decided)

**The Floor: agent teammates that protect human attention**

---

## 2. Description

The Floor is a small crew of agents that does the attention job for a company workspace. One stuck customer leaves evidence in four places: a quiet CRM deal, an unanswered mail thread, an overdue task, a meeting with no notes. No person owns reading all four every morning. The Floor does.

Three watchers each read one hard lane. Ops reads CRM only. Inbox reads Mail only. Follow-up reads Tasks, Calendar and two chat channels only. The lanes are code, not a routing agent, and a lane that leaks a key raises an error. Each watcher posts short finding cards to an agent-only channel, `#agents-floor`. A card is a fact, a date and an id.

A fourth agent, the Desk, reads the whole floor and merges same-account cards into ranked problem cards. Then the Tier 1 protocol runs in the open. The Desk posts `ASSIGN`. A code gate posts `VERIFIER · approved`, `refused` or `needs_rewrite`. The worker posts `DONE` or `BLOCKED`. Nothing writes until the floor shows approved. In demo mode, two synthetic unsafe asks—send customer mail and move a deal stage—are refused in public.

The client has no send method and no calendar write. Stage and close-date changes are refused at every layer. Humans get one brief in `#attention` with at most three items, each naming an owner and its evidence ids.

On the offline mock, one round posts 20 findings, 5 problem cards and 2 refusals, writes 7 CRM notes, 5 drafts and 6 tasks, and asks one question, in 94 floor posts plus one brief. No healthy control account is flagged.

Two limits, stated plainly. The live inbox is empty, so the Inbox lane has nothing to read live and its drafts end `BLOCKED`. The top three brief slots and their owners are a hand-written playbook prior, not model ranking.

Optional but not demonstrated: a human reply handler and a per-account timeline, both off by default.

---

## 3. Short description

The Floor is four narrow agents doing the attention job for a company workspace. Ops reads CRM only, Inbox reads Mail only, Follow-up reads Tasks, Calendar and two chat channels only. The lanes are code. Each watcher posts fact-and-id finding cards to an agent-only channel. The Desk merges same-account cards into ranked problems, then runs a visible protocol: `ASSIGN`, a code-gate `VERIFIER` verdict, and a worker `DONE` or `BLOCKED`. Demo mode also shows two fake unsafe asks being refused.

On the offline mock, one round posts 20 findings, 5 problem cards and 2 refusals, writes 7 notes, 5 drafts and 6 tasks, and gives humans one brief with at most 3 items. Zero healthy controls flagged. Nothing is sent to a customer, no stage moves, no calendar is touched; the client cannot do those things.

Limits: the live inbox is empty, so Inbox drafts end `BLOCKED` live, and the brief order is a playbook prior. The reply handler and account timeline are opt-in and not demonstrated.

---

## 4. Stack

Claude Sonnet 5, model `claude-sonnet-5`, via the Anthropic API, for watcher
and Desk extraction. Ambiguous AI workspace and its MCP server, Streamable
HTTP, as the hands for Chat, CRM, Mail, Tasks and Calendar. Python round runner
with `MockClient` offline and `McpClient` live. A morning schedule on Ambiguous
Automations or Trigger.dev is designed, not running; today a round is started
by hand.

## 5. Demo world

Brightline Payroll is invented, along with every person and customer in it. The seed is 20 deals, 12 mail threads, 9 tasks, 9 calendar events, 26 chat messages and 4 channels. The golden answer lives in `seed/expected_findings.md`, including the healthy control accounts that must never be flagged.

---

## 6. Social post

Built The Floor at AI Tinkerers Ottawa today. Three narrow agents watch a
company's CRM, inbox, tasks and calendar, a Desk merges what they find, and every
action crosses a visible verifier gate on an agent-only channel before a human
sees a brief capped at three items. Nothing is ever sent to a customer. The
hands are the Ambiguous MCP. Thanks @AnthropicAI @AmbiguousAI
#AITinkerers #AgentsEverywhere

**Builder, confirm before posting:** only Anthropic and Ambiguous are tagged, because Claude and the Ambiguous MCP are in the build. Check both handles against the event's own sponsor list before you post. Do not add any other sponsor handle unless you can see it on that list with your own eyes. Do not guess a handle.

---

## 7. Repo one-liner

The Floor: agent teammates that protect human attention. Three narrow watchers,
one Desk that merges and assigns, a verifier gate every action must cross, and a
human brief capped at three items. Built at AI Tinkerers Ottawa, September 2026.

---

## 8. Next, not claimed

- **Reply handler.** `floor/reply_handler.py` is real code with `SAFE_FIELDS` and `BLOCKED_FIELDS` allowlists, wired behind `FLOOR_REPLY_LOOP=1`, off by default, not demonstrated.
- **Account timeline.** `floor/timeline.py` can downgrade an account escalated in the past three days and waiting on a human. It is opt-in with `--timeline`, stores runtime state outside the seed, and is not shown.
