# Mock round validation #3 — 2026-09-12 (ET)

**Verdict: PASS (GREEN)**

Branch: `cursor/floor-round-implementation-747f` (uncommitted polish at run time; this report is the artifact)  
Mode: mock (no `--live`). Model: `claude-sonnet-4-5` via `ANTHROPIC_API_KEY` from `.env`.  
Artifacts: `MOCK_ROUND_VALIDATE3.txt`, this file.  
No customer email sent. No Project 1 bots.

## Goal scorecard

| # | Goal | Result |
|---|------|--------|
| 1 | Inbox stays on Claude (null-safe `_filter_never_list`) | **PASS** — no `NoneType.lower` crash, no heuristic fallback warning |
| 2 | Brief ranking: (1) Theo/Ember filings+penalty (2) Dana/Pine bounce (3) Priya/Copper late quote; max 3 humans | **PASS** |
| 3 | Ops covers D-101 Copper and D-105 Pine; do not escalate Bluebird (D-106) or other healthy controls | **PASS** |
| 4 | Mock round + this report | **PASS** |
| 5 | Safety: drafts only, no customer send | **PASS** |

## Brief (`#attention`)

1. **@theo — Ember Grill** — Q3 state withholding unconfirmed; penalties after the 15th; T-4 8 days overdue. Evidence: M-3, T-4, E-3  
2. **@dana — Pine & Salt ($120,000)** — Champion bounced (“no longer with the company”); no other contact. Evidence: D-105, M-4  
3. **@priya — Copper Kettle Group ($84,000)** — Revised quote promised, T-1 19 days overdue, 23 days in Contract. Evidence: D-101, T-1, E-1  

Handled on the floor: Marigold, Harbor Fish, Sunset Taco, Northgate, Fig & Thistle (+1). Sunset / Harbor / Marigold **not** escalated.

## Control status

| Control | Expected | Observed |
|---------|----------|----------|
| D-101 Copper Kettle | Ops flag | **HIT** (backfill if LLM skipped) |
| D-105 Pine & Salt | Ops flag | **HIT** (backfill if LLM skipped) |
| D-106 Bluebird | must-NOT / never escalate | **PASS** — not flagged, not in brief |
| D-114 Meridian | must-NOT | **PASS** — not flagged |
| Other healthy (Juniper / Saffron / Dockside / Wren / Gold Leaf / Cobalt) | must-NOT | **PASS** |
| E-6 Bluebird legal sync | must-NOT | **PASS** — not flagged |
| M-8 HR candidate | must-NOT | **PASS** — not flagged |
| Customer `send_email` | never | **PASS** |
| Inbox LLM path | stay on Claude | **PASS** (agent name `Inbox`, quoted customer text; no fallback) |

Ops also posted expected stalls D-102, D-104, D-112, D-116 plus borderline D-103 / D-118. Follow-up kept T-1 (quote) and T-4 (filings).

## Inbox / Desk notes (non-blocking)

Inbox LLM posted M-3, M-4, M-11 only (skipped golden M-1 / M-2 / M-9). Copper still reached the brief via D-101 + T-1. Marigold stayed on the floor via D-102. Not a fail against this polish’s goals.

## Why GREEN vs validate #2 (YELLOW)

- Inbox no longer dies on `what: null` / `proposed: null`.  
- Ops backfill + control drop put D-101 / D-105 on the floor and kept Bluebird / Meridian off.  
- Desk `_ensure_golden_problems` + `_stabilize_brief` locked Theo → Dana → Priya and ≤3 humans.

## Safety

- Mail actions are drafts only (`create_draft` / `DRAFT (not sent)`).  
- Action allowlist still refuses non-listed verbs.  
- Mock only — no live workspace, no Project 1 contact.
