"""Modal screen with a dialog to quit."""

from textual.app import ComposeResult
from textual.containers import Grid
from textual.screen import ModalScreen
from textual.widgets import Button
from textual.widgets import Label

__all__ = ["QuitModalScreen"]


class QuitModalScreen(ModalScreen[bool]):
    """Screen with a dialog to quit."""

    BINDINGS = [
        ("escape", "dismiss(False)", "Cancel"),
        ("q", "dismiss(True)", "Confirm Quit"),
    ]

    def compose(self) -> ComposeResult:
        yield Grid(
            Label("Are you sure you want to quit?", id="question"),
            Button("Quit (q)", variant="error", id="quit"),
            Button("Cancel (esc)", variant="primary", id="cancel"),
            id="dialog",
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "quit":
            self.dismiss(True)
        else:
            self.dismiss(False)
