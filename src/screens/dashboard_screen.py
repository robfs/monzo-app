"""Module containing dashboard screen."""

import asyncio
import logging

from textual.app import ComposeResult
from textual.containers import Container
from textual.screen import Screen
from textual.widgets import Footer
from textual.widgets import Header

from widgets import ReactiveLabel

__all__ = ["DashboardScreen"]

logger = logging.getLogger(__name__)


class DashboardScreen(Screen):
    """Dashboard screen."""

    BINDINGS = [("r", "refresh", "Refresh")]

    def compose(self) -> ComposeResult:
        """Compose the dashboard screen."""
        logger.debug("Composing the dashboard screen")
        yield Header()
        yield Footer()
        yield Container(ReactiveLabel("This is the dashboard screen."))

    def on_mount(self):
        """Mount the dashboard screen."""
        logger.debug("Mounting the dashboard screen")
        logger.debug(f"{self.app.screen_stack=}")

    async def action_refresh(self):
        """Refresh the dashboard screen."""
        logger.debug("Refreshing the dashboard screen")
        label = self.query_one(ReactiveLabel)
        label.set_updating()
        await asyncio.sleep(5)
        label.stop_updating()
