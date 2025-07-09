"""BalanceCard widget."""

import logging

from textual.app import ComposeResult
from textual.containers import Container
from textual.widgets import Placeholder

__all__ = ["BalanceCard"]

logger = logging.getLogger(__name__)


class BalanceCard(Container):
    """Widget to display the balance."""

    def compose(self) -> ComposeResult:
        logger.debug("Composing BalanceCard")
        self.border_title = "Balance"
        self.add_class("card")
        yield Placeholder("Balance")
