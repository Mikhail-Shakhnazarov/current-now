from __future__ import annotations

import _path  # noqa: F401
import json
import tempfile
import unittest

from atlas_tui.determinism import FixedClock
from atlas_tui.models import Workspace
from atlas_tui.state_store import UIContextPrefs
from atlas_tui.ui_observability import latest_snapshot_path, write_latest_snapshot
from atlas_tui.ui_snapshot import capture_snapshot


class TestSnapshotLogging(unittest.TestCase):
    def test_write_and_readback_snapshot(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            ws = Workspace(repo_root=d, project_root=d)
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
                clock=FixedClock("2000-01-01T00:00:00+00:00"),
            )
            write_latest_snapshot(ws, snap)
            path = latest_snapshot_path(ws)
            self.assertTrue(path.exists())
            obj = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(obj["schema_version"], 1)
            self.assertEqual(obj["focused_panel"], "chat")
