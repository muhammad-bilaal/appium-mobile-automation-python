from tests.app.pages.base.account_page import AccountPage
from tests.app.pages.base.settings import Settings
from tests.app.pages.base.login_page import LoginPage
from tests.app.pages.base.side_bar_menu_page import SideBarMenu
from tests.app.utils.attempts import Attempts
from tests.app.utils.constants import INSTANT_ACCOUNT_HEADING, LOGGED_OUT_MESSAGE
from tests.app.utils.locators import Locators
from tests.app.utils.look_up import LookBy
from tests.app.utils.messages import LOG_OUT, LOGIN_PAGE_LOAD


class AndroidLoginPage(LoginPage):
    def __init__(self, *, driver, logger, **kwargs):
        super().__init__(driver=driver, logger=logger, **kwargs)
        self.create_instant_account_heading = Locators(
            "Create Instant Account", LookBy.ACCESSIBILITY_ID
        )
        self.signin_with_instant_account = Locators(
            '//*[@content-desc="Create Instant Account"]', LookBy.XPATH
        )
        self.signin_with_instant_account_heading = Locators(
            '//*[@content-desc="Create Instant Account"]', LookBy.XPATH
        )
        self.recover_instance_link = Locators(
            'new UiSelector().resourceId("firstPage_recover_btn")', LookBy.ANDROID_UIAUTOMATOR
        )
        self.signup_with_email_or_phone_link = Locators(
            "Recover Instant Account", LookBy.ACCESSIBILITY_ID
        )
        self.go_back_from_recover_instance = Locators(
            'new UiSelector().resourceId("recoverInstAccPage_back_btn")', LookBy.ANDROID_UIAUTOMATOR
        )
        self.recover_input_field = Locators(
            'new UiSelector().resourceId("recoverInstAccPage_inputField")',
            LookBy.ANDROID_UIAUTOMATOR,
        )
        self.confirm_recovery_code_button = Locators(
            'new UiSelector().resourceId("recoverInstAccPage_confirm_btn")',
            LookBy.ANDROID_UIAUTOMATOR,
        )
        self.login_link = Locators('//android.view.View[@content-desc="Log in"]', LookBy.XPATH)
        self.go_back_button = Locators(
            '//android.widget.FrameLayout[@resource-id="android:id/content"]/android.widget.FrameLayout/android.widget.FrameLayout/android.view.View/android.view.View/android.view.View/android.widget.ImageView[1]',
            LookBy.XPATH,
        )
        self.info_support_question_mark = Locators(
            '//android.widget.FrameLayout[@resource-id="android:id/content"]/android.widget.FrameLayout/android.widget.FrameLayout/android.view.View/android.view.View/android.view.View/android.widget.ImageView[2]',
            LookBy.XPATH,
        )
        self.gettr_logo = Locators(
            '//android.widget.FrameLayout[@resource-id="android:id/content"]/android.widget.FrameLayout/android.widget.FrameLayout/android.view.View/android.view.View/android.view.View/android.widget.ImageView[4]',
            LookBy.XPATH,
        )
        self.login_with_your_social_media = Locators(
            "Log in with your social media", LookBy.ACCESSIBILITY_ID
        )
        self.sign_up_with_your_social_media = Locators(
            "Sign up with your social media", LookBy.ACCESSIBILITY_ID
        )
        self.google_link = Locators("google-oauth2", LookBy.ACCESSIBILITY_ID)
        self.apple_link = Locators("apple", LookBy.ACCESSIBILITY_ID)
        self.more_link = Locators("More", LookBy.ACCESSIBILITY_ID)
        self.or_partition = Locators("OR", LookBy.ACCESSIBILITY_ID)
        self.log_in_with_phone_or_email = Locators(
            "Log in with Phone Or Email", LookBy.ACCESSIBILITY_ID
        )
        self.sign_up_with_phone_or_email = Locators(
            '//android.view.View[@content-desc="Sign up with Phone or Email"]',
            LookBy.XPATH,
        )
        self.phone = Locators("Phone", LookBy.ACCESSIBILITY_ID)
        self.phone_tab = Locators("Phone\nTab 1 of 2", LookBy.ACCESSIBILITY_ID)
        self.email = Locators("Email", LookBy.ACCESSIBILITY_ID)
        self.email_or_username = Locators("Email / Username", LookBy.ACCESSIBILITY_ID)
        self.number_dropdown = Locators(
            'new UiSelector().className("android.widget.ImageView").instance(7)',
            LookBy.ANDROID_UIAUTOMATOR,
        )
        self.phone_number_input = Locators(
            '//android.widget.FrameLayout[@resource-id="android:id/content"]/android.widget.FrameLayout/android.widget.FrameLayout/android.view.View/android.view.View/android.view.View/android.view.View[6]',
            LookBy.XPATH,
        )
        self.send_code_button = Locators("Send Code", LookBy.ACCESSIBILITY_ID)
        self.having_trouble_logging_in = Locators(
            "Having trouble logging in?", LookBy.ACCESSIBILITY_ID
        )
        self.login_issue_support_text = Locators(
            "If you're having an issue logging in for GETTR, visit our support page down below.",
            LookBy.ACCESSIBILITY_ID,
        )
        self.help_centre_button = Locators("Help Center", LookBy.ACCESSIBILITY_ID)
        self.cancel_button_from_tab = Locators("Cancel", LookBy.ACCESSIBILITY_ID)
        self.login_go_back = Locators(
            '(//android.view.View[@content-desc="Log In"]//preceding-sibling::android.widget.ImageView)[1]',
            LookBy.XPATH,
        )
        self.reset_go_back = Locators(
            '(//android.view.View[@content-desc="Reset Password"]//preceding-sibling::android.widget.ImageView)[1]',
            LookBy.XPATH,
        )
        self.login_heading = Locators(
            '(//android.view.View[contains(@content-desc,"Log In")])[1]',
            LookBy.XPATH,
        )
        self.login_phone = Locators(
            '//android.view.View[contains(@content-desc,"Phone")]', LookBy.XPATH
        )
        self.login_email_or_username = Locators(
            '//android.view.View[contains(@content-desc,"Email / Username")]',
            LookBy.XPATH,
        )
        self.email_address_or_username_input = Locators(
            "(//android.widget.EditText[1]/android.widget.EditText)[1]",
            LookBy.XPATH,
        )
        self.password_input_field = Locators("(//android.widget.EditText)[3]", LookBy.XPATH)
        self.show_password_icon = Locators(
            '//android.view.View[@content-desc="Forgot password"]//preceding-sibling::android.widget.ImageView',
            LookBy.XPATH,
        )
        self.forgot_password_button = Locators(
            '//android.view.View[@content-desc="Forgot password"]', LookBy.XPATH
        )
        self.login_button_on_email_or_username_tab = Locators(
            '//android.view.View[@content-desc="Log In"]', LookBy.XPATH
        )
        self.log_in_with_one_time_code = Locators(
            '//android.view.View[@content-desc="Log in with one-time code"]',
            LookBy.XPATH,
        )
        self.sign_up_button_on_email_or_username_tab = Locators(
            '//android.view.View[@content-desc="Sign up"]', LookBy.XPATH
        )
        self.do_not_have_account_label = Locators(
            "id_login_do_not_have_an_account\nDon't have an account?",
            LookBy.ACCESSIBILITY_ID,
        )
        self.login_email_button = Locators("Email\nTab 2 of 2", LookBy.ACCESSIBILITY_ID)
        self.email_address_input = Locators(
            "//android.widget.EditText[1]",
            LookBy.XPATH,
        )
        self.email_address_input_for_reset_password = Locators(
            'new UiSelector().className("android.widget.EditText").instance(1)',
            LookBy.ANDROID_UIAUTOMATOR,
        )
        self.log_in_with_password_link = Locators(
            '//android.view.View[@content-desc="Log in with password"]',
            LookBy.XPATH,
        )
        self.login_with_credentials_button = Locators(
            "Log in with Phone, Email or Username", LookBy.ACCESSIBILITY_ID
        )
        self.email_input = Locators(
            "(//android.widget.EditText[1]/android.widget.EditText)[1]",
            LookBy.XPATH,
        )
        self.password_input = Locators("(//android.widget.EditText)[3]", LookBy.XPATH)
        self.login_button = Locators(
            '(//android.view.View[@content-desc="Log In"])[2]', LookBy.XPATH
        )
        self.reminder_button = Locators(
            '//android.view.View[@content-desc="Remind me later"]', LookBy.XPATH
        )
        self.live_section = Locators("live", LookBy.ACCESSIBILITY_ID)
        self.login_with_one_time_code_toggle = Locators(
            '//android.view.View[@content-desc="Log in with one-time code"]',
            LookBy.XPATH,
        )
        self.login_with_password_toggle = Locators(
            '//android.view.View[@content-desc="Log in with password"]',
            LookBy.XPATH,
        )
        self.sign_up_for_gettr = Locators("Sign up for GETTR", LookBy.ACCESSIBILITY_ID)
        self.forgot_password_link = Locators(
            '//android.view.View[@content-desc="Forgot password"]', LookBy.XPATH
        )
        self.reset_password_heading = Locators(
            '//android.view.View[@content-desc="Reset Password"]', LookBy.XPATH
        )
        self.enter_email_text = Locators(
            '//android.view.View[@content-desc="Please enter your email address."]',
            LookBy.XPATH,
        )
        self.verification_code_text = Locators(
            '//android.view.View[@content-desc="We’ll send you a verification code."]',
            LookBy.XPATH,
        )
        self.reset_send_code_button = Locators(
            '//android.view.View[@content-desc="Send Code"]', LookBy.XPATH
        )
        self.login_error_message = Locators(
            '//android.view.View[contains(@content-desc, "Sorry, your username or password is incorrect")]',
            LookBy.XPATH,
        )
        self.password_length_error_message = Locators(
            '//android.view.View[@content-desc="id_error\nPassword must be between 6 to 128 characters."]',
            LookBy.XPATH,
        )
        self.invalid_account_error_message = Locators(
            '//android.view.View[contains(@content-desc,"id_error\nSorry, there was no account with that information.")]',
            LookBy.XPATH,
        )
        self.dont_allow_notification_button = Locators(
            "com.android.permissioncontroller:id/permission_deny_button", LookBy.ID
        )
        self.dont_allow_notification = Locators('//*[@text="Don’t allow"]', LookBy.XPATH)
        self.please_enter_your_email_address = Locators(
            "Please enter your email address.", LookBy.ACCESSIBILITY_ID
        )
        self.we_will_send_you_a_verification_codes = Locators(
            "We’ll send you a verification code.", LookBy.ACCESSIBILITY_ID
        )
        self.reset_password = Locators("Reset Password", LookBy.ACCESSIBILITY_ID)
        self.notifications_no_data_message = Locators(
            "No Data\nJoin GETTR now to get more posts from people you want to follow!\nSign In to GETTR",
            LookBy.ACCESSIBILITY_ID,
        )

    def avatar_by_username(self, name: str):
        if "shahbaz" in name.lower():
            return Locators(
                f"(//android.view.View[contains(@content-desc,'{name}')]/preceding-sibling::android.view.View)[1]",
                LookBy.XPATH,
            )

        else:
            return Locators(
                f"(//android.view.View[contains(@content-desc,'{name}')]/preceding-sibling::android.widget.ImageView)[1]",
                LookBy.XPATH,
            )

    def validate_instant_account_signin(self, env="local"):
        instant_account_heading = self.get_element_text_by_attribute(
            self.create_instant_account_heading, "content-desc"
        )
        assert instant_account_heading == INSTANT_ACCOUNT_HEADING, LOGIN_PAGE_LOAD

    def is_instant_account_visible(self, env="local") -> bool:
        if env == "local":
            return self.is_element_displayed(self.signin_with_instant_account)
        else:
            return self.is_element_displayed(self.create_instant_account_heading)

    def click_instant_account(self, env="local"):
        self.click_element(self.create_instant_account_heading)

    def perform_logout_workflow(self, platform="android"):
        self.logger.info("Starting Logout workflow on Android...")

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
