#!/usr/bin/env python3
"""Test script to verify loading state behavior without running the interactive app."""

import asyncio
import logging
import sys
import time
from pathlib import Path

# Add the current directory to Python path so we can import our modules
sys.path.insert(0, str(Path(__file__).parent))

from core import EventType
from core import get_app_state
from core import get_data_service
from core import get_event_bus

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)


class LoadingStateMonitor:
    """Monitor for tracking loading state changes."""

    def __init__(self):
        self.events = []
        self.app_state = get_app_state()
        self.data_service = get_data_service()
        self.event_bus = get_event_bus()

        # Subscribe to all relevant events
        self.event_bus.subscribe(EventType.DATA_LOADING, self.on_data_loading)
        self.event_bus.subscribe(EventType.DATA_UPDATED, self.on_data_updated)
        self.event_bus.subscribe(EventType.DATA_ERROR, self.on_data_error)

        # Also track AppState changes
        self._initial_app_state_loading = self.app_state.is_loading
        self._app_state_changes = []

    def on_data_loading(self, event):
        """Track data loading events."""
        state_loading = self.app_state.is_loading
        service_loading = self.data_service.is_loading()

        self.events.append(
            {
                "type": "DATA_LOADING",
                "timestamp": time.time(),
                "app_state_loading": state_loading,
                "service_loading": service_loading,
            }
        )

        print(
            f"🔄 DATA_LOADING - AppState.is_loading: {state_loading}, DataService.is_loading: {service_loading}"
        )

        # Track app state changes
        if state_loading != self._initial_app_state_loading:
            self._app_state_changes.append(
                f"AppState loading changed to {state_loading}"
            )

    def on_data_updated(self, event):
        """Track data updated events."""
        state_loading = self.app_state.is_loading
        service_loading = self.data_service.is_loading()

        self.events.append(
            {
                "type": "DATA_UPDATED",
                "timestamp": time.time(),
                "app_state_loading": state_loading,
                "service_loading": service_loading,
            }
        )

        print(
            f"✅ DATA_UPDATED - AppState.is_loading: {state_loading}, DataService.is_loading: {service_loading}"
        )

        # Track app state changes
        if state_loading != self._initial_app_state_loading:
            self._app_state_changes.append(
                f"AppState loading changed to {state_loading}"
            )

    def on_data_error(self, event):
        """Track data error events."""
        state_loading = self.app_state.is_loading
        service_loading = self.data_service.is_loading()

        self.events.append(
            {
                "type": "DATA_ERROR",
                "timestamp": time.time(),
                "app_state_loading": state_loading,
                "service_loading": service_loading,
            }
        )

        print(
            f"❌ DATA_ERROR - AppState.is_loading: {state_loading}, DataService.is_loading: {service_loading}"
        )

        # Track app state changes
        if state_loading != self._initial_app_state_loading:
            self._app_state_changes.append(
                f"AppState loading changed to {state_loading}"
            )

    def print_summary(self):
        """Print a summary of events."""
        print("\n" + "=" * 60)
        print("LOADING STATE TEST SUMMARY")
        print("=" * 60)

        if not self.events:
            print("❌ No events were recorded!")
            return

        print(f"📊 Total events: {len(self.events)}")

        # Check if we got a complete loading cycle
        loading_events = [e for e in self.events if e["type"] == "DATA_LOADING"]
        updated_events = [e for e in self.events if e["type"] == "DATA_UPDATED"]
        error_events = [e for e in self.events if e["type"] == "DATA_ERROR"]

        print(f"🔄 Loading events: {len(loading_events)}")
        print(f"✅ Updated events: {len(updated_events)}")
        print(f"❌ Error events: {len(error_events)}")

        # Check final states
        final_app_state_loading = self.app_state.is_loading
        final_service_loading = self.data_service.is_loading()

        print("\nFinal States:")
        print(f"  AppState.is_loading: {final_app_state_loading}")
        print(f"  DataService.is_loading: {final_service_loading}")

        # Test results
        if len(loading_events) > 0 and len(updated_events) > 0:
            if not final_app_state_loading and not final_service_loading:
                print("\n✅ SUCCESS: Loading cycle completed properly!")
            else:
                print("\n❌ FAILURE: Loading states did not complete!")
        else:
            print("\n❌ FAILURE: Incomplete loading cycle!")

        # Print event timeline
        print("\nEvent Timeline:")
        for i, event in enumerate(self.events):
            print(
                f"  {i + 1}. {event['type']} - App: {event['app_state_loading']}, Service: {event['service_loading']}"
            )

        # Print AppState changes
        print("\nAppState Changes:")
        if self._app_state_changes:
            for change in self._app_state_changes:
                print(f"  - {change}")
        else:
            print("  No AppState changes detected!")


