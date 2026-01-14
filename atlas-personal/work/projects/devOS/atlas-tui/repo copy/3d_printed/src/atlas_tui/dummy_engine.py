from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List


def _repo_root() -> Path:
    return Path(os.environ.get("ATLAS_REPO_ROOT") or os.getcwd())


def _selected_artifacts(repo_root: Path) -> List[str]:
    candidates = ["README.md", "now.md", "pyproject.toml"]
    out: List[str] = []
    for c in candidates:
        p = repo_root / c
        if p.exists():
            out.append(c)
    if not out:
        out.append(".")
    return out


def _handle_submit(req_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    user_message = (payload.get("user_message") or "").strip()
    mode = payload.get("mode") or "interpret"
    provider = payload.get("provider") or "dummy"
    model = payload.get("model") or "dummy"
    repo_root = _repo_root()
    selected = _selected_artifacts(repo_root)

    system = "\n".join(
        [
            "ATLAS_TUI_DUMMY_ENGINE v1",
            f"mode={mode}",
            f"selected_artifacts={selected}",
            "user_message:",
            user_message,
        ]
    )

    return {
        "assembled_context": {"mode": mode, "system": system, "selected_artifacts": selected},
        "provider_request": {"provider": provider, "model": model, "system": system, "user": user_message, "messages": []},
        "diagnostics": {"engine": "dummy", "request_id": req_id},
    }


def main() -> None:
    for raw in sys.stdin:
        line = raw.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
        except json.JSONDecodeError:
            continue
        if obj.get("type") != "submit":
            continue
        req_id = obj.get("id") or ""
        payload = obj.get("payload") or {}
        try:
            out = _handle_submit(req_id, payload)
            resp = {"type": "result", "id": req_id, "ok": True, "payload": out}
        except Exception as e:
            resp = {"type": "result", "id": req_id, "ok": False, "error": {"code": "error", "message": str(e)}}
        sys.stdout.write(json.dumps(resp, ensure_ascii=False) + "\n")
        sys.stdout.flush()


if __name__ == "__main__":
    main()

