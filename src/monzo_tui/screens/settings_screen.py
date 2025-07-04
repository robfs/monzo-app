"""Settings screen for the Monzo TUI."""

import logging
from pathlib import Path

from textual.app import ComposeResult
from textual.containers import Container
from textual.events import Key
from textual.screen import ModalScreen
from textual.widgets import Footer
from textual.widgets import Input
from textual.widgets import Label
from textual.widgets import Static

__all__ = ["SettingsErrorScreen", "SettingsScreen"]

logger = logging.getLogger(__name__)


class SpreadsheetIdInput(Input):
    """Input field for the spreadsheet ID."""

    def on_mount(self) -> None:
        self.border_title = "Spreadsheet ID"


class CredentialsPathInput(Input):
    """Input field for the credentials path."""

    def on_mount(self) -> None:
        self.border_title = "Credentials Path"


class SettingsErrorScreen(ModalScreen):
    """Screen for displaying settings errors."""

    BINDINGS = [("escape", "app.pop_screen", "OK")]

    def __init__(self, message: str, *args, **kwargs):
        self.message: str = message
        super().__init__(*args, **kwargs)

    def compose(self) -> ComposeResult:
        container = Container(Label(self.message))
        container.border_title = "Credentials Error"
        container.border_subtitle = "Press 'Esc' to return to settings"
        yield container


class SettingsScreen(ModalScreen[tuple[bool, str, Path]]):
    """Settings screen for the Monzo TUI."""

    BINDINGS = [("escape", "cancel", "Cancel")]

    def __init__(self, spreadsheet_id: str, credentials_path: Path, *args, **kwargs):
        self.spreadsheet_id = spreadsheet_id
        self.credentials_path = credentials_path
        super().__init__(*args, **kwargs)

    @property
    def credentials_string(self) -> str:
        return str(self.credentials_path)

    def compose(self) -> ComposeResult:
        container = Container(
            SpreadsheetIdInput(self.spreadsheet_id),
            CredentialsPathInput(self.credentials_string),
        )
        container.border_title = "Settings"
        container.border_subtitle = "Press 'Enter' to save, 'Esc' to cancel"
        yield Footer()
        yield container

    def get_spreadsheet_id(self) -> str:
        return self.query_one(SpreadsheetIdInput).value

    def get_credentials_path(self) -> Path:
        return Path(self.query_one(CredentialsPathInput).value).expanduser()

    def action_cancel(self) -> None:
        """Cancel action triggered by ESC key."""
        self.dismiss((False, "", Path("")))

    def action_save(self) -> None:
        """Save action triggered by ENTER key."""
        spreadsheet_id = self.get_spreadsheet_id()
        credentials_path = self.get_credentials_path()
        self.dismiss((True, spreadsheet_id, credentials_path))

    def on_key(self, event: Key) -> None:
        """Handle key events, specifically Enter key when inputs are focused."""
        if event.key == "enter":
            self.action_save()
            event.prevent_default()
