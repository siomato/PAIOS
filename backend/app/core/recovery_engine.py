# app/core/recovery_engine.py
# ============================================================
# PAIOS RECOVERY ENGINE
# Action-level recovery only.
#
# ExecutionEngine owns the plan loop.
# Replanner owns replacement-plan generation.
# RecoveryEngine owns retry/reset recovery for one action.
# ============================================================

from app.core.action_executor import action_executor
from app.tools.browser_automation import browser_automation
from app.tools.browser_worker import browser_worker
import time


class RecoveryEngine:

    MAX_RETRIES = 3
    RETRY_DELAY = 1.0

    def __init__(self):
        print("🛡️ RECOVERY ENGINE MODULE LOADED 🛡️")

    # =========================================================
    # STATE HELPERS
    # =========================================================

    def _set_state(self, state, attribute, value):
        if state is None:
            return

        try:
            setter = getattr(
                state,
                f"set_{attribute}",
                None
            )

            if callable(setter):
                setter(value)
                return

        except Exception:
            pass

        try:
            setattr(state, attribute, value)
        except Exception:
            pass

    def _increment_retries(self, state):
        if state is None:
            return

        try:
            current = getattr(
                state,
                "retry_count",
                getattr(state, "retries", 0)
            )

            if isinstance(current, int):
                if hasattr(state, "retry_count"):
                    setattr(state, "retry_count", current + 1)
                elif hasattr(state, "retries"):
                    setattr(state, "retries", current + 1)

        except Exception:
            pass

    # =========================================================
    # ERROR CLASSIFICATION
    # =========================================================

    def _classify_error(self, result):
        if not isinstance(result, dict):
            return "unknown"

        error = str(
            result.get("error", "")
        ).lower()

        browser_errors = (
            "browser",
            "playwright",
            "page",
            "context",
            "target page",
            "session",
            "closed",
            "connection",
            "cannot switch to a different thread",
            "different thread",
            "thread",
            "sync_api",
            "event loop",
            "greenlet",
        )

        if any(word in error for word in browser_errors):
            return "browser"

        target_errors = (
            "target",
            "element",
            "locator",
            "resolve",
            "not found",
            "could not resolve",
            "button not found",
        )

        if any(word in error for word in target_errors):
            return "target"

        if (
            "timeout" in error
            or "timed out" in error
        ):
            return "timeout"

        network_errors = (
            "network",
            "navigation",
            "net::",
            "dns",
            "connection refused",
            "connection reset",
            "err_name_not_resolved",
        )

        if any(word in error for word in network_errors):
            return "network"

        if (
            "unknown action" in error
            or "unsupported action" in error
        ):
            return "action"

        return "unknown"

    # =========================================================
    # RECOVERABILITY
    # =========================================================

    def _is_recoverable(self, result):
        if not isinstance(result, dict):
            return True

        if result.get("status") == "success":
            return False

        if result.get("recoverable") is False:
            return False

        if result.get("recoverable") is True:
            return True

        return self._classify_error(result) != "action"

    # =========================================================
    # WAIT
    # =========================================================

    def _wait(self, seconds=None):
        time.sleep(
            self.RETRY_DELAY
            if seconds is None
            else max(0, float(seconds))
        )

    # =========================================================
    # BROWSER RESET
    # =========================================================

    def _reset_browser(self):
        print("\n♻️ RESETTING PLAYWRIGHT SESSION")

        try:
            result = browser_worker.execute(
                browser_automation.close
            )

            print(
                f"🧹 Browser cleanup result: {result}"
            )

            return True

        except Exception as exc:
            print(
                f"⚠️ Browser cleanup failed: {exc}"
            )

            try:
                cleanup = getattr(
                    browser_automation,
                    "_cleanup",
                    None
                )

                if callable(cleanup):
                    cleanup()
                    print(
                        "🧹 Emergency browser cleanup completed."
                    )
                    return True

            except Exception as cleanup_error:
                print(
                    f"⚠️ Emergency cleanup failed: "
                    f"{cleanup_error}"
                )

            return False

    # =========================================================
    # COMPATIBILITY EXECUTE ADAPTER
    # =========================================================

    def execute(self, actions, state=None):
        """
        Compatibility adapter for older callers that still invoke
        recovery_engine.execute(...).

        The RecoveryEngine does not own replanning. Actual action/plan
        execution is delegated to ActionExecutor.
        """
        return action_executor.execute(
            actions,
            state=state
        )

    # =========================================================
    # SINGLE ACTION RECOVERY
    # =========================================================

    def recover(
        self,
        failed_action,
        error=None,
        state=None,
        max_retries=None,
    ):
        """
        Recover one failed action.

        IMPORTANT:
        This method never replans an entire execution plan.
        ExecutionEngine is the only owner of plan/replan flow.
        """

        if not isinstance(failed_action, dict):
            return {
                "status": "failed",
                "error": "Failed action must be a dictionary.",
                "recovered": False,
            }

        action = str(
            failed_action.get("action", "")
        ).strip().lower()

        if not action:
            return {
                "status": "failed",
                "error": "Failed action has no action type.",
                "recovered": False,
            }

        retries = (
            self.MAX_RETRIES
            if max_retries is None
            else max(0, int(max_retries))
        )

        original_error = str(
            error
            if error is not None
            else "Action failed."
        )

        error_type = self._classify_error({
            "error": original_error
        })

        print("\n======================================")
        print("🛡️ ACTION RECOVERY")
        print("======================================")
        print(f"Action: {failed_action}")
        print(f"Error: {original_error}")
        print(f"Error type: {error_type}")
        print(f"Retries available: {retries}")

        self._set_state(
            state,
            "status",
            "recovering"
        )

        # Non-recoverable actions should go directly back to
        # ExecutionEngine so it can invoke the Replanner.
        if action in {
            "unknown",
            ""
        }:
            return {
                "status": "failed",
                "error": original_error,
                "recovered": False,
                "recoverable": False,
            }

        last_result = {
            "status": "failed",
            "action": action,
            "error": original_error,
            "recoverable": True,
        }

        for attempt in range(1, retries + 1):

            print(
                f"\n🔁 Recovery attempt "
                f"{attempt}/{retries}"
            )

            self._increment_retries(state)

            # -------------------------------------------------
            # Browser session failures
            # -------------------------------------------------

            if error_type == "browser":

                reset_ok = self._reset_browser()

                if not reset_ok:
                    self._wait()

                else:
                    # Browser reset changes the session, so give
                    # the browser worker a moment before retry.
                    self._wait(0.5)

            # -------------------------------------------------
            # Network/navigation failures
            # -------------------------------------------------

            elif error_type == "network":

                self._wait()

            # -------------------------------------------------
            # Timeout/target failures
            # -------------------------------------------------

            elif error_type in {
                "timeout",
                "target"
            }:

                self._wait(0.5)

            else:
                self._wait(0.25)

            try:

                result = action_executor.execute_action(
                    failed_action,
                    state=state,
                    step_number=1
                )

            except Exception as exc:

                result = {
                    "status": "failed",
                    "action": action,
                    "error": str(exc),
                    "recoverable": True
                }

            last_result = result

            if (
                isinstance(result, dict)
                and result.get("status") == "success"
            ):

                self._set_state(
                    state,
                    "status",
                    "executing"
                )

                return {
                    "status": "success",
                    "recovered": True,
                    "attempt": attempt,
                    "action": action,
                    "result": result,
                }

            # Reclassify because the retry may have produced a
            # more useful error.
            error_type = self._classify_error(
                result
            )

            if not self._is_recoverable(result):
                break

        self._set_state(
            state,
            "status",
            "failed"
        )

        return {
            "status": "failed",
            "recovered": False,
            "action": action,
            "attempts": retries,
            "error": (
                last_result.get(
                    "error",
                    original_error
                )
                if isinstance(last_result, dict)
                else original_error
            ),
            "recoverable": True,
            "last_result": last_result,
        }


# ============================================================
# GLOBAL INSTANCE
# ============================================================

recovery_engine = RecoveryEngine()
