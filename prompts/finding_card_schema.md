# Finding card — the one message format every watcher posts to #agents-floor

Keep it machine-readable enough for the Desk to merge, human-readable enough to be the audit trail.
Post as a chat message with this shape (a fenced block is fine; the Desk parses the labelled lines).

```
FINDING · <watcher> · <confidence: high|medium|low>
account: <account name or "—">
ref: <deal id / thread id / task id / event id>
what: <one sentence, facts and dates only>
why_stalled: <one sentence: waiting on us | waiting on customer | never started | contact lost | unclear>
evidence: <ids or links, comma-separated>
proposed: <draft reply | add note | assign task | ask <person> | cancel/flag event | none>
needs_human: <yes|no> — <one clause on why, if yes>
```

Rules baked into the format:
- `what` is facts and dates. "Unanswered 9 days, customer chased twice" — never "customer is frustrated."
- `why_stalled` is one of five values. If you cannot tell, say `unclear`; the Desk will ask a human a one-line question rather than guess.
- `needs_human: yes` is reserved for things no agent can do: a decision, a missing contact, a compliance confirmation, money.
- One card per finding. No follow-up prose. The Desk replies in-thread.

# Desk decision — what the Desk posts back, in the thread of each finding it merges

```
PROBLEM · <account> · <rank 1..n>
merges: <finding refs>
cause: <one sentence>
actions: <agent → action>, <agent → action>
human: <none | @name — one sentence>
```

# The brief — one post to #attention per round

```
Attention brief · <date> · <n> items need a person · everything else handled on the floor
1. @<name> — <account> ($<arr>): <what and why, two sentences max>. Evidence: <refs>. Ready: <what the agents prepared, e.g. "draft reply in Mail">.
2. ...
3. ...
Handled without you: <one line listing the problems the agents resolved or drafted>
Reply in this thread and I'll record it.
```
