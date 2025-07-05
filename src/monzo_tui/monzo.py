"""This is the main Monzo Textual app."""

import logging
import os
from contextlib import contextmanager
from pathlib import Path

from duckdb import DuckDBPyConnection
from monzo_py import MonzoTransactions
from textual import work
from textual.app import App
from textual.app import ComposeResult
from textual.logging import TextualHandler
from textual.message import Message
from textual.reactive import reactive
from textual.widgets import Footer
from textual.widgets import Header
from textual.worker import Worker
from textual.worker import get_current_worker

from .screens import DashboardScreen
from .screens import QuitModalScreen
from .screens import SettingsErrorScreen
from .screens import SettingsScreen

__all__ = ["Monzo"]

logging.basicConfig(level="DEBUG", handlers=[TextualHandler()])

logger = logging.getLogger(__name__)


class Monzo(App):
    """A Textual app to manage stopwatches."""

    CSS_PATH = "assets/styles.tcss"
    BINDINGS = [
        ("d", "push_screen('dashboard')", "Dashboard"),
        ("R", "get_transactions", "Refresh"),
        ("s", "open_settings", "Settings"),
        ("q", "request_quit", "Quit"),
    ]
    SCREENS = {"dashboard": DashboardScreen}

    spreadsheet_id = reactive(os.getenv("MONZO_SPREADSHEET_ID", ""))
    credentials_path = reactive(Path().home() / ".monzo" / "credentials.json")
    pay_day_type = reactive("specific")
    pay_day = reactive(25)
    monzo_transactions: reactive[MonzoTransactions | None] = reactive(None)
    db_connection: reactive[DuckDBPyConnection | None] = reactive(None)

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header()
        yield Footer()

    def on_mount(self) -> None:
        self.check_settings(self.spreadsheet_id, self.credentials_path)
        self.theme = "nord"
        self.push_screen("dashboard")

    def watch_spreadsheet_id(self, new_spreadsheet_id: str) -> None:
        """Watch for changes to spreadsheet_id and reinitialize MonzoTransactions."""
        logger.info(f"Spreadsheet ID changed to: {new_spreadsheet_id}")
        if new_spreadsheet_id and self.credentials_path.exists():
            self.get_transactions()

    def watch_credentials_path(self, new_credentials_path: Path) -> None:
        """Watch for changes to credentials_path and reinitialize MonzoTransactions."""
        logger.info(f"Credentials path changed to: {new_credentials_path}")
        if self.spreadsheet_id and new_credentials_path.exists():
            self.get_transactions()

    @work(exclusive=True, thread=True)
    def get_transactions(self) -> None:
        """Initialize MonzoTransactions with the given spreadsheet ID."""
        self.notify("Refreshing Monzo data...", severity="warning")
        worker = get_current_worker()
        spreadsheet_id = self.spreadsheet_id
        credentials_path = self.credentials_path
        try:
            creds = str(credentials_path)
            transactions = MonzoTransactions(spreadsheet_id, credentials_path=creds)

            if not worker.is_cancelled:
                # This runs in the background thread - good for slow operations
                transactions.fetch_data()
                self.notify("Monzo data updated.", title="Refresh Complete", timeout=3)

                # Safely update the reactive attribute from the background thread
                self.call_from_thread(setattr, self, "monzo_transactions", transactions)

                # Notify dashboard screen directly that data is available
                logger.info(
                    "Posting MonzoTransactionsInitialized message to dashboard screen"
                )
                # self.call_from_thread(self._post_message_to_dashboard)
                # self._post_message_to_dashboard()
                for screen in self.screen_stack:
                    screen.post_message(self.MonzoTransactionsInitialized())

        except Exception as e:
            logger.error(f"Failed to initialize MonzoTransactions: {e}")
            # Use call_from_thread to safely push screen from background thread
            self.call_from_thread(
                self.notify,
                "Failed to load transaction data.",
                title="Data Fetch Error",
                severity="error",
                timeout=5,
            )

    def on_worker_state_changed(self, event: Worker.StateChanged) -> None:
        """Called when the worker state changes."""
        self.log(event)

    class MonzoTransactionsInitialized(Message):
        """Message sent when MonzoTransactions is successfully initialized."""

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

        def save_settings(settings: tuple[bool, str, Path, str, int]) -> None:
            to_save, spreadsheet_id, credentials_path, pay_day_type, pay_day = settings
            if to_save:
                logger.info("Saving settings...")
                valid = self.check_settings(spreadsheet_id, credentials_path)
                if valid:
                    self.spreadsheet_id = spreadsheet_id
                    self.credentials_path = credentials_path
                    self.pay_day_type = pay_day_type
                    self.pay_day = pay_day
                    self.notify(
                        f"Spreadsheet ID: {spreadsheet_id}\nCredentials Path: {credentials_path}\nPay Day Type: {pay_day_type}\nPay Day: {pay_day}",
                        title="Settings Updated",
                    )
            else:
                logger.info("Settings not saved.")
                self.check_settings(self.spreadsheet_id, self.credentials_path)

        self.push_screen(
            SettingsScreen(
                self.spreadsheet_id,
                self.credentials_path,
                self.pay_day_type,
                self.pay_day,
            ),
            save_settings,
        )

    def action_get_transactions(self) -> None:
        """Action to refresh transactions data."""
        self.get_transactions()

    @contextmanager
    def get_db_connection(self):
        """Get the DuckDB connection for views to query data."""
        if not self.monzo_transactions:
            logger.error("MonzoTransactions not initialized.")
            yield None
            return

        db_conn = self.monzo_transactions.duck_db()
        try:
            yield db_conn
        finally:
            db_conn.close()


app = Monzo()
