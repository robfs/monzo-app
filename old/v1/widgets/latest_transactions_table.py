"""LatestTransactionsTable widget."""

import logging

from textual.app import ComposeResult
from textual.containers import Container
from textual.widgets import DataTable

from .data_widget import DataWidget

__all__ = ["LatestTransactionsTable"]

logger = logging.getLogger(__name__)


class LatestTransactionsTable(Container, DataWidget):
    """Widget to display the latest transactions."""

    def compose(self) -> ComposeResult:
        self.sql_query = "select expenseMonth, date, time, name, category, amount * -1 as amount from transactions order by date desc, time desc"
        logger.debug("Composing LatestTransactionsTable")
        self.border_title = "Latest Transactions"
        self.add_class("card")
        yield DataTable(zebra_stripes=True, cursor_type="row")

    def update_transactions(self) -> None:
        table = self.query_one(DataTable)
        table.clear(columns=True)
        table.add_columns(*self.pretty_columns())
        table.add_rows(self.formatted_data())

    def format_row(self, row: tuple) -> list:
        new_row = list(row)
        new_row[2] = new_row[2].strftime("%H:%M")
        new_row[5] = f"£{new_row[5]:,.2f}"
        return new_row

    def formatted_data(self) -> list[list]:
        return [self.format_row(row) for row in self.data]

    def watch_data(self, data: list[tuple]) -> None:
        logger.info("Updating LatestTransactionsTable")
        self.update_transactions()
