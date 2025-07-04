"""Module containing the DashboardScreen class."""

import logging

from textual import work
from textual.app import ComposeResult
from textual.containers import Container
from textual.reactive import reactive
from textual.screen import Screen
from textual.widgets import Footer
from textual.widgets import Header
from textual.worker import get_current_worker

from ..views import Balance
from ..views import TransactionsTable

logger = logging.getLogger(__name__)


class DashboardScreen(Screen):
    """The main dashboard screen."""

    transactions_table: reactive[TransactionsTable] = reactive(TransactionsTable())
    balance: reactive[Balance] = reactive(Balance())

    def compose(self) -> ComposeResult:
        grid = Container(self.balance, self.transactions_table)
        grid.border_title = "Dashboard"
        grid.border_subtitle = "Dashboard of headline analysis."
        yield Footer()
        yield Header()
        yield grid

    @work(exclusive=True, thread=True)
    def on_monzo_monzo_transactions_initialized(self, message) -> None:
        """Handle MonzoTransactionsInitialized message."""
        worker = get_current_worker()
        if not worker.is_cancelled:
            logger.info("Refreshing Dashboard data.")
            self.transactions_table.refresh_data()
            self.balance.refresh_data()
