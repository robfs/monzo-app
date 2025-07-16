"""Info card widgets for displaying status and system information."""

import logging

from core import AppEvent
from textual.app import ComposeResult
from textual.containers import Container
from textual.containers import Horizontal
from textual.containers import Vertical
from textual.reactive import reactive
from textual.widgets import Label

from widgets.base import StateAwareWidget
from widgets.reactive_label import CounterLabel
from widgets.reactive_label import CurrencyLabel
from widgets.reactive_label import LoadingLabel
from widgets.reactive_label import StatusLabel
from widgets.reactive_label import TimeLabel

logger = logging.getLogger(__name__)


class DataStatusCard(StateAwareWidget):
    """Widget displaying current data loading and status information."""

    def compose(self) -> ComposeResult:
        """Compose the data status card widget."""
        with Container(classes="status-card"):
            yield Label("Data Status", classes="card-title")

            with Vertical(classes="status-info"):
                # Loading status
                with Horizontal(classes="status-row"):
                    yield Label("Status:", classes="status-label")
                    loading_label = LoadingLabel(classes="status-value")
                    loading_label.loading_text = "🔄 Loading..."
                    loading_label.idle_text = "✅ Ready"
                    yield loading_label

                # Transaction count
                with Horizontal(classes="status-row"):
                    yield Label("Transactions:", classes="status-label")
                    transactions_label = CounterLabel(classes="status-value")
                    transactions_label.state_key = "transaction_count"
                    transactions_label.singular = "record"
                    transactions_label.plural = "records"
                    yield transactions_label

                # Last updated
                with Horizontal(classes="status-row"):
                    yield Label("Updated:", classes="status-label")
                    updated_label = TimeLabel(classes="status-value")
                    updated_label.state_key = "data_last_updated"
                    yield updated_label

                # Current balance
                with Horizontal(classes="status-row"):
                    yield Label("Balance:", classes="status-label")
                    balance_label = CurrencyLabel(classes="status-value")
                    balance_label.state_key = "balance"
                    balance_label.currency_symbol = "£"
                    yield balance_label

    def on_mount(self) -> None:
        """Called when widget is mounted."""
        super().on_mount()
        self.border_title = "Data Overview"
        self.add_class("info-card")

    def on_data_updated(self, event: AppEvent) -> None:
        """Handle data update events."""
        logger.debug("DataStatusCard: Data updated")
        # All reactive labels will update automatically

    def on_data_loading(self, event: AppEvent) -> None:
        """Handle data loading events."""
        logger.debug("DataStatusCard: Data loading started")

    def on_data_error(self, event: AppEvent) -> None:
        """Handle data error events."""
        logger.debug("DataStatusCard: Data error occurred")
        # Could add error display here if needed


class SettingsStatusCard(StateAwareWidget):
    """Widget displaying current application settings and configuration."""

    def compose(self) -> ComposeResult:
        """Compose the settings status card widget."""
        with Container(classes="status-card"):
            yield Label("Settings", classes="card-title")

            with Vertical(classes="settings-info"):
                # Pay day setting
                with Horizontal(classes="status-row"):
                    yield Label("Pay Day:", classes="status-label")
                    payday_label = StatusLabel(classes="status-value")
                    payday_label.state_key = "pay_day"
                    payday_label.suffix = " of month"
                    yield payday_label

                # Theme setting
                with Horizontal(classes="status-row"):
                    yield Label("Theme:", classes="status-label")
                    theme_label = StatusLabel(classes="status-value")
                    theme_label.state_key = "theme"
                    yield theme_label

                # Exclusions count
                with Horizontal(classes="status-row"):
                    yield Label("Exclusions:", classes="status-label")
                    exclusions_label = CounterLabel(classes="status-value")
                    exclusions_label.state_key = "exclusions"
                    exclusions_label.singular = "category"
                    exclusions_label.plural = "categories"
                    yield exclusions_label

                # Configuration status
                with Horizontal(classes="status-row"):
                    yield Label("Config:", classes="status-label")
                    config_label = StatusLabel(classes="status-value")
                    config_label.state_key = "spreadsheet_id"
                    config_label.status_map = {
                        None: "❌ Not configured",
                        "": "❌ Missing ID",
                    }
                    yield config_label

    def on_mount(self) -> None:
        """Called when widget is mounted."""
        super().on_mount()
        self.border_title = "Configuration"
        self.add_class("info-card")
        self._update_config_status()

    def on_settings_changed(self, event: AppEvent) -> None:
        """Handle settings change events."""
        logger.debug("SettingsStatusCard: Settings changed")
        self._update_config_status()

    def on_exclusions_changed(self, event: AppEvent) -> None:
        """Handle exclusions change events."""
        logger.debug("SettingsStatusCard: Exclusions changed")

    def _update_config_status(self) -> None:
        """Update the configuration status display."""
        # Configuration status will be handled automatically by the reactive labels


