from app.core.agent_controller import agent_controller


print("\n" + "=" * 70)
print("🤖 PAIO — FULL RECOVERY PIPELINE TEST")
print("=" * 70)


# =========================================================
# INTENTIONALLY FAILING PLAN
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


print("\n📋 TEST PLAN")

for index, action in enumerate(plan, start=1):
    print(f"{index}. {action}")


# =========================================================
# EXECUTE THROUGH AGENT CONTROLLER
# =========================================================

print("\n" + "=" * 70)
print("🚀 STARTING RECOVERY TEST")
print("=" * 70)


try:

    # Use the controller's execution interface
    result = agent_controller.execute_plan(plan)

except Exception as e:

    print("\n❌ AGENT PIPELINE CRASHED")
    print(f"Error: {e}")
    raise


# =========================================================
# RESULT
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

    print("❌ Result is not a dictionary.")
    raise SystemExit(1)


print("✅ Agent returned a result.")


execution = result


replans_used = execution.get(
    "replans_used",
    0
)

replan_history = execution.get(
    "replan_history",
    []
)


print(
    f"🔄 Replans used: {replans_used}"
)

print(
    f"📜 Replan history entries: "
    f"{len(replan_history)}"
)


# =========================================================
# RECOVERY VALIDATION
# =========================================================

if replans_used > 0:

    print(
        "✅ Failure reached Recovery/Replanner."
    )

else:

    print(
        "❌ Recovery/Replanner was NOT invoked."
    )

    raise SystemExit(1)


# =========================================================
# REPLAN HISTORY
# =========================================================

if len(replan_history) > 0:

    print(
        "✅ Replan history exists."
    )

else:

    print(
        "❌ Replan history is empty."
    )

    raise SystemExit(1)


# =========================================================
# FINAL STATUS
# =========================================================

print(
    f"📊 Final status: "
    f"{execution.get('status')}"
)


print("\n" + "=" * 70)
print("🚀 FULL RECOVERY PIPELINE TEST PASSED")
print("=" * 70)