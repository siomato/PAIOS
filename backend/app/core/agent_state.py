# ============================================================
# app/core/agent_state.py
#
# PAIO AGENT STATE
#
# Purpose:
#
# Maintain the current state of an autonomous task.
#
# Phase 2:
#
# Goal
#   ↓
# Plan
#   ↓
# Execute
#   ↓
# Observe
#   ↓
# Update State
#   ↓
# Decide
#
# V2 ADDITION:
#
# AgentState
#      ↓
# TaskContext
#
# AgentState remains the compatibility layer used by the
# existing PAIOS modules.
#
# TaskContext provides richer task memory:
#
#   objective
#   plan
#   completed steps
#   failed steps
#   observations
#   action history
#   recovery history
#   progress
# ============================================================


from app.core.task_context import TaskContext


class AgentState:

    # ========================================================
    # INITIALIZATION
    # ========================================================

    def __init__(
        self,
        user_goal: str = ""
    ):

        # ----------------------------------------------------
        # TASK INFORMATION
        # ----------------------------------------------------

        self.user_goal = (
            user_goal.strip()
            if user_goal
            else ""
        )

        self.status = "initialized"

        # ----------------------------------------------------
        # TASK CONTEXT
        #
        # New V2 memory layer.
        #
        # None is allowed when AgentState is created without
        # a goal. This preserves the original behavior.
        # ----------------------------------------------------

        self.task_context = None

        if self.user_goal:

            self.task_context = TaskContext(
                objective=self.user_goal
            )

        # ----------------------------------------------------
        # PLANNING INFORMATION
        # ----------------------------------------------------

        self.current_plan = []

        self.current_step = 0

        self.completed_steps = []

        # ----------------------------------------------------
        # FAILURE INFORMATION
        # ----------------------------------------------------

        self.failed_step = None

        self.last_error = None

        # ----------------------------------------------------
        # BROWSER STATE
        # ----------------------------------------------------

        self.current_url = None

        self.page_title = None

        # ----------------------------------------------------
        # OBSERVATIONS
        # ----------------------------------------------------

        self.observations = []

        # ----------------------------------------------------
        # ACTION HISTORY
        #
        # New V2 compatibility history.
        # Existing modules do not depend on this yet.
        # ----------------------------------------------------

        self.action_history = []

        # ----------------------------------------------------
        # RECOVERY INFORMATION
        # ----------------------------------------------------

        self.retry_count = 0

        self.replans_used = 0

        self.replan_history = []

        # ----------------------------------------------------
        # RECOVERY HISTORY
        #
        # New V2 memory layer.
        # ----------------------------------------------------

        self.recovery_history = []

    # ========================================================
    # INTERNAL HELPERS
    # ========================================================

    def _ensure_task_context(self):

        if self.task_context is None:

            if not self.user_goal:

                raise ValueError(
                    "Cannot create TaskContext without "
                    "a user goal."
                )

            self.task_context = TaskContext(
                objective=self.user_goal
            )

    # ========================================================

    def _sync_task_context_status(self):

        if self.task_context is None:
            return

        if self.status == "running":

            if self.task_context.status != "running":

                self.task_context.start()

        elif self.status == "complete":

            self.task_context.complete()

        elif self.status == "failed":

            reason = (
                self.last_error
                or
                "AgentState reports failure."
            )

            self.task_context.fail(
                reason
            )

        elif self.status == "paused":

            self.task_context.pause()

    # ========================================================
    # GOAL
    # ========================================================

    def set_goal(
        self,
        user_goal: str
    ):

        if not isinstance(
            user_goal,
            str
        ):

            raise ValueError(
                "User goal must be a string."
            )

        user_goal = user_goal.strip()

        if not user_goal:

            raise ValueError(
                "User goal cannot be empty."
            )

        self.user_goal = user_goal

        # ----------------------------------------------------
        # Create or replace TaskContext for the new task.
        # ----------------------------------------------------

        self.task_context = TaskContext(
            objective=user_goal
        )

    # ========================================================
    # START TASK
    # ========================================================

    def start_task(self):

        self._ensure_task_context()

        self.status = "running"

        self.task_context.start()

    # ========================================================
    # PLAN
    # ========================================================

    def set_plan(
        self,
        plan
    ):

        if not isinstance(
            plan,
            list
        ):

            raise ValueError(
                "Plan must be a list."
            )

        self.current_plan = plan

        self.current_step = 0

        self.completed_steps = []

        self.failed_step = None

        self.last_error = None

        # ----------------------------------------------------
        # Synchronize TaskContext.
        # ----------------------------------------------------

        self._ensure_task_context()

        self.task_context.set_plan(
            plan
        )

    # ========================================================
    # CURRENT STEP
    # ========================================================

    def set_current_step(
        self,
        step_number
    ):

        if not isinstance(
            step_number,
            int
        ):

            raise ValueError(
                "Step number must be an integer."
            )

        if step_number < 0:

            raise ValueError(
                "Step number cannot be negative."
            )

        self.current_step = step_number

        # ----------------------------------------------------
        # Keep TaskContext aligned.
        # ----------------------------------------------------

        if self.task_context is not None:

            self.task_context.current_step = (
                step_number
            )

    # ========================================================
    # COMPLETED STEP
    # ========================================================

    def mark_step_completed(
        self,
        step_number,
        step=None,
        result=None
    ):

        record = {
            "step": step_number,
            "action": step
        }

        # ----------------------------------------------------
        # Preserve original AgentState behavior.
        # ----------------------------------------------------

        self.completed_steps.append(
            record
        )

        self.current_step = (
            step_number + 1
        )

        # ----------------------------------------------------
        # Synchronize TaskContext.
        # ----------------------------------------------------

        if self.task_context is not None:

            self.task_context.complete_current_step(
                result=result
            )

    # ========================================================
    # FAILED STEP
    # ========================================================

    def mark_step_failed(
        self,
        step_number,
        error
    ):

        self.failed_step = step_number

        self.last_error = str(
            error
        )

        # ----------------------------------------------------
        # Synchronize TaskContext.
        # ----------------------------------------------------

        if self.task_context is not None:

            self.task_context.fail_current_step(
                error=self.last_error
            )

    # ========================================================
    # OBSERVATION
    # ========================================================

    def add_observation(
        self,
        observation
    ):

        if observation is None:

            return

        # ----------------------------------------------------
        # Existing AgentState behavior.
        # ----------------------------------------------------

        self.observations.append(
            observation
        )

        # ----------------------------------------------------
        # TaskContext memory.
        # ----------------------------------------------------

        if self.task_context is not None:

            self.task_context.add_observation(
                observation
            )

    # ========================================================
    # ACTION HISTORY
    # ========================================================

    def record_action(
        self,
        action,
        result=None,
        success=True,
        error=None
    ):

        record = {
            "step_index":
                self.current_step,

            "action":
                action,

            "result":
                result,

            "success":
                success,

            "error":
                error
        }

        self.action_history.append(
            record
        )

        # ----------------------------------------------------
        # TaskContext memory.
        # ----------------------------------------------------

        if self.task_context is not None:

            self.task_context.record_action(
                action=action,
                result=result,
                success=success,
                error=error
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

            self.current_url = current_url

        if page_title is not None:

            self.page_title = page_title

        # ----------------------------------------------------
        # Browser state is also useful as an observation.
        # ----------------------------------------------------

        if self.task_context is not None:

            self.task_context.add_observation(
                {
                    "type": "browser_state",

                    "current_url":
                        self.current_url,

                    "page_title":
                        self.page_title
                }
            )

    # ========================================================
    # RETRY
    # ========================================================

    def increment_retry(
        self
    ):

        self.retry_count += 1

        # ----------------------------------------------------
        # Record retry as an action/recovery observation.
        # ----------------------------------------------------

        if self.task_context is not None:

            self.task_context.record_recovery(
                strategy="retry",
                result={
                    "retry_count":
                        self.retry_count
                },
                success=False
            )

    # ========================================================
    # REPLAN
    # ========================================================

    def record_replan(
        self,
        old_plan,
        new_plan,
        reason=""
    ):

        record = {
            "old_plan": old_plan,
            "new_plan": new_plan,
            "reason": reason
        }

        # ----------------------------------------------------
        # Preserve existing AgentState behavior.
        # ----------------------------------------------------

        self.replan_history.append(
            record
        )

        self.replans_used += 1

        # ----------------------------------------------------
        # TaskContext recovery memory.
        # ----------------------------------------------------

        if self.task_context is not None:

            self.task_context.record_recovery(
                strategy="replan",
                result={
                    "old_plan": old_plan,
                    "new_plan": new_plan
                },
                success=True,
                error=reason
            )

    # ========================================================
    # STATUS
    # ========================================================

    def set_status(
        self,
        status
    ):

        if not isinstance(
            status,
            str
        ):

            raise ValueError(
                "Status must be a string."
            )

        status = status.strip()

        self.status = status

        # ----------------------------------------------------
        # Synchronize TaskContext.
        # ----------------------------------------------------

        if self.task_context is not None:

            if status == "running":

                self.task_context.start()

            elif status == "complete":

                self.task_context.complete()

            elif status == "failed":

                self.task_context.fail(
                    self.last_error
                    or
                    "AgentState reports failure."
                )

            elif status == "paused":

                self.task_context.pause()

    # ========================================================
    # TASK CONTEXT
    # ========================================================

    def get_task_context(
        self
    ):

        self._ensure_task_context()

        return self.task_context

    # ========================================================

    def task_progress(
        self
    ):

        if self.task_context is None:

            total = len(
                self.current_plan
            )

            completed = len(
                self.completed_steps
            )

            percentage = (
                0
                if total == 0
                else
                int(
                    (
                        completed
                        /
                        total
                    )
                    * 100
                )
            )

            return {
                "current_step":
                    self.current_step,

                "total_steps":
                    total,

                "completed_steps":
                    completed,

                "failed_steps":
                    (
                        1
                        if self.failed_step is not None
                        else
                        0
                    ),

                "percentage":
                    percentage
            }

        return self.task_context.progress()

    # ========================================================
    # SNAPSHOT
    # ========================================================

    def snapshot(
        self
    ):

        snapshot = {
            # ------------------------------------------------
            # Existing AgentState fields
            # ------------------------------------------------

            "user_goal":
                self.user_goal,

            "status":
                self.status,

            "current_plan":
                self.current_plan.copy(),

            "current_step":
                self.current_step,

            "completed_steps":
                self.completed_steps.copy(),

            "failed_step":
                self.failed_step,

            "last_error":
                self.last_error,

            "current_url":
                self.current_url,

            "page_title":
                self.page_title,

            "observations":
                self.observations.copy(),

            "retry_count":
                self.retry_count,

            "replans_used":
                self.replans_used,

            "replan_history":
                self.replan_history.copy(),

            # ------------------------------------------------
            # New V2 fields
            # ------------------------------------------------

            "action_history":
                self.action_history.copy(),

            "recovery_history":
                self.recovery_history.copy(),

            "task_context":
                (
                    self.task_context.to_dict()
                    if self.task_context is not None
                    else None
                )
        }

        return snapshot

    # ========================================================
    # SUMMARY
    # ========================================================

    def summary(
        self
    ):

        progress = (
            self.task_progress()
        )

        return {
            "goal":
                self.user_goal,

            "status":
                self.status,

            "current_step":
                progress["current_step"],

            "total_steps":
                progress["total_steps"],

            "completed":
                progress["completed_steps"],

            "failed":
                progress["failed_steps"],

            "progress":
                progress["percentage"],

            "observations":
                len(self.observations),

            "actions":
                len(self.action_history),

            "retries":
                self.retry_count,

            "replans":
                self.replans_used
        }

    # ========================================================
    # DEBUG
    # ========================================================

    def print_state(
        self
    ):

        print("\n")
        print("=" * 60)
        print("🧠 PAIO AGENT STATE")
        print("=" * 60)

        print(
            f"Goal          : {self.user_goal}"
        )

        print(
            f"Status        : {self.status}"
        )

        print(
            f"Current step  : {self.current_step}"
        )

        print(
            f"Completed     : {len(self.completed_steps)}"
        )

        print(
            f"Failed step   : {self.failed_step}"
        )

        print(
            f"Current URL   : {self.current_url}"
        )

        print(
            f"Page title    : {self.page_title}"
        )

        print(
            f"Observations  : {len(self.observations)}"
        )

        print(
            f"Actions       : {len(self.action_history)}"
        )

        print(
            f"Retries       : {self.retry_count}"
        )

        print(
            f"Replans       : {self.replans_used}"
        )

        # ----------------------------------------------------
        # TaskContext summary
        # ----------------------------------------------------

        if self.task_context is not None:

            context_summary = (
                self.task_context.summary()
            )

            print(
                f"Task ID       : "
                f"{context_summary['task_id']}"
            )

            print(
                f"Recoveries    : "
                f"{context_summary['recoveries']}"
            )

        print("=" * 60)


# ============================================================
# GLOBAL FACTORY
# ============================================================

def create_agent_state(
    user_goal: str
):

    return AgentState(
        user_goal
    )