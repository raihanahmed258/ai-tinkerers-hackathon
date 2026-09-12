# Scheduling the round (not enabled)

No schedule is running today. This is a deployment recipe, not a claim about the current prototype. With a small workspace-action or model budget, run manually until the write volume has been measured on the exact live configuration.

## What actually has to happen

One invocation runs a live round:

```bash
cd /path/to/the-floor
.venv/bin/python -m floor.round --live
```

The round is bounded to exactly two passes. It can still create many workspace posts and writes, so `--live` should be deliberate. Use `python -m floor.round --no-model` for free local smoke tests.

Environment it needs:

| Variable | Why |
|---|---|
| `ANTHROPIC_API_KEY` | watcher and Desk model calls; omit it and pass `--no-model` for a guaranteed no-model smoke test |
| `AMBIGUOUS_API_KEY` or `AMBIGUOUS_TOKEN` | the workspace MCP server |
| `AMBIGUOUS_MCP_URL` | optional, defaults to `https://app.ambiguous.ai/mcp` |
| `AMBIGUOUS_TOKEN_DESK` | required for live Verifier/Closer authorship unless their dedicated tokens are set |

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

Do not use the old 25-writes estimate. The Tier 1 protocol adds an `ASSIGN`, a Verifier verdict, and a `DONE` or `BLOCKED` receipt around each action. The measured heuristic demo run with safety theater produced roughly 113 workspace writes plus four model-call slots. Normal mode now omits the seven synthetic safety-demo posts, but the exact total still depends on findings and actions.

Before scheduling:

1. Run the mock with `--no-model`.
2. Run at most one deliberate live round and count workspace reads/writes.
3. Confirm how Ambiguous meters reads and posts.
4. Divide the actual allowance by that measured total.

With a 1,000-action allowance, a roughly 100-write round supports about ten runs, not a weekday month. Keep `--safety-demo`, `--timeline`, and `FLOOR_REPLY_LOOP` off unless that specific behavior is being tested.

## Status, honestly

The runner takes `--live`; unattended scheduling has not been proven over several days and is not enabled. Treat the cadence as a deployment option, not current product behavior.
