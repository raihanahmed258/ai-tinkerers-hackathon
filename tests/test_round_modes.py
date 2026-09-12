import os
import unittest
from unittest.mock import patch

from floor.client import MockClient
from floor.round import (
    _model_api_key,
    _refusal_theater,
    _timeline_store,
    post_brief,
)


class RoundModeTests(unittest.TestCase):
    def test_no_model_mode_overrides_loaded_key(self):
        with patch.dict(
            os.environ,
            {"ANTHROPIC_API_KEY": "would-cost-money", "FLOOR_NO_MODEL": "1"},
            clear=False,
        ):
            self.assertIsNone(_model_api_key())

    def test_timeline_is_off_by_default(self):
        with patch.dict(os.environ, {}, clear=True):
            self.assertIsNone(_timeline_store())

    def test_safety_demo_posts_only_when_called(self):
        ws = MockClient(verbose=False)
        _refusal_theater(ws, [{"account": "Example Co", "merges": ["D-101"]}])
        floor = "\n".join(message["text"] for message in ws.channels["agents-floor"])
        self.assertIn("Refusal theater", floor)
        self.assertEqual(floor.count("VERIFIER · refused"), 2)

    def test_brief_does_not_promise_disabled_reply_handler(self):
        ws = MockClient(verbose=False)
        with patch.dict(os.environ, {}, clear=True):
            post_brief([], ws)
        self.assertNotIn("Reply in this thread", ws.channels["attention"][-1]["text"])


if __name__ == "__main__":
    unittest.main()
