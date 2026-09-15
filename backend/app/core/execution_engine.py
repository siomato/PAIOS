from app.core.action_executor import action_executor
from app.core.recovery_engine import recovery_engine
from app.core.replanner import replanner


class ExecutionEngine:

    MAX_REPLANS = 3

    def __init__(self):
        self.replans_used = 0
        print("⚙️ EXECUTION ENGINE MODULE LOADED ⚙️")

    def reset(self):
        self.replans_used = 0

    def _validate_plan(self, steps):
        return (
            isinstance(steps, list)
            and bool(steps)
            and all(
                isinstance(step, dict) and step.get("action")
                for step in steps
            )
        )

    def _get_failed_action(self, plan, failed_step):
        if (
            not isinstance(plan, list)
            or not isinstance(failed_step, int)
            or failed_step < 1
            or failed_step > len(plan)
        ):
            return None
        return plan[failed_step - 1]

    def _remaining_steps(self, plan, failed_step):
        if not isinstance(plan, list) or not isinstance(failed_step, int):
            return []
        return list(plan[failed_step:])

    def execute_plan(self, steps):
        self.reset()

        if not self._validate_plan(steps):
            return {
                "status": "failed",
                "steps": [],
                "results": [],
                "failed_step": None,
                "error": "Invalid or empty execution plan.",
                "replans_used": 0,
                "final_plan": [],
            }

        current_plan = list(steps)
        history = []

        while True:
            print("\n========================================")
            print("         ⚙️ EXECUTION ENGINE")
            print("========================================")

            for i, step in enumerate(current_plan, 1):
                print(f"{i}. {step}")

            try:
                result = action_executor.execute(current_plan)
            except Exception as exc:
                result = {
                    "status": "failed",
                    "steps": [],
                    "results": [],
                    "failed_step": 1,
                    "error": str(exc),
                    "recoverable": True,
                }

            if not isinstance(result, dict):
                result = {
                    "status": "failed",
                    "steps": [],
                    "results": [],
                    "failed_step": 1,
                    "error": "Action executor returned an invalid result.",
                    "recoverable": True,
                }

            history.append(result)

            if result.get("status") == "success":
                return {
                    "status": "success",
                    "steps": history,
                    "results": history,
                    "failed_step": None,
                    "error": None,
                    "replans_used": self.replans_used,
                    "final_plan": current_plan,
                }

            failed_step = result.get("failed_step", 1)
            error = result.get("error", "Unknown execution failure.")

            if not isinstance(failed_step, int):
                failed_step = 1

            failed_step = max(1, min(failed_step, len(current_plan)))
            failed_action = self._get_failed_action(
                current_plan,
                failed_step
            )

            if failed_action is None:
                return {
                    "status": "failed",
                    "steps": history,
                    "results": history,
                    "failed_step": failed_step,
                    "error": "Could not identify the failed action.",
                    "replans_used": self.replans_used,
                    "final_plan": current_plan,
                }

            # Action-level recovery only.
            try:
                recovery_result = recovery_engine.recover(
                    failed_action,
                    error
                )
            except Exception as exc:
                recovery_result = {
                    "status": "failed",
                    "error": str(exc),
                    "recovered": False,
                }

            history.append({
                "status": "recovery",
                "failed_step": failed_step,
                "action": failed_action,
                "result": recovery_result,
            })

            if (
                isinstance(recovery_result, dict)
                and recovery_result.get("status") == "success"
            ):
                current_plan = self._remaining_steps(
                    current_plan,
                    failed_step
                )

                if not current_plan:
                    return {
                        "status": "success",
                        "steps": history,
                        "results": history,
                        "failed_step": None,
                        "error": None,
                        "replans_used": self.replans_used,
                        "final_plan": [],
                    }

                continue

            if self.replans_used >= self.MAX_REPLANS:
                return {
                    "status": "failed",
                    "steps": history,
                    "results": history,
                    "failed_step": failed_step,
                    "error": error,
                    "replans_used": self.replans_used,
                    "final_plan": current_plan,
                }

            self.replans_used += 1

            try:
                replan_result = replanner.replan(
                    current_plan,
                    failed_step,
                    error
                )
            except Exception as exc:
                return {
                    "status": "failed",
                    "steps": history,
                    "results": history,
                    "failed_step": failed_step,
                    "error": str(exc),
                    "replans_used": self.replans_used,
                    "final_plan": current_plan,
                }

            if not isinstance(replan_result, dict):
                return {
                    "status": "failed",
                    "steps": history,
                    "results": history,
                    "failed_step": failed_step,
                    "error": "Replanner returned an invalid result.",
                    "replans_used": self.replans_used,
                    "final_plan": current_plan,
                }

            if replan_result.get("status") != "success":
                return {
                    "status": "failed",
                    "steps": history,
                    "results": history,
                    "failed_step": failed_step,
                    "error": replan_result.get(
                        "error",
                        "Replanning failed."
                    ),
                    "replans_used": self.replans_used,
                    "final_plan": current_plan,
                }

            replacement = (
                replan_result.get("steps")
                or replan_result.get("actions")
                or []
            )

            if not isinstance(replacement, list) or not replacement:
                return {
                    "status": "failed",
                    "steps": history,
                    "results": history,
                    "failed_step": failed_step,
                    "error": "Replanner generated no replacement actions.",
                    "replans_used": self.replans_used,
                    "final_plan": current_plan,
                }

            remaining = self._remaining_steps(
                current_plan,
                failed_step
            )

            current_plan = list(replacement) + remaining


execution_engine = ExecutionEngine()
