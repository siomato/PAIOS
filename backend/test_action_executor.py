from app.core.action_planner import action_planner
from app.core.action_executor import action_executor


print(
    "========== ACTION EXECUTOR TEST =========="
)


command = (
    "Search Python tutorials "
    "then click first search result "
    "then read page"
)


print("\nUser Command:")
print(command)


# =====================================================
# PLAN
# =====================================================

steps = action_planner.plan(
    command
)


print("\nGenerated Plan:")

for index, step in enumerate(
    steps,
    start=1
):

    print(
        f"{index}. {step}"
    )


# =====================================================
# EXECUTE
# =====================================================

result = action_executor.execute(
    steps
)


# =====================================================
# FINAL RESULT
# =====================================================

print(
    "\n========== FINAL RESULT =========="
)

print(result)