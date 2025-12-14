import pytest
import allure

from tests.app.factories.page_factory import get_login_page
from tests.app.pages.base.guest_user_page import GuestUserPage
from tests.app.pages.base.home_page import HomePage
from tests.app.pages.base.base_page import BasePage
from tests.app.utils.timers import TimeOut


@allure.title("P0-1-400 Logout")
@allure.title("P0-9-390: Profile & Settings")
@pytest.mark.core
@pytest.mark.post_login
@pytest.mark.stage_1
@pytest.mark.smoke
def test_login_successful_and_logout_flow(app_driver, logger, platform, env):
    driver = app_driver["driver"]
    platform = app_driver["platform"]
    BasePage.init_base(driver, logger, platform)

    logger.info("Starting login invalid credentials test...")
    login_page = get_login_page(
        platform=platform,
        driver=driver,
        logger=logger,
    )
    home_page = HomePage()
    guest_user = GuestUserPage()
    with allure.step("Starting login successful test"):
        logger.info("Starting login successful test...")

    with allure.step("Logging in user"):
        logger.info("Attempting to log in user...")
        login_page.login_user()
        logger.info("User login successful")

    with allure.step("Validating home page elements"):
        logger.info("Validating home page elements...")
        home_page.validate_home_page_elements()
        logger.info("All home page elements validated successfully")

    with allure.step("Performing logout workflow"):
        logger.info("Initiating logout workflow...")
        login_page.perform_logout_workflow(platform)
        logger.info("Logout workflow completed successfully")

    with allure.step("Attempt to click Like button on first post"):
        home_page.scroll_until_element_visible(home_page.first_post_like_button)
        home_page.wait_and_click_element(home_page.first_post_like_button)
        logger.info("Clicked Like button as guest user.")
        login_page.validate_instant_account_signin()
        logger.info("Sign-In popup triggered successfully.")
        home_page.dismiss_half_modal()

    with allure.step("Attempt to click Comment button on first post"):
        home_page.wait_and_click_element(home_page.first_post_comment_button)
        logger.info("Clicked Comment button as guest user.")
        login_page.validate_instant_account_signin()
        logger.info("Sign-In popup triggered successfully.")
        home_page.dismiss_half_modal()

    with allure.step("Attempt to click Repost button on first post"):
        home_page.wait_and_click_element(home_page.first_post_repost_button)
        home_page.wait_for_content_to_load(TimeOut.ONE_SECOND)
        home_page.wait_and_click_element(home_page.repost_confirmation_button)
        home_page.wait_for_content_to_load(TimeOut.TWO_SECONDS)
        logger.info("Clicked Repost button as guest user.")
        login_page.validate_instant_account_signin()
        logger.info("Sign-In popup triggered successfully.")
        home_page.dismiss_half_modal()

    with allure.step("Navigate to Following tab and validate 'No Data' message"):
        home_page.wait_and_click_element(home_page.following_tab)
        home_page.wait_for_content_to_load(TimeOut.TWO_SECONDS)
        no_data_message = guest_user.get_element(login_page.notifications_no_data_message)
        assert no_data_message.is_displayed(), "'No Data' message not displayed in Following tab."
        logger.info("'No Data' message displayed successfully on Following tab.")

    with allure.step("Final verification"):
        logger.info("Login + Logout test completed successfully")
