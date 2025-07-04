"""Module containing the DashboardScreen class."""

from textual.app import ComposeResult
from textual.containers import Container
from textual.message import Message
from textual.reactive import reactive
from textual.screen import Screen
from textual.widgets import Header, Footer

from ..views import TransactionsTable


class DashboardScreen(Screen):
    """The main dashboard screen."""

    transactions_table: reactive[TransactionsTable] = reactive(TransactionsTable())

    def compose(self) -> ComposeResult:
        grid = Container(self.transactions_table)
        grid.border_title = "Dashboard"
        grid.border_subtitle = "Dashboard of headline analysis."
        yield Footer()
        yield Header()
        yield grid

    def on_message(self, message: Message) -> None:
        """Handle messages from the app."""
        if (
            hasattr(message, "__class__")
            and message.__class__.__name__ == "MonzoTransactionsInitialized"
            and self.transactions_table
        ):
            self.transactions_table.refresh_data()
