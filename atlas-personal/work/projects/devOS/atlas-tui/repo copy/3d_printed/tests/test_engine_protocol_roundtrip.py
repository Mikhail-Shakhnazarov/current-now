from __future__ import annotations

import _path  # noqa: F401
import sys
import tempfile
import unittest

from atlas_tui.engine_client import EngineClient
from atlas_tui.models import EngineInput, Workspace


class TestEngineProtocolRoundtrip(unittest.IsolatedAsyncioTestCase):
    async def test_roundtrip_dummy_engine(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            ws = Workspace(repo_root=d, project_root=d)
            cmd = [sys.executable, "-m", "atlas_tui.dummy_engine"]
            client = EngineClient(cmd, workspace=ws, timeout_s=5.0)
            inp = EngineInput(workspace=ws, mode="interpret", provider="dummy", model="dummy", user_message="hello", ui_state={})
            out = await client.submit("r1", inp)
            self.assertIn("ATLAS_TUI_DUMMY_ENGINE", out.assembled_context.system)
            self.assertIsInstance(out.assembled_context.selected_artifacts, list)
            await client.stop()
