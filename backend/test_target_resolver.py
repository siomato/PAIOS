from app.tools.browser_automation import browser_automation
from backend.app.tools.target_resolver import target_resolver


print(
    "========== TARGET RESOLVER TEST =========="
)


# =================================================
# SEARCH
# =================================================

print(
    "\nSearching Python tutorials..."
)

result = browser_automation.search(
    "Python tutorials"
)

print(
    f"\nSearch result: {result}"
)


# =================================================
# RESOLVE
# =================================================

print(
    "\nResolving first search result..."
)

target = target_resolver.resolve(
    "first search result"
)


# =================================================
# DISPLAY
# =================================================

print(
    "\n========== RESOLVED TARGET =========="
)

print(target)


# =================================================
# VALIDATION
# =================================================

if target:

    print(
        "\n✅ TARGET RESOLVER TEST PASSED"
    )

    print(
        f"Target text: {target.get('text')}"
    )

    print(
        f"Target href: {target.get('href')}"
    )

else:

    print(
        "\n❌ TARGET RESOLVER TEST FAILED"
    )


# =================================================
# KEEP BROWSER OPEN
# =================================================

input(
    "\nPress ENTER to close browser..."
)

browser_automation.close()