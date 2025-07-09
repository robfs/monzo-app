"""TopCategoriesTable widget."""

import logging

from textual.app import ComposeResult
from textual.containers import Container
from textual.widgets import Placeholder

__all__ = ["TopCategoriesTable"]

logger = logging.getLogger(__name__)


class TopCategoriesTable(Container):
    """Widget to display the top categories."""

    def compose(self) -> ComposeResult:
        logger.debug("Composing TopCategoriesTable")
        self.border_title = "Top Categories"
        self.add_class("card")
        yield Placeholder("Top Categories")
