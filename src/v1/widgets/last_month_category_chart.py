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
        sub_query: str = "select distinct expenseMonth from transactions order by expenseMonthDate desc limit 2"
        self.sql_query = f"pivot transactions on expenseMonth in ({sub_query}) using sum(amount * -1) group by category order by 3 desc limit 7"
        logger.debug("Composing LastMonthCategoryChart")
        self.border_title = "Spending Last Month"
        self.add_class("card")
        yield PlotextPlot()

    def update_last_month(self) -> None:
        chart = self.query_one(PlotextPlot)
        plt = chart.plt
        plt.clear_data()
        chart.refresh()
        if not self.data:
            return
        columns = self.pretty_columns()
        categories, this_month, last_month = [], [], []
        for row in self.data[::-1]:
            if row[1] or row[2]:
                categories.append(row[0])
                this_month.append(float(row[1] or 0))
                last_month.append(float(row[2] or 0))
        labels = columns[-2:]
        self.app.notify(str(columns))
        plt.clear_figure()
        plt.multiple_bar(
            categories,
            [this_month, last_month],
            orientation="horizontal",
            labels=labels,
        )
        chart.refresh()

    def watch_data(self, data: list[tuple]) -> None:
        logger.info("Updating last month's category chart")
        self.update_last_month()
