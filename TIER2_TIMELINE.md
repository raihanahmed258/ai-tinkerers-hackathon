# Tier 2: Timeline-Based Escalation Control

## What This Does

Adds per-account timeline tracking to prevent re-escalating accounts that are already waiting on a human response. When an account has been escalated to `#attention` within the past 3 days, subsequent rounds will downgrade it to floor-only handling instead of re-posting it to humans.

## Files Changed

### New Files

- **`floor/timeline.py`** — Timeline tracking module with per-account state:
  - `AccountTimeline`: dataclass tracking last decision, drafts prepared, waiting status
  - `TimelineStore`: JSON-backed storage for timeline state
  - `should_escalate()`: checks if an account should be escalated to humans
  - `update()`: records decisions, drafts, and escalations

- **`seed/timeline.json`** — Seed data with initial timeline state:
  - Pine & Salt: escalated 2 days ago, waiting on human
  - Copper Kettle Group: has draft prepared, not waiting
  - Ember Grill: baseline tracking, no escalation

### Modified Files

- **`floor/round.py`**:
  - Imports timeline store
  - `run_desk_merge()`: checks timeline before escalating
  - Downgrades re-escalations for accounts already waiting on humans
  - Updates timeline when desk makes decisions/escalations
  - `post_brief()`: logs timeline-skipped items

## API Surface

```python
from floor.timeline import get_default_store

# Get store (reads from seed/timeline.json by default)
store = get_default_store()

# Check if account should be escalated
should_escalate, reason = store.should_escalate("Pine & Salt")
# Returns: (False, "already waiting on human (2 days ago)")

# Update timeline after decision
store.update(
    "Copper Kettle Group",
    add_draft="M-1",
    waiting_on="none"
)

# Record escalation
store.update(
    "Ember Grill",
    escalate=True,
    escalation_cause="Customer unanswered 4 days"
)
```

## How Skip/Downgrade Works

### Check Phase (before escalation)

In `run_desk_merge()`, after problems are generated:

1. For each problem with `human` set
2. Check timeline: `should_escalate(account)`
3. If account was escalated < 3 days ago AND waiting_on="human":
   - Downgrade: set `human=None`
   - Add `_timeline_skip` marker with reason
   - Problem stays in the brief but NOT in the top 3 human items

### Update Phase (after escalation)

After problems are finalized:

1. Track drafts prepared for each problem
2. Record new escalations with cause
3. Update timeline state and save to JSON

### Logging

In `post_brief()`:
- `[Timeline] Skipped re-escalation: {account} — {reason}`

## Demo in Ambiguous (Mock)

### Setup

```bash
cd /workspace
python3 -m floor.round
```

### Expected Behavior

**Initial timeline state** (`seed/timeline.json`):
- Pine & Salt: escalated 2026-09-10 (2 days ago), waiting on human

**Round output**:
1. Pine & Salt appears on the floor (watcher finds the issue)
2. `[Timeline] Skipped re-escalation: Pine & Salt — already waiting on human (2 days ago)`
3. Pine & Salt is NOT in the top 3 brief items
4. Pine & Salt appears in "Handled without you" list
5. Timeline is updated with current decisions

**Verification**:

```bash
# Run and check for skip message
python3 -m floor.round 2>&1 | grep "Timeline"

# Verify Pine & Salt is not in top 3
python3 -m floor.round 2>&1 | grep -A10 "Attention brief"

# Check timeline state after run
cat seed/timeline.json
```

### Second Round Demo

To demonstrate ongoing skip behavior:

1. Run round once to establish escalations
2. Run again immediately
3. All accounts escalated in round 1 will be skipped in round 2 (0 days ago)

## Demo in Ambiguous (Live)

If running against live Ambiguous workspace:

```bash
export ANTHROPIC_API_KEY="your-key"
export AMBIGUOUS_API_KEY="your-token"
python3 -m floor.round --live
```

Same behavior as mock, but:
- Timeline persists across runs
- Real MCP calls to Ambiguous workspace
- Timeline.json tracks actual escalation history

## Unit Testing

Timeline module is mock-friendly:

```python
from floor.timeline import TimelineStore
from pathlib import Path

# Use custom path for testing
store = TimelineStore(Path("/tmp/test_timeline.json"))

# Test skip logic
store.update("Test Account", escalate=True, escalation_cause="test")
should, reason = store.should_escalate("Test Account")
assert not should
assert "already waiting on human (0 days ago)" in reason

# Test resolution
store.resolve_escalation("Test Account")
should, reason = store.should_escalate("Test Account")
assert should
```

## Integration with Existing Flow

The timeline system integrates cleanly without rewriting Tier 1:

- `execute_actions()`: unchanged, still handles ASSIGN→VERIFIER→DONE/BLOCKED
- `_heuristic_desk_merge()`: unchanged, timeline check happens after merge
- `_stabilize_brief()`: unchanged, timeline check happens before brief generation
- Playbook ranking: unchanged, timeline is a pre-filter

Timeline operates as a thin layer:
1. Read timeline before escalating
2. Write timeline after deciding
3. Log skips for visibility

No changes to watcher logic, desk merge theater, or action execution.