class SystemInfoCard(StateAwareWidget):
    """Widget displaying system and performance information."""

    def compose(self) -> ComposeResult:
        """Compose the system info card widget."""
        with Container(classes="status-card"):
            yield Label("System Info", classes="card-title")

            with Vertical(classes="system-info"):
                # Current screen
                with Horizontal(classes="status-row"):
                    yield Label("Screen:", classes="status-label")
                    screen_label = StatusLabel(classes="status-value")
                    screen_label.state_key = "current_screen"
                    yield screen_label

                # Application ready status
                with Horizontal(classes="status-row"):
                    yield Label("App Status:", classes="status-label")
                    app_status_label = StatusLabel(classes="status-value")
                    app_status_label.state_key = "is_ready"
                    app_status_label.status_map = {
                        True: "✅ Ready",
                        False: "🔄 Initializing",
                    }
                    yield app_status_label

                # Refresh status
                with Horizontal(classes="status-row"):
                    yield Label("Refresh:", classes="status-label")
                    refresh_label = StatusLabel(classes="status-value")
                    refresh_label.state_key = "refresh_in_progress"
                    refresh_label.status_map = {
                        True: "🔄 In progress",
                        False: "⏸️ Idle",
                    }
                    yield refresh_label

                # Error status
                with Horizontal(classes="status-row"):
                    yield Label("Errors:", classes="status-label")
                    error_label = StatusLabel(classes="status-value")
                    error_label.state_key = "last_error"
                    error_label.status_map = {
                        None: "✅ None",
                        "": "✅ None",
                    }
                    yield error_label

    def on_mount(self) -> None:
        """Called when widget is mounted."""
        super().on_mount()
        self.border_title = "System"
        self.add_class("info-card")

    def on_data_error(self, event: AppEvent) -> None:
        """Handle data error events."""
        logger.debug("SystemInfoCard: Error occurred")


class EventLogCard(StateAwareWidget):
    """Widget displaying recent system events for debugging."""

    # Reactive property for max events
    max_events: reactive[int] = reactive(5)

    def compose(self) -> ComposeResult:
        """Compose the event log card widget."""
        with Container(classes="status-card"):
            yield Label("Recent Events", classes="card-title")

            with Vertical(classes="event-log", id="event-container"):
                yield Label("No events yet...", classes="no-events")

    def on_mount(self) -> None:
        """Called when widget is mounted."""
        super().on_mount()
        self.border_title = "Event Log"
        self.add_class("info-card")

    def on_data_updated(self, event: AppEvent) -> None:
        """Handle data update events."""
        self._add_event_to_log("📊 Data updated")

    def on_data_loading(self, event: AppEvent) -> None:
        """Handle data loading events."""
        self._add_event_to_log("🔄 Loading data...")

    def on_data_error(self, event: AppEvent) -> None:
        """Handle data error events."""
        self._add_event_to_log("❌ Data error")

    def on_settings_changed(self, event: AppEvent) -> None:
        """Handle settings change events."""
        self._add_event_to_log("⚙️ Settings changed")

    def on_exclusions_changed(self, event: AppEvent) -> None:
        """Handle exclusions change events."""
        self._add_event_to_log("🚫 Exclusions updated")

    def _add_event_to_log(self, event_text: str) -> None:
        """Add an event to the log display."""
        try:
            import datetime

            timestamp = datetime.datetime.now().strftime("%H:%M:%S")
            event_display = f"[{timestamp}] {event_text}"

            container = self.query_one("#event-container")

            # Remove "no events" message if present
            try:
                no_events_label = container.query_one(".no-events")
                no_events_label.remove()
            except:
                pass

            # Add new event
            container.mount(Label(event_display, classes="event-item"))

            # Keep only the last N events
            event_items = list(container.query(".event-item"))
            if len(event_items) > self.max_events:
                event_items[0].remove()

        except Exception as e:
            logger.error(f"Error adding event to log: {e}")
