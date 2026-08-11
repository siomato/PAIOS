from app.tools.browser_automation import browser_automation


print("========== GENERIC SEARCH TEST ==========")


query = "Python tutorials"

print(
    f"\nSearching for: {query}"
)

try:

    result = browser_automation.search(
        query
    )

    print(
        "\n========== SEARCH RESULT =========="
    )

    print(result)

    print(
        "\nCurrent URL:"
    )

    print(
        browser_automation.get_current_url()
    )

    print(
        "\n✅ GENERIC SEARCH TEST PASSED"
    )

except Exception as e:

    print(
        "\n❌ GENERIC SEARCH TEST FAILED"
    )

    print(
        f"Error: {e}"
    )

finally:

    input(
        "\nPress ENTER to close browser..."
    )

    browser_automation.close()