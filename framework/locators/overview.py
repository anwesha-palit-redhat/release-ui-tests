"""Locators for root-level pages (Overview, Repositories)."""


class OverViewPageLocators:
    """Locators for the Overview Page"""

    OVERVIEW_HEADER = 'h1:has-text("Overview")'
    SKIP_TOUR_BUTTON = 'button:has-text("Skip tour")'
    # Local bridge / auth-disabled console may land before /dashboards is in the URL.
    # Prefer the unique sidebar; do not include [data-test="nav"] (matches every nav item).
    CONSOLE_READY = '[data-test="navigation-page-sidebar"]'


class RepositoriesPageLocators:
    """Locators for the Repositories Page"""

    # Repository-specific column
    REPOSITORY_COLUMN_HEADER = 'role=columnheader[name="Repository"]'
