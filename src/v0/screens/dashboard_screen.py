"""Module containing the DashboardScreen class."""

import logging

from textual import work
from textual.app import ComposeResult
from textual.containers import Container
from textual.screen import Screen
from textual.widgets import Footer
from textual.widgets import Header
from textual.widgets import Placeholder
from textual.worker import get_current_worker

from ..views import BalanceView
from ..views import LatestTransactionsView
from ..views import LogoView
from ..views import MonthlyChartView
from ..views import PayDayView
from ..views import TopCategoriesTableView
from ..views import TopMerchantsTableView
from ..views import SpendingLastMonthChartView

logger = logging.getLogger(__name__)


class DashboardScreen(Screen):
    """The main dashboard screen."""

    def compose(self) -> ComposeResult:
        container = Container(
            LogoView(),
            MonthlyChartView(classes="card"),
            self.balance_view(),
            PayDayView(classes="card"),
            SpendingLastMonthChartView(classes="card"),
            TopCategoriesTableView(classes="card"),
            TopMerchantsTableView(classes="card"),
            self.latest_transactions_table(),
            classes="screen",
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

    @property
    def top_merchants(self) -> TopMerchantsTableView:
        return self.query_one(TopMerchantsTableView)

    @property
    def top_categories(self) -> TopCategoriesTableView:
        return self.query_one(TopCategoriesTableView)

    @property
    def spending_last_month(self) -> SpendingLastMonthChartView:
        return self.query_one(SpendingLastMonthChartView)

    def latest_transactions_table(self):
        return LatestTransactionsView(classes="card")

    def balance_view(self):
        return BalanceView(classes="card")

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
        try:
            self.top_merchants.refresh_data()
        except Exception as e:
            self.app.notify(f"Error refreshing top merchants: {e}")
        try:
            self.top_categories.refresh_data()
        except Exception as e:
            self.app.notify(f"Error refreshing top categories: {e}")
        try:
            self.spending_last_month.update()
        except Exception as e:
            self.app.notify(f"Error refreshing spending last month: {e}")

    @work(exclusive=True, thread=True)
    def on_monzo_transactions_initialized(self, message) -> None:
        """Handle MonzoTransactionsInitialized message."""
        worker = get_current_worker()
        if not worker.is_cancelled:
            logger.info("Refreshing Dashboard data.")
            self.update_all()
