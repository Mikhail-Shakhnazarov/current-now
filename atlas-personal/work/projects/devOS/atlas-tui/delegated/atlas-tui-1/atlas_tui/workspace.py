from __future__ import annotations

from pathlib import Path
from typing import Optional

from .models import Workspace

_WRAPPER_MARKERS = [
    "now.md",
    "specs",
    "logs",
    ".atlas/version",
    "repo",
]

def _has_wrapper_markers(p: Path) -> bool:
    for marker in _WRAPPER_MARKERS:
        if not (p / marker).exists():
            return False
    return True

def _find_upwards(start: Path, predicate) -> Optional[Path]:
    cur = start.resolve()
    for parent in [cur, *cur.parents]:
        try:
            if predicate(parent):
                return parent
        except Exception:
            pass
    return None

def discover_workspace(cwd: Path) -> Workspace:
    cwd = cwd.resolve()

    wrapper_root = _find_upwards(cwd, _has_wrapper_markers)
    if wrapper_root is not None:
        repo_root = (wrapper_root / "repo").resolve()
        return Workspace(repo_root=str(repo_root), project_root=str(wrapper_root))

    git_root = _find_upwards(cwd, lambda p: (p / ".git").exists())
    if git_root is None:
        raise RuntimeError("No managed repo found: could not locate Atlas wrapper or .git root.")
    return Workspace(repo_root=str(git_root), project_root=None)
