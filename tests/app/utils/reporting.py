import logging
import os
import shutil
import subprocess
import uuid
from datetime import datetime
from typing import NamedTuple, Optional

import allure


def copy_allure_history(report_dir: str, results_dir: str) -> None:
    """Copy the history directory from existing report into the next run."""
    history_src = os.path.join(report_dir, "history")
    history_dst = os.path.join(results_dir, "history")
    if os.path.exists(history_src):
        shutil.copytree(history_src, history_dst, dirs_exist_ok=True)


def generate_allure_report(results_dir: str, report_dir: str, logger: logging.Logger) -> None:
    """Generate Allure report (best effort)."""
    try:
        result = subprocess.run(["allure", "--version"], capture_output=True, text=True, timeout=10)
        if result.returncode != 0:
            raise FileNotFoundError("Allure CLI not found")

        subprocess.run(
            ["allure", "generate", results_dir, "--clean", "-o", report_dir],
            check=True,
            timeout=60,
        )
        logger.info("Allure report generated successfully at: %s", report_dir)
    except FileNotFoundError:
        logger.info("Allure CLI not installed - skipping report generation")
        logger.info(
            "To enable Allure reports, install Allure CLI: https://docs.qameta.io/allure/#_installing_a_commandline"
        )
    except subprocess.TimeoutExpired:
        logger.warning("Allure report generation timed out")
    except subprocess.CalledProcessError as exc:
        logger.warning("Allure report generation failed with exit code %s", exc.returncode)
    except Exception as exc:  # noqa: BLE001 - best effort
        logger.warning("Unexpected error during Allure report generation: %s", exc)


class DriverContext(NamedTuple):
    driver: Optional[object]
    manager: Optional[object]
    is_function_scope: bool


def resolve_driver_context(item) -> DriverContext:
    """Find the active driver and manager associated with the current test item."""
    driver = None
    manager = None
    is_function_scope = False

    funcargs = getattr(item, "funcargs", {})

    if "app_driver" in funcargs:
        app_driver_fixture = funcargs["app_driver"]
        driver_candidate = (
            app_driver_fixture.get("driver")
            if isinstance(app_driver_fixture, dict)
            else getattr(app_driver_fixture, "driver", None)
        )
        if driver_candidate:
            driver = driver_candidate
            is_function_scope = True

    if "logged_in_app_driver" in funcargs:
        session_fixture = funcargs["logged_in_app_driver"]
        if isinstance(session_fixture, dict):
            manager = session_fixture.get("_manager")
            session_driver = session_fixture.get("driver")
            if session_driver and not driver:
                driver = session_driver

    return DriverContext(driver=driver, manager=manager, is_function_scope=is_function_scope)


def extract_retry_count(report) -> int:
    """Safely extract retry counter from pytest report objects."""
    if report is None:
        return 0
    raw_retry = getattr(report, "rerun", 0)
    try:
        return int(raw_retry)
    except (TypeError, ValueError):
        return 0


def determine_status_and_reason(report) -> tuple[str, str]:
    """Derive BrowserStack status and reason text from a pytest report."""
    status = "passed" if report.passed else "failed"
    reason = str(report.longrepr) if report.failed else "Test completed successfully"
    return status, reason


def _build_attempt_suffix(retry_count: int) -> str:
    return f" (Attempt {retry_count + 1})" if retry_count > 0 else ""


def capture_screenshot_artifact(
    driver, test_name: str, retry_count: int, logger: logging.Logger
) -> None:
    """Capture a screenshot, save it locally, and attach it to Allure."""
    unique_id = f"{test_name}_{retry_count}_{uuid.uuid4().hex[:8]}"
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    screenshot_name = f"{unique_id}_{timestamp}.png"
    screenshot_path = os.path.join("reports/screenshots", screenshot_name)

    try:
        driver.save_screenshot(screenshot_path)
        attempt_info = _build_attempt_suffix(retry_count)
        with open(screenshot_path, "rb") as file:
            allure.attach(
                file.read(),
                name=f"Screenshot - {test_name}{attempt_info}",
                attachment_type=allure.attachment_type.PNG,
            )
    except Exception as exc:  # noqa: BLE001 - best effort
        logger.warning("Failed to capture screenshot: %s", exc)


def handle_session_restart(manager, test_name: str, report, logger: logging.Logger) -> None:
    """Request a session restart when a failure occurs in session-scoped fixtures."""
    if not manager:
        return

    is_expected_failure = getattr(report, "wasxfail", False)
    if not report.failed or is_expected_failure:
        return

    restart_reason = str(report.longrepr) if report.longrepr else "Test failure"
    try:
        manager.request_restart(
            failing_test=test_name,
            attempt=getattr(report, "rerun", None),
            reason=restart_reason,
        )
    except Exception as exc:  # noqa: BLE001 - best effort
        logger.warning("Failed to flag logged_in_app_driver session for restart: %s", exc)


def attach_video_artifact(item, _teardown_report, logger: logging.Logger) -> None:
    """Attach or clean up recorded videos at the end of each test."""
    video_path = getattr(item, "_video_path", None)
    if not video_path or not os.path.exists(video_path):
        return

    call_report = getattr(item, "rep_call", None)
    test_failed = bool(call_report and call_report.failed)
    retry_count = extract_retry_count(call_report)
    attempt_info = _build_attempt_suffix(retry_count)

    if test_failed:
        try:
            with open(video_path, "rb") as video_file:
                allure.attach(
                    video_file.read(),
                    name=f"Video - {item.name}{attempt_info}",
                    attachment_type=allure.attachment_type.MP4,
                    extension="mp4",
                )
            logger.info("Video attached to Allure report for failed test: %s", item.name)
        except Exception as exc:  # noqa: BLE001 - best effort
            logger.error("Failed to attach video: %s", exc)
    else:
        try:
            os.remove(video_path)
            logger.info("Video deleted for passed test: %s (space optimization)", item.name)
        except Exception as exc:  # noqa: BLE001 - best effort
            logger.warning("Failed to delete video for passed test: %s", exc)
