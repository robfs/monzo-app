#!/usr/bin/env python3
"""Proper Textual tests for reactive loading states using run_test framework."""

import pytest
import asyncio
import sys
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from textual.app import App, ComposeResult
from textual.containers import Container, Vertical, Horizontal
from textual.widgets import Label

from widgets.reactive_label import LoadingLabel, StateLabel, CurrencyLabel, CounterLabel
from widgets.dashboard.balance_card import BalanceCard
from widgets.dashboard.info_cards import DataStatusCard
from core import get_app_state, get_data_service, get_event_bus, EventType


class TestLoadingWidget(App):
    """Simple test app with just a LoadingLabel widget."""

    def compose(self) -> ComposeResult:
        yield LoadingLabel(id="loading-label")


class TestBalanceCard(App):
    """Test app with BalanceCard widget."""

    def compose(self) -> ComposeResult:
        yield BalanceCard(id="balance-card")


class TestDataStatusCard(App):
    """Test app with DataStatusCard widget."""

    def compose(self) -> ComposeResult:
        yield DataStatusCard(id="data-status-card")


class TestMultipleWidgets(App):
    """Test app with multiple reactive widgets."""

    def compose(self) -> ComposeResult:
        with Vertical():
            yield BalanceCard(id="balance-card")
            yield DataStatusCard(id="data-status-card")
            with Horizontal():
                yield LoadingLabel(id="standalone-loading")
                yield CurrencyLabel(id="standalone-currency")


@pytest.mark.asyncio
async def test_loading_label_reactive_state():
    """Test that LoadingLabel properly reacts to is_loading state changes."""
    app = TestLoadingWidget()

    async with app.run_test() as pilot:
        # Get the widget and app state
        loading_label = app.query_one("#loading-label", LoadingLabel)
        app_state = get_app_state()

        # Initial state should be "Ready" (not loading)
        await pilot.pause(0.1)  # Allow initial rendering
        assert "Ready" in loading_label._label.renderable or "Up to date" in str(
            loading_label._label.renderable
        )

        # Simulate loading state change to True
        app_state.update_loading_state(True)
        await pilot.pause(0.1)  # Allow reactive update

        # Should now show loading text
        loading_text = str(loading_label._label.renderable)
        assert "Loading" in loading_text or "Refreshing" in loading_text

        # Simulate loading state change to False
        app_state.update_loading_state(False)
        await pilot.pause(0.1)  # Allow reactive update

        # Should now show ready text again
        ready_text = str(loading_label._label.renderable)
        assert "Ready" in ready_text or "Up to date" in ready_text


@pytest.mark.asyncio
async def test_balance_card_reactive_flow():
    """Test that BalanceCard properly reacts to data updates."""
    app = TestBalanceCard()

    async with app.run_test() as pilot:
        # Get the balance card and services
        balance_card = app.query_one("#balance-card", BalanceCard)
        app_state = get_app_state()
        data_service = get_data_service()

        # Wait for initial rendering
        await pilot.pause(0.1)

        # Check initial state - should show ready/not loading
        loading_labels = balance_card.query("LoadingLabel")
        if loading_labels:
            loading_label = loading_labels.first()
            initial_text = str(loading_label._label.renderable)
            # Should not show loading initially
            assert "Loading" not in initial_text and "Refreshing" not in initial_text

        # Trigger a data refresh which should show loading state
        await data_service.refresh_data()
        await pilot.pause(0.1)  # Allow reactive updates

        # After refresh, should show ready state
        if loading_labels:
            loading_label = loading_labels.first()
            final_text = str(loading_label._label.renderable)
            assert "Ready" in final_text or "Up to date" in final_text

        # Check that balance was updated
        currency_labels = balance_card.query("CurrencyLabel")
        if currency_labels:
            currency_label = currency_labels.first()
            balance_text = str(currency_label._label.renderable)
            assert "£" in balance_text  # Should show currency symbol
            assert balance_text != "£0.00"  # Should have actual data


@pytest.mark.asyncio
async def test_data_status_card_reactive_flow():
    """Test that DataStatusCard properly reacts to data updates."""
    app = TestDataStatusCard()

    async with app.run_test() as pilot:
        # Get the data status card and services
        data_status_card = app.query_one("#data-status-card", DataStatusCard)
        data_service = get_data_service()

        # Wait for initial rendering
        await pilot.pause(0.1)

        # Check initial state
        loading_labels = data_status_card.query("LoadingLabel")
        counter_labels = data_status_card.query("CounterLabel")

        # Trigger a data refresh
        await data_service.refresh_data()
        await pilot.pause(0.1)  # Allow reactive updates

        # After refresh, should show ready state
        if loading_labels:
            loading_label = loading_labels.first()
            final_text = str(loading_label._label.renderable)
            assert "Ready" in final_text or "✅" in final_text

        # Should show transaction count
        if counter_labels:
            counter_label = counter_labels.first()
            count_text = str(counter_label._label.renderable)
            assert "record" in count_text  # Should show some records


