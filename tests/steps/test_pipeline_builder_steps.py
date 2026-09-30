"""
Pipeline Builder Sanity Test Steps.

BDD step definitions for creating pipelines using the Pipeline Builder visual form.
"""

import asyncio
from pathlib import Path
from typing import Any, Dict, List

from pytest_bdd import parsers, scenarios, then, when

from framework.fixtures.async_bridge import run_async

# Register sanity + regression Pipeline Builder feature files
FEATURES_DIR = Path(__file__).parent.parent / "features"
scenarios(FEATURES_DIR / "pipeline_builder.feature")
scenarios(FEATURES_DIR / "pipeline_builder_regression.feature")


@when("the user clicks Create button on Pipelines page")
def click_create_on_pipelines_page(page: Dict[str, Any], playwright_event_loop: asyncio.AbstractEventLoop) -> None:
    """
    Click the Create button on the Pipelines list page to open the create dropdown menu.

    This step opens the dropdown menu that contains options for creating Pipeline,
    PipelineRun, and Repository resources. Waits for the menu to be visible after click.

    :param Dict[str, Any] page: Page object dictionary containing page components
    :param asyncio.AbstractEventLoop playwright_event_loop: Event loop for async execution
    :return: None: Raises AssertionError if Create button click fails
    """

    async def _step() -> None:
        create_clicked = await page["pipelines"].list.click_create_button()
        assert create_clicked, "Failed to click Create button on Pipelines list page"
        # Wait for Create dropdown menu to be visible
        await page["raw_page"].wait_for_selector('role=menuitem[name="Pipeline"]', state="visible", timeout=10000)

    run_async(playwright_event_loop, _step())


@when("the user clicks Pipeline menu item")
def click_pipeline_menu_item(page: Dict[str, Any], playwright_event_loop: asyncio.AbstractEventLoop) -> None:
    """
    Click the Pipeline menu item from the Create dropdown menu.

    This step selects the Pipeline option from the dropdown and navigates to the
    Pipeline Builder page. Waits for the Pipeline Builder header to be visible.

    :param Dict[str, Any] page: Page object dictionary containing page components
    :param asyncio.AbstractEventLoop playwright_event_loop: Event loop for async execution
    :return: None: Raises AssertionError if Pipeline menu item click fails
    """

    async def _step() -> None:
        pipeline_option_clicked = await page["pipelines"].list.click_create_pipeline_menu_item()
        assert pipeline_option_clicked, "Failed to click 'Pipeline' menu item from Create dropdown"
        # Wait for Pipeline Builder page header to be visible
        await page["raw_page"].wait_for_selector('h2:has-text("Pipeline builder")', state="visible", timeout=15000)

    run_async(playwright_event_loop, _step())


@then("the user should be on Pipeline Builder page")
def verify_on_pipeline_builder_page(page: Dict[str, Any], playwright_event_loop: asyncio.AbstractEventLoop) -> None:
    """
    Verify that the user has successfully navigated to the Pipeline Builder page.

    Checks for the presence of page-specific elements to confirm the page loaded correctly.

    :param Dict[str, Any] page: Page object dictionary containing page components
    :param asyncio.AbstractEventLoop playwright_event_loop: Event loop for async execution
    :return: None: Raises AssertionError if not on Pipeline Builder page
    """

    async def _step() -> None:
        on_builder_page = await page["pipelines"].builder.verify_on_page()
        assert on_builder_page, "Failed to navigate to Pipeline Builder page"

    run_async(playwright_event_loop, _step())


@when("the user clicks Create button on Pipeline Builder page")
def click_create_on_builder_page(
    page: Dict[str, Any], config: object, playwright_event_loop: asyncio.AbstractEventLoop
) -> None:
    """
    Click the Create button on the Pipeline Builder page to submit the pipeline definition.

    Waits for the Create button to become enabled (form validation completes) before
    clicking, then waits for network idle state to ensure navigation completes.

    :param Dict[str, Any] page: Page object dictionary containing page components
    :param object config: Config object for timeout values
    :param asyncio.AbstractEventLoop playwright_event_loop: Event loop for async execution
    :return: None: Raises AssertionError if Create button click fails
    """

    async def _step() -> None:
        # Wait for Create button to become enabled (form validation completes)
        create_button_locator = page["pipelines"].builder.locators.CREATE_BUTTON
        await page["raw_page"].wait_for_selector(f"{create_button_locator}:not([disabled])", timeout=15000)

        success = await page["pipelines"].builder.click_create()
        assert success, "Failed to click Create button"
        await page["raw_page"].wait_for_load_state("networkidle", timeout=config.timeout_ms)

    run_async(playwright_event_loop, _step())


