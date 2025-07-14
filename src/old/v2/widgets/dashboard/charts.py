"""Chart widgets for displaying spending data and trends."""

import logging
from textual.app import ComposeResult
from textual.containers import Container, Vertical, Horizontal
from textual.widgets import Label

from widgets.base import StateAwareWidget
from widgets.reactive_label import CurrencyLabel, CounterLabel, StatusLabel
from core import AppEvent, get_data_service

logger = logging.getLogger(__name__)


class MonthlySpendChart(StateAwareWidget):
    """Widget displaying monthly spending trends as a reactive chart simulation."""

    def compose(self) -> ComposeResult:
        """Compose the monthly spend chart widget."""
        with Container(classes="chart-container"):
            yield Label("Monthly Spending Trend", classes="chart-title")

            # Simulated chart area
            with Container(classes="chart-area"):
                yield Label("📊 Chart Visualization Area", classes="chart-placeholder")
                yield Label(
                    "(Reactive data updates shown below)", classes="chart-subtitle"
                )

            # Reactive data display
            with Vertical(classes="chart-data"):
                with Horizontal():
                    yield Label("Current Month:", classes="data-label")
                    monthly_label = CurrencyLabel(classes="data-value")
                    monthly_label.state_key = "monthly_spend"
                    monthly_label.currency_symbol = "£"
                    yield monthly_label

                with Horizontal():
                    yield Label("Exclusions Applied:", classes="data-label")
                    exclusions_label = CounterLabel(classes="data-value")
                    exclusions_label.state_key = "exclusions"
                    exclusions_label.singular = "category"
                    exclusions_label.plural = "categories"
                    yield exclusions_label

                with Horizontal():
                    yield Label("Data Points:", classes="data-label")
                    transactions_label = CounterLabel(classes="data-value")
                    transactions_label.state_key = "transaction_count"
                    transactions_label.singular = "transaction"
                    transactions_label.plural = "transactions"
                    yield transactions_label

    def on_mount(self) -> None:
        """Called when widget is mounted."""
        super().on_mount()
        self.border_title = "Monthly Spending"
        self.add_class("chart-widget")

    def on_data_updated(self, event: AppEvent) -> None:
        """Handle data update events."""
        logger.debug("MonthlySpendChart: Data updated")
        # Reactive labels will update automatically

    def on_exclusions_changed(self, event: AppEvent) -> None:
        """Handle exclusions change events."""
        logger.debug("MonthlySpendChart: Exclusions changed")
        # Simulate chart recalculation with exclusions
        data_service = get_data_service()
        if event.data and "exclusions" in event.data:
            exclusions = event.data["exclusions"]
            logger.info(f"Chart recalculating with {len(exclusions)} exclusions")


class SpendingComparisonChart(StateAwareWidget):
    """Widget displaying spending comparison across categories."""

    def on_mount(self) -> None:
        """Called when widget is mounted."""
        super().on_mount()
        if not hasattr(self, "_comparison_data"):
            self._comparison_data = []

    def compose(self) -> ComposeResult:
        """Compose the spending comparison chart widget."""
        with Container(classes="chart-container"):
            yield Label("Category Comparison", classes="chart-title")

            # Simulated chart area
            with Container(classes="chart-area"):
                yield Label("📈 Comparison Chart Area", classes="chart-placeholder")
                yield Label("(Top spending categories)", classes="chart-subtitle")

            # Dynamic category display
            with Vertical(classes="category-list", id="category-container"):
                yield Label("Loading categories...", classes="loading-text")

    def on_mount(self) -> None:
        """Called when widget is mounted."""
        super().on_mount()
        self.border_title = "Category Spending"
        self.add_class("chart-widget")
        self._update_categories()

    def on_data_updated(self, event: AppEvent) -> None:
        """Handle data update events."""
        logger.debug("SpendingComparisonChart: Data updated")
        self._update_categories()

    def on_exclusions_changed(self, event: AppEvent) -> None:
        """Handle exclusions change events."""
        logger.debug("SpendingComparisonChart: Exclusions changed")
        self._update_categories()

    def _update_categories(self) -> None:
        """Update the category display with current data."""
        try:
            data_service = get_data_service()
            exclusions = self.app_state.exclusions

            # Get top categories (excluding the excluded ones)
            top_categories = data_service.get_top_categories(
                limit=5, exclude=exclusions
            )

            # Update display
            container = self.query_one("#category-container")
            container.remove_children()

            if top_categories:
                for i, (category, amount, count) in enumerate(top_categories):
                    bar_width = min(int((amount / top_categories[0][1]) * 20), 20)
                    bar = "█" * bar_width + "░" * (20 - bar_width)

                    category_display = (
                        f"{i + 1}. {category:<12} {bar} £{amount:,.2f} ({count} txns)"
                    )
                    container.mount(Label(category_display, classes="category-item"))
            else:
                container.mount(Label("No data available", classes="no-data"))

        except Exception as e:
            logger.error(f"Error updating categories: {e}")
            container = self.query_one("#category-container")
            container.remove_children()
            container.mount(Label(f"Error: {e}", classes="error-text"))


class PayDayVisualization(StateAwareWidget):
    """Widget showing pay day calendar simulation."""

    def compose(self) -> ComposeResult:
        """Compose the pay day visualization widget."""
        with Container(classes="calendar-container"):
            yield Label("Pay Day Calendar", classes="chart-title")

            with Vertical(classes="calendar-info"):
                with Horizontal():
                    yield Label("Pay Day:", classes="data-label")
                    payday_label = StatusLabel(classes="data-value")
                    payday_label.state_key = "pay_day"
                    payday_label.suffix = " of the month"
                    yield payday_label

                yield Label("📅 Calendar Visualization", classes="calendar-placeholder")
                yield Label("(Pay day highlighting)", classes="calendar-subtitle")

    def on_mount(self) -> None:
        """Called when widget is mounted."""
        super().on_mount()
        self.border_title = "Pay Day"
        self.add_class("calendar-widget")

    def on_settings_changed(self, event: AppEvent) -> None:
        """Handle settings change events."""
        logger.debug("PayDayVisualization: Pay day settings changed")
        # Calendar will update automatically via reactive state
