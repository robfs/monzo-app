"""Balance card widget for displaying current account balance."""

import logging
from textual.app import ComposeResult
from textual.containers import Container, Vertical
from textual.widgets import Label

from widgets.base import StateAwareWidget
from widgets.reactive_label import CurrencyLabel, TimeLabel, LoadingLabel
from core import AppEvent

logger = logging.getLogger(__name__)


class BalanceCard(StateAwareWidget):
    """Widget displaying the current account balance with status information."""

    def compose(self) -> ComposeResult:
        """Compose the balance card widget."""
        with Container(classes="balance-card"):
            yield Label("Account Balance", classes="balance-title")
            balance_label = CurrencyLabel(classes="balance-amount")
            balance_label.state_key = "balance"
            balance_label.currency_symbol = "£"
            yield balance_label

            with Vertical(classes="balance-info"):
                loading_label = LoadingLabel(classes="balance-status")
                loading_label.loading_text = "Refreshing..."
                loading_label.idle_text = "Up to date"
                yield loading_label

                time_label = TimeLabel(classes="balance-updated")
                time_label.state_key = "data_last_updated"
                time_label.prefix = "Last updated: "
                yield time_label

    def on_mount(self) -> None:
        """Called when widget is mounted."""
        super().on_mount()
        self.border_title = "Balance"
        self.add_class("card")

    def on_data_updated(self, event: AppEvent) -> None:
        """Handle data update events."""
        logger.debug("BalanceCard: Data updated")
        # The reactive labels will update automatically via state

    def on_data_loading(self, event: AppEvent) -> None:
        """Handle data loading events."""
        logger.debug("BalanceCard: Data loading")
        # Status will update automatically via reactive state

    def on_data_error(self, event: AppEvent) -> None:
        """Handle data error events."""
        logger.debug("BalanceCard: Data error")
        # Status will be handled by the reactive labels automatically
