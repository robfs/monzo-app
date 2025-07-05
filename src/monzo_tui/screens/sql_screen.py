"""Module containing the SQLScreen class."""

import logging

from textual import work
from textual.app import ComposeResult
from textual.containers import Container
from textual.reactive import reactive
from textual.screen import Screen
from textual.widgets import Footer
from textual.widgets import Header, TextArea, Static, Button, DataTable
from textual.worker import get_current_worker
from textual_plotext import PlotextPlot

from ..views import DataView


logger = logging.getLogger(__name__)


class SQLTextView(Static):
    """A custom text area widget for displaying SQL queries."""

    def compose(self) -> ComposeResult:
        query = "select\n\tcategory,\n\tsum(amount) as total_amount\nfrom transactions\ngroup by category\norder by total_amount desc"
        yield TextArea.code_editor(query, language="sql", theme="css")
        yield Button("Run Query", variant="success", id="run-query")

    def on_mount(self) -> None:
        self.border_title = "SQL Editor"


class TableView(DataTable, DataView):
    """A custom placeholder widget for displaying table data."""

    def on_mount(self) -> None:
        self.border_title = "Table View"
        self.zebra_stripes = True
        self.cursor_type = "row"

    def update(self, query: str) -> None:
        self.clear(columns=True)
        self._column_names = self.get_column_names_from_query(query)
        columns = self.pretty_columns()
        data = self.run_query(query)

        self.add_columns(*columns)
        self.add_rows(data)


class ChartView(PlotextPlot, DataView):
    """A custom placeholder widget for displaying chart data."""

    def on_mount(self) -> None:
        self.border_title = "Chart View"

    def replot(self) -> None:
        data = self.data
        columns = self.pretty_columns()
        self.plt.bar([row[0] for row in data], [float(row[1]) for row in data])
        self.plt.title(f"{columns[1]} vs {columns[0]}")
        self.refresh()

    def update(self, query: str) -> None:
        self.plt.clear_data()
        self.refresh()
        self._column_names = self.get_column_names_from_query(query)
        self.data = self.run_query(query)
        self.replot()


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

    def code_editor(self) -> SQLTextView:
        return SQLTextView()

    def chart_view(self) -> ChartView:
        return ChartView()

    def table_view(self) -> TableView:
        return TableView()

    def on_text_area_changed(self, event: TextArea.Changed) -> None:
        self.sql_query = self.query_one(TextArea).text

    def update_all(self):
        try:
            self.query_one(TableView).update(self.sql_query)
        except Exception as e:
            logger.error(f"Error updating table view: {e}")
            self.app.notify(f"Error updating table view: {e}", severity="error")
        try:
            self.query_one(ChartView).update(self.sql_query)
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
