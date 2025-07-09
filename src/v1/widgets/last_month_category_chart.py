"""LastMonthCategoryChart widget."""

import logging

from textual.app import ComposeResult
from textual.containers import Container
from textual.widgets import Placeholder

__all__ = ["LastMonthCategoryChart"]

logger = logging.getLogger(__name__)


class LastMonthCategoryChart(Container):
    """Widget to display the last month's category chart."""

    def compose(self) -> ComposeResult:
        logger.debug("Composing LastMonthCategoryChart")
        self.border_title = "Last Month's Category Chart"
        self.add_class("card")
        yield Placeholder("Last Month's Category Chart")