async def test_loading_states():
    """Test the loading state behavior."""
    print("Starting loading state test...")

    # Create monitor
    monitor = LoadingStateMonitor()

    # Get services
    app_state = get_app_state()
    data_service = get_data_service()

    print("Initial states:")
    print(f"  AppState.is_loading: {app_state.is_loading}")
    print(f"  DataService.is_loading: {data_service.is_loading()}")

    # Initialize the data service (this should trigger loading)
    print("\n🚀 Initializing data service...")
    await data_service.initialize()

    # Give events time to propagate
    await asyncio.sleep(0.1)

    print("\nAfter initialization:")
    print(f"  AppState.is_loading: {app_state.is_loading}")
    print(f"  DataService.is_loading: {data_service.is_loading()}")

    # Test a manual refresh
    print("\n🔄 Testing manual refresh...")
    await data_service.refresh_data()

    # Give events time to propagate
    await asyncio.sleep(0.1)

    print("\nAfter manual refresh:")
    print(f"  AppState.is_loading: {app_state.is_loading}")
    print(f"  DataService.is_loading: {data_service.is_loading()}")

    # Print summary
    monitor.print_summary()


def test_state_sync():
    """Test the state synchronization."""
    print("\n" + "=" * 60)
    print("STATE SYNCHRONIZATION TEST")
    print("=" * 60)

    app_state = get_app_state()
    data_service = get_data_service()

    print("Testing state properties:")

    # Test balance
    balance = app_state.balance
    service_balance = data_service.get_balance()
    print(f"  Balance - AppState: {balance}, DataService: {service_balance}")

    # Test transaction count
    count = app_state.transaction_count
    service_count = len(data_service.get_transactions())
    print(f"  Transaction Count - AppState: {count}, DataService: {service_count}")

    # Test loading states
    loading = app_state.is_loading
    service_loading = data_service.is_loading()
    print(f"  Loading - AppState: {loading}, DataService: {service_loading}")

    # Test if state has data
    has_data = app_state.transaction_count > 0
    service_has_data = data_service.has_data()
    print(f"  Has Data - AppState: {has_data}, DataService: {service_has_data}")

    # Summary
    sync_issues = []
    if balance != service_balance:
        sync_issues.append("balance mismatch")
    if count != service_count:
        sync_issues.append("transaction count mismatch")
    if loading != service_loading:
        sync_issues.append("loading state mismatch")
    if has_data != service_has_data:
        sync_issues.append("data availability mismatch")

    if sync_issues:
        print(f"\n❌ SYNC ISSUES: {', '.join(sync_issues)}")
    else:
        print("\n✅ STATE SYNC: All states are properly synchronized")


def test_manual_event_emission():
    """Test manual event emission to verify subscription system works."""
    print("\n" + "=" * 60)
    print("MANUAL EVENT EMISSION TEST")
    print("=" * 60)

    event_bus = get_event_bus()
    app_state = get_app_state()

    # Create a simple test callback
    received_events = []

    def test_callback(event):
        received_events.append(event.type.value)
        print(f"  Test callback received: {event.type.value}")

    # Subscribe to a test event
    event_bus.subscribe(EventType.DATA_LOADING, test_callback)
    print("Subscribed test callback to DATA_LOADING")

    # Emit a test event
    print("Emitting test DATA_LOADING event...")
    event_bus.emit_simple(
        EventType.DATA_LOADING, data={"test": True}, source="TestScript"
    )

    # Check if we received it
    if received_events:
        print(f"✅ SUCCESS: Received {len(received_events)} events: {received_events}")
    else:
        print("❌ FAILURE: No events received by test callback")

    # Clean up
    event_bus.unsubscribe(EventType.DATA_LOADING, test_callback)


async def main():
    """Main test function."""
    print("Monzo App v2 - Loading State Test")
    print("=" * 60)

    try:
        # Test manual event emission first
        test_manual_event_emission()

        # Test loading states
        await test_loading_states()

        # Test state synchronization
        test_state_sync()

        print("\n🎉 Test completed!")

    except Exception as e:
        logger.error(f"Test failed with error: {e}")
        import traceback

        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    # Run the test
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
