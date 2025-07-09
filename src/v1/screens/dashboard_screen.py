"""Module defining the dashboard screen."""

import logging

from textual.app import ComposeResult
from textual.containers import Container
from textual.screen import Screen

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

    def compose(self) -> ComposeResult:
        container = Container(
            Logo(),
            MonthlySpendChart(),
            BalanceCard(),
            LastMonthCategoryChart(),
            TopCategoriesTable(),
            TopMerchantsTable(),
            PayDayCalendar(),
            LatestTransactionsTable(),
            classes="screen",
        )
        container.border_title = "Dashboard"
        container.border_subtitle = "Summary analytics screen"
        yield container
