from app.core.agent_controller import agent_controller


# ============================================================
# test_agent_natural_tasks.py
#
# NATURAL LANGUAGE TASK TEST
#
# User request
#      ↓
# Agent Controller
#      ↓
# Action Planner
#      ↓
# Multiple actions
#      ↓
# Execution Engine
#      ↓
# Browser
# ============================================================


print("\n" + "=" * 70)
print("🤖 PAIO — NATURAL LANGUAGE TASK TEST")
print("=" * 70)


# ============================================================
# TEST CASES
# ============================================================

TEST_CASES = [

    "Search for Python tutorials",

    "Search for Java tutorials",

    "Search for Python tutorials and click first search result",

    "Open https://www.python.org",

]


# ============================================================
# RUN TESTS
# ============================================================

results = []


for index, user_request in enumerate(
    TEST_CASES,
    start=1
):

    print("\n")
    print("=" * 70)
    print(f"🧪 TEST {index}/{len(TEST_CASES)}")
    print("=" * 70)

    print(
        f"\nUser request:\n"
        f"{user_request}"
    )

    try:

        result = agent_controller.run(
            user_request
        )

    except Exception as e:

        print(
            f"\n❌ Agent crashed: {e}"
        )

        result = {
            "status": "failed",
            "error": str(e)
        }

    # --------------------------------------------------------
    # Extract results
    # --------------------------------------------------------

    status = result.get(
        "status"
    )

    plan = result.get(
        "plan",
        []
    )

    execution = result.get(
        "execution",
        {}
    )

    execution_status = execution.get(
        "status"
    )

    replans = execution.get(
        "replans_used",
        0
    )

    # --------------------------------------------------------
    # Validation
    # --------------------------------------------------------

    passed = (
        status == "success"
        and
        execution_status == "success"
    )

    if passed:

        print(
            "\n✅ TEST PASSED"
        )

    else:

        print(
            "\n❌ TEST FAILED"
        )

        print(
            f"Status: {status}"
        )

        print(
            f"Execution: {execution_status}"
        )

        print(
            f"Error: {result.get('error')}"
        )

    print(
        f"\n📋 Generated actions: "
        f"{len(plan)}"
    )

    for step_number, step in enumerate(
        plan,
        start=1
    ):

        print(
            f"   {step_number}. {step}"
        )

    print(
        f"\n🔄 Replans used: {replans}"
    )

    results.append({
        "request": user_request,
        "status": status,
        "execution": execution_status,
        "replans": replans,
        "passed": passed
    })


# ============================================================
# SUMMARY
# ============================================================

print("\n")
print("=" * 70)
print("📊 NATURAL LANGUAGE TASK SUMMARY")
print("=" * 70)


total = len(results)

passed = sum(
    1
    for result in results
    if result["passed"]
)

failed = total - passed


print(
    f"\nTotal tests : {total}"
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

print("\nTEST RESULTS")
print("-" * 70)


for result in results:

    icon = (
        "✅"
        if result["passed"]
        else
        "❌"
    )

    print(
        f"{icon} "
        f"{result['request']} "
        f"| status={result['status']} "
        f"| execution={result['execution']} "
        f"| replans={result['replans']}"
    )


# ============================================================
# FINAL RESULT
# ============================================================

print("\n")
print("=" * 70)


if failed == 0:

    print(
        "🚀 NATURAL LANGUAGE TASK TEST PASSED"
    )

    print(
        "Agent successfully processed all natural-language tasks."
    )

else:

    print(
        "⚠️ NATURAL LANGUAGE TASK TEST COMPLETED WITH FAILURES"
    )

    print(
        "Review the failed task(s) above."
    )


print("=" * 70)

print("\n🏁 TEST FINISHED")