import os
import subprocess
import sys
import unittest
from unittest.mock import patch

from floor.client import MockClient
from floor.round import (
    _model_api_key,
    _refusal_theater,
    _timeline_store,
    _valid_timeline_account,
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

    def test_timeline_rejects_refs_and_uuid_placeholders(self):
        self.assertFalse(_valid_timeline_account("T-1"))
        self.assertFalse(_valid_timeline_account("6606389e-0977-415a-987e-599001037834"))
        self.assertTrue(_valid_timeline_account("Copper Kettle Group"))

    def test_safety_demo_posts_only_when_called(self):
        ws = MockClient(verbose=False)
        _refusal_theater(ws, [{"account": "Example Co", "merges": ["D-101"]}])
        floor = "\n".join(message["text"] for message in ws.channels["agents-floor"])
        self.assertIn("Refusal theater", floor)
        self.assertEqual(floor.count("VERIFIER · refused"), 2)

    def test_brief_does_not_promise_disabled_reply_handler(self):
        ws = MockClient(verbose=False)
        with patch.dict(os.environ, {}, clear=True):
            post_brief(
                [{
                    "account": "Example Co",
                    "rank": 1,
                    "merges": ["D-101"],
                    "actions": [{"action": "draft"}],
                    "human": {"who": "dana"},
                }],
                ws,
            )
        brief = ws.channels["attention"][-1]["text"]
        self.assertNotIn("Reply in this thread", brief)
        self.assertNotIn("Ready:", brief)

    def test_live_mode_preflights_before_workspace_access(self):
        env = dict(os.environ)
        for name in (
            "AMBIGUOUS_API_KEY",
            "AMBIGUOUS_TOKEN",
            "AMBIGUOUS_TOKEN_DESK",
            "AMBIGUOUS_TOKEN_VERIFIER",
        ):
            env.pop(name, None)
        result = subprocess.run(
            [sys.executable, "-m", "floor.round", "--live", "--no-model"],
            capture_output=True,
            text=True,
            env=env,
            check=False,
        )
        self.assertEqual(result.returncode, 2)
        self.assertIn("--live requires AMBIGUOUS_API_KEY", result.stderr)
        self.assertNotIn("POST", result.stdout)


if __name__ == "__main__":
    unittest.main()
