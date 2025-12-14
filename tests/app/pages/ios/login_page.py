from tests.app.pages.base.account_page import AccountPage
from tests.app.pages.base.settings import Settings
from tests.app.pages.base.login_page import LoginPage
from tests.app.pages.base.side_bar_menu_page import SideBarMenu
from tests.app.utils.attempts import Attempts
from tests.app.utils.constants import LOGGED_OUT_MESSAGE
from tests.app.utils.locators import Locators
from tests.app.utils.look_up import LookBy
from tests.app.utils.messages import LOG_OUT


class IOSLoginPage(LoginPage):
    def __init__(self, *, driver, logger, **kwargs):
        super().__init__(driver=driver, logger=logger, **kwargs)

    def validate_instant_account_signin(self, env="local"):
        if env.lower() == "local":
            instant_account_signin_button = self.get_element(self.signin_with_instant_account)
            assert (
                instant_account_signin_button.is_displayed()
            ), "Sign In button not displayed on screen"
        else:
            instant_account_signin_button = self.get_element(self.create_instant_account_heading)
            assert (
                instant_account_signin_button.is_displayed()
            ), "Sign In button not displayed on screen"

    @property
    def get_password_input_value(self):
        password_input_value = self.get_element_text(
            Locators("(//XCUIElementTypeSecureTextField)[1]", LookBy.XPATH)
        )
        return password_input_value

    def avatar_by_username(self, name: str):
        if "shahbaz" in name.lower():
            return Locators(
                f"(//XCUIElementTypeStaticText[contains(@name,'{name}')]/preceding-sibling::XCUIElementTypeOther)[1]",
                LookBy.XPATH,
            )
        else:
            return Locators(
                f"(//XCUIElementTypeStaticText[contains(@name,'{name}')]/preceding-sibling::XCUIElementTypeImage)[1]",
                LookBy.XPATH,
            )

    def click_instant_account(self, env="local"):
        if env.lower() == "local":
            self.click_element(self.signin_with_instant_account)
        else:
            self.click_element(self.create_instant_account_heading)

    def perform_logout_workflow(self, platform="ios"):
        self.logger.info("Starting Logout workflow on iOS...")

        side_bar_menu_page = SideBarMenu()
        assert side_bar_menu_page.is_element_displayed(
            side_bar_menu_page.profile_icon
        ), "Profile icon not visible"
        self.logger.info("Profile icon is visible")

        side_bar_menu_page.click_element(side_bar_menu_page.profile_icon)
        self.logger.info("Clicked on Profile icon")

        side_bar_menu_page.click_element(side_bar_menu_page.settings_tab)
        self.logger.info("Navigated to Settings tab")

        settings = Settings()
        settings.click_element(settings.account_tab)
        self.logger.info("Opened Account tab")

        account_page = AccountPage()
        account_page.click_element(account_page.account_information)
        self.logger.info("Opened Account Information page")

        account_page.wait_until_visible_with_retry(account_page.log_out, Attempts.TWO)
        assert account_page.is_element_displayed(account_page.log_out), "Log Out option not visible"

        account_page.click_element(account_page.log_out)
        self.logger.info("Selected Log Out option")

        account_page.click_element(account_page.do_not_save_and_log_out)
        self.logger.info("Chose 'Do Not Save & Log Out'")

        logged_out_message = account_page.get_element_text_cross_platform(
            account_page.log_out_pop_up, platform
        )
        account_page.wait_until_invisible_with_retry(account_page.log_out_pop_up)
        assert logged_out_message == LOGGED_OUT_MESSAGE, LOG_OUT
        self.logger.info(f"Log out confirmation message displayed: '{logged_out_message}'")
