from playwright.async_api import Page

from framework.config.config import Config
from framework.locators.pipelines import StartPipelineModalLocators
from framework.ui_components.base_page import BasePage


class StartPipelineModal(BasePage):
    """Page object for the Start Pipeline modal."""

    def __init__(self, page: Page, config: Config) -> None:
        super().__init__(page, config)
        self.locators = StartPipelineModalLocators()

    async def verify_open(self) -> bool:
        """Wait for the Start Pipeline modal title to be visible."""
        await self.page.wait_for_selector(self.locators.MODAL_TITLE, state="visible", timeout=15000)
        return await self.is_visible(self.locators.MODAL_TITLE)

    async def select_workspace_empty_directory(self, workspace_name: str) -> bool:
        """
        Select Empty Directory for the given pipeline workspace in the Start modal.
        :param str workspace_name: Workspace name as shown in the modal.
        """
        dropdown = self.locators.WORKSPACE_TYPE_DROPDOWN_TEMPLATE.format(workspace_name=workspace_name)
        # Fallback to section + dropdown-button when dataTest is not yet shipped in the plugin
        section = self.locators.WORKSPACE_SECTION_TEMPLATE.format(workspace_name=workspace_name)

        try:
            await self.page.wait_for_selector(dropdown, state="visible", timeout=5000)
            await self.click_element(dropdown)
        except Exception:
            await self.page.wait_for_selector(section, state="visible", timeout=10000)
            await self.page.locator(f'{section} [data-test-id="dropdown-button"]').click()

        # Prefer selecting by menu item key/id used by dropdown.jsx
        empty_dir = self.page.locator(self.locators.EMPTY_DIRECTORY_OPTION).first
        await empty_dir.wait_for(state="visible", timeout=10000)
        await empty_dir.click()
        return True

    async def click_start(self) -> bool:
        """Click the Start (confirm) button and wait for the modal to close."""
        success = await self.click_element(self.locators.START_BUTTON)
        if success:
            await self.page.wait_for_selector(self.locators.MODAL_TITLE, state="hidden", timeout=30000)
        return success
