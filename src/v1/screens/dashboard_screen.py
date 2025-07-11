"""Module defining the dashboard screen."""

import logging

from textual.app import ComposeResult
from textual.containers import Container
from textual.message import Message
from textual.screen import Screen
from textual.widgets import Footer
from textual.widgets import Header

from ..widgets import BalanceCard
from ..widgets import LastMonthCategoryChart
from ..widgets import LatestTransactionsTable
from ..widgets import Logo
from ..widgets import MonthlySpendChart
from ..widgets import PayDayCalendar
from ..widgets import TopCategoriesTable
from ..widgets import TopMerchantsTable

__all__ = ["DashboardScreen"]


logger = logging.getLogger(__name__)


class DashboardScreen(Screen):
    """Dashboard screen."""

    pay_day = reactive(31)

    def compose(self) -> ComposeResult:
        container = Container(
            Logo(),
            LastMonthCategoryChart(),
            MonthlySpendChart(),
            BalanceCard(),
            TopCategoriesTable(),
            TopMerchantsTable(),
            PayDayCalendar(),
            LatestTransactionsTable(),
            classes="screen",
        )
        container.border_title = "Dashboard"
        container.border_subtitle = "Summary analytics screen"
        yield container
        yield Footer()
        yield Header()

    def on_monzo_transactions_available(self, message: Message) -> None:
        self.app.notify(str(message), severity="information")
        self.query_one(BalanceCard).fetch_data()
        self.query_one(LatestTransactionsTable).fetch_data()
        self.query_one(TopMerchantsTable).fetch_data()
        self.query_one(TopCategoriesTable).fetch_data()
        self.query_one(MonthlySpendChart).fetch_data()
        self.query_one(LastMonthCategoryChart).fetch_data()

    def watch_pay_day(self, pay_day: int) -> None:
        try:
            self.query_one(PayDayCalendar).pay_day = pay_day
        except Exception:
            logger.debug("Pay day set before mounting")
