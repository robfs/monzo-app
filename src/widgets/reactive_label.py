"""Module containing ReactiveLabel widget."""

import logging

from textual.message import Message
from textual.reactive import reactive
from textual.widgets import Label

__all__ = ["ReactiveLabel"]

logger = logging.getLogger(__name__)


class ReactiveLabel(Label):
    """A label that updates its text based on a reactive value."""

    is_updating = reactive(False)

    async def watch_is_updating(self, is_updating: bool) -> None:
        if is_updating:
            self.update("🔄 Loading...")
        else:
            self.update("✅ Up to date")

    class IsUpdating(Message):
        """Message sent when the label is updating."""

    def set_updating(self) -> None:
        self.is_updating = True
        self.add_class("loading-label")
        self.post_message(self.IsUpdating())

    class UpdateComplete(Message):
        """Message sent when the label has finished updating."""

    def stop_updating(self) -> None:
        self.is_updating = False
        self.post_message(self.UpdateComplete())
        self.remove_class("loading-label")
