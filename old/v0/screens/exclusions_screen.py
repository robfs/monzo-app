"""Exclusions screen for the Monzo TUI."""

import logging

from textual.app import ComposeResult
from textual.containers import Container
from textual.message import Message
from textual.reactive import reactive
from textual.screen import ModalScreen
from textual.widgets import Footer

from ..views import ExclusionsView

__all__ = ["ExclusionsScreen"]

logger = logging.getLogger(__name__)


class ExclusionsScreen(ModalScreen):
    """Exclusions screen for the Monzo TUI."""

    BINDINGS = [("escape", "close", "Close")]
    selected = reactive([])

    # def __init__(
    #     self,
    #     spreadsheet_id: str,
    #     credentials_path: Path,
    #     pay_day_type: str,
    #     pay_day: int,
    #     *args,
    #     **kwargs,
    # ):
    #     self.existing_spreadsheet_id = spreadsheet_id
    #     self.existing_credentials_path = credentials_path
    #     self.existing_pay_day_type = pay_day_type
    #     self.existing_pay_day = pay_day
    #     super().__init__(*args, **kwargs)

    def compose(self) -> ComposeResult:
        container = Container(ExclusionsView())
        container.border_title = "Categories"
        container.border_subtitle = "'Esc' to close"
        yield Footer()
        yield container

    def on_mount(self) -> None:
        self.exclusion_list.update_exclusions_list()

    def on_monzo_transactions_initialized(self) -> None:
        self.exclusion_list.update_exclusions_list()

    @property
    def exclusion_list(self) -> ExclusionsView:
        return self.query_one(ExclusionsView)

    class ExclusionsChanged(Message):
        """Message sent when exclusions are changed."""

    def on_selection_list_selected_changed(
        self, event: ExclusionsView.SelectedChanged
    ) -> None:
        self.post_message(self.ExclusionsChanged())

    # @property
    # def credentials_string(self) -> str:
    #     return str(self.existing_credentials_path)

    # def spreadsheet_id_input(self):
    #     return SpreadsheetIdInput(self.existing_spreadsheet_id)

    # def credentials_path_input(self):
    #     return CredentialsPathInput(self.credentials_string)

    # def pay_day_type_select(self):
    #     pay_day_types: list[tuple] = [
    #         ("Last Day", "last"),
    #         ("First Day", "first"),
    #         ("Specific Day", "specific"),
    #     ]
    #     return PayDayTypeSelect(
    #         value=self.existing_pay_day_type,
    #         options=pay_day_types,
    #         allow_blank=False,
    #         compact=True,
    #     )

    # def pay_day_input(self):
    #     return PayDayInput(f"{self.existing_pay_day}", type="integer", compact=True)

    # @property
    # def spreadsheet_id(self) -> SpreadsheetIdInput:
    #     return self.query_one(SpreadsheetIdInput)

    # @property
    # def credentials_path(self) -> CredentialsPathInput:
    #     return self.query_one(CredentialsPathInput)

    # @property
    # def pay_day_type(self) -> PayDayTypeSelect:
    #     return self.query_one(PayDayTypeSelect)

    # @property
    # def pay_day(self) -> PayDayInput:
    #     return self.query_one(PayDayInput)

    def action_close(self) -> None:
        """Close action triggered by ESC key."""
        self.dismiss()

    # def action_save(self) -> None:
    #     """Save action triggered by ENTER key."""
    #     spreadsheet_id: str = self.spreadsheet_id.value
    #     credentials_path: Path = Path(self.credentials_path.value).expanduser()
    #     pay_day_type: str = self.pay_day_type.value
    #     pay_day: int = int(self.pay_day.value)

    #     self.dismiss((True, spreadsheet_id, credentials_path, pay_day_type, pay_day))

    # def on_key(self, event: Key) -> None:
    #     """Handle key events, specifically Enter key when inputs are focused."""
    #     if event.key == "enter":
    #         if isinstance(self.focused, OptionList | Select):
    #             return
    #         self.action_save()
    #         event.prevent_default()

    # @on(Select.Changed, "PayDayTypeSelect")
    # def select_pay_day_type(self, event: Select.Changed) -> None:
    #     """Handle pay day type change event."""
    #     pay_day_input = self.pay_day
    #     if event.value == "last":
    #         pay_day_input.value = "31"
    #         pay_day_input.disabled = True
    #     elif event.value == "first":
    #         pay_day_input.value = "1"
    #         pay_day_input.disabled = True
    #     elif event.value == "specific":
    #         pay_day_input.disabled = False
    #         pay_day_input.focus()
