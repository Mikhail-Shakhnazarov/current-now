from __future__ import annotations

import json
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

from .models import EngineInput, EngineOutput, Workspace
from .state_store import write_latest_pointer

DEFAULT_PREVIEW_CHARS = 800
DEFAULT_MAX_STORED_SYSTEM_CHARS = None  # set to int to hard-cap stored system fields (optional)

def log_base_dir(workspace: Workspace) -> Path:
    if workspace.project_root:
        return Path(workspace.project_root) / "logs" / "atlas-tui"
    return Path(workspace.repo_root) / ".atlas-tui" / "logs"

def _truncate(s: str, n: int) -> Dict[str, Any]:
    if n <= 0:
        return {"text": "", "truncated": len(s) > 0, "full_length": len(s)}
    if len(s) <= n:
        return {"text": s, "truncated": False, "full_length": len(s)}
    return {"text": s[:n], "truncated": True, "full_length": len(s)}

def write_assembled_log(
    workspace: Workspace,
    request_id: str,
    engine_input: EngineInput,
    engine_output: EngineOutput,
    preview_chars: int = DEFAULT_PREVIEW_CHARS,
    max_stored_system_chars: Optional[int] = DEFAULT_MAX_STORED_SYSTEM_CHARS,
) -> Path:
    """Write a deterministic inspection log record and update the 'latest.json' pointer.

    - wrapper: project_root/logs/atlas-tui/assembled/
    - no wrapper: repo_root/.atlas-tui/logs/assembled/
    """
    ts = datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")
    base_dir = log_base_dir(workspace) / "assembled"
    base_dir.mkdir(parents=True, exist_ok=True)

    assembled_system_full = engine_output.assembled_context.system
    provider_system_full = engine_output.provider_request.system

    assembled_system = assembled_system_full
    provider_system = provider_system_full
    if max_stored_system_chars is not None:
        if len(assembled_system) > max_stored_system_chars:
            assembled_system = assembled_system[:max_stored_system_chars]
        if len(provider_system) > max_stored_system_chars:
            provider_system = provider_system[:max_stored_system_chars]

    payload: Dict[str, Any] = {
        "ts": ts,
        "request_id": request_id,
        "workspace": asdict(workspace),
        "mode": engine_input.mode,
        "provider": engine_input.provider,
        "model": engine_input.model,
        "user_message": engine_input.user_message,
        "ui_state": engine_input.ui_state,
        "assembled_context": {
            "mode": engine_output.assembled_context.mode,
            "system_length_chars": len(assembled_system_full),
            "system_preview": _truncate(assembled_system_full, preview_chars),
            "system_stored_truncated": max_stored_system_chars is not None and len(assembled_system_full) > max_stored_system_chars,
            "system": assembled_system,
        },
        "provider_request": {
            "provider": engine_output.provider_request.provider,
            "model": engine_output.provider_request.model,
            "system_length_chars": len(provider_system_full),
            "system_preview": _truncate(provider_system_full, preview_chars),
            "system_stored_truncated": max_stored_system_chars is not None and len(provider_system_full) > max_stored_system_chars,
            "system": provider_system,
            "user": engine_output.provider_request.user,
            "messages": engine_output.provider_request.messages,
        },
        "diagnostics": engine_output.diagnostics,
    }

    fname = datetime.now().strftime("%Y%m%d_%H%M%S") + f"_{request_id}.json"
    path = base_dir / fname
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    # Update pointer for the web "glass" inspector.
    try:
        write_latest_pointer(workspace.repo_root, workspace.project_root, str(path), request_id)
    except Exception:
        pass

    return path

def write_chat_log(workspace: Workspace, session_id: str, entry: Dict[str, Any]) -> Path:
    base_dir = log_base_dir(workspace) / "chat"
    base_dir.mkdir(parents=True, exist_ok=True)
    path = base_dir / f"{session_id}.jsonl"
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    return path
