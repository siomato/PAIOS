from app.core.agent_controller import agent_controller


print(
    "\n"
    "=========================================="
)

print(
    "       PAIO AGENT CONTROLLER TEST"
)

print(
    "=========================================="
)


# =========================================================
# TEST COMMAND
# =========================================================

user_message = (
    "Search Python tutorials "
    "then click first search result "
    "then read page"
)


print(
    "\nUser command:"
)

print(
    user_message
)


# =========================================================
# RUN AGENT
# =========================================================

result = agent_controller.run(
    user_message
)


# =========================================================
# DISPLAY RESULT
# =========================================================

print(
    "\n"
    "=========================================="
)

print(
    "              TEST RESULT"
)

print(
    "=========================================="
)

print(
    result
)


# =========================================================
# TEST STATUS
# =========================================================

if result.get(
    "status"
) == "success":

    print(
        "\n✅ AGENT CONTROLLER TEST PASSED"
    )

else:

    print(
        "\n❌ AGENT CONTROLLER TEST FAILED"
    )