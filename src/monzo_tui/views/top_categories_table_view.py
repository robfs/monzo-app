"""Module containing the TopCategoriesTableView class."""

from textual.widgets import DataTable

from .data_view import DataView

__all__ = ["TopCategoriesTableView"]


class TopCategoriesTableView(DataTable, DataView):
    """A placeholder widget for the category table."""

    sql_query = """
    select category, sum(amount * -1) as amount, count(amount) as txns
    from transactions
    where expenseMonthDate = (select max(expenseMonthDate) from transactions)
    group by category
    order by amount desc
    """

    def on_mount(self) -> None:
        self.border_title = "Top Categories"
        self.cursor_type = "row"
        self.zebra_stripes = True

    def watch_data(self, data: list[tuple[str, str]]) -> None:
        self.clear(columns=True)
        self.add_columns(*self.pretty_columns())
        for row in data:
            self.add_row(row[0], f"£ {row[1]:,.2f}", str(row[2]))
