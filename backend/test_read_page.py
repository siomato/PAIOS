from app.tools.browser_automation import browser_automation


print("========== READ PAGE TEST ==========")

# -------------------------------------------------
# Open a real webpage
# -------------------------------------------------

print("\nOpening W3Schools...")

result = browser_automation.open_url(
    "https://www.w3schools.com/python/"
)

print(result)


# -------------------------------------------------
# Read current webpage
# -------------------------------------------------

print("\nReading current page...")

page_data = browser_automation.read_page()


# -------------------------------------------------
# Display result
# -------------------------------------------------

print("\n========== PAGE DATA ==========")

if "error" in page_data:

    print(page_data["error"])

else:

    print(f"\nTitle:\n{page_data['title']}")

    print(f"\nURL:\n{page_data['url']}")

    print("\nContent:\n")

    print(page_data["content"][:5000])


# -------------------------------------------------
# Keep browser open
# -------------------------------------------------

input(
    "\nPress ENTER to close browser..."
)

browser_automation.close()