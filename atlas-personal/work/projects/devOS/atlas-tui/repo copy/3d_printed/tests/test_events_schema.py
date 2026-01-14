from __future__ import annotations

import _path  # noqa: F401
import json
import unittest

from atlas_tui.determinism import FixedClock
from atlas_tui.ui_events import (
    focus_changed,
    glass_pointer_updated,
    key_handled,
    log_written,
    submit_done,
    submit_started,
)


class TestUIEventSchema(unittest.TestCase):
    def test_events_serialize_schema_v1(self) -> None:
        clock = FixedClock("2000-01-01T00:00:00+00:00")
        session_id = "s"
        events = [
            focus_changed(session_id, "chat", "composer", clock=clock),
            key_handled(session_id, "f1", "toggle_help", 1, "help_toggle", clock=clock),
            submit_started(session_id, "r1", "interpret", "dummy", "dummy", clock=clock),
            submit_done(session_id, "r1", True, 123, clock=clock),
            log_written(session_id, "logs/atlas-tui/assembled/r1.json", 10, clock=clock),
            glass_pointer_updated(session_id, "logs/atlas-tui/assembled/r1.json", clock=clock),
        ]
        for ev in events:
            d = ev.to_dict()
            self.assertEqual(d["schema_version"], 1)
            self.assertEqual(d["session_id"], session_id)
            self.assertEqual(d["ts"], clock.iso)
            json.dumps(d)
