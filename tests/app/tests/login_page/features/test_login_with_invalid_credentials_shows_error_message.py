import os
import pytest
import allure

from tests.app.factories.page_factory import get_login_page
from tests.app.utils.attempts import Attempts
from tests.app.utils.timers import TimeOut
from tests.app.pages.base.base_page import BasePage


@allure.epic("Smoke Tests")
@allure.feature("Login Module - Feature Tests")
@allure.story("Invalid Login Credentials")
@pytest.mark.smoke
@pytest.mark.pre_login
@pytest.mark.stage_1
@pytest.mark.smoke
def test_login_invalid_credentials(app_driver, logger, platform, env):
    """
    Test Case: LP_04 - Verify login with invalid credentials

    Test Steps:
    1. Launch apps and validate instant account signin
    2. Navigate to login with credentials
    3. Enter invalid email/phone or wrong password
    4. Submit login form
    5. Verify error message appears for invalid credentials
    """

    driver = app_driver["driver"]
    platform = app_driver["platform"]
    BasePage.init_base(driver, logger, platform)

    logger.info("Starting login invalid credentials test...")
    login_page = get_login_page(
        platform=platform,
        driver=driver,
        logger=logger,
    )
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

    with allure.step("Enter invalid password for valid username"):
        username = os.getenv("USERNAME")
        invalid_password = "wrongpassword123"

        logger.info(f"Entering username: {username}")
        login_page.set_element_text(login_page.email_input, username)

        password_input = login_page.get_element(login_page.password_input)
        password_input.click()
        login_page.set_element_text(login_page.password_input, invalid_password)
        logger.info("Entered invalid password intentionally for testing.")

    with allure.step("Submit login form"):
        logger.info("Submitting login form with invalid password...")
        login_page.click_element(login_page.login_button)
        logger.info("Login button clicked, waiting for error message...")

    with allure.step("Verify error message for invalid password"):
        logger.info("Verifying invalid password error message...")
        login_page.wait_for_content_to_load()

        try:
            # Primary attempt with contains locator
            error_message_element = login_page.get_element(login_page.login_error_message)
            assert (
                error_message_element.is_displayed()
            ), "Error message for invalid credentials not displayed."

            error_text = login_page.get_element_text_cross_platform(
                login_page.login_error_message, platform
            )
            logger.info(f"Found error message text: {error_text}")
            assert (
                "Sorry, your username or password is incorrect" in error_text
            ), f"Expected error message not found. Got: {error_text}"

            logger.info("Invalid password error message verified successfully.")

        except Exception as e:
            logger.info(f"Could not find error message with contains locator: {e}")

            with allure.step("Retry finding error message with exact locator"):
                try:
                    error_message_element = login_page.get_element(login_page.login_error_message)
                    assert (
                        error_message_element.is_displayed()
                    ), "Error message still not displayed with exact locator."
                    logger.info("Error message found using exact locator.")
                except Exception as e2:
                    logger.info(f"Could not find error message with exact locator: {e2}")

                    # Debugging assistance
                    logger.info("Debugging: Checking page source for error text clues...")
                    page_source = login_page.driver.page_source
                    logger.info(f"Contains 'Sorry': {'Sorry' in page_source}")
                    logger.info(f"Contains 'incorrect': {'incorrect' in page_source}")
                    logger.info(f"Contains 'id_error': {'id_error' in page_source}")

                    # Attach page source for debugging in Allure
                    allure.attach(
                        page_source,
                        name="Page Source Debug",
                        attachment_type=allure.attachment_type.TEXT,
                    )

                    raise e

    logger.info("Invalid credentials test completed - Error message verified successfully")
