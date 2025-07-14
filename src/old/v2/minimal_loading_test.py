#!/usr/bin/env python3
"""Minimal test to debug LoadingLabel reactive behavior."""

import asyncio
import logging
import sys
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from textual.app import App, ComposeResult
from textual.widgets import Label

from widgets.reactive_label import LoadingLabel
from core import get_app_state

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)


class MinimalApp(App):
    """Minimal app to test LoadingLabel."""

    def compose(self) -> ComposeResult:
        yield Label("Minimal LoadingLabel Test", id="title")
        yield LoadingLabel(id="test-loading")

    async def on_mount(self) -> None:
        """Called when app is mounted."""
        logger.info("MinimalApp mounted")

        # Get the loading widget and app state
        loading_widget = self.query_one("#test-loading", LoadingLabel)
        app_state = get_app_state()

        logger.info(f"Initial app_state.is_loading: {app_state.is_loading}")
        logger.info(f"Initial loading widget text: {loading_widget._label.renderable}")
        logger.info(f"Loading widget state_key: {loading_widget.state_key}")
        logger.info(
            f"Loading widget current_value: {getattr(loading_widget, 'current_value', 'NOT SET')}"
        )

        # Wait a bit then test manual state changes
        self.set_timer(2.0, self.test_state_changes)

    async def test_state_changes(self) -> None:
        """Test manual state changes."""
        loading_widget = self.query_one("#test-loading", LoadingLabel)
        app_state = get_app_state()

        logger.info("=== TEST 1: Setting loading to True ===")
        app_state.update_loading_state(True)
        await asyncio.sleep(0.5)
        logger.info(f"After True - app_state.is_loading: {app_state.is_loading}")
        logger.info(f"After True - widget text: {loading_widget._label.renderable}")
        logger.info(
            f"After True - widget current_value: {getattr(loading_widget, 'current_value', 'NOT SET')}"
        )

        logger.info("=== TEST 2: Setting loading to False ===")
        app_state.update_loading_state(False)
        await asyncio.sleep(0.5)
        logger.info(f"After False - app_state.is_loading: {app_state.is_loading}")
        logger.info(f"After False - widget text: {loading_widget._label.renderable}")
        logger.info(
            f"After False - widget current_value: {getattr(loading_widget, 'current_value', 'NOT SET')}"
        )

        logger.info("=== TEST 3: Manual widget sync ===")
        # Manually trigger sync
        loading_widget._sync_with_state()
        await asyncio.sleep(0.1)
        logger.info(
            f"After manual sync - widget text: {loading_widget._label.renderable}"
        )
        logger.info(
            f"After manual sync - widget current_value: {getattr(loading_widget, 'current_value', 'NOT SET')}"
        )

        logger.info("=== TEST 4: Direct property access ===")
        logger.info(
            f"Widget loading_text: {getattr(loading_widget, 'loading_text', 'NOT SET')}"
        )
        logger.info(
            f"Widget idle_text: {getattr(loading_widget, 'idle_text', 'NOT SET')}"
        )

        # Test the formatter directly
        formatter = getattr(loading_widget, "format_func", None)
        if formatter:
            logger.info(f"Formatter with True: {formatter(True)}")
            logger.info(f"Formatter with False: {formatter(False)}")
        else:
            logger.info("No formatter found!")


async def main():
    """Main function to run the test."""
    app = MinimalApp()

    async with app.run_test() as pilot:
        # Let the test run for 10 seconds
        await pilot.pause(10.0)


if __name__ == "__main__":
    asyncio.run(main())
