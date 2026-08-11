from app.core.action_planner import action_planner
from app.core.recovery_engine import recovery_engine


class AgentController:

    # =========================================================
    # INITIALIZATION
    # =========================================================

    def __init__(self):

        print(
            "🤖 AGENT CONTROLLER MODULE LOADED 🤖"
        )

    # =========================================================
    # PLAN TASK
    # =========================================================

    def create_plan(
        self,
        user_message: str
    ):

        print(
            "\n========== PLANNING =========="
        )

        print(
            f"User message: {user_message}"
        )

        if not user_message or not user_message.strip():

            return {
                "status": "failed",
                "error": "User message is empty.",
                "steps": []
            }

        try:

            steps = action_planner.plan(
                user_message
            )

        except Exception as e:

            print(
                f"❌ Planning failed: {e}"
            )

            return {
                "status": "failed",
                "error": str(e),
                "steps": []
            }

        # -----------------------------------------------------
        # Validate plan
        # -----------------------------------------------------

        if not isinstance(
            steps,
            list
        ):

            return {
                "status": "failed",
                "error": "Planner returned invalid plan.",
                "steps": []
            }

        if not steps:

            return {
                "status": "failed",
                "error": "Planner produced no actions.",
                "steps": []
            }

        # -----------------------------------------------------
        # Print plan
        # -----------------------------------------------------

        print(
            f"\n📋 Generated {len(steps)} action(s):"
        )

        for index, step in enumerate(
            steps,
            start=1
        ):

            print(
                f"  {index}. {step}"
            )

        return {
            "status": "success",
            "steps": steps,
            "error": None
        }

    # =========================================================
    # VALIDATE PLAN
    # =========================================================

    def validate_plan(
        self,
        steps
    ):

        if not isinstance(
            steps,
            list
        ):

            return False

        if len(steps) == 0:

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
    # EXECUTE PLAN
    # =========================================================

    def execute_plan(
        self,
        steps
    ):

        print(
            "\n========== EXECUTION =========="
        )

        print(
            f"Executing {len(steps)} action(s)..."
        )

        try:

            result = recovery_engine.execute(
                steps
            )

            return result

        except Exception as e:

            print(
                f"❌ Execution error: {e}"
            )

            return {
                "status": "failed",
                "steps": [],
                "failed_step": None,
                "error": str(e)
            }

    # =========================================================
    # RUN COMPLETE TASK
    # =========================================================

    def run(
        self,
        user_message: str
    ):

        print(
            "\n"
            "=========================================="
        )

        print(
            "          🤖 PAIO AGENT CONTROLLER"
        )

        print(
            "=========================================="
        )

        print(
            f"\nUser request:"
        )

        print(
            f"  {user_message}"
        )

        # =====================================================
        # STEP 1 — PLAN
        # =====================================================

        planning_result = self.create_plan(
            user_message
        )

        if planning_result.get(
            "status"
        ) != "success":

            print(
                "\n❌ TASK FAILED DURING PLANNING."
            )

            return {
                "status": "failed",
                "phase": "planning",
                "error": planning_result.get(
                    "error"
                ),
                "steps": []
            }

        steps = planning_result[
            "steps"
        ]

        # =====================================================
        # STEP 2 — VALIDATE
        # =====================================================

        print(
            "\n========== VALIDATION =========="
        )

        if not self.validate_plan(
            steps
        ):

            print(
                "❌ Invalid action plan."
            )

            return {
                "status": "failed",
                "phase": "validation",
                "error": "Invalid action plan.",
                "steps": steps
            }

        print(
            "✅ Action plan validated."
        )

        # =====================================================
        # STEP 3 — EXECUTE
        # =====================================================

        execution_result = self.execute_plan(
            steps
        )

        # =====================================================
        # STEP 4 — FINAL RESULT
        # =====================================================

        print(
            "\n=========================================="
        )

        print(
            "             FINAL RESULT"
        )

        print(
            "=========================================="
        )

        print(
            f"Status: "
            f"{execution_result.get('status')}"
        )

        # -----------------------------------------------------
        # SUCCESS
        # -----------------------------------------------------

        if execution_result.get(
            "status"
        ) == "success":

            print(
                "\n🎉 TASK COMPLETED SUCCESSFULLY."
            )

            return {
                "status": "success",
                "phase": "completed",
                "user_message": user_message,
                "plan": steps,
                "execution": execution_result,
                "error": None
            }

        # -----------------------------------------------------
        # FAILURE
        # -----------------------------------------------------

        print(
            "\n❌ TASK FAILED."
        )

        print(
            f"Error: "
            f"{execution_result.get('error')}"
        )

        return {
            "status": "failed",
            "phase": "execution",
            "user_message": user_message,
            "plan": steps,
            "execution": execution_result,
            "error": execution_result.get(
                "error"
            )
        }


# =============================================================
# GLOBAL INSTANCE
# =============================================================

agent_controller = AgentController()