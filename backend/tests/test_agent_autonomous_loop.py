# ============================================================
# tests/test_agent_autonomous_loop.py
#
# PAIO AUTONOMOUS EXECUTION LOOP TEST
#
# Purpose:
#
# Verify the complete:
#
#     EXECUTE
#        ↓
#     OBSERVE
#        ↓
#     AGENT STATE
#        ↓
#     EVALUATE
#        ↓
#     CONTINUE
#        ↓
#     NEXT ACTION
#        ↓
#     EXECUTE
#        ↓
#     OBSERVE
#        ↓
#     AGENT STATE
#        ↓
#     EVALUATE
#        ↓
#     COMPLETE
#
# This test intentionally does NOT modify the controller,
# replanner, or recovery engine.
#
# It proves that the existing components can participate
# in one autonomous control loop.
#
# ============================================================


from app.core.agent_state import AgentState
from app.core.action_executor import action_executor
from app.core.agent_evaluator import agent_evaluator


# ============================================================
# CONFIGURATION
# ============================================================

USER_GOAL = (
    "Search for Python tutorials "
    "and click first search result"
)

PLAN = [
    {
        "action": "search",
        "query": "Python tutorials"
    },
    {
        "action": "click",
        "target": "first search result"
    }
]


# ============================================================
# HEADER
# ============================================================

print("\n")
print("=" * 70)
print("🤖 PAIO — AUTONOMOUS EXECUTION LOOP TEST")
print("=" * 70)

print("\nUSER GOAL")
print("-" * 70)

print(USER_GOAL)

print("\nPLAN")
print("-" * 70)

for index, action in enumerate(
    PLAN,
    start=1
):

    print(
        f"{index}. {action}"
    )


# ============================================================
# CREATE AGENT STATE
# ============================================================

print("\n")
print("=" * 70)
print("🧠 INITIALIZING AGENT STATE")
print("=" * 70)


state = AgentState(
    USER_GOAL
)

state.set_plan(
    PLAN
)

state.set_status(
    "executing"
)


print(
    "✅ AgentState initialized."
)

print(
    f"Goal: {state.user_goal}"
)

print(
    f"Plan steps: {len(state.current_plan)}"
)


# ============================================================
# LOOP CONTROL
# ============================================================

loop_count = 0

max_loops = len(
    PLAN
) + 1


# ============================================================
# AUTONOMOUS LOOP
# ============================================================

while loop_count < max_loops:

    loop_count += 1

    print("\n")
    print("=" * 70)
    print(
        f"🔄 AUTONOMOUS LOOP ITERATION #{loop_count}"
    )
    print("=" * 70)

    # ========================================================
    # EVALUATE CURRENT STATE
    # ========================================================

    print("\n🧠 Evaluating current state...")

    evaluation = agent_evaluator.evaluate(
        state
    )

    print(
        f"Evaluation: {evaluation}"
    )

    evaluation_status = evaluation.get(
        "status"
    )

    # ========================================================
    # COMPLETE
    # ========================================================

    if evaluation_status == "complete":

        print(
            "\n🎯 EVALUATOR → COMPLETE"
        )

        print(
            "No additional action is required."
        )

        break

    # ========================================================
    # FAILED
    # ========================================================

    if evaluation_status == "failed":

        print(
            "\n❌ EVALUATOR → FAILED"
        )

        print(
            f"Reason: "
            f"{evaluation.get('reason')}"
        )

        raise AssertionError(
            "Autonomous loop entered FAILED state."
        )

    # ========================================================
    # CONTINUE
    # ========================================================

    if evaluation_status != "continue":

        raise AssertionError(
            f"Unexpected evaluator status: "
            f"{evaluation_status}"
        )

    print(
        "\n🔄 EVALUATOR → CONTINUE"
    )

    # --------------------------------------------------------
    # Get next action
    # --------------------------------------------------------

    next_action = evaluation.get(
        "next_action"
    )

    print(
        f"Next action: {next_action}"
    )

    if next_action is None:

        raise AssertionError(
            "Evaluator requested CONTINUE "
            "but returned no next action."
        )

    # ========================================================
    # DETERMINE EXPECTED ACTION
    # ========================================================

    completed_count = len(
        state.completed_steps
    )

    if completed_count >= len(PLAN):

        raise AssertionError(
            "No actions should remain when "
            "all plan steps are completed."
        )

    expected_action = PLAN[
        completed_count
    ]

    print(
        f"Expected action: {expected_action}"
    )

    # --------------------------------------------------------
    # Validate evaluator's selected action
    # --------------------------------------------------------

    if next_action != expected_action:

        raise AssertionError(
            "Evaluator selected an incorrect "
            "next action."
        )

    print(
        "✅ Correct next action selected."
    )

    # ========================================================
    # EXECUTE ONLY THE NEXT ACTION
    # ========================================================

    print("\n")
    print(
        "🚀 Executing selected next action..."
    )

    single_action_plan = [
        next_action
    ]

    execution_result = action_executor.execute(
        single_action_plan,
        state=state
    )

    print("\nExecution result:")

    print(
        execution_result
    )

    # ========================================================
    # VALIDATE EXECUTION
    # ========================================================

    if not isinstance(
        execution_result,
        dict
    ):

        raise AssertionError(
            "Executor did not return a dictionary."
        )

    if execution_result.get(
        "status"
    ) != "success":

        raise AssertionError(
            "Selected action failed during "
            "autonomous execution."
        )

    print(
        "✅ Selected action executed successfully."
    )

    # ========================================================
    # SHOW UPDATED STATE
    # ========================================================

    print("\n")
    print(
        "🧠 UPDATED AGENT STATE"
    )

    print(
        f"Status       : {state.status}"
    )

    print(
        f"Current step : {state.current_step}"
    )

    print(
        f"Completed    : "
        f"{len(state.completed_steps)}"
    )

    print(
        f"Observations : "
        f"{len(state.observations)}"
    )

    print(
        f"Current URL  : "
        f"{state.current_url}"
    )

    print(
        f"Page title   : "
        f"{state.page_title}"
    )

    print(
        f"Failed step  : "
        f"{state.failed_step}"
    )


