"""Module containing the TransactionsTable class."""

import logging

from textual.widgets import DataTable


logger = logging.getLogger(__name__)


class TransactionsTable(DataTable):
    """A table displaying transactions."""

    def on_mount(self) -> None:
        self.add_columns("Date", "Time", "Name", "Category", "Amount")
        self.border_title = "Latest Transactions"
        self.load_data()

    def load_data(self) -> None:
        """Load transaction data from the app's DuckDB connection."""
        try:
            # Get database connection from app using context manager
            with self.app.get_db_connection() as db_connection:
                if not db_connection:
                    logger.info("No database connection available")
                    return

                # Query transactions data
                transactions = self._get_transactions_data(db_connection)

                if not transactions:
                    logger.info("No transactions found")
                    return

                # Clear existing data
                self.clear()

                # Add rows to the table
                for transaction in transactions:
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

                logger.info(f"Loaded {len(transactions)} transactions into table")

        except Exception as e:
            logger.error(f"Failed to load transaction data: {e}")

    def _get_transactions_data(self, db_connection):
        """Get transaction data from DuckDB connection."""
        try:
            query = """
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
            return db_connection.sql(query).fetchall()
        except Exception as e:
            logger.error(f"Failed to query transactions data: {e}")
            return []

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
            return f"{symbol}{abs(amount):.2f}"
        else:
            return f"{symbol}{amount:.2f}"

    def refresh_data(self) -> None:
        """Refresh the table data."""
        self.load_data()
