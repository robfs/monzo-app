"""Module defining the dashboard screen."""

import logging
import os

from textual.app import ComposeResult
from textual.containers import Container
from textual.message import Message
from textual.reactive import reactive
from textual.screen import Screen
from textual.widgets import Footer, SelectionList
from textual.widgets import Header

from ..widgets import BalanceCard
from ..widgets import LatestTransactionsTable
from ..widgets import Logo
from ..widgets import MonthlySpendChart
from ..widgets import PayDayCalendar
from ..widgets import SpendingComparisonChart
from ..widgets import TopCategoriesTable
from ..widgets import TopMerchantsTable

__all__ = ["DashboardScreen"]


logger = logging.getLogger(__name__)


class DashboardScreen(Screen):
    """Dashboard screen."""

    pay_day = reactive(int(os.getenv("MONZO_PAY_DAY", "31")))
    exclusions = reactive([])

    def compose(self) -> ComposeResult:
        container = Container(
            Logo(),
            SpendingComparisonChart(),
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

    def update_all(self) -> None:
        self.query_one(BalanceCard).update()
        self.query_one(LatestTransactionsTable).update()
        self.query_one(TopMerchantsTable).update()
        self.query_one(TopCategoriesTable).update()
        self.query_one(MonthlySpendChart).update(exclusions=self.exclusions)
        self.query_one(SpendingComparisonChart).update()

    def on_monzo_transactions_available(self, message: Message) -> None:
        self.app.notify(f"{self.__class__.__name__}: {message}", severity="information")
        self.update_all()

    def watch_exclusions(self, exclusions: list[str]) -> None:
        self.query_one(MonthlySpendChart).update(exclusions=exclusions)
        self.query_one(SpendingComparisonChart).update(exclusions=exclusions)

    def get_exclusions(self) -> None:
        screen = self.app.get_screen("exclusions")
        selection_lists = screen.query(SelectionList)
        if selection_lists:
            self.exclusions = selection_lists.first().selected

    def watch_pay_day(self, pay_day: int) -> None:
        try:
            self.query_one(PayDayCalendar).pay_day = pay_day
        except Exception:
            logger.debug("Pay day set before mounting")
