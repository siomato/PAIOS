from app.tools.browser_tools import browser_tools
import time


class ActionExecutor:

    # =========================================================
    # RESULT HELPERS
    # =========================================================

    def _success(
        self,
        action_type,
        data=None,
        message=""
    ):
        """
        Standard success response.

        Every successful action returns the same structure.
        """

        return {
            "status": "success",
            "action": action_type,
            "data": data,
            "message": message,
            "error": None,
            "recoverable": False
        }

    # ---------------------------------------------------------

    def _failure(
        self,
        action_type,
        error,
        recoverable=True
    ):
        """
        Standard failure response.
        """

        return {
            "status": "failed",
            "action": action_type,
            "data": None,
            "message": "",
            "error": str(error),
            "recoverable": recoverable
        }

    # =========================================================
    # EXECUTE ONE ACTION
    # =========================================================

    def execute_action(
        self,
        action
    ):

        if not isinstance(
            action,
            dict
        ):

            return self._failure(
                "unknown",
                "Action must be a dictionary.",
                recoverable=False
            )

        action_type = (
            action.get("action")
            or ""
        ).strip().lower()

        print(
            "\n---------- ACTION ----------"
        )

        print(
            f"Action type: {action_type}"
        )

        # =====================================================
        # SEARCH
        # =====================================================

        if action_type == "search":

            query = (
                action.get("query")
                or ""
            ).strip()

            if not query:

                return self._failure(
                    "search",
                    "Search query is empty.",
                    recoverable=False
                )

            print(
                f"🔎 Executing search: {query}"
            )

            try:

                start_time = time.time()

                result = browser_tools.search(
                    query
                )

                duration = round(
                    time.time() - start_time,
                    3
                )

                return self._success(
                    "search",
                    data=result,
                    message=(
                        f"Search completed in "
                        f"{duration}s."
                    )
                )

            except Exception as e:

                return self._failure(
                    "search",
                    e,
                    recoverable=True
                )

        # =====================================================
        # CLICK
        # =====================================================

        if action_type == "click":

            target = (
                action.get("target")
                or ""
            ).strip()

            if not target:

                return self._failure(
                    "click",
                    "Click target is empty.",
                    recoverable=False
                )

            print(
                f"🖱️ Executing click: {target}"
            )

            try:

                start_time = time.time()

                result = browser_tools.click(
                    target
                )

                duration = round(
                    time.time() - start_time,
                    3
                )

                return self._success(
                    "click",
                    data=result,
                    message=(
                        f"Click completed in "
                        f"{duration}s."
                    )
                )

            except Exception as e:

                return self._failure(
                    "click",
                    e,
                    recoverable=True
                )

        # =====================================================
        # READ PAGE
        # =====================================================

        if action_type == "read":

            print(
                "📖 Executing read page..."
            )

            try:

                start_time = time.time()

                result = browser_tools.read_page()

                duration = round(
                    time.time() - start_time,
                    3
                )

                return self._success(
                    "read",
                    data=result,
                    message=(
                        f"Page read completed in "
                        f"{duration}s."
                    )
                )

            except Exception as e:

                return self._failure(
                    "read",
                    e,
                    recoverable=True
                )

        # =====================================================
        # FILL
        # =====================================================

        if action_type == "fill":

            command = (
                action.get("command")
                or ""
            ).strip()

            if not command:

                return self._failure(
                    "fill",
                    "Fill command is empty.",
                    recoverable=False
                )

            print(
                f"⌨️ Executing fill: {command}"
            )

            try:

                start_time = time.time()

                result = browser_tools.fill_from_command(
                    command
                )

                duration = round(
                    time.time() - start_time,
                    3
                )

                return self._success(
                    "fill",
                    data=result,
                    message=(
                        f"Fill completed in "
                        f"{duration}s."
                    )
                )

            except Exception as e:

                return self._failure(
                    "fill",
                    e,
                    recoverable=True
                )

        # =====================================================
        # PRESS
        # =====================================================

        if action_type == "press":

            key = (
                action.get("key")
                or ""
            ).strip()

            if not key:

                return self._failure(
                    "press",
                    "Press key is empty.",
                    recoverable=False
                )

            print(
                f"⌨️ Executing press: {key}"
            )

            try:

                start_time = time.time()

                result = browser_tools.press_key(
                    key
                )

                duration = round(
                    time.time() - start_time,
                    3
                )

                return self._success(
                    "press",
                    data=result,
                    message=(
                        f"Key press completed in "
                        f"{duration}s."
                    )
                )

            except Exception as e:

                return self._failure(
                    "press",
                    e,
                    recoverable=True
                )

        # =====================================================
        # OPEN URL
        # =====================================================

        if action_type == "open_url":

            url = (
                action.get("url")
                or ""
            ).strip()

            if not url:

                return self._failure(
                    "open_url",
                    "URL is empty.",
                    recoverable=False
                )

            print(
                f"🌐 Executing open_url: {url}"
            )

            try:

                start_time = time.time()

                result = browser_tools.open_url(
                    url
                )

                duration = round(
                    time.time() - start_time,
                    3
                )

                return self._success(
                    "open_url",
                    data=result,
                    message=(
                        f"URL opened in "
                        f"{duration}s."
                    )
                )

            except Exception as e:

                return self._failure(
                    "open_url",
                    e,
                    recoverable=True
                )

        # =====================================================
        # UNKNOWN ACTION
        # =====================================================

        return self._failure(
            action_type or "unknown",
            f"Unknown action: {action_type}",
            recoverable=False
        )

    # =========================================================
    # EXECUTE COMPLETE PLAN
    # =========================================================

    def execute(
        self,
        steps
    ):

        results = []

        total_steps = len(
            steps
        )

        print(
            "\n========== ACTION EXECUTOR =========="
        )

        print(
            f"Total steps: {total_steps}"
        )

        # =====================================================
        # EMPTY PLAN
        # =====================================================

        if total_steps == 0:

            return {
                "status": "failed",
                "steps": [],
                "failed_step": None,
                "error": "No actions to execute."
            }

        # =====================================================
        # EXECUTE SEQUENTIALLY
        # =====================================================

        for index, action in enumerate(
            steps,
            start=1
        ):

            print(
                f"\n========== "
                f"STEP {index}/{total_steps} "
                f"=========="
            )

            print(
                f"Action: {action}"
            )

            # -------------------------------------------------
            # Execute action
            # -------------------------------------------------

            result = self.execute_action(
                action
            )

            # -------------------------------------------------
            # Store execution record
            # -------------------------------------------------

            execution_record = {
                "step": index,
                "action": action,
                "status": result["status"],
                "result": result
            }

            results.append(
                execution_record
            )

            # =================================================
            # SUCCESS
            # =================================================

            if result["status"] == "success":

                print(
                    f"✅ Step {index} completed."
                )

                continue

            # =================================================
            # FAILURE
            # =================================================

            print(
                f"❌ Step {index} failed."
            )

            print(
                f"Reason: {result['error']}"
            )

            print(
                f"Recoverable: "
                f"{result['recoverable']}"
            )

            # -------------------------------------------------
            # STOP ON FAILURE
            #
            # Recovery layer will use this information later.
            # -------------------------------------------------

            print(
                "\n🛑 Execution stopped "
                f"at step {index}."
            )

            return {
                "status": "failed",
                "steps": results,
                "failed_step": index,
                "error": result["error"],
                "recoverable": result["recoverable"]
            }

        # =====================================================
        # ALL ACTIONS SUCCESSFUL
        # =====================================================

        print(
            "\n🎉 All actions completed successfully."
        )

        return {
            "status": "success",
            "steps": results,
            "failed_step": None,
            "error": None,
            "recoverable": False
        }


# =============================================================
# GLOBAL INSTANCE
# =============================================================

action_executor = ActionExecutor()