import logging

from selenium import webdriver

from tests.app.drivers.driver_factory import get_driver
from tests.app.factories.page_factory import get_login_page
from tests.app.pages.base.base_page import BasePage
from tests.app.utils import browserstack as browserstack_utils
from tests.web.pages.login_page import WebLoginPage


def create_function_scoped_driver(
    *,
    logger: logging.Logger,
    platform: str,
    env: str,
    test_name: str,
    login_required: bool,
):
    """Spin up a function-scoped driver and optionally perform login."""
    logger.info("Starting test '%s' on %s via %s", test_name, platform.upper(), env.upper())
    driver = get_driver(platform=platform, test_name=test_name, env=env)
    BasePage.init_base(driver, logger, platform)

    if login_required:
        login_page = get_login_page(platform=platform, driver=driver, logger=logger)
        login_page.login_user()

    return driver


def create_function_scoped_web_driver(
    *,
    logger: logging.Logger,
    platform: str,
    env: str,
    test_name: str,
    login_required: bool,
):
    """Spin up a function-scoped driver and optionally perform login."""
    logger.info("Starting test '%s' on %s via %s", test_name, platform.upper(), env.upper())
    options = webdriver.ChromeOptions()
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1440,900")

    # Create driver
    driver = webdriver.Chrome(options=options)

    # Initialize base page (your framework setup)
    BasePage.init_base(driver, logger, platform="web")

    if login_required:
        login_page = WebLoginPage(driver=driver, logger=logger)
        login_page.login_user(env)

    return driver


def create_web_session_driver(logger: logging.Logger, env: str):
    """
    Create a session-scoped Chrome WebDriver with custom capabilities
    and return a logged-in driver.
    """
    logger.info("Starting web session driver for environment: %s", env)

    # Custom Chrome options
    options = webdriver.ChromeOptions()
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1440,900")

    # Create driver
    driver = webdriver.Chrome(options=options)

    # Initialize base page (your framework setup)
    BasePage.init_base(driver, logger, platform="web")

    # Perform login
    login_page = WebLoginPage(driver=driver, logger=logger)
    login_page.login_user(env)

    return driver


def finalize_function_scoped_driver(
    *,
    driver,
    request,
    env: str,
    logger: logging.Logger,
    test_name: str,
):
    """Handle teardown for a function-scoped driver."""
    if driver is None:
        return

    browserstack_utils.finalize_function_scope_session(
        driver=driver,
        request=request,
        env=env,
        logger=logger,
        test_name=test_name,
    )

    try:
        driver.quit()
    except Exception as exc:  # noqa: BLE001 - best effort
        logger.warning("Failed to quit driver: %s", exc)
