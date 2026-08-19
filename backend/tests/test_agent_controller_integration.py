# ============================================================
# tests/test_agent_controller_integration.py
#
# PAIO AGENT CONTROLLER INTEGRATION TEST
#
# Purpose:
#
# Verify the real PAIO controller can:
#
#   1. Receive a natural-language command
#   2. Create a plan
#   3. Store the plan in AgentState
#   4. Execute actions through RecoveryEngine
#   5. Update AgentState
#   6. Evaluate the state
#   7. Continue to the next action
#   8. Detect task completion
#
# ============================================================


from app.core.agent_controller import agent_controller


# ============================================================
# TEST COMMAND
# ============================================================

USER_COMMAND = (
    "search Python tutorials "
    "and click first search result"
)


# ============================================================
# HEADER
# ============================================================

print("\n")
print("=" * 70)
print("🤖 PAIO — AGENT CONTROLLER INTEGRATION TEST")
print("=" * 70)

print("\nCommand:")
print(
    f"  {USER_COMMAND}"
)


# ============================================================
# RUN REAL AGENT CONTROLLER
# ============================================================

print("\n")
print("=" * 70)
print("🚀 STARTING AGENT CONTROLLER")
print("=" * 70)


result = agent_controller.run(
    USER_COMMAND
)


# ============================================================
# PRINT RESULT
# ============================================================

print("\n")
print("=" * 70)
print("📊 CONTROLLER RESULT")
print("=" * 70)

print(
    f"Status: {result.get('status')}"
)

print(
    f"Phase: {result.get('phase')}"
)

print(
    f"Error: {result.get('error')}"
)


# ============================================================
# VALIDATE RESULT STRUCTURE
# ============================================================

if not isinstance(
    result,
    dict
):

    raise AssertionError(
        "AgentController did not return a dictionary."
    )

print(
    "✅ Controller returned a valid result."
)


# ============================================================
# VALIDATE TOP-LEVEL SUCCESS
# ============================================================

if result.get(
    "status"
) == "success":

    print(
        "✅ Controller reported SUCCESS."
    )

else:

    print(
        "❌ Controller did not report SUCCESS."
    )

    print(
        f"Full result:\n{result}"
    )

    raise AssertionError(
        "AgentController task failed."
    )


# ============================================================
# GET AGENT STATE
# ============================================================

state = result.get(
    "state"
)


if state is None:

    raise AssertionError(
        "AgentController result does not contain AgentState."
    )

print(
    "✅ AgentState returned by controller."
)


# ============================================================
# TEST 1 — FINAL STATUS
# ============================================================

print("\n")
print("=" * 70)
print("TEST 1 — FINAL AGENT STATE")
print("=" * 70)


print(
    f"Status: {state.status}"
)


if state.status == "completed":

    print(
        "✅ AgentState status = completed."
    )

else:

    raise AssertionError(
        f"Expected completed, got {state.status}"
    )


# ============================================================
# TEST 2 — GOAL
# ============================================================

print("\n")
print("=" * 70)
print("TEST 2 — USER GOAL")
print("=" * 70)


print(
    f"Goal: {state.user_goal}"
)


if state.user_goal == USER_COMMAND:

    print(
        "✅ User goal stored correctly."
    )

else:

    raise AssertionError(
        "AgentState user_goal does not match command."
    )


# ============================================================
# TEST 3 — PLAN
# ============================================================

print("\n")
print("=" * 70)
print("TEST 3 — GENERATED PLAN")
print("=" * 70)


plan = state.current_plan


print(
    f"Plan steps: {len(plan)}"
)


for index, step in enumerate(
    plan,
    start=1
):

    print(
        f"{index}. {step}"
    )


if len(plan) >= 2:

    print(
        "✅ Multi-step plan generated."
    )

else:

    raise AssertionError(
        "Expected at least two planned actions."
    )


# ============================================================
# TEST 4 — COMPLETED STEPS
# ============================================================

print("\n")
print("=" * 70)
print("TEST 4 — COMPLETED STEPS")
print("=" * 70)


completed_steps = (
    state.completed_steps
)


