#!/usr/bin/env python3
"""Simple test to isolate AppState event handling issues."""

import sys
import logging
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from core import get_app_state, get_event_bus, EventType

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)


def test_appstate_events():
    """Test if AppState receives events properly."""
    print("=" * 60)
    print("SIMPLE APPSTATE EVENT TEST")
    print("=" * 60)

    # Get services
    event_bus = get_event_bus()
    app_state = get_app_state()

    print(f"Initial AppState.is_loading: {app_state.is_loading}")

    # Create a simple test to verify AppState responds to events
    print("\n1. Testing manual DATA_LOADING event...")

    # Emit a DATA_LOADING event with proper structure
    event_data = {
        "state": {
            "is_loading": True,
            "has_data": False,
            "transaction_count": 0,
            "last_updated": None,
            "error": None,
        }
    }

    event_bus.emit_simple(EventType.DATA_LOADING, data=event_data, source="SimpleTest")

    print(f"After DATA_LOADING event - AppState.is_loading: {app_state.is_loading}")

    print("\n2. Testing manual DATA_UPDATED event...")

    # Emit a DATA_UPDATED event with proper structure
    event_data = {
        "state": {
            "is_loading": False,
            "has_data": True,
            "transaction_count": 42,
            "last_updated": None,
            "error": None,
        }
    }

    event_bus.emit_simple(EventType.DATA_UPDATED, data=event_data, source="SimpleTest")

    print(f"After DATA_UPDATED event - AppState.is_loading: {app_state.is_loading}")
    print(
        f"After DATA_UPDATED event - AppState.transaction_count: {app_state.transaction_count}"
    )

    print("\n3. Testing direct method calls...")

    # Test calling AppState methods directly
    print("Calling app_state.update_loading_state(True)...")
    app_state.update_loading_state(True)
    print(f"Direct call result - AppState.is_loading: {app_state.is_loading}")

    print("Calling app_state.update_loading_state(False)...")
    app_state.update_loading_state(False)
    print(f"Direct call result - AppState.is_loading: {app_state.is_loading}")

    print("\n=" * 60)
    print("TEST RESULTS:")

    if hasattr(app_state, "_initialized") and app_state._initialized:
        print("✅ AppState is properly initialized")
    else:
        print("❌ AppState initialization issue")

    if hasattr(app_state, "_event_bus") and app_state._event_bus is not None:
        print("✅ AppState has event bus reference")
    else:
        print("❌ AppState missing event bus reference")

    # Check if event subscriptions exist
    subscribers = event_bus._subscribers
    data_loading_subs = len(subscribers.get(EventType.DATA_LOADING, []))
    data_updated_subs = len(subscribers.get(EventType.DATA_UPDATED, []))

    print(f"📊 DATA_LOADING subscribers: {data_loading_subs}")
    print(f"📊 DATA_UPDATED subscribers: {data_updated_subs}")

    if data_loading_subs > 0 and data_updated_subs > 0:
        print("✅ AppState appears to be subscribed to events")
    else:
        print("❌ AppState not properly subscribed to events")


if __name__ == "__main__":
    test_appstate_events()
