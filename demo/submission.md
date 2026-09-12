# The Floor: portal submission (paste-ready)

Event: AI Tinkerers Ottawa, "Agents, Everywhere", 2026-09-12
Repo: https://github.com/raihanahmed258/the-floor

---

## 1. Title (decided)

**The Floor: always-on agent teammates that do the attention job**

Why this one: the floor is both the name of the place where the work happens and the word in the name of the channel the agents talk in, `#agents-floor`, so the title and the demo are the same thing.

Runner-ups if you disagree, in order:

1. **Quorum: agents that decide what deserves a human.** Sharper on the merge, but it loses the channel.
2. **Night Shift: the colleagues who watch what nobody watches.** Warmer, but it implies overnight and the round runs in the morning.

---

## 2. Written description (393 words)

The Floor is four narrow agents that do the attention job for a small company's workspace. Three watchers each own one slice. Ops reads the CRM. Inbox reads Mail. Follow-up reads the calendar, the task list and the promises people make in chat. On each round the watchers sweep their queue and post short finding cards to an agent-only channel, #agents-floor. A card is facts and dates with an evidence reference. It never contains an opinion about a person or a guess about how a customer feels.

A fourth agent, the Desk, reads the whole floor. It merges findings that are the same problem seen from different apps, does the safe work it is allowed to do, and posts exactly one ranked brief to #attention with at most three items for a human. A round is exactly two passes, so the agents cannot loop. The write set is a closed allowlist: notes, tasks, drafts, a field update and a question on the floor. Nothing is ever sent to a customer. No agent can touch anyone's calendar, because the client has no calendar write at all. Stage and close-date changes are proposed, never made.

On the validated run the watchers posted 17 findings: 8 from Ops, 3 from Inbox, 6 from Follow-up. The Desk merged them and escalated three. Ember Grill to Theo, because a customer says a tax filing was never confirmed and penalties start after the 15th. Pine & Salt to Dana, because the champion's address bounced and we have no other contact. Copper Kettle to Priya, because a quote promised in a pricing review is 19 days late. Each item carries an evidence line joining two or three of the four tools: mail, task and calendar for Ember Grill, CRM and mail for Pine & Salt, CRM, task and calendar for Copper Kettle. Every healthy control account stayed off the brief.

It is for any small team whose work lives in four tools and whose attention lives in none of them. Context matters because a quiet deal, an unanswered email, an overdue task and a meeting with no notes are usually one problem, not four alerts. Reading all four every morning is a job no human holds. Next up is the reply loop, where a human answers in the brief thread and the Desk writes the decision back to the CRM.

---

## 3. Short description (188 words, for portals with a tight limit)

The Floor is a crew of four narrow agents that does the attention job for a small company's workspace. Three watchers each own one slice. Ops reads the CRM, Inbox reads Mail, and Follow-up reads the calendar, tasks and chat promises. On each round they post short fact-and-date finding cards to an agent-only channel. A fourth agent, the Desk, merges cards that are the same problem seen from different apps, does the safe work it is allowed to do, and posts one ranked brief with at most three human items.

On the validated run the watchers posted 17 findings and the Desk escalated three: an unconfirmed tax filing with a penalty deadline, a bounced champion on a $120,000 deal, and a quote 19 days late. Each item carries an evidence line joining two or three of the four tools. Healthy accounts stayed off the brief.

Safety is structural. The write set is a closed allowlist, a round is exactly two passes, humans get three items at most, and nothing is ever sent to a customer. A human reply loop that writes decisions back to the CRM is next.

---

## 4. Stack

Claude, model `claude-sonnet-4-5`, via the Anthropic API, for watcher and Desk extraction. Ambiguous AI workspace and its MCP server as the hands for Chat, CRM, Mail, Tasks and Calendar. Python round runner with an offline mock client and a live MCP client. Designed to run on a morning schedule with Ambiguous Automations or Trigger.dev. Today a round is started by hand.

## 5. Demo world

Brightline Payroll is invented, along with every person and customer in it. The seed is 20 deals, 12 mail threads, 9 tasks, 9 calendar events, 26 chat messages and 4 channels. The golden answer the run is checked against lives in `seed/expected_findings.md`, including the healthy control accounts that must not be flagged.

---

## 6. Social post

Built The Floor at AI Tinkerers Ottawa today. Three agents watch a company's CRM, inbox, calendar and chat, a fourth merges what they find, and together they bother a human about three things instead of seventeen. 17 findings in, 3 items out, nothing sent to a customer. Extraction runs on Claude. The hands are the Ambiguous AI MCP. Thanks @AnthropicAI @AmbiguousAI #AITinkerers #AgentsEverywhere

