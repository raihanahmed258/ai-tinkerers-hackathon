# Live workspace round report — 2026-09-12

## Final Sonnet 5 round — use this

**Complete current protocol observed in Ambiguous.** The round ran from
15:22–15:27 EDT (19:22–19:27 UTC) from commit `fd63f58`, configured for
`claude-sonnet-5`. The second run produced no Anthropic fallback warning.

Channel: `#agents-floor` (`6606389e-0977-415a-987e-599001037834`)

- Pass 1: `e2926887-86bb-4484-b4d1-47126a2915d9`
- Findings: **15** — 7 Ops, 0 Inbox, 8 Follow-up
- Pass 2: `f05da029-b4e5-4ef7-bfa6-0685cf009885`
- Desk merge: 15 findings → 6 problems; 5 PROBLEM cards posted
- Safety header: `4e0bd1d3-ce02-4263-abcf-ca536bf26148`
- Customer send refused and blocked:
  `c8b10f79-0770-4c6f-9a74-80da731b2eb8`
- Stage change refused and blocked:
  `cca94242-0126-4bcc-b938-0275766cb4a8` →
  `f9908691-b88a-45a3-9e52-87c16ced615d`
- Work summary: `23ebaa58-760a-44e8-960d-bfc80096fe43`
- Done: `d95c9237-046b-42e9-bb1a-c6eb6177216e`

Channel: `#attention` (`8db08df8-60fe-4366-beef-fb13163d73ef`)

- Clean brief: `d9aff913-9c63-48bf-895b-9ccc6021cd04`
- Three items: Ember Grill, Pine & Salt, Copper Kettle Group
- No stale `Ready:` line and no reply-handling promise

This is the definitive demo round. Inbox is still empty live, and a DONE
receipt remains the runner's report rather than independent proof of the
created object.

## Historical reference — superseded

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
  - header: message `e1a988b9-f0e4-4cb3-b431-c2716ace57ff`
  - customer-send request → `VERIFIER · refused` → `BLOCKED`, with blocked
    receipt `ffb0d680-e054-4460-a2a2-d9349ca78c7b`
  - stage-change request → `VERIFIER · refused` → `BLOCKED`, with verifier
    receipt `b660247a-54c2-4473-b859-01e96469dcec` and blocked receipt
    `fdefb7fb-9a2d-4408-8ea8-1a77208e04eb`
- Approved work:
  - Ember Grill task chain reached `VERIFIER · approved` and `DONE`:
    `505a65e2-d605-404f-a5ed-aceda1cc47cc` →
    `e19885f7-c9a6-495e-9d1b-d2eeb4a00130` →
    `bed76f86-9342-4a18-92e9-e67ee901826b`
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
  `Ready:` line and disabled reply promise. The historical message still shows
  both; the recording guide keeps those lower lines out of frame and provides
  an explicit fallback explanation if they remain visible.
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
