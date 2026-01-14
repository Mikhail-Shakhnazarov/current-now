from __future__ import annotations

import _path  # noqa: F401
import json
import tempfile
import unittest
from urllib.request import urlopen

from atlas_tui.determinism import FixedClock
from atlas_tui.log_writer import write_assembled_log
from atlas_tui.models import AssembledContext, EngineInput, EngineOutput, ProviderRequest, Workspace
from atlas_tui.state_store import UIContextPrefs
from atlas_tui.ui_observability import write_latest_snapshot
from atlas_tui.ui_snapshot import capture_snapshot
from atlas_tui.web.server import start_glass_server


class TestGlassEndpointsSmoke(unittest.TestCase):
    def test_endpoints_return_json(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            ws = Workspace(repo_root=d, project_root=d)
            clock = FixedClock("2000-01-01T00:00:00+00:00")
            engine_input = EngineInput(workspace=ws, mode="interpret", provider="dummy", model="dummy", user_message="hi", ui_state={})
            out = EngineOutput(
                assembled_context=AssembledContext(mode="interpret", system="SYS", selected_artifacts=["README.md"]),
                provider_request=ProviderRequest(provider="dummy", model="dummy", system="SYS", user="hi", messages=[]),
                diagnostics={},
            )
            write_assembled_log(workspace=ws, request_id="r1", engine_input=engine_input, engine_output=out, session_id="s", clock=clock)
            snap = capture_snapshot(
                focused_panel="chat",
                focused_widget_id="composer",
                screen_stack=["Screen"],
                selected_path=None,
                mode="interpret",
                provider="dummy",
                model="dummy",
                last_request_id="r1",
                last_log_path="logs/atlas-tui/assembled/r1.json",
                prefs=UIContextPrefs(),
                session_id="s",
                clock=clock,
            )
            write_latest_snapshot(ws, snap)

            server = start_glass_server(ws, port=0)
            try:
                for path in ["/api/latest", "/api/ui/latest_snapshot", "/api/ui/events_tail?n=10"]:
                    with urlopen(server.url.rstrip("/") + path) as r:
                        data = json.loads(r.read().decode("utf-8"))
                        self.assertIn("status", data)
            finally:
                server.stop()
