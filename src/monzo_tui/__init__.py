"""Monzo TUI app module."""

from .stopwatch_app import StopwatchApp

__all__ = ["StopwatchApp"]


def main() -> None:
    """Main entry point for the Monzo TUI application."""
    app = StopwatchApp()
    app.run()
