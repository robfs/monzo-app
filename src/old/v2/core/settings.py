"""Settings service for app-wide configuration management."""

import logging
import os
from pathlib import Path
from typing import Any, Dict, Optional
from dataclasses import dataclass, field

from .events import get_event_bus, EventType

logger = logging.getLogger(__name__)


@dataclass
class AppSettings:
    """Data class to hold application settings."""

    # Monzo API settings
    spreadsheet_id: Optional[str] = field(
        default_factory=lambda: os.getenv("MONZO_SPREADSHEET_ID")
    )
    credentials_path: str = "~/.monzo/credentials.json"

    # Pay day settings
    pay_day_type: str = "specific"  # "first", "last", "specific"
    pay_day: int = field(default_factory=lambda: int(os.getenv("MONZO_PAY_DAY", "31")))

    # UI settings
    theme: str = "nord"
    auto_refresh_interval: int = 300  # seconds

    # Data settings
    exclusions: list[str] = field(default_factory=list)

    def __post_init__(self):
        """Validate settings after initialization."""
        if self.pay_day < 1 or self.pay_day > 31:
            self.pay_day = 31
            logger.warning("Invalid pay_day value, defaulting to 31")

    @property
    def credentials_path_resolved(self) -> Path:
        """Get the resolved credentials path."""
        return Path(self.credentials_path).expanduser()

    def to_dict(self) -> Dict[str, Any]:
        """Convert settings to dictionary."""
        return {
            "spreadsheet_id": self.spreadsheet_id,
            "credentials_path": self.credentials_path,
            "pay_day_type": self.pay_day_type,
            "pay_day": self.pay_day,
            "theme": self.theme,
            "auto_refresh_interval": self.auto_refresh_interval,
            "exclusions": self.exclusions.copy(),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AppSettings":
        """Create settings from dictionary."""
        return cls(**data)


class SettingsService:
    """Service for managing application settings."""

    def __init__(self):
        self._settings = AppSettings()
        self._event_bus = get_event_bus()
        self._listeners: list = []

    @property
    def settings(self) -> AppSettings:
        """Get current settings."""
        return self._settings

    def get(self, key: str, default: Any = None) -> Any:
        """Get a specific setting value."""
        return getattr(self._settings, key, default)

    def update(self, **kwargs) -> None:
        """Update multiple settings and emit change event."""
        old_settings = self._settings.to_dict()

        for key, value in kwargs.items():
            if hasattr(self._settings, key):
                setattr(self._settings, key, value)
                logger.debug(f"Updated setting {key} = {value}")
            else:
                logger.warning(f"Unknown setting key: {key}")

        new_settings = self._settings.to_dict()
        changes = {
            key: {"old": old_settings[key], "new": new_settings[key]}
            for key in old_settings
            if old_settings[key] != new_settings[key]
        }

        if changes:
            logger.info(f"Settings changed: {list(changes.keys())}")
            self._event_bus.emit_simple(
                EventType.SETTINGS_CHANGED,
                data={"changes": changes, "settings": new_settings},
                source="SettingsService",
            )

    def set(self, key: str, value: Any) -> None:
        """Set a single setting value."""
        self.update(**{key: value})

    def reset_to_defaults(self) -> None:
        """Reset all settings to their default values."""
        logger.info("Resetting settings to defaults")
        self._settings = AppSettings()
        self._event_bus.emit_simple(
            EventType.SETTINGS_CHANGED,
            data={"changes": {}, "settings": self._settings.to_dict()},
            source="SettingsService",
        )

    def add_exclusion(self, category: str) -> None:
        """Add a category to exclusions."""
        if category not in self._settings.exclusions:
            self._settings.exclusions.append(category)
            logger.debug(f"Added exclusion: {category}")
            self._event_bus.emit_simple(
                EventType.EXCLUSIONS_CHANGED,
                data={
                    "added": category,
                    "exclusions": self._settings.exclusions.copy(),
                },
                source="SettingsService",
            )

    def remove_exclusion(self, category: str) -> None:
        """Remove a category from exclusions."""
        if category in self._settings.exclusions:
            self._settings.exclusions.remove(category)
            logger.debug(f"Removed exclusion: {category}")
            self._event_bus.emit_simple(
                EventType.EXCLUSIONS_CHANGED,
                data={
                    "removed": category,
                    "exclusions": self._settings.exclusions.copy(),
                },
                source="SettingsService",
            )

    def set_exclusions(self, exclusions: list[str]) -> None:
        """Set the complete list of exclusions."""
        old_exclusions = self._settings.exclusions.copy()
        self._settings.exclusions = exclusions.copy()

        if old_exclusions != exclusions:
            logger.info(f"Exclusions updated: {exclusions}")
            self._event_bus.emit_simple(
                EventType.EXCLUSIONS_CHANGED,
                data={"exclusions": exclusions.copy()},
                source="SettingsService",
            )

    def validate_settings(self) -> Dict[str, str]:
        """Validate current settings and return any errors."""
        errors = {}

        if not self._settings.spreadsheet_id:
            errors["spreadsheet_id"] = "Spreadsheet ID is required"

        if not self._settings.credentials_path_resolved.exists():
            errors["credentials_path"] = "Credentials file does not exist"

        if not self._settings.credentials_path_resolved.is_file():
            errors["credentials_path"] = "Credentials path is not a file"

        return errors

    def is_valid(self) -> bool:
        """Check if current settings are valid."""
        return len(self.validate_settings()) == 0


# Global settings service instance
_settings_service = SettingsService()


def get_settings_service() -> SettingsService:
    """Get the global settings service instance."""
    return _settings_service
