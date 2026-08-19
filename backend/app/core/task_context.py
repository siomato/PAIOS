# ============================================================
# app/core/task_context.py
#
# PAIOS TASK CONTEXT
#
# Purpose:
#
# Maintain structured context for one autonomous task.
#
# Task
#   ↓
# TaskContext
#   ├── objective
#   ├── status
#   ├── current step
#   ├── completed steps
#   ├── failed steps
#   ├── observations
#   ├── action history
#   └── recovery history
#
# V1:
#   Deterministic
#   No LLM
#   No database
# ============================================================

from datetime import datetime
from typing import Any, Dict, List, Optional
import uuid


class TaskContext:

    # ========================================================
    # INITIALIZATION
    # ========================================================

    def __init__(
        self,
        objective: str,
        task_id: Optional[str] = None
    ):

        if not objective:
            raise ValueError(
                "Task objective cannot be empty."
            )

        self.task_id = (
            task_id
            or str(uuid.uuid4())
        )

        self.objective = objective.strip()

        self.status = "pending"

        self.created_at = (
            datetime.utcnow().isoformat()
        )

        self.updated_at = self.created_at

        # ----------------------------------------------------
        # PLAN
        # ----------------------------------------------------

        self.plan: List[Any] = []

        self.current_step = 0

        self.completed_steps: List[Any] = []

        self.failed_steps: List[Any] = []

        # ----------------------------------------------------
        # OBSERVATIONS
        # ----------------------------------------------------

        self.observations: List[Dict[str, Any]] = []

        # ----------------------------------------------------
        # ACTION HISTORY
        # ----------------------------------------------------

        self.action_history: List[Dict[str, Any]] = []

        # ----------------------------------------------------
        # RECOVERY HISTORY
        # ----------------------------------------------------

        self.recovery_history: List[Dict[str, Any]] = []

    # ========================================================
    # INTERNAL UPDATE
    # ========================================================

    def _touch(self):

        self.updated_at = (
            datetime.utcnow().isoformat()
        )

    # ========================================================
    # TASK STATUS
    # ========================================================

    def start(self):

        self.status = "running"

        self._touch()

    # ========================================================

    def complete(self):

        self.status = "complete"

        self._touch()

    # ========================================================

    def fail(
        self,
        reason: str
    ):

        self.status = "failed"

        self.add_observation(
            {
                "type": "task_failure",
                "reason": reason
            }
        )

        self._touch()

    # ========================================================

    def pause(self):

        self.status = "paused"

        self._touch()

    # ========================================================

    # PLAN MANAGEMENT
    # ========================================================

    def set_plan(
        self,
        plan: List[Any]
    ):

        if plan is None:
            plan = []

        self.plan = list(plan)

        self.current_step = 0

        self.completed_steps = []

        self.failed_steps = []

        self._touch()

    # ========================================================

    def has_next_step(self) -> bool:

        return (
            self.current_step
            <
            len(self.plan)
        )

    # ========================================================

    def get_current_step(self):

        if not self.has_next_step():
            return None

        return self.plan[
            self.current_step
        ]

    # ========================================================

    def complete_current_step(
        self,
        result: Any = None
    ):

        if not self.has_next_step():
            return False

        step = self.plan[
            self.current_step
        ]

        self.completed_steps.append(
            {
                "index": self.current_step,
                "step": step,
                "result": result,
                "completed_at":
                    datetime.utcnow().isoformat()
            }
        )

        self.current_step += 1

        self._touch()

        return True

    # ========================================================

    def fail_current_step(
        self,
        error: str
    ):

        if not self.has_next_step():
            return False

        step = self.plan[
            self.current_step
        ]

        self.failed_steps.append(
            {
                "index": self.current_step,
                "step": step,
                "error": error,
                "failed_at":
                    datetime.utcnow().isoformat()
            }
        )

        self._touch()

        return True

    # ========================================================
    # OBSERVATIONS
    # ========================================================

    def add_observation(
        self,
        observation: Any
    ):

        entry = {
            "timestamp":
                datetime.utcnow().isoformat(),
            "data": observation
        }

        self.observations.append(
            entry
        )

        self._touch()

    # ========================================================

    def get_latest_observation(self):

        if not self.observations:
            return None

        return self.observations[-1]

    # ========================================================
    # ACTION HISTORY
    # ========================================================

    def record_action(
        self,
        action: Any,
        result: Any = None,
        success: bool = True,
        error: Optional[str] = None
    ):

        entry = {
            "timestamp":
                datetime.utcnow().isoformat(),

            "step_index":
                self.current_step,

            "action":
                action,

            "success":
                success,

            "result":
                result,

            "error":
                error
        }

        self.action_history.append(
            entry
        )

        self._touch()

    # ========================================================
    # RECOVERY HISTORY
    # ========================================================

    def record_recovery(
        self,
        strategy: str,
        result: Any = None,
        success: bool = False,
        error: Optional[str] = None
    ):

        entry = {
            "timestamp":
                datetime.utcnow().isoformat(),

            "step_index":
                self.current_step,

            "strategy":
                strategy,

            "success":
                success,

            "result":
                result,

            "error":
                error
        }

        self.recovery_history.append(
            entry
        )

        self._touch()

    # ========================================================
    # PROGRESS
    # ========================================================

    def progress(self) -> Dict[str, Any]:

        total = len(
            self.plan
        )

        completed = len(
            self.completed_steps
        )

        percentage = (
            0
            if total == 0
            else
            int(
                (completed / total)
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
                len(self.failed_steps),

            "percentage":
                percentage
        }

    # ========================================================
    # SERIALIZATION
    # ========================================================

    def to_dict(self) -> Dict[str, Any]:

        return {
            "task_id":
                self.task_id,

            "objective":
                self.objective,

            "status":
                self.status,

            "created_at":
                self.created_at,

            "updated_at":
                self.updated_at,

            "plan":
                self.plan,

            "current_step":
                self.current_step,

            "completed_steps":
                self.completed_steps,

            "failed_steps":
                self.failed_steps,

            "observations":
                self.observations,

            "action_history":
                self.action_history,

            "recovery_history":
                self.recovery_history
        }

    # ========================================================

    def summary(self) -> Dict[str, Any]:

        return {
            "task_id":
                self.task_id,

            "objective":
                self.objective,

            "status":
                self.status,

            "progress":
                self.progress(),

            "observations":
                len(self.observations),

            "actions":
                len(self.action_history),

            "recoveries":
                len(self.recovery_history)
        }


# ============================================================
# GLOBAL FACTORY
# ============================================================

def create_task_context(
    objective: str
) -> TaskContext:

    return TaskContext(
        objective=objective
    )