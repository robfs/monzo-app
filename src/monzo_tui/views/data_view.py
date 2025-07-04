"""Module containing an abstract data view for processing transaction data."""

import logging

from textual.reactive import reactive

__all__ = ["DataView"]

logger = logging.getLogger(__name__)


class DataView:
    """An abstract data view for processing transaction data."""

    sql_query: str = "SELECT 1 from transactions"
    _columns_names: list[str] = []
    data: reactive[list[tuple]] = reactive([])

    def db_connection(self):
        """Return the database connection from the app as a context manager."""
        return self.app.get_db_connection()

    def load_data(self) -> None:
        """Load transaction data from the app's DuckDB connection."""
        # Get database connection from app using context manager
        with self.db_connection() as db_connection:
            if not db_connection:
                logger.info("No database connection available")
                return

            # Query transactions data
            self.data = db_connection.sql(self.sql_query).fetchall()

            if not self.data:
                logger.info("No data found.")
                return

    def refresh_data(self) -> None:
        """Refresh the data."""
        self.load_data()

    def get_column_names_from_query(self) -> list[str]:
        with self.db_connection() as db_connection:
            if not db_connection:
                logger.info("No database connection available")
                return []

            # Query column names
            return db_connection.sql(self.sql_query).columns

    def column_names(self) -> list[str]:
        """Return the column names of the query."""
        if not self._columns_names:
            self._columns_names = self.get_column_names_from_query()
        return self._columns_names
