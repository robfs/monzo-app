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
from ..views import MonthlyChartView

logger = logging.getLogger(__name__)


class PayMonthView(Placeholder):
    """A placeholder widget for the pay month."""

    def on_mount(self) -> None:
        self.border_title = "Pay Month"


class DaysLeftView(Placeholder):
    """A placeholder widget for the days left."""

    def on_mount(self) -> None:
        self.border_title = "Days Left"


class SpendingLastMonthChartView(Placeholder):
    """A placeholder widget for the category chart."""

    def on_mount(self) -> None:
        self.border_title = "Spending Last Month"


class TopCategoriesTableView(Placeholder):
    """A placeholder widget for the category table."""

    def on_mount(self) -> None:
        self.border_title = "Spending this Month"


class TopMerchanatsTableView(Placeholder):
    """A placeholder widget for the category table."""

    def on_mount(self) -> None:
        self.border_title = "Top Merchants"


class TBCView(Placeholder):
    """A placeholder widget for the TBC."""

    def on_mount(self) -> None:
        self.border_title = "TBC"


class DashboardScreen(Screen):
    """The main dashboard screen."""

    def compose(self) -> ComposeResult:
        container = Container(
            LogoView(),
            MonthlyChartView(),
            self.balance_view(),
            PayMonthView("PayMonthView"),
            SpendingLastMonthChartView("CategoryChartView"),
            TopCategoriesTableView("CategoryTableView"),
            TopMerchanatsTableView("TopMerchantsTableView"),
            DaysLeftView("DaysLeftView"),
            TBCView("TBCView"),
            self.latest_transactions_table(),
        )
        container.border_title = "Dashboard"
        container.border_subtitle = "Dashboard of headline analysis."
        yield Footer()
        yield Header()
        yield container

    @property
    def transactions_table(self) -> LatestTransactionsView:
        return self.query_one(LatestTransactionsView)

    @property
    def balance(self) -> BalanceView:
        return self.query_one(BalanceView)

    @property
    def monthly_chart(self) -> MonthlyChartView:
        return self.query_one(MonthlyChartView)

    def latest_transactions_table(self):
        return LatestTransactionsView()

    def balance_view(self):
        return BalanceView()

    def update_all(self) -> None:
        try:
            self.transactions_table.refresh_data()
        except Exception as e:
            self.app.notify(f"Error refreshing transactions table: {e}")
        try:
            self.balance.refresh_data()
        except Exception as e:
            self.app.notify(f"Error refreshing balance: {e}")
        try:
            self.monthly_chart.update()
        except Exception as e:
            self.app.notify(f"Error refreshing monthly chart: {e}")

    @work(exclusive=True, thread=True)
    def on_monzo_transactions_initialized(self, message) -> None:
        """Handle MonzoTransactionsInitialized message."""
        worker = get_current_worker()
        if not worker.is_cancelled:
            logger.info("Refreshing Dashboard data.")
            self.update_all()
