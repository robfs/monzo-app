"""Module containing the MonthlyChartView."""

import logging

from textual_plotext import PlotextPlot

from .data_view import DataView

__all__ = ["MonthlyChartView"]

logger = logging.getLogger(__name__)


class MonthlyChartView(PlotextPlot, DataView):
    """Class representing the MonthlyChartView."""

    sql_query = """
        SELECT
            strftime('%Y-%m', date) AS month,
            SUM(amount * -1) AS total_spent
        FROM
            transactions
        WHERE
            amount < 0
        AND
            date > '2022-12-31'
        GROUP BY
            month
        ORDER BY
            month desc
    """

    def on_mount(self) -> None:
        self.border_title = "Monthly Spending Chart"

    def replot(self) -> None:
        data = self.data
        logger.info(f"Plotting {len(data)} rows")
        months = [row[0] for row in data[:12]]
        amounts = [float(row[1]) for row in data[:12]]
        self.plt.clear_figure()
        self.plt.bar(months, amounts)
        self.refresh()

    def update(self) -> None:
        logger.info("Clearing chart data")
        self.plt.clear_data()
        logger.info("Refreshing empty chart")
        self.refresh()
        logger.info("Loading data")
        self.load_data()
        logger.info("Replotting chart")
        self.replot()
