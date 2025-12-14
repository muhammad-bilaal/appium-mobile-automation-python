import json
import os
from datetime import datetime
from appium import webdriver
import logging
from appium.options.android import UiAutomator2Options
from appium.options.ios import XCUITestOptions
from typing import Union, Dict, Any
from tests.app.utils.browserstack import get_app_id_from_browserstack_api

logger = logging.getLogger(__name__)


def load_caps(path: Union[str, os.PathLike]) -> Dict[str, Any]:
    path = os.fspath(path)
    with open(path, "r", encoding="utf-8") as f:
        caps = json.load(f)

    # Resolve apps path if relative (only for local runs)
    app_path = caps.get("appium:apps") or caps.get("apps")
    if (
        isinstance(app_path, str)
        and not app_path.startswith("bs://")
        and not os.path.isabs(app_path)
    ):
        caps_dir = os.path.dirname(os.path.abspath(path))
        abs_app_path = os.path.abspath(os.path.join(caps_dir, "..", app_path))
        caps["apps"] = abs_app_path

    return caps


def get_browserstack_driver(platform, test_name):
    username = os.getenv("BROWSERSTACK_USERNAME")
    access_key = os.getenv("BROWSERSTACK_ACCESS_KEY")

    platform = platform.lower()

    # Try to find the capabilities file from different possible locations
    possible_paths = [
        f"configs/{platform}_caps.json",  # When running from app directory
        f"tests/app/configs/browserstack_{platform}_caps.json",  # When running from root directory
    ]

    caps_file = None
    for path in possible_paths:
        if os.path.exists(path):
            caps_file = path
            break

    if caps_file is None:
        raise FileNotFoundError(f"Capabilities file not found. Tried: {possible_paths}")

    desired_caps = load_caps(caps_file)
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    build_timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    full_name = f"{test_name} - {platform} at {current_time}"

    app_version = os.getenv("APP_VERSION")

    # Always try to fetch dynamic app ID from BrowserStack API
    # If APP_VERSION is not set, fetch the latest app
    try:
        version_to_fetch = app_version if app_version else "latest"
        dynamic_app_id, version = get_app_id_from_browserstack_api(
            platform, version_to_fetch, logger
        )
        if platform == "android":
            desired_caps["appium:app"] = dynamic_app_id
        else:
            desired_caps["app"] = dynamic_app_id

        if app_version:
            logger.info(f"Using dynamic app ID for {platform} version {version}: {dynamic_app_id}")
        else:
            logger.info(
                f"No APP_VERSION set, using latest app for {platform} version {version}: {dynamic_app_id}"
            )
    except Exception as e:
        logger.warning(f"Failed to fetch dynamic app ID, using static app ID from config: {e}")

    if "bstack:options" in desired_caps:
        desired_caps["bstack:options"]["sessionName"] = full_name

        # Create unique build name with timestamp (groups multiple sessions)
        platform_name = "Android" if platform == "android" else "iOS"
        desired_caps["bstack:options"]["buildName"] = (
            f"GETTR {platform_name} Tests - {build_timestamp}"
        )

    logger.info(f"Loaded capabilities for {platform}: {desired_caps}")
    if platform == "android":
        options = UiAutomator2Options().load_capabilities(desired_caps)
    elif platform == "ios":
        options = XCUITestOptions().load_capabilities(desired_caps)
    else:
        raise ValueError(f"Unsupported platform: {platform}")

    # BrowserStack SDK will handle the connection automatically when using the config
    browserstack_url = f"https://{username}:{access_key}@hub-cloud.browserstack.com/wd/hub"
    driver = webdriver.Remote(browserstack_url, options=options)

    logger.info(f"Created BrowserStack driver for {platform} with test name: {full_name}")
    return driver


def get_local_driver(platform):
    platform = platform.lower()

    # Try to find the capabilities file from different possible locations
    possible_paths = [
        f"configs/{platform}_caps.json",  # When running from app directory
        f"tests/app/configs/{platform}_caps.json",  # When running from root directory
    ]

    caps_file = None
    for path in possible_paths:
        if os.path.exists(path):
            caps_file = path
            break

    if caps_file is None:
        raise FileNotFoundError(f"Capabilities file not found. Tried: {possible_paths}")

    desired_caps = load_caps(caps_file)

    if platform == "android":
        options = UiAutomator2Options().load_capabilities(desired_caps)
    elif platform == "ios":
        options = XCUITestOptions().load_capabilities(desired_caps)
    else:
        raise ValueError(f"Unsupported platform: {platform}")

    logger.info(f"Creating local session with capabilities:\n{desired_caps}")
    driver = webdriver.Remote(command_executor="http://localhost:4723", options=options)
    return driver


def get_driver(*, platform: str, test_name: str, env: str = "browserstack") -> webdriver.Remote:
    """
    Returns a WebDriver based on environment:
      - env = "browserstack" → BrowserStack cloud
      - env = "local" → Local Appium server
    """
    if env == "browserstack":
        return get_browserstack_driver(platform, test_name)
    return get_local_driver(platform)
