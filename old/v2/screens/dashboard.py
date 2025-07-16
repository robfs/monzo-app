"""Dashboard screen for the Monzo app v2 with reactive components."""

import logging

from core import AppEvent
from textual.app import ComposeResult
from textual.containers import Container
from textual.containers import Grid
from textual.reactive import reactive
from textual.widgets import Footer
from textual.widgets import Header
from widgets.dashboard import BalanceCard
from widgets.dashboard import DataStatusCard
from widgets.dashboard import LatestTransactionsTable
from widgets.dashboard import MonthlySpendChart
from widgets.dashboard import SettingsStatusCard
from widgets.dashboard import SpendingComparisonChart
from widgets.dashboard import TopCategoriesTable
from widgets.dashboard import TopMerchantsTable
from widgets.dashboard.charts import PayDayVisualization
from widgets.dashboard.info_cards import EventLogCard
from widgets.dashboard.info_cards import SystemInfoCard

from screens.base import StateAwareScreen

logger = logging.getLogger(__name__)


class DashboardScreen(StateAwareScreen):
    """Main dashboard screen with reactive analytics components."""

    BINDINGS = [
        ("r", "refresh_data", "Refresh"),
        ("d", "toggle_debug", "Debug"),
        ("t", "show_tables", "Tables"),
        ("c", "show_charts", "Charts"),
    ]

    # Reactive properties for dashboard state
    _debug_mode: reactive[bool] = reactive(False)
    _current_view: reactive[str] = reactive("overview")

    def compose(self) -> ComposeResult:
        """Compose the dashboard screen layout."""
        yield Header()

        with Container(classes="dashboard-container"):
            with Grid(classes="dashboard-grid", id="main-grid"):
                # Top row - key metrics
                yield BalanceCard(classes="balance-widget")
                yield DataStatusCard(classes="status-widget")
                yield SettingsStatusCard(classes="settings-widget")

                # Second row - charts
                yield MonthlySpendChart(classes="monthly-chart")
                yield SpendingComparisonChart(classes="comparison-chart")
                yield PayDayVisualization(classes="payday-widget")

                # Third row - tables
                yield TopCategoriesTable(classes="categories-table")
                yield TopMerchantsTable(classes="merchants-table")
                transactions_table = LatestTransactionsTable(
                    classes="transactions-table"
                )
                transactions_table.limit = 10
                yield transactions_table

                # Debug panel (hidden by default)
                yield SystemInfoCard(classes="debug-widget hidden")
                event_log = EventLogCard(classes="event-log hidden")
                event_log.max_events = 5
                yield event_log

        yield Footer()

    def on_mount(self) -> None:
        """Called when dashboard is mounted."""
        super().on_mount()
        self.title = "Monzo Analytics Dashboard"
        self.sub_title = "Reactive Financial Analytics"
        logger.info("Dashboard screen mounted and ready")

    def on_state_updated(self) -> None:
        """Called when application state is updated."""
        logger.debug("Dashboard: State updated - refreshing components")
        # Individual components will update automatically via reactive properties

    def on_data_updated(self, event: AppEvent) -> None:
        """Handle data update events."""
        super().on_data_updated(event)
        logger.info("Dashboard: Data updated event received")
        self.notify("Data refreshed successfully", severity="information")

    def on_data_loading(self, event: AppEvent) -> None:
        """Handle data loading events."""
        super().on_data_loading(event)
        logger.info("Dashboard: Data loading started")
        self.notify("Refreshing data...", timeout=2)

    def on_data_error(self, event: AppEvent) -> None:
        """Handle data error events."""
        super().on_data_error(event)
        error_msg = "Failed to load data"
        if event.data and "error" in event.data:
            error_msg = f"Data error: {event.data['error']}"

        logger.error(f"Dashboard: {error_msg}")
        self.notify(error_msg, severity="error")

    def on_settings_changed(self, event: AppEvent) -> None:
        """Handle settings change events."""
        super().on_settings_changed(event)
        logger.info(
            "Dashboard: Settings changed - components will update automatically"
        )
        self.notify("Settings updated", severity="information")

    def on_exclusions_changed(self, event: AppEvent) -> None:
        """Handle exclusions change events."""
        super().on_exclusions_changed(event)
        logger.info("Dashboard: Exclusions changed - charts will recalculate")
        self.notify("Category exclusions updated", severity="information")

    def on_refresh_requested(self, event: AppEvent) -> None:
        """Handle refresh request events."""
        super().on_refresh_requested(event)
        logger.info("Dashboard: Refresh requested")
        self.action_refresh_data()

    def action_refresh_data(self) -> None:
        """Action to refresh all data."""
        logger.info("Dashboard: Manual refresh requested")
        self.app_state.request_refresh()

    def action_toggle_debug(self) -> None:
        """Toggle debug panel visibility."""
        self._debug_mode = not self._debug_mode

        debug_widgets = self.query(".debug-widget, .event-log")
        for widget in debug_widgets:
            if self._debug_mode:
                widget.remove_class("hidden")
            else:
                widget.add_class("hidden")

        status = "enabled" if self._debug_mode else "disabled"
        self.notify(f"Debug mode {status}", severity="information")
        logger.info(f"Dashboard: Debug mode {status}")

    def action_show_tables(self) -> None:
        """Focus on table widgets."""
        self._current_view = "tables"
        self.notify("Focusing on data tables", timeout=1)

        # Could implement view switching logic here
        tables = self.query(".categories-table, .merchants-table, .transactions-table")
        for table in tables:
            table.remove_class("dimmed")

    def action_show_charts(self) -> None:
        """Focus on chart widgets."""
        self._current_view = "charts"
        self.notify("Focusing on charts", timeout=1)

        # Could implement view switching logic here
        charts = self.query(".monthly-chart, .comparison-chart")
        for chart in charts:
            chart.remove_class("dimmed")

    def watch_is_loading(self, is_loading: bool) -> None:
        """React to loading state changes."""
        if is_loading:
            self.add_class("loading")
        else:
            self.remove_class("loading")

    def watch_transaction_count(self, count: int) -> None:
        """React to transaction count changes."""
        if count > 0:
            logger.debug(f"Dashboard: {count} transactions available")

    def watch_balance(self, balance: float) -> None:
        """React to balance changes."""
        logger.debug(f"Dashboard: Balance updated to £{balance:,.2f}")

    def watch_exclusions_count(self, count: int) -> None:
        """React to exclusions count changes."""
        logger.debug(f"Dashboard: {count} categories excluded from analysis")
