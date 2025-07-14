"""Table widgets for displaying transaction and category data."""

import logging
from textual.app import ComposeResult
from textual.containers import Container, Vertical, Horizontal
from textual.widgets import Label, DataTable
from textual.reactive import reactive

from widgets.base import StateAwareWidget, DataWidget
from widgets.reactive_label import CounterLabel, StatusLabel
from core import AppEvent, get_data_service

logger = logging.getLogger(__name__)


class TopCategoriesTable(DataWidget):
    """Widget displaying top spending categories in a table format."""

    def compose(self) -> ComposeResult:
        """Compose the top categories table widget."""
        with Container(classes="table-container"):
            yield Label("Top Spending Categories", classes="table-title")

            with Horizontal(classes="table-header"):
                yield Label(
                    "Showing top categories (excluding filtered):",
                    classes="header-label",
                )
                exclusions_label = CounterLabel(classes="exclusion-count")
                exclusions_label.state_key = "exclusions"
                exclusions_label.prefix = "("
                exclusions_label.suffix = " excluded)"
                exclusions_label.singular = "category"
                exclusions_label.plural = "categories"
                yield exclusions_label

            table = DataTable(id="categories-table", classes="data-table")
            table.add_columns(
                "Rank", "Category", "Amount", "Transactions", "Avg per Txn"
            )
            yield table

    def on_mount(self) -> None:
        """Called when widget is mounted."""
        super().on_mount()
        self.border_title = "Top Categories"
        self.add_class("table-widget")
        self._setup_query()

    def _setup_query(self) -> None:
        """Set up the data query function."""

        def get_categories_data():
            data_service = get_data_service()
            exclusions = self.app_state.exclusions
            top_categories = data_service.get_top_categories(
                limit=10, exclude=exclusions
            )

            # Convert to table rows
            rows = []
            for i, (category, total_amount, count) in enumerate(top_categories):
                avg_amount = total_amount / count if count > 0 else 0
                rows.append(
                    [
                        str(i + 1),
                        category,
                        f"£{total_amount:,.2f}",
                        str(count),
                        f"£{avg_amount:.2f}",
                    ]
                )
            return rows

        self.set_query_function(get_categories_data)

    def watch_data(self, data: list) -> None:
        """React to data changes."""
        try:
            table = self.query_one("#categories-table")
            table.clear()
            for row in data:
                table.add_row(*row)
        except Exception as e:
            logger.error(f"Error updating categories table: {e}")

    def on_exclusions_changed(self, event: AppEvent) -> None:
        """Handle exclusions change events."""
        logger.debug("TopCategoriesTable: Exclusions changed, refreshing data")
        self.refresh_data()


class TopMerchantsTable(DataWidget):
    """Widget displaying top spending merchants in a table format."""

    def compose(self) -> ComposeResult:
        """Compose the top merchants table widget."""
        with Container(classes="table-container"):
            yield Label("Top Spending Merchants", classes="table-title")

            table = DataTable(id="merchants-table", classes="data-table")
            table.add_columns(
                "Rank", "Merchant", "Amount", "Transactions", "Avg per Txn"
            )
            yield table

    def on_mount(self) -> None:
        """Called when widget is mounted."""
        super().on_mount()
        self.border_title = "Top Merchants"
        self.add_class("table-widget")
        self._setup_query()

    def _setup_query(self) -> None:
        """Set up the data query function."""

        def get_merchants_data():
            data_service = get_data_service()
            top_merchants = data_service.get_top_merchants(limit=10)

            # Convert to table rows
            rows = []
            for i, (merchant, total_amount, count) in enumerate(top_merchants):
                avg_amount = total_amount / count if count > 0 else 0
                rows.append(
                    [
                        str(i + 1),
                        merchant,
                        f"£{total_amount:,.2f}",
                        str(count),
                        f"£{avg_amount:.2f}",
                    ]
                )
            return rows

        self.set_query_function(get_merchants_data)

    def watch_data(self, data: list) -> None:
        """React to data changes."""
        try:
            table = self.query_one("#merchants-table")
            table.clear()
            for row in data:
                table.add_row(*row)
        except Exception as e:
            logger.error(f"Error updating merchants table: {e}")


