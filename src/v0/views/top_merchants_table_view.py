"""Module containing the TopMerchantsTableView class."""

from textual.widgets import DataTable

from .data_view import DataView

__all__ = ["TopMerchantsTableView"]


class TopMerchantsTableView(DataTable, DataView):
    """A placeholder widget for the category table."""

    sql_query = """
    select name, min(category) as category, sum(amount * -1) as amount, count(amount) as txns
    from transactions
    where expenseMonthDate = (select max(expenseMonthDate) from transactions)
    group by name
    order by amount desc
    """

    def on_mount(self) -> None:
        self.border_title = "Top Merchants"
        self.cursor_type = "row"
        self.zebra_stripes = True

    def watch_data(self, data: list[tuple[str, str]]) -> None:
        self.clear(columns=True)
        self.add_columns(*self.pretty_columns())
        for row in data:
            self.add_row(row[0], row[1], f"£ {row[2]:,.2f}", str(row[3]))
