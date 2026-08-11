class Replanner:

    # =========================================================
    # INIT
    # =========================================================

    def __init__(self):

        print(
            "🧠 REPLANNER MODULE LOADED 🧠"
        )

    # =========================================================
    # CREATE ALTERNATIVE ACTION
    # =========================================================

    def replan_action(
        self,
        action,
        failure
    ):

        print(
            "\n========== REPLANNING =========="
        )

        print(
            f"Failed action: {action}"
        )

        print(
            f"Failure: {failure}"
        )

        # =====================================================
        # VALIDATE ACTION
        # =====================================================

        if not isinstance(action, dict):

            return {
                "status": "failed",
                "error": "Invalid action format.",
                "actions": []
            }

        action_type = action.get(
            "action"
        )

        # =====================================================
        # SEARCH
        # =====================================================

        if action_type == "search":

            query = (
                action.get("query")
                or ""
            ).strip()

            if not query:

                return {
                    "status": "failed",
                    "error": "Search query is empty.",
                    "actions": []
                }

            print(
                "🔄 Replanning search action..."
            )

            alternative = {
                "action": "search",
                "query": query
            }

            return {
                "status": "success",
                "reason": (
                    "Retry search using the "
                    "browser search fallback."
                ),
                "actions": [
                    alternative
                ]
            }

        # =====================================================
        # CLICK
        # =====================================================

        if action_type == "click":

            target = (
                action.get("target")
                or ""
            ).strip()

            if not target:

                return {
                    "status": "failed",
                    "error": "Click target is empty.",
                    "actions": []
                }

            print(
                "🔄 Replanning click action..."
            )

            alternative_actions = [

                {
                    "action": "read"
                },

                {
                    "action": "click",
                    "target": target
                }

            ]

            return {
                "status": "success",
                "reason": (
                    "Re-read the current page "
                    "and retry the target."
                ),
                "actions": alternative_actions
            }

        # =====================================================
        # READ
        # =====================================================

        if action_type == "read":

            print(
                "🔄 Replanning page read..."
            )

            return {
                "status": "success",
                "reason": (
                    "Retry reading the current page."
                ),
                "actions": [
                    {
                        "action": "read"
                    }
                ]
            }

        # =====================================================
        # FILL
        # =====================================================

        if action_type == "fill":

            command = (
                action.get("command")
                or ""
            ).strip()

            if not command:

                return {
                    "status": "failed",
                    "error": "Fill command is empty.",
                    "actions": []
                }

            print(
                "🔄 Replanning fill action..."
            )

            return {
                "status": "success",
                "reason": (
                    "Retry the fill operation."
                ),
                "actions": [
                    {
                        "action": "fill",
                        "command": command
                    }
                ]
            }

        # =====================================================
        # PRESS
        # =====================================================

        if action_type == "press":

            key = (
                action.get("key")
                or ""
            ).strip()

            if not key:

                return {
                    "status": "failed",
                    "error": "Press key is empty.",
                    "actions": []
                }

            print(
                "🔄 Replanning key press..."
            )

            return {
                "status": "success",
                "reason": (
                    "Retry the key press."
                ),
                "actions": [
                    {
                        "action": "press",
                        "key": key
                    }
                ]
            }

        # =====================================================
        # UNKNOWN ACTION
        # =====================================================

        print(
            "❌ No replanning strategy "
            f"for action: {action_type}"
        )

        return {
            "status": "failed",
            "error": (
                f"No replanning strategy "
                f"for action: {action_type}"
            ),
            "actions": []
        }

    # =========================================================
    # REPLAN COMPLETE TASK
    # =========================================================

    def replan(
        self,
        original_steps,
        failed_step,
        failure
    ):

        print(
            "\n========================================"
        )

        print(
            "          🧠 REPLANNER"
        )

        print(
            "========================================"
        )

        # =====================================================
        # VALIDATE ORIGINAL PLAN
        # =====================================================

        if not original_steps:

            return {
                "status": "failed",
                "error": "Original plan is empty.",
                "steps": []
            }

        # =====================================================
        # VALIDATE FAILED STEP
        # =====================================================

        if not isinstance(
            failed_step,
            int
        ):

            return {
                "status": "failed",
                "error": "Failed step must be an integer.",
                "steps": []
            }

        if failed_step < 1:

            return {
                "status": "failed",
                "error": "Invalid failed step.",
                "steps": []
            }

        if failed_step > len(
            original_steps
        ):

            return {
                "status": "failed",
                "error": "Failed step is outside the plan.",
                "steps": []
            }

        # =====================================================
        # LOCATE FAILED ACTION
        # =====================================================

        failed_action = original_steps[
            failed_step - 1
        ]

        print(
            f"Failed step: {failed_step}"
        )

        print(
            f"Failed action: {failed_action}"
        )

        # =====================================================
        # GENERATE ALTERNATIVE
        # =====================================================

        result = self.replan_action(
            failed_action,
            failure
        )

        # =====================================================
        # CHECK REPLANNING RESULT
        # =====================================================

        if result.get(
            "status"
        ) != "success":

            return {
                "status": "failed",
                "error": result.get(
                    "error"
                ),
                "steps": []
            }

        new_actions = result.get(
            "actions",
            []
        )

        if not new_actions:

            return {
                "status": "failed",
                "error": (
                    "Replanner generated "
                    "no alternative actions."
                ),
                "steps": []
            }

        # =====================================================
        # PRESERVE REMAINING ORIGINAL PLAN
        # =====================================================

        remaining_steps = original_steps[
            failed_step:
        ]

        # =====================================================
        # BUILD NEW PLAN
        # =====================================================

        new_plan = (
            new_actions
            + remaining_steps
        )

        print(
            "\n📋 New plan:"
        )

        for index, step in enumerate(
            new_plan,
            start=1
        ):

            print(
                f"  {index}. {step}"
            )

        # =====================================================
        # RETURN NEW PLAN
        # =====================================================

        return {
            "status": "success",
            "reason": result.get(
                "reason"
            ),
            "steps": new_plan,
            "failed_step": failed_step
        }


# =============================================================
# GLOBAL INSTANCE
# =============================================================

replanner = Replanner()