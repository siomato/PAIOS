from app.core.execution_engine import execution_engine
from app.core.action_executor import action_executor
from app.core.recovery_engine import recovery_engine


print("\n🔥 EXECUTION ENGINE TEST 🔥")
print("=" * 60)


# =========================================================
# TEST STATE
# =========================================================

execution_count = 0
recovery_count = 0


# =========================================================
# FAKE ACTION EXECUTOR
# =========================================================

def fake_execute(steps):

    global execution_count

    execution_count += 1

    print(
        f"\n⚙️ Action Executor called "
        f"(execution #{execution_count})"
    )

    for index, step in enumerate(steps, start=1):
        print(f"   {index}. {step}")

    # -----------------------------------------------------
    # FIRST EXECUTION = FAILURE
    # -----------------------------------------------------

    if execution_count == 1:

        print(
            "\n❌ Simulated action failure."
        )

        return {
            "status": "failed",
            "steps": [
                {
                    "step": 1,
                    "action": steps[0],
                    "status": "success"
                },
                {
                    "step": 2,
                    "action": steps[1],
                    "status": "failed",
                    "error": "Target could not be resolved."
                }
            ],
            "failed_step": 2,
            "error": "Could not resolve target."
        }

    # -----------------------------------------------------
    # SECOND EXECUTION = SUCCESS
    # -----------------------------------------------------

    print(
        "\n✅ Simulated replanned execution succeeded."
    )

    return {
        "status": "success",
        "steps": [
            {
                "step": index,
                "action": step,
                "status": "success"
            }
            for index, step in enumerate(
                steps,
                start=1
            )
        ]
    }


# =========================================================
# FAKE RECOVERY ENGINE
# =========================================================

def fake_recover(plan, failure):

    global recovery_count

    recovery_count += 1

    print(
        "\n🔄 Recovery Engine called."
    )

    print(
        f"Recovery attempt: {recovery_count}"
    )

    print(
        f"Failed step: "
        f"{failure.get('failed_step')}"
    )

    print(
        f"Error: "
        f"{failure.get('error')}"
    )

    # -----------------------------------------------------
    # SIMULATED REPLANNED PLAN
    # -----------------------------------------------------

    new_plan = [
        {
            "action": "read"
        },
        {
            "action": "click",
            "target": "recovered target"
        },
        {
            "action": "read"
        }
    ]

    print("\n🧠 Replanner generated:")
    
    for index, step in enumerate(
        new_plan,
        start=1
    ):
        print(
            f"{index}. {step}"
        )

    return {
        "status": "success",
        "steps": new_plan,
        "replans_used": 1
    }


# =========================================================
# REPLACE REAL METHODS WITH TEST METHODS
# =========================================================

action_executor.execute = fake_execute

recovery_engine.recover = fake_recover


# =========================================================
# RESET ENGINE STATE
# =========================================================

execution_engine.replans_used = 0


# =========================================================
# ORIGINAL PLAN
# =========================================================

original_plan = [

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


print("\n📋 ORIGINAL PLAN")

for index, step in enumerate(
    original_plan,
    start=1
):

    print(
        f"{index}. {step}"
    )


# =========================================================
# RUN EXECUTION ENGINE
# =========================================================

print("\n🚀 Starting Execution Engine...")

result = execution_engine.execute_plan(
    original_plan
)


# =========================================================
# RESULT
# =========================================================

print("\n" + "=" * 60)
print("EXECUTION ENGINE RESULT")
print("=" * 60)

print(result)


# =========================================================
# VALIDATION
# =========================================================

print("\n" + "=" * 60)
print("VALIDATION")
print("=" * 60)


checks = []


# ---------------------------------------------------------
# CHECK 1
# ---------------------------------------------------------

checks.append(
    (
        result.get("status") == "success",
        "Execution eventually succeeded"
    )
)


# ---------------------------------------------------------
# CHECK 2
# ---------------------------------------------------------

checks.append(
    (
        execution_count == 2,
        "Executor ran original plan and replanned plan"
    )
)


# ---------------------------------------------------------
# CHECK 3
# ---------------------------------------------------------

checks.append(
    (
        recovery_count == 1,
        "Recovery Engine was invoked once"
    )
)


# ---------------------------------------------------------
# CHECK 4
# ---------------------------------------------------------

checks.append(
    (
        result.get("replans_used") == 1,
        "Exactly one replan was used"
    )
)


# ---------------------------------------------------------
# CHECK 5
# ---------------------------------------------------------

final_plan = result.get(
    "final_plan",
    []
)

checks.append(
    (
        len(final_plan) == 3,
        "Final replanned plan contains three actions"
    )
)


# =========================================================
# PRINT VALIDATION
# =========================================================

passed = 0

for status, message in checks:

    if status:

        print(
            f"✅ {message}"
        )

        passed += 1

    else:

        print(
            f"❌ {message}"
        )


# =========================================================
# FINAL RESULT
# =========================================================

print("\n" + "=" * 60)

if passed == len(checks):

    print(
        "🚀 EXECUTION ENGINE TEST PASSED"
    )

    print("=" * 60)

    print("\nVerified:")

    print("✅ Original plan executed")

    print("✅ Failure detected")

    print("✅ Recovery Engine invoked")

    print("✅ Replanned plan generated")

    print("✅ New plan executed")

    print("✅ Execution completed successfully")

else:

    print(
        "❌ EXECUTION ENGINE TEST FAILED"
    )

    print(
        f"Passed {passed}/{len(checks)} checks."
    )

print("=" * 60)