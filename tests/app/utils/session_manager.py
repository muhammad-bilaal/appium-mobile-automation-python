import json
from typing import Optional

from tests.app.drivers.driver_factory import get_driver
from tests.app.factories.page_factory import get_login_page
from tests.app.pages.base.base_page import BasePage


class SessionDriverManager:
    def __init__(self, request, logger, platform: str, env: str, username: Optional[str]):
        self.request = request
        self.logger = logger
        self.platform = platform
        self.env = env
        self.username = username
        self._session_failed = False
        self._driver = None
        self._session_index = 0
        self._current_user = None

        self.context = {
            "platform": platform,
            "logger": logger,
            "_manager": self,
            "restart": self.restart_session,
            "restart_session": self.restart_session,
            "request_restart": self.restart_session,
        }

    @staticmethod
    def _limit_reason(reason, default_message):
        message = reason or default_message
        message = str(message)
        return message[:200]

    def _build_session_name(self, username, note=None):
        parts = [self.request.node.name or "session"]
        parts.append(f"user:{username}")
        parts.append(f"session-{self._session_index}")
        if note:
            parts.append(note)
        return " :: ".join(parts)

    def _start_new_session(self, username, note=None):
        self._session_index += 1
        session_name = self._build_session_name(username=username, note=note)
        self.logger.info(
            "Starting logged-in driver session '%s' on %s via %s",
            session_name,
            self.platform.upper(),
            self.env.upper(),
        )

        driver = get_driver(platform=self.platform, test_name=session_name, env=self.env)
        BasePage.init_base(driver, self.logger, self.platform)
        login_page = get_login_page(platform=self.platform, driver=driver, logger=self.logger)
        login_page.login_user(username=username)

        self._driver = driver
        self._current_user = username
        self.context["driver"] = driver

    def restart_session(self, *, failing_test=None, attempt=None, reason=None):
        self._mark_session_failed()

        attempt_index = None
        if attempt is not None:
            try:
                attempt_index = int(attempt)
            except (TypeError, ValueError):
                attempt_index = None

        limited_reason = self._limit_reason(
            reason, default_message="Test failure triggered restart"
        )

        attempt_text = f" (attempt {attempt_index + 1})" if attempt_index is not None else ""
        self.logger.info(
            "Restarting logged-in driver session after failure in '%s'%s",
            failing_test or "unknown test",
            attempt_text,
        )

        username = self._current_user or self.username

        self._teardown_current_driver(
            status="failed",
            reason=f"{failing_test or 'Unknown test'}: {limited_reason}",
            annotate=True,
        )

        next_note = None
        if failing_test:
            if attempt_index is not None:
                next_note = f"restart-after:{failing_test}-retry-{attempt_index + 1}"
            else:
                next_note = f"restart-after:{failing_test}"
        else:
            next_note = "restart-after-failure"

        self._start_new_session(username=username, note=next_note)

    def request_restart(self, *, failing_test=None, attempt=None, reason=None):
        return self.restart_session(failing_test=failing_test, attempt=attempt, reason=reason)

    def ensure_ready_for_test(self, item):
        username = _resolve_username_from_item(item, default_username=self.username)

        if self._driver is None:
            self._start_new_session(username=username, note=f"init-for:{item.name}")
            return

        if not self._current_user:
            self._current_user = username
        elif self._current_user != username:
            self.logger.info(
                "Login session already running for %s; ignoring switch request to %s",
                self._current_user,
                username,
            )

    def finalize_session(self):
        status = "failed" if self._session_failed else "passed"
        reason = (
            "One or more tests failed in this session"
            if self._session_failed
            else "Session completed successfully"
        )
        self._teardown_current_driver(status=status, reason=reason, annotate=True)

    def _mark_session_failed(self):
        if self._session_failed:
            return
        self._session_failed = True

    def _teardown_current_driver(self, status=None, reason=None, annotate=True):
        driver = self._driver
        if not driver:
            return

        status = status or "passed"
        reason_text = self._limit_reason(reason, default_message="Session completed successfully")

        if self.env == "browserstack":
            try:
                status_command = {
                    "action": "setSessionStatus",
                    "arguments": {"status": status, "reason": reason_text},
                }
                driver.execute_script(f"browserstack_executor: {json.dumps(status_command)}")
                self.logger.info("BrowserStack session marked as %s", status.upper())
            except Exception as exc:  # noqa: BLE001 - best effort
                self.logger.warning("Failed to update BrowserStack session status: %s", exc)

            if annotate:
                try:
                    annotation_command = {
                        "action": "annotate",
                        "arguments": {
                            "data": f"Session {status.upper()} — {reason_text}",
                            "level": "info",
                        },
                    }
                    driver.execute_script(
                        f"browserstack_executor: {json.dumps(annotation_command)}"
                    )
                except Exception as exc:  # noqa: BLE001 - best effort
                    self.logger.warning("Failed to annotate BrowserStack session: %s", exc)
        else:
            log_message = (
                "Tearing down local driver session after failure"
                if status == "failed"
                else "Tearing down local driver session"
            )
            self.logger.info(log_message)

        try:
            driver.quit()
        except Exception as exc:  # noqa: BLE001 - ensure cleanup continues
            self.logger.warning("Failed to quit driver: %s", exc)
        finally:
            self.context["driver"] = None
            self._driver = None
            self._current_user = None


def _resolve_username_from_item(item, default_username):
    marker = item.get_closest_marker("user")
    if marker and marker.args:
        return marker.args[0]
    return default_username
