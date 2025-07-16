"""Event system for reactive communication throughout the application."""

import logging
from collections.abc import Callable
from dataclasses import dataclass
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)


class EventType(Enum):
    """Enumeration of application event types."""

    # Data events
    DATA_UPDATED = "data_updated"
    DATA_LOADING = "data_loading"
    DATA_ERROR = "data_error"

    # Settings events
    SETTINGS_CHANGED = "settings_changed"
    EXCLUSIONS_CHANGED = "exclusions_changed"

    # UI events
    REFRESH_REQUESTED = "refresh_requested"
    SCREEN_CHANGED = "screen_changed"

    # Application events
    APP_READY = "app_ready"
    APP_SHUTDOWN = "app_shutdown"


@dataclass
class AppEvent:
    """Represents an application event."""

    type: EventType
    data: Any = None
    source: str = "unknown"

    def __str__(self) -> str:
        return f"AppEvent(type={self.type.value}, source={self.source})"


class EventBus:
    """Central event bus for application-wide communication."""

    def __init__(self):
        self._subscribers: dict[EventType, set] = {}
        self._event_history: list[AppEvent] = []
        self._max_history = 100

    def subscribe(
        self, event_type: EventType, callback: Callable[[AppEvent], None]
    ) -> None:
        """Subscribe to an event type."""
        if event_type not in self._subscribers:
            self._subscribers[event_type] = set()

        self._subscribers[event_type].add(callback)
        logger.debug(f"Subscribed to {event_type.value}")

    def unsubscribe(
        self, event_type: EventType, callback: Callable[[AppEvent], None]
    ) -> None:
        """Unsubscribe from an event type."""
        if event_type in self._subscribers:
            self._subscribers[event_type].discard(callback)
            logger.debug(f"Unsubscribed from {event_type.value}")

    def emit(self, event: AppEvent) -> None:
        """Emit an event to all subscribers."""
        logger.debug(f"Emitting event: {event}")

        # Add to history
        self._event_history.append(event)
        if len(self._event_history) > self._max_history:
            self._event_history.pop(0)

        # Notify subscribers
        if event.type in self._subscribers:
            dead_callbacks = []
            # Create a copy of the subscribers set to avoid iteration issues
            subscribers_copy = self._subscribers[event.type].copy()
            for callback in subscribers_copy:
                try:
                    callback(event)
                except Exception as e:
                    logger.error(f"Error in event callback: {e}")
                    dead_callbacks.append(callback)

            # Clean up dead callbacks
            for callback in dead_callbacks:
                self._subscribers[event.type].discard(callback)

    def emit_simple(
        self, event_type: EventType, data: Any = None, source: str = "unknown"
    ) -> None:
        """Convenience method to emit an event with simple parameters."""
        event = AppEvent(type=event_type, data=data, source=source)
        self.emit(event)

    def get_recent_events(
        self, event_type: EventType = None, limit: int = 10
    ) -> list[AppEvent]:
        """Get recent events, optionally filtered by type."""
        events = self._event_history

        if event_type:
            events = [e for e in events if e.type == event_type]

        return events[-limit:]

    def clear_history(self) -> None:
        """Clear the event history."""
        self._event_history.clear()


# Global event bus instance
_event_bus = EventBus()


def get_event_bus() -> EventBus:
    """Get the global event bus instance."""
    return _event_bus