@pytest.mark.asyncio
async def test_multiple_widgets_sync():
    """Test that multiple widgets stay synchronized during data updates."""
    app = TestMultipleWidgets()

    async with app.run_test() as pilot:
        # Get all the widgets
        balance_card = app.query_one("#balance-card", BalanceCard)
        data_status_card = app.query_one("#data-status-card", DataStatusCard)
        standalone_loading = app.query_one("#standalone-loading", LoadingLabel)

        data_service = get_data_service()
        app_state = get_app_state()

        # Wait for initial rendering
        await pilot.pause(0.1)

        # Test that setting loading state affects all widgets
        app_state.update_loading_state(True)
        await pilot.pause(0.1)

        # Check that standalone loading widget shows loading
        loading_text = str(standalone_loading._label.renderable)
        assert "Loading" in loading_text or "Refreshing" in loading_text

        # Test that data refresh affects all widgets
        await data_service.refresh_data()
        await pilot.pause(0.1)

        # All loading widgets should now show ready
        loading_widgets = app.query("LoadingLabel")
        for widget in loading_widgets:
            widget_text = str(widget._label.renderable)
            # Should not be loading anymore
            assert "Loading" not in widget_text and "Refreshing" not in widget_text


@pytest.mark.asyncio
async def test_loading_state_transitions():
    """Test the complete loading state transition cycle."""
    app = TestLoadingWidget()

    async with app.run_test() as pilot:
        loading_label = app.query_one("#loading-label", LoadingLabel)
        app_state = get_app_state()
        event_bus = get_event_bus()

        # Track state changes
        states_seen = []

        def track_state():
            current_text = str(loading_label._label.renderable)
            states_seen.append(current_text)

        await pilot.pause(0.1)
        track_state()  # Initial state

        # Simulate the complete loading cycle
        app_state.update_loading_state(True)
        await pilot.pause(0.1)
        track_state()  # Loading state

        app_state.update_loading_state(False)
        await pilot.pause(0.1)
        track_state()  # Ready state

        # Verify we saw the transition
        assert len(states_seen) == 3

        # First state should be ready/idle
        initial_state = states_seen[0]
        assert "Loading" not in initial_state and "Refreshing" not in initial_state

        # Middle state should be loading
        loading_state = states_seen[1]
        assert "Loading" in loading_state or "Refreshing" in loading_state

        # Final state should be ready again
        final_state = states_seen[2]
        assert "Loading" not in final_state and "Refreshing" not in final_state


@pytest.mark.asyncio
async def test_data_service_integration():
    """Test that DataService loading states properly propagate to widgets."""
    app = TestBalanceCard()

    async with app.run_test() as pilot:
        balance_card = app.query_one("#balance-card", BalanceCard)
        data_service = get_data_service()

        await pilot.pause(0.1)

        # Get initial balance
        currency_labels = balance_card.query("CurrencyLabel")
        if currency_labels:
            currency_label = currency_labels.first()
            initial_balance = str(currency_label._label.renderable)

        # Refresh data multiple times to ensure consistency
        for i in range(3):
            await data_service.refresh_data()
            await pilot.pause(0.1)

            # Check that balance updates each time
            if currency_labels:
                current_balance = str(currency_label._label.renderable)
                assert "£" in current_balance
                # Balance should be non-zero after refresh
                assert current_balance != "£0.00"

            # Check that loading state completes
            loading_labels = balance_card.query("LoadingLabel")
            if loading_labels:
                loading_label = loading_labels.first()
                loading_text = str(loading_label._label.renderable)
                assert (
                    "Loading" not in loading_text and "Refreshing" not in loading_text
                )


@pytest.mark.asyncio
async def test_error_state_handling():
    """Test that widgets properly handle error states."""
    app = TestDataStatusCard()

    async with app.run_test() as pilot:
        data_status_card = app.query_one("#data-status-card", DataStatusCard)
        app_state = get_app_state()

        await pilot.pause(0.1)

        # Simulate an error state
        app_state.update_error_state("Test error message")
        await pilot.pause(0.1)

        # Check that error is handled gracefully
        # (The widgets should not crash and should show non-loading state)
        loading_labels = data_status_card.query("LoadingLabel")
        if loading_labels:
            loading_label = loading_labels.first()
            loading_text = str(loading_label._label.renderable)
            # Should not be stuck in loading state due to error
            assert "Loading" not in loading_text and "Refreshing" not in loading_text

        # Clear error state
        app_state.update_error_state(None)
        await pilot.pause(0.1)


if __name__ == "__main__":
    # Run tests directly if script is executed
    pytest.main([__file__, "-v", "--asyncio-mode=auto"])
