from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Any, Dict, Optional, List

from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.screen import ModalScreen
from textual.widgets import Static, Markdown, TextArea, Select, Input, Button

from ..models import Workspace
from ..state_store import UIContextPrefs

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
        self._chat_log_state = "off"

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

    def set_chat_log(self, state: str) -> None:
        self._chat_log_state = state
        self._render()

    def flash(self, msg: str) -> None:
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
        selection_delta: Optional[Dict[str, List[str]]] = None,
    ) -> None:
        diag = diagnostics or {}
        sel = diag.get("selected_artifacts")
        sel_count = len(sel) if isinstance(sel, list) else None
        timings = diag.get("timings_ms") or {}
        assemble_ms = timings.get("assemble")

        budget = diag.get("budgets") or {}
        unit = budget.get("unit")
        target = budget.get("target")

        lines = [
            "Last assembly",
            f"- request: {request_id}",
            f"- mode/provider/model: {mode} / {provider} / {model}",
            f"- system chars: {system_len}",
        ]
        if unit and target is not None:
            lines.append(f"- budget: {target} {unit}")
        if sel_count is not None:
            lines.append(f"- selected artifacts: {sel_count}")
        if selection_delta:
            added = selection_delta.get("added") or []
            removed = selection_delta.get("removed") or []
            if added:
                lines.append(f"- added: {', '.join(added[:5])}" + ("…" if len(added) > 5 else ""))
            if removed:
                lines.append(f"- removed: {', '.join(removed[:5])}" + ("…" if len(removed) > 5 else ""))
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

        self.update("\n".join([
            "Health (local)",
            f"- wrapper: {wrapper}",
            f"- git: {'yes' if git.exists() else 'no'}",
            f"- status: {dirty}",
        ]))

class HelpOverlay(ModalScreen):
    def compose(self) -> ComposeResult:
        text = """# Atlas TUI — keybindings

- Ctrl+Enter: submit message
- Ctrl+1 / Ctrl+2 / Ctrl+3: focus repo / chat / project
- F5: refresh repo tree
- Ctrl+K: toggle this help
- Ctrl+L: toggle chat transcript logging
- Ctrl+P: edit context prefs (pinned/excluded/profile/budget)
- Ctrl+R: restart engine child
- Esc: close / return focus

Notes:
- v2 does not call providers and does not modify repo files (except logs/state).
- Inspection logs are written on every submit (see status bar for last path).
- Paths in context hints and contracts are repo-relative.
"""
        yield Markdown(text)

class FilePreviewScreen(ModalScreen):
    def __init__(self, path: Path, title: Optional[str] = None) -> None:
        super().__init__()
        self.path = path
        self.title = title or str(path)

    def compose(self) -> ComposeResult:
        try:
            content = _safe_read_text(self.path, max_bytes=120_000)
        except Exception as e:
            content = f"Failed to read {self.path}: {e}"
        yield Markdown(f"# Preview\n\n**{self.title}**\n\n```\n{content}\n```")

class ContextPrefsScreen(ModalScreen[UIContextPrefs]):
    def __init__(self, prefs: UIContextPrefs) -> None:
        super().__init__()
        # Shallow copy to allow cancel without mutation.
        self._prefs = UIContextPrefs(
            context_profile=prefs.context_profile,
            budget_chars=prefs.budget_chars,
            pinned_paths=list(prefs.pinned_paths),
            excluded_paths=list(prefs.excluded_paths),
        )

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
            self.dismiss(self._prefs)
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
