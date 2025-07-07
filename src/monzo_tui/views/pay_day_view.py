"""Module containing the PayDayView class."""

import calendar
import datetime
import logging
import re

from textual.app import ComposeResult
from textual.containers import Container
from textual.widgets import Label
from textual.reactive import reactive

from ..utilities import next_pay_day

logger = logging.getLogger(__name__)

__all__ = ["PayDayView"]


class PayDayView(Label):
    """A placeholder widget for the pay month."""

    pay_day = reactive(31)
    pay_date = reactive(datetime.date.today())
    today = reactive(datetime.date.today())

    def on_mount(self) -> None:
        cal = calendar.month(2025, 7)
        # self._render_markup = False
        self.border_title = "Pay Day"
        self.update(cal)

    def get_previous_month_calendar(self) -> str:
        if self.today.month == 1:
            cal = calendar.month(self.today.year - 1, 12)
        else:
            cal = calendar.month(self.today.year, self.today.month - 1)
        # Dim all days
        cal = re.sub(r"(\s)1(\s)", r"\1[dim]1\2", cal)
        cal += "[/dim]"
        return cal

    def dim_before_and_highlight_today(self, cal: str, tag: str) -> str:
        cal = re.sub(r"(\s)1(\s)", r"\1[dim]1\2", cal)
        cal = re.sub(rf"(\s)({self.today.day}\s)", rf"\1[/dim][{tag}]\2", cal)
        return cal

    def highlight_all(self, cal: str, tag: str) -> str:
        cal = re.sub(r"(\s)1(\s)", rf"\1[{tag}]\2", cal)
        return cal

    def highlight_pay_day(self, cal: str, tag: str) -> str:
        cal = re.sub(
            rf"(\s)({self.pay_date.day})(\s)", rf"\1[/][{tag}]\2[/{tag}]\3", cal
        )
        return cal

    def top_calendar(self, tag: str) -> str:
        if self.today.month == self.pay_date.month:
            return self.get_previous_month_calendar()
        else:
            cal = calendar.month(self.today.year, self.today.month)
            cal = self.dim_before_and_highlight_today(cal, tag)
            return cal + "[/]"

    def bottom_calendar(self, today_tag: str, pay_day_tag: str) -> str:
        cal = calendar.month(self.today.year, self.pay_date.month)
        if self.today.month == self.pay_date.month:
            cal = self.dim_before_and_highlight_today(cal, today_tag)
        else:
            cal = self.highlight_all(cal, today_tag)
        cal = self.highlight_pay_day(cal, pay_day_tag)
        return cal

    def watch_pay_day(self, pay_day: int) -> None:
        self.today = datetime.date.today()
        self.pay_date = next_pay_day(self.today, pay_day, "next")
        diff = self.pay_date - self.today
        today_tag: str = "auto on $secondary"
        pay_day_tag: str = "auto on $primary"
        top_calendar = self.top_calendar(today_tag)
        bottom_calendar = self.bottom_calendar(today_tag, pay_day_tag)
        self.border_subtitle = f"{diff.days} days left"
        self.update(f"{top_calendar}\n\n{bottom_calendar}")
