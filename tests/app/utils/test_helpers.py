"""
Test helper utilities for UI tests.

This module provides decorators and utilities to enhance test debugging and logging.
"""

import functools
import logging
from typing import Any, Callable, Dict, Optional


def log_page_source_on_failure(driver_key: str = "driver") -> Callable:
    """
    Decorator to log page source when a test fails.

    This decorator wraps test functions and automatically logs the page source
    when an exception occurs during test execution. This helps with debugging
    by providing visibility into the application's state at the time of failure.

    Args:
        driver_key: The key in the fixture dictionary that contains the driver.
                   Defaults to "driver" for direct driver fixtures, but can be
                   set to access nested drivers (e.g., "driver" for app_driver["driver"]).

    Usage:
        @log_page_source_on_failure()
        def test_my_function(app_driver, logger):
            # Test code here
            pass

        @log_page_source_on_failure(driver_key="driver")
        def test_with_different_driver_key(driver, logger):
            # Test code here
            pass

    The decorator will:
    1. Execute the original test function
    2. If an exception occurs, log the current page source
    3. Re-raise the original exception to maintain test failure behavior
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            try:
                # Execute the original test function
                return func(*args, **kwargs)
            except Exception as e:
                # Find the driver in the arguments or fixtures
                driver = _extract_driver_from_args(args, kwargs, driver_key)

                if driver:
                    _log_page_source(driver, func.__name__, e)
                else:
                    logging.getLogger("GETTR-Logger").warning(
                        f"Could not find driver for page source logging in test: {func.__name__}"
                    )

                # Re-raise the original exception to maintain test failure
                raise

        return wrapper

    return decorator


def _extract_driver_from_args(
    args: tuple, kwargs: Dict[str, Any], driver_key: str
) -> Optional[Any]:
    """
    Extract the driver from function arguments.

    This function searches through the positional and keyword arguments
    to find the driver object that can be used for logging page source.

    Args:
        args: Positional arguments passed to the test function
        kwargs: Keyword arguments passed to the test function
        driver_key: The key to look for in fixture dictionaries

    Returns:
        The driver object if found, None otherwise
    """
    # Check keyword arguments first (most common case for fixtures)
    for key, value in kwargs.items():
        if key == driver_key:
            return value
        elif isinstance(value, dict) and driver_key in value:
            return value[driver_key]

    # Check positional arguments
    for arg in args:
        if isinstance(arg, dict) and driver_key in arg:
            return arg[driver_key]
        elif hasattr(arg, driver_key):
            # Handle cases where the driver might be an attribute
            return getattr(arg, driver_key, None)

    return None


def _log_page_source(driver: Any, test_name: str, exception: Exception) -> None:
    """
    Log the current page source for debugging purposes.

    Args:
        driver: The WebDriver/Appium driver instance
        test_name: Name of the test function for logging context
        exception: The exception that occurred (for context in logging)
    """
    try:
        logger = logging.getLogger("GETTR-Logger")

        # Log basic exception info
        logger.info(
            f"Test '{test_name}' failed with exception: {type(exception).__name__}: {exception}"
        )

        # Log page source
        logger.info(f"Logging page source for failed test: {test_name}")
        page_source = driver.page_source

        # Log key indicators that might help with debugging
        logger.info(f"Page source length: {len(page_source)} characters")

        # Check for common error indicators in the page source
        error_indicators = [
            "error",
            "Error",
            "ERROR",
            "exception",
            "Exception",
            "EXCEPTION",
            "failed",
            "Failed",
            "FAILED",
            "invalid",
            "Invalid",
            "INVALID",
            "no account",
            "No account",
            "NO ACCOUNT",
            "that information",
            "That information",
            "THAT INFORMATION",
        ]

        found_indicators = []
        for indicator in error_indicators:
            if indicator.lower() in page_source.lower():
                found_indicators.append(indicator)

        if found_indicators:
            logger.info(
                f"Found potential error indicators in page source: {', '.join(found_indicators)}"
            )
        else:
            logger.info("No common error indicators found in page source")

        # Log a snippet of the page source (first 1000 characters)
        source_snippet = page_source[:1000] + ("..." if len(page_source) > 1000 else "")
        logger.info(f"Page source snippet: {source_snippet}")

    except Exception as logging_error:
        logger = logging.getLogger("GETTR-Logger")
        logger.warning(f"Failed to log page source for test '{test_name}': {logging_error}")


def page_source_logger(driver_key: str = "driver") -> Callable:
    """
    Convenience decorator specifically for tests using app_driver fixture.

    This is a specialized version of log_page_source_on_failure that works
    specifically with the app_driver fixture pattern used in UI tests.

    Args:
        driver_key: The key in app_driver dict that contains the driver (default: "driver")

    Usage:
        @page_source_logger()
        def test_my_function(app_driver, logger):
            driver = app_driver["driver"]
            # Test code here
            pass
    """
    return log_page_source_on_failure(driver_key)
