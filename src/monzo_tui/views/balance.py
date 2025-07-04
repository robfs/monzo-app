"""Module containing the Balance widget."""

from textual.widgets import Digits

from .data_view import DataView

__all__ = ["Balance"]


class Balance(Digits, DataView):
    """Widget to display the current balance."""

    sql_query = "select sum(amount) from transactions"

    def on_mount(self) -> None:
        self.border_title = "Balance"

    def watch_data(self, data: list[tuple]) -> None:
        if data:
            self.update(f"{data[0][0]:,.2f}")
