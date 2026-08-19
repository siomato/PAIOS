# ============================================================
# tests/test_agent_state.py
#
# PAIO PHASE 2 — AGENT STATE TEST
#
# Verifies:
#   1. AgentState creation
#   2. Goal storage
#   3. Plan storage
#   4. Current-step tracking
#   5. Completed-step tracking
#   6. Failure tracking
#   7. Observation tracking
#   8. Browser-state tracking
#   9. Retry tracking
#  10. Replan tracking
#  11. Status management
#  12. Snapshot generation
# ============================================================

from app.core.agent_state import AgentState


# ============================================================
# HEADER
# ============================================================

print("\n")
print("=" * 70)
print("🧠 PAIO — AGENT STATE TEST")
print("=" * 70)


validation_passed = True


# ============================================================
# TEST 1 — CREATE STATE
# ============================================================

print("\n")
print("=" * 60)
print("TEST 1 — CREATE AGENT STATE")
print("=" * 60)

try:

    state = AgentState(
        "Search for Python tutorials"
    )

    print(
        "✅ AgentState created."
    )

except Exception as e:

    print(
        f"❌ AgentState creation failed: {e}"
    )

    validation_passed = False
    state = None


# ============================================================
# STOP IF CREATION FAILED
# ============================================================

if state is None:

    print(
        "\n❌ Cannot continue without AgentState."
    )

    raise SystemExit(1)


# ============================================================
# TEST 2 — USER GOAL
# ============================================================

print("\n")
print("=" * 60)
print("TEST 2 — USER GOAL")
print("=" * 60)

expected_goal = (
    "Search for Python tutorials"
)

if state.user_goal == expected_goal:

    print(
        "✅ User goal stored correctly."
    )

else:

    print(
        "❌ User goal mismatch."
    )

    print(
        f"Expected: {expected_goal}"
    )

    print(
        f"Actual:   {state.user_goal}"
    )

    validation_passed = False


# ============================================================
# TEST 3 — INITIAL STATUS
# ============================================================

print("\n")
print("=" * 60)
print("TEST 3 — INITIAL STATUS")
print("=" * 60)

if state.status == "initialized":

    print(
        "✅ Initial status is correct."
    )

else:

    print(
        f"❌ Unexpected initial status: "
        f"{state.status}"
    )

    validation_passed = False


# ============================================================
# TEST 4 — SET PLAN
# ============================================================

print("\n")
print("=" * 60)
print("TEST 4 — SET PLAN")
print("=" * 60)

plan = [

    {
        "action": "search",
        "query": "Python tutorials"
    },

    {
        "action": "click",
        "target": "first search result"
    },

    {
        "action": "read"
    }

]

try:

    state.set_plan(
        plan
    )

    if state.current_plan == plan:

        print(
            "✅ Plan stored correctly."
        )

    else:

        print(
            "❌ Plan was not stored correctly."
        )

        validation_passed = False

except Exception as e:

    print(
        f"❌ Plan test failed: {e}"
    )

    validation_passed = False


# ============================================================
# TEST 5 — CURRENT STEP
# ============================================================

print("\n")
print("=" * 60)
print("TEST 5 — CURRENT STEP")
print("=" * 60)

try:

    state.set_current_step(
        1
    )

    if state.current_step == 1:

        print(
            "✅ Current step updated."
        )

    else:

        print(
            "❌ Current step mismatch."
        )

        validation_passed = False

except Exception as e:

    print(
        f"❌ Current step test failed: {e}"
    )

    validation_passed = False


# ============================================================
# TEST 6 — COMPLETED STEP
# ============================================================

print("\n")
print("=" * 60)
print("TEST 6 — COMPLETED STEP")
print("=" * 60)

try:

    state.mark_step_completed(
        1,
        plan[0]
    )

    if len(
        state.completed_steps
    ) == 1:

        print(
            "✅ Completed step recorded."
        )

    else:

        print(
            "❌ Completed step was not recorded."
        )

        validation_passed = False

except Exception as e:

    print(
        f"❌ Completed step test failed: {e}"
    )

    validation_passed = False


# ============================================================
# TEST 7 — FAILURE
# ============================================================

print("\n")
print("=" * 60)
print("TEST 7 — FAILURE RECORDING")
print("=" * 60)

try:

    state.mark_step_failed(
        2,
        "Target could not be resolved."
    )

    if state.failed_step == 2:

        print(
            "✅ Failed step recorded."
        )

    else:

        print(
            "❌ Failed step mismatch."
        )

        validation_passed = False

    if (
        state.last_error
        ==
        "Target could not be resolved."
    ):

        print(
            "✅ Error recorded."
        )

    else:

        print(
            "❌ Error was not recorded correctly."
        )

        validation_passed = False

except Exception as e:

    print(
        f"❌ Failure recording test failed: {e}"
    )

    validation_passed = False


# ============================================================
# TEST 8 — OBSERVATION
# ============================================================

print("\n")
print("=" * 60)
print("TEST 8 — OBSERVATION")
print("=" * 60)

