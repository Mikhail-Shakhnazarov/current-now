from __future__ import annotations

import json
import sys
import time
from typing import Any, Dict, List

from atlas_tui.assets import atlas_docs_root

"""Long-lived engine (v2) for Atlas TUI.

Reads JSONL from stdin and writes JSONL to stdout.

This engine does not call model provider APIs. It assembles the concrete provider
request payload (system + user + model/provider metadata) so that the TUI can
log and inspect context packs deterministically.

Protocol:
- submit: {"type":"submit","id":"...","payload": EngineInput}
- result: {"type":"result","id":"...","ok":true,"payload": EngineOutput}
"""

def _emit(obj: Dict[str, Any]) -> None:
    sys.stdout.write(json.dumps(obj, ensure_ascii=False) + "\n")
    sys.stdout.flush()

def _read_text(rel_parts: List[str]) -> str:
    root = atlas_docs_root()
    p = root
    for part in rel_parts:
        p = p.joinpath(part)
    return p.read_text(encoding="utf-8")


def _assemble_system(mode: str) -> str:
    kernel = _read_text(["core", "kernel.md"])

    if mode == "interpret":
        protocol = _read_text(["protocols", "interpreter-opencode.md"])
        projection = _read_text(["projections", "interpret-opencode.md"])
    elif mode == "execute":
        protocol = _read_text(["protocols", "executor-opencode.md"])
        projection = _read_text(["projections", "execute-opencode.md"])
    else:
        protocol = _read_text(["protocols", "plan-opencode.md"])
        projection = _read_text(["projections", "plan-opencode.md"])

    return "\n\n".join([kernel, protocol, projection])

def main() -> int:
    # Optional startup event
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
            mode = str(payload.get("mode", "interpret"))
            provider = payload.get("provider", "openai")
            model = payload.get("model", "unknown")

            system = _assemble_system(mode)
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
                    "sizes": {
                        "system_chars": len(system),
                        "user_chars": len(user_message),
                    },
                    "selected_artifacts": [
                        "atlas_tui.assets:atlas/core/kernel.md",
                        f"atlas_tui.assets:atlas/protocols/{'executor-opencode.md' if mode == 'execute' else ('interpreter-opencode.md' if mode == 'interpret' else 'plan-opencode.md')}",
                        f"atlas_tui.assets:atlas/projections/{'execute-opencode.md' if mode == 'execute' else ('interpret-opencode.md' if mode == 'interpret' else 'plan-opencode.md')}",
                    ],
                    "timings_ms": {"assemble": 1},
                },
            }

            _emit({"type": "result", "id": req_id, "ok": True, "payload": out})
        except Exception as e:
            _emit({"type": "result", "id": req_id, "ok": False, "error": {"code": "exception", "message": str(e), "details": {}}})

    return 0

if __name__ == "__main__":
    raise SystemExit(main())
