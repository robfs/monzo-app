"""Main app file."""

import logging

from textual.app import App
from textual.app import ComposeResult
from textual.logging import TextualHandler
from textual.widgets import Footer
from textual.widgets import Header

from screens import DashboardScreen
from screens import OtherScreen

logging.basicConfig(
    level=logging.DEBUG,
    handlers=[TextualHandler()],
    format="%(asctime)s | %(name)s:%(lineno)d | %(levelname)8s | %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)


class MonzoApp(App):
    """Main app class."""

    CSS_PATH = "assets/styles.tcss"
    BINDINGS = [
        ("D", "switch_screen('dashboard')", "Dashboard"),
        ("O", "switch_screen('other')", "Other"),
        ("q", "quit", "Quit"),
    ]
    SCREENS = {"dashboard": DashboardScreen, "other": OtherScreen}

    def compose(self) -> ComposeResult:
        """Compose the app."""
        logger.debug("Composing the application.")
        yield Header()
        yield Footer()

    def on_mount(self) -> None:
        """Mount the app."""
        logger.debug("Mounting the application.")
        self.push_screen("dashboard")

    async def action_push_screen(self, screen: str) -> None:
        logger.debug(f"Pushing screen {screen}")
        logger.debug(f"{self.screen_stack=}")
        return await super().action_push_screen(screen)

    async def action_switch_screen(self, screen: str) -> None:
        logger.debug(f"Switching to screen {screen}")
        logger.debug(f"{self.screen_stack=}")
        return await super().action_switch_screen(screen)


app = MonzoApp()


if __name__ == "__main__":
    app = MonzoApp()
    app.run()
