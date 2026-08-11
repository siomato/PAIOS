from app.core.agent_controller import agent_controller


print("\n" + "=" * 70)
print("🤖 PAIO — FULL AGENT PIPELINE TEST")
print("=" * 70)


# =========================================================
# USER REQUEST
# =========================================================

user_request = "Search for Python tutorials and open the first result"


print("\n👤 USER REQUEST")
print(user_request)


# =========================================================
# EXECUTE FULL PIPELINE
# =========================================================

print("\n" + "=" * 70)
print("🚀 STARTING AGENT")
print("=" * 70)

try:

    result = agent_controller.run(
        user_request
    )

except Exception as e:

    print("\n❌ AGENT PIPELINE CRASHED")
    print(f"Error: {e}")

    raise


# =========================================================
# FINAL RESULT
# =========================================================

print("\n" + "=" * 70)
print("📊 FINAL AGENT RESULT")
print("=" * 70)

print(result)


# =========================================================
# VALIDATION
# =========================================================

print("\n" + "=" * 70)
print("VALIDATION")
print("=" * 70)


if not isinstance(result, dict):

    print("❌ Agent did not return a dictionary.")
    raise SystemExit(1)


print("✅ Agent returned a result.")


status = result.get("status")

print(f"📌 Final status: {status}")


# =========================================================
# SUCCESS
# =========================================================

if status == "success":

    print("✅ Intent processed")
    print("✅ Plan generated")
    print("✅ Execution started")
    print("✅ Browser action completed")
    print("✅ Final result returned")

    print("\n" + "=" * 70)
    print("🚀 FULL AGENT PIPELINE TEST PASSED")
    print("=" * 70)

else:

    print("⚠️ FULL PIPELINE DID NOT FINISH SUCCESSFULLY")

    print(
        f"Failed step: "
        f"{result.get('failed_step')}"
    )

    print(
        f"Error: "
        f"{result.get('error')}"
    )

    print("\nResult:")
    print(result)