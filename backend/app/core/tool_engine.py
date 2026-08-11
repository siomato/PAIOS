from app.tools.application_tools import application_tools


class ToolEngine:

    def __init__(self):

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

        self.open_keywords = (
            "open",
            "launch",
            "start",
            "run",
        )

    # =====================================================
    # CAN HANDLE
    # =====================================================

    def can_handle(self, user_message: str):

        if not isinstance(user_message, str):

            return False

        message = user_message.lower().strip()

        # Must contain an application command keyword
        if not any(
            keyword in message
            for keyword in self.open_keywords
        ):

            return False

        # Must contain a known application
        return any(
            alias in message
            for alias in self.application_aliases
        )

    # =====================================================
    # EXECUTE
    # =====================================================

    def execute(self, intent):

        print("\n========== TOOL ENGINE ==========")
        print(f"Received Intent: {intent}")

        # -------------------------------------------------
        # Validate intent
        # -------------------------------------------------

        if not isinstance(intent, dict):

            return "Invalid application intent."

        if intent.get("intent") != "OPEN_APPLICATION":

            return "Unsupported tool intent."

        target = intent.get("target")

        if not target:

            return "No application target provided."

        print(f"Target Application: {target}")

        # =================================================
        # APPLICATIONS
        # =================================================

        if target == "chrome":

            return application_tools.open_chrome()

        if target == "notepad":

            return application_tools.open_notepad()

        if target == "calculator":

            return application_tools.open_calculator()

        if target == "vscode":

            return application_tools.open_vscode()

        return f"Unknown application: {target}"


tool_engine = ToolEngine()