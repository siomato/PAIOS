from app.tools.browser_automation import browser_automation


print("========== BROWSER ACTION TEST ==========")


# 1. Open Google
print("\n1. Opening Google...")

print(
    browser_automation.open_url(
        "https://www.google.com"
    )
)


# 2. Fill search box
print("\n2. Filling search box...")

print(
    browser_automation.fill(
        'textarea[name="q"], input[name="q"]',
        "Python tutorials"
    )
)


# 3. Press Enter
print("\n3. Pressing Enter...")

print(
    browser_automation.press(
        'textarea[name="q"], input[name="q"]',
        "Enter"
    )
)


# 4. Read page
print("\n4. Reading page...")

page = browser_automation.read_page()

print("Title:", page.get("title"))
print("URL:", page.get("url"))

print("\nPage content preview:")
print(page.get("content", "")[:1000])


# 5. Keep browser open
input("\nPress ENTER to close the browser...")


# 6. Close browser
print(
    browser_automation.close()
)