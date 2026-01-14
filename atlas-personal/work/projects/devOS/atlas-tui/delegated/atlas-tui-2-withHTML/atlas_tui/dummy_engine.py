from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Tuple

"""Dummy long-lived engine for Atlas TUI v2.

Implements a minimal context selection policy driven by repo-relative hints:
- ui_state.selected_path (repo-relative)
- ui_state.pinned_paths / excluded_paths (repo-relative)
- ui_state.context_profile, ui_state.budget_chars
"""

def _emit(obj: Dict[str, Any]) -> None:
    sys.stdout.write(json.dumps(obj, ensure_ascii=False) + "\n")
    sys.stdout.flush()

def _repo_root(payload: Dict[str, Any]) -> Path:
    ws = payload.get("workspace", {}) or {}
    rr = ws.get("repo_root") or os.environ.get("ATLAS_REPO_ROOT") or "."
    return Path(rr).resolve()

def _norm_rel(p: str) -> str:
    return str(Path(p).as_posix()).lstrip("./")

def _assemble_system(payload: Dict[str, Any], contract_lines: List[str]) -> str:
    mode = payload.get("mode", "interpret")
    ws = payload.get("workspace", {})
    repo_root = ws.get("repo_root", "")
    project_root = ws.get("project_root")

    return "\n".join([
        "Atlas Engine (dummy) — assembled context",
        f"mode: {mode}",
        f"repo_root: {repo_root}",
        f"project_root: {project_root or 'None'}",
        "",
        "Context contract:",
        *contract_lines,
        "",
        "Notes:",
        "- dummy engine; no provider calls",
        "- selection uses repo-relative hints only",
    ])

def _select_artifacts(rr: Path, ui: Dict[str, Any]) -> Tuple[List[Dict[str, Any]], List[str], Dict[str, Any]]:
    selected: List[Dict[str, Any]] = []
    seen = set()

    profile = ui.get("context_profile") or "repo"
    budget_chars = int(ui.get("budget_chars") or 80_000)
    pinned = [_norm_rel(x) for x in (ui.get("pinned_paths") or [])]
    excluded = set(_norm_rel(x) for x in (ui.get("excluded_paths") or []))
    focus = ui.get("selected_path")
    focus = _norm_rel(focus) if isinstance(focus, str) and focus else None

    def add(path_rel: str, reason: str) -> None:
        path_rel = _norm_rel(path_rel)
        if not path_rel or path_rel in excluded or path_rel in seen:
            return
        ab = (rr / path_rel).resolve()
        if not ab.exists() or ab.is_dir():
            return
        try:
            b = ab.stat().st_size
        except Exception:
            b = None
        selected.append({"path": path_rel, "kind": "file", "bytes": b, "role": "context", "reason": reason})
        seen.add(path_rel)

    for p in pinned:
        add(p, "pinned")
    if focus:
        add(focus, "focused")

    if profile == "debug":
        selected.append({"path": "(virtual)/git_status", "kind": "virtual", "bytes": None, "role": "diagnostic", "reason": "profile:debug"})

    est_used = 0
    for it in selected:
        if isinstance(it.get("bytes"), int):
            est_used += int(it["bytes"])

    diag = {"budgets": {"unit": "chars", "target": budget_chars, "estimated_used_bytes": est_used}, "profile": profile}
    contract_lines = [
        f"- profile: {profile}",
        f"- budget_chars: {budget_chars}",
        f"- focused: {focus or '(none)'}",
        f"- pinned: {len(pinned)}",
        f"- excluded: {len(excluded)}",
        f"- selected_artifacts: {len(selected)}",
    ]
    return selected, contract_lines, diag

def main() -> int:
    _emit({"type": "event", "level": "info", "message": "dummy engine started", "ts": time.time()})

    for raw in sys.stdin:
        line = raw.strip()
        if not line:
            continue
        try:
            msg = json.loads(line)
        except json.JSONDecodeError:
            _emit({"type":"event","level":"error","message":"received non-JSON input", "ts": time.time(), "data":{"line": line[:200]}})
            continue

        if msg.get("type") != "submit":
            continue

        req_id = msg.get("id")
        payload = msg.get("payload") or {}
        if not req_id:
            continue

        try:
            user_message = payload.get("user_message", "")
            mode = payload.get("mode", "interpret")
            provider = payload.get("provider", "openai")
            model = payload.get("model", "unknown")

            ui = payload.get("ui_state") or {}
            rr = _repo_root(payload)
            selected_artifacts, contract_lines, budget_diag = _select_artifacts(rr, ui)

            system = _assemble_system(payload, contract_lines)
            provider_request = {
                "provider": provider,
                "model": model,
                "system": system,
                "user": user_message,
                "messages": [
                    {"role": "system", "content": system},
                    {"role": "user", "content": user_message},
                ],
            }

            out = {
                "assembled_context": {"mode": mode, "system": system},
                "provider_request": provider_request,
                "diagnostics": {
                    "sizes": {"system_chars": len(system), "user_chars": len(user_message)},
                    "selected_artifacts": selected_artifacts,
                    "timings_ms": {"assemble": 1},
                    **budget_diag,
                },
            }
            _emit({"type": "result", "id": req_id, "ok": True, "payload": out})
        except Exception as e:
            _emit({"type": "result", "id": req_id, "ok": False, "error": {"code": "exception", "message": str(e), "details": {}}})

    return 0

if __name__ == "__main__":
    raise SystemExit(main())
