"""Module containing the SQLScreen class."""

import logging

from textual import work
from textual.app import ComposeResult
from textual.containers import Container
from textual.reactive import reactive
from textual.screen import Screen
from textual.widgets import Button
from textual.widgets import Footer
from textual.widgets import Header
from textual.widgets import TextArea
from textual.worker import get_current_worker

from ..views import CodeEditorView
from ..views import CustomSQLChartView
from ..views import CustomSQLTableView

logger = logging.getLogger(__name__)


class SQLScreen(Screen):
    """The custom SQL screen."""

    BINDINGS = [("ctrl+enter", "run_query", "Run Query")]

    sql_query = reactive("")

    def compose(self) -> ComposeResult:
        container = Container(self.code_editor(), self.table_view(), self.chart_view())
        container.border_title = "Custom SQL"
        container.border_subtitle = "Visualise custom SQL queries"
        yield Footer()
        yield Header()
        yield container

    def on_mount(self) -> None:
        self.on_text_area_changed(TextArea.Changed(TextArea()))

    def code_editor(self) -> CodeEditorView:
        return CodeEditorView()

    def chart_view(self) -> CustomSQLChartView:
        return CustomSQLChartView()

    def table_view(self) -> CustomSQLTableView:
        return CustomSQLTableView()

    def on_text_area_changed(self, event: TextArea.Changed) -> None:
        self.sql_query = self.query_one(TextArea).text

    def update_all(self):
        try:
            self.query_one(CustomSQLTableView).update(self.sql_query)
        except Exception as e:
            logger.error(f"Error updating table view: {e}")
            self.app.notify(f"Error updating table view: {e}", severity="error")
        try:
            self.query_one(CustomSQLChartView).update(self.sql_query)
        except Exception as e:
            logger.error(f"Error updating chart view: {e}")
            self.app.notify(f"Error updating chart view: {e}", severity="error")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "run-query":
            self.update_all()

    def action_run_query(self):
        self.update_all()

    @work(exclusive=True, thread=True)
    def on_monzo_monzo_transactions_initialized(self, message) -> None:
        """Handle MonzoTransactionsInitialized message."""
        worker = get_current_worker()
        if not worker.is_cancelled:
            logger.info("Refreshing custom data.")
            self.update_all()
