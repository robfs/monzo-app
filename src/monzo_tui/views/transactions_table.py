"""Module containing the TransactionsTable class."""

import logging

from textual.reactive import reactive
from textual.widgets import DataTable

from .data_view import DataView

__all__ = ["TransactionsTable"]


logger = logging.getLogger(__name__)


class TransactionsTable(DataTable, DataView):
    """A table displaying transactions."""

    sql_query: str = """
    SELECT
        date,
        time,
        name,
        category,
        amount,
        currency
    FROM transactions
    ORDER BY date DESC, time DESC
    """
    _columns_names = ["Date", "Time", "Name", "Category", "Amount"]
    data: reactive[list[tuple]] = reactive([])

    def on_mount(self) -> None:
        self.border_title = "Latest Transactions"

    def watch_data(self) -> None:
        """Load transaction data from the app's DuckDB connection."""
        # Clear existing data
        self.clear(columns=True)
        self.add_columns(*self.column_names())

        # Add rows to the table
        for transaction in self.data:
            # Format the amount with currency symbol
            amount_str = self._format_amount(
                transaction[4],
                transaction[5],  # amount, currency
            )

            self.add_row(
                str(transaction[0]),  # date
                str(transaction[1]),  # time
                str(transaction[2]),  # name
                str(transaction[3]),  # category
                amount_str,
            )

        logger.info(f"Loaded {len(self.data)} transactions into table")

    def _format_amount(self, amount: float, currency: str) -> str:
        """Format amount with appropriate currency symbol and color."""
        if amount is None:
            return ""

        currency_symbols = {
            "GBP": "£",
            "USD": "$",
            "EUR": "€",
        }

        symbol = currency_symbols.get(currency, currency)

        # Format negative amounts (spending) in red, positive (income) in green
        if amount < 0:
            return f"{symbol} {abs(amount):.2f}"
        else:
            return f"{symbol} {amount:.2f}"
