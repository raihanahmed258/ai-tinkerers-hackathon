# Optional components, not demoed

These are deliberately outside the Tier 1 demo claim.

## Account timeline

Implemented in `floor/timeline.py`, off by default. Enable deliberately with `--timeline`; runtime state is kept under ignored `.floor/`.

## Reply handler

A handler for explicit human decisions in `#attention`, implemented in `floor/reply_handler.py` and enabled with `FLOOR_REPLY_LOOP=1`.

Neither component is enabled or shown in the Ambiguous-only Tier 1 recording.
