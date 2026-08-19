# ============================================================
# app/core/recovery_engine.py
#
# PAIOS RECOVERY ENGINE
#
# STEP 4
# Real browser/session recovery
# ============================================================

from app.core.action_executor import action_executor
from app.core.replanner import replanner

from app.tools.browser_automation import browser_automation
from app.tools.browser_worker import browser_worker

import time


class RecoveryEngine:

    # ========================================================
    # CONFIGURATION
    # ========================================================

    MAX_RETRIES = 2
    RETRY_DELAY = 1.0
    MAX_REPLANS = 2

    # ========================================================
    # INITIALIZATION
    # ========================================================

    def __init__(self):

        print(
            "🛡️ RECOVERY ENGINE MODULE LOADED 🛡️"
        )

    # ========================================================
    # STATE HELPERS
    # ========================================================

    def _set_state(
        self,
        state,
        attribute,
        value
    ):

        if state is None:
            return

        try:

            setter = getattr(
                state,
                f"set_{attribute}",
                None
            )

            if callable(setter):

                setter(
                    value
                )

                return

        except Exception:
            pass

        try:

            setattr(
                state,
                attribute,
                value
            )

        except Exception:
            pass

    # ========================================================

    def _increment_retries(
        self,
        state
    ):

        if state is None:
            return

        try:

            current = getattr(
                state,
                "retries",
                0
            )

            if isinstance(
                current,
                int
            ):

                setattr(
                    state,
                    "retries",
                    current + 1
                )

        except Exception:
            pass

    # ========================================================

    def _increment_replans(
        self,
        state
    ):

        if state is None:
            return

        try:

            current = getattr(
                state,
                "replans",
                0
            )

            if isinstance(
                current,
                int
            ):

                setattr(
                    state,
                    "replans",
                    current + 1
                )

        except Exception:
            pass

    # ========================================================

    def _set_current_step(
        self,
        state,
        step
    ):

        self._set_state(
            state,
            "current_step",
            step
        )

    # ========================================================

    def _set_failed_step(
        self,
        state,
        step
    ):

        self._set_state(
            state,
            "failed_step",
            step
        )

    # ========================================================
    # ERROR CLASSIFICATION
    # ========================================================

    def _classify_error(
        self,
        result
    ):

        if not isinstance(
            result,
            dict
        ):

            return "unknown"

        error = str(
            result.get(
                "error",
                ""
            )
        ).lower()

        # ----------------------------------------------------
        # THREAD / PLAYWRIGHT ERRORS
        # ----------------------------------------------------

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

        if any(
            word in error
            for word in browser_errors
        ):

            return "browser"

        # ----------------------------------------------------
        # TARGET
        # ----------------------------------------------------

        target_errors = (

            "target",

            "element",

            "locator",

            "resolve",

            "not found",

            "could not resolve",

            "button not found",

        )

        if any(
            word in error
            for word in target_errors
        ):

            return "target"

        # ----------------------------------------------------
        # TIMEOUT
        # ----------------------------------------------------

        if (
            "timeout" in error
            or
            "timed out" in error
        ):

            return "timeout"

        # ----------------------------------------------------
        # NETWORK
        # ----------------------------------------------------

        network_errors = (

            "network",

            "navigation",

            "net::",

            "dns",

            "connection refused",

            "connection reset",

        )

        if any(
            word in error
            for word in network_errors
        ):

            return "network"

        # ----------------------------------------------------
        # UNKNOWN ACTION
        # ----------------------------------------------------

        if "unknown action" in error or "unsupported action" in error:
            return "action"

        # ----------------------------------------------------
        # UNKNOWN
        # ----------------------------------------------------

        return "unknown"

    # ========================================================
    # RECOVERABILITY
    # ========================================================

    def _is_recoverable(
        self,
        result
    ):

        if not isinstance(
            result,
            dict
        ):

            return True

        if result.get(
            "status"
        ) == "success":

            return False

        if result.get(
            "recoverable"
        ) is False:

            return False

        return True

    # ========================================================
    # REAL BROWSER RESET
    # ========================================================

    def _reset_browser(self):

        print(
            "\n======================================"
        )

        print(
            "♻️ RESETTING PLAYWRIGHT SESSION"
        )

        print(
            "======================================"
        )

        try:

            # ------------------------------------------------
            # IMPORTANT:
            #
            # BrowserAutomation owns Playwright objects.
            #
            # Therefore cleanup itself is executed through
            # BrowserWorker.
            # ------------------------------------------------

            result = browser_worker.execute(
                browser_automation.close
            )

            print(
                f"🧹 Browser cleanup result: {result}"
            )

            print(
                "✅ Stale browser session removed."
            )

            return True

        except Exception as e:

            print(
                f"⚠️ Browser cleanup failed: {e}"
            )

            # ------------------------------------------------
            # Emergency cleanup.
            #
            # This should normally never be required.
            # ------------------------------------------------

            try:

                browser_automation._cleanup()

                print(
                    "🧹 Emergency browser cleanup completed."
                )

                return True

            except Exception as cleanup_error:

                print(
                    "❌ Emergency cleanup failed:"
                )

                print(
                    cleanup_error
                )

                return False

    # ========================================================
    # PREPARE RECOVERY
    # ========================================================

    def _prepare_recovery(
        self,
        action,
        error_type
    ):

        print(
            "\n🛠️ Preparing recovery..."
        )

        print(
            f"Recovery type: {error_type}"
        )

        # ====================================================
        # BROWSER / PLAYWRIGHT
        # ====================================================

        if error_type == "browser":

            print(
                "🌐 Browser/session issue detected."
            )

            print(
                "♻️ Destroying stale Playwright session..."
            )

            reset_success = (
                self._reset_browser()
            )

            if not reset_success:

                print(
                    "❌ Browser reset failed."
                )

                return False

            print(
                "✅ Browser reset completed."
            )

            return True

        # ====================================================
        # TARGET
        # ====================================================

        if error_type == "target":

            print(
                "🎯 Target resolution problem detected."
            )

            return True

        # ====================================================
        # TIMEOUT
        # ====================================================

        if error_type == "timeout":

            print(
                "⏳ Timeout detected."
            )

            return True

        # ====================================================
        # NETWORK
        # ====================================================

        if error_type == "network":

            print(
                "🌐 Network/navigation issue detected."
            )

            return True

        # ====================================================
        # ACTION
        # ====================================================

        if error_type == "action":

            print(
                "🧩 Invalid/unknown action detected; "
                "delegating to Replanner."
            )

            return True

        # ====================================================
        # UNKNOWN
        # ====================================================

        print(
            "❓ Unknown failure type; allowing Replanner "
            "to determine an alternative."
        )

        return True

    # ========================================================
    # WAIT
    # ========================================================

    def _wait(self):

        time.sleep(
            self.RETRY_DELAY
        )

    # ========================================================
    # EXECUTE ONE ACTION WITH RETRIES
    # ========================================================

    def execute_action(
        self,
        action,
        max_retries=None,
        state=None,
        step_number=None
    ):

        if max_retries is None:

            max_retries = (
                self.MAX_RETRIES
            )

        print(
            "\n========== RECOVERY EXECUTOR =========="
        )

        print(
            f"Action: {action}"
        )

        attempts = 0

        recovery_history = []

        last_result = None

        # ====================================================
        # CURRENT STEP
        # ====================================================

        if step_number is not None:

            self._set_current_step(
                state,
                step_number
            )

        # ====================================================
        # ATTEMPT LOOP
        # ====================================================

        while attempts <= max_retries:

            attempts += 1

            print(
                f"\n🔄 Attempt "
                f"{attempts}/{max_retries + 1}"
            )

            # ------------------------------------------------
            # EXECUTE ACTION
            # ------------------------------------------------

            try:

                result = (
                    action_executor.execute_action(
                        action,
                        state=state
                    )
                )

            except TypeError:

                # Compatibility with older executor

                try:

                    result = (
                        action_executor.execute_action(
                            action
                        )
                    )

                except Exception as e:

                    result = {
                        "status": "failed",
                        "action": action,
                        "error": str(e),
                        "recoverable": True
                    }

            except Exception as e:

                result = {
                    "status": "failed",
                    "action": action,
                    "error": str(e),
                    "recoverable": True
                }

            # ------------------------------------------------
            # Safety normalization
            # ------------------------------------------------

            if not isinstance(
                result,
                dict
            ):

                result = {
                    "status": "failed",
                    "action": action,
                    "error": str(result),
                    "recoverable": True
                }

            last_result = result

            # =================================================
            # SUCCESS
            # =================================================

            if result.get(
                "status"
            ) == "success":

                print(
                    f"✅ Action succeeded "
                    f"on attempt {attempts}."
                )

                return {
                    "status": "success",

                    "action": action,

                    "attempts": attempts,

                    "recovered":
                        attempts > 1,

                    "recovery_history":
                        recovery_history,

                    "result":
                        result,

                    "error": None
                }

            # =================================================
            # FAILURE
            # =================================================

            error_type = (
                self._classify_error(
                    result
                )
            )

            error_message = (
                result.get(
                    "error"
                )
            )

            recovery_history.append({

                "attempt":
                    attempts,

                "error":
                    error_message,

                "error_type":
                    error_type

            })

            print(
                f"❌ Attempt {attempts} failed."
            )

            print(
                f"Error type: {error_type}"
            )

            print(
                f"Reason: {error_message}"
            )

            # ------------------------------------------------
            # STATE
            # ------------------------------------------------

            self._increment_retries(
                state
            )

            self._set_failed_step(
                state,
                step_number
            )

            # =================================================
            # NON-RECOVERABLE
            # =================================================

            if not self._is_recoverable(
                result
            ):

                print(
                    "🛑 Failure marked "
                    "non-recoverable."
                )

                return {
                    "status": "failed",

                    "action": action,

                    "attempts": attempts,

                    "recovered": False,

                    "recovery_history":
                        recovery_history,

                    "result":
                        result,

                    "error":
                        error_message
                }

            # =================================================
            # RETRY LIMIT
            # =================================================

            if attempts > max_retries:

                break

            # =================================================
            # PREPARE RECOVERY
            # =================================================

            prepared = (
                self._prepare_recovery(
                    action,
                    error_type
                )
            )

            if not prepared:

                print(
                    "🛑 Recovery preparation failed."
                )

                break

            # =================================================
            # WAIT
            # =================================================

            print(
                f"⏳ Waiting "
                f"{self.RETRY_DELAY}s "
                f"before retry..."
            )

            self._wait()

        # ====================================================
        # FINAL FAILURE
        # ====================================================

        print(
            "\n❌ Recovery failed."
        )

        print(
            f"Total attempts: {attempts}"
        )

        return {

            "status": "failed",

            "action": action,

            "attempts": attempts,

            "recovered": False,

            "recovery_history":
                recovery_history,

            "result":
                last_result,

            "error":
                (
                    last_result.get(
                        "error"
                    )
                    if last_result
                    else
                    "Unknown error"
                )
        }

    # ========================================================
    # REPLAN
    # ========================================================

    def _replan(
        self,
        original_steps,
        failed_step,
        failure
    ):

        print(
            "\n======================================"
        )

        print(
            "🧠 RECOVERY → REPLANNER"
        )

        print(
            "======================================"
        )

        print(
            f"Failed step: {failed_step}"
        )

        print(
            f"Failure: {failure}"
        )

        try:

            replan_result = (
                replanner.replan(
                    original_steps,
                    failed_step,
                    failure
                )
            )

        except Exception as e:

            print(
                f"❌ Replanner error: {e}"
            )

            return {
                "status": "failed",
                "error": str(e),
                "steps": []
            }

        if not isinstance(
            replan_result,
            dict
        ):

            return {
                "status": "failed",
                "error":
                    "Invalid replanner response.",
                "steps": []
            }

        if replan_result.get(
            "status"
        ) != "success":

            return {
                "status": "failed",
                "error":
                    replan_result.get(
                        "error",
                        "Replanner failed."
                    ),
                "steps": []
            }

        new_steps = (
            replan_result.get(
                "steps",
                []
            )
        )

        if not new_steps:

            return {
                "status": "failed",
                "error":
                    "Replanner generated no steps.",
                "steps": []
            }

        print(
            "\n✅ Replanner generated a new plan."
        )

        print(
            f"Reason: "
            f"{replan_result.get('reason')}"
        )

        print(
            "\n📋 NEW PLAN"
        )

        for index, step in enumerate(
            new_steps,
            start=1
        ):

            print(
                f"{index}. {step}"
            )

        return {

            "status": "success",

            "reason":
                replan_result.get(
                    "reason"
                ),

            "steps":
                new_steps,

            "failed_step":
                failed_step
        }

    # ========================================================
    # EXECUTE COMPLETE PLAN
    # ========================================================

    def execute(
        self,
        steps,
        max_retries=None,
        state=None
    ):

        print(
            "\n======================================"
        )

        print(
            "🛡️ RECOVERY ENGINE"
        )

        print(
            "======================================"
        )

        # ====================================================
        # VALIDATE PLAN
        # ====================================================

        if not steps:

            self._set_state(
                state,
                "status",
                "failed"
            )

            return {

                "status": "failed",

                "steps": [],

                "failed_step": None,

                "error":
                    "No actions to execute.",

                "replans_used": 0,

                "replan_history": []
            }

        # ====================================================
        # INITIAL STATE
        # ====================================================

        self._set_state(
            state,
            "status",
            "executing"
        )

        self._set_current_step(
            state,
            0
        )

        # ====================================================
        # PLAN COPIES
        # ====================================================

        original_steps = list(
            steps
        )

        current_steps = list(
            steps
        )

        results = []

        replans_used = 0

        replan_history = []

        # ====================================================
        # PLAN LOOP
        # ====================================================

        while True:

            total_steps = len(
                current_steps
            )

            results = []

            print(
                f"\n📋 Executing plan with "
                f"{total_steps} steps."
            )

            plan_failed = False

            # =================================================
            # STEP LOOP
            # =================================================

            for index, action in enumerate(
                current_steps,
                start=1
            ):

                print(
                    f"\n========== "
                    f"STEP {index}/{total_steps} "
                    f"=========="
                )

                print(
                    f"Action: {action}"
                )

                self._set_current_step(
                    state,
                    index
                )

                result = (
                    self.execute_action(
                        action,
                        max_retries=max_retries,
                        state=state,
                        step_number=index
                    )
                )

                results.append({

                    "step":
                        index,

                    "action":
                        action,

                    "status":
                        result.get(
                            "status"
                        ),

                    "result":
                        result

                })

                # ---------------------------------------------
                # SUCCESS
                # ---------------------------------------------

                if result.get(
                    "status"
                ) == "success":

                    if result.get(
                        "recovered"
                    ):

                        print(
                            "♻️ Step recovered "
                            "successfully."
                        )

                    else:

                        print(
                            "✅ Step completed."
                        )

                    continue

                # ---------------------------------------------
                # FAILURE
                # ---------------------------------------------

                print(
                    f"❌ Step {index} failed "
                    "after recovery attempts."
                )

                plan_failed = True

                failed_step = index

                failure = (
                    result.get(
                        "error"
                    )
                )

                self._set_failed_step(
                    state,
                    failed_step
                )

                break

            # =================================================
            # COMPLETE SUCCESS
            # =================================================

            if not plan_failed:

                print(
                    "\n🎉 ALL STEPS COMPLETED."
                )

                self._set_state(
                    state,
                    "status",
                    "completed"
                )

                self._set_failed_step(
                    state,
                    None
                )

                return {

                    "status":
                        "success",

                    "steps":
                        results,

                    "failed_step":
                        None,

                    "error":
                        None,

                    "replans_used":
                        replans_used,

                    "replan_history":
                        replan_history
                }

            # =================================================
            # REPLAN LIMIT
            # =================================================

            if (
                replans_used
                >=
                self.MAX_REPLANS
            ):

                print(
                    "\n🛑 Maximum replanning "
                    "attempts reached."
                )

                self._set_state(
                    state,
                    "status",
                    "failed"
                )

                return {

                    "status":
                        "failed",

                    "steps":
                        results,

                    "failed_step":
                        failed_step,

                    "error":
                        failure,

                    "replans_used":
                        replans_used,

                    "replan_history":
                        replan_history
                }

            # =================================================
            # REPLAN
            # =================================================

            print(
                "\n🔁 Recovery retries exhausted."
            )

            print(
                "🧠 Sending failure to Replanner..."
            )

            replan_result = (
                self._replan(
                    original_steps,
                    failed_step,
                    failure
                )
            )

            replan_history.append({

                "replan_attempt":
                    replans_used + 1,

                "failed_step":
                    failed_step,

                "failure":
                    failure,

                "result":
                    replan_result

            })

            # =================================================
            # REPLAN FAILURE
            # =================================================

            if replan_result.get(
                "status"
            ) != "success":

                print(
                    "\n❌ Replanning failed."
                )

                self._set_state(
                    state,
                    "status",
                    "failed"
                )

                return {

                    "status":
                        "failed",

                    "steps":
                        results,

                    "failed_step":
                        failed_step,

                    "error":
                        replan_result.get(
                            "error"
                        ),

                    "replans_used":
                        replans_used,

                    "replan_history":
                        replan_history
                }

            # =================================================
            # ACCEPT NEW PLAN
            # =================================================

            replans_used += 1

            self._increment_replans(
                state
            )

            current_steps = list(
                replan_result.get(
                    "steps",
                    []
                )
            )

            if not current_steps:

                self._set_state(
                    state,
                    "status",
                    "failed"
                )

                return {

                    "status":
                        "failed",

                    "steps":
                        results,

                    "failed_step":
                        failed_step,

                    "error":
                        "Replanner returned "
                        "empty plan.",

                    "replans_used":
                        replans_used,

                    "replan_history":
                        replan_history
                }

            print(
                "\n♻️ NEW PLAN ACCEPTED."
            )

            print(
                f"Replans used: "
                f"{replans_used}/"
                f"{self.MAX_REPLANS}"
            )

            self._set_current_step(
                state,
                0
            )

            self._set_state(
                state,
                "status",
                "executing"
            )

            # ------------------------------------------------
            # Continue with new plan
            # ------------------------------------------------


# ============================================================
# GLOBAL INSTANCE
# ============================================================

recovery_engine = RecoveryEngine()