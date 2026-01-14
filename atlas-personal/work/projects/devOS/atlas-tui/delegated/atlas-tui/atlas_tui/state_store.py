from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import List, Literal, Optional

ContextProfile = Literal["minimal", "repo", "project", "debug"]

@dataclass
class UIContextPrefs:
    context_profile: ContextProfile = "repo"
    budget_chars: int = 80_000
    pinned_paths: List[str] = None  # repo-relative
    excluded_paths: List[str] = None  # repo-relative

    def __post_init__(self) -> None:
        if self.pinned_paths is None:
            self.pinned_paths = []
        if self.excluded_paths is None:
            self.excluded_paths = []

def state_dir(repo_root: str, project_root: Optional[str]) -> Path:
    if project_root:
        return Path(project_root) / "logs" / "atlas-tui" / "state"
    return Path(repo_root) / ".atlas-tui" / "state"

def prefs_path(repo_root: str, project_root: Optional[str]) -> Path:
    return state_dir(repo_root, project_root) / "ui_state.json"

def load_prefs(repo_root: str, project_root: Optional[str]) -> UIContextPrefs:
    p = prefs_path(repo_root, project_root)
    if not p.exists():
        return UIContextPrefs()
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
        return UIContextPrefs(
            context_profile=data.get("context_profile", "repo"),
            budget_chars=int(data.get("budget_chars", 80_000)),
            pinned_paths=list(data.get("pinned_paths", []) or []),
            excluded_paths=list(data.get("excluded_paths", []) or []),
        )
    except Exception:
        return UIContextPrefs()

def save_prefs(repo_root: str, project_root: Optional[str], prefs: UIContextPrefs) -> Path:
    d = state_dir(repo_root, project_root)
    d.mkdir(parents=True, exist_ok=True)
    p = prefs_path(repo_root, project_root)
    p.write_text(json.dumps(asdict(prefs), ensure_ascii=False, indent=2), encoding="utf-8")
    return p
