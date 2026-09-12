# Judge Q&A — The Floor

## Why multiple agents instead of one broad agent?

Each watcher has a hard evidence lane: Ops sees CRM only, Inbox sees Mail only, and Follow-up sees Tasks, Calendar, and selected chat only. The Desk is the one place where those narrow findings are merged into a customer-level problem. That is how the system reduces duplicate alerts without giving every agent unrestricted access.

## What is the visible multi-agent protocol?

The floor shows a fixed handoff: `ASSIGN → VERIFIER · approved | refused | needs_rewrite → DONE | BLOCKED`. The Desk assigns bounded work, the Verifier gate decides whether it is permitted, and the worker reports the result back to `#agents-floor`.

## Is Verifier a separate Ambiguous agent?

Not necessarily. The safety boundary is the Verifier code gate and its visible floor verdict. If Ambiguous seats are limited, that verdict can post through the Desk or a human-controlled identity. We do not claim a dedicated Verifier or Closer seat unless it is visibly available in the workspace.

## How do you show the system refuses unsafe work?

Every round includes two clearly labelled fake safety tests: `send customer email` and `move stage`. Both must show `VERIFIER · refused` before a worker acts. They are refusal theater by design: no real customer request and no real write is attempted.

## What can the system change?

It can prepare or coordinate bounded internal work. It cannot send customer messages, move stages, or move close dates. The `#attention` brief is capped at three human items, so an unresolved issue becomes a named decision rather than an autonomous business change.

## Why do you not show Mail drafts?

The live workspace has an inbound-mail gap, and seed drafts are not reliable evidence that this round created a draft. The live recording proves the floor protocol, verifier verdicts, worker receipts, and brief. It does not claim a Mail-draft result that cannot be shown cleanly.

## Is the demo live?

Yes: the recording stays in Ambiguous and shows live channel artifacts. The recording does not rely on a terminal or claim that every workspace capability is available. The protocol is the product proof.

## What is still unfinished?

A persistent account timeline and a human-reply handler are designed and coding in parallel. They are not shown or claimed as working in the two-minute Tier 1 recording.

## How do you evaluate it?

After a run, use [evals.md](evals.md). `GREEN` means the expected behavior and safety checks passed; `AMBER` means the run needs review before it is used as demo evidence.
