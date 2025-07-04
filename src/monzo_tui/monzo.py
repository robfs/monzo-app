"""This is the main Monzo Textual app."""

import os
import logging
from pathlib import Path

from duckdb import DuckDBPyConnection

from textual.app import App
from textual.app import ComposeResult
from textual.logging import TextualHandler
from textual.reactive import reactive
from textual.widgets import Footer
from textual.widgets import Header

from monzo_py import MonzoTransactions

from .screens import QuitModalScreen
from .screens import SettingsScreen
from .screens import SettingsErrorScreen
from .screens import DashboardScreen


__all__ = ["Monzo"]

logging.basicConfig(level="DEBUG", handlers=[TextualHandler()])

logger = logging.getLogger(__name__)


class Monzo(App):
    """A Textual app to manage stopwatches."""

    CSS_PATH = "assets/styles.tcss"
    BINDINGS = [
        ("q", "request_quit", "Quit"),
        ("d", "push_screen('dashboard')", "Dashboard"),
        ("s", "open_settings", "Settings"),
    ]
    SCREENS = {"dashboard": DashboardScreen}

    spreadsheet_id = reactive(os.getenv("MONZO_SPREADSHEET_ID", ""))
    credentials_path = reactive(Path().home() / ".monzo" / "credentials.json")
    monzo_transactions: reactive[MonzoTransactions | None] = reactive(None)
    db_connection: reactive[DuckDBPyConnection | None] = reactive(None)

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header()
        yield Footer()

    def on_mount(self) -> None:
        self.check_settings(self.spreadsheet_id, self.credentials_path)
        self.theme = "catppuccin-latte"
        self.push_screen("dashboard")

    def check_settings(
        self, spreadsheet_id: str | None, credentials_path: Path
    ) -> bool:
        logger.info(f"Checking settings: {spreadsheet_id=}, {credentials_path=}")
        if not spreadsheet_id:
            logger.info("Spreadsheet ID is not provided.")
            self.action_open_settings()
            self.push_screen(SettingsErrorScreen("Must provide spreadsheet ID."))
            return False
        if not credentials_path.exists() or not credentials_path.is_file():
            logger.info(f"Credentials path ({credentials_path}) is not valid.")
            self.action_open_settings()
            self.push_screen(
                SettingsErrorScreen("Credentials path must link to a valid file.")
            )
            return False
        return True

    def action_request_quit(self) -> None:
        """Action to display the quit dialog."""

        def check_quit(quit: bool | None) -> None:
            """Called when QuitScreen is dismissed."""
            if quit:
                self.exit()

        self.push_screen(QuitModalScreen(), check_quit)

    def action_open_settings(self) -> None:
        """Action to open the settings screen."""

        def save_settings(settings: tuple[bool, str, Path]) -> None:
            to_save, spreadsheet_id, credentials_path = settings
            if to_save:
                logger.info("Saving settings...")
                valid = self.check_settings(spreadsheet_id, credentials_path)
                if valid:
                    self.spreadsheet_id = spreadsheet_id
                    self.credentials_path = credentials_path
            else:
                logger.info("Settings not saved.")
                self.check_settings(self.spreadsheet_id, self.credentials_path)

        self.push_screen(
            SettingsScreen(self.spreadsheet_id, self.credentials_path), save_settings
        )



app = Monzo()
