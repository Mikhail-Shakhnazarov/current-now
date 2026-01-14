from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

from atlas_tui.engine_client import EngineClient
from atlas_tui.models import EngineInput, Workspace


ENGINE_STUB = r"""
import json, sys, time
for raw in sys.stdin:
    line = raw.strip()
    if not line:
        continue
    try:
        msg = json.loads(line)
    except json.JSONDecodeError:
        continue
    if msg.get("type") != "submit":
        continue
    req_id = msg.get("id")
    payload = msg.get("payload") or {}
    system = "stub-system"
    out = {
        "assembled_context": {"mode": payload.get("mode", "interpret"), "system": system},
        "provider_request": {
            "provider": payload.get("provider", "openai"),
            "model": payload.get("model", "stub-model"),
            "system": system,
            "user": payload.get("user_message", ""),
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": payload.get("user_message", "")},
            ],
        },
        "diagnostics": {"timings_ms": {"assemble": 0}},
    }
    print(json.dumps({"type": "result", "id": req_id, "ok": True, "payload": out}), flush=True)
"""


class TestEngineClientSmoke(unittest.IsolatedAsyncioTestCase):
    async def test_engine_roundtrip(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d) / "repo"
            root.mkdir()
            (root / ".git").mkdir()
            ws = Workspace(repo_root=str(root.resolve()), project_root=None)

            client = EngineClient(
                cmd=[sys.executable, "-u", "-c", ENGINE_STUB],
                workspace=ws,
                timeout_s=5.0,
            )

            inp = EngineInput(
                workspace=ws,
                mode="interpret",
                provider="openai",
                model="stub-model",
                user_message="hello",
                ui_state={"selected_path": "README.md"},
            )
            try:
                out = await client.submit("req-1", inp)
                self.assertEqual(out.assembled_context.system, "stub-system")
                self.assertEqual(out.provider_request.user, "hello")
            finally:
                await client.stop()
