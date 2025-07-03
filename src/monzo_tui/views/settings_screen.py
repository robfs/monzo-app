"""Settings screen for the Monzo TUI."""

from pathlib import Path

from textual.app import ComposeResult
from textual.screen import ModalScreen
from textual.widgets import Input, Label, Static, Button, Footer
from textual.containers import Grid


__all__ = ["SettingsScreen"]


class SpreadsheetIdInput(Static):
    """Input field for the spreadsheet ID."""

    def compose(self) -> ComposeResult:
        yield Label("Spreadsheet ID")
        yield Input(placeholder="Enter spreadsheet ID", id="spreadsheet_id")


class CredentialsPathInput(Static):
    """Input field for the credentials path."""

    def compose(self) -> ComposeResult:
        yield Label("Credentials Path")
        yield Input(
            placeholder=str(self.default_credentials_path()), id="credentials_path"
        )

    @staticmethod
    def default_credentials_path() -> Path:
        dir = Path.home() / ".monzo"
        return dir / "credentials.json"


class SettingsScreen(ModalScreen[tuple[str, str]]):
    """Settings screen for the Monzo TUI."""

    BINDINGS = [("escape", "app.pop_screen", "Cancel")]

    def compose(self) -> ComposeResult:
        yield Footer()
        yield Grid(
            SpreadsheetIdInput(),
            CredentialsPathInput(),
            Button("Save", variant="success", id="save"),
            Button(
                "Cancel (esc)", action="app.pop_screen", variant="error", id="cancel"
            ),
            id="settings-grid",
        )

    def get_spreadsheet_id(self) -> str:
        return self.query_one("#spreadsheet_id", Input).value

    def get_credentials_path(self) -> str:
        return self.query_one("#credentials_path", Input).value

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "save":
            spreadsheet_id = self.get_spreadsheet_id()
            credentials_path = self.get_credentials_path()
            self.dismiss((spreadsheet_id, credentials_path))
        else:
            self.dismiss(("", ""))
