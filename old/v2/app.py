"""Main application file for Monzo app v2 with improved architecture."""

import asyncio
import logging
from typing import Any

from core import AppEvent
from core import EventType
from core import get_app_state
from core import get_data_service
from core import get_event_bus
from core import get_settings_service
from screens import DashboardScreen
from screens import ExclusionsScreen
from screens import SettingsScreen
from textual import work
from textual.app import App
from textual.app import ComposeResult
from textual.logging import TextualHandler
from textual.widgets import Footer
from textual.widgets import Header

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    handlers=[TextualHandler()],
    format="%(name)s: %(message)s",
)

logger = logging.getLogger(__name__)


class MonzoApp(App):
    """Main Monzo application with reactive architecture."""

    CSS_PATH = "assets/styles.tcss"

    BINDINGS = [
        ("d", "push_screen('dashboard')", "Dashboard"),
        ("s", "open_settings", "Settings"),
        ("e", "open_exclusions", "Exclusions"),
        ("r", "refresh_data", "Refresh"),
        ("q", "quit", "Quit"),
        ("ctrl+c", "quit", "Quit"),
        ("?", "show_help", "Help"),
    ]

    SCREENS = {
        "dashboard": DashboardScreen,
        "settings": SettingsScreen,
        "exclusions": ExclusionsScreen,
    }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._app_state = get_app_state()
        self._settings_service = get_settings_service()
        self._data_service = get_data_service()
        self._event_bus = get_event_bus()
        self._is_ready = False

    def compose(self) -> ComposeResult:
        """Compose the main application layout."""
        yield Header()
        yield Footer()

    async def on_mount(self) -> None:
        """Called when the app is mounted."""
        logger.info("Monzo app v2 starting up...")

        # Set theme
        theme = self._settings_service.get("theme", "nord")
        self.theme = theme

        # Set up event subscriptions
        self._setup_event_listeners()

        # Initialize data service and show dashboard
        await self._initialize_app()

        # Start with dashboard
        self.push_screen("dashboard")

        logger.info("Monzo app v2 ready!")

    def _setup_event_listeners(self) -> None:
        """Set up application-level event listeners."""

        def on_refresh_requested(event: AppEvent) -> None:
            """Handle refresh requests from anywhere in the app."""
            logger.info("App: Refresh requested")
            self.refresh_data_async()

        def on_settings_changed(event: AppEvent) -> None:
            """Handle settings changes."""
            if event.data and "settings" in event.data:
                settings = event.data["settings"]
                # Update theme if it changed
                new_theme = settings.get("theme")
                if new_theme and new_theme != self.theme:
                    self.theme = new_theme
                    logger.info(f"App: Theme changed to {new_theme}")

        def on_app_ready(event: AppEvent) -> None:
            """Handle app ready event."""
            self._is_ready = True
            logger.info("App: Application marked as ready")

        # Subscribe to events
        self._event_bus.subscribe(EventType.REFRESH_REQUESTED, on_refresh_requested)
        self._event_bus.subscribe(EventType.SETTINGS_CHANGED, on_settings_changed)
        self._event_bus.subscribe(EventType.APP_READY, on_app_ready)

    async def _initialize_app(self) -> None:
        """Initialize the application asynchronously."""
        try:
            # Initialize data service
            await self._data_service.initialize()

            # Mark app as ready
            self._app_state.set_ready()

            logger.info("App initialization completed successfully")

        except Exception as e:
            logger.error(f"Error during app initialization: {e}")
            self.notify(f"Initialization error: {e}", severity="error")

    # Action methods
    async def action_quit(self) -> None:
        """Quit the application."""
        logger.info("App: Quit requested")
        self._app_state.shutdown()
        self.exit()

    def action_refresh_data(self) -> None:
        """Refresh data action."""
        logger.info("App: Manual refresh requested")
        self.refresh_data_async()

    def action_open_settings(self) -> None:
        """Open settings modal."""
        logger.info("App: Opening settings")

        def on_settings_saved(result: dict | None) -> None:
            """Handle settings save callback."""
            if result:
                logger.info("App: Settings saved from modal")
                self.notify("Settings saved successfully", severity="information")
                # Settings service will emit events automatically
            else:
                logger.debug("App: Settings modal cancelled")

        def on_settings_cancelled() -> None:
            """Handle settings cancel callback."""
            logger.debug("App: Settings modal cancelled")

        settings_screen = SettingsScreen()
        settings_screen.on_save_callback = on_settings_saved
        settings_screen.on_cancel_callback = on_settings_cancelled
        self.push_screen(settings_screen)

    def action_open_exclusions(self) -> None:
        """Open exclusions modal."""
        logger.info("App: Opening exclusions")

        def on_exclusions_saved(result: dict | None) -> None:
            """Handle exclusions save callback."""
            if result:
                excluded_count = len(result.get("exclusions", []))
                logger.info(
                    f"App: Exclusions saved - {excluded_count} categories excluded"
                )
                self.notify(
                    f"Exclusions updated: {excluded_count} categories excluded",
                    severity="information",
                )
            else:
                logger.debug("App: Exclusions modal cancelled")

        def on_exclusions_cancelled() -> None:
            """Handle exclusions cancel callback."""
            logger.debug("App: Exclusions modal cancelled")

        exclusions_screen = ExclusionsScreen()
        exclusions_screen.on_save_callback = on_exclusions_saved
        exclusions_screen.on_cancel_callback = on_exclusions_cancelled
        self.push_screen(exclusions_screen)

    def action_show_help(self) -> None:
        """Show help information."""
        help_text = """
Monzo App v2 - Reactive Financial Analytics

Key Bindings:
• D - Dashboard (main screen)
• S - Settings (configure app)
• E - Exclusions (manage categories)
• R - Refresh data
• Q / Ctrl+C - Quit application
• ? - Show this help

Features:
• Reactive data flow - components update automatically
• Real-time balance and transaction tracking
• Category-based spending analysis
• Customizable exclusions
• Multiple chart views and data tables

This is a demonstration version showing reactive architecture.
Data is mocked for educational purposes.
        """
        self.notify(help_text.strip(), title="Help", timeout=10)

    @work(exclusive=True, thread=True)
    def refresh_data_async(self) -> None:
        """Refresh data in a background thread."""
        logger.info("App: Starting background data refresh")
        try:
            # This will run the async refresh in a thread
            asyncio.run(self._data_service.refresh_data())
        except Exception as e:
            logger.error(f"Error during background refresh: {e}")
            self.call_from_thread(self.notify, f"Refresh error: {e}", severity="error")

    async def _on_exit_app(self) -> None:
        """Called when the app is exiting."""
        logger.info("App: Shutting down...")

        try:
            # Clean up state
            self._app_state.shutdown()

            # Close any database connections if they exist
            # (In real implementation, this would close the DuckDB connection)

            logger.info("App: Cleanup completed")
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")

        return await super()._on_exit_app()

    # Properties for debugging and monitoring
    @property
    def is_ready(self) -> bool:
        """Check if the application is ready."""
        return self._is_ready

    @property
    def app_state(self):
        """Get the application state for debugging."""
        return self._app_state

    def get_debug_info(self) -> dict[str, Any]:
        """Get debug information about the application state."""
        try:
            current_screen = (
                self.screen.title if hasattr(self.screen, "title") else "unknown"
            )
        except Exception:
            current_screen = "no_screen"

        return {
            "is_ready": self.is_ready,
            "theme": self.theme,
            "current_screen": current_screen,
            "state_summary": self._app_state.get_state_summary(),
            "settings_valid": self._settings_service.is_valid(),
            "data_loaded": self._data_service.has_data(),
        }


def create_app() -> MonzoApp:
    """Factory function to create the app."""
    return MonzoApp()


app = create_app()


def main():
    """Main entry point for the application."""
    app = create_app()

    try:
        app.run()
    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise
    finally:
        logger.info("Application shutdown complete")


if __name__ == "__main__":
    main()
