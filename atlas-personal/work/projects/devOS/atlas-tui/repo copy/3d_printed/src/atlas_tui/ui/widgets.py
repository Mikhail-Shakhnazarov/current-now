from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Markdown, Static, TextArea


class HelpOverlay(ModalScreen[None]):
    BINDINGS = [("escape", "dismiss", "Close"), ("esc", "dismiss", "Close")]

    def compose(self) -> ComposeResult:
        yield Vertical(
            Static("Help", classes="panel-title"),
            Markdown(
                "\n".join(
                    [
                        "# Atlas TUI (3d_printed)",
                        "",
                        "- `F1` toggle help",
                        "- `F2` cycle focus (repo -> chat -> project)",
                        "- `Esc` close modal / open quit confirm",
                        "- `Ctrl+C` force quit",
                    ]
                )
            ),
            id="help_body",
        )

    def action_dismiss(self) -> None:
        self.dismiss(None)


class QuitConfirmScreen(ModalScreen[bool]):
    BINDINGS = [("escape", "cancel", "Cancel"), ("esc", "cancel", "Cancel")]

    def compose(self) -> ComposeResult:
        yield Vertical(
            Static("Quit?", classes="panel-title"),
            Static("Press Quit to exit, Esc to cancel."),
            Horizontal(
                Button("Cancel", id="cancel", variant="default"),
                Button("Quit", id="quit", variant="error"),
                id="quit_buttons",
            ),
            id="quit_confirm",
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "quit":
            self.dismiss(True)
        else:
            self.dismiss(False)

    def action_cancel(self) -> None:
        self.dismiss(False)


class ChatComposer(TextArea):
    def __init__(self) -> None:
        super().__init__(id="composer")

    async def _on_key(self, event) -> None:  # type: ignore[override]
        key = getattr(event, "key", "")
        if key == "enter" and getattr(event, "shift", False):
            return await super()._on_key(event)
        if key == "enter":
            event.stop()
            app = self.app
            if hasattr(app, "action_submit"):
                await app.action_submit()  # type: ignore[misc]
            return
        return await super()._on_key(event)