print(
    f"Completed steps: "
    f"{len(completed_steps)}"
)


for step in completed_steps:

    print(
        f"  {step}"
    )


if len(
    completed_steps
) == len(plan):

    print(
        "✅ All planned actions recorded as completed."
    )

else:

    raise AssertionError(
        "Not all planned actions were completed."
    )


# ============================================================
# TEST 5 — OBSERVATIONS
# ============================================================

print("\n")
print("=" * 70)
print("TEST 5 — OBSERVATIONS")
print("=" * 70)


observations = (
    state.observations
)


print(
    f"Observations: "
    f"{len(observations)}"
)


for observation in observations:

    print(
        f"  {observation}"
    )


if len(
    observations
) >= len(plan):

    print(
        "✅ Observations recorded."
    )

else:

    raise AssertionError(
        "Expected observations for executed actions."
    )


# ============================================================
# TEST 6 — BROWSER STATE
# ============================================================

print("\n")
print("=" * 70)
print("TEST 6 — BROWSER STATE")
print("=" * 70)


print(
    f"Current URL : {state.current_url}"
)

print(
    f"Page title  : {state.page_title}"
)


if (
    isinstance(
        state.current_url,
        str
    )
    and
    state.current_url.strip()
):

    print(
        "✅ Current browser URL captured."
    )

else:

    raise AssertionError(
        "Browser URL was not captured."
    )


if (
    isinstance(
        state.page_title,
        str
    )
    and
    state.page_title.strip()
):

    print(
        "✅ Page title captured."
    )

else:

    raise AssertionError(
        "Page title was not captured."
    )


# ============================================================
# TEST 7 — FAILURE STATE
# ============================================================

print("\n")
print("=" * 70)
print("TEST 7 — FAILURE STATE")
print("=" * 70)


print(
    f"Failed step: {state.failed_step}"
)

print(
    f"Last error : {state.last_error}"
)


if state.failed_step is None:

    print(
        "✅ No failed step."
    )

else:

    raise AssertionError(
        f"Unexpected failed step: "
        f"{state.failed_step}"
    )


if state.last_error is None:

    print(
        "✅ No execution error."
    )

else:

    raise AssertionError(
        f"Unexpected error: "
        f"{state.last_error}"
    )


# ============================================================
# TEST 8 — RECOVERY INFORMATION
# ============================================================

print("\n")
print("=" * 70)
print("TEST 8 — RECOVERY STATE")
print("=" * 70)


print(
    f"Retries       : {state.retry_count}"
)

print(
    f"Replans       : {state.replans_used}"
)

print(
    f"Replan history: {len(state.replan_history)}"
)


if state.replans_used >= 0:

    print(
        "✅ Recovery state is valid."
    )

else:

    raise AssertionError(
        "Invalid replan count."
    )


# ============================================================
# TEST 9 — CURRENT STEP
# ============================================================

print("\n")
print("=" * 70)
print("TEST 9 — STEP TRACKING")
print("=" * 70)


print(
    f"Current step: {state.current_step}"
)


if state.current_step >= len(plan):

    print(
        "✅ Current step indicates plan completion."
    )

else:

    raise AssertionError(
        "Current step does not indicate completion."
    )


# ============================================================
# FINAL RESULT
# ============================================================

print("\n")
print("=" * 70)
print("🚀 AGENT CONTROLLER INTEGRATION TEST PASSED")
print("=" * 70)

print("\nVerified:")

print(
    "   ✅ Natural-language command"
)

print(
    "   ✅ Planner integration"
)

print(
    "   ✅ AgentState integration"
)

print(
    "   ✅ Real action execution"
)

print(
    "   ✅ Autonomous CONTINUE flow"
)

print(
    "   ✅ Multi-step completion"
)

print(
    "   ✅ Browser URL tracking"
)

print(
    "   ✅ Page-title tracking"
)

print(
    "   ✅ Observation tracking"
)

print(
    "   ✅ Failure tracking"
)

print(
    "   ✅ Recovery state"
)

print(
    "   ✅ Final COMPLETE state"
)

print("\n🏁 TEST FINISHED")