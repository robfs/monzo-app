import asyncio
import pytest

from textual.app import App, ComposeResult
from widgets import ReactiveLabel


@pytest.fixture
def test_app() -> App:
    class TestApp(App):
        BINDINGS = [("r", "refresh", "Refresh")]

        def compose(self) -> ComposeResult:
            yield ReactiveLabel(id="test-label")

        async def action_refresh(self):
            """Refresh the dashboard screen."""
            label = self.query_one(ReactiveLabel)
            label.set_updating()
            await asyncio.sleep(5)
            label.stop_updating()

    app = TestApp()

    return app