try:

    observation = {
        "url": "https://www.python.org",
        "title": "Welcome to Python.org"
    }

    state.add_observation(
        observation
    )

    if (
        len(state.observations) == 1
        and
        state.observations[0] == observation
    ):

        print(
            "✅ Observation recorded."
        )

    else:

        print(
            "❌ Observation was not recorded correctly."
        )

        validation_passed = False

except Exception as e:

    print(
        f"❌ Observation test failed: {e}"
    )

    validation_passed = False


# ============================================================
# TEST 9 — BROWSER STATE
# ============================================================

print("\n")
print("=" * 60)
print("TEST 9 — BROWSER STATE")
print("=" * 60)

try:

    state.update_browser_state(
        current_url="https://www.python.org",
        page_title="Welcome to Python.org"
    )

    if (
        state.current_url
        ==
        "https://www.python.org"
    ):

        print(
            "✅ Current URL stored."
        )

    else:

        print(
            "❌ Current URL mismatch."
        )

        validation_passed = False

    if (
        state.page_title
        ==
        "Welcome to Python.org"
    ):

        print(
            "✅ Page title stored."
        )

    else:

        print(
            "❌ Page title mismatch."
        )

        validation_passed = False

except Exception as e:

    print(
        f"❌ Browser state test failed: {e}"
    )

    validation_passed = False


# ============================================================
# TEST 10 — RETRY
# ============================================================

print("\n")
print("=" * 60)
print("TEST 10 — RETRY COUNT")
print("=" * 60)

try:

    state.increment_retry()
    state.increment_retry()

    if state.retry_count == 2:

        print(
            "✅ Retry count tracked correctly."
        )

    else:

        print(
            f"❌ Retry count mismatch: "
            f"{state.retry_count}"
        )

        validation_passed = False

except Exception as e:

    print(
        f"❌ Retry test failed: {e}"
    )

    validation_passed = False


# ============================================================
# TEST 11 — REPLAN
# ============================================================

print("\n")
print("=" * 60)
print("TEST 11 — REPLAN TRACKING")
print("=" * 60)

new_plan = [

    {
        "action": "read"
    },

    {
        "action": "click",
        "target": "first search result"
    }

]

try:

    state.record_replan(
        old_plan=plan,
        new_plan=new_plan,
        reason="Click target failed."
    )

    if state.replans_used == 1:

        print(
            "✅ Replan count recorded."
        )

    else:

        print(
            f"❌ Replan count mismatch: "
            f"{state.replans_used}"
        )

        validation_passed = False

    if len(
        state.replan_history
    ) == 1:

        print(
            "✅ Replan history recorded."
        )

    else:

        print(
            "❌ Replan history missing."
        )

        validation_passed = False

except Exception as e:

    print(
        f"❌ Replan test failed: {e}"
    )

    validation_passed = False


# ============================================================
# TEST 12 — STATUS
# ============================================================

print("\n")
print("=" * 60)
print("TEST 12 — STATUS UPDATE")
print("=" * 60)

try:

    state.set_status(
        "executing"
    )

    if state.status == "executing":

        print(
            "✅ Status updated correctly."
        )

    else:

        print(
            f"❌ Status mismatch: "
            f"{state.status}"
        )

        validation_passed = False

except Exception as e:

    print(
        f"❌ Status test failed: {e}"
    )

    validation_passed = False


# ============================================================
# TEST 13 — SNAPSHOT
# ============================================================

print("\n")
print("=" * 60)
print("TEST 13 — STATE SNAPSHOT")
print("=" * 60)

try:

    snapshot = state.snapshot()

    required_fields = [

        "user_goal",
        "status",
        "current_plan",
        "current_step",
        "completed_steps",
        "failed_step",
        "last_error",
        "current_url",
        "page_title",
        "observations",
        "retry_count",
        "replans_used",
        "replan_history"

    ]

    missing_fields = [

        field
        for field in required_fields
        if field not in snapshot

    ]

    if not missing_fields:

        print(
            "✅ Snapshot contains all required fields."
        )

    else:

        print(
            "❌ Snapshot missing fields:"
        )

        for field in missing_fields:

            print(
                f"   - {field}"
            )

        validation_passed = False

except Exception as e:

    print(
        f"❌ Snapshot test failed: {e}"
    )

    validation_passed = False


# ============================================================
# DISPLAY FINAL STATE
# ============================================================

print("\n")
print("=" * 70)
print("📦 FINAL AGENT STATE")
print("=" * 70)

state.print_state()


# ============================================================
# FINAL RESULT
# ============================================================

print("\n")
print("=" * 70)

if validation_passed:

    print(
        "🚀 AGENT STATE TEST PASSED"
    )

    print(
        "AgentState is ready for integration."
    )

else:

    print(
        "❌ AGENT STATE TEST FAILED"
    )

    print(
        "Fix AgentState before connecting it "
        "to the PAIO pipeline."
    )

print("=" * 70)

print("\n🏁 TEST FINISHED")