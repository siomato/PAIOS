from app.core.action_executor import action_executor
from app.core.replanner import replanner

import time


class RecoveryEngine:

    # =========================================================
    # CONFIGURATION
    # =========================================================

    MAX_RETRIES = 2
    RETRY_DELAY = 1.0
    MAX_REPLANS = 1

    # =========================================================
    # INITIALIZATION
    # =========================================================

    def __init__(self):

        print(
            "🛡️ RECOVERY ENGINE MODULE LOADED 🛡️"
        )

    # =========================================================
    # CLASSIFY ERROR
    # =========================================================

    def _classify_error(
        self,
        result
    ):

        error = (
            result.get("error")
            or ""
        ).lower()

        # -----------------------------------------------------
        # Browser/session errors
        # -----------------------------------------------------

        browser_errors = (
            "browser",
            "page",
            "context",
            "target page",
            "session",
            "closed",
            "connection",
            "playwright",
        )

        if any(
            word in error
            for word in browser_errors
        ):

            return "browser"

        # -----------------------------------------------------
        # Target errors
        # -----------------------------------------------------

        target_errors = (
            "target",
            "element",
            "locator",
            "resolve",
            "not found",
            "could not resolve",
        )

        if any(
            word in error
            for word in target_errors
        ):

            return "target"

        # -----------------------------------------------------
        # Timeout
        # -----------------------------------------------------

        if (
            "timeout" in error
            or "timed out" in error
        ):

            return "timeout"

        # -----------------------------------------------------
        # Network
        # -----------------------------------------------------

        network_errors = (
            "network",
            "connection",
            "navigation",
            "net::",
        )

        if any(
            word in error
            for word in network_errors
        ):

            return "network"

        # -----------------------------------------------------
        # Unknown
        # -----------------------------------------------------

        return "unknown"

    # =========================================================
    # RECOVERABILITY
    # =========================================================

    def _is_recoverable(
        self,
        result
    ):

        if result.get(
            "status"
        ) == "success":

            return False

        if result.get(
            "recoverable"
        ) is False:

            return False

        return True

    # =========================================================
    # WAIT
    # =========================================================

    def _wait(
        self
    ):

        time.sleep(
            self.RETRY_DELAY
        )

    # =========================================================
    # PREPARE RECOVERY
    # =========================================================

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

        # -----------------------------------------------------
        # Browser/session
        # -----------------------------------------------------

        if error_type == "browser":

            print(
                "🌐 Browser/session issue detected."
            )

            return True

        # -----------------------------------------------------
        # Target
        # -----------------------------------------------------

        if error_type == "target":

            print(
                "🎯 Target resolution problem detected."
            )

            return True

        # -----------------------------------------------------
        # Timeout
        # -----------------------------------------------------

        if error_type == "timeout":

            print(
                "⏳ Timeout detected."
            )

            return True

        # -----------------------------------------------------
        # Network
        # -----------------------------------------------------

        if error_type == "network":

            print(
                "🌐 Network/navigation issue detected."
            )

            return True

        # -----------------------------------------------------
        # Unknown
        # -----------------------------------------------------

        print(
            "❓ Unknown failure type."
        )

        return True

    # =========================================================
    # EXECUTE ONE ACTION WITH RETRIES
    # =========================================================

    def execute_action(
        self,
        action,
        max_retries=None
    ):

        if max_retries is None:

            max_retries = self.MAX_RETRIES

        print(
            "\n========== RECOVERY EXECUTOR =========="
        )

        print(
            f"Action: {action}"
        )

        attempts = 0

        recovery_history = []

        last_result = None

        # =====================================================
        # FIRST EXECUTION + RETRIES
        # =====================================================

        while attempts <= max_retries:

            attempts += 1

            print(
                f"\n🔄 Attempt "
                f"{attempts}/{max_retries + 1}"
            )

            try:

                result = action_executor.execute_action(
                    action
                )

            except Exception as e:

                result = {
                    "status": "failed",
                    "action": action,
                    "error": str(e),
                    "recoverable": True
                }

            last_result = result

            # -------------------------------------------------
            # SUCCESS
            # -------------------------------------------------

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
                    "recovered": attempts > 1,
                    "recovery_history": recovery_history,
                    "result": result,
                    "error": None
                }

            # -------------------------------------------------
            # FAILURE
            # -------------------------------------------------

            error_type = self._classify_error(
                result
            )

            recovery_history.append({
                "attempt": attempts,
                "error": result.get(
                    "error"
                ),
                "error_type": error_type
            })

            print(
                f"❌ Attempt {attempts} failed."
            )

            print(
                f"Error type: {error_type}"
            )

            print(
                f"Reason: "
                f"{result.get('error')}"
            )

            # -------------------------------------------------
            # NON-RECOVERABLE
            # -------------------------------------------------

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
                    "recovery_history": recovery_history,
                    "result": result,
                    "error": result.get(
                        "error"
                    )
                }

            # -------------------------------------------------
            # RETRY LIMIT
            # -------------------------------------------------

            if attempts > max_retries:

                break

            # -------------------------------------------------
            # PREPARE
            # -------------------------------------------------

            prepared = self._prepare_recovery(
                action,
                error_type
            )

            if not prepared:

                print(
                    "🛑 Recovery preparation failed."
                )

                break

            # -------------------------------------------------
            # WAIT
            # -------------------------------------------------

            print(
                f"⏳ Waiting "
                f"{self.RETRY_DELAY}s "
                f"before retry..."
            )

            self._wait()

        # =====================================================
        # FINAL FAILURE
        # =====================================================

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
            "recovery_history": recovery_history,
            "result": last_result,
            "error": (
                last_result.get("error")
                if last_result
                else "Unknown error"
            )
        }

    # =========================================================
    # REPLAN FAILED PLAN
    # =========================================================

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

            replan_result = replanner.replan(
                original_steps,
                failed_step,
                failure
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
                "error": "Invalid replanner response.",
                "steps": []
            }

        if replan_result.get(
            "status"
        ) != "success":

            print(
                "❌ Replanner failed."
            )

            return {
                "status": "failed",
                "error": replan_result.get(
                    "error",
                    "Replanner failed."
                ),
                "steps": []
            }

        new_steps = replan_result.get(
            "steps",
            []
        )

        if not new_steps:

            print(
                "❌ Replanner returned no steps."
            )

            return {
                "status": "failed",
                "error": "Replanner generated no steps.",
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
            "reason": replan_result.get(
                "reason"
            ),
            "steps": new_steps,
            "failed_step": failed_step
        }

    # =========================================================
    # EXECUTE COMPLETE PLAN WITH
    # RETRY + REPLANNING
    # =========================================================

    def execute(
        self,
        steps,
        max_retries=None
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

        if not steps:

            return {
                "status": "failed",
                "steps": [],
                "failed_step": None,
                "error": "No actions to execute.",
                "replans_used": 0,
                "replan_history": []
            }

        # -----------------------------------------------------
        # Keep original plan
        # -----------------------------------------------------

        original_steps = list(
            steps
        )

        current_steps = list(
            steps
        )

        results = []

        replans_used = 0

        replan_history = []

        # =====================================================
        # PLAN EXECUTION LOOP
        # =====================================================

        while True:

            total_steps = len(
                current_steps
            )

            results = []

            print(
                f"\n📋 Executing plan with "
                f"{total_steps} steps."
            )

            # =================================================
            # EXECUTE EACH STEP
            # =================================================

            plan_failed = False

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

                result = self.execute_action(
                    action,
                    max_retries=max_retries
                )

                results.append({
                    "step": index,
                    "action": action,
                    "status": result.get(
                        "status"
                    ),
                    "result": result
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

                failure = result.get(
                    "error"
                )

                failed_result = result

                break

            # =================================================
            # ENTIRE PLAN SUCCESS
            # =================================================

            if not plan_failed:

                print(
                    "\n🎉 ALL STEPS COMPLETED."
                )

                return {
                    "status": "success",
                    "steps": results,
                    "failed_step": None,
                    "error": None,
                    "replans_used": replans_used,
                    "replan_history": replan_history
                }

            # =================================================
            # REPLAN LIMIT
            # =================================================

            if replans_used >= self.MAX_REPLANS:

                print(
                    "\n🛑 Maximum replanning attempts reached."
                )

                return {
                    "status": "failed",
                    "steps": results,
                    "failed_step": failed_step,
                    "error": failure,
                    "replans_used": replans_used,
                    "replan_history": replan_history
                }

            # =================================================
            # CALL REPLANNER
            # =================================================

            print(
                "\n🔁 Recovery retries exhausted."
            )

            print(
                "🧠 Sending failure to Replanner..."
            )

            replan_result = self._replan(
                original_steps,
                failed_step,
                failure
            )

            replan_history.append({
                "replan_attempt": replans_used + 1,
                "failed_step": failed_step,
                "failure": failure,
                "result": replan_result
            })

            # =================================================
            # REPLAN FAILED
            # =================================================

            if replan_result.get(
                "status"
            ) != "success":

                print(
                    "\n❌ Replanning failed."
                )

                return {
                    "status": "failed",
                    "steps": results,
                    "failed_step": failed_step,
                    "error": replan_result.get(
                        "error"
                    ),
                    "replans_used": replans_used,
                    "replan_history": replan_history
                }

            # =================================================
            # USE NEW PLAN
            # =================================================

            replans_used += 1

            current_steps = list(
                replan_result.get(
                    "steps",
                    []
                )
            )

            if not current_steps:

                return {
                    "status": "failed",
                    "steps": results,
                    "failed_step": failed_step,
                    "error": "Replanner returned empty plan.",
                    "replans_used": replans_used,
                    "replan_history": replan_history
                }

            print(
                "\n♻️ NEW PLAN ACCEPTED."
            )

            print(
                f"Replans used: "
                f"{replans_used}/{self.MAX_REPLANS}"
            )

            # -------------------------------------------------
            # Loop back and execute new plan
            # -------------------------------------------------


# =============================================================
# GLOBAL INSTANCE
# =============================================================

recovery_engine = RecoveryEngine()