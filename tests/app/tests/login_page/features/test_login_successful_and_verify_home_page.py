import os

import pytest
import allure

from tests.app.factories.page_factory import get_login_page
from tests.app.pages.base.home_page import HomePage
from tests.app.utils.attempts import Attempts
from tests.app.utils.timers import TimeOut
from tests.app.pages.base.base_page import BasePage


@allure.title("P0-1-220: Login with Username and Password")
@allure.title("P0-9-320: Login & Authentication")
@pytest.mark.core
@pytest.mark.pre_login
@pytest.mark.stage_1
@pytest.mark.smoke
def test_login_successful_and_verify_home_page(app_driver, logger, platform, env):
    """
    Test Case: Verify user successfully logs in and lands on Home page

    Test Steps:
    1. Launch apps and validate instant account signin
    2. Navigate to login with credentials
    3. Enter valid email and password
    4. Submit login form
    5. Handle reminder popup
    6. Verify user lands on home page successfully
    """

    driver = app_driver["driver"]
    platform = app_driver["platform"]
    BasePage.init_base(driver, logger, platform)

    logger.info(f"DEBUG - Platform parameter: '{platform}'")
    logger.info(f"DEBUG - BasePage.is_ios: {BasePage.is_ios}")
    logger.info(f"DEBUG - platform != 'android': {platform != 'android'}")

    logger.info("Starting login successful test...")
    home_page = HomePage()
    login_page = get_login_page(
        platform=platform,
        driver=driver,
        logger=logger,
    )
    # FIXME: Implemented this for 1.75.0 changed behaviour for Instant popup
    # time.sleep(5)
    # create_post_visible = home_page.check_visibility(home_page.home_create_post_button)
    # if create_post_visible:
    #     home_page.wait_and_click_element(home_page.home_create_post_button)
    with allure.step("Initialize login page and wait for login link to be visible"):
        login_page.wait_until_visible_with_retry(
            login_page.login_link, Attempts.THREE, TimeOut.THREE_SECONDS
        )
        login_page.handle_alert_if_present(platform)
        logger.info("Login link visible and alert (if any) handled.")

    with allure.step("Validate instant account signin state"):
        login_page.validate_instant_account_signin()
        logger.info("Instant account signin validation complete.")

    with allure.step("Navigate to login with credentials"):
        logger.info("Navigating to login with credentials...")
        login_page.click_element(login_page.login_link)
        login_page.click_element(login_page.login_with_email)
        logger.info("Navigated to email login screen.")

    with allure.step("Enter valid login credentials"):
        username = os.getenv("USERNAME")
        password = os.getenv("PASSWORD")

        logger.info(f"Entering credentials for user: {username}")
        login_page.set_element_text(login_page.email_input, username)

        password_input = login_page.get_element(login_page.password_input)
        password_input.click()
        login_page.set_element_text(login_page.password_input, password)
        logger.info("Login credentials entered successfully.")

    with allure.step("Submit login form"):
        logger.info("Submitting login form...")
        login_page.click_element(login_page.login_button)
        logger.info("Login button clicked, waiting for post-login content...")

    with allure.step("Handle reminder popup (if displayed)"):
        logger.info("Handling reminder popup if visible...")
        login_page.wait_and_click_element(login_page.reminder_button)
        login_page.wait_for_content_to_load()
        logger.info("Reminder popup handled successfully.")

    with allure.step("Verify user lands on Home Page and validate banners"):
        home_page = HomePage()
        logger.info("Verifying user landed on Home Page...")

        home_page.click_element(home_page.direct_message_banner)
        home_page.click_element(home_page.live_stream_banner)
        logger.info("Direct Message and Live Stream banners validated.")

    with allure.step("Validate all Home Page UI elements"):
        logger.info("Validating all home page elements...")
        home_page.validate_home_page_elements()
        logger.info("All home page elements validated successfully.")

    logger.info("Login successful test completed - All home page elements verified successfully")
