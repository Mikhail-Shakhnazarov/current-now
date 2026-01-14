from __future__ import annotations

import uuid
from pathlib import Path
from typing import Optional, Dict, Any, Set

from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import DirectoryTree, Footer, Header, Static, TextArea, Select
from textual import on

from ..models import EngineInput, Mode, Provider, Workspace
from ..engine_client import EngineClient
from ..log_writer import write_assembled_log, write_chat_log, log_base_dir
from ..state_store import UIContextPrefs, load_prefs, save_prefs
from .widgets import StatusBar, InspectionPanel, ProjectPanel, HelpOverlay, FilePreviewScreen, RepoHealthPanel, ContextPrefsScreen

DEFAULT_MODE: Mode = "interpret"
DEFAULT_PROVIDER: Provider = "openai"
DEFAULT_MODELS = {
    "openai": ["gpt-4.1-mini", "gpt-4.1", "gpt-4o-mini"],
    "anthropic": ["claude-3.5-sonnet", "claude-3.5-haiku"],
}

def _to_repo_rel(repo_root: Path, p: Optional[Path]) -> Optional[str]:
    if p is None:
        return None
    try:
        return str(p.resolve().relative_to(repo_root.resolve()).as_posix())
    except Exception:
        return None

class AtlasTUIApp(App):
    CSS = """
    Screen { layout: vertical; }
    #topbar { height: 3; }
    #main { height: 1fr; }
    #left, #center, #right { width: 1fr; border: solid $primary; }
    #left { width: 34%; }
    #center { width: 42%; }
    #right { width: 24%; }
    #composer { height: 6; }
    .panel-title { background: $panel; padding: 0 1; text-style: bold; }
    """

    BINDINGS = [
        ("ctrl+enter", "submit", "Submit"),
        ("ctrl+1", "focus_repo", "Focus repo"),
        ("ctrl+2", "focus_chat", "Focus chat"),
        ("ctrl+3", "focus_project", "Focus project"),
        ("f5", "refresh_tree", "Refresh tree"),
        ("ctrl+k", "toggle_help", "Help"),
        ("ctrl+l", "toggle_chat_log", "Chat log"),
        ("ctrl+p", "edit_context", "Context prefs"),
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

        self._session_id: str = uuid.uuid4().hex[:10]
        self._chat_logging_enabled: bool = False

        self.repo_root_path = Path(self.workspace.repo_root).resolve()
        self.prefs: UIContextPrefs = load_prefs(self.workspace.repo_root, self.workspace.project_root)
        self._last_selected_paths: Set[str] = set()

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)

        with Horizontal(id="topbar"):
            yield Static(self._workspace_text(), id="workspace_label")

            self.mode_select = Select([(m, m) for m in ["interpret", "plan", "execute"]], value=self.mode, id="mode_select")
            yield self.mode_select

            self.provider_select = Select([(p, p) for p in ["openai", "anthropic"]], value=self.provider, id="provider_select")
            yield self.provider_select

            self.model_select = Select([(m, m) for m in DEFAULT_MODELS[self.provider]], value=self.model, id="model_select")
            yield self.model_select

        with Horizontal(id="main"):
            with Vertical(id="left"):
                yield Static("Repository", classes="panel-title")
                self.repo_health = RepoHealthPanel()
                yield self.repo_health
                self.tree = DirectoryTree(self.repo_root_path, id="repo_tree")
                yield self.tree

            with Vertical(id="center"):
                yield Static("Chat", classes="panel-title")
                self.transcript = Static("", id="transcript")
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

        self._append_transcript(f"[atlas-tui] repo_root={self.workspace.repo_root}")
        self._append_transcript(f"[atlas-tui] project_root={self.workspace.project_root or 'None'}")
        self._append_transcript(f"[atlas-tui] context prefs: profile={self.prefs.context_profile}, budget_chars={self.prefs.budget_chars}, pinned={len(self.prefs.pinned_paths)}, excluded={len(self.prefs.excluded_paths)}")

        if self.glass_url:
            self._append_transcript(f"[glass] {self.glass_url}")
            self.status_bar.set_glass("on")

        await self.project_panel.load(self.workspace)
        await self.repo_health.load(self.workspace)

        self._engine = EngineClient(cmd=self.engine_cmd, workspace=self.workspace, timeout_s=self.engine_timeout_s)
        try:
            await self._engine.start()
            self.status_bar.set_engine_status(self._engine.status.message)
        except Exception as e:
            self.status_bar.set_engine_status(f"engine start failed: {e}")
        self.status_bar.set_idle()

    def _workspace_text(self) -> str:
        return f"repo: {self.workspace.repo_root} | project: {self.workspace.project_root or 'None'}"

    def _append_transcript(self, line: str) -> None:
        text = self.transcript.plain
        new = line if not text else (text + "\n" + line)
        lines = new.splitlines()
        if len(lines) > 400:
            lines = lines[-400:]
        self.transcript.update("\n".join(lines))

        if self._chat_logging_enabled:
            entry = {
                "ts": __import__("datetime").datetime.now(__import__("datetime").timezone.utc).astimezone().isoformat(timespec="seconds"),
                "session_id": self._session_id,
                "line": line,
            }
            try:
                write_chat_log(self.workspace, self._session_id, entry)
            except Exception:
                pass

    def _set_busy(self, what: str) -> None:
        self._busy = True
        self.status_bar.set_busy(what)
        self.composer.disabled = True

    def _set_idle(self, what: str = "") -> None:
        self._busy = False
        self.status_bar.set_idle(what)
        self.composer.disabled = False
        self.set_focus(self.composer)

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

    def _selected_repo_rel_path(self) -> Optional[str]:
        try:
            node = self.tree.cursor_node
            if node and node.data and hasattr(node.data, "path"):
                return _to_repo_rel(self.repo_root_path, Path(node.data.path))
        except Exception:
            return None
        return None

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

        ui_state: Dict[str, Any] = {
            "focused_panel": self._focused_panel_name(),
            "selected_path": self._selected_repo_rel_path(),
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

            log_path = write_assembled_log(
                workspace=self.workspace,
                request_id=request_id,
                engine_input=engine_input,
                engine_output=out,
                preview_chars=self.preview_chars,
            )

            sys_len = len(out.assembled_context.system)
            preview = out.assembled_context.system[: min(self.preview_chars, sys_len)]

            diag = out.diagnostics or {}
            sel = diag.get("selected_artifacts") or []
            current_sel = set()
            if isinstance(sel, list):
                for it in sel:
                    p = it.get("path")
                    if isinstance(p, str):
                        current_sel.add(p)

            added = sorted(list(current_sel - self._last_selected_paths))
            removed = sorted(list(self._last_selected_paths - current_sel))
            self._last_selected_paths = current_sel
            delta = {"added": added, "removed": removed}

            self.inspection_panel.update_summary(
                request_id=request_id,
                log_path=str(log_path),
                mode=self.mode,
                provider=self.provider,
                model=self.model,
                system_len=sys_len,
                system_preview=preview,
                diagnostics=out.diagnostics,
                selection_delta=delta,
            )

            self.status_bar.set_last_log(str(log_path))
            self._append_transcript(f"[engine] assembled context (len={sys_len}) — log: {log_path}")

        except Exception as e:
            self._append_transcript(f"[error] {e}")
            self.status_bar.flash(f"error: {e}")
        finally:
            if self._engine:
                self.status_bar.set_engine_status(self._engine.status.message)
            self._set_idle()

    async def action_focus_repo(self) -> None:
        self.set_focus(self.tree)
        self.status_bar.flash("focus: repo")

    async def action_focus_chat(self) -> None:
        self.set_focus(self.composer)
        self.status_bar.flash("focus: chat")

    async def action_focus_project(self) -> None:
        self.set_focus(self.project_panel)
        self.status_bar.flash("focus: project")

    async def action_refresh_tree(self) -> None:
        try:
            self.tree.reload()
        except Exception:
            self.tree.remove()
            self.tree = DirectoryTree(self.repo_root_path, id="repo_tree")
            self.query_one("#left").mount(self.tree)
        await self.repo_health.load(self.workspace)
        self.status_bar.flash("repo tree refreshed")

    async def action_toggle_help(self) -> None:
        await self.push_screen(HelpOverlay())

    async def action_escape(self) -> None:
        if len(self.screen_stack) > 1:
            await self.pop_screen()
        else:
            self.set_focus(self.composer)

    async def action_toggle_chat_log(self) -> None:
        self._chat_logging_enabled = not self._chat_logging_enabled
        state = "on" if self._chat_logging_enabled else "off"
        if self._chat_logging_enabled:
            (log_base_dir(self.workspace) / "chat").mkdir(parents=True, exist_ok=True)
        self.status_bar.set_chat_log(state)
        self.status_bar.flash(f"chat logging: {state}")

    async def action_edit_context(self) -> None:
        prefs = await self.push_screen_wait(ContextPrefsScreen(self.prefs))
        if isinstance(prefs, UIContextPrefs):
            self.prefs = prefs
            p = save_prefs(self.workspace.repo_root, self.workspace.project_root, self.prefs)
            self._append_transcript(f"[atlas-tui] context prefs saved: {p}")
            self.status_bar.flash("context prefs saved")

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

    @on(Select.Changed, "#provider_select")
    async def _provider_changed(self, event: Select.Changed) -> None:
        self.provider = event.value  # type: ignore[assignment]
        models = DEFAULT_MODELS.get(self.provider, [])
        self.model = models[0] if models else ""
        self.model_select.set_options([(m, m) for m in models])
        self.model_select.value = self.model
        self.status_bar.flash(f"provider: {self.provider}")

    @on(Select.Changed, "#model_select")
    async def _model_changed(self, event: Select.Changed) -> None:
        self.model = event.value  # type: ignore[assignment]
        self.status_bar.flash(f"model: {self.model}")

    @on(DirectoryTree.FileSelected)
    async def _file_selected(self, event: DirectoryTree.FileSelected) -> None:
        rel = _to_repo_rel(self.repo_root_path, event.path) or str(event.path)
        await self.push_screen(FilePreviewScreen(path=event.path, title=rel))
