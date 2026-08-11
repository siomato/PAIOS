# ============================================================
# test_agent_real_tasks.py
#
# REAL PAIO AGENT - MULTI TASK BROWSER TEST
#
# Purpose:
#   Validate that the complete PAIO agent can execute
#   multiple real natural-language browser tasks.
#
# Flow:
#
# User Request
#      ↓
# Agent Controller
#      ↓
# Action Planner
#      ↓
# Execution Engine
#      ↓
# Browser Automation
#      ↓
# Target Resolver
#      ↓
# Result
#
# ============================================================

from app.core.agent_controller import agent_controller


# ============================================================
# TEST CONFIGURATION
# ============================================================

TEST_CASES = [

    {
        "name": "Search Python tutorials",
        "request": "Search for Python tutorials"
    },

    {
        "name": "Search and click first result",
        "request": (
            "Search for Python tutorials "
            "and click first search result"
        )
    },

    {
        "name": "Search Java tutorials",
        "request": "Search for Java tutorials"
    },

    {
        "name": "Open Python website",
        "request": "Open https://www.python.org"
    },

]


# ============================================================
# HEADER
# ============================================================

print("\n")
print("=" * 70)
print("🤖 PAIO — REAL MULTI-TASK AGENT TEST")
print("=" * 70)

print("\nTesting complete agent pipeline:")
print("Agent Controller")
print("      ↓")
print("Action Planner")
print("      ↓")
print("Execution Engine")
print("      ↓")
print("Browser Automation")
print("      ↓")
print("Real Browser")
print("=" * 70)


# ============================================================
# TEST STATISTICS
# ============================================================

total_tests = len(TEST_CASES)

passed_tests = 0
failed_tests = 0

results = []


# ============================================================
# RUN TEST CASES
# ============================================================

for index, test_case in enumerate(
    TEST_CASES,
    start=1
):

    name = test_case["name"]
    user_request = test_case["request"]

    print("\n")
    print("=" * 70)
    print(
        f"🧪 TEST {index}/{total_tests}: {name}"
    )
    print("=" * 70)

    print("\nUSER REQUEST")
    print("-" * 70)

    print(user_request)

    # --------------------------------------------------------
    # RUN AGENT
    # --------------------------------------------------------

    try:

        result = agent_controller.run(
            user_request
        )

    except Exception as e:

        print("\n❌ AGENT CRASHED")

        print(
            f"Error: {e}"
        )

        result = {
            "status": "failed",
            "error": str(e)
        }

    # --------------------------------------------------------
    # DISPLAY RESULT
    # --------------------------------------------------------

    print("\n")
    print("📦 TEST RESULT")
    print("-" * 70)

    print(result)

    # --------------------------------------------------------
    # VALIDATION
    # --------------------------------------------------------

    test_passed = True

    print("\n")
    print("🔎 VALIDATION")
    print("-" * 70)

    # ========================================================
    # CHECK 1 — RESULT EXISTS
    # ========================================================

    if isinstance(result, dict):

        print(
            "✅ Agent returned a dictionary."
        )

    else:

        print(
            "❌ Agent did not return a dictionary."
        )

        test_passed = False

    # ========================================================
    # CHECK 2 — STATUS
    # ========================================================

    final_status = None

    if isinstance(result, dict):

        final_status = result.get(
            "status"
        )

    if final_status == "success":

        print(
            "✅ Final status: SUCCESS"
        )

    else:

        print(
            f"⚠️ Final status: {final_status}"
        )

        test_passed = False

    # ========================================================
    # CHECK 3 — PLAN
    # ========================================================

    plan = []

    if isinstance(result, dict):

        plan = result.get(
            "plan",
            []
        )

    if isinstance(plan, list) and plan:

        print(
            f"✅ Plan generated: "
            f"{len(plan)} action(s)"
        )

    else:

        print(
            "❌ No valid plan generated."
        )

        test_passed = False

    # ========================================================
    # CHECK 4 — EXECUTION
    # ========================================================

    execution = {}

    if isinstance(result, dict):

        execution = result.get(
            "execution",
            {}
        )

    if isinstance(execution, dict):

        print(
            "✅ Execution result returned."
        )

    else:

        print(
            "❌ Execution result missing."
        )

        test_passed = False

    # ========================================================
    # CHECK 5 — EXECUTION STATUS
    # ========================================================

    execution_status = None

    if isinstance(execution, dict):

        execution_status = execution.get(
            "status"
        )

    if execution_status == "success":

        print(
            "✅ Execution status: SUCCESS"
        )

    else:

        print(
            f"⚠️ Execution status: "
            f"{execution_status}"
        )

        test_passed = False

    # ========================================================
    # CHECK 6 — REPLANS
    # ========================================================

    replans_used = 0

    if isinstance(execution, dict):

        replans_used = execution.get(
            "replans_used",
            0
        )

    print(
        f"🔄 Replans used: {replans_used}"
    )

    # Replanning is NOT mandatory for this test.
    #
    # A normal successful task should ideally finish
    # without needing recovery.

    if replans_used == 0:

        print(
            "ℹ️ Task completed without replanning."
        )

    else:

        print(
            "ℹ️ Recovery/replanning was required."
        )

    # ========================================================
    # CHECK 7 — REPLAN HISTORY
    # ========================================================

    replan_history = []

    if isinstance(execution, dict):

        replan_history = execution.get(
            "replan_history",
            []
        )

    if isinstance(replan_history, list):

        print(
            f"📚 Replan history entries: "
            f"{len(replan_history)}"
        )

    # ========================================================
    # TEST RESULT
    # ========================================================

    if test_passed:

        passed_tests += 1

        print("\n")
        print(
            "✅ TEST PASSED"
        )

    else:

        failed_tests += 1

        print("\n")
        print(
            "❌ TEST FAILED"
        )

    # --------------------------------------------------------
    # STORE RESULT
    # --------------------------------------------------------

    results.append(
        {
            "name": name,
            "request": user_request,
            "status": final_status,
            "execution_status": execution_status,
            "replans_used": replans_used,
            "passed": test_passed
        }
    )


# ============================================================
# FINAL SUMMARY
# ============================================================

print("\n")
print("=" * 70)
print("📊 MULTI-TASK TEST SUMMARY")
print("=" * 70)

print(
    f"Total tests : {total_tests}"
)

print(
    f"Passed      : {passed_tests}"
)

print(
    f"Failed      : {failed_tests}"
)


# ============================================================
# INDIVIDUAL RESULTS
# ============================================================

print("\n")
print("TEST RESULTS")
print("-" * 70)

for result in results:

    status = (
        "✅ PASS"
        if result["passed"]
        else "❌ FAIL"
    )

    print(
        f"{status} | "
        f"{result['name']} | "
        f"status={result['status']} | "
        f"execution={result['execution_status']} | "
        f"replans={result['replans_used']}"
    )


# ============================================================
# FINAL VALIDATION
# ============================================================

print("\n")
print("=" * 70)

if failed_tests == 0:

    print(
        "🚀 REAL MULTI-TASK AGENT TEST PASSED"
    )

    print(
        "All real browser tasks completed successfully."
    )

else:

    print(
        "⚠️ REAL MULTI-TASK AGENT TEST COMPLETED WITH FAILURES"
    )

    print(
        "Review the failed task(s) above."
    )

print("=" * 70)


# ============================================================
# END
# ============================================================

print("\n🏁 TEST FINISHED")