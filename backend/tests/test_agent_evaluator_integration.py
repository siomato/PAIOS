# ============================================================
# tests/test_agent_evaluator_integration.py
#
# PAIO AGENT EVALUATOR INTEGRATION TEST
#
# Purpose:
#
# Verify that the real PAIO execution pipeline can:
#
#     1. Create AgentState
#     2. Create an action plan
#     3. Execute the real browser action
#     4. Update AgentState
#     5. Evaluate AgentState
#     6. Correctly determine COMPLETE
#
# Pipeline:
#
# User Goal
#     ↓
# AgentState
#     ↓
# Action Plan
#     ↓
# ActionExecutor
#     ↓
# Real Browser
#     ↓
# AgentState Update
#     ↓
# AgentEvaluator
#     ↓
# COMPLETE
#
# ============================================================


from app.core.agent_state import AgentState
from app.core.action_executor import action_executor
from app.core.agent_evaluator import agent_evaluator


# ============================================================
# CONFIGURATION
# ============================================================

USER_GOAL = "Open Python website"

PLAN = [
    {
        "action": "open_url",
        "url": "https://www.python.org"
    }
]


# ============================================================
# HEADER
# ============================================================

print("\n")
print("=" * 70)
print("🧠 PAIO — AGENT EVALUATOR INTEGRATION TEST")
print("=" * 70)


# ============================================================
# TEST 1 — CREATE AGENT STATE
# ============================================================

print("\n")
print("=" * 70)
print("TEST 1 — AGENT STATE")
print("=" * 70)


state = AgentState(
    USER_GOAL
)

state.set_plan(
    PLAN
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
        "❌ AgentState goal mismatch."
    )

    raise AssertionError(
        "AgentState was not initialized correctly."
    )


# ============================================================
# TEST 2 — REAL ACTION EXECUTION
# ============================================================

print("\n")
print("=" * 70)
print("TEST 2 — REAL ACTION EXECUTION")
print("=" * 70)


execution_result = action_executor.execute(
    PLAN,
    state=state
)


print("\nExecution result:")
print(
    execution_result
)


# ============================================================
# VALIDATE EXECUTION
# ============================================================

if not isinstance(
    execution_result,
    dict
):

    print(
        "❌ Executor did not return a dictionary."
    )

    raise AssertionError(
        "Invalid execution result."
    )


print(
    "✅ Executor returned a result."
)


if execution_result.get(
    "status"
) == "success":

    print(
        "✅ Real browser execution succeeded."
    )

else:

    print(
        "❌ Real browser execution failed."
    )

    raise AssertionError(
        f"Execution failed: "
        f"{execution_result}"
    )


# ============================================================
# TEST 3 — AGENT STATE UPDATED
# ============================================================

print("\n")
print("=" * 70)
print("TEST 3 — AGENT STATE UPDATE")
print("=" * 70)


print(
    f"Status       : {state.status}"
)

print(
    f"Current URL  : {state.current_url}"
)

print(
    f"Page title   : {state.page_title}"
)

print(
    f"Completed    : {len(state.completed_steps)}"
)

print(
    f"Observations : {len(state.observations)}"
)


# ------------------------------------------------------------
# Status
# ------------------------------------------------------------

if state.status == "completed":

    print(
        "✅ AgentState reached completed status."
    )

else:

    print(
        f"❌ Unexpected AgentState status: "
        f"{state.status}"
    )

    raise AssertionError(
        "AgentState did not reach completed status."
    )


# ------------------------------------------------------------
# Completed step
# ------------------------------------------------------------

if len(
    state.completed_steps
) == 1:

    print(
        "✅ Completed step recorded."
    )

else:

    print(
        "❌ Completed step was not recorded correctly."
    )

    raise AssertionError(
        "Expected exactly one completed step."
    )


# ------------------------------------------------------------
# Observation
# ------------------------------------------------------------

if len(
    state.observations
) >= 1:

    print(
        "✅ Browser observation recorded."
    )

else:

    print(
        "❌ Browser observation missing."
    )

    raise AssertionError(
        "Expected at least one observation."
    )


# ------------------------------------------------------------
# Browser URL
# ------------------------------------------------------------

