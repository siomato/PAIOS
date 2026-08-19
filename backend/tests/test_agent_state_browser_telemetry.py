# ============================================================
# tests/test_agent_state_browser_telemetry.py
#
# PAIO AGENT STATE — BROWSER TELEMETRY TEST
#
# Purpose:
#
# Verify that a REAL browser execution updates AgentState
# with:
#
#   1. Current URL
#   2. Page title
#   3. Completed steps
#   4. Observations
#
# Flow:
#
# User Goal
#     ↓
# AgentState
#     ↓
# ActionExecutor
#     ↓
# BrowserTools
#     ↓
# Real Playwright Browser
#     ↓
# Browser Telemetry
#     ↓
# AgentState
#
# ============================================================


from app.core.agent_state import AgentState
from app.core.action_executor import action_executor


# ============================================================
# TEST CONFIGURATION
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
print("🌐 PAIO — AGENT STATE BROWSER TELEMETRY TEST")
print("=" * 70)

print("\nUSER GOAL")
print("-" * 70)

print(USER_GOAL)

print("\nPLAN")
print("-" * 70)

print(PLAN)


# ============================================================
# CREATE AGENT STATE
# ============================================================

print("\n")
print("=" * 70)
print("🧠 CREATING AGENT STATE")
print("=" * 70)

state = AgentState(
    USER_GOAL
)

state.set_plan(
    PLAN
)

print(
    "✅ AgentState created."
)

print(
    f"Goal: {state.user_goal}"
)

print(
    f"Initial status: {state.status}"
)


# ============================================================
# EXECUTE REAL BROWSER ACTION
# ============================================================

print("\n")
print("=" * 70)
print("🚀 EXECUTING REAL BROWSER ACTION")
print("=" * 70)

execution = action_executor.execute(
    PLAN,
    state=state
)


# ============================================================
# DISPLAY EXECUTION RESULT
# ============================================================

print("\n")
print("=" * 70)
print("📦 EXECUTION RESULT")
print("=" * 70)

print(
    execution
)


# ============================================================
# DISPLAY AGENT STATE
# ============================================================

print("\n")
print("=" * 70)
print("🧠 FINAL AGENT STATE")
print("=" * 70)

state.print_state()


# ============================================================
# DISPLAY TELEMETRY
# ============================================================

print("\n")
print("=" * 70)
print("🌐 BROWSER TELEMETRY")
print("=" * 70)

print(
    f"Current URL : {state.current_url}"
)

print(
    f"Page title  : {state.page_title}"
)

print(
    f"Observations: {len(state.observations)}"
)

print(
    f"Completed   : {len(state.completed_steps)}"
)


# ============================================================
# VALIDATION
# ============================================================

print("\n")
print("=" * 70)
print("🔎 VALIDATION")
print("=" * 70)

validation_passed = True


# ============================================================
# CHECK 1 — EXECUTION RESULT
# ============================================================

if isinstance(
    execution,
    dict
):

    print(
        "✅ Execution returned a dictionary."
    )

else:

    print(
        "❌ Execution did not return a dictionary."
    )

    validation_passed = False


# ============================================================
# CHECK 2 — EXECUTION STATUS
# ============================================================

execution_status = (
    execution.get(
        "status"
    )
    if isinstance(
        execution,
        dict
    )
    else None
)

if execution_status == "success":

    print(
        "✅ Execution status: SUCCESS."
    )

else:

    print(
        f"❌ Execution status: {execution_status}"
    )

    validation_passed = False


# ============================================================
# CHECK 3 — AGENT STATE STATUS
# ============================================================

if state.status == "completed":

    print(
        "✅ AgentState status: COMPLETED."
    )

else:

    print(
        f"❌ AgentState status: {state.status}"
    )

    validation_passed = False


# ============================================================
# CHECK 4 — COMPLETED STEPS
# ============================================================

if len(
    state.completed_steps
) >= 1:

    print(
        "✅ AgentState recorded completed step."
    )

else:

    print(
        "❌ AgentState did not record completed step."
    )

    validation_passed = False


# ============================================================
# CHECK 5 — OBSERVATIONS
# ============================================================

if len(
    state.observations
) >= 1:

    print(
        "✅ AgentState recorded browser observation."
    )

else:

    print(
        "❌ No browser observations recorded."
    )

    validation_passed = False


# ============================================================
# CHECK 6 — CURRENT URL
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
        f"✅ Current URL captured: "
        f"{state.current_url}"
    )

else:

    print(
        "❌ Current browser URL was not captured."
    )

    validation_passed = False


# ============================================================
# CHECK 7 — PAGE TITLE
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
        f"✅ Page title captured: "
        f"{state.page_title}"
    )

else:

    print(
        "❌ Page title was not captured."
    )

    validation_passed = False


# ============================================================
# CHECK 8 — NO FAILED STEP
# ============================================================

if state.failed_step is None:

    print(
        "✅ No failed step recorded."
    )

else:

    print(
        f"❌ Unexpected failed step: "
        f"{state.failed_step}"
    )

    validation_passed = False


# ============================================================
# CHECK 9 — NO LAST ERROR
# ============================================================

if state.last_error is None:

    print(
        "✅ No execution error recorded."
    )

else:

    print(
        f"❌ Unexpected error: "
        f"{state.last_error}"
    )

    validation_passed = False


# ============================================================
# FINAL RESULT
# ============================================================

print("\n")
print("=" * 70)

if validation_passed:

    print(
        "🚀 BROWSER TELEMETRY TEST PASSED"
    )

    print(
        "AgentState successfully captured "
        "real browser execution state."
    )

else:

    print(
        "❌ BROWSER TELEMETRY TEST FAILED"
    )

    print(
        "Review the validation output above."
    )

print("=" * 70)


# ============================================================
# DEBUG SUMMARY
# ============================================================

print("\n")
print("Verified:")

print(
    f"   Execution status : {execution_status}"
)

print(
    f"   AgentState status: {state.status}"
)

print(
    f"   Completed steps  : {len(state.completed_steps)}"
)

print(
    f"   Observations     : {len(state.observations)}"
)

print(
    f"   Current URL      : {state.current_url}"
)

print(
    f"   Page title       : {state.page_title}"
)

print(
    f"   Failed step      : {state.failed_step}"
)

print(
    f"   Last error       : {state.last_error}"
)

print("\n🏁 TEST FINISHED")