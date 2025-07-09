"""BalanceCard widget."""

import logging

from textual.app import ComposeResult
from textual.containers import Container
from textual.widgets import Digits

from .data_widget import DataWidget

__all__ = ["BalanceCard"]

logger = logging.getLogger(__name__)


class BalanceCard(Container, DataWidget):
    """Widget to display the balance."""

    sql_query = "select sum(amount) from transactions"

    def compose(self) -> ComposeResult:
        logger.debug("Composing BalanceCard")
        self.border_title = "Balance"
        self.add_class("card")
        yield Digits("0.00")

    def update_balance(self) -> None:
        if not (self.data and self.data[0]):
            return
        row = self.data[0]
        value = row[0] or 0
        string_value = f"{value:,.0f}" if value >= 1000 else f"{value:,.2f}"
        self.query_one(Digits).update(string_value)

    def watch_data(self, data: list[tuple]) -> None:
        logger.info("Updating BalanceCard")
        self.update_balance()
