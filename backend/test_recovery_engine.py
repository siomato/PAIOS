from app.core.recovery_engine import recovery_engine


# =========================================================
# RECOVERY ENGINE TEST
# =========================================================

print("🛡️ RECOVERY ENGINE INTEGRATION TEST 🛡️")
print("=" * 60)


# =========================================================
# TEST PLAN
# =========================================================

test_plan = [

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


# =========================================================
# DISPLAY TEST PLAN
# =========================================================

print("\n📋 TEST PLAN")

for index, step in enumerate(
    test_plan,
    start=1
):

    print(
        f"{index}. {step}"
    )


# =========================================================
# START RECOVERY ENGINE
# =========================================================

print(
    "\n🚀 Starting Recovery Engine..."
)

print(
    "=" * 60
)


try:

    result = recovery_engine.execute(
        test_plan,
        max_retries=1
    )


except Exception as e:

    print(
        "\n❌ RECOVERY ENGINE CRASHED"
    )

    print(
        f"Error: {e}"
    )

    raise


# =========================================================
# DISPLAY RESULT
# =========================================================

print(
    "\n" + "=" * 60
)

print(
    "RECOVERY ENGINE RESULT"
)

print(
    "=" * 60
)

print(
    result
)


# =========================================================
# VALIDATION
# =========================================================

print(
    "\n" + "=" * 60
)

print(
    "VALIDATION"
)

print(
    "=" * 60
)


status = result.get(
    "status"
)


if status == "success":

    print(
        "✅ Recovery Engine completed successfully."
    )

    print(
        f"✅ Replans used: "
        f"{result.get('replans', 0)}"
    )

    print(
        "\n🎉 RECOVERY ENGINE TEST PASSED"
    )


else:

    print(
        "❌ Recovery Engine test failed."
    )

    print(
        f"Failed step: "
        f"{result.get('failed_step')}"
    )

    print(
        f"Error: "
        f"{result.get('error')}"
    )

    print(
        "\n❌ RECOVERY ENGINE TEST FAILED"
    )