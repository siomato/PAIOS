# ============================================================
# test_agent_real_recovery_success.py
#
# REAL PAIO AGENT RECOVERY -> REPLANNER -> SUCCESS TEST
#
# Flow:
#
# User request
#       ↓
# Agent Controller
#       ↓
# Action Planner
#       ↓
# Execution Engine
#       ↓
# SEARCH succeeds
#       ↓
# CLICK #1 fails
#       ↓
# CLICK #2 fails
#       ↓
# CLICK #3 fails
#       ↓
# Recovery retries exhausted
#       ↓
# Replanner
#       ↓
# New plan generated
#       ↓
# READ inserted
#       ↓
# CLICK #4
#       ↓
# Real browser_tools.click()
#       ↓
# SUCCESS
#
# ============================================================


from app.core.agent_controller import agent_controller
from app.tools.browser_tools import browser_tools


# ============================================================
# MODULE INFORMATION
# ============================================================

print("\n🔥 BROWSER AUTOMATION MODULE LOADED 🔥")
print("🎯 TARGET RESOLVER MODULE LOADED 🎯")
print("🧠 REPLANNER MODULE LOADED 🧠")
print("🛡️ RECOVERY ENGINE MODULE LOADED 🛡️")
print("🤖 AGENT CONTROLLER MODULE LOADED 🤖")


# ============================================================
# TEST CONFIGURATION
# ============================================================

USER_REQUEST = (
    "Search for Python tutorials "
    "and click first search result"
)


# ============================================================
# TEST HEADER
# ============================================================

print("\n")
print("=" * 70)
print("🤖 PAIO — REAL RECOVERY → REPLANNER SUCCESS TEST")
print("=" * 70)


print("\nUSER REQUEST")
print("-" * 70)
print(USER_REQUEST)


# ============================================================
# SAVE ORIGINAL CLICK
# ============================================================

original_click = browser_tools.click


# ============================================================
# FAILURE CONTROLLER
# ============================================================

click_attempts = 0


def controlled_click(target):
    """
    Force the first THREE click attempts to fail.

    Recovery Engine configuration:

        MAX_RETRIES = 2

    Therefore:

        Attempt 1 -> failure
        Attempt 2 -> failure
        Attempt 3 -> failure
        -----------------------
        Replanner invoked

    After replanning:

        Attempt 4 -> REAL CLICK
    """

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
    # FORCE FIRST THREE ATTEMPTS TO FAIL
    # ========================================================

    if click_attempts <= 3:

        print(
            "⚠️ Intentionally forcing click failure."
        )

        raise RuntimeError(
            "Intentional test failure: "
            f"click attempt {click_attempts}"
        )


    # ========================================================
    # ATTEMPT #4+
    #
    # Allow the REAL browser implementation.
    # ========================================================

    print(
        "✅ Replanned retry reached."
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
    print("🚀 STARTING REAL AGENT PIPELINE")
    print("=" * 70)

    result = agent_controller.run(
        USER_REQUEST
    )


except Exception as e:

    print("\n")
    print("=" * 70)
    print("❌ TEST EXECUTION CRASHED")
    print("=" * 70)

    print(
        f"Error: {e}"
    )

    result = {
        "status": "failed",
        "error": str(e)
    }


finally:

    # ========================================================
    # ALWAYS RESTORE REAL CLICK
    # ========================================================

    browser_tools.click = original_click

    print(
        "\n🔄 Original browser_tools.click restored."
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
# VALIDATION
# ============================================================

print("\n")
print("=" * 70)
print("🔎 VALIDATION")
print("=" * 70)


validation_passed = True


# ============================================================
# CHECK 1 — RESULT EXISTS
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
# EXTRACT EXECUTION RESULT
# ============================================================

execution = {}

if isinstance(result, dict):

    execution = result.get(
        "execution",
        {}
    )

    if not isinstance(
        execution,
        dict
    ):

        execution = {}


# ============================================================
# EXTRACT REPLAN INFORMATION
# ============================================================

replans_used = execution.get(
    "replans_used",
    0
)

replan_history = execution.get(
    "replan_history",
    []
)


# ============================================================
# CHECK 2 — MULTIPLE CLICK ATTEMPTS
# ============================================================

if click_attempts >= 4:

    print(
        f"✅ Click attempts detected: "
        f"{click_attempts}"
    )

else:

    print(
        f"❌ Expected at least 4 click attempts, "
        f"got {click_attempts}."
    )

    validation_passed = False


# ============================================================
# CHECK 3 — FIRST THREE CLICKS FAILED
# ============================================================

if click_attempts >= 4:

    print(
        "✅ Three initial click failures were forced."
    )

else:

    print(
        "❌ Three recovery attempts were not completed."
    )

    validation_passed = False


# ============================================================
# CHECK 4 — REPLANNER INVOKED
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
# CHECK 5 — REPLAN HISTORY
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
# CHECK 6 — FINAL STATUS
# ============================================================

final_status = None

if isinstance(result, dict):

    final_status = result.get(
        "status"
    )


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
# CHECK 7 — EXECUTION STATUS
# ============================================================

execution_status = execution.get(
    "status"
)


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
# CHECK 8 — REAL CLICK COMPLETED
# ============================================================

if (
    click_attempts >= 4
    and final_status == "success"
):

    print(
        "✅ Real browser click succeeded "
        "after recovery/replanning."
    )

else:

    print(
        "❌ Real browser click did not "
        "complete after replanning."
    )

    validation_passed = False


# ============================================================
# CHECK 9 — EXACTLY ONE REPLAN
# ============================================================

if replans_used == 1:

    print(
        "✅ Exactly one replan was used."
    )

elif replans_used > 1:

    print(
        f"⚠️ More than one replan used: "
        f"{replans_used}"
    )

else:

    print(
        "❌ No replan occurred."
    )

    validation_passed = False


# ============================================================
# FINAL TEST RESULT
# ============================================================

print("\n")
print("=" * 70)


if validation_passed:

    print(
        "🚀 REAL AGENT RECOVERY SUCCESS TEST PASSED"
    )

else:

    print(
        "❌ REAL AGENT RECOVERY SUCCESS TEST FAILED"
    )


print("=" * 70)


# ============================================================
# DEBUG INFORMATION
# ============================================================

print("\nVerified:")

print(
    f"   Click attempts : {click_attempts}"
)

print(
    f"   Replans used   : {replans_used}"
)

print(
    f"   Replan history : {len(replan_history)}"
)

print(
    f"   Final status   : {final_status}"
)

print(
    f"   Execution      : {execution_status}"
)

print(
    "\n🏁 TEST FINISHED"
)