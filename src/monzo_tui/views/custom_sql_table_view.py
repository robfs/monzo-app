"""Module containing the table view for visualising custom SQL queries."""

from textual.widgets import DataTable

from .data_view import DataView

__all__ = ["CustomSQLTableView"]


class CustomSQLTableView(DataTable, DataView):
    """A custom placeholder widget for displaying table data."""

    def on_mount(self) -> None:
        self.border_title = "Table View"
        self.zebra_stripes = True
        self.cursor_type = "row"

    def update(self, query: str) -> None:
        self.clear(columns=True)
        self._column_names = self.get_column_names_from_query(query)
        columns = self.pretty_columns()
        data = self.run_query(query)

        self.add_columns(*columns)
        self.add_rows(data)
