# ============================================================
# EXISTING CONTENT (MOBILE) → UNTOUCHED
# ============================================================
import logging
import os
import base64
import datetime
import pytest
import allure
from dotenv import load_dotenv

pytest_plugins = ["tests.common.cli_options"]
pytest_html = None

load_dotenv()


def pytest_configure(config):
    # Create logger object
    logger = logging.getLogger("Logger")
    logger.setLevel(logging.DEBUG)

    # Create file handler for logging to file
    file_handler = logging.FileHandler("Logger.log")
    file_handler.setLevel(logging.DEBUG)

    # Create console handler for logging to console
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)

    # Set log format
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    # Add handlers only if none exist to avoid duplicates
    if not logger.handlers:
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

    global pytest_html
    try:
        import pytest_html  # type: ignore
    except ImportError:
        pytest_html = None


@pytest.fixture(scope="session", autouse=True)
def create_report_dirs():
    # mobile screenshots
    os.makedirs("reports/mobile/screenshots", exist_ok=True)
    # web screenshots + videos
    os.makedirs("reports/web/screenshots", exist_ok=True)
    os.makedirs("reports/web/videos", exist_ok=True)


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    # Execute all other hooks to get the report object
    outcome = yield
    rep = outcome.get_result()

    if rep.when == "call" and rep.failed:
        # --- MOBILE ---
        app_driver_fixture = item.funcargs.get("app_driver", None)
        if app_driver_fixture and "driver" in app_driver_fixture:
            driver = app_driver_fixture["driver"]

            timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            screenshot_name = f"{item.name}_{timestamp}.png"
            screenshot_path = os.path.join("reports/mobile/screenshots", screenshot_name)

            driver.save_screenshot(screenshot_path)

            with open(screenshot_path, "rb") as f:
                allure.attach(
                    f.read(),
                    name="Mobile Failure Screenshot",
                    attachment_type=allure.attachment_type.PNG,
                )

            if pytest_html:
                with open(screenshot_path, "rb") as image_file:
                    encoded_image = base64.b64encode(image_file.read()).decode("utf-8")
                    html_img = f'<div><img src="data:image/png;base64,{encoded_image}" style="width:300px;height:auto;" /></div>'
                    if hasattr(rep, "extra"):
                        rep.extra.append(pytest_html.extras.html(html_img))
                    else:
                        rep.extra = [pytest_html.extras.html(html_img)]

        # --- WEB ---
        page_fixture = item.funcargs.get("page", None)
        if page_fixture:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            screenshot_name = f"{item.name}_{timestamp}.png"
            screenshot_path = os.path.join("reports/web/screenshots", screenshot_name)

            page_fixture.screenshot(path=screenshot_path)

            with open(screenshot_path, "rb") as f:
                allure.attach(
                    f.read(),
                    name="Web Failure Screenshot",
                    attachment_type=allure.attachment_type.PNG,
                )

            if pytest_html:
                with open(screenshot_path, "rb") as image_file:
                    encoded_image = base64.b64encode(image_file.read()).decode("utf-8")
                    html_img = f'<div><img src="data:image/png;base64,{encoded_image}" style="width:300px;height:auto;" /></div>'
                    if hasattr(rep, "extra"):
                        rep.extra.append(pytest_html.extras.html(html_img))
                    else:
                        rep.extra = [pytest_html.extras.html(html_img)]
