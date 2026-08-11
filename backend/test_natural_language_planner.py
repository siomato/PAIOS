from app.core.agent_controller import agent_controller


print("\n" + "=" * 70)
print("🧠 PAIO — NATURAL LANGUAGE PLANNER TEST")
print("=" * 70)


# =========================================================
# USER REQUEST
# =========================================================

user_request = (
    "Search for Python tutorials and click "
    "THIS TARGET DOES NOT EXIST"
)


print("\n👤 USER REQUEST")
print(user_request)


# =========================================================
# CHECK CONTROLLER API
# =========================================================

print("\n" + "=" * 70)
print("🔍 CHECKING AGENT CONTROLLER")
print("=" * 70)


available_methods = [
    name
    for name in dir(agent_controller)
    if not name.startswith("_")
]


print("Available methods:")
print(available_methods)


# =========================================================
# GENERATE PLAN
# =========================================================

print("\n" + "=" * 70)
print("🧠 GENERATING PLAN")
print("=" * 70)


try:

    if hasattr(agent_controller, "plan"):

        plan = agent_controller.plan(
            user_request
        )

    elif hasattr(agent_controller, "create_plan"):

        plan = agent_controller.create_plan(
            user_request
        )

    elif hasattr(agent_controller, "generate_plan"):

        plan = agent_controller.generate_plan(
            user_request
        )

    else:

        raise AttributeError(
            "AgentController has no known "
            "planning method."
        )

except Exception as e:

    print("\n❌ PLANNER TEST CRASHED")
    print(f"Error: {e}")
    raise


# =========================================================
# DISPLAY PLAN
# =========================================================

print("\n" + "=" * 70)
print("📋 GENERATED PLAN")
print("=" * 70)


print(plan)


# =========================================================
# NORMALIZE PLAN
# =========================================================

if isinstance(plan, dict):

    steps = plan.get(
        "plan",
        plan.get(
            "steps",
            []
        )
    )

else:

    steps = plan


# =========================================================
# VALIDATION
# =========================================================

print("\n" + "=" * 70)
print("VALIDATION")
print("=" * 70)


if not isinstance(steps, list):

    print("❌ Plan is not a list.")
    raise SystemExit(1)


print(
    f"📊 Number of generated actions: "
    f"{len(steps)}"
)


# ---------------------------------------------------------
# ACTION TYPES
# ---------------------------------------------------------

action_types = [
    step.get("action")
    for step in steps
    if isinstance(step, dict)
]


print(
    f"🔧 Action types: "
    f"{action_types}"
)


# =========================================================
# SEARCH VALIDATION
# =========================================================

has_search = any(
    step.get("action") == "search"
    for step in steps
    if isinstance(step, dict)
)


if has_search:

    print("✅ SEARCH action generated.")

else:

    print("❌ SEARCH action missing.")


# =========================================================
# CLICK VALIDATION
# =========================================================

has_click = any(
    step.get("action") == "click"
    for step in steps
    if isinstance(step, dict)
)


if has_click:

    print("✅ CLICK action generated.")

else:

    print("❌ CLICK action missing.")


# =========================================================
# MULTI-ACTION VALIDATION
# =========================================================

if len(steps) >= 2:

    print("✅ Multiple actions generated.")

else:

    print(
        "❌ Planner generated only one action."
    )


# =========================================================
# FINAL VALIDATION
# =========================================================

if (
    has_search
    and has_click
    and len(steps) >= 2
):

    print("\n" + "=" * 70)
    print("🚀 NATURAL LANGUAGE PLANNER TEST PASSED")
    print("=" * 70)

else:

    print("\n" + "=" * 70)
    print("❌ NATURAL LANGUAGE PLANNER TEST FAILED")
    print("=" * 70)

    print("\nExpected structure:")

    print(
        """
[
    {
        "action": "search",
        "query": "Python tutorials"
    },
    {
        "action": "click",
        "target": "THIS TARGET DOES NOT EXIST"
    }
]
"""
    )

    raise SystemExit(1)