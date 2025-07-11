"""Module containing utility functions."""

import calendar
import datetime
from typing import Literal

__all__ = ["next_pay_day"]


def _adjust_pay_day_for_month(year: int, month: int, pay_day: int) -> datetime.date:
    """Get the pay date for a given date and pay day, accounting for shorter months.

    Args:
        year: The year to get the pay date for
        month: The month to get the pay date for
        pay_day: The day of the month that pay occurs (1-31)

    Returns:
        The pay date for the given month, adjusted if the pay day doesn't exist
        in that month (e.g., 31st in February becomes 28th/29th)
    """
    last_day_of_month = calendar.monthrange(year, month)[1]
    if pay_day > last_day_of_month:
        return datetime.date(year, month, last_day_of_month)
    return datetime.date(year, month, pay_day)


def _adjust_pay_day_for_weekends(
    year: int, month: int, pay_day: int, move_to: Literal["next", "previous"]
) -> datetime.date:
    """Get the pay date for a month, adjusting for weekends.

    Args:
        year: The year to get the pay date for
        month: The month to get the pay date for
        pay_day: The day of the month that pay occurs (1-31)
        move_to: Direction to move weekend pay dates - "previous" moves to Friday,
                "next" moves to Monday

    Returns:
        The pay date for the given month, adjusted to avoid weekends.
        If pay day falls on Saturday/Sunday and move_to is "previous",
        returns the preceding Friday. If move_to is "next", returns
        the following Monday.
    """
    this_pay_day = _adjust_pay_day_for_month(year, month, pay_day)
    dow = this_pay_day.isoweekday()
    diff = max(0, dow - 5)
    if move_to == "previous":
        return this_pay_day - datetime.timedelta(days=diff)
    elif move_to == "next":
        if diff:
            return this_pay_day + datetime.timedelta(days=3 - diff)
        return this_pay_day


def next_pay_day(
    date: datetime.date, pay_day: int, move_to: Literal["next", "previous"]
) -> datetime.date:
    """Get the next pay date for a given date and pay day, accounting for weekends.

    Args:
        date: The current date to find the next pay date from
        pay_day: The day of the month that pay occurs (1-31)
        move_to: Direction to move weekend pay dates - "previous" moves to Friday,
                "next" moves to Monday

    Returns:
        The next pay date after the given date.
    """
    pay_date = _adjust_pay_day_for_weekends(date.year, date.month, pay_day, move_to)
    if date < pay_date:
        return pay_date
    if date.month == 12:
        year, month = date.year + 1, 1
    else:
        year, month = date.year, date.month + 1
    return _adjust_pay_day_for_weekends(year, month, pay_day, move_to)
