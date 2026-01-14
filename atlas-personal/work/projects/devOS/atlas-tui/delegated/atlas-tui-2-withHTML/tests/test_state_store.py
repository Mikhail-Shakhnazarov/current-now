from pathlib import Path
import tempfile
from atlas_tui.state_store import load_prefs, save_prefs, UIContextPrefs, write_latest_pointer, latest_pointer_path

def test_state_store_roundtrip_and_latest_pointer():
    with tempfile.TemporaryDirectory() as d:
        rr = Path(d) / "repo"
        rr.mkdir()
        prefs = UIContextPrefs(context_profile="debug", budget_chars=123, pinned_paths=["a.md"], excluded_paths=["b.md"])
        p = save_prefs(str(rr), None, prefs)
        assert p.exists()
        loaded = load_prefs(str(rr), None)
        assert loaded.context_profile == "debug"
        assert loaded.budget_chars == 123

        lp = write_latest_pointer(str(rr), None, str(rr / ".atlas-tui" / "logs" / "assembled" / "x.json"), "rid")
        assert lp == latest_pointer_path(str(rr), None)
