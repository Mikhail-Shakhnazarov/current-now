from pathlib import Path
import tempfile
from atlas_tui.workspace import discover_workspace

def test_discover_git_root():
    with tempfile.TemporaryDirectory() as d:
        root = Path(d) / "repo"
        root.mkdir()
        (root / ".git").mkdir()
        sub = root / "a" / "b"
        sub.mkdir(parents=True)
        ws = discover_workspace(sub)
        assert ws.repo_root == str(root.resolve())
        assert ws.project_root is None

def test_discover_wrapper_root():
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
        assert ws.project_root == str(pr.resolve())
        assert ws.repo_root == str((pr / "repo").resolve())