@when(parsers.parse('the user fills pipeline name "{pipeline_name}" in builder view'))
def fill_pipeline_name_in_builder(
    page: Dict[str, Any], pipeline_name: str, playwright_event_loop: asyncio.AbstractEventLoop
) -> None:
    """
    Fill the pipeline name field in the Pipeline Builder visual form.

    This is a required field for creating a pipeline. The name must be unique within the namespace.

    :param Dict[str, Any] page: Page object dictionary containing page components
    :param str pipeline_name: Name for the pipeline (e.g., "my-build-pipeline")
    :param asyncio.AbstractEventLoop playwright_event_loop: Event loop for async execution
    :return: None: Raises AssertionError if pipeline name fill fails
    """

    async def _step() -> None:
        filled = await page["pipelines"].builder.builder_view.fill_pipeline_name(pipeline_name)
        assert filled, f"Failed to fill pipeline name '{pipeline_name}'"

    run_async(playwright_event_loop, _step())


@when(parsers.parse('the user adds task "{task_name}" in builder view'))
def add_task_in_builder(page: Dict[str, Any], task_name: str, playwright_event_loop: asyncio.AbstractEventLoop) -> None:
    """
    Add a task to the pipeline using the quick search dialog in the Pipeline Builder.

    Opens the quick search dialog, searches for the specified task name, and adds it
    to the pipeline canvas. Waits for the task node to appear on the canvas.

    :param Dict[str, Any] page: Page object dictionary containing page components
    :param str task_name: Name of the task to add (e.g., "git-clone", "buildah", "git-cli")
    :param asyncio.AbstractEventLoop playwright_event_loop: Event loop for async execution
    :return: None: Raises AssertionError if task addition fails
    """

    async def _step() -> None:
        added = await page["pipelines"].builder.builder_view.add_task_by_name(task_name)
        assert added, f"Failed to add task '{task_name}'"

    run_async(playwright_event_loop, _step())


@when(parsers.parse('the user adds pipeline parameter with name "{param_name}" and description "{param_description}"'))
def add_pipeline_parameter(
    page: Dict[str, Any],
    param_name: str,
    param_description: str,
    playwright_event_loop: asyncio.AbstractEventLoop,
) -> None:
    """
    Add a pipeline parameter to the pipeline definition.

    Pipeline parameters allow pipelines to accept input values at runtime.
    Waits for parameter input fields to be visible before configuring.

    :param Dict[str, Any] page: Page object dictionary containing page components
    :param str param_name: Name of the parameter (e.g., "image-name", "revision")
    :param str param_description: Description of the parameter's purpose
    :param asyncio.AbstractEventLoop playwright_event_loop: Event loop for async execution
    :return: None: Raises AssertionError if parameter configuration fails
    """

    async def _step() -> None:
        await page["pipelines"].builder.builder_view.close_task_sidebar()
        await page["pipelines"].builder.builder_view.click_add_parameter()
        param_index = await _next_param_index(page)
        success = await page["pipelines"].builder.builder_view.configure_pipeline_parameter(
            param_index=param_index, name=param_name, description=param_description
        )
        assert success, f"Failed to configure pipeline parameter '{param_name}'"

    run_async(playwright_event_loop, _step())


@when(
    parsers.parse(
        'the user adds pipeline parameter with name "{param_name}" description "{param_description}" and default "{default_value}"'
    )
)
def add_pipeline_parameter_with_default(
    page: Dict[str, Any],
    param_name: str,
    param_description: str,
    default_value: str,
    playwright_event_loop: asyncio.AbstractEventLoop,
) -> None:
    """Add a pipeline parameter including a default value (optional at start time)."""

    async def _step() -> None:
        await page["pipelines"].builder.builder_view.close_task_sidebar()
        await page["pipelines"].builder.builder_view.click_add_parameter()
        param_index = await _next_param_index(page)
        success = await page["pipelines"].builder.builder_view.configure_pipeline_parameter(
            param_index=param_index,
            name=param_name,
            description=param_description,
            default_value=default_value,
        )
        assert success, f"Failed to configure pipeline parameter '{param_name}'"

    run_async(playwright_event_loop, _step())


async def _next_param_index(page: Dict[str, Any]) -> int:
    """Return the index of the newly added (last) parameter row."""
    locator = page["raw_page"].locator('input[id^="form-input-formData-params-"][id$="-name-field"]')
    count = await locator.count()
    return max(count - 1, 0)


