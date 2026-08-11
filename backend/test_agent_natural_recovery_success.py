# ============================================================
# test_agent_natural_recovery_success.py
#
# REAL NATURAL-LANGUAGE RECOVERY SUCCESS TEST
#
# Flow:
#
# User request
#      ↓
# Agent Controller
#      ↓
# Action Planner
#      ↓
# SEARCH
#      ↓
# CLICK → intentional failures
#      ↓
# Recovery Engine
#      ↓
# Replanner
#      ↓
# READ inserted
#      ↓
# CLICK retry
#      ↓
# Real BrowserTools.click()
#      ↓
# SUCCESS
# ============================================================

from app.core.agent_controller import agent_controller
from app.tools.browser_tools import browser_tools


# ============================================================
# TEST CONFIGURATION
# ============================================================

USER_REQUEST = (
    "Search for Python tutorials "
    "and click first search result"
)


# ============================================================
# IMPORTANT
#
# The execution engine can retry a failed action internally.
# Therefore one forced failure is NOT enough to reach the
# Recovery Engine / Replanner.
#
# We intentionally force 3 failures.
#
# Expected:
#
# CLICK #1 -> FAIL
# CLICK #2 -> FAIL
# CLICK #3 -> FAIL
#             ↓
#       Recovery Engine
#             ↓
#          Replanner
#             ↓
#           READ
#             ↓
# CLICK #4 -> REAL SUCCESS
#
# ============================================================

FORCED_FAILURES = 3


print("\n")
print("=" * 70)
print("🤖 PAIO — NATURAL LANGUAGE RECOVERY SUCCESS TEST")
print("=" * 70)

print("\nUSER REQUEST")
print("-" * 70)
print(USER_REQUEST)

print("\nTEST CONFIGURATION")
print("-" * 70)
print(
    f"Forced click failures: {FORCED_FAILURES}"
)


# ============================================================
# SAVE ORIGINAL CLICK
# ============================================================

original_click = browser_tools.click


# ============================================================
# FAILURE CONTROLLER
# ============================================================

click_attempts = 0


def controlled_click(target):

    global click_attempts

    click_attempts += 1

    print("\n")
    print("=" * 60)
    print(
        f"🧪 CONTROLLED CLICK ATTEMPT #{click_attempts}"
    )
    print("=" * 60)

    print(
        f"Target: {target}"
    )

    # ========================================================
    # INTENTIONAL FAILURES
    # ========================================================

    if click_attempts <= FORCED_FAILURES:

        print(
            "⚠️ Intentionally forcing click failure."
        )

        print(
            f"Failure "
            f"{click_attempts}/{FORCED_FAILURES}"
        )

        raise RuntimeError(
            "Intentional test failure: "
            f"click attempt #{click_attempts} "
            "must fail to trigger recovery."
        )

    # ========================================================
    # REAL CLICK AFTER RECOVERY
    # ========================================================

    print(
        "✅ Recovery retry detected."
    )

    print(
        "🖱️ Executing REAL browser_tools.click()."
    )

    return original_click(target)


# ============================================================
# PATCH CLICK
# ============================================================

browser_tools.click = controlled_click


# ============================================================
# RUN AGENT
# ============================================================

result = None

try:

    print("\n")
    print("=" * 70)
    print(
        "🚀 STARTING NATURAL-LANGUAGE "
        "RECOVERY PIPELINE"
    )
    print("=" * 70)

    result = agent_controller.run(
        USER_REQUEST
    )


except Exception as e:

    print("\n")
    print("=" * 70)
    print("❌ AGENT EXECUTION CRASHED")
    print("=" * 70)

    print(
        f"Error: {e}"
    )

    result = {
        "status": "failed",
        "error": str(e),
        "execution": {}
    }


finally:

    # ========================================================
    # ALWAYS RESTORE ORIGINAL CLICK
    # ========================================================

    browser_tools.click = original_click

    print(
        "\n🔄 Original browser_tools.click() restored."
    )


# ============================================================
# DISPLAY FINAL RESULT
# ============================================================

print("\n")
print("=" * 70)
print("📦 FINAL AGENT RESULT")
print("=" * 70)

print(result)


# ============================================================
# NORMALIZE RESULT
# ============================================================

if not isinstance(result, dict):

    result = {
        "status": "failed",
        "execution": {}
    }


execution = result.get(
    "execution",
    {}
)


if not isinstance(execution, dict):

    execution = {}


# ============================================================
# EXTRACT VALIDATION DATA
# ============================================================

final_status = result.get(
    "status"
)

execution_status = execution.get(
    "status"
)

replans_used = execution.get(
    "replans_used",
    0
)

replan_history = execution.get(
    "replan_history",
    []
)

failed_step = execution.get(
    "failed_step"
)

execution_error = execution.get(
    "error"
)

