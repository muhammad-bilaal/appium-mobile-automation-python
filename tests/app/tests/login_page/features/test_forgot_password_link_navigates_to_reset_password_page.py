import allure
import pytest

from tests.app.factories.page_factory import get_login_page
from tests.app.pages.base.base_page import BasePage
from tests.app.utils.attempts import Attempts
from tests.app.utils.timers import TimeOut


@allure.title("P0-9-320: Login & Authentication(Verify 'Forgot Password' flow)")
@pytest.mark.smoke
@pytest.mark.pre_login
@pytest.mark.stage_1
@pytest.mark.smoke
def test_forgot_password_navigation(app_driver, logger, platform, env):
    """
    Test Case: LP_05 - Verify Forgot Password link navigation

    Test Steps:
    1. Launch apps and validate instant account signin
    2. Navigate to login with credentials
    3. Click on Forgot Password link
    4. Verify user is redirected to password reset page
    5. Verify all required elements are present on reset password page
    """

    driver = app_driver["driver"]
    platform = app_driver["platform"]

    # Initialize BasePage with driver, logger, and platform
    BasePage.init_base(driver, logger, platform)
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
        logger.info(" Login link visible and alert (if any) handled.")

    with allure.step("Validate instant account signin state"):
        login_page.validate_instant_account_signin()
        logger.info(" Instant account signin validation complete.")

    with allure.step("Navigate to login with credentials"):
        logger.info(" Navigating to login with credentials...")
        login_page.click_element(login_page.login_link)
        login_page.click_element(login_page.login_with_email)
        logger.info(" Reached email login screen.")

    with allure.step("Click on 'Forgot Password' link"):
        logger.info(" Clicking on Forgot Password link...")
        forgot_password_link = login_page.get_element(login_page.forgot_password_link)
        assert (
            forgot_password_link.is_displayed()
        ), " Forgot Password link is not displayed on login page."
        login_page.click_element(login_page.forgot_password_link)
        login_page.wait_for_content_to_load()
        logger.info(" Forgot Password page loading initiated.")

    with allure.step("Verify Reset Password page elements"):
        logger.info(" Verifying reset password page elements...")

        reset_heading = login_page.get_element(login_page.reset_password_heading)
        assert reset_heading.is_displayed(), " Reset Password heading is not displayed."
        logger.info(" Reset Password heading verified.")

        email_text = login_page.get_element(login_page.enter_email_text)
        assert email_text.is_displayed(), " Enter email address text is not displayed."
        logger.info(" Email instruction text verified.")

        verification_text = login_page.get_element(login_page.verification_code_text)
        assert verification_text.is_displayed(), " Verification code text is not displayed."
        logger.info(" Verification code text verified.")

        send_code_btn = login_page.get_element(login_page.reset_send_code_button)
        assert send_code_btn.is_displayed(), " Send Code button is not displayed."
        logger.info(" Send Code button verified.")

    logger.info(" Forgot password navigation test completed - All elements verified successfully")
