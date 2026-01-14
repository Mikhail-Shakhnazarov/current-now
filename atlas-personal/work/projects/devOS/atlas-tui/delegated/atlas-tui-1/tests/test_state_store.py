from pathlib import Path
import tempfile
from atlas_tui.state_store import load_prefs, save_prefs, UIContextPrefs

def test_state_store_roundtrip_no_wrapper():
    with tempfile.TemporaryDirectory() as d:
        rr = Path(d) / "repo"
        rr.mkdir()
        prefs = UIContextPrefs(context_profile="debug", budget_chars=123, pinned_paths=["a.md"], excluded_paths=["b.md"])
        p = save_prefs(str(rr), None, prefs)
        assert p.exists()
        loaded = load_prefs(str(rr), None)
        assert loaded.context_profile == "debug"
        assert loaded.budget_chars == 123
        assert loaded.pinned_paths == ["a.md"]
        assert loaded.excluded_paths == ["b.md"]
