"""Module containing the TransactionsTable class."""

import logging

from monzo_py import MonzoTransactions
from textual.reactive import reactive
from textual.widgets import DataTable


logger = logging.getLogger(__name__)


class TransactionsTable(DataTable):
    """A table displaying transactions."""

    def on_mount(self) -> None:
        self.add_columns("Date", "Time", "Name", "Category", "Description", "Amount")
