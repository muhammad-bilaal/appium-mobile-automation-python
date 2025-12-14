import pytest
import allure

from tests.app.factories.page_factory import get_login_page
from tests.app.utils.attempts import Attempts
from tests.app.utils.timers import TimeOut


@pytest.mark.pre_login
@pytest.mark.stage_1
@pytest.mark.smoke
@allure.title("Short Password Validation Test")
@allure.description(
    "Verify that entering a password shorter than 6 characters shows the correct validation error message."
)
def test_short_password_validation(app_driver, platform, env, logger):
    logger.info("Starting short password validation test...")
    driver = app_driver["driver"]
    platform = app_driver["platform"]
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

    with allure.step("Enter valid email and short password"):
        valid_email = "test@gettr.com"
        short_password = "12345"  # Only 5 characters

        logger.info(f"Entering valid email: {valid_email}")
        login_page.set_element_text(login_page.email_input, valid_email)

        password_input = login_page.get_element(login_page.password_input)
        password_input.click()
        login_page.set_element_text(login_page.password_input, short_password)
        logger.info(f"Entered short password: {short_password} (expected to fail validation).")

    with allure.step("Submit login form"):
        logger.info("Clicking login button with short password...")
        login_page.click_element(login_page.login_button)
        logger.info("Login button clicked, waiting for validation message...")

    with allure.step("Verify password length error message appears"):
        logger.info("Verifying password length error message...")
        login_page.wait_for_content_to_load()

        try:
            error_message_element = login_page.get_element(login_page.password_length_error_message)
            assert (
                error_message_element.is_displayed()
            ), "Password length error message not displayed."

            error_text = login_page.get_element_text_cross_platform(
                login_page.password_length_error_message, platform
            )
            logger.info(f"Found error message text: {error_text}")
            assert (
                "Password must be between 6 to 128 characters" in error_text
            ), f"Expected password length error message not found. Got: {error_text}"

            logger.info("Password length validation message verified successfully.")

        except Exception as e:
            logger.info(f"Could not find password length error message: {e}")
            logger.info("Debugging page source for potential clues...")
            page_source = login_page.driver.page_source

            logger.info(f"Contains 'Password must be': {'Password must be' in page_source}")
            logger.info(f"Contains '6 to 128': {'6 to 128' in page_source}")
            logger.info(f"Contains 'id_error': {'id_error' in page_source}")

            # Attach page source to Allure for debugging
            allure.attach(
                page_source,
                name="Page Source Debug",
                attachment_type=allure.attachment_type.TEXT,
            )

            raise e
        logger.info(
            "Password length validation test completed - Error message verified successfully"
        )
