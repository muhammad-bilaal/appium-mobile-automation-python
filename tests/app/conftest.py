import os
from datetime import datetime
from dotenv import load_dotenv
import pytest
import logging
from browserstack_sdk import BrowserStackSdk
from tests.app.utils import app_driver as app_driver_utils
from tests.app.utils import browserstack as browserstack_utils
from tests.app.utils import reporting as reporting_utils
from tests.app.utils.app_driver import create_web_session_driver
from tests.app.utils.session_manager import SessionDriverManager
from tests.app.utils.video import (
    build_unique_video_name,
    save_recording,
    should_record_video,
)

pytest_plugins = ["tests.common.cli_options"]
pytest_html = None

log = logging.getLogger("Logger")

# Initialize BrowserStack SDK so it can auto-capture enhanced session data
sdk = BrowserStackSdk()

load_dotenv()

BASE_REPORT_DIR = "reports"
ALLURE_RESULTS_DIR = os.path.join(BASE_REPORT_DIR, "allure-results")
ALLURE_REPORT_DIR = os.path.join(BASE_REPORT_DIR, "allure-report")


def pytest_configure(config):
    # ---- Logging Setup ----
    logger = logging.getLogger("Logger")
    logger.setLevel(logging.INFO)

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    log_filename = f"reports/logs/test_log_{timestamp}.log"
    os.makedirs(os.path.dirname(log_filename), exist_ok=True)

    file_handler = logging.FileHandler(log_filename)
    file_handler.setLevel(logging.INFO)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)

    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    if not logger.hasHandlers():
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

    config._metadata = getattr(config, "_metadata", {})
    config._metadata["log_file"] = log_filename

    # ---- HTML Plugin Setup ----
    global pytest_html
    try:
        import pytest_html
    except ImportError:
        pytest_html = None


@pytest.fixture(scope="session")
def logger():
    return logging.getLogger("Logger")


def pytest_runtest_setup(item):
    """Called before each test runs"""
    global _current_test_name
    _current_test_name = item.name

    log.info(f"***** Setting up: {item.name}")

    manager = None
    context = item.funcargs.get("logged_in_app_driver") if hasattr(item, "funcargs") else None
    if isinstance(context, dict):
        manager = context.get("_manager")
        if manager:
            try:
                manager.ensure_ready_for_test(item)
            except Exception as exc:
                log.warning(f"Failed to prepare session driver for {item.name}: {exc}")

    # Update BrowserStack session name and mark test start
    env = item.config.getoption("--env")
    if env == "browserstack":
        driver = None

        if "app_driver" in item.fixturenames:
            try:
                if hasattr(item, "funcargs") and "app_driver" in item.funcargs:
                    app_driver_fixture = item.funcargs["app_driver"]
                    if app_driver_fixture and "driver" in app_driver_fixture:
                        driver = app_driver_fixture["driver"]
            except Exception:
                pass

        if driver is None and isinstance(context, dict):
            driver = context.get("driver") or driver

        if driver:
            browserstack_utils.mark_test_start(driver, item.name, env, log)


def pytest_collection_modifyitems(config, items):
    """Ensure that if any test in a module requires login, all tests in that module inherit the marker."""
    module_requires_login = {}

    for item in items:
        module = getattr(item, "module", None)
        if module is None:
            continue
        if item.get_closest_marker("requires_login"):
            module_requires_login[module] = True
        elif module not in module_requires_login:
            module_requires_login[module] = False

    for item in items:
        module = getattr(item, "module", None)
        if module_requires_login.get(module):
            if not item.get_closest_marker("requires_login"):
                item.add_marker(pytest.mark.requires_login)

    platform = getattr(config, "platform", "ios")
    for item in items:
        if "android_only" in item.keywords and platform == "ios":
            item.add_marker(pytest.mark.skip(reason="Runs on Android only"))


@pytest.fixture(scope="function")
def app_driver(logger, request, platform, env):
    test_name = request.node.name
    login_needed = request.node.get_closest_marker("requires_login") is not None

    driver = app_driver_utils.create_function_scoped_driver(
        logger=logger,
        platform=platform,
        env=env,
        test_name=test_name,
        login_required=login_needed,
    )

    try:
        yield {"driver": driver, "platform": platform, "logger": logger}
    finally:
        app_driver_utils.finalize_function_scoped_driver(
            driver=driver,
            request=request,
            env=env,
            logger=logger,
            test_name=test_name,
        )


# Global variable to track current test for session-scoped fixtures
_current_test_name = None


@pytest.fixture(scope="function")
def web_driver(logger, request, platform, env):
    test_name = request.node.name
    login_needed = request.node.get_closest_marker("requires_login") is not None

    if platform.lower() != "web":
        pytest.skip("web_session_driver is only for web tests")

    driver = app_driver_utils.create_function_scoped_web_driver(
        logger=logger,
        platform=platform,
        env=env,
        test_name=test_name,
        login_required=login_needed,
    )

    yield driver

    driver.quit()


