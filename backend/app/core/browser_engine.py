from app.tools.browser_tools import browser_tools
from app.core.action_planner import action_planner


print("🔥 BROWSER ENGINE MODULE LOADED 🔥")


class BrowserEngine:

    # =====================================================
    # CAN HANDLE
    # =====================================================

    def can_handle(
        self,
        user_message: str
    ):

        message = (
            user_message
            .lower()
            .strip()
        )

        browser_keywords = (
            "search",
            "google",
            "youtube",
            "chatgpt",
            "github",
            "linkedin",
            "gmail",
            "website",
            "open",
            "click",
            "fill",
            "press",
            "read page",
        )

        return any(
            keyword in message
            for keyword in browser_keywords
        )

    # =====================================================
    # PARSE STEPS
    # =====================================================

    def _parse_steps(
        self,
        user_message: str
    ):

        """
        Use the centralized ActionPlanner.

        Example:

        Search Python tutorials then click first search result then read page

        becomes:

        [
            {
                "action": "search",
                "query": "Python tutorials"
            },
            {
                "action": "click",
                "target": "first search result"
            },
            {
                "action": "read"
            }
        ]
        """

        return action_planner.plan(
            user_message
        )

    # =====================================================
    # EXECUTE SINGLE STEP
    # =====================================================

    def _execute_single_step(
        self,
        step
    ):

        # -------------------------------------------------
        # Validate planned step
        # -------------------------------------------------

        if not isinstance(
            step,
            dict
        ):

            raise RuntimeError(
                f"Invalid planned step: {step}"
            )

        action = step.get(
            "action"
        )

        print(
            f"\nExecuting action: {action}"
        )

        # =================================================
        # SEARCH
        # =================================================

        if action == "search":

            query = step.get(
                "query",
                ""
            )

            query = query.strip()

            if not query:

                raise ValueError(
                    "Search query cannot be empty."
                )

            print(
                f"🔎 Searching: {query}"
            )

            return browser_tools.search(
                query
            )

        # =================================================
        # CLICK
        # =================================================

        if action == "click":

            target = step.get(
                "target",
                ""
            )

            target = target.strip()

            if not target:

                raise ValueError(
                    "Click target cannot be empty."
                )

            print(
                f"🖱️ Clicking: {target}"
            )

            return browser_tools.click(
                target
            )

        # =================================================
        # FILL
        # =================================================

        if action == "fill":

            command = step.get(
                "command",
                ""
            )

            command = command.strip()

            if not command:

                raise ValueError(
                    "Fill command cannot be empty."
                )

            print(
                f"⌨️ Fill request: {command}"
            )

            return browser_tools.fill_from_command(
                command
            )

        # =================================================
        # PRESS
        # =================================================

        if action == "press":

            key = step.get(
                "key",
                ""
            )

            key = key.strip()

            if not key:

                raise ValueError(
                    "Key cannot be empty."
                )

            print(
                f"⌨️ Pressing: {key}"
            )

            return browser_tools.press_key(
                key
            )

        # =================================================
        # READ PAGE
        # =================================================

        if action == "read":

            print(
                "📖 Reading current page..."
            )

            return browser_tools.read_page()

        # =================================================
        # OPEN URL
        # =================================================

        if action == "open_url":

            url = step.get(
                "url",
                ""
            )

            url = url.strip()

            if not url:

                raise ValueError(
                    "URL cannot be empty."
                )

            print(
                f"🌐 Opening: {url}"
            )

            return browser_tools.open_url(
                url
            )

        # =================================================
        # UNKNOWN
        # =================================================

        if action == "unknown":

            command = step.get(
                "command",
                ""
            )

            raise RuntimeError(
                f"Unknown browser command: {command}"
            )

        # =================================================
        # INVALID ACTION
        # =================================================

        raise RuntimeError(
            f"Unsupported browser action: {action}"
        )

    # =====================================================
    # EXECUTE
    # =====================================================

    def execute(
        self,
        user_message: str
    ):

        print(
            "\n========== BROWSER ENGINE =========="
        )

        print(
            f"Received Message: {user_message}"
        )

        # =================================================
        # CREATE PLAN
        # =================================================

        steps = self._parse_steps(
            user_message
        )

        print(
            f"\n📋 Parsed {len(steps)} step(s):"
        )

        for index, step in enumerate(
            steps,
            start=1
        ):

            print(
                f"{index}. {step}"
            )

        # =================================================
        # EMPTY PLAN
        # =================================================

        if not steps:

            print(
                "❌ No executable browser actions found."
            )

            return {
                "status": "failed",
                "steps": [],
                "error": (
                    "No executable browser "
                    "actions found."
                )
            }

        # =================================================
        # EXECUTE SEQUENTIALLY
        # =================================================

        results = []

        for index, step in enumerate(
            steps,
            start=1
        ):

            print(
                f"\n========== STEP "
                f"{index}/{len(steps)} =========="
            )

            try:

                result = (
                    self._execute_single_step(
                        step
                    )
                )

                results.append({
                    "step": index,
                    "action": step,
                    "status": "success",
                    "result": result,
                })

                print(
                    f"✅ Step {index} completed."
                )

            except Exception as e:

                print(
                    f"❌ Step {index} failed: {e}"
                )

                results.append({
                    "step": index,
                    "action": step,
                    "status": "failed",
                    "error": str(e),
                })

                # -----------------------------------------
                # STOP ON FAILURE
                # -----------------------------------------

                print(
                    f"🛑 Execution stopped "
                    f"at step {index}."
                )

                break

        # =================================================
        # FINAL STATUS
        # =================================================

        successful = (
            len(results) == len(steps)
            and all(
                result["status"] == "success"
                for result in results
            )
        )

        final_result = {
            "status": (
                "success"
                if successful
                else "failed"
            ),
            "steps": results,
        }

        # =================================================
        # FINAL OUTPUT
        # =================================================

        print(
            "\n========== FINAL RESULT =========="
        )

        print(
            final_result
        )

        return final_result


# =========================================================
# GLOBAL INSTANCE
# =========================================================

browser_engine = BrowserEngine()