# ============================================================
# tests/test_agent_state_integration.py
#
# PAIO — AGENT STATE INTEGRATION TEST
#
# Purpose:
# Verify that AgentState is connected correctly to the
# complete AgentController pipeline.
#
# Flow:
#
# User Request
#      ↓
# AgentController
#      ↓
# AgentState
#      ↓
# ActionPlanner
#      ↓
# RecoveryEngine
#      ↓
# ActionExecutor
#      ↓
# Browser
#      ↓
# AgentState updated
#
# This test does NOT intentionally break the browser.
# Recovery is tested separately.
# ============================================================

from app.core.agent_controller import agent_controller


# ============================================================
# TEST CONFIGURATION
# ============================================================

USER_REQUEST = (
    "Search for Python tutorials"
)


# ============================================================
# HEADER
# ============================================================

print("\n")
print("=" * 70)
print("🧠 PAIO — AGENT STATE INTEGRATION TEST")
print("=" * 70)

print("\nUSER REQUEST")
print("-" * 70)

print(
    USER_REQUEST
)


# ============================================================
# VALIDATION
# ============================================================

validation_passed = True


# ============================================================
# RUN AGENT
# ============================================================

print("\n")
print("=" * 70)
print("🚀 STARTING AGENT PIPELINE")
print("=" * 70)

try:

    result = agent_controller.run(
        USER_REQUEST
    )

except Exception as e:

    print(
        "\n❌ Agent execution raised an exception."
    )

    print(
        f"{type(e).__name__}: {e}"
    )

    raise SystemExit(1)


# ============================================================
# DISPLAY RESULT
# ============================================================

print("\n")
print("=" * 70)
print("📦 AGENT RESULT")
print("=" * 70)

print(
    result
)


# ============================================================
# TEST 1 — RESULT EXISTS
# ============================================================

print("\n")
print("=" * 60)
print("TEST 1 — RESULT OBJECT")
print("=" * 60)

if isinstance(
    result,
    dict
):

    print(
        "✅ Agent returned a dictionary."
    )

else:

    print(
        "❌ Agent did not return a dictionary."
    )

    validation_passed = False


# ============================================================
# TEST 2 — FINAL STATUS
# ============================================================

print("\n")
print("=" * 60)
print("TEST 2 — FINAL STATUS")
print("=" * 60)

final_status = result.get(
    "status"
)

print(
    f"Final status: {final_status}"
)

if final_status == "success":

    print(
        "✅ Agent completed successfully."
    )

else:

    print(
        "❌ Agent did not complete successfully."
    )

    validation_passed = False


# ============================================================
# TEST 3 — AGENT STATE EXISTS
# ============================================================

print("\n")
print("=" * 60)
print("TEST 3 — AGENT STATE")
print("=" * 60)

state = result.get(
    "state"
)

if state is not None:

    print(
        "✅ AgentState object returned."
    )

else:

    print(
        "❌ AgentState was not returned."
    )

    validation_passed = False


# ============================================================
# STOP STATE TESTS IF STATE IS MISSING
# ============================================================

if state is None:

    print("\n")
    print("=" * 70)

    print(
        "❌ AGENT STATE INTEGRATION TEST FAILED"
    )

    print("=" * 70)

    raise SystemExit(1)


# ============================================================
# TEST 4 — USER GOAL
# ============================================================

print("\n")
print("=" * 60)
print("TEST 4 — USER GOAL")
print("=" * 60)

if state.user_goal == USER_REQUEST:

    print(
        "✅ AgentState contains the correct user goal."
    )

else:

    print(
        "❌ AgentState user goal mismatch."
    )

    print(
        f"Expected: {USER_REQUEST}"
    )

    print(
        f"Actual:   {state.user_goal}"
    )

    validation_passed = False


# ============================================================
# TEST 5 — PLAN
# ============================================================

print("\n")
print("=" * 60)
print("TEST 5 — PLAN STATE")
print("=" * 60)

plan = getattr(
    state,
    "current_plan",
    None
)

if isinstance(
    plan,
    list
) and plan:

    print(
        f"✅ AgentState contains "
        f"{len(plan)} planned action(s)."
    )

    for index, step in enumerate(
        plan,
        start=1
    ):

        print(
            f"   {index}. {step}"
        )

else:

    print(
        "❌ AgentState does not contain a valid plan."
    )

    validation_passed = False


# ============================================================
# TEST 6 — CURRENT STEP
# ============================================================