class LatestTransactionsTable(DataWidget):
    """Widget displaying the latest transactions."""

    # Reactive property for transaction limit
    limit: reactive[int] = reactive(15)

    def compose(self) -> ComposeResult:
        """Compose the latest transactions table widget."""
        with Container(classes="table-container"):
            with Horizontal(classes="table-header"):
                yield Label("Latest Transactions", classes="table-title")
                transactions_label = CounterLabel(classes="transaction-count")
                transactions_label.state_key = "transaction_count"
                transactions_label.prefix = "(showing "
                transactions_label.suffix = f" of {{value}} total)"
                transactions_label.singular = "transaction"
                transactions_label.plural = "transactions"
                yield transactions_label

            table = DataTable(id="transactions-table", classes="data-table")
            table.add_columns("Date", "Description", "Category", "Merchant", "Amount")
            yield table

    def on_mount(self) -> None:
        """Called when widget is mounted."""
        super().on_mount()
        self.border_title = f"Latest {self.limit} Transactions"
        self.add_class("table-widget")
        self._setup_query()

    def _setup_query(self) -> None:
        """Set up the data query function."""

        def get_transactions_data():
            data_service = get_data_service()
            transactions = data_service.get_transactions(limit=self.limit)

            # Convert to table rows
            rows = []
            for transaction in transactions:
                rows.append(
                    [
                        transaction.date.strftime("%Y-%m-%d"),
                        transaction.description[:30] + "..."
                        if len(transaction.description) > 30
                        else transaction.description,
                        transaction.category,
                        transaction.merchant,
                        f"£{transaction.amount:,.2f}",
                    ]
                )
            return rows

        self.set_query_function(get_transactions_data)

    def watch_data(self, data: list) -> None:
        """React to data changes."""
        try:
            table = self.query_one("#transactions-table")
            table.clear()
            for row in data:
                table.add_row(*row)
        except Exception as e:
            logger.error(f"Error updating transactions table: {e}")

    def _format_count_label_text(self, total_count: int) -> str:
        """Format the count label text."""
        displayed = min(self.limit, total_count)
        return f"(showing {displayed} of {total_count} total)"


class CategorySummaryTable(DataWidget):
    """Widget displaying a summary of all categories with spending totals."""

    def compose(self) -> ComposeResult:
        """Compose the category summary table widget."""
        with Container(classes="table-container"):
            yield Label("Category Summary", classes="table-title")

            table = DataTable(id="category-summary-table", classes="data-table")
            table.add_columns(
                "Category", "Total Spent", "Transactions", "% of Total", "Status"
            )
            yield table

    def on_mount(self) -> None:
        """Called when widget is mounted."""
        super().on_mount()
        self.border_title = "All Categories"
        self.add_class("table-widget")
        self._setup_query()

    def _setup_query(self) -> None:
        """Set up the data query function."""

        def get_category_summary_data():
            data_service = get_data_service()
            exclusions = self.app_state.exclusions

            # Get all categories
            all_categories = data_service.get_top_categories(limit=100)
            total_spending = sum(amount for _, amount, _ in all_categories)

            # Convert to table rows
            rows = []
            for category, amount, count in all_categories:
                percentage = (
                    (amount / total_spending * 100) if total_spending > 0 else 0
                )
                status = "🚫 Excluded" if category in exclusions else "✅ Included"

                rows.append(
                    [
                        category,
                        f"£{amount:,.2f}",
                        str(count),
                        f"{percentage:.1f}%",
                        status,
                    ]
                )
            return rows

        self.set_query_function(get_category_summary_data)

    def watch_data(self, data: list) -> None:
        """React to data changes."""
        try:
            table = self.query_one("#category-summary-table")
            table.clear()
            for row in data:
                table.add_row(*row)
        except Exception as e:
            logger.error(f"Error updating category summary table: {e}")

    def on_exclusions_changed(self, event: AppEvent) -> None:
        """Handle exclusions change events."""
        logger.debug("CategorySummaryTable: Exclusions changed, refreshing data")
        self.refresh_data()
