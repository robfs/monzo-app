"""Settings screen for the Monzo TUI."""

import logging
from pathlib import Path

from textual import on
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


class PayDayTypeSelect(Select):
    """Select field for the payday."""

    def on_mount(self) -> None:
        self.border_title = "Payday Type"


class PayDayInput(Input):
    """Input field for the payday."""

    def on_mount(self) -> None:
        self.border_title = "Payday"


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


class SettingsModalScreen(ModalScreen[tuple[bool, str, Path, str, int]]):
    """Settings screen for the Monzo TUI."""

    BINDINGS = [("escape", "cancel", "Cancel"), ("enter", "save", "Save")]

    def __init__(
        self,
        spreadsheet_id: str = "",
        credentials_path: Path = Path(""),
        pay_day_type: str = "first",
        pay_day: int = 1,
        *args,
        **kwargs,
    ):
        self.existing_spreadsheet_id = spreadsheet_id
        self.existing_credentials_path = credentials_path
        self.existing_pay_day_type = pay_day_type
        self.existing_pay_day = pay_day
        super().__init__(*args, **kwargs)

    def compose(self) -> ComposeResult:
        pay_day_type_options = [
            ("First day of the month", "first"),
            ("Last day of the month", "last"),
            ("Specific day of the month", "specific"),
        ]
        container = Container(
            SpreadsheetIdInput(self.existing_spreadsheet_id),
            CredentialsPathInput(self.credentials_string),
            PayDayTypeSelect(
                pay_day_type_options,
                value=self.existing_pay_day_type,
                allow_blank=False,
            ),
            PayDayInput(str(self.existing_pay_day), type="integer"),
        )
        container.border_title = "Settings"
        container.border_subtitle = "Press 'Enter' to save, 'Esc' to cancel"
        container.add_class("screen")
        yield Footer()
        yield container

    @property
    def credentials_string(self) -> str:
        return str(self.existing_credentials_path)

    def action_cancel(self) -> None:
        """Cancel action triggered by ESC key."""
        self.dismiss((False, "", Path(""), "last", 31))

    def action_save(self) -> None:
        """Save action triggered by ENTER key."""
        spreadsheet_id: str = self.query_one(SpreadsheetIdInput).value
        credentials_path: Path = Path(
            self.query_one(CredentialsPathInput).value
        ).expanduser()
        pay_day_type: str = self.query_one(PayDayTypeSelect).value
        pay_day_value: int = int(self.query_one(PayDayInput).value)

        self.dismiss(
            (True, spreadsheet_id, credentials_path, pay_day_type, pay_day_value)
        )

    def on_key(self, event: Key) -> None:
        """Handle key events, specifically Enter key when inputs are focused."""
        if event.key == "enter":
            if isinstance(self.focused, OptionList | Select):
                return
            self.action_save()
            event.prevent_default()

    @on(Select.Changed, "PayDayTypeSelect")
    def select_pay_day_type(self, event: Select.Changed) -> None:
        """Handle pay day type change event."""
        pay_day_input = self.query_one(PayDayInput)
        if event.value == "last":
            pay_day_input.value = "31"
            pay_day_input.disabled = True
        elif event.value == "first":
            pay_day_input.value = "1"
            pay_day_input.disabled = True
        elif event.value == "specific":
            pay_day_input.disabled = False
            pay_day_input.focus()
