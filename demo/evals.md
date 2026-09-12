# Evaluation quick check

Run evaluations outside the live Ambiguous recording. They are for validating a captured round, not for the two-minute shot list.

```bash
python -m floor.round --no-model | tee run.txt
python -m floor.eval_expected run.txt
FLOOR_NO_MODEL=1 python -m floor.eval_unpinned --trace
```

The no-model path is expected to score AMBER on brief ordering. These commands
are free smoke tests for safety and control handling, not polished demo evidence.

## Read the result

- **GREEN:** the captured round meets the expected behavior and safety checks. This is the only result to use as polished demo evidence.
- **AMBER:** no immediate hard failure, but expected findings, ordering, or another evaluated behavior needs review. Inspect the report and fix or explain the gap before recording.
- **RED:** a required safety or correctness check failed. Do not use the run for a demo.

`eval_expected` checks the captured round against the golden seed expectations. `eval_unpinned --trace` helps show how the behavior changes without stabilising logic, so it is useful for reviewing how much the implementation relies on those guards.
