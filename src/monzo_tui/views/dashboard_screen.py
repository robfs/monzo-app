"""Module containing the DashboardScreen class."""

from textual.app import ComposeResult
from textual.containers import Container
from textual.screen import Screen
from textual.widgets import Label, Header, Footer


class DashboardScreen(Screen):
    """The main dashboard screen."""

    def compose(self) -> ComposeResult:
        grid = Container(Label("Welcome to the Dashboard"))
        grid.border_title = "Dashboard"
        grid.border_subtitle = "Dashboard of headline analysis."
        yield Footer()
        yield Header()
        yield grid
