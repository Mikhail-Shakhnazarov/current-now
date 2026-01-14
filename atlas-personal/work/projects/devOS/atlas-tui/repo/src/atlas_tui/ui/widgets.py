from __future__ import annotations

import os
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional

from textual.app import ComposeResult
from textual.containers import Vertical
from textual.screen import ModalScreen
from textual.widgets import Static, Markdown

from ..models import Workspace

def _safe_read_text(path: Path, max_bytes: int = 60_000) -> str:
    data = path.read_bytes()
    if b"\x00" in data[:2048]:
        return f"[binary file] {path.name} ({len(data)} bytes)"
    data = data[:max_bytes]
    return data.decode("utf-8", errors="replace")

class StatusBar(Static):
    def __init__(self) -> None:
        super().__init__("")
        self._busy = False
        self._engine_status = "n/a"
        self._last_log = ""
        self._last_action = ""
        self._engine_cmd = ""
        self._chat_log_state = "off"
        self._chat_log_path = ""

    def set_engine_cmd(self, cmd: str) -> None:
        self._engine_cmd = cmd
        self._render()

    def set_engine_status(self, msg: str) -> None:
        self._engine_status = msg or "n/a"
        self._render()

    def set_last_log(self, path: str) -> None:
        self._last_log = path
        self._render()

    def set_busy(self, what: str) -> None:
        self._busy = True
        self._last_action = what
        self._render()

    def set_idle(self, what: str = "") -> None:
        self._busy = False
        self._last_action = what
        self._render()

    def set_chat_log(self, state: str, path: str) -> None:
        self._chat_log_state = state
        self._chat_log_path = path
        self._render()

    def flash(self, msg: str) -> None:
        # lightweight: just set as last action
        self._last_action = msg
        self._render()

    def _render(self) -> None:
        busy = "busy" if self._busy else "idle"
        parts = [
            f"[{busy}]",
            f"engine={self._engine_status}",
            f"chatlog={self._chat_log_state}",
        ]
        if self._last_action:
            parts.append(f"last={self._last_action}")
        if self._last_log:
            parts.append(f"log={self._last_log}")
        self.update(" | ".join(parts))

class InspectionPanel(Static):
    def __init__(self) -> None:
        super().__init__("")
        self.update("No submissions yet.")

    def update_summary(
        self,
        request_id: str,
        log_path: str,
        mode: str,
        provider: str,
        model: str,
        system_len: int,
        system_preview: str,
        diagnostics: Optional[Dict[str, Any]] = None,
    ) -> None:
        diag = diagnostics or {}
        sel = diag.get("selected_artifacts")
        sel_count = len(sel) if isinstance(sel, list) else None
        timings = diag.get("timings_ms") or {}
        assemble_ms = timings.get("assemble")

        lines = [
            "Last assembly",
            f"- request: {request_id}",
            f"- mode/provider/model: {mode} / {provider} / {model}",
            f"- system chars: {system_len}",
        ]
        if sel_count is not None:
            lines.append(f"- selected artifacts: {sel_count}")
        if assemble_ms is not None:
            lines.append(f"- assemble ms: {assemble_ms}")
        lines += [
            f"- log: {log_path}",
            "",
            "Preview:",
            system_preview.replace("\n", "\n"),
        ]
        self.update("\n".join(lines))

class ProjectPanel(Static):
    def __init__(self) -> None:
        super().__init__("")

    async def load(self, workspace: Workspace) -> None:
        if not workspace.project_root:
            self.update("No Atlas wrapper detected.\n\nScaffolding: [stub] (future engine action).")
            return

        pr = Path(workspace.project_root)
        now = pr / "now.md"
        specs = pr / "specs"
        logs = pr / "logs"

        now_preview = ""
        if now.exists():
            now_preview = _safe_read_text(now, max_bytes=6000)
        spec_files = []
        if specs.exists():
            spec_files = sorted([p for p in specs.glob("**/*") if p.is_file()], key=lambda p: p.stat().st_mtime, reverse=True)[:12]
        log_files = []
        if logs.exists():
            log_files = sorted([p for p in logs.glob("**/*") if p.is_file()], key=lambda p: p.stat().st_mtime, reverse=True)[:10]

        def fmt_list(items):
            return "\n".join([f"- {p.relative_to(pr)}" for p in items]) if items else "- (none)"

        text = [
            "Wrapper detected",
            "",
            "now.md (preview):",
            (now_preview[:1200] + ("…\n" if len(now_preview) > 1200 else "")),
            "",
            "specs (recent):",
            fmt_list(spec_files),
            "",
            "logs (recent):",
            fmt_list(log_files),
        ]
        self.update("\n".join(text))

class RepoHealthPanel(Static):
    def __init__(self) -> None:
        super().__init__("")

    async def load(self, workspace: Workspace) -> None:
        rr = Path(workspace.repo_root)
        git = rr / ".git"
        wrapper = "yes" if workspace.project_root else "no"
        dirty = "(unknown)"
        try:
            if git.exists():
                r = subprocess.run(["git", "status", "--porcelain"], cwd=str(rr), capture_output=True, text=True, timeout=1.5)
                dirty = "dirty" if r.stdout.strip() else "clean"
        except Exception:
            dirty = "(error)"

        self.update(
            "\n".join([
                "Health (local)",
                f"- wrapper: {wrapper}",
                f"- git: {'yes' if git.exists() else 'no'}",
                f"- status: {dirty}",
            ])
        )

class HelpOverlay(ModalScreen):
    def __init__(self, app_ref) -> None:
        super().__init__()
        self.app_ref = app_ref

    def compose(self) -> ComposeResult:
        text = """# Atlas TUI — keybindings

- Ctrl+Enter: submit message
- Ctrl+1 / Ctrl+2 / Ctrl+3: focus repo / chat / project
- F5: refresh repo tree
- Ctrl+K: toggle this help
- Ctrl+L: toggle chat transcript logging
- Ctrl+R: restart engine child
- Esc: close / return focus

Notes:
- v2 does not call providers and does not modify repo files.
- Inspection logs are written on every submit (see status bar for last path).
"""
        yield Markdown(text)

class FilePreviewScreen(ModalScreen):
    def __init__(self, path: Path) -> None:
        super().__init__()
        self.path = path

    def compose(self) -> ComposeResult:
        content = ""
        try:
            content = _safe_read_text(self.path, max_bytes=120_000)
        except Exception as e:
            content = f"Failed to read {self.path}: {e}"
        yield Markdown(f"# Preview\n\n**{self.path}**\n\n```\n{content}\n```")