print("\n")
print("=" * 60)
print("TEST 6 — CURRENT STEP")
print("=" * 60)

current_step = getattr(
    state,
    "current_step",
    None
)

print(
    f"Current step: {current_step}"
)

if isinstance(
    current_step,
    int
):

    print(
        "✅ Current step is tracked."
    )

else:

    print(
        "❌ Current step is not tracked correctly."
    )

    validation_passed = False


# ============================================================
# TEST 7 — COMPLETED STEPS
# ============================================================

print("\n")
print("=" * 60)
print("TEST 7 — COMPLETED STEPS")
print("=" * 60)

completed_steps = getattr(
    state,
    "completed_steps",
    None
)

if isinstance(
    completed_steps,
    list
):

    print(
        f"Completed steps recorded: "
        f"{len(completed_steps)}"
    )

    if len(completed_steps) >= 1:

        print(
            "✅ Completed execution was recorded."
        )

    else:

        print(
            "⚠️ No completed-step entries recorded."
        )

else:

    print(
        "❌ completed_steps is not a list."
    )

    validation_passed = False


# ============================================================
# TEST 8 — BROWSER URL
# ============================================================

print("\n")
print("=" * 60)
print("TEST 8 — BROWSER STATE")
print("=" * 60)

current_url = getattr(
    state,
    "current_url",
    None
)

page_title = getattr(
    state,
    "page_title",
    None
)

print(
    f"Current URL: {current_url}"
)

print(
    f"Page title : {page_title}"
)

if current_url:

    print(
        "✅ Browser URL is stored in AgentState."
    )

else:

    print(
        "⚠️ Browser URL was not populated."
    )


# ============================================================
# TEST 9 — RETRY STATE
# ============================================================

print("\n")
print("=" * 60)
print("TEST 9 — RETRY STATE")
print("=" * 60)

retry_count = getattr(
    state,
    "retry_count",
    0
)

print(
    f"Retry count: {retry_count}"
)

if isinstance(
    retry_count,
    int
):

    print(
        "✅ Retry state is available."
    )

else:

    print(
        "❌ Retry state is invalid."
    )

    validation_passed = False


# ============================================================
# TEST 10 — REPLAN STATE
# ============================================================

print("\n")
print("=" * 60)
print("TEST 10 — REPLAN STATE")
print("=" * 60)

replans_used = getattr(
    state,
    "replans_used",
    0
)

replan_history = getattr(
    state,
    "replan_history",
    []
)

print(
    f"Replans used   : {replans_used}"
)

print(
    f"Replan history : {len(replan_history)}"
)

if isinstance(
    replans_used,
    int
):

    print(
        "✅ Replan counter is available."
    )

else:

    print(
        "❌ Replan counter is invalid."
    )

    validation_passed = False


# ============================================================
# TEST 11 — FINAL STATE
# ============================================================

print("\n")
print("=" * 60)
print("TEST 11 — FINAL AGENT STATE")
print("=" * 60)

state_status = getattr(
    state,
    "status",
    None
)

print(
    f"AgentState status: {state_status}"
)

if state_status in (
    "completed",
    "success"
):

    print(
        "✅ AgentState reached a successful final state."
    )

else:

    print(
        "❌ AgentState did not reach a successful "
        "final state."
    )

    validation_passed = False


# ============================================================
# TEST 12 — SNAPSHOT
# ============================================================

print("\n")
print("=" * 60)
print("TEST 12 — STATE SNAPSHOT")
print("=" * 60)

try:

    snapshot = state.snapshot()

except Exception as e:

    print(
        f"❌ Snapshot generation failed: {e}"
    )

    validation_passed = False

else:

    if isinstance(
        snapshot,
        dict
    ):

        print(
            "✅ AgentState snapshot generated."
        )

        print(
            "\nSnapshot:"
        )

        for key, value in snapshot.items():

            print(
                f"   {key}: {value}"
            )

    else:

        print(
            "❌ Snapshot is not a dictionary."
        )

        validation_passed = False


# ============================================================
# FINAL VALIDATION
# ============================================================

print("\n")
print("=" * 70)

if validation_passed:

    print(
        "🚀 AGENT STATE INTEGRATION TEST PASSED"
    )

    print(
        "AgentState is successfully connected "
        "to the PAIO agent pipeline."
    )

else:

    print(
        "❌ AGENT STATE INTEGRATION TEST FAILED"
    )

    print(
        "Review the failed validation above."
    )

print("=" * 70)

print(
    "\n🏁 TEST FINISHED"
)