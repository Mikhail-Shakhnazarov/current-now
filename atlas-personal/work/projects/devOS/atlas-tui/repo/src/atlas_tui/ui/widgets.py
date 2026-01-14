from __future__ import annotations

import os
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional

from textual import events
from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Input, Markdown, Select, Static, TextArea

from ..models import Workspace
from ..state_store import UIContextPrefs

def _safe_read_text(path: Path, max_bytes: int = 60_000) -> str:
    data = path.read_bytes()
    if b"\x00" in data[:2048]:
        return f"[binary file] {path.name} ({len(data)} bytes)"
    data = data[:max_bytes]
    return data.decode("utf-8", errors="replace")

class ChatComposer(TextArea):
    """Message composer that supports chat-style submit.

    - Enter: submit message
    - Shift+Enter: newline

    This is implemented here because TextArea may consume Ctrl+* keys and prevent
    app-level bindings from firing (terminal + Textual version dependent).
    """

    async def on_key(self, event: events.Key) -> None:
        key = event.key

        if key == "enter":
            await self.app.action_submit()  # type: ignore[attr-defined]
            event.stop()
            return

        if key == "f2":
            await self.app.action_focus_cycle()  # type: ignore[attr-defined]
            event.stop()
            return

        if key == "f1":
            await self.app.action_toggle_help()  # type: ignore[attr-defined]
            event.stop()
            return

        if key in {"escape", "esc"}:
            await self.app.action_escape()  # type: ignore[attr-defined]
            event.stop()
            return

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
        self._glass_state = "off"
        self._glass_url = ""
        self._details_visible = False

    def set_engine_cmd(self, cmd: str) -> None:
        self._engine_cmd = cmd
        self._refresh()

    def set_engine_status(self, msg: str) -> None:
        self._engine_status = msg or "n/a"
        self._refresh()

    def set_last_log(self, path: str) -> None:
        self._last_log = path
        self._refresh()

    def set_busy(self, what: str) -> None:
        self._busy = True
        self._last_action = what
        self._refresh()

    def set_idle(self, what: str = "") -> None:
        self._busy = False
        self._last_action = what
        self._refresh()

    def set_chat_log(self, state: str, path: str) -> None:
        self._chat_log_state = state
        self._chat_log_path = path
        self._refresh()

    def set_glass(self, state: str, url: str = "") -> None:
        self._glass_state = state
        self._glass_url = url
        self._refresh()

    def set_details_visible(self, visible: bool) -> None:
        self._details_visible = visible
        self._refresh()

    def flash(self, msg: str) -> None:
        # lightweight: just set as last action
        self._last_action = msg
        self._refresh()

    def _refresh(self) -> None:
        busy = "busy" if self._busy else "idle"
        parts = [
            f"[{busy}]",
            f"engine={self._engine_status}",
            f"glass={self._glass_state}",
            f"chatlog={self._chat_log_state}",
        ]
        if self._details_visible:
            if self._glass_url:
                parts.append(f"glass_url={self._glass_url}")
            if self._last_action:
                parts.append(f"last={self._last_action}")
            if self._last_log:
                parts.append(f"log={self._last_log}")
        self.update(" | ".join(parts))

class InspectionPanel(Static):
    can_focus = True

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
            f"request: {request_id}",
            f"{mode} / {provider} / {model}",
            f"system_chars: {system_len}",
        ]
        if sel_count is not None:
            lines.append(f"selected_artifacts: {sel_count}")
        if assemble_ms is not None:
            lines.append(f"assemble_ms: {assemble_ms}")
        lines += [
            f"log: {log_path}",
            "",
            "Preview (truncated):",
            system_preview.replace("\n", "\n"),
        ]
        self.update("\n".join(lines))

