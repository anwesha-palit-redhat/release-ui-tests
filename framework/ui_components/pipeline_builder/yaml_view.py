from playwright.async_api import Page

from framework.config.config import Config
from framework.locators.pipelines import YamlViewLocators
from framework.ui_components.base_page import BasePage
from framework.ui_components.commons.monaco_editor import MonacoEditor


class YamlView(BasePage):
    """
    View object for Pipeline Builder's YAML editor interface.
    Handles YAML editor-specific UI elements and interactions.

    Uses MonacoEditor component for reliable editor interactions following
    the Composition pattern (composing MonacoEditor rather than duplicating logic).
    """

    def __init__(self, page: Page, config: Config) -> None:
        super().__init__(page, config)
        self.locators = YamlViewLocators()
        # Compose MonacoEditor component for editor interactions
        # Pipeline Builder may not set data-test="code-editor" immediately after view switch,
        # so we use the .monaco-editor selector as a more reliable wait target
        self.monaco_editor = MonacoEditor(page, config, custom_selector=self.locators.YAML_EDITOR)

    async def click_sidebar_close(self) -> bool:
        """
        Clicks the Close button to close the sidebar panel.
        :return: bool: True if click succeeds.
        """
        return await self.click_element(self.locators.SIDEBAR_CLOSE_BUTTON)

    async def click_samples_tab(self) -> bool:
        """
        Clicks the 'Samples' tab in the sidebar to view sample pipelines.
        :return: bool: True if click succeeds.
        """
        return await self.click_element(self.locators.SAMPLES_TAB)

    async def click_snippets_tab(self) -> bool:
        """
        Clicks the 'Snippets' tab in the sidebar to view YAML snippets.
        :return: bool: True if click succeeds.
        """
        return await self.click_element(self.locators.SNIPPETS_TAB)

    async def click_sample_try_it(self, index: int = 0) -> bool:
        """
        Clicks the 'Try it' button for a specific sample pipeline.
        :param int index: The zero-based index of the sample (0 for first, 1 for second, etc.).
        :return: bool: True if click succeeds.
        """
        locator = f"{self.locators.SAMPLE_TRY_IT_BUTTON} >> nth={index}"
        return await self.click_element(locator)

    async def click_sample_download_yaml(self, index: int = 0) -> bool:
        """
        Clicks the 'Download YAML' button for a specific sample pipeline.
        :param int index: The zero-based index of the sample (0 for first, 1 for second, etc.).
        :return: bool: True if click succeeds.
        """
        locator = f"{self.locators.SAMPLE_DOWNLOAD_YAML_BUTTON} >> nth={index}"
        return await self.click_element(locator)

    async def get_yaml_content(self) -> str:
        """Return current YAML editor content."""
        return await self.monaco_editor.get_content()

    async def set_yaml_content(self, content: str) -> bool:
        """Replace YAML editor content."""
        return await self.monaco_editor.set_content(content)

    async def update_param_default(self, param_name: str, new_default: str) -> bool:
        """
        Update a pipeline parameter's default value in YAML.
        Matches `- name: <param_name>` then rewrites the following `default:` line.
        """
        content = await self.get_yaml_content()
        if not content:
            return False

        lines = content.splitlines()
        updated_lines: list[str] = []
        in_target_param = False
        replaced = False

        for line in lines:
            stripped = line.strip()
            if stripped.startswith("- name:") and param_name in stripped:
                in_target_param = True
                updated_lines.append(line)
                continue

            if in_target_param and stripped.startswith("- name:"):
                in_target_param = False

            if in_target_param and stripped.startswith("default:"):
                indent = line[: len(line) - len(line.lstrip())]
                updated_lines.append(f'{indent}default: "{new_default}"')
                replaced = True
                in_target_param = False
                continue

            updated_lines.append(line)

        if not replaced:
            # Append default under the named param if missing
            rebuilt: list[str] = []
            for line in updated_lines:
                rebuilt.append(line)
                if line.strip() == f"- name: {param_name}" or line.strip() == f'- name: "{param_name}"':
                    indent = "  " if not line.startswith(" ") else line[: len(line) - len(line.lstrip())] + "  "
                    rebuilt.append(f'{indent}default: "{new_default}"')
                    replaced = True
            updated_lines = rebuilt

        if not replaced:
            return False

        return await self.set_yaml_content("\n".join(updated_lines) + "\n")
