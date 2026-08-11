from app.core.action_planner import action_planner


print("========== ACTION PLANNER TEST ==========")


command = (
    "Search Python tutorials "
    "then click first search result "
    "then read page"
)


print("\nInput:")
print(command)


steps = action_planner.plan(command)


print("\nPlanned Steps:")

for index, step in enumerate(steps, start=1):

    print(
        f"{index}. {step}"
    )