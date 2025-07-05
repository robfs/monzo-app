"""Module containing an abstract data view for processing transaction data."""

import logging
import re

from textual.reactive import reactive

__all__ = ["DataView"]

logger = logging.getLogger(__name__)


class DataView:
    """An abstract data view for processing transaction data."""

    _camel_regex = re.compile(r"(?<=[a-z0-9])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])")
    _snake_regex = re.compile(r"_+")

    sql_query: str = "SELECT 1 from transactions"
    _column_names: list[str] = []
    data: reactive[list[tuple]] = reactive([])

    def db_connection(self):
        """Return the database connection from the app as a context manager."""
        return self.app.get_db_connection()

    def camel_to_human_readable(self, camel_string: str) -> str:
        """Convert a camel case string to a human readable capitalised string."""
        # Insert space before uppercase letters that follow lowercase letters or digits
        # and handle sequences of uppercase letters properly
        return self._camel_regex.sub(r" ", camel_string)

    def snake_to_human_readable(self, snake_string: str) -> str:
        """Convert a snake_case string to a human readable capitalised string."""
        # Replace underscores with spaces and capitalize
        return self._snake_regex.sub(r" ", snake_string)

    def pretty_columns(self) -> list[str]:
        raw_names = self.column_names()
        camel_converted = map(self.camel_to_human_readable, raw_names)
        snake_converted = map(self.snake_to_human_readable, camel_converted)
        return list(map(str.title, snake_converted))

    def run_query(self, query: str) -> list[tuple]:
        """Run a SQL query and return the results."""
        with self.db_connection() as db_connection:
            if not db_connection:
                logger.info("No database connection available")
                return []

            # Query transactions data
            return db_connection.sql(query).fetchall()

    def load_data(self) -> None:
        """Load transaction data from the app's DuckDB connection."""
        # Get database connection from app using context manager
        self.data = self.run_query(self.sql_query) or []
        if not self.data:
            logger.info("No data found.")

    def refresh_data(self) -> None:
        """Refresh the data."""
        self.load_data()

    def get_column_names_from_query(self, query: str) -> list[str]:
        with self.db_connection() as db_connection:
            if not db_connection:
                logger.info("No database connection available")
                return []

            # Query column names
            return db_connection.sql(query).columns

    def column_names(self) -> list[str]:
        """Return the column names of the query."""
        if not self._column_names:
            self._column_names = self.get_column_names_from_query(self.sql_query)
        return self._column_names
