from __future__ import annotations

import _path  # noqa: F401
import json
import tempfile
import unittest

from atlas_tui.determinism import FixedClock
from atlas_tui.log_writer import write_assembled_log
from atlas_tui.models import AssembledContext, EngineInput, EngineOutput, ProviderRequest, Workspace
from atlas_tui.state_store import latest_pointer_path
from atlas_tui.ui_observability import events_log_path


class TestLogWriterSmoke(unittest.TestCase):
    def test_writes_assembled_and_latest_and_events(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            ws = Workspace(repo_root=d, project_root=d)
            engine_input = EngineInput(workspace=ws, mode="interpret", provider="dummy", model="dummy", user_message="hi", ui_state={})
            out = EngineOutput(
                assembled_context=AssembledContext(mode="interpret", system="SYS", selected_artifacts=["README.md"]),
                provider_request=ProviderRequest(provider="dummy", model="dummy", system="SYS", user="hi", messages=[]),
                diagnostics={},
            )
            p = write_assembled_log(
                workspace=ws,
                request_id="r1",
                engine_input=engine_input,
                engine_output=out,
                session_id="s",
                clock=FixedClock("2000-01-01T00:00:00+00:00"),
            )
            self.assertTrue(p.exists())
            self.assertEqual(p.name, "r1.json")
            assembled = json.loads(p.read_text(encoding="utf-8"))
            self.assertEqual(assembled["request_id"], "r1")

            lp = latest_pointer_path(ws)
            self.assertTrue(lp.exists())
            meta = json.loads(lp.read_text(encoding="utf-8"))
            self.assertEqual(meta["request_id"], "r1")
            self.assertTrue(str(meta["last_log_path"]).replace("\\", "/").startswith("logs/atlas-tui/assembled/"))

            evp = events_log_path(ws)
            lines = evp.read_text(encoding="utf-8").splitlines()
            self.assertGreaterEqual(len(lines), 2)
