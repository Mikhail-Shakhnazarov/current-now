from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Literal

from .models import Workspace
from .workspace import log_base_dir, rel_to_project_root, resolve_project_path

ContextProfile = Literal["minimal", "repo", "project", "debug"]


@dataclass
class UIContextPrefs:
    context_profile: ContextProfile = "repo"
    budget_chars: int = 80_000
    pinned_paths: list[str] = field(default_factory=list)
    excluded_paths: list[str] = field(default_factory=list)


def state_dir(workspace: Workspace) -> Path:
    d = log_base_dir(workspace) / "state"
    d.mkdir(parents=True, exist_ok=True)
    return d


def prefs_path(workspace: Workspace) -> Path:
    return state_dir(workspace) / "ui_state.json"


def latest_pointer_path(workspace: Workspace) -> Path:
    return state_dir(workspace) / "latest.json"


def load_prefs(workspace: Workspace) -> UIContextPrefs:
    path = prefs_path(workspace)
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


def save_prefs(workspace: Workspace, prefs: UIContextPrefs) -> Path:
    path = prefs_path(workspace)
    path.write_text(json.dumps(asdict(prefs), ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def write_latest_pointer(workspace: Workspace, assembled_log_path: Path, request_id: str, updated_ts: str) -> Path:
    path = latest_pointer_path(workspace)
    payload = {
        "last_log_path": rel_to_project_root(workspace, assembled_log_path),
        "request_id": request_id,
        "updated_ts": updated_ts,
    }
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def resolve_latest_log_path(workspace: Workspace, last_log_path: str) -> Path:
    if last_log_path.startswith("logs/") or last_log_path.startswith("logs\\"):
        return resolve_project_path(workspace, last_log_path)
    return resolve_project_path(workspace, last_log_path)

