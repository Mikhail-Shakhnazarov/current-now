from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path
from typing import Any, Dict, Optional

from .determinism import Clock, RealClock
from .models import EngineInput, EngineOutput, Workspace
from .state_store import write_latest_pointer
from .ui_events import glass_pointer_updated, log_written
from .ui_observability import append_ui_event
from .workspace import log_base_dir, rel_to_project_root


def assembled_dir(workspace: Workspace) -> Path:
    d = log_base_dir(workspace) / "assembled"
    d.mkdir(parents=True, exist_ok=True)
    return d


def write_assembled_log(
    *,
    workspace: Workspace,
    request_id: str,
    engine_input: EngineInput,
    engine_output: EngineOutput,
    session_id: str,
    clock: Optional[Clock] = None,
) -> Path:
    clock = clock or RealClock()
    ts = clock.now_iso()

    path = assembled_dir(workspace) / f"{request_id}.json"
    payload: Dict[str, Any] = {
        "schema_version": 1,
        "ts": ts,
        "request_id": request_id,
        "workspace": asdict(workspace),
        "mode": engine_input.mode,
        "provider": engine_input.provider,
        "model": engine_input.model,
        "user_message": engine_input.user_message,
        "ui_state": engine_input.ui_state,
        "selected_artifacts": list(engine_output.assembled_context.selected_artifacts),
        "assembled_context": {
            "mode": engine_output.assembled_context.mode,
            "system_length_chars": len(engine_output.assembled_context.system),
            "system": engine_output.assembled_context.system,
        },
        "diagnostics": engine_output.diagnostics,
    }
    b = json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8")
    path.write_bytes(b)

    write_latest_pointer(workspace, path, request_id, updated_ts=ts)

    rel = rel_to_project_root(workspace, path)
    append_ui_event(workspace, log_written(session_id, rel, len(b), clock=clock))
    append_ui_event(workspace, glass_pointer_updated(session_id, rel, clock=clock))
    return path
