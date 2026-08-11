from app.tools.browser_automation import browser_automation
from app.tools.target_resolver import target_resolver


print(
    "========== CLICK RESOLVED TARGET TEST =========="
)


# =================================================
# STEP 1 — SEARCH
# =================================================

print(
    "\nSTEP 1 — Searching..."
)

search_result = browser_automation.search(
    "Python tutorials"
)

print(
    f"Search result: {search_result}"
)


# =================================================
# STEP 2 — RESOLVE
# =================================================

print(
    "\nSTEP 2 — Resolving first search result..."
)

target = target_resolver.resolve(
    "first search result"
)

print(
    "\nResolved Target:"
)

print(target)


if not target:

    print(
        "\n❌ TEST FAILED — Target not resolved."
    )

    browser_automation.close()

    raise SystemExit(1)


# =================================================
# STEP 3 — CLICK / NAVIGATE
# =================================================

print(
    "\nSTEP 3 — Opening resolved target..."
)

href = target.get("href")

text = target.get(
    "text",
    ""
)

print(
    f"Target text: {text}"
)

print(
    f"Target href: {href}"
)


if not href:

    print(
        "\n❌ TEST FAILED — Target has no href."
    )

    browser_automation.close()

    raise SystemExit(1)


result = browser_automation.open_url(
    href
)

print(
    "\nNavigation result:"
)

print(result)


# =================================================
# STEP 4 — VERIFY
# =================================================

current_url = (
    browser_automation.get_current_url()
)

print(
    "\nCurrent Browser URL:"
)

print(current_url)


# =================================================
# VALIDATION
# =================================================

if (
    current_url
    and current_url != "No active browser session."
    and current_url.startswith("http")
):

    print(
        "\n✅ CLICK RESOLVED TARGET TEST PASSED"
    )

else:

    print(
        "\n❌ CLICK RESOLVED TARGET TEST FAILED"
    )


# =================================================
# KEEP BROWSER OPEN
# =================================================

input(
    "\nPress ENTER to close browser..."
)

browser_automation.close()