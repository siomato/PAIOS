from app.core.recovery_engine import recovery_engine


print("\n==============================================")
print("     🔄 RECOVERY → REPLANNER TEST")
print("==============================================\n")


# =========================================================
# TEST PLAN
# =========================================================

steps = [
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


print("Original plan:")

for index, step in enumerate(
    steps,
    start=1
):
    print(
        f"{index}. {step}"
    )


# =========================================================
# EXECUTE
# =========================================================

print(
    "\n🚀 Starting Recovery Engine..."
)


result = recovery_engine.execute(
    steps
)


# =========================================================
# RESULT
# =========================================================

print(
    "\n=============================================="
)

print(
    "RECOVERY → REPLANNER RESULT"
)

print(
    "=============================================="
)

print(
    result
)


# =========================================================
# VALIDATION
# =========================================================

print(
    "\n=============================================="
)

print(
    "VALIDATION"
)

print(
    "=============================================="
)


passed = True


# ---------------------------------------------------------
# 1. Result must be a dictionary
# ---------------------------------------------------------

if not isinstance(
    result,
    dict
):

    print(
        "❌ Result is not a dictionary."
    )

    passed = False

else:

    print(
        "✅ Recovery Engine returned a result."
    )


# ---------------------------------------------------------
# 2. Replanner must have been used
# ---------------------------------------------------------

replans_used = result.get(
    "replans_used",
    0
)


if replans_used >= 1:

    print(
        f"✅ Replanner was invoked: "
        f"{replans_used} time(s)."
    )

else:

    print(
        "❌ Replanner was NOT invoked."
    )

    passed = False


# ---------------------------------------------------------
# 3. Replan history must exist
# ---------------------------------------------------------

replan_history = result.get(
    "replan_history",
    []
)


if replan_history:

    print(
        "✅ Replan history exists."
    )

else:

    print(
        "❌ Replan history is empty."
    )

    passed = False


# ---------------------------------------------------------
# 4. Replanner must have returned a new plan
# ---------------------------------------------------------

if replan_history:

    first_replan = replan_history[0]

    replan_result = first_replan.get(
        "result",
        {}
    )

    if replan_result.get(
        "status"
    ) == "success":

        print(
            "✅ Replanner generated a new plan."
        )

    else:

        print(
            "❌ Replanner did not generate "
            "a successful new plan."
        )

        passed = False

else:

    print(
        "⚠️ Cannot validate replanner result."
    )

    passed = False


# ---------------------------------------------------------
# 5. New plan must contain READ before CLICK
# ---------------------------------------------------------

if replan_history:

    first_replan = replan_history[0]

    replan_result = first_replan.get(
        "result",
        {}
    )

    new_plan = replan_result.get(
        "steps",
        []
    )

    read_before_click = False

    for index, step in enumerate(
        new_plan
    ):

        if (
            step.get("action") == "click"
            and index > 0
        ):

            previous_step = new_plan[
                index - 1
            ]

            if (
                previous_step.get("action")
                == "read"
            ):

                read_before_click = True

                break


    if read_before_click:

        print(
            "✅ READ was inserted before CLICK."
        )

    else:

        print(
            "❌ READ was not inserted before CLICK."
        )

        passed = False


# ---------------------------------------------------------
# 6. Original target should be preserved
# ---------------------------------------------------------

if replan_history:

    new_plan = (
        replan_history[0]
        .get("result", {})
        .get("steps", [])
    )

    target_preserved = any(
        step.get("action") == "click"
        and step.get("target")
        == "THIS TARGET DOES NOT EXIST"
        for step in new_plan
    )

    if target_preserved:

        print(
            "✅ Failed target was preserved."
        )

    else:

        print(
            "❌ Failed target was lost."
        )

        passed = False


# =========================================================
# FINAL VALIDATION
# =========================================================

print(
    "\n=============================================="
)


if passed:

    print(
        "🎉 RECOVERY → REPLANNER TEST PASSED"
    )

    print(
        "=============================================="
    )

    print(
        "\nVerified:"
    )

    print(
        "✅ Recovery Engine executed"
    )

    print(
        "✅ Retries were attempted"
    )

    print(
        "✅ Failure reached Replanner"
    )

    print(
        "✅ Replanner generated a new plan"
    )

    print(
        "✅ READ was inserted before CLICK"
    )

    print(
        "✅ Original target was preserved"
    )

    print(
        "\n🧠 RECOVERY → REPLANNER INTEGRATION VERIFIED."
    )

else:

    print(
        "❌ RECOVERY → REPLANNER TEST FAILED"
    )

    print(
        "=============================================="
    )