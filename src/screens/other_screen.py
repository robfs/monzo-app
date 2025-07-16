"""Module containing the OtherScreen class."""

import logging

from textual.app import ComposeResult
from textual.containers import Container
from textual.screen import Screen
from textual.widgets import Footer
from textual.widgets import Header
from textual.widgets import Label

__all__ = ["OtherScreen"]

logger = logging.getLogger(__name__)


class OtherScreen(Screen):
    """Screen for displaying other information."""

    def compose(self) -> ComposeResult:
        """Compose the screen."""
        logger.debug("Composing OtherScreen")
        yield Header()
        yield Footer()
        yield Container(Label("This is the other Screen"))

    def on_mount(self):
        """Mount the other screen."""
        logger.debug("Mounting the other screen")
        logger.debug(f"{self.app.screen_stack=}")
