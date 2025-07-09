"""MonthlySpendChart widget."""

import logging

from textual.app import ComposeResult
from textual.containers import Container
from textual.widgets import Placeholder

__all__ = ["MonthlySpendChart"]

logger = logging.getLogger(__name__)


class MonthlySpendChart(Container):
    """Widget to display the monthly spend chart."""

    def compose(self) -> ComposeResult:
        logger.debug("Composing MonthlySpendChart")
        self.border_title = "Monthly Spend Chart"
        self.add_class("card")
        yield Placeholder("Monthly Spend Chart")