plan = result.get(
    "plan",
    []
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
# CHECK 1 — AGENT RESULT
# ============================================================

if isinstance(result, dict):

    print(
        "✅ Agent returned a result."
    )

else:

    print(
        "❌ Agent did not return a dictionary."
    )

    validation_passed = False


# ============================================================
# CHECK 2 — SEARCH ACTION
# ============================================================

actions = []

for step in plan:

    if isinstance(step, dict):

        actions.append(
            step.get("action")
        )


if "search" in actions:

    print(
        "✅ SEARCH action exists in original plan."
    )

else:

    print(
        "❌ SEARCH action missing."
    )

    validation_passed = False


# ============================================================
# CHECK 3 — CLICK ACTION
# ============================================================

if "click" in actions:

    print(
        "✅ CLICK action exists in original plan."
    )

else:

    print(
        "❌ CLICK action missing."
    )

    validation_passed = False


# ============================================================
# CHECK 4 — FORCED FAILURES OCCURRED
# ============================================================

if click_attempts > FORCED_FAILURES:

    print(
        f"✅ Forced failures completed: "
        f"{FORCED_FAILURES}"
    )

else:

    print(
        f"❌ Expected at least "
        f"{FORCED_FAILURES + 1} click attempts, "
        f"got {click_attempts}."
    )

    validation_passed = False


# ============================================================
# CHECK 5 — REAL RETRY OCCURRED
# ============================================================

if click_attempts >= FORCED_FAILURES + 1:

    print(
        f"✅ Real retry detected at "
        f"click attempt #{FORCED_FAILURES + 1}."
    )

else:

    print(
        "❌ Real browser retry did not occur."
    )

    validation_passed = False


# ============================================================
# CHECK 6 — REPLANNER INVOKED
# ============================================================

if replans_used >= 1:

    print(
        f"✅ Replanner was invoked: "
        f"{replans_used} time(s)."
    )

else:

    print(
        "❌ Replanner was not invoked."
    )

    validation_passed = False


# ============================================================
# CHECK 7 — REPLAN HISTORY
# ============================================================

if replan_history:

    print(
        f"✅ Replan history recorded: "
        f"{len(replan_history)} entr(y/ies)."
    )

else:

    print(
        "❌ No replan history recorded."
    )

    validation_passed = False


# ============================================================
# CHECK 8 — EXACTLY ONE REPLAN
# ============================================================

if replans_used == 1:

    print(
        "✅ Exactly one replan was used."
    )

else:

    print(
        f"❌ Expected exactly one replan, "
        f"got {replans_used}."
    )

    validation_passed = False


# ============================================================
# CHECK 9 — FINAL AGENT STATUS
# ============================================================

if final_status == "success":

    print(
        "✅ Final agent status: SUCCESS."
    )

else:

    print(
        f"❌ Final agent status: "
        f"{final_status}"
    )

    validation_passed = False


# ============================================================
# CHECK 10 — EXECUTION STATUS
# ============================================================

if execution_status == "success":

    print(
        "✅ Execution engine finished successfully."
    )

else:

    print(
        f"❌ Execution engine status: "
        f"{execution_status}"
    )

    validation_passed = False


# ============================================================
# CHECK 11 — REAL BROWSER CLICK
# ============================================================

if (
    click_attempts >= FORCED_FAILURES + 1
    and
    final_status == "success"
    and
    execution_status == "success"
):

    print(
        "✅ Real browser click succeeded "
        "after recovery/replanning."
    )

else:

    print(
        "❌ Real browser click did not "
        "complete successfully."
    )

    validation_passed = False


# ============================================================
# CHECK 12 — FINAL RECOVERY
# ============================================================

if (
    final_status == "success"
    and
    execution_status == "success"
    and
    replans_used >= 1
):

    print(
        "✅ Final execution recovered successfully."
    )

else:

    print(
        "❌ Final execution recovery failed."
    )

    if failed_step is not None:

        print(
            f"Failed step: {failed_step}"
        )

    if execution_error:

        print(
            f"Execution error: {execution_error}"
        )

    validation_passed = False


# ============================================================
# FINAL RESULT
# ============================================================

print("\n")
print("=" * 70)


if validation_passed:

    print(
        "🚀 FULL NATURAL RECOVERY SUCCESS TEST PASSED"
    )

    print(
        "Natural-language task successfully recovered "
        "from intentional browser failures."
    )

else:

    print(
        "❌ FULL NATURAL RECOVERY SUCCESS TEST FAILED"
    )

    print(
        "Review the validation output above."
    )


print("=" * 70)


# ============================================================
# DEBUG INFORMATION
# ============================================================

print("\nVerified:")

print(
    f"   Forced failures : {FORCED_FAILURES}"
)

print(
    f"   Click attempts  : {click_attempts}"
)

print(
    f"   Replans used    : {replans_used}"
)

print(
    f"   Replan history  : {len(replan_history)}"
)

print(
    f"   Final status    : {final_status}"
)

print(
    f"   Execution       : {execution_status}"
)

print(
    f"   Failed step     : {failed_step}"
)

print(
    "\n🏁 TEST FINISHED"
)