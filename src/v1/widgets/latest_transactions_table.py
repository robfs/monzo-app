"""LatestTransactionsTable widget."""

import logging

from textual.app import ComposeResult
from textual.containers import Container
from textual.widgets import Placeholder

__all__ = ["LatestTransactionsTable"]

logger = logging.getLogger(__name__)


class LatestTransactionsTable(Container):
    """Widget to display the latest transactions."""

    def compose(self) -> ComposeResult:
        logger.debug("Composing LatestTransactionsTable")
        self.border_title = "Latest Transactions"
        self.add_class("card")
        yield Placeholder("Latest Transactions")
