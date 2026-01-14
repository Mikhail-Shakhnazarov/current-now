from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import List, Literal, Optional

ContextProfile = Literal["minimal", "repo", "project", "debug"]

@dataclass
class UIContextPrefs:
    """UI-owned context hints (repo-relative paths everywhere)."""
    context_profile: ContextProfile = "repo"
    budget_chars: int = 80_000
    pinned_paths: List[str] = None
    excluded_paths: List[str] = None

    def __post_init__(self) -> None:
        if self.pinned_paths is None:
            self.pinned_paths = []
        if self.excluded_paths is None:
            self.excluded_paths = []

def state_dir(repo_root: str, project_root: Optional[str]) -> Path:
    """State lives outside the managed repo when a wrapper exists, else under repo_root/.atlas-tui/state."""
    if project_root:
        return Path(project_root) / "logs" / "atlas-tui" / "state"
    return Path(repo_root) / ".atlas-tui" / "state"

def prefs_path(repo_root: str, project_root: Optional[str]) -> Path:
    return state_dir(repo_root, project_root) / "ui_state.json"

def latest_pointer_path(repo_root: str, project_root: Optional[str]) -> Path:
    return state_dir(repo_root, project_root) / "latest.json"

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

def write_latest_pointer(repo_root: str, project_root: Optional[str], log_path: str, request_id: str) -> Path:
    d = state_dir(repo_root, project_root)
    d.mkdir(parents=True, exist_ok=True)
    p = latest_pointer_path(repo_root, project_root)
    payload = {
        "last_log_path": log_path,
        "request_id": request_id,
        "updated_ts": __import__("datetime").datetime.now(__import__("datetime").timezone.utc).astimezone().isoformat(timespec="seconds"),
    }
    p.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return p
