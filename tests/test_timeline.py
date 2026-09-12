import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from floor.timeline import TimelineStore, get_default_store


class TimelineStoreTests(unittest.TestCase):
    def test_escalation_is_persisted_and_can_be_resolved(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "timeline.json"
            store = TimelineStore(path)
            store.update("Example Co", escalate=True, escalation_cause="needs a decision")

            should_escalate, reason = TimelineStore(path).should_escalate("Example Co")
            self.assertFalse(should_escalate)
            self.assertIn("already waiting on human", reason)

            store.resolve_escalation("Example Co")
            self.assertEqual(TimelineStore(path).should_escalate("Example Co"), (True, ""))

    def test_default_path_is_runtime_state_not_seed_data(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "state.json"
            with patch.dict(os.environ, {"FLOOR_TIMELINE_PATH": str(path)}):
                store = get_default_store()
                store.update("Example Co", waiting_on="customer")
            self.assertTrue(path.exists())


if __name__ == "__main__":
    unittest.main()
