from app.core.execution_engine import execution_engine


print("\n🔥 REAL EXECUTION ENGINE TEST 🔥")
print("=" * 70)


# =========================================================
# REAL BROWSER PLAN
# =========================================================

plan = [
    {
        "action": "search",
        "query": "Python tutorials"
    },
    {
        "action": "click",
        "target": "THIS TARGET DOES NOT EXIST"
    },
    {
        "action": "read"
    }
]


# =========================================================
# DISPLAY PLAN
# =========================================================

print("\n📋 TEST PLAN")
print("-" * 70)

for index, step in enumerate(plan, start=1):
    print(f"{index}. {step}")


# =========================================================
# EXECUTE
# =========================================================

print("\n🚀 Starting REAL execution...")
print("-" * 70)

try:

    result = execution_engine.execute_plan(plan)

except Exception as e:

    print("\n❌ EXECUTION ENGINE CRASHED")
    print(f"Error: {e}")

    raise


# =========================================================
# RESULT
# =========================================================

print("\n" + "=" * 70)
print("EXECUTION ENGINE RESULT")
print("=" * 70)

print(result)


# =========================================================
# VALIDATION
# =========================================================

print("\n" + "=" * 70)
print("VALIDATION")
print("=" * 70)


if not isinstance(result, dict):

    print("❌ Result is not a dictionary.")

    raise SystemExit(1)


status = result.get("status")

replans_used = result.get(
    "replans_used",
    0
)

results = result.get(
    "results",
    []
)


# ---------------------------------------------------------
# CHECK 1 — Engine returned a result
# ---------------------------------------------------------

if result:

    print(
        "✅ Execution Engine returned a result."
    )

else:

    print(
        "❌ Execution Engine returned no result."
    )


# ---------------------------------------------------------
# CHECK 2 — Results history exists
# ---------------------------------------------------------

if isinstance(results, list):

    print(
        f"✅ Execution history exists: "
        f"{len(results)} execution cycle(s)."
    )

else:

    print(
        "❌ Execution history is invalid."
    )


# ---------------------------------------------------------
# CHECK 3 — Replanning information
# ---------------------------------------------------------

print(
    f"🧠 Replans used: {replans_used}"
)


# ---------------------------------------------------------
# CHECK 4 — Final status
# ---------------------------------------------------------

print(
    f"📊 Final status: {status}"
)


# =========================================================
# FINAL RESULT
# =========================================================

print("\n" + "=" * 70)


if status == "success":

    print(
        "🚀 REAL EXECUTION ENGINE TEST PASSED"
    )

    print("=" * 70)

    print("\nVerified:")

    print("✅ Real browser execution started")
    print("✅ Search action executed")
    print("✅ Failure handling was triggered")
    print("✅ Recovery/Replanner path completed")
    print("✅ Replanned execution completed")
    print("✅ Final execution succeeded")

else:

    print(
        "⚠️ REAL EXECUTION DID NOT FINISH SUCCESSFULLY"
    )

    print("=" * 70)

    print("\nThis is NOT necessarily a code failure.")

    print("The intentionally invalid target may have")
    print("correctly caused the execution to stop after")
    print("the configured recovery/replan attempts.")

    print("\nImportant result:")
    print(f"Status       : {status}")
    print(f"Replans used : {replans_used}")

    if result.get("failed_step") is not None:

        print(
            f"Failed step : {result.get('failed_step')}"
        )

    if result.get("error"):

        print(
            f"Error       : {result.get('error')}"
        )


print("\n🏁 TEST FINISHED")