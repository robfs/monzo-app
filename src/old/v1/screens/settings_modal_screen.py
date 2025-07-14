"""Settings screen for the Monzo TUI."""

import logging
import os
from pathlib import Path

from textual import on
from textual.app import ComposeResult
from textual.containers import Container
from textual.events import Key
from textual.reactive import reactive
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


class SettingsModalScreen(ModalScreen[bool]):
    """Settings screen for the Monzo TUI."""

    BINDINGS = [("escape", "cancel", "Cancel"), ("enter", "save", "Save")]

    spreadsheet_id: reactive[str | None] = reactive(os.getenv("MONZO_SPREADSHEET_ID"))
    _credentials_path: reactive[str] = reactive("~/.monzo/credentials.json")
    pay_day_type: reactive[str] = reactive("specific")
    pay_day: reactive[int] = reactive(int(os.getenv("MONZO_PAY_DAY", "31")))

    def compose(self) -> ComposeResult:
        pay_day_type_options = [
            ("First day of the month", "first"),
            ("Last day of the month", "last"),
            ("Specific day of the month", "specific"),
        ]
        container = Container(
            SpreadsheetIdInput(self.spreadsheet_id),
            CredentialsPathInput(self._credentials_path),
            PayDayTypeSelect(
                pay_day_type_options, allow_blank=False, value=self.pay_day_type
            ),
            PayDayInput(str(self.pay_day), type="integer"),
        )
        container.border_title = "Settings"
        container.border_subtitle = "Press 'Enter' to save, 'Esc' to cancel"
        container.add_class("screen")
        yield Footer()
        yield container

    @property
    def credentials_path(self) -> Path:
        return Path(self._credentials_path).expanduser()

    def action_cancel(self) -> None:
        """Cancel action triggered by ESC key."""
        self.dismiss(False)

    def action_save(self) -> None:
        """Save action triggered by ENTER key."""
        self.spreadsheet_id = self.query_one(SpreadsheetIdInput).value
        self._credentials_path = self.query_one(CredentialsPathInput).value
        self.pay_day_type = self.query_one(PayDayTypeSelect).value
        self.pay_day = int(self.query_one(PayDayInput).value)

        self.dismiss(True)

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
