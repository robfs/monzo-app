"""LastMonthCategoryChart widget."""

import logging

from textual.app import ComposeResult
from textual.containers import Container
from textual_plotext import PlotextPlot

from .data_widget import DataWidget

__all__ = ["LastMonthCategoryChart"]

logger = logging.getLogger(__name__)


class LastMonthCategoryChart(Container, DataWidget):
    """Widget to display the last month's category chart."""

    def compose(self) -> ComposeResult:
        self.sql_query = "select category, sum(amount * -1) as total from transactions where amount < 0 and expenseMonthDate = (select max(expenseMonthDate) - interval 1 month from transactions) group by category order by total"
        logger.debug("Composing LastMonthCategoryChart")
        self.border_title = "Spending Last Month"
        self.add_class("card")
        yield PlotextPlot()

    def update_last_month(self) -> None:
        chart = self.query_one(PlotextPlot)
        plt = chart.plt
        plt.clear_data()
        chart.refresh()
        categories = [row[0] for row in self.data]
        amounts = [float(row[1]) for row in self.data]
        plt.clear_figure()
        plt.bar(categories, amounts, orientation="horizontal")
        chart.refresh()

    def watch_data(self, data: list[tuple]) -> None:
        logger.info("Updating last month's category chart")
        self.update_last_month()
