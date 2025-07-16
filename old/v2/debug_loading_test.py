#!/usr/bin/env python3
"""Simple debug test to understand the loading state issue."""

import asyncio
import logging
import sys
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from core import EventType
from core import get_app_state
from core import get_data_service
from core import get_event_bus
from textual.app import App
from textual.app import ComposeResult
from textual.containers import Vertical
from textual.widgets import Label
from widgets.reactive_label import LoadingLabel

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)


class DebugLoadingApp(App):
    """Simple app to debug loading state issues."""

    def compose(self) -> ComposeResult:
        with Vertical():
            yield Label("Debug Loading State Test", id="title")
            yield LoadingLabel(id="loading-1")
            yield LoadingLabel(id="loading-2")
            yield Label("", id="debug-info")

    async def on_mount(self) -> None:
        """Called when app is mounted."""
        logger.info("DebugLoadingApp mounted")

        # Get services
        self.app_state = get_app_state()
        self.data_service = get_data_service()

        # Show initial state
        await self.update_debug_info()

        # Wait a bit then test state changes
        self.set_timer(2.0, self.test_loading_states)

    async def update_debug_info(self) -> None:
        """Update debug information display."""
        debug_label = self.query_one("#debug-info", Label)
        loading1 = self.query_one("#loading-1", LoadingLabel)
        loading2 = self.query_one("#loading-2", LoadingLabel)

        info = (
            f"AppState.is_loading: {self.app_state.is_loading}\n"
            f"DataService.is_loading: {self.data_service.is_loading()}\n"
            f"Loading1 text: {loading1._label.renderable}\n"
            f"Loading2 text: {loading2._label.renderable}"
        )

        debug_label.update(info)
        logger.info(f"Debug info updated: {info}")

    async def test_loading_states(self) -> None:
        """Test loading state transitions."""
        logger.info("=== Starting loading state test ===")

        # Test 1: Set loading to True via AppState
        logger.info("TEST 1: Setting loading to True via AppState")
        self.app_state.update_loading_state(True)
        await asyncio.sleep(0.5)
        await self.update_debug_info()

        # Test 2: Set loading to False via AppState
        logger.info("TEST 2: Setting loading to False via AppState")
        self.app_state.update_loading_state(False)
        await asyncio.sleep(0.5)
        await self.update_debug_info()

        # Test 3: Trigger data refresh
        logger.info("TEST 3: Triggering data refresh")
        await self.data_service.refresh_data()
        await asyncio.sleep(0.5)
        await self.update_debug_info()

        # Test 4: Manual event emission
        logger.info("TEST 4: Manual event emission")
        event_bus = get_event_bus()
        event_bus.emit_simple(
            EventType.DATA_LOADING,
            data={"state": {"is_loading": True}},
            source="DebugTest",
        )
        await asyncio.sleep(0.5)
        await self.update_debug_info()

        event_bus.emit_simple(
            EventType.DATA_UPDATED,
            data={"state": {"is_loading": False}},
            source="DebugTest",
        )
        await asyncio.sleep(0.5)
        await self.update_debug_info()

        logger.info("=== Loading state test complete ===")


async def run_debug_test():
    """Run the debug test."""
    app = DebugLoadingApp()

    async with app.run_test() as pilot:
        # Let the app run for a bit to see the state changes
        await pilot.pause(10.0)  # Wait 10 seconds to see all state changes


def run_simple_debug():
    """Run a simple debug test without the app."""
    print("=== Simple Debug Test ===")

    # Get services
    app_state = get_app_state()
    data_service = get_data_service()
    event_bus = get_event_bus()

    print(f"Initial AppState.is_loading: {app_state.is_loading}")
    print(f"Initial DataService.is_loading: {data_service.is_loading()}")

    # Test state changes
    print("\n1. Setting AppState loading to True...")
    app_state.update_loading_state(True)
    print(f"   AppState.is_loading: {app_state.is_loading}")

    print("\n2. Setting AppState loading to False...")
    app_state.update_loading_state(False)
    print(f"   AppState.is_loading: {app_state.is_loading}")

    # Test event emission
    print("\n3. Testing event emission...")

    received_events = []

    def test_callback(event):
        received_events.append(event.type.value)
        print(f"   Received event: {event.type.value}")

    event_bus.subscribe(EventType.DATA_LOADING, test_callback)
    event_bus.subscribe(EventType.DATA_UPDATED, test_callback)

    print("   Emitting DATA_LOADING...")
    event_bus.emit_simple(EventType.DATA_LOADING, source="DebugTest")

    print("   Emitting DATA_UPDATED...")
    event_bus.emit_simple(EventType.DATA_UPDATED, source="DebugTest")

    print(f"   Events received: {received_events}")

    # Clean up
    event_bus.unsubscribe(EventType.DATA_LOADING, test_callback)
    event_bus.unsubscribe(EventType.DATA_UPDATED, test_callback)


async def main():
    """Main debug function."""
    print("Starting Loading State Debug")
    print("=" * 50)

    # First run simple debug
    run_simple_debug()

    print("\n" + "=" * 50)
    print("Running Textual app debug test...")

    # Then run the app debug
    await run_debug_test()


if __name__ == "__main__":
    # Run simple debug first
    run_simple_debug()

    print("\nTo run the full app debug test, use:")
    print("python debug_loading_test.py --app")

    if len(sys.argv) > 1 and sys.argv[1] == "--app":
        asyncio.run(main())
