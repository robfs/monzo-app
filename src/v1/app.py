"""Main app file."""

import logging

from textual.app import App
from textual.logging import TextualHandler

from .screens import DashboardScreen

logging.basicConfig(level=logging.DEBUG, handlers=[TextualHandler()])


class MonzoApp(App):
    """Main app class."""

    CSS_PATH = "assets/styles.tcss"
    BINDINGS = [
        ("D", "push_screen('dashboard')", "Dashboard"),
        ("q", "request_quit", "Quit"),
    ]
    SCREENS = {
        "dashboard": DashboardScreen,
    }

    ## DEFAULT METHODS
    def on_mount(self) -> None:
        self.theme = "nord"
        self.push_screen("dashboard")

    ## ACTION METHODS
    def action_request_quit(self):
        self.exit()


app = MonzoApp()

if __name__ == "__main__":
    app = MonzoApp()
    app.run()
