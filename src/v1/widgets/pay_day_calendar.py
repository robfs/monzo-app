"""PayDayCalendar widget."""

import logging

from textual.app import ComposeResult
from textual.containers import Container
from textual.widgets import Placeholder

__all__ = ["PayDayCalendar"]

logger = logging.getLogger(__name__)


class PayDayCalendar(Container):
    """Widget to display the pay day calendar."""

    def compose(self) -> ComposeResult:
        logger.debug("Composing PayDayCalendar")
        self.border_title = "Pay Day Calendar"
        self.add_class("card")
        yield Placeholder("Pay Day Calendar")
