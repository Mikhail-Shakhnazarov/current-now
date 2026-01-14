from __future__ import annotations

import _path  # noqa: F401
import sys
import tempfile
import unittest
from pathlib import Path

from atlas_tui.determinism import FixedClock, FixedIds
from atlas_tui.models import Workspace
from atlas_tui.ui_observability import latest_snapshot_path

try:
    from atlas_tui.ui.app import AtlasTUIApp
except ModuleNotFoundError as e:
    if getattr(e, "name", "") == "textual":
        AtlasTUIApp = None  # type: ignore[assignment]
    else:
        raise


@unittest.skipIf(AtlasTUIApp is None, "textual is not installed")
class TestUISmoke(unittest.IsolatedAsyncioTestCase):
    async def test_help_overlay_open_close(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            repo = Path(d) / "repo"
            repo.mkdir(parents=True)
            (repo / ".git").mkdir()
            ws = Workspace(repo_root=str(repo), project_root=d)
            app = AtlasTUIApp(
                workspace=ws,
                engine_cmd=[sys.executable, "-c", "raise SystemExit(0)"],
                clock=FixedClock("2000-01-01T00:00:00+00:00"),
                ids=FixedIds(session_id="s", request_id="r"),
            )
            async with app.run_test(size=(120, 40)) as pilot:
                await pilot.press("f1")
                self.assertGreater(len(app.screen_stack), 1)
                await pilot.press("escape")
                self.assertEqual(len(app.screen_stack), 1)

    async def test_escape_opens_and_cancels_quit_confirm(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            repo = Path(d) / "repo"
            repo.mkdir(parents=True)
            (repo / ".git").mkdir()
            ws = Workspace(repo_root=str(repo), project_root=d)
            app = AtlasTUIApp(
                workspace=ws,
                engine_cmd=[sys.executable, "-c", "raise SystemExit(0)"],
                clock=FixedClock("2000-01-01T00:00:00+00:00"),
                ids=FixedIds(session_id="s", request_id="r"),
            )
            async with app.run_test(size=(120, 40)) as pilot:
                await pilot.press("escape")
                self.assertGreater(len(app.screen_stack), 1)
                await pilot.press("escape")
                self.assertEqual(len(app.screen_stack), 1)

    async def test_focus_cycle_writes_snapshot(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            repo = Path(d) / "repo"
            repo.mkdir(parents=True)
            (repo / ".git").mkdir()
            ws = Workspace(repo_root=str(repo), project_root=d)
            app = AtlasTUIApp(
                workspace=ws,
                engine_cmd=[sys.executable, "-c", "raise SystemExit(0)"],
                clock=FixedClock("2000-01-01T00:00:00+00:00"),
                ids=FixedIds(session_id="s", request_id="r"),
            )
            async with app.run_test(size=(120, 40)) as pilot:
                await pilot.pause(0.05)
                await pilot.press("f2")
                await pilot.press("f2")
                await pilot.press("f2")
                self.assertTrue(latest_snapshot_path(ws).exists())
