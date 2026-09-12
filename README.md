# The Floor — kit for AI Tinkerers Ottawa (Agents, Everywhere)

Always-on agent teammates that do the attention job for a workspace: three narrow watchers, one Desk that merges and decides, an agent-only channel where they coordinate, and a three-item brief for humans.

**What's prep and what's the build.** Everything in this kit is preparation you're allowed to do the night before: the fictional company, the roster, prompt drafts, a mock client so you can develop offline, the demo script and submission text. 

**The day's build:** The actual agent logic in `floor/round.py` — specifically the five core functions that were implemented during the hackathon:
1. `run_watcher` — calls LLM with playbook + data slice, returns FINDING cards (rung 1)
2. `run_desk_merge` — Desk merges findings into PROBLEM blocks (rung 2)
3. `post_brief` — renders and posts the 3-item brief to #attention (rung 2)
4. `execute_actions` — closed allowlist action execution with safety refusal (rung 3)
5. `reply_loop` — human reply processing (rung 4 stub)

Plus the MCP mapping in `floor/client.py` for live workspace integration.

Nothing in here is from any real company. Brightline Payroll, its people and customers are invented.

---

## Layout

```
agents.yaml                  the roster: who watches what, allowed tools, the "never" list, round shape
seed/                        the fictional company (day-offset dates → always fresh)
  company.json               people, channels
  crm_deals.json             20 deals — 6 stalled for different reasons, the rest controls
  mail_threads.json          12 threads — 5 unanswered incl. a bounce, plus spam/HR distractors
  chat_history.json          #sales and #ops-team with promises that were never kept
  calendar_events.json       orphaned customer meetings, a meeting with a departed attendee
  tasks.json                 overdue tasks tied to the same problems
  expected_findings.md       the golden answer: what each watcher should post, what the Desk should merge, the 3 human items
prompts/                     system prompt drafts for Ops, Inbox, Follow-up, Desk + the card/brief format
floor/
  client.py                  WorkspaceClient interface · MockClient (offline, in memory) · McpClient (TODO: map tools)
  seed.py                    loads the seed into any client
  round.py                   THE BUILD — two-pass round, five TODO functions, the rung ladder in the docstring
demo/
  script.md                  the two-minute video, timed
  submission.md              title options, written description, social post, README one-liner
```

## Run the mock right now (no network)

```bash
pip install -r requirements.txt
python3 -m floor.seed          # prints counts: 20 deals, 12 threads, 9 tasks, 9 events, 26 chat messages
python3 -m floor.round         # runs complete mock round with heuristic fallback (no API key needed)
```

**Mock vs Live:**
- **Mock mode (default):** `python3 -m floor.round` — runs entirely offline using `MockClient` with in-memory seed data. All posts, drafts, notes, and tasks print to terminal. Perfect for development and testing.
- **Live mode:** `python3 -m floor.round --live` — connects to your Ambiguous workspace via MCP. Requires `AMBIGUOUS_API_KEY` or `AMBIGUOUS_TOKEN` environment variable.

**API Key behavior:**
- **With OpenAI API key:** Set `OPENAI_API_KEY` environment variable. The system calls GPT to analyze data and generate findings/decisions.
- **Without API key (CI/demo fallback):** The system uses built-in heuristic rules to generate plausible findings. This ensures `python3 -m floor.round` always produces terminal output even without credentials.

`MockClient` prints every action as it happens, so you can watch the entire round unfold with zero credentials. Check output against `seed/expected_findings.md`. If Bluebird (D-106) gets flagged, the logic is too eager — the controls are there to catch exactly that.

---

## Tonight (60–90 minutes, in this order)

1. **Workspace.** In your Ambiguous account create channels `#agents-floor`, `#attention`, `#sales`, `#ops-team`. Invite four agent teammates — Ops, Inbox, Follow-up, Desk. **Check whether agents count toward the five-teammate free tier**; if they do, four agents plus you is exactly five — fine, but don't add a fifth.
2. **Automations app.** Open it and see whether it can run an agent on a schedule or on an event. If it can, it replaces Trigger.dev for the morning run (still mention Trigger.dev if you use it anywhere).
3. **MCP.** Follow the workspace's agent connection guide. From any MCP client, **list the tools** and prove the eight calls in `client.py`: read a channel, post a message, list CRM records, add a note / set a field, list mail threads, create a draft, list tasks / create a task, list calendar events. Write the real tool names next to each method in `McpClient`. This is the step most likely to eat time — do it tonight, not at 11:15.
4. **Seed the workspace.** Once the mapping exists, extend `seed.py`'s live branch to call the create methods and load the company. If MCP is not cooperating by bedtime, seed by hand tomorrow morning: the CSVs are small, and the demo only needs Copper Kettle, Marigold, Ember Grill and Pine & Salt to be perfect.
5. **Model access.** Starter credits and repo come from the organisers before the event — confirm the model name and put it in `agents.yaml › defaults.model`.
6. **Budget.** Free tier is 1,000 AI actions/month. A full round is roughly 20–40 actions. Test on the mock; hit the live workspace only for end-to-end checks and the recording.
7. **Sleep.** Seriously. Four hours of building on no sleep loses to three hours on eight.

## The day (11:15–15:30)

| Time | Rung | Done when |
|---|---|---|
| 11:15–12:00 | 1 · Ops pass 1 | `run_watcher` works on the mock for Ops; cards match expected_findings; then live: cards land in #agents-floor |
| 12:00–12:45 | 2 · Desk + brief | `run_desk_merge` + `post_brief`; one brief in #attention with ≤3 items — **you are now submittable** |
| 12:45–14:00 | 3 · Inbox, Follow-up, actions | all three watchers; merges visible in-thread; `execute_actions` writes a CRM note, a draft, a task |
| 14:00–14:45 | 4 · reply loop | reply as Dana in the thread → note written back → confirmation on the floor |
| 14:45–15:15 | polish | controls not flagged; wording facts-only; run once warm |
| 15:15–15:45 | **record** | reseed, one take per `demo/script.md`; export |
| 15:45–16:00 | submit | title, description, repo public, video link, social post |

**Rule for the day:** whatever rung you are on at 15:15, stop and record. A finished small thing beats an unfinished bigger one every time.

## Design decisions to say out loud (judges reward these)

- **Narrow agents beat one broad one** — each sees a slice; the merge happens at the Desk. That's why the same customer shows up as one problem instead of four alerts.
- **The agent channel is the audit trail** — every decision is a message a human can read later.
- **Human attention is the scarce resource** — max three items; everything else handled and logged.
- **Two passes, no loops** — the round is bounded by construction, not by hoping.
- **Read-heavy, write-light** — notes, drafts and tasks only; never sends, never changes stages or calendars. The closed action set in `execute_actions` refuses anything else — show the refusal.
- **Facts and dates, never opinions about people** — the "never" list in `agents.yaml`.

## If MCP fights you

Run the entire demo on `MockClient` with the terminal as the "floor" — it still shows the multiplayer merge and the brief. Less pretty, fully honest, and you can say "the workspace adapter is the next hour of work." Working beats wired.
