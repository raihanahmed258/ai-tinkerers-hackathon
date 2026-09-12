# Running the round every morning

The product claim is "always-on", so the round has to fire without anyone typing a command. This is the recipe, plus the honest note about which part is wired today.

## What actually has to happen

One invocation of `run_round` per weekday morning, against the live workspace:

```bash
cd /path/to/the-floor
.venv/bin/python -m floor.round --live
```

That is the whole job. The round is bounded to exactly two passes, so there is no supervisor to write, nothing to poll, and no way for it to run long. It either completes or it fails, and a failure is safe because the write surface is notes, drafts and tasks.

Environment it needs:

| Variable | Why |
|---|---|
| `ANTHROPIC_API_KEY` | the watcher and Desk model calls. Without it the round silently falls back to heuristics and the brief comes out wrong, so treat a missing key as a hard failure, not a degraded mode |
| `AMBIGUOUS_API_KEY` or `AMBIGUOUS_TOKEN` | the workspace MCP server |
| `AMBIGUOUS_MCP_URL` | optional, defaults to `https://app.ambiguous.ai/mcp` |

## Option 1 — the workspace's own Automations app

The right home for it, because the schedule then lives next to the agents it drives and a teammate can see it without reading this repo. Point a weekday 09:00 trigger at the runner.

Worth checking before you rely on it: whether Automations can invoke an external process at all, or only workspace-native actions. If it is the latter, it can still be the trigger — have it post a message to `#agents-floor` and let option 2 or 3 watch for that.

## Option 2 — Trigger.dev

A scheduled task that shells out to the runner. Cron expression for weekdays at 09:00:

```
0 9 * * 1-5
```

Set the timezone explicitly rather than inheriting UTC, or the round arrives at 04:00 local and the brief is stale by the time anyone reads it.

## Option 3 — plain cron or launchd

The unglamorous option that works. On macOS, `launchd` survives reboots where a user crontab may not.

```
0 9 * * 1-5  cd /path/to/the-floor && .venv/bin/python -m floor.round --live >> logs/round-$(date +\%Y-\%m-\%d).log 2>&1
```

Redirect to a dated log and the scorecard becomes part of the schedule:

```bash
.venv/bin/python -m floor.eval_expected logs/round-$(date +%Y-%m-%d).log
```

It exits non-zero when a control got flagged or the brief lost its lead item, so the same cron line can page you when a round goes wrong instead of leaving a bad brief sitting in `#attention`.

## Budget

The free tier is 1,000 AI actions per month, so the schedule has to fit inside it. Measured from the validated round:

| Per round | Count |
|---|---|
| Posts to `#agents-floor` | 21 |
| Post to `#attention` | 1 |
| Tasks created | 3 |
| Workspace writes | **25** |
| Workspace reads (deals, threads, tasks, events, two channels) | ~6 |
| Claude model calls | 4 |

Weekdays only is about 21 rounds a month, so roughly 525 write actions, or about 650 if reads are counted too. Both fit, with room for the end-to-end checks you will run by hand. Two rounds a day would not fit comfortably, and a round per hour would blow the tier in three days.

Confirm what the workspace actually counts as an "action" before trusting that arithmetic. Reads being free versus metered is the difference between comfortable and tight.

## Status, honestly

The runner works and takes `--live`. The schedule is a wrapper around one command and none of the options above are exotic. What has not been proven out is a scheduled round running unattended against the live workspace over several days, so treat the cadence as designed and the runner as tested. Saying it that way costs nothing and is much better than being asked when it last ran and having to guess.