if (
    isinstance(
        state.current_url,
        str
    )
    and
    state.current_url.strip()
):

    print(
        f"✅ Browser URL captured: "
        f"{state.current_url}"
    )

else:

    print(
        "❌ Browser URL was not captured."
    )

    raise AssertionError(
        "AgentState current_url is empty."
    )


# ------------------------------------------------------------
# Page title
# ------------------------------------------------------------

if (
    isinstance(
        state.page_title,
        str
    )
    and
    state.page_title.strip()
):

    print(
        f"✅ Page title captured: "
        f"{state.page_title}"
    )

else:

    print(
        "❌ Page title was not captured."
    )

    raise AssertionError(
        "AgentState page_title is empty."
    )


# ============================================================
# TEST 4 — REAL AGENT EVALUATOR
# ============================================================

print("\n")
print("=" * 70)
print("TEST 4 — AGENT EVALUATOR")
print("=" * 70)


evaluation_result = agent_evaluator.evaluate(
    state
)


print("\nEvaluation result:")
print(
    evaluation_result
)


# ============================================================
# VALIDATE EVALUATION
# ============================================================

if not isinstance(
    evaluation_result,
    dict
):

    print(
        "❌ Evaluator did not return a dictionary."
    )

    raise AssertionError(
        "Invalid evaluator result."
    )


print(
    "✅ Evaluator returned a result."
)


# ============================================================
# EXPECT COMPLETE
# ============================================================

evaluation_status = evaluation_result.get(
    "status"
)


print(
    f"Evaluation status: "
    f"{evaluation_status}"
)


if evaluation_status == "complete":

    print(
        "✅ Evaluator correctly identified "
        "the task as COMPLETE."
    )

else:

    print(
        "❌ Evaluator did not identify "
        "the task as COMPLETE."
    )

    raise AssertionError(
        f"Expected COMPLETE, "
        f"received: {evaluation_status}"
    )


# ============================================================
# TEST 5 — NO NEXT ACTION
# ============================================================

print("\n")
print("=" * 70)
print("TEST 5 — FINAL DECISION")
print("=" * 70)


next_action = evaluation_result.get(
    "next_action"
)


print(
    f"Next action: {next_action}"
)


if next_action is None:

    print(
        "✅ No additional action required."
    )

else:

    print(
        "❌ Evaluator incorrectly requested "
        "another action."
    )

    raise AssertionError(
        "Completed task should not have a next action."
    )


# ============================================================
# TEST 6 — CONVENIENCE METHODS
# ============================================================

print("\n")
print("=" * 70)
print("TEST 6 — EVALUATOR CONVENIENCE METHODS")
print("=" * 70)


if agent_evaluator.is_complete(
    state
):

    print(
        "✅ is_complete() returned True."
    )

else:

    print(
        "❌ is_complete() returned False."
    )

    raise AssertionError(
        "is_complete() should return True."
    )


if not agent_evaluator.should_continue(
    state
):

    print(
        "✅ should_continue() returned False."
    )

else:

    print(
        "❌ should_continue() incorrectly returned True."
    )

    raise AssertionError(
        "Completed task should not continue."
    )


if not agent_evaluator.has_failed(
    state
):

    print(
        "✅ has_failed() returned False."
    )

else:

    print(
        "❌ has_failed() incorrectly returned True."
    )

    raise AssertionError(
        "Completed task should not be failed."
    )


# ============================================================
# FINAL STATE SNAPSHOT
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
print("🚀 AGENT EVALUATOR INTEGRATION TEST PASSED")
print("=" * 70)

print(
    "Real browser execution successfully "
    "connected to AgentState and AgentEvaluator."
)

print("\nVerified:")

print(
    "   ✅ AgentState creation"
)

print(
    "   ✅ Real browser execution"
)

print(
    "   ✅ AgentState update"
)

print(
    "   ✅ Browser telemetry"
)

print(
    "   ✅ Completed-step tracking"
)

print(
    "   ✅ Observation tracking"
)

print(
    "   ✅ Evaluator decision"
)

print(
    "   ✅ COMPLETE detection"
)

print(
    "   ✅ No unnecessary next action"
)

print(
    "   ✅ Evaluator convenience methods"
)

print("\n🏁 TEST FINISHED")