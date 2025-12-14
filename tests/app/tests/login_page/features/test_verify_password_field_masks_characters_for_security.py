import allure
import pytest

from tests.app.factories.page_factory import get_login_page
from tests.app.utils.attempts import Attempts
from tests.app.utils.timers import TimeOut


@allure.epic("Smoke Tests")
@allure.feature("Login Module - Feature Tests")
@allure.story("Password Masking")
@pytest.mark.smoke
@pytest.mark.pre_login
@pytest.mark.stage_1
@pytest.mark.smoke
def test_password_masking(app_driver, logger, platform, env):
    """
    Test Case: LP_06 - Verify password is masked

    Test Steps:
    1. Launch apps and validate instant account signin
    2. Navigate to login with credentials
    3. Enter text in password field
    4. Verify password characters are masked (hidden) as •••••••
    """

    driver = app_driver["driver"]
    platform = app_driver["platform"]

    # Initialize BasePage with driver, logger, and platform
    from tests.app.pages.base.base_page import BasePage

    BasePage.init_base(driver, logger, platform)

    logger.info("Starting password masking test...")
    login_page = get_login_page(
        platform=platform,
        driver=driver,
        logger=logger,
    )
    login_page.wait_until_visible_with_retry(
        login_page.login_link, Attempts.THREE, TimeOut.THREE_SECONDS
    )

    # Handle iOS alert if needed
    login_page.handle_alert_if_present(platform)

    # Step 1: Initialize login page and validate instant account signin
    login_page.validate_instant_account_signin()

    # Step 2: Navigate to login with credentials
    logger.info("Navigating to login with credentials...")
    login_page.click_element(login_page.login_link)
    # login.click_element(login.login_with_credentials_button)
    login_page.click_element(login_page.login_with_email)

    # Step 3: Enter text in password field
    logger.info("Entering password to test masking...")
    test_password = "TestPassword123"

    # Click on password field and enter password
    password_input = login_page.get_element(login_page.password_input)
    password_input.click()
    login_page.set_element_text(login_page.password_input, test_password)
    if platform == "android":
        # Step 4: Verify password characters are masked
        logger.info("Verifying password masking...")
        # Get the actual text/value from the password field
        password_field_value = password_input.get_attribute("text")
        if not password_field_value:
            password_field_value = password_input.get_attribute("value")
    else:
        password_field_value = login_page.get_ios_password_input_value

    logger.info(f"Password field shows: '{password_field_value}'")

    # Verify the password is masked with bullet characters
    expected_masked_length = len(test_password)

    # Check if the displayed value contains masked characters (bullets or asterisks)
    is_masked = (
        "•" in password_field_value
        or "*" in password_field_value
        or "" in password_field_value
        or len(password_field_value) == expected_masked_length
        and password_field_value != test_password
    )

    assert is_masked, f"Password is not properly masked. Expected masked characters but got: '{password_field_value}'"

    # Additional verification: ensure the actual password text is not visible
    assert (
        test_password not in password_field_value
    ), f"Password text is visible and not masked: '{password_field_value}'"

    logger.info("Password masking verified - Characters are properly hidden")

    # Optional: Verify the length matches (if the masking shows same number of characters)
    if "•" in password_field_value or "*" in password_field_value or "" in password_field_value:
        masked_char_count = len([c for c in password_field_value if c in "•*"])
        logger.info(
            f"Found {masked_char_count} masked characters for {expected_masked_length} input characters"
        )

    logger.info("Password masking test completed successfully")
