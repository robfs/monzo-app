"""Helper utility functions for the Monzo app v2."""

import logging
from datetime import datetime
from typing import Any, Optional

logger = logging.getLogger(__name__)


def format_currency(
    amount: float, currency_symbol: str = "£", decimal_places: int = 2
) -> str:
    """Format a number as currency with proper formatting.

    Args:
        amount: The amount to format
        currency_symbol: Currency symbol to use (default: £)
        decimal_places: Number of decimal places (default: 2)

    Returns:
        Formatted currency string
    """
    try:
        return f"{currency_symbol}{amount:,.{decimal_places}f}"
    except (ValueError, TypeError):
        return f"{currency_symbol}0.00"


def format_percentage(value: float, decimal_places: int = 1) -> str:
    """Format a number as a percentage.

    Args:
        value: The value to format (0.15 -> 15.0%)
        decimal_places: Number of decimal places (default: 1)

    Returns:
        Formatted percentage string
    """
    try:
        return f"{value * 100:.{decimal_places}f}%"
    except (ValueError, TypeError):
        return "0.0%"


def format_date(
    date: datetime, format_string: str = "%Y-%m-%d", fallback: str = "Never"
) -> str:
    """Format a datetime object as a string.

    Args:
        date: The datetime object to format
        format_string: The format string to use (default: %Y-%m-%d)
        fallback: What to return if date is None (default: Never)

    Returns:
        Formatted date string
    """
    if date is None:
        return fallback

    try:
        return date.strftime(format_string)
    except (AttributeError, ValueError):
        return fallback


def truncate_text(text: str, max_length: int = 30, suffix: str = "...") -> str:
    """Truncate text to a maximum length with optional suffix.

    Args:
        text: The text to truncate
        max_length: Maximum length before truncation (default: 30)
        suffix: Suffix to add when truncated (default: ...)

    Returns:
        Truncated text string
    """
    if not isinstance(text, str):
        text = str(text)

    if len(text) <= max_length:
        return text

    return text[: max_length - len(suffix)] + suffix


def safe_divide(numerator: float, denominator: float, fallback: float = 0.0) -> float:
    """Safely divide two numbers, returning fallback on division by zero.

    Args:
        numerator: The numerator
        denominator: The denominator
        fallback: Value to return if division by zero (default: 0.0)

    Returns:
        Division result or fallback
    """
    try:
        if denominator == 0:
            return fallback
        return numerator / denominator
    except (TypeError, ValueError):
        return fallback


def clamp(value: float, min_value: float, max_value: float) -> float:
    """Clamp a value between minimum and maximum bounds.

    Args:
        value: The value to clamp
        min_value: Minimum allowed value
        max_value: Maximum allowed value

    Returns:
        Clamped value
    """
    try:
        return max(min_value, min(max_value, value))
    except (TypeError, ValueError):
        return min_value


def pluralize(count: int, singular: str, plural: Optional[str] = None) -> str:
    """Return the correct plural form based on count.

    Args:
        count: The count to check
        singular: Singular form of the word
        plural: Plural form (default: singular + 's')

    Returns:
        Correct form of the word
    """
    if plural is None:
        plural = singular + "s"

    return singular if count == 1 else plural


def format_count(count: int, singular: str, plural: Optional[str] = None) -> str:
    """Format a count with the correct plural form.

    Args:
        count: The count to format
        singular: Singular form of the word
        plural: Plural form (default: singular + 's')

    Returns:
        Formatted count string (e.g., "1 item", "5 items")
    """
    word = pluralize(count, singular, plural)
    return f"{count:,} {word}"


def generate_bar_chart(
    value: float,
    max_value: float,
    width: int = 20,
    filled_char: str = "█",
    empty_char: str = "░",
) -> str:
    """Generate a simple ASCII bar chart.

    Args:
        value: Current value
        max_value: Maximum value for the bar
        width: Width of the bar in characters (default: 20)
        filled_char: Character for filled portion (default: █)
        empty_char: Character for empty portion (default: ░)

    Returns:
        ASCII bar chart string
    """
    if max_value <= 0:
        return empty_char * width

    ratio = clamp(value / max_value, 0.0, 1.0)
    filled_width = int(ratio * width)
    empty_width = width - filled_width

    return filled_char * filled_width + empty_char * empty_width


def format_time_ago(timestamp: datetime) -> str:
    """Format a timestamp as "time ago" string.

    Args:
        timestamp: The timestamp to format

    Returns:
        Human-readable time ago string
    """
    if timestamp is None:
        return "Never"

    try:
        now = datetime.now()
        diff = now - timestamp

        seconds = diff.total_seconds()

        if seconds < 60:
            return f"{int(seconds)} seconds ago"
        elif seconds < 3600:
            minutes = int(seconds / 60)
            return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
        elif seconds < 86400:
            hours = int(seconds / 3600)
            return f"{hours} hour{'s' if hours != 1 else ''} ago"
        else:
            days = int(seconds / 86400)
            return f"{days} day{'s' if days != 1 else ''} ago"

    except (AttributeError, TypeError):
        return "Unknown"


def validate_pay_day(pay_day: int) -> bool:
    """Validate that a pay day is within valid range.

    Args:
        pay_day: The pay day to validate

    Returns:
        True if valid, False otherwise
    """
    try:
        return 1 <= int(pay_day) <= 31
    except (ValueError, TypeError):
        return False


def camel_to_title(camel_string: str) -> str:
    """Convert camelCase string to Title Case.

    Args:
        camel_string: String in camelCase format

    Returns:
        String in Title Case format
    """
    import re

    # Insert space before uppercase letters
    result = re.sub(r"(?<=[a-z])(?=[A-Z])", " ", camel_string)
    return result.title()


def snake_to_title(snake_string: str) -> str:
    """Convert snake_case string to Title Case.

    Args:
        snake_string: String in snake_case format

    Returns:
        String in Title Case format
    """
    return snake_string.replace("_", " ").title()


def format_file_size(size_bytes: int) -> str:
    """Format file size in human-readable format.

    Args:
        size_bytes: Size in bytes

    Returns:
        Human-readable size string
    """
    try:
        for unit in ["B", "KB", "MB", "GB", "TB"]:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} PB"
    except (TypeError, ValueError):
        return "0 B"


def parse_currency(currency_string: str) -> float:
    """Parse a currency string and return the numeric value.

    Args:
        currency_string: String like "£123.45" or "$1,234.56"

    Returns:
        Numeric value as float
    """
    try:
        # Remove currency symbols and commas
        import re

        cleaned = re.sub(r"[£$€¥,]", "", currency_string)
        return float(cleaned)
    except (ValueError, TypeError):
        return 0.0


def mask_sensitive_data(data: str, visible_chars: int = 4, mask_char: str = "*") -> str:
    """Mask sensitive data, showing only the last few characters.

    Args:
        data: The sensitive data to mask
        visible_chars: Number of characters to show at the end (default: 4)
        mask_char: Character to use for masking (default: *)

    Returns:
        Masked string
    """
    if not data or len(data) <= visible_chars:
        return data

    mask_length = len(data) - visible_chars
    return mask_char * mask_length + data[-visible_chars:]
