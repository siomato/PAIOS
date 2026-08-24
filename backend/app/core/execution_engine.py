from app.core.action_executor import action_executor
from app.core.recovery_engine import recovery_engine
from app.core.replanner import replanner


class ExecutionEngine:

    # =========================================================
    # CONFIGURATION
    # =========================================================

    MAX_REPLANS = 3

    # =========================================================
    # INITIALIZATION
    # =========================================================

    def __init__(self):

        self.replans_used = 0

        print(
            "⚙️ EXECUTION ENGINE MODULE LOADED ⚙️"
        )

    # =========================================================
    # RESET STATE
    # =========================================================

    def reset(self):

        self.replans_used = 0

    # =========================================================
    # VALIDATE PLAN
    # =========================================================

    def _validate_plan(self, steps):

        if not isinstance(
            steps,
            list
        ):

            return False

        if not steps:

            return False

        for step in steps:

            if not isinstance(
                step,
                dict
            ):

                return False

            if not step.get(
                "action"
            ):

                return False

        return True

    # =========================================================
    # EXTRACT FAILED ACTION
    # =========================================================

    def _get_failed_action(
        self,
        plan,
        failed_step
    ):

        if not isinstance(
            failed_step,
            int
        ):

            return None

        if failed_step < 1:

            return None

        if failed_step > len(
            plan
        ):

            return None

        return plan[
            failed_step - 1
        ]

    # =========================================================
    # EXECUTE PLAN
    # =========================================================

    def execute_plan(
        self,
        steps
    ):

        self.reset()

        if not self._validate_plan(
            steps
        ):

            return {
                "status": "failed",
                "steps": [],
                "error": "Invalid or empty execution plan.",
                "replans_used": 0
            }

        current_plan = list(
            steps
        )

        execution_history = []

        print(
            "\n========================================"
        )

        print(
            "         ⚙️ EXECUTION ENGINE"
        )

        print(
            "========================================"
        )

        print(
            f"Maximum replans: {self.MAX_REPLANS}"
        )

        # =====================================================
        # MAIN EXECUTION LOOP
        # =====================================================

        while True:

            print(
                "\n========================================"
            )

            print(
                "📋 CURRENT EXECUTION PLAN"
            )

            print(
                "========================================"
            )

            for index, step in enumerate(
                current_plan,
                start=1
            ):

                print(
                    f"{index}. {step}"
                )

            # -------------------------------------------------
            # EXECUTE PLAN
            # -------------------------------------------------

            print(
                "\n▶️ Executing current plan..."
            )

            try:

                result = action_executor.execute(
                    current_plan
                )

            except Exception as e:

                result = {
                    "status": "failed",
                    "steps": [],
                    "failed_step": None,
                    "error": str(e)
                }

            execution_history.append(
                result
            )

            # =================================================
            # SUCCESS
            # =================================================

            if result.get(
                "status"
            ) == "success":

                print(
                    "\n🎉 EXECUTION COMPLETED SUCCESSFULLY."
                )

                return {
                    "status": "success",
                    "results": execution_history,
                    "replans_used": self.replans_used,
                    "final_plan": current_plan
                }

            # =================================================
            # FAILURE
            # =================================================

            failed_step = result.get(
                "failed_step"
            )

            error = result.get(
                "error"
            )

            print(
                "\n❌ CURRENT PLAN FAILED."
            )

            print(
                f"Failed step: {failed_step}"
            )

            print(
                f"Error: {error}"
            )

            # -------------------------------------------------
            # Validate failed step
            # -------------------------------------------------

            failed_action = self._get_failed_action(
                current_plan,
                failed_step
            )

            if failed_action is None:

                print(
                    "\n❌ Could not identify failed action."
                )

                return {
                    "status": "failed",
                    "results": execution_history,
                    "failed_step": failed_step,
                    "error": error,
                    "replans_used": self.replans_used,
                    "final_plan": current_plan
                }

            print(
                f"\n🎯 Failed action: {failed_action}"
            )

            # =================================================
            # RECOVERY ENGINE
            # =================================================

            print(
                "\n🔄 Starting Recovery Engine..."
            )

            try:

                recovery_result = (
                    recovery_engine.execute_action(
                        failed_action
                    )
                )

            except Exception as e:

                recovery_result = {
                    "status": "failed",
                    "action": failed_action,
                    "attempts": 0,
                    "recovered": False,
                    "error": str(e)
                }

            # -------------------------------------------------
            # Store recovery result
            # -------------------------------------------------

            execution_history.append({
                "type": "recovery",
                "failed_step": failed_step,
                "action": failed_action,
                "result": recovery_result
            })

            # =================================================
            # RECOVERY SUCCESS
            # =================================================

            if recovery_result.get(
                "status"
            ) == "success":

                print(
                    "\n♻️ Recovery succeeded."
                )

                                # ---------------------------------------------
                # Recovery successfully handled the failed action.
                #
                # The failed step is now complete, so remove it
                # from the plan and continue with everything after it.
                # ---------------------------------------------

                next_index = failed_step

                remaining_steps = current_plan[
                    next_index:
                ]

                # -------------------------------------------------
                # No remaining work means the entire objective is
                # complete.
                # -------------------------------------------------

                if not remaining_steps:

                    print(
                        "\n🎉 Recovery completed the final step."
                    )

                    return {
                        "status": "success",
                        "results": execution_history,
                        "replans_used": self.replans_used,
                        "final_plan": []
                    }

                # -------------------------------------------------
                # Continue with the remaining plan.
                #
                # IMPORTANT:
                # failed_step is relative to the OLD plan.
                # The new current_plan starts at index 1 again.
                # -------------------------------------------------

                current_plan = list(
                    remaining_steps
                )

                print(
                    "\n▶️ Continuing with remaining steps..."
                )

                print(
                    f"Remaining steps: "
                    f"{len(current_plan)}"
                )

                continue

            # =================================================
            # RECOVERY FAILED
            # =================================================

            print(
                "\n❌ Recovery attempts exhausted."
            )

            # =================================================
            # MAX REPLAN CHECK
            # =================================================

            if self.replans_used >= self.MAX_REPLANS:

                print(
                    "\n🛑 Maximum replan limit reached."
                )

                print(
                    f"Replans used: "
                    f"{self.replans_used}/"
                    f"{self.MAX_REPLANS}"
                )

                return {
                    "status": "failed",
                    "results": execution_history,
                    "failed_step": failed_step,
                    "error": error,
                    "replans_used": self.replans_used,
                    "final_plan": current_plan
                }

            # =================================================
            # REPLANNER
            # =================================================

            print(
                "\n🧠 Sending failure to Replanner..."
            )

            failure = {
                "status": "failed",
                "error": (
                    recovery_result.get(
                        "error"
                    )
                    or error
                    or "Unknown execution failure."
                ),
                "error_type": (
                    recovery_result.get(
                        "error_type"
                    )
                    or "unknown"
                ),
                "recoverable": True
            }

            try:

                replan_result = replanner.replan(
                    original_steps=current_plan,
                    failed_step=failed_step,
                    failure=failure
                )

            except Exception as e:

                print(
                    "\n❌ Replanner crashed."
                )

                print(
                    f"Reason: {e}"
                )

                return {
                    "status": "failed",
                    "results": execution_history,
                    "failed_step": failed_step,
                    "error": str(e),
                    "replans_used": self.replans_used,
                    "final_plan": current_plan
                }

            # -------------------------------------------------
            # Store replanner result
            # -------------------------------------------------

            execution_history.append({
                "type": "replan",
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
                    "\n❌ Replanner could not generate "
                    "a new plan."
                )

                return {
                    "status": "failed",
                    "results": execution_history,
                    "failed_step": failed_step,
                    "error": replan_result.get(
                        "error"
                    ),
                    "replans_used": self.replans_used,
                    "final_plan": current_plan
                }

            # =================================================
            # GET NEW PLAN
            # =================================================

            new_plan = replan_result.get(
                "steps"
            )

            if not new_plan:

                print(
                    "\n❌ Replanner returned an empty plan."
                )

                return {
                    "status": "failed",
                    "results": execution_history,
                    "failed_step": failed_step,
                    "error": "Replanner returned no steps.",
                    "replans_used": self.replans_used,
                    "final_plan": current_plan
                }

            # =================================================
            # UPDATE PLAN
            # =================================================

            self.replans_used += 1

            current_plan = list(
                new_plan
            )

            print(
                "\n========================================"
            )

            print(
                f"🧠 REPLAN #{self.replans_used}"
            )

            print(
                "========================================"
            )

            print(
                "📋 NEW EXECUTION PLAN:"
            )

            for index, step in enumerate(
                current_plan,
                start=1
            ):

                print(
                    f"{index}. {step}"
                )

            print(
                "\n▶️ Executing replanned plan..."
            )


# =============================================================
# GLOBAL INSTANCE
# =============================================================

execution_engine = ExecutionEngine()