from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

from .models import Workspace
from .ui_events import UIEvent
from .ui_snapshot import UISnapshot
from .workspace import log_base_dir


def ui_dir(workspace: Workspace) -> Path:
    d = log_base_dir(workspace) / "ui"
    d.mkdir(parents=True, exist_ok=True)
    return d


def events_log_path(workspace: Workspace) -> Path:
    return ui_dir(workspace) / "events.jsonl"


def latest_snapshot_path(workspace: Workspace) -> Path:
    return ui_dir(workspace) / "latest_snapshot.json"


def append_ui_event(workspace: Workspace, event: UIEvent) -> Path:
    path = events_log_path(workspace)
    record = event.to_dict()
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")
    return path


def write_latest_snapshot(workspace: Workspace, snapshot: UISnapshot) -> Path:
    path = latest_snapshot_path(workspace)
    record: Dict[str, Any] = snapshot.to_dict()
    path.write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8")
    return path

