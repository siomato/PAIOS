from typing import Any, Dict, List


class Replanner:

    # =========================================================
    # INITIALIZATION
    # =========================================================

    def __init__(self):
        print(
            "🧠 REPLANNER MODULE LOADED 🧠"
        )

    # =========================================================
    # ACTION SIGNATURE
    # =========================================================

    def _action_signature(
        self,
        action: Any
    ):
        if not isinstance(
            action,
            dict
        ):
            return None

        return (
            action.get("action"),
            action.get("target"),
            action.get("query"),
            action.get("url"),
            action.get("command"),
            action.get("key")
        )

    # =========================================================
    # SAME ACTION CHECK
    # =========================================================

    def _same_action(
        self,
        first: Any,
        second: Any
    ) -> bool:

        first_signature = (
            self._action_signature(
                first
            )
        )

        second_signature = (
            self._action_signature(
                second
            )
        )

        if (
            first_signature is None
            or
            second_signature is None
        ):
            return False

        return (
            first_signature
            ==
            second_signature
        )

    # =========================================================
    # STRIP EXECUTION METADATA
    # =========================================================

    def _clean_action(
        self,
        action
    ):

        if not isinstance(
            action,
            dict
        ):
            return action

        cleaned = dict(
            action
        )

        cleaned.pop(
            "plan_id",
            None
        )

        cleaned.pop(
            "step_index",
            None
        )

        cleaned.pop(
            "total_steps",
            None
        )

        cleaned.pop(
            "replanned",
            None
        )

        return cleaned

    # =========================================================
    # STRATEGY GENERATION
    # =========================================================

    def replan_action(
        self,
        action,
        failure
    ):

        if not isinstance(
            action,
            dict
        ):
            return {
                "status": "failed",
                "error": "Invalid failed action.",
                "actions": []
            }

        action_type = str(
            action.get(
                "action",
                ""
            )
        ).strip().lower()

        # =====================================================
        # SEARCH
        # =====================================================

        if action_type == "search":

            query = str(
                action.get(
                    "query",
                    ""
                )
            ).strip()

            if not query:
                return {
                    "status": "failed",
                    "error": "Search query is empty.",
                    "actions": []
                }

            return {
                "status": "success",
                "reason":
                    "Refresh the page context before retrying search.",
                "actions": [
                    {
                        "action": "read"
                    },
                    {
                        "action": "search",
                        "query": query
                    }
                ]
            }

        # =====================================================
        # CLICK
        # =====================================================

        if action_type == "click":

            target = str(
                action.get(
                    "target",
                    ""
                )
            ).strip()

            if not target:

                return {
                    "status": "failed",
                    "error":
                        "Click target is empty.",
                    "actions": []
                }

            return {
                "status": "success",
                "reason":
                    "Re-read the current page before "
                    "retrying the click target.",
                "actions": [
                    {
                        "action": "read"
                    },
                    {
                        "action": "click",
                        "target": target
                    }
                ]
            }

        # =====================================================
        # FIND
        # =====================================================

        if action_type == "find":

            query = str(
                action.get(
                    "query",
                    ""
                )
            ).strip()

            if not query:

                return {
                    "status": "failed",
                    "error":
                        "Find query is empty.",
                    "actions": []
                }

            return {
                "status": "success",
                "reason":
                    "Refresh page context before retrying find.",
                "actions": [
                    {
                        "action": "read"
                    },
                    {
                        "action": "find",
                        "query": query
                    }
                ]
            }

        # =====================================================
        # READ
        # =====================================================

        if action_type == "read":

            return {
                "status": "success",
                "reason":
                    "Re-read the current page before retrying.",
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

            command = str(
                action.get(
                    "command",
                    ""
                )
            ).strip()

            if not command:

                return {
                    "status": "failed",
                    "error":
                        "Fill command is empty.",
                    "actions": []
                }

            return {
                "status": "success",
                "reason":
                    "Re-read the page before retrying fill.",
                "actions": [
                    {
                        "action": "read"
                    },
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

            key = str(
                action.get(
                    "key",
                    ""
                )
            ).strip()

            if not key:

                return {
                    "status": "failed",
                    "error":
                        "Press key is empty.",
                    "actions": []
                }

            return {
                "status": "success",
                "reason":
                    "Re-establish page context before pressing key.",
                "actions": [
                    {
                        "action": "press",
                        "key": key
                    }
                ]
            }

        # =====================================================
        # OPEN URL
        # =====================================================

        if action_type == "open_url":

            url = str(
                action.get(
                    "url",
                    ""
                )
            ).strip()

            if not url:

                return {
                    "status": "failed",
                    "error":
                        "Open URL is empty.",
                    "actions": []
                }

            return {
                "status": "success",
                "reason":
                    "Retry URL navigation using the supported "
                    "open_url action.",
                "actions": [
                    {
                        "action": "open_url",
                        "url": url
                    }
                ]
            }

        # =====================================================
        # UNSUPPORTED ACTION
        # =====================================================

        return {
            "status": "failed",
            "error":
                f"No replanning strategy for action: {action_type}",
            "actions": []
        }

    # =========================================================
    # REPLAN
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

        if (
            not isinstance(
                original_steps,
                list
            )
            or
            not original_steps
        ):

            return {
                "status": "failed",
                "error":
                    "Original plan is empty or invalid.",
                "steps": []
            }

        # =====================================================
        # VALIDATE FAILED STEP
        # =====================================================

        if (
            not isinstance(
                failed_step,
                int
            )
            or
            failed_step < 1
            or
            failed_step > len(
                original_steps
            )
        ):

            return {
                "status": "failed",
                "error":
                    "Failed step is outside the plan.",
                "steps": []
            }

        # =====================================================
        # GET FAILED ACTION
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

        if result.get(
            "status"
        ) != "success":

            return {
                "status": "failed",
                "error":
                    result.get(
                        "error",
                        "Replanner failed."
                    ),
                "steps": []
            }

        new_actions = (
            result.get(
                "actions"
            )
            or
            []
        )

        if not new_actions:

            return {
                "status": "failed",
                "error":
                    "Replanner generated no alternative actions.",
                "steps": []
            }

        # =====================================================
        # CLEAN METADATA
        # =====================================================

        cleaned_actions = []

        for action in new_actions:

            cleaned_actions.append(
                self._clean_action(
                    action
                )
            )

        new_actions = cleaned_actions

        # =====================================================
        # LOOP GUARD #1
        #
        # Prevent a direct identical retry.
        # =====================================================

        if len(
            new_actions
        ) == 1:

            if self._same_action(
                new_actions[0],
                failed_action
            ):

                return {
                    "status": "failed",
                    "error":
                        "Replanner generated the same failed action.",
                    "steps": []
                }

        # =====================================================
        # REMAINING ORIGINAL STEPS
        # =====================================================

        remaining_steps = original_steps[
            failed_step:
        ]

        # =====================================================
        # BUILD NEW PLAN
        # =====================================================

        new_plan = (
            list(
                new_actions
            )
            +
            [
                self._clean_action(
                    step
                )
                for step in remaining_steps
            ]
        )

        # =====================================================
        # LOOP GUARD #2
        #
        # Example:
        #
        # read
        # click SAME_FAILED_TARGET
        #
        # This is not a meaningful click recovery.
        # =====================================================

        if len(
            new_actions
        ) >= 2:

            generated_retry = (
                new_actions[-1]
            )

            if self._same_action(
                generated_retry,
                failed_action
            ):

                action_type = str(
                    failed_action.get(
                        "action",
                        ""
                    )
                ).strip().lower()

                if action_type == "click":

                    failure_text = str(
                        failure.get(
                            "error",
                            ""
                        )
                        if isinstance(
                            failure,
                            dict
                        )
                        else
                        failure
                    ).lower()

                    target_failure = (
                        "could not resolve target"
                        in failure_text
                        or
                        "target"
                        in failure_text
                    )

                    if target_failure:

                        return {
                            "status": "failed",
                            "error":
                                "Replanner could not produce "
                                "a different click target.",
                            "steps": []
                        }

        # =====================================================
        # REMOVE IMMEDIATE EXACT RETRY
        # =====================================================

        if len(
            new_plan
        ) > 1:

            if self._same_action(
                new_plan[0],
                failed_action
            ):

                new_plan = new_plan[
                    1:
                ]

        # =====================================================
        # FINAL PLAN VALIDATION
        # =====================================================

        if not new_plan:

            return {
                "status": "failed",
                "error":
                    "Replanner produced an empty plan.",
                "steps": []
            }

        # =====================================================
        # PLAN METADATA
        # =====================================================

        total_steps = len(
            new_plan
        )

        plan_id = (
            "replan-"
            +
            str(
                abs(
                    hash(
                        str(
                            new_plan
                        )
                    )
                )
            )
        )

        final_steps = []

        for index, action in enumerate(
            new_plan,
            start=1
        ):

            if not isinstance(
                action,
                dict
            ):
                continue

            enriched = dict(
                action
            )

            enriched[
                "plan_id"
            ] = plan_id

            enriched[
                "step_index"
            ] = index

            enriched[
                "total_steps"
            ] = total_steps

            enriched[
                "replanned"
            ] = True

            final_steps.append(
                enriched
            )

        # =====================================================
        # FINAL VALIDATION
        # =====================================================

        if not final_steps:

            return {
                "status": "failed",
                "error":
                    "Replanner produced no valid actions.",
                "steps": []
            }

        # =====================================================
        # LOG PLAN
        # =====================================================

        print(
            "\n🧠 Replanned steps:"
        )

        for index, step in enumerate(
            final_steps,
            start=1
        ):

            print(
                f"{index}. {step}"
            )

        # =====================================================
        # SUCCESS
        # =====================================================

        return {
            "status": "success",
            "reason":
                result.get(
                    "reason",
                    "Alternative execution plan generated."
                ),
            "steps":
                final_steps,
            "failed_step":
                failed_step
        }


# =============================================================
# GLOBAL INSTANCE
# =============================================================

replanner = Replanner()