from __future__ import annotations

import asyncio
import os
import uuid
from dataclasses import asdict
from pathlib import Path
from typing import Optional

from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Button, DirectoryTree, Footer, Header, Static, TextArea, Select
from textual import on
from textual.message import Message
from textual.screen import ModalScreen

from ..models import EngineInput, Mode, Provider, Workspace
from ..engine_client import EngineClient
from ..log_writer import write_assembled_log, write_chat_log, log_base_dir
from ..state_store import UIContextPrefs, load_prefs, save_prefs
from ..workspace import discover_workspace
from .widgets import (
    StatusBar,
    InspectionPanel,
    ProjectPanel,
    HelpOverlay,
    FilePreviewScreen,
    RepoHealthPanel,
    ChatComposer,
    ContextPrefsScreen,
    QuitConfirmScreen,
)

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
        border: solid $surface;
    }

    #left:focus-within,
    #center:focus-within,
    #right:focus-within {
        border: solid $accent;
    }

    #left { width: 34%; }
    #center { width: 42%; }
    #right { width: 24%; }

    #composer {
        height: 7;
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
        ("f1", "toggle_help", "Help"),
        ("f2", "focus_cycle", "Cycle focus"),
        ("escape", "escape", "Close/Back"),
        ("esc", "escape", "Close/Back"),
    ]

    def __init__(
        self,
        workspace: Workspace,
        engine_cmd: list[str],
        engine_cmd_str: str,
        preview_chars: int = 800,
        engine_timeout_s: float = 60.0,
        glass_url: Optional[str] = None,
    ) -> None:
        super().__init__()
        self.workspace = workspace
        self.engine_cmd = engine_cmd
        self.engine_cmd_str = engine_cmd_str
        self.preview_chars = preview_chars
        self.engine_timeout_s = engine_timeout_s
        self.glass_url = glass_url

        self.mode: Mode = DEFAULT_MODE
        self.provider: Provider = DEFAULT_PROVIDER
        self.model: str = DEFAULT_MODELS[self.provider][0]

        self._engine: Optional[EngineClient] = None
        self._busy: bool = False
        self._last_log_path: Optional[Path] = None

        self._session_id: str = uuid.uuid4().hex[:10]
        self._chat_logging_enabled: bool = False
        self._chat_log_path: Optional[Path] = None

        self._repo_root_path = Path(self.workspace.repo_root).resolve()
        self.prefs: UIContextPrefs = load_prefs(self.workspace.repo_root, self.workspace.project_root)
        self._quit_confirm_pending: bool = False
        # Transcript buffer is maintained separately from UI rendering.
        # This avoids early-render crashes when widgets are not fully sized.
        self._transcript_lines: list[str] = []
        self._transcript_ready: bool = False

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)

        # Top controls
        with Horizontal(id="topbar"):
            self.workspace_label = Static(self._workspace_identity_text(), id="workspace_label")
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

            self.btn_help = Button("Help", id="btn_help")
            self.btn_refresh = Button("Refresh", id="btn_refresh")
            self.btn_chatlog = Button("Chat Log", id="btn_chatlog")
            self.btn_details = Button("Details", id="btn_details")
            self.btn_prefs = Button("Prefs", id="btn_prefs")
            self.btn_restart = Button("Restart", id="btn_restart")
            self.btn_quit = Button("Quit", id="btn_quit", variant="error")
            yield self.btn_help
            yield self.btn_refresh
            yield self.btn_chatlog
            yield self.btn_details
            yield self.btn_prefs
            yield self.btn_restart
            yield self.btn_quit

        with Horizontal(id="main"):
            with Vertical(id="left"):
                yield Static("Repository", classes="panel-title")
                self.repo_health = RepoHealthPanel()
                yield self.repo_health
                self.selected_path_label = Static("selected_path: (none)", id="selected_path_label")
                yield self.selected_path_label
                self.repo_tree = DirectoryTree(Path(self.workspace.repo_root), id="repo_tree")
                yield self.repo_tree

            with Vertical(id="center"):
                yield Static("Chat", classes="panel-title")
                # Transcript is a read-only TextArea to avoid version-specific log widget issues.
                self.transcript = TextArea(id="transcript")
                try:
                    self.transcript.read_only = True
                except Exception:
                    pass
                try:
                    self.transcript.show_line_numbers = False
                except Exception:
                    pass
                yield self.transcript
                self.composer = ChatComposer(id="composer")
                try:
                    self.composer.placeholder = "Type message...  (Enter to submit; Shift+Enter for newline)"
                except Exception:
                    pass
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
        # Keep identity out of the transcript; show in header/status instead.

    async def on_ready(self) -> None:
        # UI layout is ready; safe to render transcript.
        self._transcript_ready = True
        try:
            self._set_textarea_text(self.transcript, "\n".join(self._transcript_lines))
        except Exception:
            pass

        # Initialize panels
        await self._refresh_project_panel()
        await self._refresh_repo_health()
        self._update_selected_path_label()

        # Start engine
        self._engine = EngineClient(cmd=self.engine_cmd, workspace=self.workspace, timeout_s=self.engine_timeout_s)
        try:
            await self._engine.start()
            self.status_bar.set_engine_status(self._engine.status.message)
        except Exception as e:
            self.status_bar.set_engine_status(f"engine start failed: {e}")

        self.status_bar.set_engine_cmd(self.engine_cmd_str)
        if self.glass_url:
            self.status_bar.set_glass("on", self.glass_url)
        self.status_bar.set_idle()

    def _workspace_identity_text(self) -> str:
        repo_name = Path(self.workspace.repo_root).name or "repo"
        proj_name = Path(self.workspace.project_root).name if self.workspace.project_root else "None"
        wrapper = "yes" if self.workspace.project_root else "no"
        return f"repo:{repo_name} project:{proj_name} wrapper:{wrapper}"

    def _short_path(self, p: Optional[Path]) -> str:
        if not p:
            return "(none)"
        try:
            if self.workspace.project_root:
                base = Path(self.workspace.project_root).resolve()
                return str(p.resolve().relative_to(base)).replace("\\", "/")
            base = Path(self.workspace.repo_root).resolve()
            return str(p.resolve().relative_to(base)).replace("\\", "/")
        except Exception:
            return p.name

    def _update_selected_path_label(self) -> None:
        sel = self._selected_path() or "(none)"
        self.selected_path_label.update(f"selected_path: {sel}")

    def _get_textarea_text(self, widget: TextArea) -> str:
        for attr in ("text", "value"):
            try:
                v = getattr(widget, attr)
            except Exception:
                continue
            if isinstance(v, str):
                return v
        return ""

    def _set_textarea_text(self, widget: TextArea, text: str) -> None:
        for attr in ("text", "value"):
            try:
                setattr(widget, attr, text)
                return
            except Exception:
                continue

    def _append_transcript(self, line: str) -> None:
        # Maintain transcript separately from the widget to avoid early-render crashes.
        self._transcript_lines.append(line)
        if len(self._transcript_lines) > 400:
            self._transcript_lines = self._transcript_lines[-400:]

        if not self._transcript_ready:
            return

        try:
            self._set_textarea_text(self.transcript, "\n".join(self._transcript_lines))
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

        msg = self._get_textarea_text(self.composer).strip()
        if not msg:
            return

        self._set_textarea_text(self.composer, "")
        self._append_transcript(f"> {msg}")

        request_id = uuid.uuid4().hex
        ui_state = {
            "focused_panel": self._focused_panel_name(),
            "selected_path": self._selected_path(),
            "context_profile": self.prefs.context_profile,
            "budget_chars": self.prefs.budget_chars,
            "pinned_paths": list(self.prefs.pinned_paths),
            "excluded_paths": list(self.prefs.excluded_paths),
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
                log_path=self._short_path(log_path),
                mode=self.mode,
                provider=self.provider,
                model=self.model,
                system_len=sys_len,
                system_preview=preview,
                diagnostics=out.diagnostics,
            )

            self.status_bar.set_last_log(self._short_path(log_path))
            self._append_transcript(
                f"[engine] assembled context (len={sys_len}) - log: {self._short_path(log_path)}"
            )

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
        if w in {self.repo_tree, self.repo_health}:
            return "repo"
        if w in {self.project_panel, self.inspection_panel}:
            return "project"
        return "chat"

    def _selected_path(self) -> Optional[str]:
        try:
            node = self.repo_tree.cursor_node
            if node and node.data:
                p = Path(node.data.path).resolve()
                rel = p.relative_to(self._repo_root_path)
                return rel.as_posix()
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

    async def action_focus_cycle(self) -> None:
        order = ["repo", "chat", "project"]
        current = self._focused_panel_name()
        try:
            idx = order.index(current)
        except ValueError:
            idx = 0
        nxt = order[(idx + 1) % len(order)]
        if nxt == "repo":
            await self.action_focus_repo()
            return
        if nxt == "project":
            await self.action_focus_project()
            return
        await self.action_focus_chat()

    async def action_refresh_tree(self) -> None:
        # DirectoryTree has a reload method in newer versions; rebuild if absent.
        try:
            self.repo_tree.reload()
        except Exception:
            self.repo_tree.remove()
            self.repo_tree = DirectoryTree(Path(self.workspace.repo_root), id="repo_tree")
            self.query_one("#left").mount(self.repo_tree)
        await self._refresh_repo_health()
        self._update_selected_path_label()
        self.status_bar.flash("repo tree refreshed")

    async def action_toggle_help(self) -> None:
        await self.push_screen(HelpOverlay(self))

    async def action_edit_context(self) -> None:
        def _apply(result) -> None:
            if not isinstance(result, UIContextPrefs):
                self.status_bar.flash("context prefs canceled")
                return

            self.prefs = result
            try:
                path = save_prefs(self.workspace.repo_root, self.workspace.project_root, self.prefs)
                self._append_transcript(f"[atlas-tui] context prefs saved: {path}")
                self.status_bar.flash("context prefs saved")
            except Exception as e:
                self._append_transcript(f"[error] failed to save prefs: {e}")
                self.status_bar.flash(f"save prefs failed: {e}")

        try:
            # Textual 7+: avoid blocking an action handler waiting for dismissal.
            await self.push_screen(ContextPrefsScreen(self.prefs), callback=_apply)  # type: ignore[call-arg]
        except TypeError:
            # Older Textual: no callback arg.
            _apply(await self.push_screen_wait(ContextPrefsScreen(self.prefs)))

    async def action_escape(self) -> None:
        # Close modal if present; else open quit confirmation.
        if len(self.screen_stack) > 1:
            # Prefer dismissing modals so any waiting callbacks resolve.
            top = self.screen
            try:
                if isinstance(top, ModalScreen):
                    top.dismiss(None)  # type: ignore[arg-type]
                    return
            except Exception:
                pass
            await self.pop_screen()
        else:
            await self.action_quit()

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

    async def _request_quit_confirm(self) -> None:
        if self._quit_confirm_pending:
            return
        self._quit_confirm_pending = True

        def _apply(result) -> None:
            try:
                if result:
                    self.exit()
            finally:
                self._quit_confirm_pending = False

        try:
            # Textual 7+: avoid blocking an action handler waiting for dismissal.
            await self.push_screen(QuitConfirmScreen(), callback=_apply)  # type: ignore[call-arg]
        except TypeError:
            # Older Textual: no callback arg.
            confirm = bool(await self.push_screen_wait(QuitConfirmScreen()))
            self._quit_confirm_pending = False
            if confirm:
                self.exit()

    async def action_quit(self) -> None:
        await self._request_quit_confirm()

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        bid = event.button.id
        if bid == "btn_help":
            await self.action_toggle_help()
            return
        if bid == "btn_refresh":
            await self.action_refresh_tree()
            return
        if bid == "btn_chatlog":
            await self.action_toggle_chat_log()
            return
        if bid == "btn_details":
            self.status_bar.set_details_visible(not self.status_bar._details_visible)
            return
        if bid == "btn_prefs":
            await self.action_edit_context()
            return
        if bid == "btn_restart":
            await self.action_restart_engine()
            return
        if bid == "btn_quit":
            await self.action_quit()
            return

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
        await self._set_model_options(models)

    async def _set_model_options(self, models: list[str]) -> None:
        # Textual 7's Select.set_options expects the internal overlay to exist.
        # During early mounts, Select.Changed can fire before the model Select is
        # fully composed; retry a few times to avoid crashing.
        options = [(m, m) for m in models]
        last_error: Exception | None = None
        for _ in range(6):
            try:
                self.model_select.set_options(options)
                if self.model:
                    try:
                        self.model_select.value = self.model
                    except Exception:
                        pass
                return
            except Exception as e:
                last_error = e
                await asyncio.sleep(0)
        if last_error:
            self.status_bar.flash(f"model options update failed: {last_error}")
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
        self._update_selected_path_label()
