from tests.app.exceptions.platform_exceptions import PlatformSupportError
from tests.app.pages.android.login_page import AndroidLoginPage
from tests.app.pages.android.profile_page import AndroidProfilePage
from tests.app.pages.ios.login_page import IOSLoginPage
from tests.app.pages.ios.profile_page import IOSProfilePage
from tests.web.pages.home_profile_page import WebHomeProfilePage
from tests.web.pages.login_page import WebLoginPage


def get_login_page(*, platform, driver, logger, **kwargs):
    platform = platform.lower()
    if platform == "android":
        return AndroidLoginPage(driver=driver, logger=logger, **kwargs)
    if platform == "ios":
        return IOSLoginPage(driver=driver, logger=logger, **kwargs)
    if platform == "web":
        return WebLoginPage(driver=driver, logger=logger, **kwargs)
    raise PlatformSupportError("Unsupported Platform", field_name="platform")

