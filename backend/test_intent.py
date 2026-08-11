from app.core.intent_engine import intent_engine


tests = [

    # Applications
    "Open Chrome",
    "Launch VS Code",
    "Start Calculator",
    "Run Notepad",

    # Websites
    "Open YouTube",
    "Open GitHub",
    "Open ChatGPT",
    "Open LinkedIn",
    "Open Gmail",

    # Search
    "Search Python tutorials",
    "Search artificial intelligence news",

    # Browser actions
    "Click first result",
    "Fill search box",
    "Press Enter",
    "Read page",

    # Chat
    "Hello",
    "How are you?",
]


for test in tests:

    print("=" * 60)

    print(f"Input : {test}")

    result = intent_engine.detect_intent(test)

    print(f"Output: {result}")