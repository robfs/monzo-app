"""PayDayCalendar widget."""

import calendar
import datetime
import logging
import os
import re

from textual.app import ComposeResult
from textual.containers import Container
from textual.reactive import reactive
from textual.widgets import Label

from ..utilities import next_pay_day

__all__ = ["PayDayCalendar"]

logger = logging.getLogger(__name__)


class PayDayCalendar(Container):
    """Widget to display the pay day calendar."""

    pay_day = reactive(int(os.getenv("MONZO_PAY_DAY", "31")))
    pay_date = reactive(datetime.date.today())
    today = reactive(datetime.date.today())

    def compose(self) -> ComposeResult:
        self.add_class("card")
        yield Label("Pay Day Calendar")

    def on_mount(self) -> None:
        cal = calendar.month(2025, 7)
        self.border_title = "Pay Day"
        self.update(cal)

    def update(self, cal: str) -> None:
        self.query_one(Label).update(cal)

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
        cal = re.sub(
            rf"(\s)({self.today.day})(\s)", rf"\1[/dim][{tag}][bold]\2[/bold]\3", cal
        )
        return cal

    def highlight_all(self, cal: str, tag: str) -> str:
        cal = re.sub(r"(\s1\s)", rf"[{tag}]\1", cal)
        return cal

    def highlight_pay_day(self, cal: str, tag: str) -> str:
        cal = re.sub(rf"(\s{self.pay_date.day}\s)", rf"[/][{tag}]\1[/{tag}]", cal)
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
