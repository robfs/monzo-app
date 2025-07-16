import pytest

from app import MonzoApp


@pytest.mark.asyncio
async def test_app_initiation():
    app = MonzoApp()
    async with app.run_test():
        assert app.screen.__class__.__name__ == "DashboardScreen"


@pytest.mark.asyncio
async def test_keys():
    """Test pressing keys has the desired result."""
    app = MonzoApp()

    async with app.run_test() as pilot:
        await pilot.press("O")
        assert app.screen.__class__.__name__ == "OtherScreen"

        await pilot.press("D")
        assert app.screen.__class__.__name__ == "DashboardScreen"


#         # Test pressing the G key
#         await pilot.press("g")
#         assert app.screen.styles.background == Color.parse("green")

#         # Test pressing the B key
#         await pilot.press("b")
#         assert app.screen.styles.background == Color.parse("blue")

#         # Test pressing the X key
#         await pilot.press("x")
#         # No binding (so no change to the color)
#         assert app.screen.styles.background == Color.parse("blue")


# async def test_buttons():
#     """Test pressing keys has the desired result."""
#     app = RGBApp()
#     async with app.run_test() as pilot:
#         # Test clicking the "red" button
#         await pilot.click("#red")
#         assert app.screen.styles.background == Color.parse("red")

#         # Test clicking the "green" button
#         await pilot.click("#green")
#         assert app.screen.styles.background == Color.parse("green")

#         # Test clicking the "blue" button
#         await pilot.click("#blue")
#         assert app.screen.styles.background == Color.parse("blue")
