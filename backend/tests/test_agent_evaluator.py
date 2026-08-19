# ============================================================
# tests/test_agent_evaluator.py
#
# PAIO AGENT EVALUATOR TEST
#
# Tests:
#
# TEST 1
#     Completed task
#
# TEST 2
#     Incomplete task
#
# TEST 3
#     Failed task
#
# ============================================================


from app.core.agent_state import AgentState
from app.core.agent_evaluator import agent_evaluator


# ============================================================
# TEST CONFIGURATION
# ============================================================

GOAL = (
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
print("🧠 PAIO — AGENT EVALUATOR TEST")
print("=" * 70)


# ============================================================
# TEST 1 — COMPLETE
# ============================================================

print("\n")
print("=" * 70)
print("TEST 1 — COMPLETE TASK")
print("=" * 70)


complete_state = AgentState(
    GOAL
)

complete_state.set_plan(
    PLAN
)

complete_state.mark_step_completed(
    1,
    PLAN[0]
)

complete_state.mark_step_completed(
    2,
    PLAN[1]
)

complete_state.set_status(
    "completed"
)


complete_result = agent_evaluator.evaluate(
    complete_state
)


print(
    f"Result: {complete_result}"
)


if complete_result["status"] == "complete":

    print(
        "✅ Complete-state evaluation passed."
    )

else:

    print(
        "❌ Complete-state evaluation failed."
    )

    raise AssertionError(
        "Expected COMPLETE."
    )


# ============================================================
# TEST 2 — CONTINUE
# ============================================================

print("\n")
print("=" * 70)
print("TEST 2 — INCOMPLETE TASK")
print("=" * 70)


continue_state = AgentState(
    GOAL
)

continue_state.set_plan(
    PLAN
)

continue_state.mark_step_completed(
    1,
    PLAN[0]
)

continue_state.set_status(
    "executing"
)


continue_result = agent_evaluator.evaluate(
    continue_state
)


print(
    f"Result: {continue_result}"
)


if continue_result["status"] == "continue":

    print(
        "✅ Continue-state evaluation passed."
    )

else:

    print(
        "❌ Continue-state evaluation failed."
    )

    raise AssertionError(
        "Expected CONTINUE."
    )


# ============================================================
# VALIDATE NEXT ACTION
# ============================================================

expected_next_action = PLAN[1]

if (
    continue_result["next_action"]
    == expected_next_action
):

    print(
        "✅ Correct next action identified."
    )

else:

    print(
        "❌ Incorrect next action."
    )

    print(
        f"Expected: {expected_next_action}"
    )

    print(
        f"Received: "
        f"{continue_result['next_action']}"
    )

    raise AssertionError(
        "Evaluator selected incorrect next action."
    )


# ============================================================
# TEST 3 — FAILED
# ============================================================

print("\n")
print("=" * 70)
print("TEST 3 — FAILED TASK")
print("=" * 70)


failed_state = AgentState(
    GOAL
)

failed_state.set_plan(
    PLAN
)

failed_state.mark_step_failed(
    2,
    "Browser click failed."
)

failed_state.set_status(
    "failed"
)


failed_result = agent_evaluator.evaluate(
    failed_state
)


print(
    f"Result: {failed_result}"
)


if failed_result["status"] == "failed":

    print(
        "✅ Failed-state evaluation passed."
    )

else:

    print(
        "❌ Failed-state evaluation failed."
    )

    raise AssertionError(
        "Expected FAILED."
    )


# ============================================================
# TEST 4 — EMPTY PLAN
# ============================================================

print("\n")
print("=" * 70)
print("TEST 4 — EMPTY PLAN")
print("=" * 70)


empty_state = AgentState(
    "Do something"
)

empty_state.set_plan(
    []
)


empty_result = agent_evaluator.evaluate(
    empty_state
)


print(
    f"Result: {empty_result}"
)


if empty_result["status"] == "failed":

    print(
        "✅ Empty-plan evaluation passed."
    )

else:

    print(
        "❌ Empty-plan evaluation failed."
    )

    raise AssertionError(
        "Expected FAILED for empty plan."
    )


# ============================================================
# TEST 5 — CONVENIENCE METHODS
# ============================================================

print("\n")
print("=" * 70)
print("TEST 5 — CONVENIENCE METHODS")
print("=" * 70)


if agent_evaluator.is_complete(
    complete_state
):

    print(
        "✅ is_complete() passed."
    )

else:

    print(
        "❌ is_complete() failed."
    )

    raise AssertionError(
        "is_complete() should return True."
    )


if agent_evaluator.should_continue(
    continue_state
):

    print(
        "✅ should_continue() passed."
    )

else:

    print(
        "❌ should_continue() failed."
    )

    raise AssertionError(
        "should_continue() should return True."
    )


if agent_evaluator.has_failed(
    failed_state
):

    print(
        "✅ has_failed() passed."
    )

else:

    print(
        "❌ has_failed() failed."
    )

    raise AssertionError(
        "has_failed() should return True."
    )


# ============================================================
# FINAL RESULT
# ============================================================

print("\n")
print("=" * 70)
print("🚀 AGENT EVALUATOR TEST PASSED")
print("=" * 70)

print(
    "AgentEvaluator correctly identified:"
)

print(
    "   COMPLETE  → completed task"
)

print(
    "   CONTINUE  → remaining actions"
)

print(
    "   FAILED    → failed task"
)

print(
    "   NEXT      → next planned action"
)

print("\n🏁 TEST FINISHED")