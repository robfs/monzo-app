"""Module containing the DashboardScreen class."""

import logging

from textual import work
from textual.app import ComposeResult
from textual.containers import Container
from textual.reactive import reactive
from textual.screen import Screen
from textual.widgets import Footer
from textual.widgets import Header
from textual.widgets import Placeholder
from textual.worker import get_current_worker

from ..views import BalanceView
from ..views import LatestTransactionsView
from ..views import LogoView

logger = logging.getLogger(__name__)


class MonthlyChartView(Placeholder):
    """A placeholder widget for the monthly expenditure chart."""


class PayMonthView(Placeholder):
    """A placeholder widget for the pay month."""


class DaysLeftView(Placeholder):
    """A placeholder widget for the days left."""


class CategoryChartView(Placeholder):
    """A placeholder widget for the category chart."""


class CategoryTableView(Placeholder):
    """A placeholder widget for the category table."""


class DashboardScreen(Screen):
    """The main dashboard screen."""

    def compose(self) -> ComposeResult:
        grid = Container(
            LogoView(), self.latest_transactions_table(), self.balance_view()
        )
        grid.border_title = "Dashboard"
        grid.border_subtitle = "Dashboard of headline analysis."
        yield Footer()
        yield Header()
        yield grid

    @property
    def transactions_table(self) -> LatestTransactionsView:
        return self.query_one(LatestTransactionsView)

    @property
    def balance(self) -> BalanceView:
        return self.query_one(BalanceView)

    def latest_transactions_table(self):
        return LatestTransactionsView()

    def balance_view(self):
        return BalanceView()

    def update_all(self) -> None:
        self.transactions_table.refresh_data()
        self.balance.refresh_data()

    @work(exclusive=True, thread=True)
    def on_monzo_transactions_initialized(self, message) -> None:
        """Handle MonzoTransactionsInitialized message."""
        worker = get_current_worker()
        if not worker.is_cancelled:
            logger.info("Refreshing Dashboard data.")
            self.update_all()
