# ============================================================
# app/core/action_executor.py
#
# PAIO ACTION EXECUTOR
#
# AgentState-aware execution
#
# Pipeline:
#
# Action Plan
#      ↓
# ActionExecutor
#      ↓
# AgentState updated
#      ↓
# Browser Tools
#      ↓
# Browser Telemetry
#      ↓
# Result
#      ↓
# AgentState observation
# ============================================================


from app.tools.browser_tools import browser_tools

import time


class ActionExecutor:

    # ========================================================
    # INITIALIZATION
    # ========================================================

    def __init__(self):

        print(
            "⚙️ ACTION EXECUTOR MODULE LOADED ⚙️"
        )

    # ========================================================
    # STATE HELPERS
    # ========================================================

    def _set_state(
        self,
        state,
        attribute,
        value
    ):
        """
        Safely update AgentState.

        Supports both:

            state.set_status(...)

        and:

            state.status = ...

        This keeps the executor compatible with
        the existing AgentState implementation.
        """

        if state is None:
            return

        # ----------------------------------------------------
        # Try dedicated setter first
        # ----------------------------------------------------

        try:

            setter = getattr(
                state,
                f"set_{attribute}",
                None
            )

            if callable(setter):

                setter(
                    value
                )

                return

        except Exception:

            pass

        # ----------------------------------------------------
        # Fallback to direct attribute
        # ----------------------------------------------------

        try:

            setattr(
                state,
                attribute,
                value
            )

        except Exception:

            pass

    # ========================================================
    # COMPLETED STEP
    # ========================================================

    def _increment_completed(
        self,
        state,
        step_number,
        action
    ):
        """
        Record a successfully completed action
        in AgentState.
        """

        if state is None:
            return

        # ----------------------------------------------------
        # Preferred AgentState API
        # ----------------------------------------------------

        try:

            state.mark_step_completed(
                step_number,
                action
            )

            return

        except Exception as e:

            print(
                f"⚠️ Could not record completed step "
                f"through AgentState: {e}"
            )

        # ----------------------------------------------------
        # Compatibility fallback
        # ----------------------------------------------------

        try:

            completed_steps = getattr(
                state,
                "completed_steps",
                None
            )

            if isinstance(
                completed_steps,
                list
            ):

                completed_steps.append({
                    "step": step_number,
                    "action": action
                })

        except Exception:

            pass

    # ========================================================
    # FAILED STEP
    # ========================================================

    def _record_failure(
        self,
        state,
        step_number,
        error
    ):
        """
        Record the failed step and error
        in AgentState.
        """

        if state is None:
            return

        # ----------------------------------------------------
        # Preferred AgentState API
        # ----------------------------------------------------

        try:

            state.mark_step_failed(
                step_number,
                error
            )

            return

        except Exception as e:

            print(
                f"⚠️ Could not record failed step "
                f"through AgentState: {e}"
            )

        # ----------------------------------------------------
        # Compatibility fallback
        # ----------------------------------------------------

        try:

            state.failed_step = step_number

            state.last_error = str(
                error
            )

        except Exception:

            pass

    # ========================================================
    # ACTION HISTORY
    # ========================================================

    def _record_action_history(
        self,
        state,
        action,
        result
    ):
        """
        Record every executed action into AgentState
        and TaskContext.
        """

        if state is None:
            return

        if not isinstance(result, dict):
            return

        action_record = {
            "action": action,
            "status": result.get("status"),
            "result": result,
            "error": result.get("error"),
            "step": getattr(
                state,
                "current_step",
                None
            )
        }

        # ----------------------------------------------------
        # AgentState V2
        # ----------------------------------------------------

        try:

            recorder = getattr(
                state,
                "record_action",
                None
            )

            if callable(recorder):

                recorder(
                    action=action,
                    result=result,
                    success=(
                        result.get("status")
                        == "success"
                    ),
                    error=result.get("error")
                )

                return

        except Exception as e:

            print(
                f"⚠️ Could not record action "
                f"through AgentState: {e}"
            )

        # ----------------------------------------------------
        # Compatibility fallback
        # ----------------------------------------------------

        try:

            history = getattr(
                state,
                "action_history",
                None
            )

            if isinstance(
                history,
                list
            ):

                history.append(
                    action_record
                )

        except Exception:

            pass

    # ========================================================
    # OBSERVATION
    # ========================================================

    def _record_observation(
        self,
        state,
        action,
        result
    ):
        """
        Store the result of an executed action
        as an AgentState observation.
        """

        if state is None:
            return

        if not isinstance(
            result,
            dict
        ):
            return

        observation = {
            "action": action,
            "status": result.get(
                "status"
            ),
            "message": result.get(
                "message"
            ),
            "data": result.get(
                "data"
            ),
            "error": result.get(
                "error"
            )
        }

        try:

            state.add_observation(
                observation
            )

        except Exception as e:

            print(
                f"⚠️ Could not record observation: {e}"
            )

    # ========================================================
    # BROWSER TELEMETRY
    # ========================================================

    def _update_browser_state(
        self,
        state
    ):
        """
        Capture the current browser URL and page title
        and store them in AgentState.

        The existing BrowserTools.read_page() already
        returns:

            {
                "title": ...,
                "url": ...,
                "content": ...
            }

        Therefore we use that existing API rather than
        introducing another browser abstraction.
        """

        if state is None:
            return

        try:

            telemetry = browser_tools.read_page()

            # ------------------------------------------------
            # Validate response
            # ------------------------------------------------

            if not isinstance(
                telemetry,
                dict
            ):

                print(
                    "⚠️ Browser telemetry returned "
                    "an unexpected response."
                )

                return

            # ------------------------------------------------
            # Extract URL
            # ------------------------------------------------

            current_url = (
                telemetry.get("url")
                or ""
            )

            # ------------------------------------------------
            # Extract page title
            # ------------------------------------------------

            page_title = (
                telemetry.get("title")
                or ""
            )

            # ------------------------------------------------
            # Update AgentState
            # ------------------------------------------------

            state.update_browser_state(
                current_url=current_url,
                page_title=page_title
            )

            print(
                f"🌐 State URL: {current_url}"
            )

            print(
                f"📄 State title: {page_title}"
            )

        except Exception as e:

            print(
                f"⚠️ Browser telemetry unavailable: {e}"
            )

    # ========================================================
    # CURRENT STEP
    # ========================================================

    def _set_current_step(
        self,
        state,
        step_number
    ):
        """
        Update the currently executing step.
        """

        if state is None:
            return

        # ----------------------------------------------------
        # Preferred AgentState API
        # ----------------------------------------------------

        try:

            state.set_current_step(
                step_number
            )

            return

        except Exception:

            pass

        # ----------------------------------------------------
        # Compatibility fallback
        # ----------------------------------------------------

        self._set_state(
            state,
            "current_step",
            step_number
        )

    # ========================================================
    # RESULT HELPERS
    # ========================================================

    def _success(
        self,
        action_type,
        data=None,
        message=""
    ):
        """
        Standard success response.
        """

        return {
            "status": "success",
            "action": action_type,
            "data": data,
            "message": message,
            "error": None,
            "recoverable": False
        }

    # ========================================================

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

    # ========================================================
    # EXECUTE ONE ACTION
    # ========================================================

    def execute_action(
        self,
        action,
        state=None
    ):
        """
        Execute one browser action.

        Supported actions:

            search
            click
            find
            read
            fill
            press
            open_url
        """

        # ====================================================
        # VALIDATE ACTION
        # ====================================================

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

        # ====================================================
        # UPDATE AGENT STATE
        # ====================================================

        if state is not None:

            self._set_state(
                state,
                "status",
                "executing"
            )

        print(
            "\n---------- ACTION ----------"
        )

        print(
            f"Action type: {action_type}"
        )

        # ====================================================
        # SEARCH
        # ====================================================

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

        # ====================================================
        # CLICK
        # ====================================================

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

                # ====================================================
        # FIND
        # ====================================================

        if action_type == "find":

            query = (
                action.get("query")
                or ""
            ).strip()

            if not query:

                return self._failure(
                    "find",
                    "Find query is empty.",
                    recoverable=False
                )

            print(
                f"🔎 Executing find: {query}"
            )

            try:

                start_time = time.time()

                # ------------------------------------------------
                # FIND uses BrowserTools.find().
                #
                # FIND is intentionally separate from CLICK:
                #
                #     find asyncio
                #
                # resolves the target without executing a click.
                #
                # The planner/executor contract is:
                #
                #     {"action": "find", "query": "..."}
                # ------------------------------------------------

                finder = getattr(
                    browser_tools,
                    "find",
                    None
                )

                if not callable(finder):

                    return self._failure(
                        "find",
                        "BrowserTools.find() is not available.",
                        recoverable=False
                    )

                result = finder(
                    query
                )

                duration = round(
                    time.time() - start_time,
                    3
                )

                return self._success(
                    "find",
                    data=result,
                    message=(
                        f"Find completed in "
                        f"{duration}s."
                    )
                )

            except Exception as e:

                return self._failure(
                    "find",
                    e,
                    recoverable=True
                )
        # ====================================================
        # READ PAGE
        # ====================================================

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

        # ====================================================
        # FILL
        # ====================================================

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

        # ====================================================
        # PRESS
        # ====================================================

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

        # ====================================================
        # OPEN URL
        # ====================================================

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

        # ====================================================
        # UNKNOWN ACTION
        # ====================================================

        return self._failure(
            action_type or "unknown",
            f"Unknown action: {action_type}",
            recoverable=False
        )

    # ========================================================
    # EXECUTE COMPLETE PLAN
    # ========================================================

    def execute(
        self,
        steps,
        state=None
    ):
        """
        Execute a complete plan sequentially.

        `state` is optional so existing callers remain
        compatible.

        Example:

            action_executor.execute(
                steps,
                state
            )
        """

        results = []

        # ----------------------------------------------------
        # Validate steps
        # ----------------------------------------------------

        if steps is None:

            steps = []

        if not isinstance(
            steps,
            list
        ):

            steps = list(
                steps
            )

        total_steps = len(
            steps
        )

        print(
            "\n========== ACTION EXECUTOR =========="
        )

        print(
            f"Total steps: {total_steps}"
        )

        # ====================================================
        # INITIAL STATE
        # ====================================================

        if state is not None:

            self._set_state(
                state,
                "status",
                "executing"
            )

            self._set_current_step(
                state,
                0
            )

        # ====================================================
        # EMPTY PLAN
        # ====================================================

        if total_steps == 0:

            if state is not None:

                self._set_state(
                    state,
                    "status",
                    "failed"
                )

                self._record_failure(
                    state,
                    0,
                    "No actions to execute."
                )

            return {
                "status": "failed",
                "steps": [],
                "failed_step": None,
                "error": "No actions to execute.",
                "recoverable": False
            }

        # ====================================================
        # EXECUTE SEQUENTIALLY
        # ====================================================

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

            # ------------------------------------------------
            # UPDATE CURRENT STEP
            # ------------------------------------------------

            self._set_current_step(
                state,
                index
            )

            # ------------------------------------------------
            # EXECUTE ACTION
            # ------------------------------------------------

            result = self.execute_action(
                action,
                state=state
            )

            # ------------------------------------------------
            # RECORD ACTION HISTORY
            # ------------------------------------------------

            self._record_action_history(
                state,
                action,
                result
            )

            # ------------------------------------------------
            # STORE EXECUTION RECORD
            # ------------------------------------------------

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

                # ------------------------------------------------
                # Record completed action
                # ------------------------------------------------

                self._increment_completed(
                    state,
                    index,
                    action
                )

                # ------------------------------------------------
                # Record action observation
                # ------------------------------------------------

                self._record_observation(
                    state,
                    action,
                    result
                )

                # ------------------------------------------------
                # Capture browser telemetry
                # ------------------------------------------------

                self._update_browser_state(
                    state
                )

                # ------------------------------------------------
                # Clear previous failure information
                # ------------------------------------------------

                if state is not None:

                    try:

                        state.failed_step = None
                        state.last_error = None

                    except Exception:

                        pass

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

            # ------------------------------------------------
            # Record failed step
            # ------------------------------------------------

            self._record_failure(
                state,
                index,
                result["error"]
            )

            # ------------------------------------------------
            # Record failure observation
            # ------------------------------------------------

            self._record_observation(
                state,
                action,
                result
            )

            # ------------------------------------------------
            # Capture browser state even after failure
            # ------------------------------------------------

            self._update_browser_state(
                state
            )

            # ------------------------------------------------
            # Update AgentState
            # ------------------------------------------------

            self._set_state(
                state,
                "status",
                "failed"
            )

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

        # ====================================================
        # ALL ACTIONS SUCCESSFUL
        # ====================================================

        self._set_state(
            state,
            "status",
            "completed"
        )

        self._set_state(
            state,
            "failed_step",
            None
        )

        self._set_state(
            state,
            "last_error",
            None
        )

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


# ============================================================
# GLOBAL INSTANCE
# ============================================================

action_executor = ActionExecutor()