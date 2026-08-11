from app.tools.browser_tools import browser_tools

print("\n" + "=" * 70)
print("🌐 OPEN URL TEST")
print("=" * 70)

url = "https://www.python.org"

print(f"\nOpening: {url}")

try:
    result = browser_tools.open_url(url)

    print("\nRESULT")
    print("-" * 70)
    print(result)

    if isinstance(result, dict):
        print("\nSTATUS:", result.get("status"))
        print("ERROR:", result.get("error"))
        print("MESSAGE:", result.get("message"))

    print("\n" + "=" * 70)
    print("✅ OPEN URL TEST FINISHED")
    print("=" * 70)

except Exception as e:

    print("\n" + "=" * 70)
    print("❌ OPEN URL TEST FAILED")
    print("=" * 70)

    print(f"\nException: {type(e).__name__}")
    print(f"Error: {e}")

    import traceback
    traceback.print_exc()