"""LogoView class for displaying the Monzo logo."""

from pathlib import Path

from textual.app import ComposeResult
from textual.reactive import reactive
from textual.widgets import Label
from textual.widgets import Static


class LogoView(Static):
    """LogoView class for displaying the Monzo logo."""

    logo_text = reactive("")

    def compose(self) -> ComposeResult:
        local = Path(__file__).parent
        main = local.parent
        assets = main / "assets"
        with open(assets / "logo.txt") as file:
            self.logo_text = file.read()
        yield Label(self.logo_text)
