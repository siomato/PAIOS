from app.tools.browser_automation import browser_automation
from app.tools.page_analyzer import page_analyzer


print("========== PAGE ANALYZER TEST ==========")


# Open Google
print("\nOpening Google...")

print(
    browser_automation.open_url(
        "https://www.google.com"
    )
)


# Search
print("\nSearching Python tutorials...")

print(
    browser_automation.google_search(
        "Python tutorials"
    )
)


# Analyze page
print("\nAnalyzing page...")

elements = page_analyzer.print_elements()

print(
    f"\nTotal elements found: {len(elements)}"
)


input(
    "\nPress ENTER to close browser..."
)


browser_automation.close()