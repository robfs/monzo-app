"""Module containing the chart view for visualising custom SQL queries."""

from textual_plotext import PlotextPlot

from .data_view import DataView

__all__ = ["CustomSQLChartView"]


class CustomSQLChartView(PlotextPlot, DataView):
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
