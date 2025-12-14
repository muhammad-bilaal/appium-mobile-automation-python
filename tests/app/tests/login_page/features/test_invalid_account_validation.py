import pytest
import allure
from tests.app.factories.page_factory import get_login_page
from tests.app.utils.attempts import Attempts
from tests.app.utils.timers import TimeOut
from tests.app.pages.base.base_page import BasePage


@allure.epic("Smoke Tests")
@allure.feature("Login Module - Feature Tests")
@allure.story("Invalid Account Validation")
@pytest.mark.smoke
@pytest.mark.pre_login
@pytest.mark.stage_1
@pytest.mark.smoke
def test_invalid_account_validation(app_driver, logger, platform, env):
    """
    Test Case: LP_08 - Verify invalid account/email validation

    Test Steps:
    1. Launch apps and validate instant account signin
    2. Navigate to login with credentials
    3. Enter invalid/non-existent email and valid password
    4. Submit login form
    5. Verify error message appears for invalid account
    """

    driver = app_driver["driver"]
    platform = app_driver["platform"]
    BasePage.init_base(driver, logger, platform)

    logger.info("Starting invalid account validation test...")
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
        logger.info("Reached email login screen.")

    with allure.step("Enter invalid email and valid password"):
        logger.info("Entering invalid email and valid password...")
        invalid_email = "nonexistent@invalid.com"
        valid_password = "ValidPassword123"

        login_page.set_element_text(login_page.email_input, invalid_email)
        password_input = login_page.get_element(login_page.password_input)
        password_input.click()
        login_page.set_element_text(login_page.password_input, valid_password)
        logger.info(f"Email entered: {invalid_email}")
        logger.info("Valid password entered successfully.")

    with allure.step("Submit login form"):
        logger.info("Clicking login button with invalid account...")
        login_page.click_element(login_page.login_button)
        logger.info("Login button clicked, waiting for response...")

    with allure.step("Verify invalid account error message appears"):
        logger.info("Verifying invalid account error message...")
        login_page.wait_for_content_to_load()

        try:
            error_message_element = login_page.get_element(login_page.invalid_account_error_message)
            assert (
                error_message_element.is_displayed()
            ), "Invalid account error message is not displayed."
            error_text = login_page.get_element_text_cross_platform(
                login_page.invalid_account_error_message, platform
            )

            logger.info(f"Found error message text: {error_text}")
            assert (
                "Sorry, there was no account with that information" in error_text
            ), f"Expected invalid account error message not found. Got: {error_text}"

            logger.info("Invalid account error message verified successfully.")

        except Exception as e:
            logger.info(f"Could not find invalid account error message: {e}")
            logger.info("Debugging page source for potential text clues...")
            page_source = login_page.driver.page_source

            logger.info(f"Contains 'no account': {'no account' in page_source}")
            logger.info(f"Contains 'that information': {'that information' in page_source}")
            logger.info(f"Contains 'id_error': {'id_error' in page_source}")
            allure.attach(
                page_source,
                name="Page Source Debug",
                attachment_type=allure.attachment_type.TEXT,
            )
            raise e

    logger.info("Invalid account validation test completed - Error message verified successfully")