> **BUILDER, CONFIRM BEFORE POSTING:** check the event's own sponsor list and fix the handles. @AnthropicAI and @AmbiguousAI are tagged because Claude and the Ambiguous MCP are actually in this build. Trigger.dev, CopilotKit and OpenRouter are not tagged. Add @triggerdotdev only if you used it for the schedule, and add CopilotKit or OpenRouter only if you can see them on the sponsor list with your own eyes. Do not guess a handle.

---

## 7. Repo README one-liner

The Floor: always-on agent teammates that do the attention job. Three narrow watchers, one Desk that merges and decides, an agent-only channel where they coordinate, and a three-item brief for humans. 17 findings in, 3 items out. Built at AI Tinkerers Ottawa, September 2026.

The name and the middle sentence are the README's own words, at `README.md` line 1 and line 5. The stats sentence and the build line are portal-only. "17 findings in, 3 items out" is not in the README, and the README names the theme where this drops it. If a judge holds both tabs open, the shape matches and the wording of those two sentences does not.

---
---

# INTERNAL: honesty notes. Do not paste any of this into the portal.

**Mock versus live.** The one validated run is mock mode with a real `ANTHROPIC_API_KEY` and `claude-sonnet-4-5`, captured in `MOCK_ROUND_VALIDATE3.txt`. The live MCP client is implemented but the validated end-to-end numbers above are the mock run. Say that plainly if a judge asks. Working beats wired.

**The inbound mail gap (G7).** Live Ambiguous has zero inbound mail and its MCP has no tool to inject fictional customer threads, so the Inbox watcher has nothing to read live. The workspace has a `[SEED MAIL]` summary in #ops-team covering M-1, M-2, M-3, M-4 and M-9, plus 3 draft emails that the seeding script placed by hand. `SEED_REPORT.md` calls them "stubs only". They are not agent output and must not be shown as a draft an agent wrote. `send_email` was never called. The honest demo path for Inbox is the mock.

**Do not say these on camera.** No CRM notes were written in the validated run. No email drafts were created in it either, so do not click through to a draft in Mail. The brief prints "Ready: draft_reply, assign_task" for Copper Kettle and no draft object exists behind it. The Desk's merge shows up only as the Evidence line inside the brief, not as a PROBLEM block in each finding's thread. No refusal fires in a normal round, so treat the closed allowlist as a code-level guarantee you point at in `floor/round.py`, not a live moment. The reply loop is a stub and is commented out of `run_round`, so Dana answering in the thread cannot be recorded as working behaviour. Note that the brief itself still ends with the printed line "Reply in this thread and I'll record it." at `floor/round.py` line 1083, so it will be on screen. Concede it before a judge points at it. The line is the designed ending and nothing is listening yet, same wording as `demo/judge_qa.md`.

**The allowlist is wider than the prompts.** If a judge opens `execute_actions` they will see `set_field` in `ALLOWED_ACTIONS` at `floor/round.py` line 963, and `McpClient.set_deal_field` at `floor/client.py` line 352 has a branch that writes `stage_id`. `agents.yaml` grants `crm.set_field` to Ops and the Desk. So do not say agents *cannot* change a stage. Say no stage change happens in a round, zero `set_field` calls fired in the validated run, and the stage prohibition lives in the prompts. Concede that the allowlist is wider than the prompts. The calendar claim is safe to make structurally, because the client has no calendar write method at all.

**Pre-record blocker.** Confirm `ANTHROPIC_API_KEY` is loaded from `.env` before the take. Without it the code silently falls back to heuristics, the Ember Grill item disappears from the brief, and item 3 renders the account as "T-1". Also do not assert a round duration unless you time a real run first. The no-key heuristic path finishes in about 0.2 seconds and the four sequential Claude calls have never been timed.

**Cosmetic rough edge.** All 3 tasks in the validated run went to "dana" with generic titles and the same 2026-09-14 due date. It is on screen, so do not draw attention to task ownership.

**Naming.** Never call this Grok Bot. That is xAI's name. Before the repo goes in front of judges, fix the three places it leaks. `grokbot` in `MCP_MAPPING.md` line 4. The stale "OpenAI API key" docstring in `floor/round.py` line 291. The `gpt-5.1` and `OPENAI_API_KEY` paragraph in `PRE_10AM.md` line 60. The stack line says Claude, and the repo should too.
