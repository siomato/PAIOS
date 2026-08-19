# ============================================================
# tests/test_agent_evaluator_continue.py
#
# PAIO AGENT EVALUATOR — CONTINUE TEST
#
# Purpose:
#
# Verify that AgentEvaluator can correctly determine that a
# task is NOT finished when only part of the plan has executed.
#
# Pipeline:
#
#       AgentState
#           ↓
#       Partial execution
#           ↓
#       AgentEvaluator
#           ↓
#        CONTINUE
#           ↓
#       Identify next action
#
# ============================================================


from app.core.agent_state import AgentState
from app.core.agent_evaluator import agent_evaluator


# ============================================================
# CONFIGURATION
# ============================================================

USER_GOAL = (
    "Search for Python tutorials "
    "and click the first search result"
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
print("🧠 PAIO — AGENT EVALUATOR CONTINUE TEST")
print("=" * 70)


# ============================================================
# TEST 1 — CREATE STATE
# ============================================================

print("\n")
print("=" * 70)
print("TEST 1 — CREATE PARTIAL AGENT STATE")
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
    f"Goal   : {state.user_goal}"
)

print(
    f"Plan   : {state.current_plan}"
)

print(
    f"Status : {state.status}"
)


if state.user_goal == USER_GOAL:

    print(
        "✅ AgentState created successfully."
    )

else:

    print(
        "❌ AgentState creation failed."
    )

    raise AssertionError(
        "AgentState goal mismatch."
    )


# ============================================================
# TEST 2 — SIMULATE FIRST STEP COMPLETION
# ============================================================

print("\n")
print("=" * 70)
print("TEST 2 — FIRST ACTION COMPLETED")
print("=" * 70)


first_action = PLAN[0]


state.mark_step_completed(
    1,
    first_action
)


print(
    f"Completed steps: "
    f"{state.completed_steps}"
)

print(
    f"Current step: "
    f"{state.current_step}"
)


if len(
    state.completed_steps
) == 1:

    print(
        "✅ First action recorded as completed."
    )

else:

    print(
        "❌ First action was not recorded."
    )

    raise AssertionError(
        "Expected exactly one completed action."
    )


# ============================================================
# TEST 3 — EVALUATE PARTIAL STATE
# ============================================================

print("\n")
print("=" * 70)
print("TEST 3 — EVALUATE PARTIAL TASK")
print("=" * 70)


evaluation = agent_evaluator.evaluate(
    state
)


print(
    "\nEvaluation result:"
)

print(
    evaluation
)


# ============================================================
# VALIDATE CONTINUE
# ============================================================

if evaluation.get(
    "status"
) == "continue":

    print(
        "✅ Evaluator correctly returned CONTINUE."
    )

else:

    print(
        "❌ Evaluator did not return CONTINUE."
    )

    raise AssertionError(
        "Expected evaluator status to be 'continue'."
    )


# ============================================================
# TEST 4 — VALIDATE NEXT ACTION
# ============================================================

print("\n")
print("=" * 70)
print("TEST 4 — NEXT ACTION")
print("=" * 70)


next_action = evaluation.get(
    "next_action"
)


print(
    f"Next action: {next_action}"
)


expected_action = PLAN[1]


if next_action == expected_action:

    print(
        "✅ Correct next action identified."
    )

else:

    print(
        "❌ Incorrect next action identified."
    )

    print(
        f"Expected: {expected_action}"
    )

    print(
        f"Received: {next_action}"
    )

    raise AssertionError(
        "Evaluator selected the wrong next action."
    )


# ============================================================
# TEST 5 — CONVENIENCE METHOD
# ============================================================

print("\n")
print("=" * 70)
print("TEST 5 — SHOULD CONTINUE")
print("=" * 70)


if agent_evaluator.should_continue(
    state
):

    print(
        "✅ should_continue() returned True."
    )

else:

    print(
        "❌ should_continue() returned False."
    )

    raise AssertionError(
        "Expected should_continue() to return True."
    )


# ============================================================
# TEST 6 — VERIFY NOT COMPLETE
# ============================================================

print("\n")
print("=" * 70)
print("TEST 6 — NOT COMPLETE")
print("=" * 70)


if not agent_evaluator.is_complete(
    state
):

    print(
        "✅ is_complete() correctly returned False."
    )

else:

    print(
        "❌ is_complete() incorrectly returned True."
    )

    raise AssertionError(
        "Partial task must not be marked complete."
    )


# ============================================================
# TEST 7 — VERIFY NOT FAILED
# ============================================================

print("\n")
print("=" * 70)
print("TEST 7 — NOT FAILED")
print("=" * 70)


if not agent_evaluator.has_failed(
    state
):

    print(
        "✅ has_failed() correctly returned False."
    )

else:

    print(
        "❌ has_failed() incorrectly returned True."
    )

    raise AssertionError(
        "Partial task should not be marked failed."
    )


# ============================================================
# FINAL STATE
# ============================================================

print("\n")
print("=" * 70)
print("🧠 FINAL PARTIAL AGENT STATE")
print("=" * 70)


print(
    f"Goal          : {state.user_goal}"
)

print(
    f"Status        : {state.status}"
)

print(
    f"Current step  : {state.current_step}"
)

print(
    f"Completed     : {len(state.completed_steps)}"
)

print(
    f"Failed step   : {state.failed_step}"
)

print(
    f"Last error    : {state.last_error}"
)


# ============================================================
# FINAL RESULT
# ============================================================

print("\n")
print("=" * 70)
print("🚀 AGENT EVALUATOR CONTINUE TEST PASSED")
print("=" * 70)

print(
    "Evaluator correctly detected that the task "
    "is incomplete."
)

print(
    "Evaluator correctly selected the next action."
)

print(
    "Evaluator correctly requested CONTINUE."
)

print("\nVerified:")

print(
    "   ✅ Partial plan execution"
)

print(
    "   ✅ CONTINUE decision"
)

print(
    "   ✅ Next action detection"
)

print(
    "   ✅ should_continue()"
)

print(
    "   ✅ is_complete() = False"
)

print(
    "   ✅ has_failed() = False"
)

print("\n🏁 TEST FINISHED")