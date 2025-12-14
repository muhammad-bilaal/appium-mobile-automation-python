from __future__ import annotations

import json
import logging
import os
import time
import traceback
import requests
from functools import lru_cache
from typing import TypedDict
from datetime import datetime


def _is_browserstack(env: str) -> bool:
    return env == "browserstack"


def mark_test_start(driver, test_name: str, env: str, logger: logging.Logger) -> None:
    """Mark the start of an individual test on BrowserStack."""
    if not _is_browserstack(env):
        return

    try:
        max_retries = 3
        for attempt in range(max_retries):
            try:
                command = {
                    "action": "annotate",
                    "arguments": {
                        "data": f"Individual Test Started: {test_name}",
                        "level": "info",
                    },
                }
                logger.info("mark_test_start Updating BrowserStack session %s", test_name)
                driver.execute_script(f"browserstack_executor: {json.dumps(command)}")
                break
            except Exception as exc:  # noqa: BLE001 - log and retry
                logger.warning("Failed to mark test start (attempt %s): %s", attempt + 1, exc)
                if attempt < max_retries - 1:
                    time.sleep(1)
                else:
                    logger.error("Failed to mark test start after %s attempts", max_retries)
    except Exception as exc:  # noqa: BLE001 - best effort operation
        logger.warning("Failed to mark test start on BrowserStack: %s", exc)


def update_test_name(driver, test_name: str, env: str, logger: logging.Logger) -> None:
    """Update the BrowserStack session name and add a start annotation."""
    if not _is_browserstack(env):
        return

    try:
        session_id = getattr(driver, "session_id", None)
        if not session_id:
            logger.warning("No session ID available for BrowserStack update")
            return

        time.sleep(2)
        logger.info(
            "Updating BrowserStack session name to: %s for session: %s",
            test_name,
            session_id,
        )
        max_retries = 3
        for attempt in range(max_retries):
            try:
                command = {"action": "setSessionName", "arguments": {"name": test_name}}
                driver.execute_script(f"browserstack_executor: {json.dumps(command)}")
                logger.info("Successfully sent setSessionName command for: %s", test_name)
                break
            except Exception as exc:  # noqa: BLE001 - retry
                logger.warning("Failed to update session name (attempt %s): %s", attempt + 1, exc)
                if attempt < max_retries - 1:
                    time.sleep(1)
                else:
                    logger.error(
                        "Failed to update BrowserStack session name after %s attempts",
                        max_retries,
                    )

        for attempt in range(max_retries):
            try:
                annotation_command = {
                    "action": "annotate",
                    "arguments": {
                        "data": f"Starting Individual Test: {test_name}",
                        "level": "info",
                    },
                }
                driver.execute_script(f"browserstack_executor: {json.dumps(annotation_command)}")
                break
            except Exception as exc:  # noqa: BLE001 - retry
                logger.warning(
                    "Failed to add start annotation (attempt %s): %s",
                    attempt + 1,
                    exc,
                )
                if attempt < max_retries - 1:
                    time.sleep(1)
                else:
                    logger.error("Failed to add start annotation after %s attempts", max_retries)
    except Exception:  # noqa: BLE001 - need traceback for debugging
        logger.warning(
            "Failed to update test name on BrowserStack:\n%s",
            traceback.format_exc(),
        )


def mark_test_end(
    driver,
    test_name: str,
    status: str,
    reason: str,
    env: str,
    logger: logging.Logger,
) -> None:
    """Mark the completion of an individual test on BrowserStack."""
    if not _is_browserstack(env):
        return

    try:
        command = {
            "action": "annotate",
            "arguments": {
                "data": f"Test {status.upper()}: {test_name} - Session terminating",
                "level": "info",
            },
        }
        driver.execute_script(f"browserstack_executor: {json.dumps(command)}")
        status_command = {
            "action": "setSessionStatus",
            "arguments": {"status": status, "reason": f"{test_name}: {reason}"},
        }
        driver.execute_script(f"browserstack_executor: {json.dumps(status_command)}")
    except Exception as exc:  # noqa: BLE001 - best effort
        logger.warning("Failed to mark test end on BrowserStack: %s", exc)


def update_function_scope_status(
    driver,
    test_name: str,
    status: str,
    reason: str,
    env: str,
    logger: logging.Logger,
) -> None:
    """Update BrowserStack status for function-scoped sessions."""
    if not _is_browserstack(env):
        return

    try:
        status_command = {
            "action": "setSessionStatus",
            "arguments": {"status": status, "reason": f"{test_name}: {reason}"},
        }
        driver.execute_script(f"browserstack_executor: {json.dumps(status_command)}")
    except Exception as exc:  # noqa: BLE001 - best effort
        logger.warning("Failed to update BrowserStack status: %s", exc)


class BrowserStackApp(TypedDict):
    """Type definition for BrowserStack app response."""

    app_name: str
    app_version: str
    app_url: str
    app_id: str
    uploaded_at: str
    custom_id: str | None
    shareable_id: str | None


