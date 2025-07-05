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


class SettingsScreen(ModalScreen[tuple[bool, str, Path, str, int]]):
    """Settings screen for the Monzo TUI."""

    BINDINGS = [("escape", "cancel", "Cancel")]

    def __init__(
        self,
        spreadsheet_id: str,
        credentials_path: Path,
        pay_day_type: str,
        pay_day: int,
        *args,
        **kwargs,
    ):
        self.existing_spreadsheet_id = spreadsheet_id
        self.existing_credentials_path = credentials_path
        self.existing_pay_day_type = pay_day_type
        self.existing_pay_day = pay_day
        super().__init__(*args, **kwargs)

    def compose(self) -> ComposeResult:
        container = Container(
            self.spreadsheet_id_input(),
            self.credentials_path_input(),
            self.pay_day_type_select(),
            self.pay_day_input(),
        )
        container.border_title = "Settings"
        container.border_subtitle = "Press 'Enter' to save, 'Esc' to cancel"
        yield Footer()
        yield container

    @property
    def credentials_string(self) -> str:
        return str(self.existing_credentials_path)

    def spreadsheet_id_input(self):
        return SpreadsheetIdInput(self.existing_spreadsheet_id)

    def credentials_path_input(self):
        return CredentialsPathInput(self.credentials_string)

    def pay_day_type_select(self):
        pay_day_types: list[tuple] = [
            ("Last Day", "last"),
            ("First Day", "first"),
            ("Specific Day", "specific"),
        ]
        return PayDayTypeSelect(
            value=self.existing_pay_day_type,
            options=pay_day_types,
            allow_blank=False,
            compact=True,
        )

    def pay_day_input(self):
        return PayDayInput(f"{self.existing_pay_day}", type="integer", compact=True)

    @property
    def spreadsheet_id(self) -> SpreadsheetIdInput:
        return self.query_one(SpreadsheetIdInput)

    @property
    def credentials_path(self) -> CredentialsPathInput:
        return self.query_one(CredentialsPathInput)

    @property
    def pay_day_type(self) -> PayDayTypeSelect:
        return self.query_one(PayDayTypeSelect)

    @property
    def pay_day(self) -> PayDayInput:
        return self.query_one(PayDayInput)

    def action_cancel(self) -> None:
        """Cancel action triggered by ESC key."""
        self.dismiss((False, "", Path(""), "", 0))

    def action_save(self) -> None:
        """Save action triggered by ENTER key."""
        spreadsheet_id: str = self.spreadsheet_id.value
        credentials_path: Path = Path(self.credentials_path.value).expanduser()
        pay_day_type: str = self.pay_day_type.value
        pay_day: int = int(self.pay_day.value)

        self.dismiss((True, spreadsheet_id, credentials_path, pay_day_type, pay_day))

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
        pay_day_input = self.pay_day
        if event.value == "last":
            pay_day_input.value = "31"
            pay_day_input.disabled = True
        elif event.value == "first":
            pay_day_input.value = "1"
            pay_day_input.disabled = True
        elif event.value == "specific":
            pay_day_input.disabled = False
            pay_day_input.focus()
