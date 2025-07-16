"""Module containing all views."""

from .balance_view import BalanceView
from .code_editor_view import CodeEditorView
from .custom_sql_chart_view import CustomSQLChartView
from .custom_sql_table_view import CustomSQLTableView
from .data_view import DataView
from .exclusions_view import ExclusionsView
from .latest_transactions_view import LatestTransactionsView
from .logo_view import LogoView
from .monthly_chart_view import MonthlyChartView
from .pay_day_view import PayDayView
from .spending_last_month import SpendingLastMonthChartView
from .top_categories_table_view import TopCategoriesTableView
from .top_merchants_table_view import TopMerchantsTableView

__all__ = [
    "BalanceView",
    "CodeEditorView",
    "CustomSQLChartView",
    "CustomSQLTableView",
    "DataView",
    "ExclusionsView",
    "LatestTransactionsView",
    "LogoView",
    "MonthlyChartView",
    "PayDayView",
    "SpendingLastMonthChartView",
    "TopCategoriesTableView",
    "TopMerchantsTableView",
]
