"""Settings screen for the Monzo TUI."""

from pathlib import Path

from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Input, Label, Static, Button, Footer


__all__ = ["SettingsScreen"]


class SpreadsheetIdInput(Static):
    """Input field for the spreadsheet ID."""

    def compose(self) -> ComposeResult:
        yield Label("Spreadsheet ID")
        yield Input(placeholder="Enter spreadsheet ID")


class CredentialsPathInput(Static):
    """Input field for the credentials path."""

    def compose(self) -> ComposeResult:
        yield Label("Credentials Path")
        yield Input(placeholder=str(self.default_credentials_path()))

    def default_credentials_path(self) -> Path:
        dir = Path.home() / ".monzo"
        return dir / "credentials.json"


class SettingsScreen(Screen):
    """Settings screen for the Monzo TUI."""

    BINDINGS = [("escape", "app.pop_screen", "Cancel")]

    def compose(self) -> ComposeResult:
        yield Footer()
        yield SpreadsheetIdInput()
        yield CredentialsPathInput()
        yield Button("Save", variant="success", id="save_settings_button")
        yield Button(
            "Cancel", action="app.pop_screen", variant="error", id="cancel_button"
        )
