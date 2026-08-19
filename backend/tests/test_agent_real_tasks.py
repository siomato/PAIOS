# ============================================================
# tests/test_agent_real_tasks.py
#
# PAIO — REAL MULTI-TASK AGENT TEST
#
# Tests:
#
# 1. Search Python tutorials
# 2. Search Python tutorials and click first result
# 3. Search Java tutorials
# 4. Open Python website
#
# Pipeline:
#
# User Request
#      ↓
# AgentController
#      ↓
# ActionPlanner
#      ↓
# RecoveryEngine
#      ↓
# ActionExecutor
#      ↓
# BrowserAutomation
#
# AgentState is also passed through the execution pipeline.
# ============================================================

from app.core.agent_controller import agent_controller


# ============================================================
# TEST CONFIGURATION
# ============================================================

TESTS = [

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


# ============================================================
# RESULTS
# ============================================================

results = []

passed = 0
failed = 0


# ============================================================
# RUN TESTS
# ============================================================

for index, test in enumerate(
    TESTS,
    start=1
):

    name = test["name"]
    request = test["request"]

    print("\n")
    print("=" * 70)
    print(
        f"🧪 TEST {index}/{len(TESTS)}"
    )
    print("=" * 70)

    print(
        f"\nTask: {name}"
    )

    print(
        f"Request: {request}"
    )

    try:

        # ====================================================
        # RUN COMPLETE AGENT
        # ====================================================

        result = agent_controller.run(
            request
        )

        # ====================================================
        # BASIC VALIDATION
        # ====================================================

        if not isinstance(
            result,
            dict
        ):

            print(
                "❌ Agent returned invalid result."
            )

            results.append({
                "name": name,
                "status": "failed",
                "execution": "failed",
                "replans": 0
            })

            failed += 1

            continue

        # ====================================================
        # EXTRACT RESULT
        # ====================================================

        status = result.get(
            "status"
        )

        execution = result.get(
            "execution",
            {}
        )

        execution_status = execution.get(
            "status"
        )

        replans_used = execution.get(
            "replans_used",
            0
        )

        # ====================================================
        # SUCCESS
        # ====================================================

        if (
            status == "success"
            and
            execution_status == "success"
        ):

            print(
                "\n✅ TEST PASSED"
            )

            print(
                f"   Plan generated: "
                f"{len(result.get('plan', []))} action(s)"
            )

            print(
                "   Execution result returned."
            )

            print(
                f"   Execution status: "
                f"{execution_status}"
            )

            print(
                f"   Replans used: "
                f"{replans_used}"
            )

            results.append({
                "name": name,
                "status": "success",
                "execution": execution_status,
                "replans": replans_used
            })

            passed += 1

        # ====================================================
        # FAILURE
        # ====================================================

        else:

            print(
                "\n❌ TEST FAILED"
            )

            print(
                f"   Agent status: "
                f"{status}"
            )

            print(
                f"   Execution status: "
                f"{execution_status}"
            )

            print(
                f"   Error: "
                f"{result.get('error')}"
            )

            results.append({
                "name": name,
                "status": status,
                "execution": execution_status,
                "replans": replans_used
            })

            failed += 1

    except Exception as e:

        print(
            "\n❌ TEST EXCEPTION"
        )

        print(
            f"   {type(e).__name__}: {e}"
        )

        results.append({
            "name": name,
            "status": "failed",
            "execution": "exception",
            "replans": 0
        })

        failed += 1


# ============================================================
# SUMMARY
# ============================================================

print("\n")
print("=" * 70)
print("📊 MULTI-TASK TEST SUMMARY")
print("=" * 70)

print(
    f"Total tests : {len(TESTS)}"
)

print(
    f"Passed      : {passed}"
)

print(
    f"Failed      : {failed}"
)


# ============================================================
# INDIVIDUAL RESULTS
# ============================================================

print("\n")
print("TEST RESULTS")
print("-" * 70)

for item in results:

    if (
        item["status"] == "success"
        and
        item["execution"] == "success"
    ):

        print(
            "✅ PASS | "
            f"{item['name']} | "
            f"status={item['status']} | "
            f"execution={item['execution']} | "
            f"replans={item['replans']}"
        )

    else:

        print(
            "❌ FAIL | "
            f"{item['name']} | "
            f"status={item['status']} | "
            f"execution={item['execution']} | "
            f"replans={item['replans']}"
        )


# ============================================================
# FINAL RESULT
# ============================================================

print("\n")
print("=" * 70)

if failed == 0:

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
# FINISHED
# ============================================================

print("\n🏁 TEST FINISHED")