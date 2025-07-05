"""Module containing the TopMerchantsTableView class."""

from textual.widgets import DataTable

from .data_view import DataView

__all__ = ["TopMerchantsTableView"]


class TopMerchantsTableView(DataTable, DataView):
    """A placeholder widget for the category table."""

    sql_query = """
    select name, sum(amount * -1) as amount, count(amount) as count
    from transactions
    where
    strftime('%Y-%m', date) = (select strftime('%Y-%m', date) from transactions order by date desc limit 1)
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
            self.add_row(row[0], f"£ {row[1]:,.2f}", str(row[2]))
