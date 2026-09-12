# Live workspace round report — 2026-09-12

## Verdict

**Complete live protocol observed in Ambiguous.** The round began at 17:13 UTC,
posted through 17:18 UTC, and ended with a linked brief in `#attention`.
This report was assembled from read-only workspace queries on 2026-09-12; no
model calls or workspace writes were made during verification.

## Observed sequence

Channel: `#agents-floor` (`6606389e-0977-415a-987e-599001037834`)

- Pass 1 header: message `4b0ef2d8-ac1b-447a-b7a5-b213d31f8a91`
- Findings: **8**, all authored by the Follow-up agent
- Pass 2 header: message `8ee91750-6923-4662-94eb-5cbb6aeb0c5d`
- Merged problems: **5**
  1. Ember Grill
  2. Copper Kettle Group
  3. Marigold Diners
  4. Harbor Fish
  5. Northgate Brewing
- Safety demo:
  - customer-send request → `VERIFIER · refused` → `BLOCKED`
  - stage-change request → `VERIFIER · refused` → `BLOCKED`
- Approved work:
  - Ember Grill task chain reached `VERIFIER · approved` and `DONE`
  - other task and internal-question chains also reached `DONE`
  - unresolved Inbox draft chains ended `BLOCKED`, not fake `DONE`
- Work summary: message `718753c3-9e87-48ab-9ff1-05b97334f283`
- Round complete: message `b8e239fa-fb86-4856-aba8-8fc86fdf1d5b`

Channel: `#attention` (`8db08df8-60fe-4366-beef-fb13163d73ef`)

- Brief: message `3c3d3750-29fc-4aed-9930-015caa11731c`
- Human items: **1**
- Lead: `@theo — Ember Grill`
- Evidence: live deal/task identifiers

## What this proves

- The Python protocol completed against the real Ambiguous workspace.
- Agent identities posted as Desk, Follow-up, Inbox, and Ops.
- The visible `ASSIGN → VERIFIER → DONE | BLOCKED` sequence works live.
- Unsafe customer-send and stage-change requests were refused live.
- The Desk produced and linked a bounded human brief.
- The empty live Inbox fails closed: unresolved drafts become `BLOCKED`.

## Limits

- The channel does not independently prove which model path produced the
  findings. Do not call this a Claude-validated run without a matching runner
  log.
- Ops and Inbox posted no findings in this round; all eight came from
  Follow-up.
- The brief contains one human item, not the three-item mock story.
- This round predates the cleanup that removed the brief's misleading
  `Ready:` line and disabled reply promise.
- Floor `DONE` receipts prove what the runner reported. A read-only task search
  found Ember Grill tasks created earlier at 16:18 and 16:32 UTC, but no task
  timestamped during this round, so the 17:16 task receipt was not independently
  matched to a newly created task object.

## Recording recommendation

This round is suitable for demonstrating the live orchestration protocol:
findings, merge, safety refusals, approved work, blocked work, and the human
brief. Present the brief as **at most three items**, not exactly three. Do not
claim live Inbox discovery, model provenance, timeline behavior, reply handling,
or a newly verified task object.