@when(parsers.parse('the user adds pipeline workspace with name "{workspace_name}"'))
def add_pipeline_workspace(
    page: Dict[str, Any], workspace_name: str, playwright_event_loop: asyncio.AbstractEventLoop
) -> None:
    """
    Add a pipeline workspace to the pipeline definition.

    Workspaces provide shared storage volumes that can be passed between tasks.
    Waits for workspace input fields to be visible before configuring.

    :param Dict[str, Any] page: Page object dictionary containing page components
    :param str workspace_name: Name of the workspace (e.g., "source", "output", "cache")
    :param asyncio.AbstractEventLoop playwright_event_loop: Event loop for async execution
    :return: None: Raises AssertionError if workspace configuration fails
    """

    async def _step() -> None:
        await page["pipelines"].builder.builder_view.close_task_sidebar()
        await page["pipelines"].builder.builder_view.click_add_workspace()

        success = await page["pipelines"].builder.builder_view.configure_pipeline_workspace(
            workspace_index=0, name=workspace_name
        )
        assert success, f"Failed to configure pipeline workspace '{workspace_name}'"

    run_async(playwright_event_loop, _step())


@when(parsers.parse('the user clicks on task "{task_name}" to configure'))
def click_task_to_configure(
    page: Dict[str, Any], task_name: str, playwright_event_loop: asyncio.AbstractEventLoop
) -> None:
    """
    Click on a task node in the pipeline canvas to open its configuration sidebar.

    Opens the task configuration panel where task parameters, workspaces, and display
    name can be configured. Waits for the configuration sidebar to be visible.

    :param Dict[str, Any] page: Page object dictionary containing page components
    :param str task_name: Name of the task to configure (e.g., "git-clone", "git-cli")
    :param asyncio.AbstractEventLoop playwright_event_loop: Event loop for async execution
    :return: None: Raises AssertionError if task click fails
    """

    async def _step() -> None:
        success = await page["pipelines"].builder.builder_view.click_task_node(task_name)
        assert success, f"Failed to click on task '{task_name}'"

    run_async(playwright_event_loop, _step())


@when(parsers.parse("the user configures {task_name} task:"))
def configure_task_with_params(
    page: Dict[str, Any], task_name: str, datatable: List[List[str]], playwright_event_loop: asyncio.AbstractEventLoop
) -> None:
    """
    Configure task parameters and workspaces using data from a Gherkin data table.

    Supports configuring task display name, parameters, and workspace mappings.
    Common fields: displayName (task instance name), source/output (workspace names),
    url (for git-clone tasks), script (for git-cli tasks).

    Waits for network idle state after configuration to ensure form updates complete.

    :param Dict[str, Any] page: Page object dictionary containing page components
    :param str task_name: Name of the task being configured (e.g., "git-clone", "git-cli")
    :param List[List[str]] datatable: Gherkin data table with field and value columns
    :param asyncio.AbstractEventLoop playwright_event_loop: Event loop for async execution
    :return: None: Raises AssertionError if task configuration fails
    """

    async def _step() -> None:
        # Parse datatable: skip header row, build config dict
        # Validate table structure before parsing
        config = {}
        for i, row in enumerate(datatable):
            if i == 0:
                continue  # Skip header row
            if len(row) < 2:
                raise ValueError(
                    f"Data table row {i} has {len(row)} columns, expected at least 2 (field, value). Row content: {row}"
                )
            config[row[0]] = row[1]

        # Fill task name (required field with id="task-name")
        if "displayName" in config:
            await page["pipelines"].builder.builder_view.fill_task_name(config["displayName"])

        # Configure source workspace (for git-cli)
        if "source" in config:
            await page["pipelines"].builder.builder_view.select_task_workspace(
                task_index=0, workspace_index=0, workspace_name=config["source"], workspace_type="source"
            )

        # Configure script parameter (for git-cli - parameter 11)
        if "script" in config:
            await page["pipelines"].builder.builder_view.configure_task_param(
                task_index=0, param_index=11, value=config["script"]
            )

        # Configure url if provided (for git-clone tasks)
        if "url" in config:
            await page["pipelines"].builder.builder_view.configure_task_param(
                task_index=0, param_index=0, value=config["url"]
            )

        # Configure output workspace if provided
        if "output" in config:
            await page["pipelines"].builder.builder_view.select_task_workspace(
                task_index=0, workspace_index=0, workspace_name=config["output"], workspace_type="output"
            )

        # Wait for form to update after configuration changes
        await page["raw_page"].wait_for_load_state("networkidle", timeout=10000)

    run_async(playwright_event_loop, _step())


