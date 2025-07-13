"""TopCategoriesTable widget."""

import logging

from textual.app import ComposeResult
from textual.containers import Container
from textual.widgets import DataTable

from .data_widget import DataWidget

__all__ = ["TopCategoriesTable"]

logger = logging.getLogger(__name__)


class TopCategoriesTable(Container, DataWidget):
    """Widget to display the top categories."""

    def compose(self) -> ComposeResult:
        self.sql_query = "select category, sum(amount * -1) as amount, count(amount) as txns from transactions where expenseMonthDate = (select max(expenseMonthDate) from transactions) group by category order by amount desc"
        logger.debug("Composing TopCategoriesTable")
        self.border_title = "Top Categories"
        self.add_class("card")
        yield DataTable(
            zebra_stripes=True, cursor_type="row", id="top-categories-table"
        )

    def update_categories(self) -> None:
        table = self.query_one(DataTable)
        table.clear(columns=True)
        table.add_columns(*self.pretty_columns())
        table.add_rows(self.formatted_data())

    def format_row(self, row: tuple) -> list:
        new_row = list(row)
        new_row[1] = f"£{new_row[1]:,.2f}"
        return new_row

    def formatted_data(self) -> list[list]:
        return [self.format_row(row) for row in self.data]

    def watch_data(self, data: list[tuple]) -> None:
        logger.info("Updating Top Categories")
        self.update_categories()
