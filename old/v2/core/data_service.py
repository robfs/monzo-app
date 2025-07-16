"""Data service for managing application data and reactive updates."""

import logging
import random
from dataclasses import dataclass
from dataclasses import field
from datetime import datetime
from datetime import timedelta
from typing import Any

from .events import EventType
from .events import get_event_bus

logger = logging.getLogger(__name__)


@dataclass
class MockTransaction:
    """Mock transaction data for demonstration."""

    id: str
    date: datetime
    amount: float
    description: str
    category: str
    merchant: str

    def to_tuple(self) -> tuple:
        """Convert to tuple format for compatibility."""
        return (
            self.id,
            self.date.strftime("%Y-%m-%d"),
            self.amount,
            self.description,
            self.category,
            self.merchant,
        )


@dataclass
class DataState:
    """Current state of application data."""

    # Mock data
    transactions: list[MockTransaction] = field(default_factory=list)
    balance: float = 0.0
    categories: list[str] = field(default_factory=list)
    merchants: list[str] = field(default_factory=list)

    # Data status
    is_loading: bool = False
    last_updated: datetime | None = None
    error_message: str | None = None

    # Statistics
    total_spend_this_month: float = 0.0
    total_spend_last_month: float = 0.0
    transaction_count: int = 0


class DataService:
    """Service for managing application data with reactive updates."""

    def __init__(self):
        self._state = DataState()
        self._event_bus = get_event_bus()
        self._is_initialized = False

        # Mock data generators
        self._categories = [
            "Groceries",
            "Transport",
            "Entertainment",
            "Restaurants",
            "Shopping",
            "Bills",
            "Healthcare",
            "Education",
            "Travel",
            "Gas",
            "Coffee",
            "Subscriptions",
            "Gifts",
        ]

        self._merchants = [
            "Tesco",
            "Uber",
            "Netflix",
            "Amazon",
            "Starbucks",
            "Shell",
            "McDonald's",
            "Spotify",
            "Apple",
            "Google",
            "British Gas",
            "Sainsbury's",
            "Costa Coffee",
            "Waitrose",
            "M&S",
            "John Lewis",
            "Zara",
            "H&M",
            "IKEA",
            "Argos",
        ]

    @property
    def state(self) -> DataState:
        """Get current data state."""
        return self._state

    def get_balance(self) -> float:
        """Get current balance."""
        return self._state.balance

    def get_transactions(self, limit: int | None = None) -> list[MockTransaction]:
        """Get transactions, optionally limited."""
        transactions = self._state.transactions
        if limit:
            return transactions[:limit]
        return transactions

    def get_categories(self) -> list[str]:
        """Get all available categories."""
        return self._state.categories

    def get_merchants(self) -> list[str]:
        """Get all available merchants."""
        return self._state.merchants

    def is_loading(self) -> bool:
        """Check if data is currently loading."""
        return self._state.is_loading

    def has_data(self) -> bool:
        """Check if we have any data loaded."""
        return len(self._state.transactions) > 0

    def get_last_updated(self) -> datetime | None:
        """Get the timestamp of last data update."""
        return self._state.last_updated

    async def initialize(self) -> None:
        """Initialize the data service with mock data."""
        if self._is_initialized:
            return

        logger.info("Initializing data service")
        await self.refresh_data()
        self._is_initialized = True

    async def refresh_data(self) -> None:
        """Refresh all data from mock sources."""
        logger.info("DataService: Starting data refresh")

        # Set loading state
        self._state.is_loading = True
        self._state.error_message = None
        logger.debug(f"DataService: Set loading state to {self._state.is_loading}")
        self._emit_data_event(EventType.DATA_LOADING)

        try:
            # Simulate API delay
            logger.debug("DataService: Starting simulated API delay")
            await self._simulate_delay(1.0, 2.5)
            logger.debug("DataService: API delay completed")

            # Generate mock data
            logger.debug("DataService: Generating mock transactions")
            self._generate_mock_transactions()
            logger.debug("DataService: Calculating statistics")
            self._calculate_statistics()

            # Update state
            self._state.is_loading = False
            self._state.last_updated = datetime.now()
            logger.debug(f"DataService: Set loading state to {self._state.is_loading}")

            logger.info(
                f"DataService: Data refreshed successfully - {len(self._state.transactions)} transactions loaded"
            )
            self._emit_data_event(EventType.DATA_UPDATED)

        except Exception as e:
            logger.error(f"DataService: Error refreshing data: {e}")
            self._state.is_loading = False
            self._state.error_message = str(e)
            logger.debug(
                f"DataService: Set loading state to {self._state.is_loading} due to error"
            )
            self._emit_data_event(EventType.DATA_ERROR, {"error": str(e)})

    def _generate_mock_transactions(self) -> None:
        """Generate mock transaction data."""
        transactions = []

        # Generate transactions for the last 90 days
        start_date = datetime.now() - timedelta(days=90)
        num_transactions = random.randint(50, 150)

        for i in range(num_transactions):
            # Random date within the last 90 days
            days_ago = random.randint(0, 90)
            transaction_date = start_date + timedelta(days=days_ago)

            # Random transaction details
            category = random.choice(self._categories)
            merchant = random.choice(self._merchants)
            amount = round(random.uniform(-200.0, -5.0), 2)  # Negative for expenses

            # Occasional positive amounts (refunds, income)
            if random.random() < 0.05:  # 5% chance
                amount = round(random.uniform(50.0, 1000.0), 2)

            transaction = MockTransaction(
                id=f"tx_{i:04d}",
                date=transaction_date,
                amount=amount,
                description=f"{merchant} Purchase",
                category=category,
                merchant=merchant,
            )
            transactions.append(transaction)

        # Sort by date (most recent first)
        transactions.sort(key=lambda t: t.date, reverse=True)

        self._state.transactions = transactions
        self._state.categories = list(set(self._categories))
        self._state.merchants = list(set(self._merchants))
        self._state.transaction_count = len(transactions)

    def _calculate_statistics(self) -> None:
        """Calculate derived statistics from transaction data."""
        now = datetime.now()
        current_month_start = now.replace(
            day=1, hour=0, minute=0, second=0, microsecond=0
        )
        last_month_start = (current_month_start - timedelta(days=1)).replace(day=1)

        # Calculate balance (sum of all transactions)
        self._state.balance = sum(t.amount for t in self._state.transactions)

        # Calculate monthly spending (only negative amounts)
        current_month_spend = sum(
            abs(t.amount)
            for t in self._state.transactions
            if t.date >= current_month_start and t.amount < 0
        )

        last_month_spend = sum(
            abs(t.amount)
            for t in self._state.transactions
            if last_month_start <= t.date < current_month_start and t.amount < 0
        )

        self._state.total_spend_this_month = current_month_spend
        self._state.total_spend_last_month = last_month_spend

    async def _simulate_delay(self, min_seconds: float, max_seconds: float) -> None:
        """Simulate API delay for realistic loading experience."""
        import asyncio

        delay = random.uniform(min_seconds, max_seconds)
        await asyncio.sleep(delay)

    def _emit_data_event(self, event_type: EventType, data: Any = None) -> None:
        """Emit a data-related event."""
        event_data = {
            "state": {
                "is_loading": self._state.is_loading,
                "has_data": self.has_data(),
                "transaction_count": self._state.transaction_count,
                "last_updated": self._state.last_updated,
                "error": self._state.error_message,
            }
        }

        if data:
            event_data.update(data)

        logger.debug(
            f"DataService: Emitting {event_type.value} event with is_loading={self._state.is_loading}"
        )
        self._event_bus.emit_simple(event_type, data=event_data, source="DataService")

    def get_top_categories(
        self, limit: int = 5, exclude: list[str] = None
    ) -> list[tuple[str, float, int]]:
        """Get top spending categories."""
        exclude = exclude or []

        category_totals = {}
        category_counts = {}

        for transaction in self._state.transactions:
            if transaction.category in exclude or transaction.amount >= 0:
                continue

            category = transaction.category
            amount = abs(transaction.amount)

            category_totals[category] = category_totals.get(category, 0) + amount
            category_counts[category] = category_counts.get(category, 0) + 1

        # Sort by total amount
        sorted_categories = sorted(
            category_totals.items(), key=lambda x: x[1], reverse=True
        )

        return [
            (category, amount, category_counts[category])
            for category, amount in sorted_categories[:limit]
        ]

    def get_top_merchants(self, limit: int = 5) -> list[tuple[str, float, int]]:
        """Get top spending merchants."""
        merchant_totals = {}
        merchant_counts = {}

        for transaction in self._state.transactions:
            if transaction.amount >= 0:  # Skip income
                continue

            merchant = transaction.merchant
            amount = abs(transaction.amount)

            merchant_totals[merchant] = merchant_totals.get(merchant, 0) + amount
            merchant_counts[merchant] = merchant_counts.get(merchant, 0) + 1

        # Sort by total amount
        sorted_merchants = sorted(
            merchant_totals.items(), key=lambda x: x[1], reverse=True
        )

        return [
            (merchant, amount, merchant_counts[merchant])
            for merchant, amount in sorted_merchants[:limit]
        ]

    def get_monthly_spending_data(self, months: int = 6) -> list[tuple[str, float]]:
        """Get monthly spending data for charts."""
        monthly_data = {}

        for transaction in self._state.transactions:
            if transaction.amount >= 0:  # Skip income
                continue

            month_key = transaction.date.strftime("%Y-%m")
            amount = abs(transaction.amount)
            monthly_data[month_key] = monthly_data.get(month_key, 0) + amount

        # Sort by month and limit to requested number of months
        sorted_months = sorted(monthly_data.items(), reverse=True)
        return sorted_months[:months]


# Global data service instance
_data_service = DataService()


def get_data_service() -> DataService:
    """Get the global data service instance."""
    return _data_service
