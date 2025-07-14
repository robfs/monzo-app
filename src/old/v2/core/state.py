"""Central state management system for the Monzo app v2."""

import logging
from typing import Any, Optional
from textual.reactive import reactive

from .events import get_event_bus, EventType, AppEvent
from .settings import get_settings_service
from .data_service import get_data_service

logger = logging.getLogger(__name__)


class AppState:
    """Central state manager for the application."""

    def __init__(self):
        logger.debug("AppState: Constructor called - initializing...")

        # Initialize services as None - will be lazy loaded
        self._event_bus = None
        self._settings_service = None
        self._data_service = None
        self._initialized = False

        # Store strong references to callback methods to prevent garbage collection
        self._callback_refs = []

        # State properties (not reactive here, just regular attributes)
        self.is_ready = False
        self.current_screen = "dashboard"
        self.is_loading = False
        self.last_error = None

        # Data state
        self.data_last_updated = None
        self.transaction_count = 0
        self.balance = 0.0
        self.monthly_spend = 0.0

        # Settings state (mirrors from settings service)
        self.spreadsheet_id = None
        self.pay_day = 31
        self.exclusions = []

        # UI state
        self.theme = "nord"
        self.refresh_in_progress = False

        logger.debug(
            "AppState: Constructor completed - lazy initialization will happen on first access"
        )

    def _ensure_initialized(self) -> None:
        """Ensure the AppState is properly initialized with services."""
        if self._initialized:
            return

        logger.debug("AppState: Lazy initialization starting...")

        # Initialize services
        self._event_bus = get_event_bus()
        self._settings_service = get_settings_service()
        self._data_service = get_data_service()
        logger.debug("AppState: Services initialized")

        # Set up event subscriptions
        self._setup_event_listeners()

        # Initialize state from services
        self._sync_from_services()

        self._initialized = True
        logger.debug("AppState: Lazy initialization completed successfully")

    def _setup_event_listeners(self) -> None:
        """Set up event listeners for state synchronization."""
        logger.debug("AppState: Setting up event listeners")

        # Store strong references to prevent garbage collection
        self._callback_refs = [
            self._on_data_updated,
            self._on_data_loading,
            self._on_data_error,
            self._on_settings_changed,
            self._on_exclusions_changed,
        ]

        # Subscribe to events using instance methods
        self._event_bus.subscribe(EventType.DATA_UPDATED, self._on_data_updated)
        logger.debug("AppState: Subscribed to DATA_UPDATED")
        self._event_bus.subscribe(EventType.DATA_LOADING, self._on_data_loading)
        logger.debug("AppState: Subscribed to DATA_LOADING")
        self._event_bus.subscribe(EventType.DATA_ERROR, self._on_data_error)
        logger.debug("AppState: Subscribed to DATA_ERROR")
        self._event_bus.subscribe(EventType.SETTINGS_CHANGED, self._on_settings_changed)
        logger.debug("AppState: Subscribed to SETTINGS_CHANGED")
        self._event_bus.subscribe(
            EventType.EXCLUSIONS_CHANGED, self._on_exclusions_changed
        )
        logger.debug("AppState: Subscribed to EXCLUSIONS_CHANGED")
        logger.debug("AppState: Event listener setup complete")

    def _on_data_updated(self, event: AppEvent) -> None:
        """Handle data update events."""
        logger.debug("AppState: Received DATA_UPDATED event")
        if event.data and "state" in event.data:
            state = event.data["state"]
            self.is_loading = state.get("is_loading", False)
            self.transaction_count = state.get("transaction_count", 0)
            self.refresh_in_progress = False

            if state.get("last_updated"):
                self.data_last_updated = state["last_updated"].strftime("%H:%M:%S")

            # Update derived data
            self.balance = self._data_service.get_balance()
            self.monthly_spend = self._data_service.state.total_spend_this_month

            logger.debug(
                f"AppState: State updated from data service - is_loading: {self.is_loading}"
            )

            # Emit a state change event so widgets can update
            self._emit_state_change()

    def _on_data_loading(self, event: AppEvent) -> None:
        """Handle data loading events."""
        logger.debug("AppState: Received DATA_LOADING event")
        self.is_loading = True
        self.last_error = None
        self.refresh_in_progress = True
        logger.debug(f"AppState: State loading started - is_loading: {self.is_loading}")

        # Emit a state change event so widgets can update
        self._emit_state_change()

    def _on_data_error(self, event: AppEvent) -> None:
        """Handle data error events."""
        logger.debug("AppState: Received DATA_ERROR event")
        self.is_loading = False
        self.refresh_in_progress = False
        if event.data and "error" in event.data:
            self.last_error = event.data["error"]

        logger.debug(f"AppState: State error occurred - is_loading: {self.is_loading}")

        # Emit a state change event so widgets can update
        self._emit_state_change()

    def _on_settings_changed(self, event: AppEvent) -> None:
        """Handle settings change events."""
        logger.debug("AppState: Received SETTINGS_CHANGED event")
        if event.data and "settings" in event.data:
            settings = event.data["settings"]
            self.spreadsheet_id = settings.get("spreadsheet_id")
            self.pay_day = settings.get("pay_day", 31)
            self.theme = settings.get("theme", "nord")
            logger.debug("AppState: State updated from settings service")

            # Emit a state change event so widgets can update
            self._emit_state_change()

    def _on_exclusions_changed(self, event: AppEvent) -> None:
        """Handle exclusions change events."""
        logger.debug("AppState: Received EXCLUSIONS_CHANGED event")
        if event.data and "exclusions" in event.data:
            self.exclusions = event.data["exclusions"].copy()
            logger.debug(f"AppState: Exclusions updated: {self.exclusions}")

            # Emit a state change event so widgets can update
            self._emit_state_change()

    def _sync_from_services(self) -> None:
        """Synchronize state from underlying services."""
        # Sync from settings service
        settings = self._settings_service.settings
        self.spreadsheet_id = settings.spreadsheet_id
        self.pay_day = settings.pay_day
        self.theme = settings.theme
        self.exclusions = settings.exclusions.copy()

        # Sync from data service
        data_state = self._data_service.state
        self.is_loading = data_state.is_loading
        self.transaction_count = data_state.transaction_count
        self.balance = data_state.balance
        self.monthly_spend = data_state.total_spend_this_month

        if data_state.last_updated:
            self.data_last_updated = data_state.last_updated.strftime("%H:%M:%S")

    def _emit_state_change(self) -> None:
        """Emit a state change event for widgets to react to."""
        # Ensure we're initialized before emitting events
        self._ensure_initialized()

        # Create a custom event type for state changes
        self._event_bus.emit_simple(
            EventType.DATA_UPDATED,  # Reuse this event type
            data={"state_changed": True, "app_state": self},
            source="AppState",
        )

    def set_ready(self) -> None:
        """Mark the application as ready."""
        self._ensure_initialized()

        self.is_ready = True
        self._event_bus.emit_simple(EventType.APP_READY, source="AppState")
        logger.info("Application state marked as ready")

        # Emit state change
        self._emit_state_change()

    def set_current_screen(self, screen_name: str) -> None:
        """Update the current screen."""
        self._ensure_initialized()

        old_screen = self.current_screen
        self.current_screen = screen_name

        self._event_bus.emit_simple(
            EventType.SCREEN_CHANGED,
            data={"from": old_screen, "to": screen_name},
            source="AppState",
        )
        logger.debug(f"Screen changed: {old_screen} -> {screen_name}")

        # Emit state change
        self._emit_state_change()

    def request_refresh(self) -> None:
        """Request a data refresh."""
        self._ensure_initialized()

        if not self.refresh_in_progress:
            self._event_bus.emit_simple(EventType.REFRESH_REQUESTED, source="AppState")
            logger.info("Data refresh requested")

            # Emit state change
            self._emit_state_change()

    def get_state_summary(self) -> dict[str, Any]:
        """Get a summary of current state for debugging."""
        self._ensure_initialized()

        return {
            "is_ready": self.is_ready,
            "current_screen": self.current_screen,
            "is_loading": self.is_loading,
            "transaction_count": self.transaction_count,
            "balance": self.balance,
            "monthly_spend": self.monthly_spend,
            "pay_day": self.pay_day,
            "exclusions_count": len(self.exclusions),
            "last_error": self.last_error,
            "data_last_updated": self.data_last_updated,
        }

    def update_loading_state(self, is_loading: bool) -> None:
        """Update loading state and notify widgets."""
        old_loading = self.is_loading
        self.is_loading = is_loading

        if not is_loading:
            self.refresh_in_progress = False

        if old_loading != is_loading:
            logger.debug(f"Loading state changed: {old_loading} -> {is_loading}")
            self._emit_state_change()

    def update_error_state(self, error: str | None) -> None:
        """Update error state and notify widgets."""
        old_error = self.last_error
        self.last_error = error

        if old_error != error:
            if error:
                logger.error(f"Application error: {error}")
            self._emit_state_change()

    def shutdown(self) -> None:
        """Clean up state on application shutdown."""
        if self._initialized and self._event_bus:
            self._event_bus.emit_simple(EventType.APP_SHUTDOWN, source="AppState")
        logger.info("Application state shutdown")


# Global state instance
logger.debug("Creating global AppState instance...")
_app_state = AppState()
logger.debug("Global AppState instance created")


def get_app_state() -> AppState:
    """Get the global application state instance."""
    # Trigger lazy initialization when first accessed
    _app_state._ensure_initialized()
    return _app_state