@pytest.fixture(scope="session")
def web_session_driver(logger, env, platform):
    """
    Session-scoped web driver fixture.
    Logs in once and shares the same session across all web tests.
    """
    if platform.lower() != "web":
        pytest.skip("web_session_driver is only for web tests")

    driver = create_web_session_driver(logger, env)

    yield driver

    driver.quit()


@pytest.fixture(scope="session")
def logged_in_app_driver(logger, request, platform, env):
    """
    Creates a session-scoped Appium driver for tests requiring login.
    The session is restarted automatically after failures or user changes.
    """
    user_marker = request.node.get_closest_marker("user")
    username = user_marker.args[0] if user_marker else os.getenv("USERNAME")
    session_manager = SessionDriverManager(
        request=request,
        logger=logger,
        platform=platform,
        env=env,
        username=username,
    )

    try:
        yield session_manager.context
    finally:
        session_manager.finalize_session()


@pytest.fixture(scope="session", autouse=True)
def create_report_dirs():
    os.makedirs("reports/screenshots", exist_ok=True)
    os.makedirs("reports/logs", exist_ok=True)


@pytest.fixture(scope="function", autouse=True)
def record_video(request):
    """
    Records video for all tests but only attaches to Allure report for failed tests.
    Videos for passed tests are automatically deleted to save storage space.
    """
    driver = None
    if "logged_in_app_driver" in request.fixturenames:
        context = request.getfixturevalue("logged_in_app_driver")
        manager = context.get("_manager") if isinstance(context, dict) else None
        if manager:
            try:
                manager.ensure_ready_for_test(request.node)
            except Exception as exc:
                log.warning(f"Failed to prepare session driver for recording: {exc}")
        if isinstance(context, dict):
            driver = context.get("driver", None)
    _env = request.config.getoption("--env")
    is_browser_stack = _env == "browserstack"

    if not should_record_video(driver, is_browser_stack):
        yield
        return

    test_name = request.node.name
    retry_count = request.node.execution_count if hasattr(request.node, "execution_count") else 0
    unique_id = build_unique_video_name(test_name, retry_count)
    video_folder = "reports/videos"

    driver.start_recording_screen()
    yield

    video_file = save_recording(driver, video_folder, unique_id)

    # Store video path with unique identifier
    request.node._video_path = video_file
    request.node._video_name = unique_id


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()
    setattr(item, f"rep_{rep.when}", rep)

    # Take screenshot for every test (pass or fail) during test execution phase
    if rep.when == "call":
        env = item.config.getoption("--env")
        driver_context = reporting_utils.resolve_driver_context(item)

        if driver_context.driver:
            browserstack_utils.update_test_name(driver_context.driver, item.name, env, log)
            retry_count = reporting_utils.extract_retry_count(rep)
            reporting_utils.capture_screenshot_artifact(
                driver_context.driver, item.name, retry_count, log
            )

            status, reason = reporting_utils.determine_status_and_reason(rep)
            if driver_context.is_function_scope:
                browserstack_utils.update_function_scope_status(
                    driver_context.driver, item.name, status, reason, env, log
                )

        reporting_utils.handle_session_restart(driver_context.manager, item.name, rep, log)

    # Attach video only for failed tests after teardown
    if rep.when == "teardown":
        reporting_utils.attach_video_artifact(item, rep, log)


def pytest_runtest_call(item):
    """Called when each test runs"""
    log.info(f"Running: {item.name}")


def pytest_runtest_teardown(item, nextitem):
    """Called after each test completes"""
    global _current_test_name
    log.info(f"***** Setting down: {item.name}")

    # Mark test completion on BrowserStack
    env = item.config.getoption("--env")
    if env == "browserstack":
        driver = None

        # Get driver from appropriate fixture
        if "app_driver" in item.fixturenames:
            try:
                if hasattr(item, "funcargs") and "app_driver" in item.funcargs:
                    app_driver_fixture = item.funcargs["app_driver"]
                    if app_driver_fixture and "driver" in app_driver_fixture:
                        driver = app_driver_fixture["driver"]
            except Exception:
                pass

        if driver:
            # Determine test outcome
            status = "passed"
            reason = "Test completed successfully"

            if hasattr(item, "rep_call") and item.rep_call.failed:
                status = "failed"
                reason = str(item.rep_call.longrepr)[:200]  # Limit reason length

            browserstack_utils.mark_test_end(driver, item.name, status, reason, env, log)

    # Reset current test name
    _current_test_name = None


@pytest.hookimpl(tryfirst=True)
def pytest_sessionstart(session):
    """Before tests start, copy history if available."""
    reporting_utils.copy_allure_history(ALLURE_REPORT_DIR, ALLURE_RESULTS_DIR)


@pytest.hookimpl(trylast=True)
def pytest_sessionfinish(session, exitstatus):
    """After tests finish, generate report with history."""
    log.info(f"Test session finished with exit code: {exitstatus}")
    reporting_utils.generate_allure_report(ALLURE_RESULTS_DIR, ALLURE_REPORT_DIR, log)
