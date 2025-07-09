"""MonthlySpendChart widget."""

import logging

from textual.app import ComposeResult
from textual.containers import Container
from textual_plotext import PlotextPlot

from .data_widget import DataWidget

__all__ = ["MonthlySpendChart"]

logger = logging.getLogger(__name__)


class MonthlySpendChart(Container, DataWidget):
    """Widget to display the monthly spend chart."""

    def compose(self) -> ComposeResult:
        self.sql_query = "select expenseMonth, sum(amount * -1), expenseMonthDate as total from transactions where amount < 0 group by expenseMonth, expenseMonthDate order by expenseMonthDate"
        logger.debug("Composing MonthlySpendChart")
        self.border_title = "Monthly Spend Chart"
        self.add_class("card")
        yield PlotextPlot()

    def update_monthly_spend(self) -> None:
        chart = self.query_one(PlotextPlot)
        plt = chart.plt
        plt.clear_data()
        chart.refresh()
        months = [row[0] for row in self.data[-12:]]
        amounts = [float(row[1]) for row in self.data[-12:]]
        plt.clear_figure()
        plt.bar(months, amounts)
        chart.refresh()

    def watch_data(self, data: list[tuple]) -> None:
        logger.info("Updating Monthly Spend")
        self.update_monthly_spend()
