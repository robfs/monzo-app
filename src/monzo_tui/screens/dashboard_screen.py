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

from ..views import BalanceView
from ..views import LatestTransactionsView
from ..views import LogoView

logger = logging.getLogger(__name__)


class DashboardScreen(Screen):
    """The main dashboard screen."""

    transactions_table: reactive[LatestTransactionsView] = reactive(
        LatestTransactionsView()
    )
    balance: reactive[BalanceView] = reactive(BalanceView())

    def compose(self) -> ComposeResult:
        grid = Container(LogoView(), self.transactions_table, self.balance)
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
