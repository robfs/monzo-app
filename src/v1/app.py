"""Main app file."""

import logging
import os
from pathlib import Path
from typing import Literal

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

from .screens import DashboardScreen
from .screens import SettingsModalScreen

logging.basicConfig(level=logging.DEBUG, handlers=[TextualHandler()])

logger = logging.getLogger(__name__)


class Monzo(App):
    """Main app class."""

    CSS_PATH = "assets/styles.tcss"
    BINDINGS = [
        ("D", "push_screen('dashboard')", "Dashboard"),
        ("r", "refresh_data", "Refresh"),
        ("s", "open_settings", "Settings"),
        ("q", "request_quit", "Quit"),
    ]
    SCREENS = {"dashboard": DashboardScreen, "settings": SettingsModalScreen}

    transactions: reactive[MonzoTransactions | None] = reactive(None)
    db: reactive[DuckDBPyConnection | None] = reactive(None)

    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()

    ## DEFAULT METHODS
    def on_mount(self) -> None:
        self.theme = "nord"
        self.push_screen("dashboard")
        self.fetch_monzo_transactions()

    async def _on_exit_app(self) -> None:
        if self.db:
            logger.debug("Closing database connection.")
            self.db.close()
        return await super()._on_exit_app()

    ## ACTION METHODS
    def action_request_quit(self):
        self.exit()

    def action_open_settings(self):
        def save_settings(to_update: bool) -> None:
            if to_update:
                pay_day = self.get_setting("pay_day")
                self.get_screen("dashboard").pay_day = pay_day
                self.fetch_monzo_transactions()

        self.push_screen("settings", save_settings)

    class TransactionsAvailable(Message):
        """Message sent when transactions are available."""

    ## MONZO METHODS
    @work(exclusive=True, thread=True)
    def fetch_monzo_transactions(self) -> None:
        logger.info("Fetching monzo data.")
        spreadsheet_id: str = self.get_setting("spreadsheet_id")
        credentials_path: Path = self.get_setting("credentials_path")
        pay_day: int = self.get_setting("pay_day")
        if not (
            spreadsheet_id
            and credentials_path
            and credentials_path.exists()
            and credentials_path.is_file()
        ):
            self.notify("Missing spreadsheet ID or credentials path", severity="error")
            return
        try:
            self.transactions = MonzoTransactions(
                spreadsheet_id=spreadsheet_id,
                credentials_path=credentials_path,
            )
            db = self.transactions.duck_db()
            self.add_pay_days_table(db, pay_day)
            self.add_pay_days_to_transactions(db)
            self.db = db
        except Exception as e:
            self.notify(f"Error fetching Monzo transactions: {e}", severity="error")
            return

    def get_setting(
        self, setting_name: Literal["spreadsheet_id", "credentials_path", "pay_day"]
    ):
        settings_screen = self.get_screen("settings")
        return getattr(settings_screen, setting_name)

    def action_refresh_data(self):
        logger.info("Refreshing data")
        self.fetch_monzo_transactions()

    def add_pay_days_table(self, db: DuckDBPyConnection, pay_day: int) -> None:
        app = Path(__file__).parent
        sql = app / "sql_scripts"
        with open(sql / "add_pay_days_table.sql") as f:
            sql = f.read()
        db.sql(sql, params=[pay_day])

    def add_pay_days_to_transactions(self, db: DuckDBPyConnection) -> None:
        app = Path(__file__).parent
        sql = app / "sql_scripts"
        with open(sql / "add_pay_days_to_transactions.sql") as f:
            sql = f.read()
        db.sql(sql)

    def watch_db(self, transactions: MonzoTransactions | None) -> None:
        logger.info("Transactions updated.")
        if transactions:
            self.post_transactions_available()

    def post_transactions_available(self) -> None:
        for screen in self.screen_stack:
            logger.debug(f"Posting TransactionsAvailable message to {screen}.")
            screen.post_message(self.TransactionsAvailable())


app = Monzo()

if __name__ == "__main__":
    app = Monzo()
    app.run()
