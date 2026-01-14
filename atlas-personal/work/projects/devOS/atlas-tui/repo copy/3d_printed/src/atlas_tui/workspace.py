from __future__ import annotations

from dataclasses import asdict
from pathlib import Path
from typing import Any, Dict

from .models import Workspace


def ensure_project_root(workspace: Workspace) -> Path:
    if workspace.project_root:
        return Path(workspace.project_root)
    return Path(workspace.repo_root)


def repo_relative_path(repo_root: str, path: str) -> str:
    try:
        rel = str(Path(path).resolve().relative_to(Path(repo_root).resolve()))
        return rel.replace("\\", "/")
    except Exception:
        return str(Path(path)).replace("\\", "/")


def workspace_dict(workspace: Workspace) -> Dict[str, Any]:
    return asdict(workspace)


def log_base_dir(workspace: Workspace) -> Path:
    base = ensure_project_root(workspace) / "logs" / "atlas-tui"
    base.mkdir(parents=True, exist_ok=True)
    return base


def resolve_project_path(workspace: Workspace, rel: str) -> Path:
    return ensure_project_root(workspace) / Path(rel)


def rel_to_project_root(workspace: Workspace, path: Path) -> str:
    try:
        rel = str(path.resolve().relative_to(ensure_project_root(workspace).resolve()))
    except Exception:
        rel = str(path)
    return rel.replace("\\", "/")

