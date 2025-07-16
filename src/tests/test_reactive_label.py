import pytest

from textual.app import App
from widgets import ReactiveLabel


@pytest.mark.asyncio
async def test_label_updating(test_app: App):
    """Test that the label updates correctly."""
    async with test_app.run_test() as pilot:
        await pilot.press("r")
        await pilot.pause(1)
        label = pilot.app.query_one(ReactiveLabel)
        assert label.has_class("loading-label")
        # pilot.pause(5)
        # assert not label.has_class("loading-label")
