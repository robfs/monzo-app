"""Module containing the base DataWidget class."""

import logging
import re
from typing import Any

from duckdb import DuckDBPyConnection
from textual.reactive import reactive
from textual.widget import Widget

logger = logging.getLogger(__name__)


class DataWidget(Widget):
    """Base class for widgets that display data."""

    _camel_regex = re.compile(r"(?<=[a-z0-9])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])")
    _snake_regex = re.compile(r"_+")

    data: reactive[list[tuple]] = reactive([])
    sql_query: reactive[str] = reactive("select 1;")
    sql_params: reactive[dict[str, Any]] = reactive({})
    _column_names: reactive[list[str]] = reactive([])

    @property
    def db(self) -> DuckDBPyConnection | None:
        if self.app.db:
            return self.app.db
        logger.error("Database connection not available")

    def run_query(self, query: str, *args, **kwargs) -> list[tuple]:
        if not self.db:
            return []
        return self.db.sql(query, *args, **kwargs).fetchall()

    # def watch_sql_params(self, params: list):
    #     if params:
    #         self.fetch_data()

    def update(self, /, **kwargs) -> None:
        for key, value in kwargs.items():
            setattr(self, key, value)
        self.fetch_data()

    def fetch_data(self) -> None:
        logger.info(f"Updating data on {self.__class__.__name__}")
        params = {}
        for name, param in self.sql_params.items():
            if f"${name}" in self.sql_query:
                params[name] = param
        self.data = self.run_query(self.sql_query, params=params)
        if not self.data:
            logger.info(f"No data returned for {self.__class__.__name__}")

    def query_columns(self, query: str, *args, **kwargs) -> list[str]:
        if not self.db:
            return []
        return self.db.sql(query, *args, **kwargs).columns

    def fetch_column_names(self) -> None:
        params = {}
        for name, param in self.sql_params.items():
            if f"${name}" in self.sql_query:
                params[name] = param
        self._column_names = self.query_columns(self.sql_query, params=params)

    @property
    def column_names(self) -> list[str]:
        if not self._column_names:
            self.fetch_column_names()
        return self._column_names

    def _camel_to_human_readable(self, camel_string: str) -> str:
        """Convert a camel case string to a human readable capitalised string."""
        # Insert space before uppercase letters that follow lowercase letters or digits
        # and handle sequences of uppercase letters properly
        return self._camel_regex.sub(r" ", camel_string)

    def _snake_to_human_readable(self, snake_string: str) -> str:
        """Convert a snake_case string to a human readable capitalised string."""
        # Replace underscores with spaces and capitalize
        return self._snake_regex.sub(r" ", snake_string)

    def pretty_columns(self) -> list[str]:
        camel_converted = map(self._camel_to_human_readable, self.column_names)
        snake_converted = map(self._snake_to_human_readable, camel_converted)
        return list(map(str.title, snake_converted))
