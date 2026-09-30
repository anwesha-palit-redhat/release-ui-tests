from playwright.async_api import Page

from framework.config.config import Config
from framework.locators.overview import OverViewPageLocators
from framework.ui_components.base_page import BasePage

# Flag to track if tour has been skipped across test sessions
# This avoids unnecessary wait time in test execution
# TODO: When parallel test execution is implemented, make this thread-safe by:
#       1. Import threading module
#       2. Add _tour_skipped_lock = threading.Lock()
#       3. Wrap the flag check and modification in: with _tour_skipped_lock:
#       4. Use double-check locking pattern for optimal performance
_tour_skipped = False


class OverViewPage(BasePage):
    def __init__(self, page: Page, config: Config) -> None:
        super().__init__(page, config)
        self.locators = OverViewPageLocators()

    async def verify_on_page(self) -> bool:
        """
        Verifies that the console has loaded after login.

        Prefers the cluster Overview (/dashboards + Overview header). For local bridge
        with auth disabled, accepts a loaded shell (nav visible) if /dashboards is slow
        or not the landing route.
        """
        global _tour_skipped

        try:
            overview_page_status = await self._verify_page(
                "dashboards", self.locators.OVERVIEW_HEADER, "Overview page"
            )
        except (AssertionError, Exception):
            # Local console often stays on "/" briefly; wait for nav shell instead
            if not await self.is_visible(self.locators.CONSOLE_READY, timeout=self.config.timeout_ms):
                raise AssertionError(
                    f"Console did not finish loading after login. Current URL: {self.page.url}. "
                    "For localhost: ensure oc login works (bridge token) and "
                    "console-plugin is serving on :9001 (yarn start)."
                ) from None
            overview_page_status = True

        if not _tour_skipped:
            if await self.is_visible(self.locators.SKIP_TOUR_BUTTON, timeout=5000):
                try:
                    await self.click_element(self.locators.SKIP_TOUR_BUTTON)
                except Exception:
                    pass
            _tour_skipped = True

        return overview_page_status
