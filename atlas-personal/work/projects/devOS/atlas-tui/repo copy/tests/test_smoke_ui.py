from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

from atlas_tui.models import Workspace
from atlas_tui.ui.app import AtlasTUIApp


def _make_temp_workspace() -> tuple[Workspace, tempfile.TemporaryDirectory]:
    d = tempfile.TemporaryDirectory()
    root = Path(d.name) / "repo"
    root.mkdir(parents=True)
    (root / ".git").mkdir()
    (root / "README.md").write_text("hello", encoding="utf-8")
    ws = Workspace(repo_root=str(root.resolve()), project_root=None)
    # Caller must keep `d` alive.
    return ws, d


def _dump_app(app: AtlasTUIApp) -> str:
    focused = getattr(getattr(app, "focused", None), "id", None)
    try:
        stack = [type(s).__name__ for s in app.screen_stack]
    except Exception:
        stack = ["(unavailable)"]
    return "\n".join(
        [
            f"focused={focused!r}",
            f"screen_stack={stack!r}",
            f"focused_panel={app._focused_panel_name()!r}",
        ]
    )


class TestUISmoke(unittest.IsolatedAsyncioTestCase):
    async def test_help_overlay_open_close(self) -> None:
        ws, tmp = _make_temp_workspace()
        app = AtlasTUIApp(
            workspace=ws,
            engine_cmd=[sys.executable, "-c", "raise SystemExit(0)"],
            engine_cmd_str="(unused)",
        )

        with tmp:
            async with app.run_test(size=(120, 40)) as pilot:
                await pilot.press("f1")
                self.assertGreater(
                    len(app.screen_stack),
                    1,
                    msg="Help overlay did not open\n" + _dump_app(app),
                )
                await pilot.press("escape")
                self.assertEqual(
                    len(app.screen_stack),
                    1,
                    msg="Help overlay did not close\n" + _dump_app(app),
                )

    async def test_escape_opens_and_cancels_quit_confirm(self) -> None:
        ws, tmp = _make_temp_workspace()
        app = AtlasTUIApp(
            workspace=ws,
            engine_cmd=[sys.executable, "-c", "raise SystemExit(0)"],
            engine_cmd_str="(unused)",
        )

        with tmp:
            async with app.run_test(size=(120, 40)) as pilot:
                await pilot.press("escape")
                self.assertGreater(
                    len(app.screen_stack),
                    1,
                    msg="Quit confirm did not open\n" + _dump_app(app),
                )
                await pilot.press("escape")
                self.assertEqual(
                    len(app.screen_stack),
                    1,
                    msg="Quit confirm did not cancel/close\n" + _dump_app(app),
                )

    async def test_focus_cycle(self) -> None:
        ws, tmp = _make_temp_workspace()
        app = AtlasTUIApp(
            workspace=ws,
            engine_cmd=[sys.executable, "-c", "raise SystemExit(0)"],
            engine_cmd_str="(unused)",
        )

        with tmp:
            async with app.run_test(size=(120, 40)) as pilot:
                # Let on_mount/on_ready settle.
                await pilot.pause(0.05)

                self.assertEqual(app._focused_panel_name(), "chat", msg=_dump_app(app))

                await pilot.press("f2")
                self.assertEqual(app._focused_panel_name(), "project", msg=_dump_app(app))

                await pilot.press("f2")
                self.assertEqual(app._focused_panel_name(), "repo", msg=_dump_app(app))

                await pilot.press("f2")
                self.assertEqual(app._focused_panel_name(), "chat", msg=_dump_app(app))
