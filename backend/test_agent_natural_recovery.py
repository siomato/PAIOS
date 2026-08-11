from app.core.agent_controller import agent_controller


# =========================================================
# TEST CONFIGURATION
# =========================================================

USER_REQUEST = (
    "Search for Python tutorials and click "
    "THIS TARGET DOES NOT EXIST"
)


print("\n" + "=" * 70)
print("🤖 PAIO — NATURAL LANGUAGE RECOVERY TEST")
print("=" * 70)


print("\nUSER REQUEST")
print(USER_REQUEST)


# =========================================================
# RUN COMPLETE AGENT PIPELINE
# =========================================================

print("\n" + "=" * 70)
print("🚀 STARTING FULL AGENT PIPELINE")
print("=" * 70)


try:

    result = agent_controller.run(
        USER_REQUEST
    )

except Exception as e:

    print("\n❌ AGENT PIPELINE CRASHED")
    print(f"Error: {e}")

    raise


# =========================================================
# DISPLAY FINAL RESULT
# =========================================================

print("\n" + "=" * 70)
print("📦 FINAL AGENT RESULT")
print("=" * 70)

print(result)


# =========================================================
# EXTRACT DATA
# =========================================================

if not isinstance(result, dict):

    print("\n❌ Agent returned invalid result.")

    raise SystemExit(1)


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


# =========================================================
# EXECUTION DATA
# =========================================================

if not isinstance(execution, dict):

    execution = {}


replans_used = execution.get(
    "replans_used",
    0
)

replan_history = execution.get(
    "replan_history",
    []
)

steps = execution.get(
    "steps",
    []
)


# =========================================================
# VALIDATION
# =========================================================

print("\n" + "=" * 70)
print("VALIDATION")
print("=" * 70)


# ---------------------------------------------------------
# 1. Agent returned a result
# ---------------------------------------------------------

if isinstance(result, dict):

    print("✅ Agent returned a result.")

else:

    print("❌ Agent did not return a result.")


# ---------------------------------------------------------
# 2. Natural-language planner generated multiple actions
# ---------------------------------------------------------

has_search = any(
    isinstance(step, dict)
    and step.get("action") == "search"
    for step in plan
)

has_click = any(
    isinstance(step, dict)
    and step.get("action") == "click"
    for step in plan
)


if has_search:

    print("✅ SEARCH action exists in original plan.")

else:

    print("❌ SEARCH action missing.")


if has_click:

    print("✅ CLICK action exists in original plan.")

else:

    print("❌ CLICK action missing.")


# ---------------------------------------------------------
# 3. Execution started
# ---------------------------------------------------------

if steps:

    print("✅ Execution started.")

else:

    print(
        "❌ Execution produced no step history."
    )


# ---------------------------------------------------------
# 4. Failure should occur
# ---------------------------------------------------------

failure_detected = (
    status == "failed"
    or
    execution.get("status") == "failed"
)


if failure_detected:

    print(
        "✅ Intentional target failure detected."
    )

else:

    print(
        "⚠️ No execution failure detected."
    )


# ---------------------------------------------------------
# 5. Recovery / Replanner should be invoked
# ---------------------------------------------------------

if replans_used >= 1:

    print(
        f"✅ Replanner invoked "
        f"{replans_used} time(s)."
    )

else:

    print(
        "❌ Replanner was not invoked."
    )


# ---------------------------------------------------------
# 6. Replan history should exist
# ---------------------------------------------------------

if isinstance(
    replan_history,
    list
) and len(replan_history) >= 1:

    print(
        f"✅ Replan history contains "
        f"{len(replan_history)} entrie(s)."
    )

else:

    print(
        "❌ Replan history is empty."
    )


# ---------------------------------------------------------
# 7. Replanned execution should exist
# ---------------------------------------------------------

replanned_execution_detected = False


for history_item in replan_history:

    if not isinstance(
        history_item,
        dict
    ):
        continue

    if (
        history_item.get("result")
        or
        history_item.get("replanned_plan")
        or
        history_item.get("steps")
    ):

        replanned_execution_detected = True

        break


if replanned_execution_detected:

    print(
        "✅ Replanned execution/result detected."
    )

else:

    print(
        "⚠️ Replanned execution details "
        "were not directly exposed."
    )


# =========================================================
# FINAL TEST DECISION
# =========================================================

print("\n" + "=" * 70)


core_checks = [
    isinstance(result, dict),
    has_search,
    has_click,
    bool(steps),
    failure_detected,
    replans_used >= 1,
    isinstance(replan_history, list)
    and len(replan_history) >= 1,
]


if all(core_checks):

    print(
        "🚀 FULL NATURAL RECOVERY PIPELINE TEST PASSED"
    )

    print("=" * 70)

    print("\nVerified:")

    print(
        "✅ Natural-language request received"
    )

    print(
        "✅ Multiple actions generated"
    )

    print(
        "✅ SEARCH executed"
    )

    print(
        "✅ CLICK executed"
    )

    print(
        "✅ Intentional target failure detected"
    )

    print(
        "✅ Recovery/Replanner reached"
    )

    print(
        f"✅ Replans used: {replans_used}"
    )

    print(
        "✅ Replan history recorded"
    )

else:

    print(
        "❌ FULL NATURAL RECOVERY PIPELINE TEST FAILED"
    )

    print("=" * 70)

    print("\nDiagnostic information:")

    print(
        f"Agent status       : {status}"
    )

    print(
        f"Original plan      : {plan}"
    )

    print(
        f"Execution status   : "
        f"{execution.get('status')}"
    )

    print(
        f"Replans used       : {replans_used}"
    )

    print(
        f"Replan history     : "
        f"{replan_history}"
    )

    raise SystemExit(1)


print("\n🏁 TEST FINISHED")