class ProjectPanel(Static):
    can_focus = True

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
        preview_lines = now_preview.splitlines()
        max_lines = 28
        truncated = len(preview_lines) > max_lines
        preview_text = "\n".join(preview_lines[:max_lines])
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
            (preview_text + ("\n... (truncated; open now.md for full view)" if truncated else "")),
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
    BINDINGS = [
        ("escape", "close", "Close"),
        ("esc", "close", "Close"),
        ("f1", "close", "Close"),
    ]

    def __init__(self, app_ref) -> None:
        super().__init__()
        self.app_ref = app_ref

    def action_close(self) -> None:
        self.dismiss(None)

    def compose(self) -> ComposeResult:
        text = """# Atlas TUI - keybindings

 - Enter: submit message (in composer)
 - Shift+Enter: newline (in composer)
 - F1: toggle help
 - F2: cycle focus (repo > chat > project)
 - Ctrl+C: force quit (no confirmation)
 - Esc: close modal or quit (with confirmation) if no modal

Notes:
- v2 does not call providers and does not modify repo files.
- Inspection logs are written on every submit (see status bar for last path).
 - Other actions are available via top-bar buttons (Refresh, Chat Log, Details, Prefs, Restart, Quit).
"""
        yield Markdown(text)

class FilePreviewScreen(ModalScreen):
    BINDINGS = [
        ("escape", "close", "Close"),
        ("q", "close", "Close"),
    ]

    def __init__(self, path: Path) -> None:
        super().__init__()
        self.path = path

    def action_close(self) -> None:
        self.dismiss(None)

    def compose(self) -> ComposeResult:
        content = ""
        try:
            content = _safe_read_text(self.path, max_bytes=120_000)
        except Exception as e:
            content = f"Failed to read {self.path}: {e}"
        yield Markdown(
            f"# Preview\n\n**{self.path}**\n\nPress Esc or q to close.\n\n```\n{content}\n```"
        )


class ContextPrefsScreen(ModalScreen[Optional[UIContextPrefs]]):
    BINDINGS = [
        ("escape", "cancel", "Cancel"),
    ]

    def __init__(self, prefs: UIContextPrefs) -> None:
        super().__init__()
        self._prefs = UIContextPrefs(
            context_profile=prefs.context_profile,
            budget_chars=prefs.budget_chars,
            pinned_paths=list(prefs.pinned_paths),
            excluded_paths=list(prefs.excluded_paths),
        )

    def action_cancel(self) -> None:
        self.dismiss(None)

    def compose(self) -> ComposeResult:
        yield Markdown("# Context prefs (repo-relative paths)")

        self.profile_select = Select([(p, p) for p in ["minimal", "repo", "project", "debug"]], value=self._prefs.context_profile)
        yield Static("Profile:")
        yield self.profile_select

        self.budget_input = Input(value=str(self._prefs.budget_chars), placeholder="budget chars")
        yield Static("Budget (chars):")
        yield self.budget_input

        self.pins_area = TextArea()
        self.pins_area.text = "\n".join(self._prefs.pinned_paths)
        self.pins_area.placeholder = "Pinned paths (one per line, repo-relative)"
        yield Static("Pinned:")
        yield self.pins_area

        self.excl_area = TextArea()
        self.excl_area.text = "\n".join(self._prefs.excluded_paths)
        self.excl_area.placeholder = "Excluded paths (one per line, repo-relative)"
        yield Static("Excluded:")
        yield self.excl_area

        with Horizontal():
            yield Button("Save", id="ctx_save", variant="primary")
            yield Button("Cancel", id="ctx_cancel")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "ctx_cancel":
            self.dismiss(None)
            return

        prof = self.profile_select.value or "repo"
        try:
            budget = int((self.budget_input.value or "").strip())
        except Exception:
            budget = self._prefs.budget_chars

        pins = [p.strip() for p in (self.pins_area.text or "").splitlines() if p.strip()]
        excl = [p.strip() for p in (self.excl_area.text or "").splitlines() if p.strip()]

        self._prefs.context_profile = prof  # type: ignore[assignment]
        self._prefs.budget_chars = budget
        self._prefs.pinned_paths = pins
        self._prefs.excluded_paths = excl

        self.dismiss(self._prefs)


class QuitConfirmScreen(ModalScreen[bool]):
    BINDINGS = [
        ("escape", "cancel", "Cancel"),
        ("esc", "cancel", "Cancel"),
    ]

    def action_cancel(self) -> None:
        self.dismiss(False)

    def compose(self) -> ComposeResult:
        yield Markdown("## Quit\n\nSure you want to quit?")
        with Horizontal():
            yield Button("Quit", id="quit_yes", variant="error")
            yield Button("Cancel", id="quit_no")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "quit_yes":
            self.dismiss(True)
            return
        self.dismiss(False)
