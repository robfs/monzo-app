"""Modal screen to manage exclusions."""

import logging

from textual.app import ComposeResult
from textual.containers import Container
from textual.screen import ModalScreen
from textual.widgets import SelectionList

from v1.widgets.data_widget import DataWidget

__all__ = ["ExclusionsModalScreen"]

logger = logging.getLogger(__name__)


class ExclusionsWidget(Container, DataWidget):
    def compose(self) -> ComposeResult:
        self.sql_query = "select distinct category from transactions"
        self.border_title = "Excluded Categories"
        self.add_class("screen")
        yield SelectionList(id="exclusions")

    def on_mount(self) -> None:
        list = self.query_one(SelectionList)
        self.app.notify("Adding options...")
        list.clear_options()
        list.add_options(self.options())

    def options(self) -> list[tuple[str, str]]:
        self.fetch_data()
        return [(row[0], row[0]) for row in self.data]


class ExclusionsModalScreen(ModalScreen):
    """Modal screen to manage exclusions."""

    BINDINGS = [("escape", "app.pop_screen", "OK")]

    def compose(self) -> ComposeResult:
        yield ExclusionsWidget()

    def on_selection_list_selected_changed(
        self, event: SelectionList.SelectedChanged
    ) -> None:
        selection_list = self.query_one(SelectionList)
        self.app.get_screen("dashboard").exclusions = selection_list.selected
