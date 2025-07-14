"""Module containing the SQL editor component view."""

from textual.app import ComposeResult
from textual.widgets import Button
from textual.widgets import Static
from textual.widgets import TextArea

__all__ = ["CodeEditorView"]


class CodeEditorView(Static):
    """A custom text area widget for displaying SQL queries."""

    def compose(self) -> ComposeResult:
        query = "select\n\tcategory,\n\tsum(amount) as total_amount\nfrom transactions\ngroup by category\norder by total_amount desc"
        yield TextArea.code_editor(query, language="sql", theme="css")
        yield Button("Run Query", variant="success", id="run-query")

    def on_mount(self) -> None:
        self.border_title = "SQL Editor"
