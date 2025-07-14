"""Settings modal screen for configuration management."""

import logging
from pathlib import Path
from textual.app import ComposeResult
from textual.containers import Container, Grid, Horizontal
from textual.widgets import Input, Select, Button, Label
from textual.reactive import reactive
from textual import on

from screens.base import ConfigurableModalScreen
from core import AppEvent, get_settings_service

logger = logging.getLogger(__name__)


class SettingsScreen(ConfigurableModalScreen):
    """Modal screen for managing application settings."""

    BINDINGS = [
        ("escape", "cancel", "Cancel"),
        ("ctrl+s", "save", "Save"),
        ("enter", "save", "Save"),
    ]

    # Local reactive properties for form data
    spreadsheet_id: reactive[str] = reactive("")
    credentials_path: reactive[str] = reactive("")
    pay_day_type: reactive[str] = reactive("specific")
    pay_day: reactive[int] = reactive(31)
    theme: reactive[str] = reactive("nord")

    # Reactive properties for form state
    _form_widgets: reactive[dict] = reactive({})
    _validation_errors: reactive[dict] = reactive({})

    def on_mount(self) -> None:
        """Called when screen is mounted."""
        super().on_mount()
        if not hasattr(self, "_settings_service"):
            self._settings_service = get_settings_service()
        self.border_title = "Settings"
        self.border_subtitle = "Press Ctrl+S to save, Esc to cancel"
        # Load settings after compose has run
        self.call_after_refresh(self._on_widgets_ready)
        logger.debug("Settings modal mounted")

    def compose(self) -> ComposeResult:
        """Compose the settings modal layout."""
        with Container(classes="settings-modal"):
            yield Label("Application Settings", classes="modal-title")

            with Grid(classes="settings-grid"):
                # Spreadsheet configuration
                yield Label("Google Sheets Configuration:", classes="section-label")

                spreadsheet_input = Input(
                    placeholder="1ABc2DEf3GHi4JKl5MNop6QRs7TUv8WXy9Z",
                    classes="settings-input",
                    id="spreadsheet-id-input",
                )
                spreadsheet_input.border_title = "Spreadsheet ID"
                yield spreadsheet_input

                credentials_input = Input(
                    placeholder="/path/to/credentials.json",
                    classes="settings-input",
                    id="credentials-path-input",
                )
                credentials_input.border_title = "Credentials Path"
                yield credentials_input

                # Pay day configuration
                yield Label("Pay Day Configuration:", classes="section-label")

                pay_day_options = [
                    ("First day of the month", "first"),
                    ("Last day of the month", "last"),
                    ("Specific day of the month", "specific"),
                ]

                pay_day_type_select = Select(
                    pay_day_options,
                    allow_blank=False,
                    value="specific",
                    classes="settings-select",
                    id="pay-day-type-select",
                )
                pay_day_type_select.border_title = "Pay Day Type"
                yield pay_day_type_select

                pay_day_input = Input(
                    type="integer", classes="settings-input", id="pay-day-input"
                )
                pay_day_input.border_title = "Pay Day (1-31)"
                yield pay_day_input

                # Theme configuration
                yield Label("Appearance:", classes="section-label")

                theme_options = [
                    ("Nord (default)", "nord"),
                    ("Dark mode", "dark"),
                    ("Light mode", "light"),
                    ("Monokai", "monokai"),
                ]

                theme_select = Select(
                    theme_options,
                    allow_blank=False,
                    value="nord",
                    classes="settings-select",
                    id="theme-select",
                )
                theme_select.border_title = "Theme"
                yield theme_select

                # Build complete form widgets dictionary and set it once
                form_widgets = {
                    "spreadsheet_id": spreadsheet_input,
                    "credentials_path": credentials_input,
                    "pay_day_type": pay_day_type_select,
                    "pay_day": pay_day_input,
                    "theme": theme_select,
                }
                self._form_widgets = form_widgets

            # Action buttons
            with Horizontal(classes="button-bar"):
                yield Button(
                    "Save Settings",
                    variant="primary",
                    classes="action-button",
                    id="save-button",
                )
                yield Button(
                    "Cancel",
                    variant="default",
                    classes="action-button",
                    id="cancel-button",
                )

            # Validation messages
            with Container(classes="validation-container", id="validation-messages"):
                pass

    def _on_widgets_ready(self) -> None:
        """Called after compose has run to load settings."""
        self._load_current_settings()

    def _load_current_settings(self) -> None:
        """Load current settings into the form."""
        settings = self._settings_service.settings

        # Update reactive properties
        self.spreadsheet_id = settings.spreadsheet_id or ""
        self.credentials_path = settings.credentials_path
        self.pay_day_type = settings.pay_day_type
        self.pay_day = settings.pay_day
        self.theme = settings.theme

        # Update form widgets
        self._form_widgets["spreadsheet_id"].value = self.spreadsheet_id
        self._form_widgets["credentials_path"].value = self.credentials_path
        self._form_widgets["pay_day_type"].value = self.pay_day_type
        self._form_widgets["pay_day"].value = str(self.pay_day)
        self._form_widgets["theme"].value = self.theme

        # Update pay day input state based on type
        self._update_pay_day_input_state()

    def _update_pay_day_input_state(self) -> None:
        """Update pay day input based on the selected type."""
        pay_day_input = self._form_widgets["pay_day"]

        if self.pay_day_type == "first":
            pay_day_input.value = "1"
            pay_day_input.disabled = True
        elif self.pay_day_type == "last":
            pay_day_input.value = "31"
            pay_day_input.disabled = True
        else:  # specific
            pay_day_input.disabled = False
            if pay_day_input.value in ["1", "31"]:
                pay_day_input.value = str(self.pay_day)

    @on(Select.Changed, "#pay-day-type-select")
    def on_pay_day_type_changed(self, event: Select.Changed) -> None:
        """Handle pay day type selection changes."""
        self.pay_day_type = event.value
        self._update_pay_day_input_state()

    @on(Button.Pressed, "#save-button")
    def on_save_button_pressed(self) -> None:
        """Handle save button press."""
        self.action_save()

    @on(Button.Pressed, "#cancel-button")
    def on_cancel_button_pressed(self) -> None:
        """Handle cancel button press."""
        self.action_cancel()

    def _validate_form(self) -> bool:
        """Validate the form data and return True if valid."""
        validation_errors = {}

        # Validate spreadsheet ID
        spreadsheet_id = self._form_widgets["spreadsheet_id"].value.strip()
        if not spreadsheet_id:
            validation_errors["spreadsheet_id"] = "Spreadsheet ID is required"

        # Validate credentials path
        credentials_path = self._form_widgets["credentials_path"].value.strip()
        if not credentials_path:
            validation_errors["credentials_path"] = "Credentials path is required"
        else:
            try:
                path = Path(credentials_path).expanduser()
                if not path.exists():
                    validation_errors["credentials_path"] = (
                        "Credentials file does not exist"
                    )
                elif not path.is_file():
                    validation_errors["credentials_path"] = "Path is not a file"
            except Exception as e:
                validation_errors["credentials_path"] = f"Invalid path: {e}"

        # Validate pay day
        if self.pay_day_type == "specific":
            try:
                pay_day = int(self._form_widgets["pay_day"].value)
                if pay_day < 1 or pay_day > 31:
                    validation_errors["pay_day"] = "Pay day must be between 1 and 31"
            except ValueError:
                validation_errors["pay_day"] = "Pay day must be a valid number"

        # Update reactive property with new validation errors
        self._validation_errors = validation_errors
        self._display_validation_errors()
        return len(validation_errors) == 0

    def _display_validation_errors(self) -> None:
        """Display validation errors in the UI."""
        container = self.query_one("#validation-messages")
        container.remove_children()

        if self._validation_errors:
            for field, error in self._validation_errors.items():
                error_label = Label(f"❌ {error}", classes="validation-error")
                container.mount(error_label)
        else:
            # Clear any existing errors
            pass

    def get_save_data(self) -> dict:
        """Get the data to save from the form."""
        if not self._validate_form():
            raise ValueError("Form validation failed")

        # Collect form data
        data = {
            "spreadsheet_id": self._form_widgets["spreadsheet_id"].value.strip(),
            "credentials_path": self._form_widgets["credentials_path"].value.strip(),
            "pay_day_type": self._form_widgets["pay_day_type"].value,
            "theme": self._form_widgets["theme"].value,
        }

        # Handle pay day based on type
        if data["pay_day_type"] == "first":
            data["pay_day"] = 1
        elif data["pay_day_type"] == "last":
            data["pay_day"] = 31
        else:  # specific
            data["pay_day"] = int(self._form_widgets["pay_day"].value)

        return data

    def action_save(self) -> None:
        """Save settings action."""
        try:
            settings_data = self.get_save_data()

            # Update settings service
            self._settings_service.update(**settings_data)

            logger.info("Settings saved successfully")
            self.app.notify("Settings saved successfully", severity="information")

            # Call parent save with the data
            super().action_save()

        except ValueError as e:
            # Validation error - don't close modal
            logger.warning(f"Settings validation failed: {e}")
            self.app.notify("Please fix validation errors", severity="warning")
        except Exception as e:
            logger.error(f"Error saving settings: {e}")
            self.app.notify(f"Error saving settings: {e}", severity="error")

    def action_cancel(self) -> None:
        """Cancel settings action."""
        logger.debug("Settings modal cancelled")
        super().action_cancel()

    # Watchers for reactive properties
    def watch_spreadsheet_id(self, value: str) -> None:
        """React to spreadsheet ID changes."""
        if hasattr(self, "_form_widgets") and "spreadsheet_id" in self._form_widgets:
            self._form_widgets["spreadsheet_id"].value = value

    def watch_credentials_path(self, value: str) -> None:
        """React to credentials path changes."""
        if hasattr(self, "_form_widgets") and "credentials_path" in self._form_widgets:
            self._form_widgets["credentials_path"].value = value

    def watch_pay_day_type(self, value: str) -> None:
        """React to pay day type changes."""
        if hasattr(self, "_form_widgets") and "pay_day_type" in self._form_widgets:
            self._form_widgets["pay_day_type"].value = value
            self._update_pay_day_input_state()

    def watch_pay_day(self, value: int) -> None:
        """React to pay day changes."""
        if hasattr(self, "_form_widgets") and "pay_day" in self._form_widgets:
            self._form_widgets["pay_day"].value = str(value)

    def watch_theme(self, value: str) -> None:
        """React to theme changes."""
        if hasattr(self, "_form_widgets") and "theme" in self._form_widgets:
            self._form_widgets["theme"].value = value
