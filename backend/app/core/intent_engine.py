class IntentEngine:

    def __init__(self):

        # -------------------------
        # Application Aliases
        # -------------------------

        self.application_aliases = {

            "chrome": "chrome",
            "google chrome": "chrome",

            "notepad": "notepad",
            "note pad": "notepad",

            "calculator": "calculator",
            "calc": "calculator",

            "vscode": "vscode",
            "vs code": "vscode",
            "visual studio code": "vscode",
        }

        # -------------------------
        # Application Open Keywords
        # -------------------------

        self.open_keywords = [
            "open",
            "launch",
            "start",
            "run",
        ]

        # -------------------------
        # Website Aliases
        # -------------------------

        self.website_aliases = {

            "youtube": "youtube",
            "github": "github",
            "chatgpt": "chatgpt",
            "linkedin": "linkedin",
            "gmail": "gmail",
        }

    # =====================================================
    # INTENT DETECTION
    # =====================================================

    def detect_intent(self, user_message: str):

        message = user_message.lower().strip()

        # =================================================
        # 1. WEB SEARCH
        # =================================================

        if message.startswith("search "):

            query = user_message[7:].strip()

            if query:

                return {
                    "intent": "WEB_SEARCH",
                    "target": query,
                }

        # =================================================
        # 2. OPEN WEBSITE
        # =================================================

        if any(
            keyword in message
            for keyword in self.website_aliases
        ):

            for alias, website in self.website_aliases.items():

                if alias in message:

                    return {
                        "intent": "OPEN_WEBSITE",
                        "target": website,
                    }

        # =================================================
        # 3. OPEN APPLICATION
        # =================================================

        if any(
            keyword in message
            for keyword in self.open_keywords
        ):

            for alias, application in self.application_aliases.items():

                if alias in message:

                    return {
                        "intent": "OPEN_APPLICATION",
                        "target": application,
                    }

        # =================================================
        # 4. CLICK
        # =================================================

        if message.startswith("click "):

            target = user_message[6:].strip()

            return {
                "intent": "BROWSER_CLICK",
                "target": target,
            }

        # =================================================
        # 5. FILL
        # =================================================

        if message.startswith("fill "):

            target = user_message[5:].strip()

            return {
                "intent": "BROWSER_FILL",
                "target": target,
            }

        # =================================================
        # 6. PRESS
        # =================================================

        if message.startswith("press "):

            key = user_message[6:].strip()

            return {
                "intent": "BROWSER_PRESS",
                "target": key,
            }

        # =================================================
        # 7. READ PAGE
        # =================================================

        if (
            message == "read page"
            or message == "read this page"
            or message == "read webpage"
            or message == "read website"
        ):

            return {
                "intent": "READ_PAGE",
                "target": None,
            }

        # =================================================
        # 8. CHAT
        # =================================================

        return {
            "intent": "CHAT",
            "target": None,
        }


intent_engine = IntentEngine()