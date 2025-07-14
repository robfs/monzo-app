"""Base screen classes for the Monzo app v2."""

import logging
from typing import Any, Callable, Optional
from textual.screen import Screen, ModalScreen
from textual.reactive import reactive

from core import get_app_state, get_event_bus, EventType, AppEvent

logger = logging.getLogger(__name__)


class BaseScreen(Screen):
    """Base screen class with state management and event handling."""

    # Reactive properties for screen state
    _is_mounted: reactive[bool] = reactive(False)

    def on_mount(self) -> None:
        """Called when screen is mounted."""
        # Initialize state management if not already done
        if not hasattr(self, "_app_state"):
            self._app_state = get_app_state()
        if not hasattr(self, "_event_bus"):
            self._event_bus = get_event_bus()
        if not hasattr(self, "_subscriptions"):
            self._subscriptions = []

        self._is_mounted = True
        self.setup_subscriptions()
        logger.debug(f"{self.__class__.__name__} mounted")

    def on_unmount(self) -> None:
        """Called when screen is unmounted."""
        self._is_mounted = False
        self.cleanup_subscriptions()
        logger.debug(f"{self.__class__.__name__} screen unmounted")

    def setup_subscriptions(self) -> None:
        """Override this method to set up event subscriptions."""
        # Subscribe to common events
        self.subscribe(EventType.DATA_UPDATED, self.on_data_updated)
        self.subscribe(EventType.DATA_LOADING, self.on_data_loading)
        self.subscribe(EventType.DATA_ERROR, self.on_data_error)
        self.subscribe(EventType.SETTINGS_CHANGED, self.on_settings_changed)
        self.subscribe(EventType.EXCLUSIONS_CHANGED, self.on_exclusions_changed)
        self.subscribe(EventType.REFRESH_REQUESTED, self.on_refresh_requested)

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
    def app_state(self):
        """Get the application state."""
        return self._app_state

    @property
    def is_mounted(self) -> bool:
        """Check if screen is currently mounted."""
        return self._is_mounted

    # Event handlers - override in subclasses
    def on_data_updated(self, event: AppEvent) -> None:
        """Handle data update events."""
        pass

    def on_data_loading(self, event: AppEvent) -> None:
        """Handle data loading events."""
        pass

    def on_data_error(self, event: AppEvent) -> None:
        """Handle data error events."""
        pass

    def on_settings_changed(self, event: AppEvent) -> None:
        """Handle settings change events."""
        pass

    def on_exclusions_changed(self, event: AppEvent) -> None:
        """Handle exclusions change events."""
        pass

    def on_refresh_requested(self, event: AppEvent) -> None:
        """Handle refresh request events."""
        pass


class BaseModalScreen(ModalScreen):
    """Base modal screen class with state management."""

    # Reactive properties for modal screen state
    _is_mounted: reactive[bool] = reactive(False)

    def on_mount(self) -> None:
        """Called when screen is mounted."""
        # Initialize state management if not already done
        if not hasattr(self, "_app_state"):
            self._app_state = get_app_state()
        if not hasattr(self, "_event_bus"):
            self._event_bus = get_event_bus()
        if not hasattr(self, "_subscriptions"):
            self._subscriptions = []

        self._is_mounted = True
        self.setup_subscriptions()
        logger.debug(f"{self.__class__.__name__} mounted")

    def on_unmount(self) -> None:
        """Called when modal screen is unmounted."""
        self._is_mounted = False
        self.cleanup_subscriptions()
        logger.debug(f"{self.__class__.__name__} modal unmounted")

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
    def app_state(self):
        """Get the application state."""
        return self._app_state

    @property
    def is_mounted(self) -> bool:
        """Check if modal is currently mounted."""
        return self._is_mounted


class ConfigurableModalScreen(BaseModalScreen):
    """Modal screen that can be configured with callback functions."""

    # Reactive properties for callback functions
    on_save_callback: reactive[Optional[Callable]] = reactive(None)
    on_cancel_callback: reactive[Optional[Callable]] = reactive(None)

    def on_mount(self) -> None:
        """Called when modal screen is mounted."""
        super().on_mount()
        # Initialize callbacks if not already set
        if not hasattr(self, "_on_save_callback"):
            self._on_save_callback = self.on_save_callback
        if not hasattr(self, "_on_cancel_callback"):
            self._on_cancel_callback = self.on_cancel_callback

    def action_save(self) -> None:
        """Save action - calls callback if provided."""
        try:
            result = self.get_save_data()
            if self._on_save_callback:
                self._on_save_callback(result)
            self.dismiss(result)
        except Exception as e:
            logger.error(f"Error in save action: {e}")
            self.app.notify(f"Save error: {e}", severity="error")

    def action_cancel(self) -> None:
        """Cancel action - calls callback if provided."""
        if self._on_cancel_callback:
            self._on_cancel_callback()
        self.dismiss(None)

    def get_save_data(self) -> Any:
        """Override this method to return data to save."""
        return None


class StateAwareScreen(BaseScreen):
    """Screen that automatically updates when application state changes."""

    # Reactive properties that mirror app state
    is_loading: reactive[bool] = reactive(False)
    transaction_count: reactive[int] = reactive(0)
    balance: reactive[float] = reactive(0.0)
    exclusions_count: reactive[int] = reactive(0)

    def on_mount(self) -> None:
        """Called when screen is mounted."""
        super().on_mount()
        self._sync_with_state()

    def _sync_with_state(self) -> None:
        """Synchronize local state with application state."""
        self.is_loading = self.app_state.is_loading
        self.transaction_count = self.app_state.transaction_count
        self.balance = self.app_state.balance
        self.exclusions_count = len(self.app_state.exclusions)

    def on_data_updated(self, event: AppEvent) -> None:
        """Handle data update events."""
        self._sync_with_state()
        self.on_state_updated()

    def on_settings_changed(self, event: AppEvent) -> None:
        """Handle settings change events."""
        self._sync_with_state()
        self.on_state_updated()

    def on_exclusions_changed(self, event: AppEvent) -> None:
        """Handle exclusions change events."""
        self._sync_with_state()
        self.on_state_updated()

    def on_state_updated(self) -> None:
        """Called when state is updated. Override in subclasses."""
        pass

    def watch_is_loading(self, is_loading: bool) -> None:
        """React to loading state changes."""
        pass

    def watch_transaction_count(self, count: int) -> None:
        """React to transaction count changes."""
        pass

    def watch_balance(self, balance: float) -> None:
        """React to balance changes."""
        pass

    def watch_exclusions_count(self, count: int) -> None:
        """React to exclusions count changes."""
        pass
