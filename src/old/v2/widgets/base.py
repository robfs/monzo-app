"""Base widget classes for reactive behavior."""

import logging
from typing import Any, Callable, Optional
from textual.widget import Widget
from textual.reactive import reactive

from core import get_app_state, get_event_bus, EventType, AppEvent

logger = logging.getLogger(__name__)


class ReactiveWidget(Widget):
    """Base widget class with reactive capabilities."""

    # Reactive properties for event management
    _is_mounted: reactive[bool] = reactive(False)

    def on_mount(self) -> None:
        """Called when widget is mounted."""
        # Initialize event system if not already done
        if not hasattr(self, "_event_bus"):
            self._event_bus = get_event_bus()
        if not hasattr(self, "_subscriptions"):
            self._subscriptions = []

        self._is_mounted = True
        self.setup_subscriptions()
        logger.debug(f"{self.__class__.__name__} mounted")

    def on_unmount(self) -> None:
        """Called when widget is unmounted."""
        self._is_mounted = False
        self.cleanup_subscriptions()
        logger.debug(f"{self.__class__.__name__} unmounted")

    def setup_subscriptions(self) -> None:
        """Override this method to set up event subscriptions."""
        pass

    def cleanup_subscriptions(self) -> None:
        """Clean up event subscriptions."""
        for event_type, callback in self._subscriptions:
            self._event_bus.unsubscribe(event_type, callback)
        self._subscriptions.clear()

    def subscribe(
        self, event_type: EventType, callback: Callable[[AppEvent], None]
    ) -> None:
        """Subscribe to an event type."""
        self._event_bus.subscribe(event_type, callback)
        self._subscriptions.append((event_type, callback))

    def emit(self, event_type: EventType, data: Any = None) -> None:
        """Emit an event."""
        self._event_bus.emit_simple(
            event_type, data=data, source=self.__class__.__name__
        )

    @property
    def is_mounted(self) -> bool:
        """Check if widget is currently mounted."""
        return self._is_mounted


class StateAwareWidget(ReactiveWidget):
    """Widget that automatically syncs with application state."""

    def setup_subscriptions(self) -> None:
        """Set up standard state subscriptions."""
        # Initialize app state if not already done
        if not hasattr(self, "_app_state"):
            self._app_state = get_app_state()

        super().setup_subscriptions()

        # Subscribe to key state changes
        self.subscribe(EventType.DATA_UPDATED, self.on_data_updated)
        self.subscribe(EventType.DATA_LOADING, self.on_data_loading)
        self.subscribe(EventType.DATA_ERROR, self.on_data_error)
        self.subscribe(EventType.SETTINGS_CHANGED, self.on_settings_changed)
        self.subscribe(EventType.EXCLUSIONS_CHANGED, self.on_exclusions_changed)
        self.subscribe(EventType.APP_READY, self.on_app_ready)

    def on_data_updated(self, event: AppEvent) -> None:
        """Handle data update events. Override in subclasses."""
        pass

    def on_data_loading(self, event: AppEvent) -> None:
        """Handle data loading events. Override in subclasses."""
        pass

    def on_data_error(self, event: AppEvent) -> None:
        """Handle data error events. Override in subclasses."""
        pass

    def on_settings_changed(self, event: AppEvent) -> None:
        """Handle settings change events. Override in subclasses."""
        pass

    def on_exclusions_changed(self, event: AppEvent) -> None:
        """Handle exclusions change events. Override in subclasses."""
        pass

    def on_app_ready(self, event: AppEvent) -> None:
        """Handle app ready events. Override in subclasses."""
        pass

    @property
    def app_state(self):
        """Get the application state."""
        return self._app_state


class DataWidget(StateAwareWidget):
    """Base class for widgets that display data with query capabilities."""

    # Reactive properties for data management
    data: reactive[list] = reactive([])
    is_loading: reactive[bool] = reactive(False)
    error_message: reactive[Optional[str]] = reactive(None)
    last_updated: reactive[Optional[str]] = reactive(None)

    def on_mount(self) -> None:
        """Called when widget is mounted."""
        super().on_mount()
        if not hasattr(self, "_query_func"):
            self._query_func: Optional[Callable] = None

    def set_query_function(self, func: Callable) -> None:
        """Set the function used to query data."""
        self._query_func = func
        if self.is_mounted:
            self.refresh_data()

    def refresh_data(self) -> None:
        """Refresh widget data using the query function."""
        if not self._query_func:
            logger.warning(f"{self.__class__.__name__}: No query function set")
            return

        try:
            self.is_loading = True
            self.error_message = None

            # Execute query function
            result = self._query_func()
            self.data = result if isinstance(result, list) else []

            self.is_loading = False
            self.last_updated = "Just now"
            logger.debug(
                f"{self.__class__.__name__}: Data refreshed, {len(self.data)} items"
            )

        except Exception as e:
            self.is_loading = False
            self.error_message = str(e)
            logger.error(f"{self.__class__.__name__}: Error refreshing data: {e}")

    def on_data_updated(self, event: AppEvent) -> None:
        """Refresh data when global data is updated."""
        self.refresh_data()

    def watch_data(self, data: list) -> None:
        """React to data changes. Override in subclasses."""
        pass

    def watch_is_loading(self, is_loading: bool) -> None:
        """React to loading state changes. Override in subclasses."""
        pass

    def watch_error_message(self, error: Optional[str]) -> None:
        """React to error changes. Override in subclasses."""
        if error:
            logger.error(f"{self.__class__.__name__}: {error}")
