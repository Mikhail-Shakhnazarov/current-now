from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Literal, Optional

ContextProfile = Literal["minimal", "repo", "project", "debug"]


@dataclass
class UIContextPrefs:
    """UI-owned context hints (repo-relative paths everywhere)."""

    context_profile: ContextProfile = "repo"
    budget_chars: int = 80_000
    pinned_paths: list[str] = field(default_factory=list)
    excluded_paths: list[str] = field(default_factory=list)


def state_dir(repo_root: str, project_root: Optional[str]) -> Path:
    if project_root:
        return Path(project_root) / "logs" / "atlas-tui" / "state"
    return Path(repo_root) / ".atlas-tui" / "state"


def prefs_path(repo_root: str, project_root: Optional[str]) -> Path:
    return state_dir(repo_root, project_root) / "ui_state.json"


def latest_pointer_path(repo_root: str, project_root: Optional[str]) -> Path:
    return state_dir(repo_root, project_root) / "latest.json"


def load_prefs(repo_root: str, project_root: Optional[str]) -> UIContextPrefs:
    path = prefs_path(repo_root, project_root)
    if not path.exists():
        return UIContextPrefs()
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return UIContextPrefs(
            context_profile=data.get("context_profile", "repo"),
            budget_chars=int(data.get("budget_chars", 80_000)),
            pinned_paths=list(data.get("pinned_paths", []) or []),
            excluded_paths=list(data.get("excluded_paths", []) or []),
        )
    except Exception:
        return UIContextPrefs()


def save_prefs(repo_root: str, project_root: Optional[str], prefs: UIContextPrefs) -> Path:
    directory = state_dir(repo_root, project_root)
    directory.mkdir(parents=True, exist_ok=True)
    path = prefs_path(repo_root, project_root)
    path.write_text(json.dumps(asdict(prefs), ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def write_latest_pointer(repo_root: str, project_root: Optional[str], log_path: str, request_id: str) -> Path:
    directory = state_dir(repo_root, project_root)
    directory.mkdir(parents=True, exist_ok=True)
    path = latest_pointer_path(repo_root, project_root)
    payload = {
        "last_log_path": log_path,
        "request_id": request_id,
        "updated_ts": __import__("datetime").datetime.now(__import__("datetime").timezone.utc)
        .astimezone()
        .isoformat(timespec="seconds"),
    }
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return path