@lru_cache(maxsize=10)
def _get_app_id_cached(platform: str, version: str) -> tuple[str, str]:
    """
    Internal cached function to fetch app ID from BrowserStack API.

    This function is cached to avoid redundant API calls when running multiple test cases
    with the same platform and version combination.

    Args:
        platform: 'android' or 'ios'
        version: Version string from environment variable, or 'latest' to fetch most recent

    Returns:
        Tuple of (app_url, app_version) - e.g., ('bs://...', '1.0.0')

    Raises:
        ValueError: If API call fails, credentials missing, or no app found
    """
    # Use module-level logger for cached function
    module_logger = logging.getLogger(__name__)

    credentials = _get_browserstack_credentials()
    url = "https://api-cloud.browserstack.com/app-automate/recent_apps"

    try:
        apps = _fetch_apps_from_api(url, credentials, module_logger)
        platform_apps = _filter_apps_by_platform(apps, platform)

        if not platform_apps:
            raise ValueError(f"No apps found for platform: {platform}")

        # If version is 'latest', skip exact match and get most recent
        if version.lower() == "latest":
            latest_app = max(platform_apps, key=lambda app: _parse_timestamp(app["uploaded_at"]))
            module_logger.info(
                f"Fetching latest app for {platform}: version {latest_app['app_version']}, "
                f"URL: {latest_app['app_url']}"
            )
            return latest_app["app_url"], latest_app["app_version"]

        # Try exact version match first
        matched_app = _find_app_by_version(platform_apps, version)
        if matched_app:
            module_logger.info(
                f"Found matching app for {platform} version {version}: {matched_app['app_url']}"
            )
            return matched_app["app_url"], matched_app["app_version"]

        # Fall back to most recent app
        return _get_most_recent_app(platform_apps, platform, version, module_logger)

    except requests.RequestException as e:
        module_logger.error(f"Failed to fetch apps from BrowserStack API: {e}")
        raise ValueError(f"BrowserStack API request failed: {e}")


def get_app_id_from_browserstack_api(
    platform: str, version: str, logger: logging.Logger
) -> tuple[str, str]:
    """
    Fetch the app ID for the given platform and version from BrowserStack API.

    Results are cached per (platform, version) combination to avoid redundant API calls
    when running multiple test cases. The actual API call is delegated to a cached
    internal function.

    Args:
        platform: 'android' or 'ios'
        version: Version string from environment variable, or 'latest' to fetch most recent app
        logger: Logger instance (used for logging cache hits)

    Returns:
        Tuple of (app_url, app_version) - e.g., ('bs://...', '1.0.0')

    Raises:
        ValueError: If API call fails, credentials missing, or no app found
    """
    # Check if result is already cached
    cache_info = _get_app_id_cached.cache_info()
    logger.info(
        f"BrowserStack API cache stats - hits: {cache_info.hits}, "
        f"misses: {cache_info.misses}, size: {cache_info.currsize}"
    )

    return _get_app_id_cached(platform, version)


def _get_browserstack_credentials() -> tuple[str, str]:
    """Get BrowserStack credentials from environment variables."""
    username = os.getenv("BROWSERSTACK_USERNAME")
    access_key = os.getenv("BROWSERSTACK_ACCESS_KEY")

    if not username or not access_key:
        raise ValueError("BrowserStack credentials not found in environment variables")

    return username, access_key


def _fetch_apps_from_api(
    url: str, credentials: tuple[str, str], logger: logging.Logger
) -> list[BrowserStackApp]:
    """Fetch apps from BrowserStack API."""
    response = requests.get(url, auth=credentials, timeout=30)
    response.raise_for_status()
    apps = response.json()
    logger.info(f"Retrieved {len(apps)} apps from BrowserStack API")
    return apps


def _filter_apps_by_platform(apps: list[BrowserStackApp], platform: str) -> list[BrowserStackApp]:
    """
    Filter apps by platform based on file extension.

    Platform is determined by the app_name extension:
    - android: .apk files
    - ios: .ipa files
    """
    PLATFORM_EXTENSIONS = {
        "android": ".apk",
        "ios": ".ipa",
    }

    extension = PLATFORM_EXTENSIONS.get(platform)
    if not extension:
        raise ValueError(f"Invalid platform: {platform}. Must be 'android' or 'ios'")

    return [app for app in apps if app["app_name"].lower().endswith(extension)]


def _find_app_by_version(apps: list[BrowserStackApp], version: str) -> BrowserStackApp | None:
    """Find app with exact version match."""
    for app in apps:
        if app["app_version"] == version:
            return app
    return None


def _get_most_recent_app(
    apps: list[BrowserStackApp], platform: str, requested_version: str, logger: logging.Logger
) -> tuple[str, str]:
    """
    Get the most recently uploaded app based on uploaded_at timestamp.

    Raises:
        ValueError: If no suitable app found
    """
    if not apps:
        raise ValueError(f"No suitable app found for {platform} version {requested_version}")

    # Sort by uploaded_at timestamp and get the most recent
    latest_app = max(apps, key=lambda app: _parse_timestamp(app["uploaded_at"]))

    logger.warning(
        f"No exact version match for {requested_version}, "
        f"using latest app version {latest_app['app_version']}: {latest_app['app_url']}"
    )
    return latest_app["app_url"], latest_app["app_version"]


def _parse_timestamp(timestamp_str: str) -> datetime:
    """
    Parse BrowserStack timestamp format: '2025-11-03 04:49:30 UTC'
    Falls back to epoch if parsing fails.
    """
    try:
        return datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S %Z")
    except (ValueError, TypeError):
        return datetime.min


def finalize_function_scope_session(
    driver,
    request,
    env: str,
    logger: logging.Logger,
    test_name: str,
) -> None:
    """Wrap up a function-scoped BrowserStack session."""
    if not _is_browserstack(env):
        return

    status = "passed"
    reason = "Test completed successfully"

    report = getattr(request.node, "rep_call", None)
    if report and report.failed:
        status = "failed"
        reason = str(report.longrepr)[:200]

    try:
        mark_test_end(driver, test_name, status, reason, env, logger)
        logger.info("BrowserStack session terminated for test: %s", test_name)
    except Exception as exc:  # noqa: BLE001 - best effort
        logger.warning("Failed to properly terminate BrowserStack session: %s", exc)
