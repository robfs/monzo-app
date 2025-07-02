"""This is the main Monzo Textual app."""


from textual.app import App
from textual.app import ComposeResult
from textual.containers import VerticalScroll
from textual.reactive import Reactive
from textual.widgets import Footer
from textual.widgets import Header

from .views import QuitModalScreen
from .views import Stopwatch


class StopwatchApp(App):
    """A Textual app to manage stopwatches."""

    CSS_PATH = "assets/styles.tcss"
    BINDINGS = [
        ("q", "request_quit", "Quit"),
        ("d", "toggle_dark", "Toggle dark mode"),
        ("a", "add_stopwatch", "Add"),
        ("r", "remove_stopwatch", "Remove"),
    ]
    theme = Reactive("textual-light")

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header()
        yield Footer()
        yield VerticalScroll(Stopwatch(), Stopwatch(), Stopwatch(), id="timers")

    def action_request_quit(self) -> None:
        """Action to display the quit dialog."""

        def check_quit(quit: bool | None) -> None:
            """Called when QuitScreen is dismissed."""
            if quit:
                self.exit()

        self.push_screen(QuitModalScreen(), check_quit)

    def action_add_stopwatch(self) -> None:
        """An action to add a timer."""
        new_stopwatch = Stopwatch()
        self.query_one("#timers").mount(new_stopwatch)
        new_stopwatch.scroll_visible()

    def action_remove_stopwatch(self) -> None:
        """Called to remove a timer."""
        timers = self.query("Stopwatch")
        if timers:
            timers.last().remove()

    def action_toggle_dark(self) -> None:
        """An action to toggle dark mode."""
        self.theme = (
            "textual-dark" if self.theme == "textual-light" else "textual-light"
        )


app = StopwatchApp()
