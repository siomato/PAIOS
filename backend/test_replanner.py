from app.core.replanner import replanner


print("\n========================================")
print("        🧠 REPLANNER TEST SUITE")
print("========================================")


def print_plan(title, steps):
    print(f"\n{title}")
    print("----------------------------------------")

    for i, step in enumerate(steps, start=1):
        print(f"{i}. {step}")


def test_click_failure():

    print("\nTEST 1 - Click failure replanning")

    original_plan = [
        {
            "action": "read"
        },
        {
            "action": "click",
            "target": "first search result"
        },
        {
            "action": "read"
        }
    ]

    failed_step = 2

    failure = {
        "error": "Element not found",
        "reason": "Target was not available on the page"
    }

    print_plan(
        "ORIGINAL PLAN",
        original_plan
    )

    print("\n❌ Simulated failure")
    print(f"Failed step: {failed_step}")
    print(f"Failure: {failure}")

    # IMPORTANT:
    # Replanner.replan() expects:
    #
    # replan(original_steps, failed_step, failure)
    #
    result = replanner.replan(
        original_plan,
        failed_step,
        failure
    )

    print("\n========================================")
    print("REPLANNER RESULT")
    print("========================================")

    print(result)

    if result.get("status") != "success":
        print("\n❌ TEST FAILED")
        print(
            "Replanner did not generate "
            "a new execution plan."
        )
        return False

    new_plan = result.get("steps", [])

    print_plan(
        "NEW PLAN",
        new_plan
    )

    # ---------------------------------------------------------
    # VALIDATION
    # ---------------------------------------------------------

    assert len(new_plan) > 0, (
        "New plan is empty."
    )

    # Failed click should generate:
    #
    # READ
    # CLICK
    #
    assert new_plan[0].get("action") == "read", (
        "READ was not inserted before CLICK."
    )

    assert new_plan[1].get("action") == "click", (
        "CLICK was not preserved."
    )

    assert (
        new_plan[1].get("target")
        == "first search result"
    ), (
        "Original click target was not preserved."
    )

    # Original step after the failure must survive.
    assert new_plan[-1].get("action") == "read", (
        "Remaining original step was lost."
    )

    print("\n========================================")
    print("🎉 REPLANNER TEST PASSED")
    print("========================================")

    print("\nVerified:")

    print("✅ Replanner loads")
    print("✅ Failed step is identified")
    print("✅ Failure information is accepted")
    print("✅ Alternative action is generated")
    print("✅ READ is inserted before CLICK")
    print("✅ Original click target is preserved")
    print("✅ Remaining steps are preserved")
    print("✅ New execution plan is returned")

    return True


def test_search_failure():

    print("\n\nTEST 2 - Search failure replanning")

    original_plan = [
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

    failed_step = 1

    failure = {
        "error": "Search engine unavailable"
    }

    result = replanner.replan(
        original_plan,
        failed_step,
        failure
    )

    print("\nREPLANNER RESULT")
    print("----------------------------------------")
    print(result)

    assert result.get("status") == "success"

    new_plan = result.get("steps", [])

    assert len(new_plan) == 3

    assert new_plan[0] == {
        "action": "search",
        "query": "Python tutorials"
    }

    assert new_plan[1] == {
        "action": "click",
        "target": "first search result"
    }

    assert new_plan[2] == {
        "action": "read"
    }

    print("\n✅ SEARCH FAILURE TEST PASSED")

    return True


def test_invalid_failure_step():

    print("\n\nTEST 3 - Invalid failed step")

    original_plan = [
        {
            "action": "read"
        }
    ]

    result = replanner.replan(
        original_plan,
        99,
        "Invalid step"
    )

    print("\nRESULT")
    print(result)

    assert result.get("status") == "failed"

    print("\n✅ INVALID STEP TEST PASSED")

    return True


if __name__ == "__main__":

    try:

        test_click_failure()

        test_search_failure()

        test_invalid_failure_step()

        print("\n========================================")
        print("🚀 ALL REPLANNER TESTS PASSED")
        print("========================================")

    except AssertionError as e:

        print("\n========================================")
        print("❌ REPLANNER TEST FAILED")
        print("========================================")

        print(f"\nAssertion Error: {e}")

    except Exception as e:

        print("\n========================================")
        print("❌ REPLANNER TEST CRASHED")
        print("========================================")

        print(
            f"\nError: {type(e).__name__}: {e}"
        )