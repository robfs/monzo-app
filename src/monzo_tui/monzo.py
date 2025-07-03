"""This is the main Monzo Textual app."""

from textual.app import App
from textual.app import ComposeResult
from textual.reactive import reactive
from textual.widgets import Footer
from textual.widgets import Header

from .views import QuitModalScreen
from .views import SettingsScreen


__all__ = ["Monzo"]


class Monzo(App):
    """A Textual app to manage stopwatches."""

    CSS_PATH = "assets/styles.tcss"
    BINDINGS = [
        ("q", "request_quit", "Quit"),
        ("d", "toggle_dark", "Toggle dark mode"),
        ("s", "open_settings", "Settings"),
    ]

    spreadsheet_id = reactive("")
    credentials_path = reactive("")

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header()
        yield Footer()

    def on_mount(self) -> None:
        self.theme = "catppuccin-latte"
        if not self.spreadsheet_id:
            self.action_open_settings()

    def action_request_quit(self) -> None:
        """Action to display the quit dialog."""

        def check_quit(quit: bool | None) -> None:
            """Called when QuitScreen is dismissed."""
            if quit:
                self.exit()

        self.push_screen(QuitModalScreen(), check_quit)

    def action_open_settings(self) -> None:
        """Action to open the settings screen."""

        def get_settings(settings: tuple[str, str]) -> None:
            spreadsheet_id, credentials_path = settings
            self.spreadsheet_id = spreadsheet_id
            self.credentials_path = credentials_path

        self.push_screen(SettingsScreen(), get_settings)

    def action_toggle_dark(self) -> None:
        """An action to toggle dark mode."""
        self.theme = (
            "catppuccin-mocha"
            if self.theme == "catppuccin-latte"
            else "catppuccin-latte"
        )


app = Monzo()
