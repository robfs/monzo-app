"""Module containing the TransactionsTable class."""

import logging

from textual.reactive import reactive
from textual.widgets import DataTable

from .data_view import DataView

__all__ = ["LatestTransactionsView"]


logger = logging.getLogger(__name__)


class LatestTransactionsView(DataTable, DataView):
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
    LIMIT 100
    """
    _column_names = ["Date", "Time", "Name", "Category", "Amount"]
    _column_widths = [10, 8, 22, 16, 7]
    data: reactive[list[tuple]] = reactive([])

    def on_mount(self) -> None:
        self.border_title = "Latest Transactions"
        self.cursor_type = "row"
        self.zebra_stripes = True

    def watch_data(self, data: list[tuple]) -> None:
        """Load transaction data from the app's DuckDB connection."""
        # Clear existing data
        self.clear(columns=True)
        for column, width in zip(
            self.column_names(), self.column_widths(), strict=True
        ):
            self.add_column(column, width=width)

        # Add rows to the table
        for transaction in data:
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

        logger.info(f"Loaded {len(data)} transactions into table")

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
