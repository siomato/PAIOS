# ============================================================
# app/core/agent_evaluator.py
#
# PAIO AGENT EVALUATOR
#
# Phase 3 - Step 2
#
# Purpose:
#
# Evaluate the current AgentState and determine whether the
# autonomous task should:
#
#     COMPLETE
#     CONTINUE
#     FAILED
#
# V2 remains deterministic and does NOT use an LLM.
#
# Evaluation pipeline:
#
#     AgentState
#          ↓
#     Execution outcome
#          ↓
#     Action-specific validation
#          ↓
#     Plan progress validation
#          ↓
#     COMPLETE / CONTINUE / FAILED
#
# IMPORTANT:
#
# This evaluator is backward compatible with the existing
# AgentController contract:
#
#     {
#         "status": "...",
#         "reason": "...",
#         "next_action": ...
#     }
#
# It also understands the Phase 3 planner metadata:
#
#     plan_id
#     step_index
#     total_steps
#
# No Playwright objects are used here.
# ============================================================


class AgentEvaluator:

    # ========================================================
    # INITIALIZATION
    # ========================================================

    def __init__(self):

        print(
            "🧠 AGENT EVALUATOR MODULE LOADED 🧠"
        )

    # ========================================================
    # SAFE ATTRIBUTE HELPERS
    # ========================================================

    def _get(
        self,
        state,
        name,
        default=None
    ):

        try:
            return getattr(
                state,
                name,
                default
            )
        except Exception:
            return default

    # ========================================================

    def _normalize_status(
        self,
        value
    ):

        if value is None:
            return ""

        return str(
            value
        ).strip().lower()

    # ========================================================

    def _last_action(
        self,
        state,
        plan
    ):
        """
        Determine the action most recently attempted.

        Supports both the new Phase 3 state metadata and the
        existing completed_steps list.
        """

        # Prefer the newest recorded action from the action history.
        # ActionExecutor now records every executed action there.
        action_history = self._get(
            state,
            "action_history",
            []
        ) or []

        if action_history:
            latest = action_history[-1]

            if isinstance(latest, dict):
                recorded_action = latest.get("action")

                if isinstance(recorded_action, dict):
                    return recorded_action

                # Backward-compatible history format where the
                # history record itself is the action.
                return latest

        current_action = self._get(
            state,
            "current_action",
            None
        )

        if isinstance(
            current_action,
            dict
        ):
            return current_action

        completed_steps = (
            self._get(
                state,
                "completed_steps",
                []
            )
            or []
        )

        if completed_steps:

            last = completed_steps[-1]

            if isinstance(
                last,
                dict
            ):
                return last

        if plan:

            index = len(
                completed_steps
            ) - 1

            if (
                index >= 0
                and
                index < len(plan)
            ):

                action = plan[index]

                if isinstance(
                    action,
                    dict
                ):
                    return action

        return None

    # ========================================================
    # ACTION RESULT
    # ========================================================

    def _get_action_result(
        self,
        state
    ):
        """
        Extract the latest execution result using several
        backward-compatible field names.

        The evaluator never assumes that a specific AgentState
        implementation exists.
        """

        # Prefer the result attached to the newest action-history
        # record. This connects the evaluator to the new execution
        # memory without breaking older AgentState implementations.
        action_history = self._get(
            state,
            "action_history",
            []
        ) or []

        if action_history:
            latest = action_history[-1]

            if isinstance(latest, dict):
                recorded_result = latest.get("result")

                if recorded_result is not None:
                    return recorded_result

        candidates = (
            "last_result",
            "last_action_result",
            "action_result",
            "last_execution_result",
            "execution_result",
            "last_observation",
            "observation",
        )

        for name in candidates:

            value = self._get(
                state,
                name,
                None
            )

            if value is not None:
                return value

        return None

    # ========================================================
    # EXTRACT RESULT STATUS
    # ========================================================

    def _result_status(
        self,
        result
    ):

        if result is None:
            return None

        if isinstance(
            result,
            dict
        ):

            status = result.get(
                "status"
            )

            if status is not None:

                normalized = (
                    self._normalize_status(
                        status
                    )
                )

                if normalized in (
                    "success",
                    "succeeded",
                    "complete",
                    "completed",
                    "ok",
                    "passed",
                ):
                    return "success"

                if normalized in (
                    "failed",
                    "failure",
                    "error",
                    "cancelled",
                    "canceled",
                ):
                    return "failed"

                if normalized in (
                    "continue",
                    "running",
                    "pending",
                    "in_progress",
                ):
                    return "continue"

            # Some existing action results use an explicit
            # success boolean.
            if "success" in result:

                success = result.get(
                    "success"
                )

                if success is True:
                    return "success"

                if success is False:
                    return "failed"

            # Error field is strong evidence of failure.
            if result.get(
                "error"
            ):

                return "failed"

            return None

        return None

    # ========================================================
    # TEXT EXTRACTION
    # ========================================================

    def _result_text(
        self,
        result
    ):
        """
        Convert an observation/result into searchable text.

        This is deliberately conservative. It is used only for
        deterministic checks such as target presence.
        """

        if result is None:
            return ""

        if isinstance(
            result,
            str
        ):
            return result

        if isinstance(
            result,
            dict
        ):

            parts = []

            for key in (
                "message",
                "content",
                "text",
                "title",
                "page_title",
                "url",
                "current_url",
                "target",
                "query",
            ):

                value = result.get(
                    key
                )

                if value is not None:

                    parts.append(
                        str(value)
                    )

            return " ".join(
                parts
            )

        return str(
            result
        )

    # ========================================================
    # ACTION-SPECIFIC VALIDATION
    # ========================================================

    def _validate_action_result(
        self,
        action,
        result
    ):
        """
        Return:

            None       -> no contradiction / not enough data
            True       -> deterministic success evidence
            False      -> deterministic failure evidence

        We intentionally do not invent success merely because an
        action returned a value.
        """

        if not isinstance(
            action,
            dict
        ):
            return None

        if result is None:
            return None

        result_status = (
            self._result_status(
                result
            )
        )

        if result_status == "failed":
            return False

        if result_status == "success":
            return True

        action_type = (
            self._normalize_status(
                action.get(
                    "action"
                )
            )
        )

        text = (
            self._result_text(
                result
            ).casefold()
        )

        # ----------------------------------------------------
        # SEARCH
        # ----------------------------------------------------

        if action_type == "search":

            query = str(
                action.get(
                    "query",
                    ""
                )
            ).strip().casefold()

            if query and query in text:
                return True

        # ----------------------------------------------------
        # CLICK
        # ----------------------------------------------------

        elif action_type == "click":

            target = str(
                action.get(
                    "target",
                    ""
                )
            ).strip().casefold()

            if target:

                if (
                    target in text
                    or
                    f"clicked target: {target}"
                    in text
                ):
                    return True

        # ----------------------------------------------------
        # OPEN URL
        # ----------------------------------------------------

        elif action_type == "open_url":

            expected_url = str(
                action.get(
                    "url",
                    ""
                )
            ).strip().casefold()

            if expected_url:

                actual_url = ""

                if isinstance(
                    result,
                    dict
                ):

                    actual_url = str(
                        result.get(
                            "current_url",
                            result.get(
                                "url",
                                ""
                            )
                        )
                    ).strip().casefold()

                if actual_url:

                    # Exact match is preferred.
                    if actual_url == expected_url:
                        return True

                    # Also allow a trailing slash difference.
                    if (
                        actual_url.rstrip("/")
                        ==
                        expected_url.rstrip("/")
                    ):
                        return True

        # ----------------------------------------------------
        # FILL
        # ----------------------------------------------------

        elif action_type == "fill":

            if isinstance(
                result,
                dict
            ):

                # A successful fill operation can report the
                # target/value directly.
                if (
                    result.get(
                        "status"
                    )
                    in (
                        "success",
                        "complete",
                        "completed",
                        "ok",
                    )
                ):
                    return True

        # ----------------------------------------------------
        # PRESS
        # ----------------------------------------------------

        elif action_type == "press":

            if isinstance(
                result,
                dict
            ):

                if (
                    result.get(
                        "status"
                    )
                    in (
                        "success",
                        "complete",
                        "completed",
                        "ok",
                    )
                ):
                    return True

        # ----------------------------------------------------
        # READ
        # ----------------------------------------------------

        elif action_type == "read":

            if isinstance(
                result,
                dict
            ):

                content = (
                    result.get(
                        "content"
                    )
                    or
                    result.get(
                        "text"
                    )
                    or
                    result.get(
                        "message"
                    )
                )

                if content:
                    return True

        return None

    # ========================================================
    # VALIDATE PLAN METADATA
    # ========================================================

    def _validate_plan_progress(
        self,
        plan,
        completed_steps
    ):
        """
        Ensure the planner metadata is internally consistent.

        Returns:
            None
            failure reason string
        """

        if not plan:
            return None

        for index, action in enumerate(
            plan,
            start=1
        ):

            if not isinstance(
                action,
                dict
            ):
                continue

            step_index = action.get(
                "step_index"
            )

            total_steps = action.get(
                "total_steps"
            )

            if (
                step_index is not None
                and
                step_index != index
            ):

                return (
                    "Plan step metadata is inconsistent."
                )

            if (
                total_steps is not None
                and
                total_steps != len(plan)
            ):

                return (
                    "Plan total_steps metadata is inconsistent."
                )

        return None

    # ========================================================
    # ACTION HISTORY VALIDATION
    # ========================================================

    def _validate_action_history(
        self,
        state
    ):
        """
        Validate the newest action-history record.

        Returns:
            None   -> no history / insufficient information
            True   -> latest recorded action succeeded
            False  -> latest recorded action failed
        """

        history = self._get(
            state,
            "action_history",
            []
        ) or []

        if not history:
            return None

        latest = history[-1]

        if not isinstance(latest, dict):
            return None

        # Explicit success flag is authoritative when present.
        if "success" in latest:
            success = latest.get("success")

            if success is True:
                return True

            if success is False:
                return False

        result = latest.get("result")

        return self._result_status(result) == "success" if result is not None else None

    # ========================================================
    # EVALUATE
    # ========================================================

    def evaluate(
        self,
        state
    ):
        """
        Evaluate the current AgentState.

        Returns:

            {
                "status":
                    "complete" |
                    "continue" |
                    "failed",

                "reason": "...",

                "next_action": ...
            }
        """

        # ====================================================
        # VALIDATE STATE
        # ====================================================

        if state is None:

            return {
                "status": "failed",
                "reason":
                    "AgentState is missing.",
                "next_action": None
            }

        # ====================================================
        # FAILURE CHECK
        # ====================================================

        failed_step = self._get(
            state,
            "failed_step",
            None
        )

        if failed_step is not None:

            return {
                "status": "failed",
                "reason": (
                    "AgentState contains "
                    "a failed step."
                ),
                "next_action": None
            }

        # ====================================================
        # EXPLICIT FAILURE STATUS
        # ====================================================

        state_status = (
            self._normalize_status(
                self._get(
                    state,
                    "status",
                    ""
                )
            )
        )

        if state_status == "failed":

            return {
                "status": "failed",
                "reason": (
                    self._get(
                        state,
                        "last_error",
                        None
                    )
                    or
                    "AgentState reports failure."
                ),
                "next_action": None
            }

        # ====================================================
        # GET PLAN
        # ====================================================

        plan = self._get(
            state,
            "current_plan",
            []
        )

        if plan is None:
            plan = []

        # ====================================================
        # GET COMPLETED STEPS
        # ====================================================

        completed_steps = self._get(
            state,
            "completed_steps",
            []
        )

        if completed_steps is None:
            completed_steps = []

        # ====================================================
        # PLAN VALIDATION
        # ====================================================

        plan_error = (
            self._validate_plan_progress(
                plan,
                completed_steps
            )
        )

        if plan_error:

            return {
                "status": "failed",
                "reason": plan_error,
                "next_action": None
            }

        # ====================================================
        # NO PLAN
        # ====================================================

        if len(plan) == 0:

            return {
                "status": "failed",
                "reason": (
                    "No plan is available "
                    "for evaluation."
                ),
                "next_action": None
            }

        # ====================================================
        # ACTION RESULT VALIDATION
        # ====================================================

        last_action = self._last_action(
            state,
            plan
        )

        last_result = self._get_action_result(
            state
        )

        # ----------------------------------------------------
        # ACTION HISTORY VALIDATION
        # ----------------------------------------------------

        history_validation = (
            self._validate_action_history(
                state
            )
        )

        if history_validation is False:
            return {
                "status": "failed",
                "reason": (
                    "The most recent recorded action "
                    "failed according to action history."
                ),
                "next_action": None
            }

        action_validation = (
            self._validate_action_result(
                last_action,
                last_result
            )
        )

        if action_validation is False:

            return {
                "status": "failed",
                "reason": (
                    "The most recent action "
                    "has a deterministic failure result."
                ),
                "next_action": None
            }

        # ====================================================
        # ALL STEPS COMPLETED
        # ====================================================

        if len(completed_steps) >= len(plan):

            return {
                "status": "complete",
                "reason": (
                    "All planned actions have "
                    "been completed and no "
                    "deterministic failure was found."
                ),
                "next_action": None
            }

        # ====================================================
        # DETERMINE NEXT ACTION
        # ====================================================

        next_index = len(
            completed_steps
        )

        next_action = None

        if next_index < len(plan):

            next_action = plan[
                next_index
            ]

        # ====================================================
        # CONTINUE
        # ====================================================

        return {
            "status": "continue",
            "reason": (
                "The current action state is valid "
                "and additional planned actions remain."
            ),
            "next_action": next_action
        }

    # ========================================================
    # ACTION HISTORY
    # ========================================================

    def get_action_history(
        self,
        state
    ):
        """
        Return a safe copy of the recorded action history.
        """

        history = self._get(
            state,
            "action_history",
            []
        ) or []

        if isinstance(history, list):
            return list(history)

        return []

    # ========================================================
    # CONVENIENCE METHODS
    # ========================================================

    def is_complete(
        self,
        state
    ):
        """
        Return True when the task is complete.
        """

        result = self.evaluate(
            state
        )

        return (
            result["status"]
            == "complete"
        )

    # ========================================================

    def should_continue(
        self,
        state
    ):
        """
        Return True when more actions are required.
        """

        result = self.evaluate(
            state
        )

        return (
            result["status"]
            == "continue"
        )

    # ========================================================

    def has_failed(
        self,
        state
    ):
        """
        Return True when the task has failed.
        """

        result = self.evaluate(
            state
        )

        return (
            result["status"]
            == "failed"
        )


# ============================================================
# GLOBAL INSTANCE
# ============================================================

agent_evaluator = AgentEvaluator()