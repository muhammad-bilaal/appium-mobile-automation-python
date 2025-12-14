import os
from abc import abstractmethod
from tests.app.pages.base.new_base_page import BasePage
from tests.app.utils.locators import Locators
from tests.app.utils.look_up import LookBy


class LoginPage(BasePage):
    def __init__(self, *, driver, logger, **kwargs):
        super().__init__(driver=driver, logger=logger, **kwargs)
        self.create_instant_account_heading = Locators(
            "Create Instant Account", LookBy.ACCESSIBILITY_ID
        )
        self.signin_with_instant_account = Locators(
            "Create Instant Account", LookBy.ACCESSIBILITY_ID
        )
        self.signin_with_instant_account_heading = Locators(
            "Create Instant Account", LookBy.ACCESSIBILITY_ID
        )
        self.recover_instance_link = Locators(
            '//XCUIElementTypeStaticText[@name="firstPage_recover_btn"]', LookBy.XPATH
        )
        self.signup_with_email_or_phone_link = Locators(
            "firstPage_signup_btn", LookBy.ACCESSIBILITY_ID
        )
        self.go_back_from_recover_instance = Locators(
            "recoverInstAccPage_back_btn", LookBy.ACCESSIBILITY_ID
        )
        self.recover_input_field = Locators(
            "recoverInstAccPage_inputField",
            LookBy.ACCESSIBILITY_ID,
        )
        self.confirm_recovery_code_button = Locators(
            "recoverInstAccPage_confirm_btn",
            LookBy.ACCESSIBILITY_ID,
        )
        self.instant_account_recovery_heading = Locators(
            "Instant Account Recovery", LookBy.ACCESSIBILITY_ID
        )
        self.input_recover_code_heading = Locators("Input recover code", LookBy.ACCESSIBILITY_ID)
        self.login_link = Locators("Log in", LookBy.ACCESSIBILITY_ID)
        self.go_back_button = Locators(
            '//XCUIElementTypeApplication[@name="GETTR"]//XCUIElementTypeImage[1]',
            LookBy.XPATH,
        )
        self.info_support_question_mark = Locators(
            '//XCUIElementTypeApplication[@name="GETTR"]//XCUIElementTypeImage[2]',
            LookBy.XPATH,
        )
        self.gettr_logo = Locators(
            '//XCUIElementTypeApplication[@name="GETTR"]//XCUIElementTypeImage[3]',
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
            '//XCUIElementTypeStaticText[@name="Sign up with Phone or Email"]',
            LookBy.XPATH,
        )
        self.phone = Locators("Phone", LookBy.ACCESSIBILITY_ID)
        self.phone_tab = Locators("Phone\nTab 1 of 2", LookBy.ACCESSIBILITY_ID)
        self.email = Locators("Email", LookBy.ACCESSIBILITY_ID)
        self.email_or_username = Locators("Email / Username", LookBy.ACCESSIBILITY_ID)
        self.number_dropdown = Locators(
            "//XCUIElementTypeWindow//XCUIElementTypeImage[2]", LookBy.XPATH
        )
        self.phone_number_input = Locators("Phone Number", LookBy.ACCESSIBILITY_ID)
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
            '//XCUIElementTypeApplication[@name="GETTR"]//XCUIElementTypeImage',
            LookBy.XPATH,
        )
        self.reset_go_back = Locators(
            '//XCUIElementTypeApplication[@name="GETTR"]//XCUIElementTypeImage',
            LookBy.XPATH,
        )
        self.login_heading = Locators('//XCUIElementTypeOther[@name="Log In"]', LookBy.XPATH)
        self.login_phone = Locators("Phone\nTab 1 of 2", LookBy.ACCESSIBILITY_ID)
        self.login_email_or_username = Locators(
            "Email / Username\nTab 2 of 2", LookBy.ACCESSIBILITY_ID
        )
        self.email_address_or_username_input = Locators(
            "Email address or username", LookBy.ACCESSIBILITY_ID
        )
        self.password_input_field = Locators("Password", LookBy.ACCESSIBILITY_ID)
        self.show_password_icon = Locators(
            '//XCUIElementTypeApplication[@name="GETTR"]//XCUIElementTypeImage',
            LookBy.XPATH,
        )
        self.forgot_password_button = Locators("Forgot password", LookBy.ACCESSIBILITY_ID)
        self.login_button_on_email_or_username_tab = Locators(
            '//XCUIElementTypeStaticText[@name="Log In"]', LookBy.XPATH
        )
        self.log_in_with_one_time_code = Locators(
            "Log in with one-time code", LookBy.ACCESSIBILITY_ID
        )
        self.sign_up_button_on_email_or_username_tab = Locators("Sign up", LookBy.ACCESSIBILITY_ID)
        self.do_not_have_account_label = Locators(
            "id_login_do_not_have_an_account\nDon't have an account?",
            LookBy.ACCESSIBILITY_ID,
        )
        self.login_email_button = Locators("Email\nTab 2 of 2", LookBy.ACCESSIBILITY_ID)
        self.email_address_input = Locators("Email address", LookBy.ACCESSIBILITY_ID)
        self.email_address_input_for_reset_password = Locators(
            "Email address", LookBy.ACCESSIBILITY_ID
        )
        self.log_in_with_password_link = Locators("Log in with password", LookBy.ACCESSIBILITY_ID)
        self.login_with_credentials_button = Locators(
            "Log in with Phone, Email or Username", LookBy.ACCESSIBILITY_ID
        )
        self.login_with_email = Locators("Email / Username", LookBy.ACCESSIBILITY_ID)
        self.email_input = Locators("Email address or username", LookBy.ACCESSIBILITY_ID)
        self.password_input = Locators("Password", LookBy.ACCESSIBILITY_ID)
        self.login_button = Locators(
            'name == "Log In" AND label == "Log In" AND value == "Log In"',
            LookBy.IOS_PREDICATE,
        )
        self.reminder_button = Locators("Remind me later", LookBy.ACCESSIBILITY_ID)
        self.live_section = Locators("live", LookBy.ACCESSIBILITY_ID)
        self.login_with_one_time_code_toggle = Locators(
            "Log in with one-time code", LookBy.ACCESSIBILITY_ID
        )
        self.login_with_password_toggle = Locators("Log in with password", LookBy.ACCESSIBILITY_ID)
        self.sign_up_for_gettr = Locators("Sign up for GETTR", LookBy.ACCESSIBILITY_ID)
        self.forgot_password_link = Locators("Forgot password", LookBy.ACCESSIBILITY_ID)
        self.reset_password_heading = Locators("Reset Password", LookBy.ACCESSIBILITY_ID)
        self.enter_email_text = Locators(
            "Please enter your email address.", LookBy.ACCESSIBILITY_ID
        )
        self.verification_code_text = Locators(
            '//XCUIElementTypeStaticText[contains(@name, "We’ll send you a verification code.")]',
            LookBy.XPATH,
        )
        self.reset_send_code_button = Locators("Send Code", LookBy.ACCESSIBILITY_ID)
        self.login_error_message = Locators(
            '//XCUIElementTypeStaticText[contains(@name, "Sorry, your username or password is incorrect") and contains(@name, "Please try again")]',
            LookBy.XPATH,
        )
        self.password_length_error_message = Locators(
            '//XCUIElementTypeStaticText[contains(@name, "Password must be between 6 to 128 characters.")]',
            LookBy.XPATH,
        )
        self.invalid_account_error_message = Locators(
            '//XCUIElementTypeStaticText[contains(@name, "Sorry, there was no account with that information.")]',
            LookBy.XPATH,
        )
        self.dont_allow_notification_button = Locators("", LookBy.XPATH)
        self.dont_allow_notification = Locators('//*[@label="Don’t allow"]', LookBy.XPATH)
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

    @property
    def get_ios_password_input_value(self):
        # Locate the secure password text field
        password_input_value = self.get_element_text(
            Locators("(//XCUIElementTypeSecureTextField)[1]", LookBy.XPATH)
        )
        return password_input_value

    def validate_instant_account_signin(self, env="local"):
        """
        Validate instant account sign-in for a given environment.
        Must be implemented in platform-specific classes.
        """
        raise NotImplementedError("validate_instant_account_signin() not implemented")

    def is_instant_account_visible(self, env="local") -> bool:
        if env == "local":
            return self.is_element_displayed(self.signin_with_instant_account)
        else:
            return self.is_element_displayed(self.create_instant_account_heading)

    def click_instant_account(self, env="local"):
        raise NotImplementedError("click_instant_account() not implemented")

    def login_user(self, username=None):
        # Determine which user to use
        username = username or os.getenv("USERNAME")
        password = os.getenv("PASSWORD")

        # FIXME: Implemented this for 1.75.0 changed behaviour for Instant popup
        # self.wait_for_content_to_load(3)
        # try:
        #     # Check if "Create Post" button is visible
        #     create_post_visible = self.wait_until_visible_with_retry(
        #         self.home_create_post_button,
        #         Attempts.THREE,
        #         TimeOut.TWO_SECONDS,
        #     )
        #
        #     if create_post_visible:
        #         self.wait_and_click_element(self.home_create_post_button)
        #     else:
        #         raise TimeoutException  # Continue with login flow if not visible
        #
        # except TimeoutException:
        #     pass

        self.wait_and_click_element(self.login_link)
        self.click_element(self.login_with_email)

        self.logger.info(f"Setting up email address: {username}")
        self.set_element_text(self.email_input, username)

        password_input = self.get_element(self.password_input)
        password_input.click()
        self.set_element_text(self.password_input, password)

        self.click_element(self.login_button)
        self.wait_and_click_element(self.reminder_button)
        self.wait_for_content_to_load()
        # Step 7: Wait for Home Feed
        self.logger.info(" Waiting for home feed to load...")
        self.wait_for_content_to_load()
        self.logger.info(" User login workflow completed successfully!")

        # Step 7: Wait for Home Feed
        self.logger.info(" Waiting for home feed to load...")
        self.wait_for_content_to_load()
        self.logger.info(" User login workflow completed successfully!")

    @abstractmethod
    def perform_logout_workflow(self, platform):
        """
        Perform full logout workflow:
        1. Open sidebar menu → Profile → Settings → Account
        2. Navigate to Account Information and Log Out
        3. Confirm log out action
        4. Validate log out confirmation message
        5. Validate user is redirected back to Sign Up screen
        """
        raise NotImplementedError("perform_logout_workflow() not implemented")

    def avatar_by_username(self, name: str):
        """
        Return avatar locator based on username.
        Must be implemented in platform-specific subclasses.
        """
        raise NotImplementedError("avatar_by_username() not implemented")
