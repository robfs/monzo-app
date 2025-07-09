"""Main app file."""

import logging
import os
from pathlib import Path

from duckdb import DuckDBPyConnection
from monzo_py import MonzoTransactions
from textual import work
from textual.app import App
from textual.logging import TextualHandler
from textual.message import Message
from textual.reactive import reactive

from .screens import DashboardScreen

logging.basicConfig(level=logging.DEBUG, handlers=[TextualHandler()])

logger = logging.getLogger(__name__)


class Monzo(App):
    """Main app class."""

    CSS_PATH = "assets/styles.tcss"
    BINDINGS = [
        ("D", "push_screen('dashboard')", "Dashboard"),
        ("q", "request_quit", "Quit"),
    ]
    SCREENS = {
        "dashboard": DashboardScreen,
    }
    transactions: reactive[MonzoTransactions | None] = reactive(None)
    db: reactive[DuckDBPyConnection | None] = reactive(None)
    spreadsheet_id: reactive[str | None] = reactive(None)
    credentials_path: reactive[Path | None] = reactive(None)

    ## DEFAULT METHODS
    def on_mount(self) -> None:
        self.theme = "nord"
        self.spreadsheet_id = os.getenv("MONZO_SPREADSHEET_ID")
        self.credentials_path = Path("~/.monzo/credentials.json").expanduser()
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

    class TransactionsAvailable(Message):
        """Message sent when transactions are available."""

    ## MONZO METHODS
    @work(exclusive=True, thread=True)
    def fetch_monzo_transactions(self) -> None:
        logger.info("Fetching monzo data.")
        if not (
            self.spreadsheet_id
            and self.credentials_path
            and self.credentials_path.exists()
            and self.credentials_path.is_file()
        ):
            self.notify("Missing spreadsheet ID or credentials path")
            return
        self.transactions = MonzoTransactions(
            spreadsheet_id=self.spreadsheet_id, credentials_path=self.credentials_path
        )

    def watch_spreadsheet_id(self, spreadsheet_id: str) -> None:
        logger.info("New spreadsheet ID")
        self.fetch_monzo_transactions()

    def watch_credentials_path(self, credentials_path: Path) -> None:
        logger.info("New credentials path")
        self.fetch_monzo_transactions()

    def add_pay_days_table(self, db: DuckDBPyConnection) -> None:
        app = Path(__file__).parent
        sql = app / "sql_scripts"
        with open(sql / "add_pay_days_table.sql") as f:
            sql = f.read()
        db.sql(sql, params=[25])

    def add_pay_days_to_transactions(self, db: DuckDBPyConnection) -> None:
        app = Path(__file__).parent
        sql = app / "sql_scripts"
        with open(sql / "add_pay_days_to_transactions.sql") as f:
            sql = f.read()
        db.sql(sql)

    def watch_transactions(self, transactions: MonzoTransactions | None) -> None:
        logger.info("Transactions updated.")
        if transactions:
            self.db = transactions.duck_db()
            self.add_pay_days_table(self.db)
            self.add_pay_days_to_transactions(self.db)
            self.post_transactions_available()

    def post_transactions_available(self) -> None:
        for screen in self.screen_stack:
            logger.debug(f"Posting TransactionsAvailable message to {screen}.")
            screen.post_message(self.TransactionsAvailable())


app = Monzo()

if __name__ == "__main__":
    app = Monzo()
    app.run()
