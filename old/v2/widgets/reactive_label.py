"""Reactive label widgets for demonstrating state flow."""

import logging
from collections.abc import Callable
from typing import Any

from core import AppEvent
from textual.app import ComposeResult
from textual.reactive import reactive
from textual.widgets import Label

from widgets.base import StateAwareWidget

logger = logging.getLogger(__name__)


class ReactiveLabel(StateAwareWidget):
    """A label that updates reactively based on application state."""

    # Reactive properties
    text_value: reactive[str] = reactive("")
    prefix: reactive[str] = reactive("")
    suffix: reactive[str] = reactive("")
    format_func: reactive[Callable | None] = reactive(None)
    state_key: reactive[str | None] = reactive(None)
    current_value: reactive[Any] = reactive(None)

    def compose(self) -> ComposeResult:
        """Compose the widget."""
        self._label = Label()
        yield self._label

    def on_mount(self) -> None:
        """Called when widget is mounted."""
        super().on_mount()
        # Update display after mount
        self.update_display()

    def update_display(self) -> None:
        """Update the display text."""
        if not hasattr(self, "_label") or self._label is None:
            return

        # Use the already formatted text_value directly
        display_text = self.text_value

        # Add prefix and suffix
        full_text = f"{self.prefix}{display_text}{self.suffix}"
        self._label.update(full_text)

    def set_value(self, value: Any) -> None:
        """Set the value to display."""
        # Store the original value
        self.current_value = value

        # For display purposes, we need to apply formatting to the original value
        # not the string representation
        if self.format_func:
            try:
                formatted_value = self.format_func(value)
                new_value = str(formatted_value)
            except Exception as e:
                logger.error(f"Error applying format function: {e}")
                new_value = str(value)
        else:
            new_value = str(value)

        if new_value != self.text_value:
            self.text_value = new_value

    def watch_text_value(self, value: str) -> None:
        """React to text value changes."""
        self.update_display()

    def watch_prefix(self, prefix: str) -> None:
        """React to prefix changes."""
        self.update_display()

    def watch_suffix(self, suffix: str) -> None:
        """React to suffix changes."""
        self.update_display()

    def watch_format_func(self, func: Callable | None) -> None:
        """React to format function changes."""
        self.update_display()


class StateLabel(ReactiveLabel):
    """A label that automatically syncs with a specific state property."""

    def on_mount(self) -> None:
        """Called when widget is mounted."""
        super().on_mount()
        # Initial sync with state
        self._sync_with_state()

    def _sync_with_state(self) -> None:
        """Sync with the current state value."""
        if self.state_key and hasattr(self.app_state, self.state_key):
            value = getattr(self.app_state, self.state_key)
            logger.debug(f"StateLabel({self.state_key}): Syncing value: {value}")
            self.set_value(value)

    def on_data_updated(self, event: AppEvent) -> None:
        """Handle data update events."""
        logger.debug(f"StateLabel({self.state_key}): Data updated event received")
        self._sync_with_state()

    def on_data_loading(self, event: AppEvent) -> None:
        """Handle data loading events."""
        logger.debug(f"StateLabel({self.state_key}): Data loading event received")
        self._sync_with_state()

    def on_data_error(self, event: AppEvent) -> None:
        """Handle data error events."""
        logger.debug(f"StateLabel({self.state_key}): Data error event received")
        self._sync_with_state()

    def on_settings_changed(self, event: AppEvent) -> None:
        """Handle settings change events."""
        logger.debug(f"StateLabel({self.state_key}): Settings changed event received")
        self._sync_with_state()

    def on_exclusions_changed(self, event: AppEvent) -> None:
        """Handle exclusions change events."""
        logger.debug(f"StateLabel({self.state_key}): Exclusions changed event received")
        self._sync_with_state()

    def on_app_ready(self, event: AppEvent) -> None:
        """Handle app ready events."""
        logger.debug(f"StateLabel({self.state_key}): App ready event received")
        self._sync_with_state()


class CounterLabel(StateLabel):
    """A specialized label for displaying counts."""

    # Reactive properties for counter configuration
    singular: reactive[str] = reactive("item")
    plural: reactive[str] = reactive("items")

    def compose(self) -> ComposeResult:
        """Compose the widget and set up formatter."""

        def count_formatter(value):
            try:
                count = int(value)
                unit = self.singular if count == 1 else self.plural
                return f"{count:,} {unit}"
            except (ValueError, TypeError):
                return str(value)

        self.format_func = count_formatter
        yield from super().compose()


class CurrencyLabel(StateLabel):
    """A specialized label for displaying currency amounts."""

    # Reactive property for currency symbol
    currency_symbol: reactive[str] = reactive("£")

    def compose(self) -> ComposeResult:
        """Compose the widget and set up formatter."""

        def currency_formatter(value):
            try:
                amount = float(value)
                return f"{self.currency_symbol}{amount:,.2f}"
            except (ValueError, TypeError):
                return str(value)

        self.format_func = currency_formatter
        yield from super().compose()


class StatusLabel(StateLabel):
    """A specialized label for displaying status information."""

    # Reactive property for status mapping
    status_map: reactive[dict] = reactive({})

    def compose(self) -> ComposeResult:
        """Compose the widget and set up formatter."""

        def status_formatter(value):
            return self.status_map.get(value, str(value))

        self.format_func = status_formatter
        yield from super().compose()


class TimeLabel(StateLabel):
    """A specialized label for displaying time information."""

    # Reactive property for time format
    time_format: reactive[str] = reactive("%H:%M:%S")

    def compose(self) -> ComposeResult:
        """Compose the widget and set up formatter."""

        def time_formatter(value):
            if value is None:
                return "Never"
            if hasattr(value, "strftime"):
                return value.strftime(self.time_format)
            return str(value)

        self.format_func = time_formatter
        yield from super().compose()


class LoadingLabel(StateLabel):
    """A specialized label that shows loading status."""

    # Reactive properties for loading text
    loading_text: reactive[str] = reactive("Loading...")
    idle_text: reactive[str] = reactive("Ready")

    def on_mount(self) -> None:
        """Called when widget is mounted."""
        # Set default state_key for loading labels
        if not self.state_key:
            self.state_key = "is_loading"
        logger.debug(f"LoadingLabel mounted with state_key: {self.state_key}")

        # Set up the formatter after reactive properties are initialized
        self.format_func = self._create_loading_formatter()

        super().on_mount()

    def _create_loading_formatter(self) -> Callable:
        """Create the loading formatter function."""

        def loading_formatter(value):
            try:
                is_loading = bool(value)
                # Access the reactive properties directly
                loading_text_val = self.loading_text
                idle_text_val = self.idle_text
                result = loading_text_val if is_loading else idle_text_val
                logger.debug(
                    f"LoadingLabel({self.state_key}): Formatting {value} -> {result}"
                )
                return result
            except (ValueError, TypeError) as e:
                logger.error(
                    f"LoadingLabel({self.state_key}): Error formatting value {value}: {e}"
                )
                return str(value)

        return loading_formatter

    def compose(self) -> ComposeResult:
        """Compose the widget."""
        yield from super().compose()

    def watch_loading_text(self, loading_text: str) -> None:
        """React to loading text changes."""
        # Recreate formatter when loading text changes
        self.format_func = self._create_loading_formatter()
        self.update_display()

    def watch_idle_text(self, idle_text: str) -> None:
        """React to idle text changes."""
        # Recreate formatter when idle text changes
        self.format_func = self._create_loading_formatter()
        self.update_display()
