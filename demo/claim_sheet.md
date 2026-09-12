# Claim sheet: The Floor, 2026-09-12

Every other file in `demo/` must agree with this sheet. If a doc and this sheet disagree, the sheet wins and the doc is wrong.

Live source: the final Sonnet 5 round completed from 15:22–15:27 EDT
(19:22–19:27 UTC), documented in
[`../LIVE_ROUND_REPORT.md`](../LIVE_ROUND_REPORT.md). It has 15 findings across
Ops and Follow-up, five posted problem cards, both refusal chains, approved
work, and a clean three-item brief.

## WILL CLAIM LIVE

- **Hard watcher lanes.** `#agents-floor` shows 7 `FINDING · Ops` and 8
  `FINDING · Follow-up` cards, each carrying a `ref:` line. Inbox correctly
  posts none because the live inbox is empty. Lanes are code in
  `floor/router.py`, not an LLM.
- **Desk merge.** `#agents-floor`, label `PROBLEM · <account> · rank N`, with a `merges:` line of evidence ids. Up to five cards, sliced in code; five on the mock, three live-shaped. Point only at a card with an account name.
- **Refusal theater, when the demo flag is enabled, before any worker acts.** Run with `--safety-demo`; `#agents-floor` then shows `ASSIGN · Inbox → send email to customer`, `VERIFIER · refused`, `BLOCKED`, followed by the equivalent refused `set_field` chain. Normal rounds omit this synthetic work.
- **The Tier 1 handoff.** `#agents-floor`: at least one chain of `ASSIGN`, `VERIFIER · approved`, `DONE`. Live-shaped that chain is `ASSIGN · Follow-up → assign task`, `VERIFIER · approved`, `DONE · Follow-up · assign_task`; an `add_note` chain exists only if Ops posted a finding. The VERIFIER verdict posts as Desk, which requires `AMBIGUOUS_TOKEN_DESK` before the round; without it the floor freezes on the first refusal-theater `ASSIGN` and no brief is posted.
- **Fail-closed receipts.** `#agents-floor`: recording mode shows the two
  refusal-theater `BLOCKED` receipts. A `BLOCKED · Inbox · draft` receipt appears
  only when a draft was planned and no live thread resolved.
- **One human brief.** `#attention`, one post headed `Attention brief · <date>`, line `N item(s) need a person` with N at most 3, each item naming an owner and an `Evidence:` line of ids.
- **No send, no stage, no calendar.** The client has no send method and no calendar write; `set_field` is never approved for any field; a stage write raises `PermissionError` in `floor/client.py`.

## WILL NOT CLAIM

- Any claim that the historical 17:13 UTC round used Claude. The final 15:22
  EDT run used the Sonnet 5 configuration and produced no fallback warning.
- A live Inbox finding or a live Mail draft as agent output. The three drafts in the workspace were placed during seeding.
- The reply loop as working. It is implemented in `floor/reply_handler.py` behind `FLOOR_REPLY_LOOP`, off by default, and the brief does not promise reply handling while it is off.
- The account timeline as demonstrated. It is merged but opt-in (`--timeline`), uses ignored runtime state under `.floor/`, and is kept off for the recording. The `rank=None` fix is present on current `main`.
- The brief order as model judgment. Findings and merge are derived; ranks 1 to 3 and their owners are a hand-written playbook prior in `_stabilize_brief` (H7). No budget figure, no schedule running, and no dedicated Verifier or Closer seat (H8).
