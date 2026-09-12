# Claim sheet: The Floor, 2026-09-12

Every other file in `demo/` must agree with this sheet. If a doc and this sheet disagree, the sheet wins and the doc is wrong.

## WILL CLAIM LIVE

- **Hard watcher lanes.** `#agents-floor`, label `FINDING · Follow-up`, each card carrying a `ref:` line (a seed id on the mock, a live id or chat message live). Lanes are code in `floor/router.py` `slice_for`, not an LLM. `FINDING · Ops` and `FINDING · Inbox` are claimed only if a judge can see one on screen: the live CRM has no stage-entered date and the live inbox is empty, so both blocks can be absent. Cards carry their own seat name only if the three watcher tokens are set; otherwise every post is signed as Desk.
- **Desk merge.** `#agents-floor`, label `PROBLEM · <account> · rank N`, with a `merges:` line of evidence ids. Up to five cards, sliced in code; five on the mock, three live-shaped. Point only at a card with an account name.
- **Refusal theater, every round, before any worker acts.** `#agents-floor`: `ASSIGN · Inbox → send email to customer`, then `VERIFIER · refused`, then `BLOCKED · Inbox · send email to customer`; and `ASSIGN · Ops → set_field`, then `VERIFIER · refused`, then `BLOCKED · Ops · set_field`.
- **The Tier 1 handoff.** `#agents-floor`: at least one chain of `ASSIGN`, `VERIFIER · approved`, `DONE`. Live-shaped that chain is `ASSIGN · Follow-up → assign task`, `VERIFIER · approved`, `DONE · Follow-up · assign_task`; an `add_note` chain exists only if Ops posted a finding. The VERIFIER verdict posts as Desk, which requires `AMBIGUOUS_TOKEN_DESK` before the round; without it the floor freezes on the first refusal-theater `ASSIGN` and no brief is posted.
- **Fail-closed receipts.** `#agents-floor`: the two refusal-theater `BLOCKED` receipts every round. A `BLOCKED · Inbox · draft` receipt appears only when a draft was planned and no live thread resolved; with an empty inbox no draft is planned at all, so do not promise that receipt.
- **One human brief.** `#attention`, one post headed `Attention brief · <date>`, line `N item(s) need a person` with N at most 3, each item naming an owner and an `Evidence:` line of ids.
- **No send, no stage, no calendar.** The client has no send method and no calendar write; `set_field` is never approved for any field; a stage write raises `PermissionError` in `floor/client.py`.

## WILL NOT CLAIM

- A model-validated run of the current protocol. The only validation artifact predates the protocol (H1). The counts we quote come from the offline mock on the heuristic path.
- A live Inbox finding, a live Mail draft as agent output, or the `Ready:` line in the brief (H3, H4). The three drafts in the workspace were placed during seeding.
- The reply loop as working. It is implemented in `floor/reply_handler.py` behind `FLOOR_REPLY_LOOP`, off by default, not demonstrated (H5).
- The account timeline or the `rank=None` fix. Both merged to GitHub `main` in PR #4 at `76be8d5`, after the recording checkout `54ef2e6`, and neither is in the code being recorded. On the merged code the seeded timeline downgrades every golden item and the brief reads `0 item(s) need a person`, so the checkout is not pulled before the take (H10, H11).
- The brief order as model judgment. Findings and merge are derived; ranks 1 to 3 and their owners are a hand-written playbook prior in `_stabilize_brief` (H7). No budget figure, no schedule running, and no dedicated Verifier or Closer seat (H8).
