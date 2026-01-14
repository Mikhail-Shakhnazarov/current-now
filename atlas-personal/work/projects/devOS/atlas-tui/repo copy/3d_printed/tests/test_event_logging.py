from __future__ import annotations

import _path  # noqa: F401
import json
import tempfile
import unittest

from atlas_tui.determinism import FixedClock
from atlas_tui.models import Workspace
from atlas_tui.ui_events import key_handled
from atlas_tui.ui_observability import append_ui_event, events_log_path


class TestEventLogging(unittest.TestCase):
    def test_append_and_readback_jsonl(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            ws = Workspace(repo_root=d, project_root=d)
            ev = key_handled("s", "f1", "toggle_help", 1, "help_toggle", clock=FixedClock("2000-01-01T00:00:00+00:00"))
            append_ui_event(ws, ev)
            path = events_log_path(ws)
            self.assertTrue(path.exists())
            lines = path.read_text(encoding="utf-8").splitlines()
            self.assertEqual(len(lines), 1)
            obj = json.loads(lines[0])
            self.assertEqual(obj["type"], "key_handled")
