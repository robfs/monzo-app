#!/usr/bin/env python3
"""Simple test script to verify imports work correctly."""

import sys
from pathlib import Path

# Add the v2 directory to the Python path
v2_dir = Path(__file__).parent
sys.path.insert(0, str(v2_dir))


def test_core_imports():
    """Test that core module imports work."""
    try:
        from core.data_service import get_data_service
        from core.events import EventType
        from core.events import get_event_bus
        from core.settings import get_settings_service
        from core.state import get_app_state

        print("✓ Core imports successful")
        return True
    except ImportError as e:
        print(f"✗ Core import failed: {e}")
        return False


def test_widget_imports():
    """Test that widget imports work."""
    try:
        from widgets.base import StateAwareWidget
        from widgets.reactive_label import ReactiveLabel
        from widgets.reactive_label import StateLabel

        print("✓ Widget imports successful")
        return True
    except ImportError as e:
        print(f"✗ Widget import failed: {e}")
        return False


def test_screen_imports():
    """Test that screen imports work."""
    try:
        from screens.dashboard import DashboardScreen
        from screens.exclusions import ExclusionsScreen
        from screens.settings import SettingsScreen

        print("✓ Screen imports successful")
        return True
    except ImportError as e:
        print(f"✗ Screen import failed: {e}")
        return False


def test_basic_functionality():
    """Test basic functionality without UI."""
    try:
        # Test event bus
        from core.events import EventType
        from core.events import get_event_bus

        event_bus = get_event_bus()
        event_bus.emit_simple(EventType.APP_READY, data="test")

        # Test settings service
        from core.settings import get_settings_service

        settings_service = get_settings_service()
        settings_service.set("test_key", "test_value")

        # Test data service
        from core.data_service import get_data_service

        data_service = get_data_service()

        # Test app state
        from core.state import get_app_state

        app_state = get_app_state()

        print("✓ Basic functionality test successful")
        return True
    except Exception as e:
        print(f"✗ Basic functionality test failed: {e}")
        return False


def main():
    """Run all tests."""
    print("Testing Monzo App v2 imports and basic functionality...")
    print()

    tests = [
        test_core_imports,
        test_widget_imports,
        test_screen_imports,
        test_basic_functionality,
    ]

    results = []
    for test in tests:
        results.append(test())

    print()
    if all(results):
        print("🎉 All tests passed! The application should run correctly.")
        return 0
    else:
        print("❌ Some tests failed. Check the error messages above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
