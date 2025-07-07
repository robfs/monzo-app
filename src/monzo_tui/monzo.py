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
from .screens import SQLScreen
from .screens.dashboard_screen import PayDayView

__all__ = ["Monzo"]

logging.basicConfig(level="DEBUG", handlers=[TextualHandler()])

logger = logging.getLogger(__name__)
# 157 x 55


class Monzo(App):
    """A Textual app to manage stopwatches."""

    CSS_PATH = "assets/styles.tcss"
    BINDINGS = [
        ("D", "push_screen('dashboard')", "Dashboard"),
        ("C", "push_screen('sql')", "Custom SQL"),
        ("r", "get_transactions", "Refresh"),
        ("s", "open_settings", "Settings"),
        ("q", "request_quit", "Quit"),
    ]
    SCREENS = {"dashboard": DashboardScreen, "sql": SQLScreen}

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

    def watch_pay_day(self, new_pay_day: int) -> None:
        """Watch for changes to pay_day and update the pay day widget."""
        dashboard = self.get_screen("dashboard")
        widget = dashboard.query_one(PayDayView)
        widget.pay_day = new_pay_day

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
                    screen.post_message(self.TransactionsInitialized())

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

    class TransactionsInitialized(Message):
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
            self.add_pay_day_information(db_conn)
            yield db_conn
        finally:
            db_conn.close()

    def add_pay_days_table(self, db_conn: DuckDBPyConnection) -> None:
        sql_query: str = """
        CREATE OR REPLACE TABLE paydays AS
        WITH month_series AS (
            SELECT
                date_part('year', date_series) as year,
                date_part('month', date_series) as monthNum
            FROM generate_series(
                DATE '2017-01-01',
                DATE '2030-12-01',
                INTERVAL '1 month'
            ) as t(date_series)
        )
        SELECT
            year,
            monthNum,
            make_date(
                CAST(year AS INTEGER),
                CAST(monthNum AS INTEGER),
                ?
            ) + INTERVAL (
                CASE
                    WHEN date_part('isodow', make_date(CAST(year AS INTEGER), CAST(monthNum AS INTEGER), 25)) BETWEEN 1 AND 5 THEN 0
                    WHEN date_part('isodow', make_date(CAST(year AS INTEGER), CAST(monthNum AS INTEGER), 25)) = 6 THEN 2  -- Saturday -> Monday
                    WHEN date_part('isodow', make_date(CAST(year AS INTEGER), CAST(monthNum AS INTEGER), 25)) = 7 THEN 1  -- Sunday -> Monday
                END
            ) DAY as lastDate,
            lead(lastDate) over (order by lastDate) as nextDate
        FROM month_series
        ORDER BY year, monthNum
        """
        db_conn.sql(sql_query, params=[self.pay_day])

    def add_pay_day_information(self, db_conn: DuckDBPyConnection) -> None:
        self.add_pay_days_table(db_conn)
        sql_query = """
        ALTER VIEW transactions RENAME TO RAW_TRANSACTIONS;

        CREATE OR REPLACE TABLE transactions
        AS SELECT
            raw_transactions.*,
            paydays.*,
            if (raw_transactions.date < paydays.lastDate, paydays.lastDate, paydays.nextDate) as nextPayDay,
            date_trunc('month', nextPayDay) as expenseMonthDate,
            case date_part('month', expenseMonthDate)
                when 1 then 'January'
                when 2 then 'February'
                when 3 then 'March'
                when 4 then 'April'
                when 5 then 'May'
                when 6 then 'June'
                when 7 then 'July'
                when 8 then 'August'
                when 9 then 'September'
                when 10 then 'October'
                when 11 then 'November'
                when 12 then 'December'
            end || ' ' || date_part('year', expenseMonthDate) as expenseMonth,
            date_part('isodow', date) as dayOfWeekNum,
            case dayOfWeekNum
                when 1 then 'Monday'
                when 2 then 'Tuesday'
                when 3 then 'Wednesday'
                when 4 then 'Thursday'
                when 5 then 'Friday'
                when 6 then 'Saturday'
                when 7 then 'Sunday'
            end as dayOfWeek,
            case monthNum
                when 1 then 'January'
                when 2 then 'February'
                when 3 then 'March'
                when 4 then 'April'
                when 5 then 'May'
                when 6 then 'June'
                when 7 then 'July'
                when 8 then 'August'
                when 9 then 'September'
                when 10 then 'October'
                when 11 then 'November'
                when 12 then 'December'
            end as month,
            sum(amount) OVER (ORDER BY date, time ROWS UNBOUNDED PRECEDING) as balance
        FROM raw_transactions
        LEFT JOIN paydays ON date_part('year', raw_transactions.date) = paydays.year AND date_part('month', raw_transactions.date) = paydays.monthNum;
        """
        db_conn.sql(sql_query)


app = Monzo()
