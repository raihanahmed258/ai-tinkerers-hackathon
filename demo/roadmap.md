# Designed next, coding in parallel

These are deliberately outside the Tier 1 demo claim.

## Account timeline

A persistent, per-account record of findings, assignments, verifier verdicts, worker receipts, and human decisions across rounds. It should prevent the same unresolved issue from being reintroduced as a brand-new alert every day.

## Reply handler

A handler for explicit human decisions in `#attention`. It should extract only an unambiguous decision, run that proposed write through the same Verifier gate, and then post a `DONE` or `BLOCKED` receipt on `#agents-floor`.

Neither component is shown in the Ambiguous-only Tier 1 recording or described as working today.