@then("the user should be on pipeline details page")
def verify_on_pipeline_details_page(page: Dict[str, Any], playwright_event_loop: asyncio.AbstractEventLoop) -> None:
    """
    Verify that the user has successfully navigated to the pipeline details page.

    Confirms pipeline creation succeeded by checking for the presence of page-specific
    elements on the pipeline details page.

    :param Dict[str, Any] page: Page object dictionary containing page components
    :param asyncio.AbstractEventLoop playwright_event_loop: Event loop for async execution
    :return: None: Raises AssertionError if not on pipeline details page
    """

    async def _step() -> None:
        on_details_page = await page["pipelines"].pipeline.details.verify_on_page()
        assert on_details_page, "Failed to navigate to pipeline details page"

    run_async(playwright_event_loop, _step())


@then(parsers.parse('the pipeline details page should display the pipeline name as "{expected_name}"'))
def verify_pipeline_name_on_details(
    page: Dict[str, Any], expected_name: str, playwright_event_loop: asyncio.AbstractEventLoop
) -> None:
    """
    Verify the pipeline name displayed on the details page matches the expected value.

    Retrieves the pipeline name from the page header and compares it with the expected
    name to confirm the correct pipeline was created.

    :param Dict[str, Any] page: Page object dictionary containing page components
    :param str expected_name: Expected pipeline name (e.g., "builder-test-pipeline")
    :param asyncio.AbstractEventLoop playwright_event_loop: Event loop for async execution
    :return: None: Raises AssertionError if pipeline name doesn't match
    """

    async def _step() -> None:
        actual_name = await page["pipelines"].pipeline.details.get_pipeline_name()
        assert actual_name == expected_name, (
            f"Pipeline name mismatch. Expected: '{expected_name}', Got: '{actual_name}'"
        )

    run_async(playwright_event_loop, _step())


@when(parsers.parse('the user adds task "{task_name}" after task "{existing_task}" in builder view'))
def add_task_after_existing(
    page: Dict[str, Any],
    task_name: str,
    existing_task: str,
    playwright_event_loop: asyncio.AbstractEventLoop,
) -> None:
    """Add a sequential task after an existing builder node."""

    async def _step() -> None:
        await page["pipelines"].builder.builder_view.close_task_sidebar()
        added = await page["pipelines"].builder.builder_view.add_task_after(existing_task, task_name)
        assert added, f"Failed to add task '{task_name}' after '{existing_task}'"

    run_async(playwright_event_loop, _step())


@when("the user switches to YAML view")
def switch_to_yaml_view(page: Dict[str, Any], playwright_event_loop: asyncio.AbstractEventLoop) -> None:
    """Switch Pipeline Builder to YAML view."""

    async def _step() -> None:
        await page["pipelines"].builder.builder_view.close_task_sidebar()
        success = await page["pipelines"].builder.switch_to_yaml_view()
        assert success, "Failed to switch to YAML view"

    run_async(playwright_event_loop, _step())


@when("the user switches to Form view")
def switch_to_form_view(page: Dict[str, Any], playwright_event_loop: asyncio.AbstractEventLoop) -> None:
    """Switch Pipeline Builder back to Form view."""

    async def _step() -> None:
        success = await page["pipelines"].builder.switch_to_builder_view()
        assert success, "Failed to switch to Form view"
        await page["raw_page"].wait_for_selector(
            page["pipelines"].builder.builder_view.locators.PIPELINE_NAME_INPUT,
            state="visible",
            timeout=15000,
        )

    run_async(playwright_event_loop, _step())


@when(parsers.parse('the user updates parameter "{param_name}" default to "{new_default}" in YAML view'))
def update_param_default_in_yaml(
    page: Dict[str, Any],
    param_name: str,
    new_default: str,
    playwright_event_loop: asyncio.AbstractEventLoop,
) -> None:
    """Update a parameter default value via the YAML editor."""

    async def _step() -> None:
        success = await page["pipelines"].builder.yaml_view.update_param_default(param_name, new_default)
        assert success, f"Failed to update parameter '{param_name}' default in YAML"

    run_async(playwright_event_loop, _step())


@when("the user toggles show required task params only")
def toggle_show_required_params(page: Dict[str, Any], playwright_event_loop: asyncio.AbstractEventLoop) -> None:
    """Enable 'Show required task params only'."""

    async def _step() -> None:
        success = await page["pipelines"].builder.builder_view.set_show_required_task_params_only(True)
        assert success, "Failed to enable show required task params only"

    run_async(playwright_event_loop, _step())


