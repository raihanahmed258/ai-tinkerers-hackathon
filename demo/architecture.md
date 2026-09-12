# The Floor — Tier 1 orchestration

> **Current protocol:** Desk `ASSIGN` → `VERIFIER · approved | refused | needs_rewrite` → worker `DONE | BLOCKED`. The human brief goes only to `#attention` and contains at most three items.

```mermaid
flowchart LR
  S[Workspace signals] --> R[Hard router lanes]
  R -->|CRM only| O[Ops]
  R -->|Mail only| I[Inbox]
  R -->|Tasks · Calendar · selected chat| F[Follow-up]
  O --> FLOOR[#agents-floor]
  I --> FLOOR
  F --> FLOOR
  FLOOR --> D[Desk: merge and ASSIGN]
  D --> V[Verifier code gate]
  V -->|approved| W[Assigned worker]
  V -->|needs_rewrite| D
  V -->|refused| FLOOR
  W -->|DONE or BLOCKED| FLOOR
  FLOOR --> D
  D --> BRIEF[#attention: at most 3 items]
  T[Optional demo tests:\nsend customer email · move stage] --> V
```

## Hard lanes, not a broad router agent

The router is an implementation boundary, not another agent persona and not an LLM deciding who should see what:

- **Ops** receives CRM only.
- **Inbox** receives Mail only.
- **Follow-up** receives Tasks, Calendar, and selected chat only.

That keeps evidence narrow before the Desk makes a cross-tool merge.

## Verifier is a protocol, not a required seat

The important visible artifact is the `VERIFIER` verdict on the floor. A dedicated Ambiguous Verifier or Closer seat is optional. Without one, the code gate posts through the Desk token. It never falls back to a human/default token; without either a role token or Desk token, it fails closed.

## Safety theater is deliberate

Pass `--safety-demo` to inject two fake requests: `send customer email` and `move stage`. Both should receive `VERIFIER · refused` before productive work. Normal rounds omit this synthetic traffic.

## Optional and not demo claims

- **Account timeline:** opt-in persistent per-account memory (`--timeline`).
- **Reply handler:** opt-in recording of an explicit human decision (`FLOOR_REPLY_LOOP=1`).

Neither is part of the Tier 1 live recording. See [roadmap.md](roadmap.md).
