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
from textual.widgets import OptionList
from textual.widgets import Select

__all__ = ["SettingsErrorScreen", "SettingsModalScreen"]

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


class SettingsModalScreen(ModalScreen[tuple[bool, str, Path]]):
    """Settings screen for the Monzo TUI."""

    BINDINGS = [("escape", "cancel", "Cancel"), ("enter", "save", "Save")]

    def __init__(
        self,
        spreadsheet_id: str = "",
        credentials_path: Path = Path(""),
        *args,
        **kwargs,
    ):
        self.existing_spreadsheet_id = spreadsheet_id
        self.existing_credentials_path = credentials_path
        super().__init__(*args, **kwargs)

    def compose(self) -> ComposeResult:
        container = Container(
            self.spreadsheet_id_input(), self.credentials_path_input()
        )
        container.border_title = "Settings"
        container.border_subtitle = "Press 'Enter' to save, 'Esc' to cancel"
        container.add_class("screen")
        yield Footer()
        yield container

    @property
    def credentials_string(self) -> str:
        return str(self.existing_credentials_path)

    def spreadsheet_id_input(self):
        return SpreadsheetIdInput(self.existing_spreadsheet_id)

    def credentials_path_input(self):
        return CredentialsPathInput(self.credentials_string)

    @property
    def spreadsheet_id(self) -> SpreadsheetIdInput:
        return self.query_one(SpreadsheetIdInput)

    @property
    def credentials_path(self) -> CredentialsPathInput:
        return self.query_one(CredentialsPathInput)

    def action_cancel(self) -> None:
        """Cancel action triggered by ESC key."""
        self.dismiss((False, "", Path("")))

    def action_save(self) -> None:
        """Save action triggered by ENTER key."""
        spreadsheet_id: str = self.spreadsheet_id.value
        credentials_path: Path = Path(self.credentials_path.value).expanduser()

        self.dismiss((True, spreadsheet_id, credentials_path))

    def on_key(self, event: Key) -> None:
        """Handle key events, specifically Enter key when inputs are focused."""
        if event.key == "enter":
            if isinstance(self.focused, OptionList | Select):
                return
            self.action_save()
            event.prevent_default()
