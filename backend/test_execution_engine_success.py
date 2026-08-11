from app.core.execution_engine import execution_engine


print("\n" + "=" * 60)
print("REAL EXECUTION ENGINE TEST")
print("=" * 60)


# ---------------------------------------------------------
# REAL EXECUTION PLAN
# ---------------------------------------------------------

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


print("\n📋 ORIGINAL PLAN")

for i, step in enumerate(plan, start=1):
    print(f"{i}. {step}")


# ---------------------------------------------------------
# EXECUTE
# ---------------------------------------------------------

print("\n🚀 Starting real execution...\n")

try:

    result = execution_engine.execute_plan(plan)

except Exception as e:

    print("\n❌ EXECUTION ENGINE CRASHED")
    print(f"Error: {e}")
    raise


# ---------------------------------------------------------
# RESULT
# ---------------------------------------------------------

print("\n" + "=" * 60)
print("EXECUTION ENGINE RESULT")
print("=" * 60)

print(result)


# ---------------------------------------------------------
# VALIDATION
# ---------------------------------------------------------

print("\n" + "=" * 60)
print("VALIDATION")
print("=" * 60)


if not isinstance(result, dict):

    print("❌ Result is not a dictionary.")

    raise SystemExit(1)


print("✅ Execution Engine returned a result.")


status = result.get("status")

print(f"📊 Final status: {status}")


if status == "success":

    print("✅ REAL EXECUTION SUCCEEDED")
    print("✅ Search executed")
    print("✅ Target resolved")
    print("✅ Click executed")
    print("✅ Page read")
    print("🚀 REAL EXECUTION ENGINE VERIFIED")

else:

    print("❌ REAL EXECUTION DID NOT SUCCEED")

    print("\nResult details:")

    print(
        f"Failed step: "
        f"{result.get('failed_step')}"
    )

    print(
        f"Error: "
        f"{result.get('error')}"
    )