@when("the user toggles show all task params")
def toggle_show_all_params(page: Dict[str, Any], playwright_event_loop: asyncio.AbstractEventLoop) -> None:
    """Disable 'Show required task params only' to show optional params again."""

    async def _step() -> None:
        success = await page["pipelines"].builder.builder_view.set_show_required_task_params_only(False)
        assert success, "Failed to show all task params"

    run_async(playwright_event_loop, _step())


@when("the user toggles workspace optional view")
def toggle_workspace_optional(page: Dict[str, Any], playwright_event_loop: asyncio.AbstractEventLoop) -> None:
    """Mark the workspace as optional."""

    async def _step() -> None:
        success = await page["pipelines"].builder.builder_view.set_workspace_optional(True)
        assert success, "Failed to set workspace as optional"

    run_async(playwright_event_loop, _step())


@when("the user toggles workspace required view")
def toggle_workspace_required(page: Dict[str, Any], playwright_event_loop: asyncio.AbstractEventLoop) -> None:
    """Mark the workspace as required (uncheck optional)."""

    async def _step() -> None:
        success = await page["pipelines"].builder.builder_view.set_workspace_optional(False)
        assert success, "Failed to set workspace as required"

    run_async(playwright_event_loop, _step())


@when(
    parsers.parse(
        'the user maps task "{task_name}" workspace "{workspace_type}" to pipeline workspace "{pipeline_workspace}"'
    )
)
def map_task_workspace(
    page: Dict[str, Any],
    task_name: str,
    workspace_type: str,
    pipeline_workspace: str,
    playwright_event_loop: asyncio.AbstractEventLoop,
) -> None:
    """Open a task sidebar and map a task workspace to a pipeline workspace."""

    async def _step() -> None:
        clicked = await page["pipelines"].builder.builder_view.click_task_node(task_name)
        assert clicked, f"Failed to open task '{task_name}'"
        selected = await page["pipelines"].builder.builder_view.select_task_workspace(
            task_index=0,
            workspace_index=0,
            workspace_name=pipeline_workspace,
            workspace_type=workspace_type,
        )
        assert selected, (
            f"Failed to map task '{task_name}' workspace '{workspace_type}' to '{pipeline_workspace}'"
        )
        await page["pipelines"].builder.builder_view.close_task_sidebar()

    run_async(playwright_event_loop, _step())


@when("the user starts the pipeline")
def start_pipeline_from_details(page: Dict[str, Any], playwright_event_loop: asyncio.AbstractEventLoop) -> None:
    """Open Start Pipeline modal from pipeline details Actions menu."""

    async def _step() -> None:
        opened = await page["pipelines"].pipeline.details.open_start_pipeline_modal()
        assert opened, "Failed to open Start Pipeline modal"

    run_async(playwright_event_loop, _step())


@when(parsers.parse('the user selects Empty Directory for workspace "{workspace_name}" in Start Pipeline modal'))
def select_empty_directory_workspace(
    page: Dict[str, Any], workspace_name: str, playwright_event_loop: asyncio.AbstractEventLoop
) -> None:
    """Choose Empty Directory volume type for a workspace in the Start modal."""

    async def _step() -> None:
        selected = await page["pipelines"].pipeline.details.start_modal.select_workspace_empty_directory(
            workspace_name
        )
        assert selected, f"Failed to select Empty Directory for workspace '{workspace_name}'"

    run_async(playwright_event_loop, _step())


@when("the user confirms Start Pipeline")
def confirm_start_pipeline(page: Dict[str, Any], playwright_event_loop: asyncio.AbstractEventLoop) -> None:
    """Click Start in the Start Pipeline modal."""

    async def _step() -> None:
        started = await page["pipelines"].pipeline.details.start_modal.click_start()
        assert started, "Failed to confirm Start Pipeline"

    run_async(playwright_event_loop, _step())


@then("the user should be redirected to a PipelineRun details page")
def verify_redirected_to_pipelinerun_details(
    page: Dict[str, Any], playwright_event_loop: asyncio.AbstractEventLoop
) -> None:
    """Verify navigation landed on a PipelineRun details page after Start."""

    async def _step() -> None:
        await page["raw_page"].wait_for_load_state("networkidle")
        on_page = await page["pipelines"].pipelinerun.details.verify_on_page()
        assert on_page, "Failed to navigate to PipelineRun details page after starting pipeline"

    run_async(playwright_event_loop, _step())
