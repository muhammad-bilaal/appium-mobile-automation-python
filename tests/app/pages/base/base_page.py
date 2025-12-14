import time
from abc import ABC

from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from tests.app.utils.gestures import Gestures
from tests.app.utils.locators import Locators
from tests.app.utils.look_up import LookBy
from tests.app.utils.timers import TimeOut


class BasePage(ABC):
    driver = None
    logger = None
    is_ios = None

    def __init__(self):
        if not self.driver or not self.logger:
            raise ValueError("BasePage dependencies not set. Please initialize before using.")

    @classmethod
    def init_base(cls, driver, logger, platform):
        cls.driver = driver
        cls.logger = logger
        cls.is_ios = platform != "android"

    def get_element(self, locator: Locators):
        self.logger.info(f"Getting element:{locator.locator} using {locator.by}")
        return WebDriverWait(self.driver, locator.time_out).until(
            EC.presence_of_element_located((locator.by, locator.locator))
        )

    def get_elements(self, locator: Locators):
        self.logger.info(f"Getting element:{locator.locator} using {locator.by}")
        return WebDriverWait(self.driver, locator.time_out).until(
            EC.presence_of_all_elements_located((locator.by, locator.locator))
        )

    def click_element(self, locator: Locators):
        self.get_element(locator).click()

    def set_element_text(self, locator, text):
        self.get_element(locator).send_keys(text)

    def clear_and_set_text(self, locator, text):
        """
        Clears the input field completely before setting new text.
        Works reliably on Android and iOS.
        """
        element = self.get_element(locator)
        element.click()
        time.sleep(0.2)
        element.clear()
        element.send_keys(text)

    def get_element_text(self, locator: Locators):
        element = self.get_element(locator)
        if self.is_ios:
            return element.text or element.get_attribute("name") or element.get_attribute("value")
        else:
            return element.text or element.get_attribute("contentDescription")

    def get_element_text_across_platform(self, locator: Locators):
        if self.is_ios:
            return self.get_element_text_by_attribute(locator, "name")
        else:
            return self.get_element_text_by_attribute(locator, "text")

    def get_element_text_by_attribute(self, locator: Locators, attribute_name):
        return self.get_element(locator).get_attribute(attribute_name)

    def wait_and_click_element(self, locator: Locators):
        self.wait_for_content_to_load()
        self.get_element(locator).click()

    def wait_for_content_to_load(self, timeout=TimeOut.TWO_SECONDS):
        time.sleep(timeout)

    def accept_allow_full_access_alert(self):
        self.driver.execute_script(
            "mobile: alert", {"action": "accept", "buttonLabel": "Allow Full Access"}
        )

    @property
    def go_back(self):
        return (
            Locators("//XCUIElementTypeImage[1]", LookBy.XPATH)
            if self.is_ios
            else Locators("//android.widget.ImageView[1]", LookBy.XPATH)
        )

    @property
    def download_go_back(self):
        return (
            Locators("//XCUIElementTypeImage[1]", LookBy.XPATH)
            if self.is_ios
            else Locators(
                'new UiSelector().className("android.widget.ImageView").instance(0)',
                LookBy.ANDROID_UIAUTOMATOR,
            )
        )

    @property
    def cancel_button(self):
        return (
            Locators("Cancel", LookBy.ACCESSIBILITY_ID)
            if self.is_ios
            else Locators("Cancel", LookBy.ACCESSIBILITY_ID)
        )

    def is_element_visible(self, locator, timeout=5):
        try:
            wait = WebDriverWait(self.driver, timeout)
            wait.until(EC.visibility_of_element_located(locator))
            return True
        except:  # noqa: E722
            return False

    def is_element_displayed(self, locator, timeout=10):
        """
        Wait up to `timeout` seconds for element to be visible.
        Fail test if not displayed within timeout.
        """
        wait = WebDriverWait(self.driver, timeout)
        by_value = locator.by if isinstance(locator.by, str) else locator.by.value
        locator_tuple = (by_value, locator.locator)

        self.logger.info(f"Waiting for visibility of element: {locator.locator}")

        try:
            element = wait.until(EC.visibility_of_element_located(locator_tuple))
            if element.is_displayed():
                self.logger.info(f"Element displayed: {locator}")
                return True
            else:
                self.logger.error(f"Element found but not visible: {locator}")
                raise AssertionError(f"Element found but not visible: {locator}")
        except Exception:
            self.logger.error(f"Element not displayed within {timeout}s: {locator}")
            raise AssertionError(f"Element not displayed within {timeout}s: {locator}")

    @property
    def home_button(self):
        return Locators("home", LookBy.ACCESSIBILITY_ID)

    def wait_until_visible_with_retry(self, locator, max_attempts=50, rest_time=3):
        """
        Waits until the element becomes visible on screen with retry mechanism.

        :param max_attempts: Maximum number of retries
        :param visible_timeout: How long to wait for visibility during each attempt
        :return: WebElement if found and visible, else raises last exception
        """
        attempt = 1
        while attempt <= max_attempts:
            try:
                self.logger.info(
                    f"[Attempt {attempt}] Waiting for visibility of element: {locator.locator}"
                )
                element = WebDriverWait(
                    self.driver,
                    rest_time,
                    poll_frequency=0.5,
                    ignored_exceptions=[NoSuchElementException],
                ).until(EC.visibility_of_element_located((locator.by, locator.locator)))
                self.logger.info(f" Element visible: {locator.locator}")
                return element

            except (NoSuchElementException, TimeoutException) as e:
                # Just log short reason instead of full Appium trace
                self.logger.warning(
                    f" Attempt {attempt} failed: {type(e).__name__} – element not found/visible yet."
                )
                time.sleep(rest_time)
                attempt += 1

        # Final failure after all attempts
        msg = f" Element not visible after {max_attempts} attempts: {locator.locator}"
        self.logger.error(msg)
        raise TimeoutException(msg)

    def wait_until_invisible_with_retry(
        self, locator, max_attempts=10, rest_time=1, min_total_wait=6
    ):
        """
        Waits until the element becomes invisible, retrying until it does or max attempts are reached.
        Ensures at least `min_total_wait` seconds are spent checking.

        :param locator: Locator object with 'by', 'locator', and 'time_out'
        :param max_attempts: Maximum number of retries
        :param rest_time: Delay between retries (in seconds)
        :param min_total_wait: Minimum total time to spend trying (in seconds)
        :return: True if element becomes invisible, else raises TimeoutException
        """
        attempt = 1
        start_time = time.time()

        while attempt <= max_attempts:
            try:
                self.logger.info(
                    f"[Attempt {attempt}] Waiting for invisibility of element: {locator.locator}"
                )
                is_invisible = WebDriverWait(self.driver, locator.time_out).until(
                    EC.invisibility_of_element_located((locator.by, locator.locator))
                )
                current_time = time.time()
                total_elapsed = current_time - start_time

                if is_invisible:
                    if total_elapsed < min_total_wait:
                        remaining_wait = min_total_wait - total_elapsed
                        self.logger.info(
                            f" Element became invisible early, waiting additional {remaining_wait:.2f}s to meet min wait"
                        )
                        time.sleep(remaining_wait)
                    self.logger.info(f" Element confirmed invisible: {locator}")
                    return True

            except TimeoutException as e:
                self.logger.info(f" Attempt {attempt} failed (still visible): {e}")
            except NoSuchElementException:
                self.logger.info(f" Element not present in DOM anymore: {locator}")
                return True

            time.sleep(rest_time)
            attempt += 1

        raise TimeoutException(f"Element still visible after {max_attempts} attempts: {locator}")

    def get_element_text_cross_platform(self, locator, platform: str):
        if platform == "android":
            return self.get_element_text_by_attribute(locator, "content-desc")
        else:  # iOS
            return self.get_element_text(locator)

    def get_element_text_cross_platform_by_attribute(self, locator, platform: str):
        if platform == "android":
            return self.get_element_text_by_attribute(locator, "content-desc")
        else:  # iOS
            return self.get_element_text_by_attribute(locator, "name")

    def swipe_up(
        self,
        start_y=Gestures.START_Y_HIGH,
        end_y=Gestures.END_Y_LOW,
        duration=Gestures.DURATION_MEDIUM,
    ):
        """
        Simple and reliable swipe up using driver.swipe()
        """
        window_size = self.driver.get_window_size()

        # Calculate coordinates for a substantial swipe
        start_x = window_size["width"] * 0.5
        _start_y = window_size["height"] * start_y
        _end_y = window_size["height"] * end_y
        self.driver.swipe(start_x, _start_y, start_x, _end_y, duration)
        time.sleep(0.3)

    def swipe_down(
        self,
        start_y=Gestures.START_Y_LOW,
        end_y=Gestures.END_Y_MAX,
        duration=Gestures.DURATION_MEDIUM,
    ):
        """
        Simple and reliable swipe down using driver.swipe()
        """
        window_size = self.driver.get_window_size()

        # Calculate coordinates for a substantial swipe (reverse of swipe_up)
        start_x = window_size["width"] * 0.5
        _start_y = window_size["height"] * start_y
        _end_y = window_size["height"] * end_y

        self.driver.swipe(start_x, _start_y, start_x, _end_y, duration)

        time.sleep(0.3)

    def scroll_to_bottom(self, start_y=0.7, end_y=0.3, swipes=3):
        """
        Scroll to the bottom of the screen
        """
        for _ in range(swipes):
            self.swipe_up(start_y=start_y, end_y=end_y)
        return True

    def scroll_to_top(self, swipes=3):
        """
        Scroll to the top of the screen
        """
        for _ in range(swipes):
            self.swipe_down()
        return True

    def scroll_until_element_visible(self, element_locator, max_attempts=10):
        """
        Keep swiping up until the specified element is visible
        or max attempts reached.
        """
        for attempt in range(max_attempts):
            try:
                element = self.get_element(element_locator)
                if element and element.is_displayed():
                    self.logger.info(f" Found element after {attempt + 1} swipe(s)")
                    return element
            except Exception:
                pass  # element not found yet

            self.logger.info(f"→ Swiping up attempt {attempt + 1}/{max_attempts}")
            self.swipe_up(end_y=Gestures.END_Y_HIGH)

        raise AssertionError(f" Element not found after {max_attempts} scroll attempts")

    def handle_alert_if_present(self, platform: str, timeout: int = 2):
        try:
            self.wait_for_content_to_load(timeout)

            if platform == "ios":
                try:
                    WebDriverWait(self.driver, timeout).until(EC.alert_is_present())
                    self.driver.switch_to.alert.accept()
                    if self.logger:
                        self.logger.info(" iOS alert accepted after content load")
                except Exception:
                    if self.logger:
                        self.logger.info(" No iOS alert found — continuing")
        except Exception as e:
            if self.logger:
                self.logger.warning(f" Skipped wait/alert handling due to error: {e}")

    def check_visibility(self, locator, timeout=5):
        try:
            wait = WebDriverWait(self.driver, timeout)
            by_value = locator.by if isinstance(locator.by, str) else locator.by.value
            locator_tuple = (by_value, locator.locator)
            self.logger.info(f"Checking visibility of element: {locator.locator}")
            element = wait.until(EC.visibility_of_element_located(locator_tuple))
            return element.is_displayed()

        except Exception:
            self.logger.info(f"Element not visible within {timeout}s: {locator.locator}")
            return False

    def handle_alert_or_dismiss_modal(self, platform: str, timeout: int = 2):
        try:
            self.wait_for_content_to_load(timeout)

            if platform == "ios":
                try:
                    WebDriverWait(self.driver, timeout).until(EC.alert_is_present())
                    self.driver.switch_to.alert.accept()
                    if self.logger:
                        self.logger.info("iOS alert accepted")
                    return
                except Exception:
                    # No alert, tap center to dismiss modal
                    screen_size = self.driver.get_window_size()
                    tap_x = screen_size["width"] // 2
                    tap_y = screen_size["height"] // 2

                    self.driver.tap([(tap_x, tap_y)])
                    if self.logger:
                        self.logger.info("Dismissed modal by tapping center")

        except Exception as e:
            if self.logger:
                self.logger.warning(f"Error handling alert/modal: {e}")

    def handle_allow_full_access_alert_if_present(self, platform: str, timeout: int = 2):
        try:
            self.wait_for_content_to_load(timeout)

            if platform == "ios":
                try:
                    WebDriverWait(self.driver, timeout).until(EC.alert_is_present())
                    self.accept_allow_full_access_alert()
                    if self.logger:
                        self.logger.info(" iOS full access alert accepted after content load")
                except Exception:
                    if self.logger:
                        self.logger.info(" No iOS full access alert found — continuing")
        except Exception as e:
            if self.logger:
                self.logger.warning(f" Skipped wait/alert handling due to error: {e}")

    @property
    def home_create_post_button(self):
        return (
            Locators("Home post", LookBy.ACCESSIBILITY_ID)
            if self.is_ios
            else Locators("Home post", LookBy.ACCESSIBILITY_ID)
        )

    @property
    def hide_keyboard(self):
        # Hide the on-screen keyboard on both Android and iOS.
        try:
            # Try the standard Appium command first
            self.driver.hide_keyboard()
        except Exception:
            try:
                # Alternative 1: Dismiss keyboard using the 'Done' key
                self.driver.hide_keyboard(strategy="pressKey", key_name="Done")
            except Exception:
                try:
                    # Alternative 2: Tap outside the text field (near top area)
                    window = self.driver.get_window_size()
                    tap_x = int(window["width"] * 0.5)
                    tap_y = int(window["height"] * 0.1)
                    self.driver.execute_script("mobile: tap", {"x": tap_x, "y": tap_y})
                except Exception as exc:
                    self.logger.warning(f"Failed to hide iOS keyboard: {exc}")

    def dismiss_half_modal(self):
        screen_size = self.driver.get_window_size()
        tap_x = screen_size["width"] // 2
        tap_y = int(screen_size["height"] * 0.2)
        self.driver.tap([(tap_x, tap_y)])

    def is_element_not_displayed(self, locator, timeout=TimeOut.FIVE_SECONDS):
        """
        Check that an element is NOT displayed or NOT present within the timeout.
        Passes if element is absent or invisible.
        """
        wait = WebDriverWait(self.driver, timeout)
        try:
            self.logger.info(
                f"Waiting for element to disappear or not be visible: {locator.locator}"
            )
            by_value = locator.by if isinstance(locator.by, str) else locator.by.value
            locator_tuple = (by_value, locator.locator)

            result = wait.until_not(EC.presence_of_element_located(locator_tuple))
            if result:
                self.logger.info(f"Element not visible as expected: {locator}")
                return True
            else:
                raise AssertionError(f"Element still visible after {timeout}s: {locator}")
        except Exception as e:
            raise AssertionError(f"Element still visible after {timeout}s: {locator}") from e

    def close_popup_by_tapping_top(self):
        screen_size = self.driver.get_window_size()
        tap_x = screen_size["width"] // 2
        tap_y = int(screen_size["height"] * 0.2)
        self.driver.tap([(tap_x, tap_y)])
        self.logger.info("Popup dismissed successfully")