# ============================================================
# LOOP TERMINATION VALIDATION
# ============================================================

print("\n")
print("=" * 70)
print("🔎 AUTONOMOUS LOOP VALIDATION")
print("=" * 70)


# ============================================================
# CHECK 1 — LOOP TERMINATED
# ============================================================

if loop_count <= max_loops:

    print(
        f"✅ Loop terminated safely "
        f"after {loop_count} iteration(s)."
    )

else:

    raise AssertionError(
        "Autonomous loop exceeded maximum iterations."
    )


# ============================================================
# CHECK 2 — FINAL AGENT STATE
# ============================================================

if state.status == "completed":

    print(
        "✅ Final AgentState status: COMPLETED."
    )

else:

    raise AssertionError(
        f"Expected completed state, "
        f"got {state.status}"
    )


# ============================================================
# CHECK 3 — ALL ACTIONS COMPLETED
# ============================================================

if len(
    state.completed_steps
) == len(PLAN):

    print(
        "✅ All planned actions completed."
    )

else:

    raise AssertionError(
        f"Expected {len(PLAN)} completed steps, "
        f"got {len(state.completed_steps)}"
    )


# ============================================================
# CHECK 4 — OBSERVATIONS
# ============================================================

if len(
    state.observations
) >= len(PLAN):

    print(
        "✅ Observations recorded for "
        "executed actions."
    )

else:

    raise AssertionError(
        "Expected observations for each action."
    )


# ============================================================
# CHECK 5 — BROWSER URL
# ============================================================

if (
    isinstance(
        state.current_url,
        str
    )
    and
    state.current_url.strip()
):

    print(
        f"✅ Final browser URL: "
        f"{state.current_url}"
    )

else:

    raise AssertionError(
        "Final browser URL was not captured."
    )


# ============================================================
# CHECK 6 — PAGE TITLE
# ============================================================

if (
    isinstance(
        state.page_title,
        str
    )
    and
    state.page_title.strip()
):

    print(
        f"✅ Final page title: "
        f"{state.page_title}"
    )

else:

    raise AssertionError(
        "Final page title was not captured."
    )


# ============================================================
# CHECK 7 — NO FAILURE
# ============================================================

if state.failed_step is None:

    print(
        "✅ No failed step recorded."
    )

else:

    raise AssertionError(
        f"Unexpected failed step: "
        f"{state.failed_step}"
    )


# ============================================================
# CHECK 8 — FINAL EVALUATION
# ============================================================

final_evaluation = agent_evaluator.evaluate(
    state
)

print(
    f"\nFinal evaluation: "
    f"{final_evaluation}"
)


if final_evaluation.get(
    "status"
) == "complete":

    print(
        "✅ Final evaluator decision: COMPLETE."
    )

else:

    raise AssertionError(
        "Final evaluator did not return COMPLETE."
    )


# ============================================================
# FINAL SNAPSHOT
# ============================================================

print("\n")
print("=" * 70)
print("🧠 FINAL AGENT STATE SNAPSHOT")
print("=" * 70)


snapshot = state.snapshot()


for key, value in snapshot.items():

    print(
        f"{key}: {value}"
    )


# ============================================================
# FINAL RESULT
# ============================================================

print("\n")
print("=" * 70)
print("🚀 AUTONOMOUS EXECUTION LOOP TEST PASSED")
print("=" * 70)

print(
    "PAIO successfully completed:"
)

print(
    "   1. Execute"
)

print(
    "   2. Observe"
)

print(
    "   3. Update AgentState"
)

print(
    "   4. Evaluate"
)

print(
    "   5. Continue"
)

print(
    "   6. Select next action"
)

print(
    "   7. Execute next action"
)

print(
    "   8. Evaluate again"
)

print(
    "   9. Detect COMPLETE"
)

print("\n🏁 TEST FINISHED")