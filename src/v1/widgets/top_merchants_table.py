"""TopMerchantsTable widget."""

import logging

from textual.app import ComposeResult
from textual.containers import Container
from textual.widgets import Placeholder

__all__ = ["TopMerchantsTable"]

logger = logging.getLogger(__name__)


class TopMerchantsTable(Container):
    """Widget to display the top merchants."""

    def compose(self) -> ComposeResult:
        logger.debug("Composing TopMerchantsTable")
        self.border_title = "Top Merchants"
        self.add_class("card")
        yield Placeholder("Top Merchants")
