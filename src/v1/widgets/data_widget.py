"""Module containing the base DataWidget class."""

import logging

from duckdb import DuckDBPyConnection
from textual.reactive import reactive
from textual.widget import Widget

logger = logging.getLogger(__name__)


class DataWidget(Widget):
    """Base class for widgets that display data."""

    data: reactive[list[tuple]] = reactive([])
    sql_query = "select 1;"

    @property
    def db(self) -> DuckDBPyConnection | None:
        if self.app.db:
            return self.app.db
        logger.error("Database connection not available")
        self.app.notify("Database connection not available")

    def run_query(self, query: str) -> list[tuple]:
        if not self.db:
            return []
        return self.db.sql(query).fetchall()

    def fetch_data(self) -> None:
        logger.info(f"Updating data on {self.__class__.__name__}")
        self.data = self.run_query(self.sql_query)
        if not self.data:
            logger.info(f"No data returned for {self.__class__.__name__}")
