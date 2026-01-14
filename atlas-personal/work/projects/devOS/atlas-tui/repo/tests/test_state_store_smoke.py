from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from atlas_tui.state_store import UIContextPrefs, load_prefs, save_prefs, write_latest_pointer


class TestStateStoreSmoke(unittest.TestCase):
    def test_prefs_roundtrip(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            repo = Path(d) / "repo"
            repo.mkdir()
            prefs = UIContextPrefs(
                context_profile="debug",
                budget_chars=123,
                pinned_paths=["a/b.txt"],
                excluded_paths=["c/d.txt"],
            )
            path = save_prefs(str(repo), None, prefs)
            self.assertTrue(path.exists())
            loaded = load_prefs(str(repo), None)
            self.assertEqual(loaded.context_profile, "debug")
            self.assertEqual(loaded.budget_chars, 123)
            self.assertEqual(loaded.pinned_paths, ["a/b.txt"])
            self.assertEqual(loaded.excluded_paths, ["c/d.txt"])

    def test_latest_pointer_written(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            repo = Path(d) / "repo"
            repo.mkdir()
            lp = write_latest_pointer(str(repo), None, log_path="x.json", request_id="rid")
            self.assertTrue(lp.exists())
            text = lp.read_text(encoding="utf-8")
            self.assertIn("\"last_log_path\": \"x.json\"", text)
            self.assertIn("\"request_id\": \"rid\"", text)

