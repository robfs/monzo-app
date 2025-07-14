"""Module defining the logo widget."""

import logging
from pathlib import Path

from textual.app import ComposeResult
from textual.containers import Container
from textual.widgets import Label

logger = logging.getLogger(__name__)


class Logo(Container):
    """Widget displaying the Monzo logo."""

    def compose(self) -> ComposeResult:
        yield Label()

    def on_mount(self) -> None:
        label = self.query_one(Label)
        with open(self.logo_path) as file:
            label.update(file.read())

    @property
    def logo_path(self) -> Path:
        widgets = Path(__file__).parent
        app = widgets.parent
        assets = app / "assets"
        return assets / "logo.txt"
