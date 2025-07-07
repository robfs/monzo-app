"""Module containing the SpendingLastMonth."""

import logging

from textual_plotext import PlotextPlot

from .data_view import DataView

__all__ = ["SpendingLastMonthChartView"]

logger = logging.getLogger(__name__)


class SpendingLastMonthChartView(PlotextPlot, DataView):
    """Class representing the SpendingLastMonth."""

    sql_query = """
        SELECT
            category,
            SUM(amount * -1) AS total
        FROM
            transactions
        WHERE
            amount < 0
        AND
            strftime('%Y-%m', date) = (select strftime('%Y-%m', date - INTERVAL '1 month') from transactions order by date desc limit 1)
        GROUP BY
            category
        ORDER BY
            total
    """

    def on_mount(self) -> None:
        self.border_title = "Monthly Spending Chart"

    def replot(self) -> None:
        data = self.data
        logger.info(f"Plotting {len(data)} rows")
        months = [row[0] for row in data[:12]]
        amounts = [float(row[1]) for row in data[:12]]
        self.plt.clear_figure()
        self.plt.bar(months, amounts, orientation="horizontal")
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
