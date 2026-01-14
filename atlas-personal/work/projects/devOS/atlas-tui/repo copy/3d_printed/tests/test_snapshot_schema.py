from __future__ import annotations

import _path  # noqa: F401
import json
import unittest

from atlas_tui.determinism import FixedClock
from atlas_tui.state_store import UIContextPrefs
from atlas_tui.ui_snapshot import capture_snapshot


class TestUISnapshotSchema(unittest.TestCase):
    def test_snapshot_schema_v1(self) -> None:
        clock = FixedClock("2000-01-01T00:00:00+00:00")
        snap = capture_snapshot(
            focused_panel="chat",
            focused_widget_id="composer",
            screen_stack=["Screen"],
            selected_path=None,
            mode="interpret",
            provider="dummy",
            model="dummy",
            last_request_id=None,
            last_log_path=None,
            prefs=UIContextPrefs(),
            session_id="s",
            clock=clock,
        )
        d = snap.to_dict()
        self.assertEqual(d["schema_version"], 1)
        self.assertEqual(d["session_id"], "s")
        self.assertEqual(d["focused_panel"], "chat")
        self.assertIn("prefs", d)
        json.dumps(d)
