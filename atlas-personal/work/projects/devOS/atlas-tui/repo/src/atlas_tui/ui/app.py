from __future__ import annotations

import asyncio
import os
import uuid
from dataclasses import asdict
from pathlib import Path
from typing import Optional

from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import DirectoryTree, Footer, Header, Static, TextArea, Select
from textual import on
from textual.message import Message
from textual.screen import ModalScreen

from ..models import EngineInput, Mode, Provider, Workspace
from ..engine_client import EngineClient
from ..log_writer import write_assembled_log, write_chat_log, log_base_dir
from ..workspace import discover_workspace
from .widgets import StatusBar, InspectionPanel, ProjectPanel, HelpOverlay, FilePreviewScreen, RepoHealthPanel

DEFAULT_MODE: Mode = "interpret"
DEFAULT_PROVIDER: Provider = "openai"
DEFAULT_MODELS = {
    "openai": ["gpt-4.1-mini", "gpt-4.1", "gpt-4o-mini"],
    "anthropic": ["claude-3.5-sonnet", "claude-3.5-haiku"],
}

class AtlasTUIApp(App):
    CSS = """
    Screen {
        layout: vertical;
    }

    #topbar {
        height: 3;
    }

    #main {
        height: 1fr;
    }

    #left, #center, #right {
        width: 1fr;
        border: solid $primary;
    }

    #left { width: 34%; }
    #center { width: 42%; }
    #right { width: 24%; }

    #composer {
        height: 6;
    }

    .panel-title {
        background: $panel;
        padding: 0 1;
        text-style: bold;
    }

    .section {
        border-top: solid $primary;
    }
    """

    BINDINGS = [
        ("ctrl+enter", "submit", "Submit"),
        ("ctrl+1", "focus_repo", "Focus repo"),
        ("ctrl+2", "focus_chat", "Focus chat"),
        ("ctrl+3", "focus_project", "Focus project"),
        ("f5", "refresh_tree", "Refresh tree"),
        ("ctrl+k", "toggle_help", "Help"),
        ("ctrl+l", "toggle_chat_log", "Toggle chat log"),
        ("ctrl+r", "restart_engine", "Restart engine"),
        ("escape", "escape", "Close/Back"),
    ]

    def __init__(
        self,
        workspace: Workspace,
        engine_cmd: list[str],
        engine_cmd_str: str,
        preview_chars: int = 800,
        engine_timeout_s: float = 60.0,
    ) -> None:
        super().__init__()
        self.workspace = workspace
        self.engine_cmd = engine_cmd
        self.engine_cmd_str = engine_cmd_str
        self.preview_chars = preview_chars
        self.engine_timeout_s = engine_timeout_s

        self.mode: Mode = DEFAULT_MODE
        self.provider: Provider = DEFAULT_PROVIDER
        self.model: str = DEFAULT_MODELS[self.provider][0]

        self._engine: Optional[EngineClient] = None
        self._busy: bool = False
        self._last_log_path: Optional[Path] = None

        self._session_id: str = uuid.uuid4().hex[:10]
        self._chat_logging_enabled: bool = False
        self._chat_log_path: Optional[Path] = None

        # Transcript buffer is maintained separately from UI rendering.
        # This avoids early-render crashes when widgets are not fully sized.
        self._transcript_lines: list[str] = []
        self._transcript_ready: bool = False

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)

        # Top controls
        with Horizontal(id="topbar"):
            self.workspace_label = Static(self._workspace_text(), id="workspace_label")
            yield self.workspace_label

            mode_opts = [(m, m) for m in ["interpret", "plan", "execute"]]
            self.mode_select = Select(mode_opts, value=self.mode, id="mode_select")
            yield self.mode_select

            prov_opts = [(p, p) for p in ["openai", "anthropic"]]
            self.provider_select = Select(prov_opts, value=self.provider, id="provider_select")
            yield self.provider_select

            model_opts = [(m, m) for m in DEFAULT_MODELS[self.provider]]
            self.model_select = Select(model_opts, value=self.model, id="model_select")
            yield self.model_select

        with Horizontal(id="main"):
            with Vertical(id="left"):
                yield Static("Repository", classes="panel-title")
                self.repo_health = RepoHealthPanel()
                yield self.repo_health
                self.repo_tree = DirectoryTree(Path(self.workspace.repo_root), id="repo_tree")
                yield self.repo_tree

            with Vertical(id="center"):
                yield Static("Chat", classes="panel-title")
                # Transcript is a read-only TextArea to avoid version-specific log widget issues.
                self.transcript = TextArea(id="transcript")
                self.transcript.read_only = True
                self.transcript.show_line_numbers = False
                yield self.transcript
                self.composer = TextArea(id="composer")
                self.composer.placeholder = "Type message…  (Ctrl+Enter to submit)"
                yield self.composer

            with Vertical(id="right"):
                yield Static("Project & Inspection", classes="panel-title")
                self.project_panel = ProjectPanel()
                yield self.project_panel
                self.inspection_panel = InspectionPanel()
                yield self.inspection_panel

        self.status_bar = StatusBar()
        yield self.status_bar
        yield Footer()

    async def on_mount(self) -> None:
        self.set_focus(self.composer)
        # Avoid writing to transcript widgets during mount; queue lines and flush on_ready.
        self._append_transcript(f"[atlas-tui] workspace resolved: repo_root={self.workspace.repo_root}")
        if self.workspace.project_root:
            self._append_transcript(f"[atlas-tui] wrapper detected: project_root={self.workspace.project_root}")
        else:
            self._append_transcript("[atlas-tui] no wrapper detected (using .git root)")

    async def on_ready(self) -> None:
        # UI layout is ready; safe to render transcript.
        self._transcript_ready = True
        try:
            self.transcript.text = "\n".join(self._transcript_lines)
        except Exception:
            pass

        # Initialize panels
        await self._refresh_project_panel()
        await self._refresh_repo_health()

        # Start engine
        self._engine = EngineClient(cmd=self.engine_cmd, workspace=self.workspace, timeout_s=self.engine_timeout_s)
        try:
            await self._engine.start()
            self.status_bar.set_engine_status(self._engine.status.message)
        except Exception as e:
            self.status_bar.set_engine_status(f"engine start failed: {e}")

        self.status_bar.set_engine_cmd(self.engine_cmd_str)
        self.status_bar.set_idle()

    def _workspace_text(self) -> str:
        pr = self.workspace.project_root or "None"
        return f"repo: {self.workspace.repo_root} | project: {pr}"

    def _append_transcript(self, line: str) -> None:
        # Maintain transcript separately from the widget to avoid early-render crashes.
        self._transcript_lines.append(line)
        if len(self._transcript_lines) > 400:
            self._transcript_lines = self._transcript_lines[-400:]

        if not self._transcript_ready:
            return

        try:
            self.transcript.text = "\n".join(self._transcript_lines)
        except Exception as e:
            try:
                self.status_bar.flash(f"transcript error: {e}")
            except Exception:
                pass

        if self._chat_logging_enabled:
            entry = {
                "ts": __import__("datetime").datetime.now(__import__("datetime").timezone.utc).astimezone().isoformat(timespec="seconds"),
                "session_id": self._session_id,
                "line": line,
            }
            try:
                self._chat_log_path = write_chat_log(self.workspace, self._session_id, entry)
            except Exception:
                # avoid surfacing here; status bar will show last error on submit paths
                pass

    async def _refresh_project_panel(self) -> None:
        await self.project_panel.load(self.workspace)

    async def _refresh_repo_health(self) -> None:
        await self.repo_health.load(self.workspace)

    def _set_busy(self, what: str) -> None:
        self._busy = True
        self.status_bar.set_busy(what)
        self.composer.disabled = True

    def _set_idle(self, what: str = "") -> None:
        self._busy = False
        self.status_bar.set_idle(what)
        self.composer.disabled = False
        self.set_focus(self.composer)

    async def action_submit(self) -> None:
        if self._busy:
            self.status_bar.flash("busy: request in flight")
            return

        msg = self.composer.text.strip()
        if not msg:
            return

        self.composer.text = ""
        self._append_transcript(f"> {msg}")

        request_id = uuid.uuid4().hex
        ui_state = {
            "focused_panel": self._focused_panel_name(),
            "selected_path": self._selected_path(),
        }

        engine_input = EngineInput(
            workspace=self.workspace,
            mode=self.mode,
            provider=self.provider,
            model=self.model,
            user_message=msg,
            ui_state=ui_state,
        )

        if not self._engine:
            self._engine = EngineClient(cmd=self.engine_cmd, workspace=self.workspace, timeout_s=self.engine_timeout_s)

        self._set_busy("assembling context")

        try:
            out = await self._engine.submit(request_id, engine_input)
            # Write inspection log
            log_path = write_assembled_log(
                workspace=self.workspace,
                request_id=request_id,
                engine_input=engine_input,
                engine_output=out,
                preview_chars=self.preview_chars,
            )
            self._last_log_path = log_path

            sys_len = len(out.assembled_context.system)
            preview = out.assembled_context.system[: min(self.preview_chars, sys_len)]
            self.inspection_panel.update_summary(
                request_id=request_id,
                log_path=str(log_path),
                mode=self.mode,
                provider=self.provider,
                model=self.model,
                system_len=sys_len,
                system_preview=preview,
                diagnostics=out.diagnostics,
            )

            self.status_bar.set_last_log(str(log_path))
            self._append_transcript(f"[engine] assembled context (len={sys_len}) — log: {log_path}")

        except Exception as e:
            self._append_transcript(f"[error] {e}")
            self.status_bar.flash(f"error: {e}")
        finally:
            # Update engine status if available
            if self._engine:
                self.status_bar.set_engine_status(self._engine.status.message)
            self._set_idle()

    def _focused_panel_name(self) -> str:
        w = self.focused
        if w is None:
            return "chat"
        wid = getattr(w, "id", "") or ""
        if "repo" in wid:
            return "repo"
        if "project" in wid or "inspection" in wid:
            return "project"
        return "chat"

    def _selected_path(self) -> Optional[str]:
        try:
            node = self.repo_tree.cursor_node
            if node and node.data:
                return str(node.data.path)
        except Exception:
            return None
        return None

    async def action_focus_repo(self) -> None:
        self.set_focus(self.repo_tree)
        self.status_bar.flash("focus: repo")

    async def action_focus_chat(self) -> None:
        self.set_focus(self.composer)
        self.status_bar.flash("focus: chat")

    async def action_focus_project(self) -> None:
        self.set_focus(self.project_panel)
        self.status_bar.flash("focus: project")

    async def action_refresh_tree(self) -> None:
        # DirectoryTree has a reload method in newer versions; rebuild if absent.
        try:
            self.repo_tree.reload()
        except Exception:
            self.repo_tree.remove()
            self.repo_tree = DirectoryTree(Path(self.workspace.repo_root), id="repo_tree")
            self.query_one("#left").mount(self.repo_tree)
        await self._refresh_repo_health()
        self.status_bar.flash("repo tree refreshed")

    async def action_toggle_help(self) -> None:
        await self.push_screen(HelpOverlay(self))

    async def action_escape(self) -> None:
        # Close modal if present; else return focus to composer.
        if len(self.screen_stack) > 1:
            await self.pop_screen()
        else:
            self.set_focus(self.composer)

    async def action_toggle_chat_log(self) -> None:
        self._chat_logging_enabled = not self._chat_logging_enabled
        state = "on" if self._chat_logging_enabled else "off"
        if self._chat_logging_enabled:
            # Ensure directory exists
            _ = log_base_dir(self.workspace) / "chat"
            _.mkdir(parents=True, exist_ok=True)
            self._chat_log_path = log_base_dir(self.workspace) / "chat" / f"{self._session_id}.jsonl"
        self.status_bar.set_chat_log(state, str(self._chat_log_path) if self._chat_log_path else "")
        self.status_bar.flash(f"chat logging: {state}")

    async def action_restart_engine(self) -> None:
        if not self._engine:
            self._engine = EngineClient(cmd=self.engine_cmd, workspace=self.workspace, timeout_s=self.engine_timeout_s)
        self._set_busy("restarting engine")
        try:
            await self._engine.restart()
            self.status_bar.flash("engine restarted")
        except Exception as e:
            self.status_bar.flash(f"restart failed: {e}")
        finally:
            self.status_bar.set_engine_status(self._engine.status.message if self._engine else "n/a")
            self._set_idle()

    @on(Select.Changed, "#mode_select")
    async def _mode_changed(self, event: Select.Changed) -> None:
        self.mode = event.value  # type: ignore[assignment]
        if self.mode == "execute":
            self.status_bar.flash("execute mode is stubbed in v2 (no file writes)")
        await self._refresh_repo_health()

    @on(Select.Changed, "#provider_select")
    async def _provider_changed(self, event: Select.Changed) -> None:
        self.provider = event.value  # type: ignore[assignment]
        models = DEFAULT_MODELS.get(self.provider, [])
        self.model = models[0] if models else ""
        self.model_select.set_options([(m, m) for m in models])
        self.model_select.value = self.model
        self.status_bar.flash(f"provider: {self.provider}")
        await self._refresh_repo_health()

    @on(Select.Changed, "#model_select")
    async def _model_changed(self, event: Select.Changed) -> None:
        self.model = event.value  # type: ignore[assignment]
        self.status_bar.flash(f"model: {self.model}")

    @on(DirectoryTree.FileSelected)
    async def _file_selected(self, event: DirectoryTree.FileSelected) -> None:
        # Open file preview modal.
        path = event.path
        await self.push_screen(FilePreviewScreen(path=path))
