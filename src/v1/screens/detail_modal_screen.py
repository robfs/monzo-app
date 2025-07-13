"""Module containing the DetailModalScreen to more in depth analysis."""

import logging

from textual.app import ComposeResult
from textual.containers import Container
from textual.reactive import reactive
from textual.screen import ModalScreen
from textual.widgets import DataTable
from textual.widgets import Footer
from textual_plotext import PlotextPlot

from ..widgets.data_widget import DataWidget

__all__ = ["DetailModalScreen"]

logger = logging.getLogger(__name__)


class MonthlyChart(Container, DataWidget):
    """Widget to display the monthly spend chart."""

    exclusions: reactive[tuple] = reactive(())

    def compose(self) -> ComposeResult:
        logger.debug("Composing MonthlySpendChart")
        self.border_title = "Monthly Spend Chart"
        self.add_class("card")
        yield PlotextPlot()

    def update_monthly_spend(self) -> None:
        charts = self.query(PlotextPlot)
        if not charts:
            return
        chart = charts.first()
        plt = chart.plt
        plt.clear_data()
        chart.refresh()
        months = [row[0] for row in self.data[-12:]]
        amounts = [float(row[1]) for row in self.data[-12:]]
        plt.clear_figure()
        plt.bar(months, amounts, width=5 / 7)
        chart.refresh()

    def watch_sql_params(self, params) -> None:
        if "type" not in params:
            return
        column = params["type"]
        self.sql_query = f"select expenseMonth, sum(amount * -1), expenseMonthDate from transactions where {column} = $item group by expenseMonth, expenseMonthDate order by expenseMonthDate"
        self.fetch_data()
        logger.info("Updating Monthly Spend")
        self.update_monthly_spend()


class TransactionTable(Container, DataWidget):
    def compose(self) -> ComposeResult:
        self.border_title = "Transactions"
        self.sql_params = {}
        self.add_class("card")
        yield DataTable(zebra_stripes=True, cursor_type="row")

    def update_categories(self) -> None:
        table = self.query_one(DataTable)
        table.clear(columns=True)
        table.add_columns(*self.pretty_columns())
        table.add_rows(self.data)

    def format_row(self, row: tuple) -> list:
        new_row = list(row)
        new_row[1] = f"£{new_row[1]:,.2f}"
        return new_row

    def formatted_data(self) -> list[list]:
        return [self.format_row(row) for row in self.data]

    def watch_sql_params(self, params) -> None:
        if "type" not in params:
            return
        column = params["type"]
        self.sql_query = f"select expenseMonth, name, amount * -1 as amount from transactions where {column} = $item order by expenseMonthDate desc, amount desc"
        self.fetch_data()
        self.fetch_column_names()
        logger.info("Updating Top Categories")
        self.update_categories()


class DetailModalScreen(ModalScreen):
    BINDINGS = [("escape", "app.pop_screen", "Close")]
    sql_params = reactive({})

    def compose(self) -> ComposeResult:
        container = Container(MonthlyChart(), TransactionTable())
        container.border_title = "Group Analysis"
        container.add_class("screen")
        yield container
        yield Footer()

    def on_mount(self) -> None:
        monthly_chart = self.query_one(MonthlyChart)
        table = self.query_one(TransactionTable)
        monthly_chart.sql_params = self.sql_params
        table.sql_params = self.sql_params

    def watch_sql_params(self, params) -> None:
        charts = self.query(MonthlyChart)
        tables = self.query(TransactionTable)
        if not tables:
            return
        monthly_chart = charts.first()
        table = tables.first()
        monthly_chart.sql_params = self.sql_params
        table.sql_params = self.sql_params
