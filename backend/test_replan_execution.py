from app.core.replanner import replanner


def print_plan(title, plan):
    print("\n" + "=" * 60)
    print(title)
    print("=" * 60)

    for i, step in enumerate(plan, start=1):
        print(f"{i}. {step}")


def main():

    print("\n🧠 REPLAN EXECUTION TEST 🧠")

    # ---------------------------------------------------------
    # ORIGINAL PLAN
    # ---------------------------------------------------------

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

    print_plan(
        "ORIGINAL PLAN",
        original_plan
    )

    # ---------------------------------------------------------
    # SIMULATE FAILURE
    # ---------------------------------------------------------

    failed_step = 2

    failure = {
        "error": "Could not resolve target: THIS TARGET DOES NOT EXIST",
        "error_type": "target"
    }

    print("\n❌ Simulated failure")
    print(f"Failed step : {failed_step}")
    print(f"Failure     : {failure}")

    # ---------------------------------------------------------
    # CALL REPLANNER
    # ---------------------------------------------------------

    result = replanner.replan(
        original_steps=original_plan,
        failed_step=failed_step,
        failure=failure
    )

    # ---------------------------------------------------------
    # VALIDATE REPLANNER
    # ---------------------------------------------------------

    if result.get("status") != "success":

        print("\n❌ REPLANNING FAILED")
        print(result)

        return

    new_plan = result.get(
        "steps",
        []
    )

    print_plan(
        "GENERATED REPLAN",
        new_plan
    )

    # ---------------------------------------------------------
    # VALIDATION
    # ---------------------------------------------------------

    print("\n" + "=" * 60)
    print("VALIDATION")
    print("=" * 60)

    checks = []

    # Check 1
    checks.append(
        (
            len(new_plan) > 0,
            "Replanner generated a new plan"
        )
    )

    # Check 2
    has_read = any(
        step.get("action") == "read"
        for step in new_plan
        if isinstance(step, dict)
    )

    checks.append(
        (
            has_read,
            "READ action exists in replanned plan"
        )
    )

    # Check 3
    has_click = any(
        step.get("action") == "click"
        for step in new_plan
        if isinstance(step, dict)
    )

    checks.append(
        (
            has_click,
            "CLICK action exists in replanned plan"
        )
    )

    # Check 4
    original_target_preserved = any(
        step.get("target") == "THIS TARGET DOES NOT EXIST"
        for step in new_plan
        if isinstance(step, dict)
    )

    checks.append(
        (
            original_target_preserved,
            "Original failed target is preserved"
        )
    )

    # Check 5
    remaining_read_preserved = any(
        step.get("action") == "read"
        for step in new_plan[2:]
        if isinstance(step, dict)
    )

    checks.append(
        (
            remaining_read_preserved,
            "Remaining original steps are preserved"
        )
    )

    # ---------------------------------------------------------
    # PRINT RESULTS
    # ---------------------------------------------------------

    passed = 0

    for status, message in checks:

        if status:

            print(f"✅ {message}")
            passed += 1

        else:

            print(f"❌ {message}")

    print("\n" + "=" * 60)

    if passed == len(checks):

        print("🚀 REPLAN EXECUTION PREPARATION TEST PASSED")
        print("=" * 60)

        print("\nVerified:")

        print("✅ Failure reaches Replanner")
        print("✅ New actions are generated")
        print("✅ READ recovery action exists")
        print("✅ CLICK retry exists")
        print("✅ Failed target is preserved")
        print("✅ Remaining plan is preserved")

    else:

        print("❌ REPLAN TEST FAILED")
        print(
            f"Passed {passed}/{len(checks)} checks."
        )


if __name__ == "__main__":
    main()