from __future__ import annotations

import sys
from dataclasses import asdict
from pathlib import Path
from typing import Optional

from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import DirectoryTree, Footer, Header, Static

from ..determinism import Clock, IdProvider, RealClock, UuidIds
from ..engine_client import EngineClient
from ..log_writer import write_assembled_log
from ..models import EngineInput, Mode, Provider, Workspace
from ..state_store import UIContextPrefs, load_prefs
from ..ui_events import focus_changed, key_handled, submit_done, submit_started
from ..ui_observability import append_ui_event, write_latest_snapshot
from ..ui_snapshot import capture_snapshot
from ..workspace import repo_relative_path, rel_to_project_root
from ..web.server import start_glass_server
from .widgets import ChatComposer, HelpOverlay, QuitConfirmScreen

DEFAULT_MODE: Mode = "interpret"
DEFAULT_PROVIDER: Provider = "dummy"


class AtlasTUIApp(App):
    CSS = """
    Screen { layout: vertical; }
    #main { height: 1fr; }
    #left, #center, #right { width: 1fr; border: solid $surface; }
    #left { width: 34%; }
    #center { width: 42%; }
    #right { width: 24%; }
    #composer { height: 7; }
    .panel-title { background: $panel; padding: 0 1; text-style: bold; }
    """

    BINDINGS = [
        ("f1", "toggle_help", "Help"),
        ("f2", "focus_cycle", "Cycle focus"),
        ("escape", "escape", "Close/Back"),
        ("esc", "escape", "Close/Back"),
        ("ctrl+c", "force_quit", "Force quit"),
    ]

    def __init__(
        self,
        *,
        workspace: Workspace,
        engine_cmd: list[str],
        clock: Optional[Clock] = None,
        ids: Optional[IdProvider] = None,
        engine_timeout_s: float = 20.0,
        start_glass: bool = False,
    ) -> None:
        super().__init__()
        self.workspace = workspace
        self.clock = clock or RealClock()
        self.ids = ids or UuidIds()
        self.session_id = self.ids.new_session_id()
        self.mode: Mode = DEFAULT_MODE
        self.provider: Provider = DEFAULT_PROVIDER
        self.model: str = "dummy"

        self._prefs: UIContextPrefs = load_prefs(workspace)
        self._engine = EngineClient(engine_cmd, workspace=workspace, timeout_s=engine_timeout_s)

        self._focused_panel: str = "chat"
        self._selected_path: Optional[str] = None
        self._last_request_id: Optional[str] = None
        self._last_log_path: Optional[Path] = None
        self._glass_url: Optional[str] = None
        self._start_glass = bool(start_glass)

    def compose(self) -> ComposeResult:
        yield Header(show_clock=False)
        yield Horizontal(
            Vertical(
                Static("Repo", classes="panel-title"),
                DirectoryTree(self.workspace.repo_root, id="repo_tree"),
                id="left",
            ),
            Vertical(
                Static("Chat", classes="panel-title"),
                ChatComposer(),
                id="center",
            ),
            Vertical(
                Static("Project/Inspection", classes="panel-title"),
                Static("", id="inspection"),
                id="right",
            ),
            id="main",
        )
        yield Footer()

    async def on_mount(self) -> None:
        self.query_one("#composer").focus()
        if self._start_glass:
            try:
                server = start_glass_server(self.workspace, port=0)
                self._glass_url = server.url
            except Exception:
                self._glass_url = None
        await self._emit_focus_changed()
        await self._write_snapshot()

    async def _emit_focus_changed(self) -> None:
        focused = getattr(getattr(self, "focused", None), "id", None)
        append_ui_event(self.workspace, focus_changed(self.session_id, self._focused_panel_name(), focused, clock=self.clock))

    def _focused_panel_name(self) -> str:
        focused = getattr(getattr(self, "focused", None), "id", None)
        if focused in {"repo_tree"}:
            return "repo"
        if focused in {"composer"}:
            return "chat"
        if focused in {"inspection"}:
            return "project"
        return self._focused_panel

    async def _write_snapshot(self) -> None:
        focused = getattr(getattr(self, "focused", None), "id", None)
        snap = capture_snapshot(
            focused_panel=self._focused_panel_name(),
            focused_widget_id=focused,
            screen_stack=[type(s).__name__ for s in self.screen_stack],
            selected_path=self._selected_path,
            mode=self.mode,
            provider=self.provider,
            model=self.model,
            last_request_id=self._last_request_id,
            last_log_path=rel_to_project_root(self.workspace, self._last_log_path) if self._last_log_path else None,
            prefs=self._prefs,
            session_id=self.session_id,
            clock=self.clock,
        )
        write_latest_snapshot(self.workspace, snap)

    async def action_toggle_help(self) -> None:
        if len(self.screen_stack) > 1 and isinstance(self.screen_stack[-1], HelpOverlay):
            self.pop_screen()
            append_ui_event(
                self.workspace,
                key_handled(self.session_id, "f1", "toggle_help", len(self.screen_stack), "help_toggle", clock=self.clock),
            )
            await self._write_snapshot()
            return
        self.push_screen(HelpOverlay())
        append_ui_event(
            self.workspace,
            key_handled(self.session_id, "f1", "toggle_help", len(self.screen_stack), "help_toggle", clock=self.clock),
        )
        await self._write_snapshot()

    async def action_focus_cycle(self) -> None:
        panel = self._focused_panel_name()
        order = ["repo", "chat", "project"]
        try:
            idx = order.index(panel)
        except ValueError:
            idx = 1
        nxt = order[(idx + 1) % len(order)]
        if nxt == "repo":
            self.query_one("#repo_tree").focus()
        elif nxt == "project":
            self.query_one("#inspection").focus()
        else:
            self.query_one("#composer").focus()
        self._focused_panel = nxt
        append_ui_event(self.workspace, key_handled(self.session_id, "f2", "focus_cycle", len(self.screen_stack), "focus_cycle", clock=self.clock))
        await self._emit_focus_changed()
        await self._write_snapshot()

    async def action_escape(self) -> None:
        if len(self.screen_stack) > 1:
            self.pop_screen()
            append_ui_event(self.workspace, key_handled(self.session_id, "escape", "escape", len(self.screen_stack), "pop", clock=self.clock))
            await self._write_snapshot()
            return
        self.push_screen(QuitConfirmScreen(), callback=self._on_quit_confirm)
        append_ui_event(self.workspace, key_handled(self.session_id, "escape", "escape", len(self.screen_stack), "quit_confirm", clock=self.clock))
        await self._write_snapshot()

    def _on_quit_confirm(self, quit_selected: bool) -> None:
        if quit_selected:
            self.exit()

    def action_force_quit(self) -> None:
        raise SystemExit(0)

    async def action_submit(self) -> None:
        composer = self.query_one("#composer", ChatComposer)
        msg = composer.text.strip()
        if not msg:
            return
        request_id = self.ids.new_request_id()
        self._last_request_id = request_id

        ui_state = {
            "focused_panel": self._focused_panel_name(),
            "selected_path": self._selected_path,
            "prefs": asdict(self._prefs),
        }
        append_ui_event(self.workspace, submit_started(self.session_id, request_id, self.mode, self.provider, self.model, clock=self.clock))
        await self._write_snapshot()

        ok = False
        system_chars = 0
        try:
            engine_input = EngineInput(
                workspace=self.workspace,
                mode=self.mode,
                provider=self.provider,
                model=self.model,
                user_message=msg,
                ui_state=ui_state,
            )
            engine_output = await self._engine.submit(request_id, engine_input)
            system_chars = len(engine_output.assembled_context.system)
            self._last_log_path = write_assembled_log(
                workspace=self.workspace,
                request_id=request_id,
                engine_input=engine_input,
                engine_output=engine_output,
                session_id=self.session_id,
                clock=self.clock,
            )
            ok = True
            self.query_one("#inspection", Static).update(
                f"request_id={request_id}\nselected={len(engine_output.assembled_context.selected_artifacts)}\nlog={self._last_log_path}"
            )
            composer.text = ""
        except Exception as e:
            self.query_one("#inspection", Static).update(f"submit failed: {e}")
        finally:
            append_ui_event(self.workspace, submit_done(self.session_id, request_id, ok, system_chars, clock=self.clock))
            await self._write_snapshot()

    async def on_directory_tree_file_selected(self, event: DirectoryTree.FileSelected) -> None:
        self._selected_path = repo_relative_path(self.workspace.repo_root, str(event.path))
        await self._write_snapshot()
