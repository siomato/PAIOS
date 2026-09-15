# ============================================================
# app/core/agent_state.py
#
# PAIOS / ULTRON AGENT STATE
#
# Purpose:
#   Single source of truth for autonomous execution.
#
# Responsibilities:
#   - Track task
#   - Track plan
#   - Track current action
#   - Track completed steps
#   - Track failed step
#   - Track action history
#   - Track observations
#   - Track browser state
#   - Track execution status
#
# No Playwright objects belong here.
# ============================================================


class AgentState:

    # ========================================================
    # INITIALIZATION
    # ========================================================

    def __init__(
        self,
        user_message=None,
        current_plan=None,
        plan_id=None
    ):

        # ----------------------------------------------------
        # TASK
        # ----------------------------------------------------

        self.user_message = (
            user_message
            if user_message is not None
            else ""
        )

        # ----------------------------------------------------
        # PLAN
        # ----------------------------------------------------

        self.current_plan = (
            list(current_plan)
            if isinstance(current_plan, list)
            else []
        )

        self.plan_id = plan_id

        # ----------------------------------------------------
        # EXECUTION POINTER
        # ----------------------------------------------------

        self.current_step = 0

        self.current_action = None

        # ----------------------------------------------------
        # PROGRESS
        # ----------------------------------------------------

        self.completed_steps = []

        self.failed_step = None

        # ----------------------------------------------------
        # EXECUTION RESULTS
        # ----------------------------------------------------

        self.last_result = None

        self.last_action_result = None

        self.action_result = None

        self.last_execution_result = None

        self.execution_result = None

        self.last_error = None

        # ----------------------------------------------------
        # HISTORY
        # ----------------------------------------------------

        self.action_history = []

        self.observations = []

        # ----------------------------------------------------
        # BROWSER STATE
        # ----------------------------------------------------

        self.current_url = None

        self.page_title = None

        self.browser_state = {}

        # ----------------------------------------------------
        # RECOVERY
        # ----------------------------------------------------

        self.retry_count = 0

        self.replans_used = 0

        self.replan_history = []

        # ----------------------------------------------------
        # GLOBAL STATUS
        #
        # Possible values:
        #
        #   idle
        #   running
        #   completed
        #   failed
        # ----------------------------------------------------

        self.status = "idle"

        # ----------------------------------------------------
        # VERSION
        # ----------------------------------------------------

        self.state_version = 1

    # ========================================================
    # TASK
    # ========================================================

    def set_task(
        self,
        user_message
    ):

        self.user_message = (
            user_message
            if user_message is not None
            else ""
        )

    # ========================================================
    # PLAN
    # ========================================================

    def set_plan(
        self,
        plan,
        plan_id=None
    ):

        if not isinstance(
            plan,
            list
        ):
            raise ValueError(
                "Plan must be a list."
            )

        self.current_plan = list(plan)

        if plan_id is not None:
            self.plan_id = plan_id

        self.current_step = 0

        self.current_action = None

        self.completed_steps = []

        self.failed_step = None

        self.last_error = None

        self.status = "running"

    # ========================================================
    # CURRENT STEP
    # ========================================================

    def set_current_step(
        self,
        step_number
    ):

        if step_number is None:
            self.current_step = 0
            return

        try:

            step_number = int(
                step_number
            )

        except (
            TypeError,
            ValueError
        ):

            raise ValueError(
                "Step number must be an integer."
            )

        if step_number < 0:
            raise ValueError(
                "Step number cannot be negative."
            )

        self.current_step = (
            step_number
        )

        # ----------------------------------------------------
        # Automatically attach current action
        # ----------------------------------------------------

        index = step_number - 1

        if (
            0 <= index
            < len(self.current_plan)
        ):

            self.current_action = (
                self.current_plan[index]
            )

    # ========================================================
    # CURRENT ACTION
    # ========================================================

    def set_current_action(
        self,
        action
    ):

        if action is not None and not isinstance(
            action,
            dict
        ):

            raise ValueError(
                "Current action must be a dictionary."
            )

        self.current_action = action

    # ========================================================
    # ACTION RECORD
    # ========================================================

    def record_action(
        self,
        action,
        result=None,
        success=False,
        error=None
    ):

        # ----------------------------------------------------
        # Normalize
        # ----------------------------------------------------

        if not isinstance(
            action,
            dict
        ):

            action = {
                "action": str(action)
            }

        # ----------------------------------------------------
        # Determine step
        # ----------------------------------------------------

        step_number = (
            action.get(
                "step_index"
            )
        )

        if step_number is None:

            step_number = (
                self.current_step
            )

        # ----------------------------------------------------
        # Record current action
        # ----------------------------------------------------

        self.current_action = (
            action
        )

        # ----------------------------------------------------
        # Store result in all compatibility fields
        # ----------------------------------------------------

        self.last_result = result

        self.last_action_result = result

        self.action_result = result

        self.last_execution_result = result

        self.execution_result = result

        # ----------------------------------------------------
        # Error
        # ----------------------------------------------------

        if error is not None:

            self.last_error = str(
                error
            )

        elif isinstance(
            result,
            dict
        ):

            result_error = result.get(
                "error"
            )

            if result_error:

                self.last_error = str(
                    result_error
                )

        # ----------------------------------------------------
        # Normalize success
        # ----------------------------------------------------

        if success:

            self.status = "running"

        # ----------------------------------------------------
        # History entry
        # ----------------------------------------------------

        history_entry = {

            "step": step_number,

            "action": dict(
                action
            ),

            "result": result,

            "success": bool(
                success
            ),

            "error": (
                str(error)
                if error is not None
                else None
            )
        }

        self.action_history.append(
            history_entry
        )

    # ========================================================
    # COMPLETE STEP
    # ========================================================

    def mark_step_completed(
        self,
        step_number,
        action=None
    ):

        try:

            step_number = int(
                step_number
            )

        except (
            TypeError,
            ValueError
        ):

            raise ValueError(
                "Step number must be an integer."
            )

        if step_number <= 0:

            raise ValueError(
                "Step number must be greater than zero."
            )

        # ----------------------------------------------------
        # Prevent duplicate completed steps
        # ----------------------------------------------------

        already_completed = False

        for item in self.completed_steps:

            if isinstance(
                item,
                dict
            ):

                if item.get(
                    "step"
                ) == step_number:

                    already_completed = True

                    break

            elif item == step_number:

                already_completed = True

                break

        # ----------------------------------------------------
        # Add completion record
        # ----------------------------------------------------

        if not already_completed:

            completion_record = {

                "step": step_number,

                "action": (
                    dict(action)
                    if isinstance(
                        action,
                        dict
                    )
                    else action
                )
            }

            self.completed_steps.append(
                completion_record
            )

        # ----------------------------------------------------
        # Keep ordered
        # ----------------------------------------------------

        self.completed_steps.sort(
            key=lambda item:
                item.get(
                    "step",
                    0
                )
                if isinstance(
                    item,
                    dict
                )
                else item
        )

        # ----------------------------------------------------
        # Clear failure
        # ----------------------------------------------------

        if self.failed_step == step_number:

            self.failed_step = None

        # ----------------------------------------------------
        # Update current pointer
        # ----------------------------------------------------

        self.current_step = step_number

        # ----------------------------------------------------
        # Determine task completion
        # ----------------------------------------------------

        if (
            self.current_plan
            and
            len(
                self.completed_steps
            )
            >=
            len(
                self.current_plan
            )
        ):

            self.status = "completed"

        else:

            self.status = "running"

    # ========================================================
    # FAILED STEP
    # ========================================================

    def mark_step_failed(
        self,
        step_number,
        error
    ):

        try:

            step_number = int(
                step_number
            )

        except (
            TypeError,
            ValueError
        ):

            raise ValueError(
                "Step number must be an integer."
            )

        self.failed_step = (
            step_number
        )

        self.last_error = str(
            error
        )

        self.status = "failed"

    # ========================================================
    # OBSERVATION
    # ========================================================

    def add_observation(
        self,
        observation
    ):

        if not isinstance(
            observation,
            dict
        ):

            observation = {
                "value": observation
            }

        self.observations.append(
            dict(observation)
        )

    # ========================================================
    # BROWSER STATE
    # ========================================================

    def update_browser_state(
        self,
        current_url=None,
        page_title=None
    ):

        if current_url is not None:

            self.current_url = str(
                current_url
            )

        if page_title is not None:

            self.page_title = str(
                page_title
            )

        self.browser_state = {

            "current_url":
                self.current_url,

            "page_title":
                self.page_title
        }

    # ========================================================
    # RETRY
    # ========================================================

    def set_retry_count(
        self,
        count
    ):

        try:

            count = int(
                count
            )

        except (
            TypeError,
            ValueError
        ):

            raise ValueError(
                "Retry count must be an integer."
            )

        if count < 0:

            raise ValueError(
                "Retry count cannot be negative."
            )

        self.retry_count = count

    def increment_retry(
        self
    ):

        self.retry_count += 1

        return self.retry_count

    # ========================================================
    # REPLANNING
    # ========================================================

    def record_replan(
        self,
        old_plan=None,
        new_plan=None,
        reason=None
    ):

        self.replans_used += 1

        record = {

            "replan_number":
                self.replans_used,

            "old_plan":
                (
                    list(old_plan)
                    if isinstance(
                        old_plan,
                        list
                    )
                    else old_plan
                ),

            "new_plan":
                (
                    list(new_plan)
                    if isinstance(
                        new_plan,
                        list
                    )
                    else new_plan
                ),

            "reason": reason
        }

        self.replan_history.append(
            record
        )

    # ========================================================
    # RESET CURRENT ACTION
    # ========================================================

    def clear_current_action(
        self
    ):

        self.current_action = None

    # ========================================================
    # CLEAR FAILURE
    # ========================================================

    def clear_failure(
        self
    ):

        self.failed_step = None

        self.last_error = None

        if self.status == "failed":

            self.status = "running"

    # ========================================================
    # COMPLETE TASK
    # ========================================================

    def mark_completed(
        self
    ):

        self.failed_step = None

        self.last_error = None

        self.status = "completed"

    # ========================================================
    # FAIL TASK
    # ========================================================

    def mark_failed(
        self,
        error=None
    ):

        if error is not None:

            self.last_error = str(
                error
            )

        self.status = "failed"

    # ========================================================
    # PROGRESS
    # ========================================================

    def completed_count(
        self
    ):

        return len(
            self.completed_steps
        )

    def total_steps(
        self
    ):

        return len(
            self.current_plan
        )

    def remaining_steps(
        self
    ):

        return max(
            0,
            self.total_steps()
            -
            self.completed_count()
        )

    # ========================================================
    # STATUS HELPERS
    # ========================================================

    def is_complete(
        self
    ):

        return (
            self.status
            == "completed"
        )

    def is_failed(
        self
    ):

        return (
            self.status
            == "failed"
        )

    def is_running(
        self
    ):

        return (
            self.status
            == "running"
        )

    # ========================================================
    # SERIALIZATION
    # ========================================================

    def to_dict(
        self
    ):

        return {

            "user_message":
                self.user_message,

            "plan_id":
                self.plan_id,

            "current_plan":
                list(
                    self.current_plan
                ),

            "current_step":
                self.current_step,

            "current_action":
                self.current_action,

            "completed_steps":
                list(
                    self.completed_steps
                ),

            "failed_step":
                self.failed_step,

            "last_result":
                self.last_result,

            "last_error":
                self.last_error,

            "action_history":
                list(
                    self.action_history
                ),

            "observations":
                list(
                    self.observations
                ),

            "current_url":
                self.current_url,

            "page_title":
                self.page_title,

            "browser_state":
                dict(
                    self.browser_state
                ),

            "retry_count":
                self.retry_count,

            "replans_used":
                self.replans_used,

            "replan_history":
                list(
                    self.replan_history
                ),

            "status":
                self.status,

            "state_version":
                self.state_version
        }

    # ========================================================
    # DEBUG
    # ========================================================

    def summary(
        self
    ):

        return {

            "status":
                self.status,

            "current_step":
                self.current_step,

            "completed":
                self.completed_count(),

            "total":
                self.total_steps(),

            "remaining":
                self.remaining_steps(),

            "failed_step":
                self.failed_step,

            "retry_count":
                self.retry_count,

            "replans_used":
                self.replans_used,

            "current_url":
                self.current_url,

            "page_title":
                self.page_title
        }

    def __repr__(
        self
    ):

        return (
            "AgentState("
            f"status={self.status!r}, "
            f"step={self.current_step}, "
            f"completed="
            f"{self.completed_count()}/"
            f"{self.total_steps()}, "
            f"failed_step="
            f"{self.failed_step!r})"
        )


# ============================================================
# GLOBAL INSTANCE
# ============================================================

agent_state = AgentState()


print(
    "🧠 AGENT STATE MODULE LOADED 🧠"
)