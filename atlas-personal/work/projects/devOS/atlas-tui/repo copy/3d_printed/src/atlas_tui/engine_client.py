from __future__ import annotations

import asyncio
import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Optional

from .models import EngineInput, EngineOutput, Workspace


class EngineProtocolError(RuntimeError):
    pass


@dataclass
class EngineStatus:
    connected: bool
    message: str = ""


class EngineClient:
    def __init__(self, cmd: list[str], workspace: Workspace, timeout_s: float = 30.0) -> None:
        self.cmd = cmd
        self.workspace = workspace
        self.timeout_s = timeout_s

        self._proc: Optional[asyncio.subprocess.Process] = None
        self._reader_task: Optional[asyncio.Task] = None
        self._pending: Dict[str, asyncio.Future] = {}
        self.status = EngineStatus(connected=False, message="not started")

    async def start(self) -> None:
        if self._proc and self._proc.returncode is None:
            return

        env = os.environ.copy()
        env["ATLAS_REPO_ROOT"] = self.workspace.repo_root
        if self.workspace.project_root:
            env["ATLAS_PROJECT_ROOT"] = self.workspace.project_root
        src_root = str(Path(__file__).resolve().parents[1])
        existing_pp = env.get("PYTHONPATH", "")
        if existing_pp:
            env["PYTHONPATH"] = src_root + os.pathsep + existing_pp
        else:
            env["PYTHONPATH"] = src_root

        self._proc = await asyncio.create_subprocess_exec(
            *self.cmd,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=self.workspace.repo_root,
            env=env,
        )
        self.status = EngineStatus(connected=True, message="connected")
        self._reader_task = asyncio.create_task(self._read_stdout_loop())
        asyncio.create_task(self._read_stderr_loop())

    async def stop(self) -> None:
        if not self._proc:
            return
        proc = self._proc
        self._proc = None

        if self._reader_task:
            self._reader_task.cancel()
            self._reader_task = None

        for req_id, fut in list(self._pending.items()):
            if not fut.done():
                fut.set_result(RuntimeError("Engine stopped"))
            self._pending.pop(req_id, None)

        try:
            if proc.returncode is None:
                try:
                    proc.terminate()
                except ProcessLookupError:
                    pass
                try:
                    await asyncio.wait_for(proc.wait(), timeout=0.75)
                except asyncio.TimeoutError:
                    try:
                        proc.kill()
                    except ProcessLookupError:
                        pass
                    await proc.wait()
        finally:
            self.status = EngineStatus(connected=False, message="stopped")

    async def submit(self, request_id: str, engine_input: EngineInput) -> EngineOutput:
        await self.start()
        if not self._proc or not self._proc.stdin or not self._proc.stdout:
            raise RuntimeError("Engine process not available.")

        fut: asyncio.Future = asyncio.get_event_loop().create_future()
        self._pending[request_id] = fut

        msg = {"type": "submit", "id": request_id, "payload": engine_input.to_dict()}
        self._proc.stdin.write((json.dumps(msg, ensure_ascii=False) + "\n").encode("utf-8"))
        await self._proc.stdin.drain()

        try:
            result = await asyncio.wait_for(fut, timeout=self.timeout_s)
        except asyncio.TimeoutError:
            self._pending.pop(request_id, None)
            self.status = EngineStatus(connected=True, message="timeout")
            raise RuntimeError(f"Engine request timed out after {self.timeout_s:.0f}s")

        if isinstance(result, Exception):
            raise result
        return EngineOutput.from_dict(result)

    async def _read_stdout_loop(self) -> None:
        assert self._proc and self._proc.stdout
        stdout = self._proc.stdout
        try:
            while True:
                raw = await stdout.readline()
                if not raw:
                    break
                line = raw.decode("utf-8", errors="replace").strip()
                if not line:
                    continue
                try:
                    obj = json.loads(line)
                except json.JSONDecodeError:
                    err = EngineProtocolError(f"Engine emitted non-JSON on stdout: {line[:200]}")
                    for req_id, fut in list(self._pending.items()):
                        if not fut.done():
                            fut.set_result(err)
                        self._pending.pop(req_id, None)
                    self.status = EngineStatus(connected=False, message="protocol error")
                    continue

                if obj.get("type") != "result":
                    continue
                req_id = obj.get("id")
                ok = bool(obj.get("ok"))
                if not req_id:
                    continue
                fut = self._pending.pop(req_id, None)
                if fut is None or fut.done():
                    continue
                if ok:
                    fut.set_result(obj.get("payload") or {})
                else:
                    e = obj.get("error") or {}
                    fut.set_result(RuntimeError(f"Engine error: {e.get('code','error')} - {e.get('message','')}"))
        finally:
            self.status = EngineStatus(connected=False, message="disconnected")
            for req_id, fut in list(self._pending.items()):
                if not fut.done():
                    fut.set_result(RuntimeError("Engine disconnected"))
                self._pending.pop(req_id, None)

    async def _read_stderr_loop(self) -> None:
        if not self._proc or not self._proc.stderr:
            return
        while True:
            raw = await self._proc.stderr.readline()
            if not raw:
                break
            await asyncio.sleep(0)
