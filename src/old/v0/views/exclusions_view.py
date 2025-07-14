from textual.widgets import SelectionList
from .data_view import DataView


__all__ = ["ExclusionsView"]


class ExclusionsView(SelectionList, DataView):
    """View for managing exclusions."""

    def update_exclusions_list(self) -> None:
        self.app.notify("Updating exclusions...")
        with self.db_connection() as conn:
            query = "select distinct category from transactions"
            data = conn.execute(query).fetchall()
        options = {row[0] for row in data}
        self.clear_options()
        self.add_options([(name, name) for name in options])
        # if "Transfers" in options:
        #     self.select("Transfers")
        # if "Income" in options:
        #     self.select("Income")
