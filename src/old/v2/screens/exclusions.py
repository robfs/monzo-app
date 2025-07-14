"""Exclusions modal screen for category management."""

import logging
from textual.app import ComposeResult
from textual.containers import Container, Vertical, Horizontal
from textual.widgets import SelectionList, Button, Label
from textual.reactive import reactive
from textual import on

from screens.base import ConfigurableModalScreen
from core import AppEvent, get_settings_service, get_data_service

logger = logging.getLogger(__name__)


class ExclusionsScreen(ConfigurableModalScreen):
    """Modal screen for managing category exclusions."""

    BINDINGS = [
        ("escape", "cancel", "Cancel"),
        ("ctrl+s", "save", "Apply"),
        ("enter", "save", "Apply"),
        ("space", "toggle_selection", "Toggle"),
    ]

    # Reactive properties
    available_categories: reactive[list[str]] = reactive([])
    selected_exclusions: reactive[list[str]] = reactive([])

    def on_mount(self) -> None:
        """Called when screen is mounted."""
        super().on_mount()
        if not hasattr(self, "_settings_service"):
            self._settings_service = get_settings_service()
        if not hasattr(self, "_data_service"):
            self._data_service = get_data_service()
        if not hasattr(self, "_selection_list"):
            self._selection_list = None

    def compose(self) -> ComposeResult:
        """Compose the exclusions modal layout."""
        with Container(classes="exclusions-modal"):
            yield Label("Category Exclusions", classes="modal-title")

            yield Label(
                "Select categories to exclude from spending analysis:",
                classes="modal-description",
            )

            with Container(classes="selection-container"):
                self._selection_list = SelectionList(
                    id="category-selection-list", classes="category-list"
                )
                yield self._selection_list

            # Status information
            with Horizontal(classes="status-bar"):
                yield Label("Categories available:", classes="status-label")
                yield Label("0", classes="status-count", id="available-count")
                yield Label("Selected for exclusion:", classes="status-label")
                yield Label("0", classes="status-count", id="selected-count")

            # Action buttons
            with Horizontal(classes="button-bar"):
                yield Button(
                    "Select All",
                    variant="default",
                    id="select-all-button",
                    classes="modal-button",
                )
                yield Button(
                    "Clear All",
                    variant="default",
                    id="clear-all-button",
                    classes="modal-button",
                )
                yield Button(
                    "Cancel",
                    variant="default",
                    id="cancel-button",
                    classes="modal-button",
                )
                yield Button(
                    "Apply Exclusions",
                    variant="primary",
                    id="save-button",
                    classes="modal-button",
                )

    def on_mount(self) -> None:
        """Called when the exclusions modal is mounted."""
        super().on_mount()
        self.border_title = "Category Exclusions"
        self.border_subtitle = "Press Space to toggle, Ctrl+S to apply, Esc to cancel"
        self._load_categories()
        logger.debug("Exclusions modal mounted")

    def _load_categories(self) -> None:
        """Load available categories and current exclusions."""
        try:
            # Get available categories from data service
            categories = self._data_service.get_categories()
            self.available_categories = sorted(categories)

            # Get current exclusions from settings
            current_exclusions = self._settings_service.settings.exclusions
            self.selected_exclusions = current_exclusions.copy()

            # Populate the selection list
            self._populate_selection_list()

            logger.debug(
                f"Loaded {len(categories)} categories, {len(current_exclusions)} excluded"
            )

        except Exception as e:
            logger.error(f"Error loading categories: {e}")
            self.app.notify(f"Error loading categories: {e}", severity="error")

    def _populate_selection_list(self) -> None:
        """Populate the selection list with categories."""
        if not self._selection_list:
            return

        # Clear existing options
        self._selection_list.clear_options()

        # Add categories as options
        for category in self.available_categories:
            self._selection_list.add_option(category, category)

        # Set initial selections
        for category in self.selected_exclusions:
            if category in self.available_categories:
                try:
                    index = self.available_categories.index(category)
                    self._selection_list.select(index)
                except (ValueError, IndexError):
                    logger.warning(f"Could not select category: {category}")

        self._update_status_counts()

    def _update_status_counts(self) -> None:
        """Update the status count displays."""
        try:
            available_count = self.query_one("#available-count")
            selected_count = self.query_one("#selected-count")

            available_count.update(str(len(self.available_categories)))

            if self._selection_list:
                selected_count.update(str(len(self._selection_list.selected)))
        except Exception as e:
            logger.error(f"Error updating status counts: {e}")

    @on(SelectionList.SelectedChanged, "#category-selection-list")
    def on_selection_changed(self, event: SelectionList.SelectedChanged) -> None:
        """Handle selection changes in the category list."""
        self._update_status_counts()

        # Update selected exclusions based on current selection
        if self._selection_list:
            selected_indices = self._selection_list.selected
            self.selected_exclusions = [
                self.available_categories[i]
                for i in selected_indices
                if i < len(self.available_categories)
            ]

        logger.debug(
            f"Selection changed: {len(self.selected_exclusions)} categories selected"
        )

    @on(Button.Pressed, "#select-all-button")
    def on_select_all_pressed(self) -> None:
        """Handle select all button press."""
        if self._selection_list:
            # Select all categories
            for i in range(len(self.available_categories)):
                self._selection_list.select(i)

            self.app.notify("All categories selected for exclusion", timeout=2)

    @on(Button.Pressed, "#clear-all-button")
    def on_clear_all_pressed(self) -> None:
        """Handle clear all button press."""
        if self._selection_list:
            # Deselect all categories
            self._selection_list.deselect_all()

            self.app.notify("All categories cleared", timeout=2)

    @on(Button.Pressed, "#save-button")
    def on_save_button_pressed(self) -> None:
        """Handle save button press."""
        self.action_save()

    @on(Button.Pressed, "#cancel-button")
    def on_cancel_button_pressed(self) -> None:
        """Handle cancel button press."""
        self.action_cancel()

    def action_toggle_selection(self) -> None:
        """Toggle selection of the currently focused item."""
        if self._selection_list and self._selection_list.has_focus:
            self._selection_list.toggle(self._selection_list.cursor)

    def get_save_data(self) -> dict:
        """Get the exclusions data to save."""
        if not self._selection_list:
            return {"exclusions": []}

        # Get currently selected categories
        selected_indices = self._selection_list.selected
        selected_categories = [
            self.available_categories[i]
            for i in selected_indices
            if i < len(self.available_categories)
        ]

        return {"exclusions": selected_categories}

    def action_save(self) -> None:
        """Save exclusions action."""
        try:
            data = self.get_save_data()
            exclusions = data["exclusions"]

            # Update settings service
            self._settings_service.set_exclusions(exclusions)

            excluded_count = len(exclusions)
            total_count = len(self.available_categories)

            logger.info(
                f"Exclusions saved: {excluded_count}/{total_count} categories excluded"
            )
            self.app.notify(
                f"Exclusions applied: {excluded_count} categories excluded",
                severity="information",
            )

            # Call parent save with the data
            super().action_save()

        except Exception as e:
            logger.error(f"Error saving exclusions: {e}")
            self.app.notify(f"Error saving exclusions: {e}", severity="error")

    def action_cancel(self) -> None:
        """Cancel exclusions action."""
        logger.debug("Exclusions modal cancelled")
        super().action_cancel()

    # Reactive property watchers
    def watch_available_categories(self, categories: list[str]) -> None:
        """React to available categories changes."""
        if hasattr(self, "_selection_list") and self._selection_list:
            self._populate_selection_list()

    def watch_selected_exclusions(self, exclusions: list[str]) -> None:
        """React to selected exclusions changes."""
        logger.debug(f"Selected exclusions updated: {exclusions}")

    def on_data_updated(self, event: AppEvent) -> None:
        """Handle data update events."""
        logger.debug("ExclusionsScreen: Data updated, refreshing categories")
        self._load_categories()
