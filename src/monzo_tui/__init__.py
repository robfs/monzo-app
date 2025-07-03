"""Monzo TUI app module."""

from .monzo import Monzo

__all__ = ["Monzo"]


def main() -> None:
    """Main entry point for the Monzo TUI application."""
    app = Monzo()
    app.run()
