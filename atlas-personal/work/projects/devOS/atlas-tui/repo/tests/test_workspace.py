from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from atlas_tui.workspace import discover_workspace


class TestWorkspaceDiscovery(unittest.TestCase):
    def test_discover_git_root(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d) / "repo"
            root.mkdir()
            (root / ".git").mkdir()
            sub = root / "a" / "b"
            sub.mkdir(parents=True)
            ws = discover_workspace(sub)
            self.assertEqual(ws.repo_root, str(root.resolve()))
            self.assertIsNone(ws.project_root)

    def test_discover_wrapper_root(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            pr = Path(d) / "proj"
            pr.mkdir()
            (pr / "now.md").write_text("now", encoding="utf-8")
            (pr / "specs").mkdir()
            (pr / "logs").mkdir()
            (pr / ".atlas").mkdir()
            (pr / ".atlas" / "version").write_text("1", encoding="utf-8")
            (pr / "repo").mkdir()
            (pr / "repo" / ".git").mkdir()
            sub = pr / "repo" / "x"
            sub.mkdir()
            ws = discover_workspace(sub)
            self.assertEqual(ws.project_root, str(pr.resolve()))
            self.assertEqual(ws.repo_root, str((pr / "repo").resolve()))
