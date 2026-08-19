# ============================================================
# app/core/agent_controller.py
#
# PAIOS AGENT CONTROLLER
#
# Reliable autonomous controller with event callbacks
#
# Pipeline:
#
# User Request
#      ↓
# AgentState
#      ↓
# Action Planner
#      ↓
# Plan Validation
#      ↓
# Execute ONE action
#      ↓
# Browser Telemetry
#      ↓
# AgentState Update
#      ↓
# AgentEvaluator
#      ↓
# CONTINUE / COMPLETE / FAILED
#
# Event pipeline:
#
# AgentController
#      ↓
# event_callback(...)
#      ↓
# Future FastAPI SSE / WebSocket layer
#      ↓
# PAIOS Frontend
#
# ============================================================


from app.core.action_planner import action_planner
from app.core.recovery_engine import recovery_engine
from app.core.agent_state import AgentState
from app.core.agent_evaluator import agent_evaluator
from app.tools.browser_tools import browser_tools
from app.memory.knowledge_manager import KnowledgeManager


class AgentController:

    # ========================================================
    # INITIALIZATION
    # ========================================================

    def __init__(self):

        self.knowledge = KnowledgeManager()

        print(
            "🤖 AGENT CONTROLLER MODULE LOADED 🤖"
        )

    # ========================================================
    # EVENT EMITTER
    # ========================================================

    def _emit_event(
        self,
        event_callback,
        stage,
        message,
        data=None
    ):

        """
        Send an autonomous execution event.

        This method is intentionally isolated from the
        execution logic so event/streaming failures can
        never break the actual agent.

        Parameters:
            event_callback:
                Callable receiving one event dictionary.

            stage:
                plan / validate / execute / observe /
                evaluate / continue / complete / failed

            message:
                Human-readable event message.

            data:
                Optional structured event data.
        """

        event = {

            "stage": stage,

            "message": message,

            "data": (
                data
                if isinstance(data, dict)
                else {}
            )

        }

        print(
            f"📡 EVENT [{stage.upper()}] "
            f"{message}"
        )

        if not callable(
            event_callback
        ):

            return

        try:

            event_callback(
                event
            )

        except Exception as e:

            # ------------------------------------------------
            # IMPORTANT:
            #
            # A frontend/streaming failure must NEVER
            # terminate the autonomous agent.
            # ------------------------------------------------

            print(
                "⚠️ Event callback failed: "
                f"{e}"
            )

    # ========================================================
    # PLAN TASK
    # ========================================================

    def create_plan(
        self,
        user_message: str
    ):

        print(
            "\n========== PLANNING =========="
        )

        print(
            f"User message: {user_message}"
        )

        if (
            not user_message
            or not user_message.strip()
        ):

            return {

                "status": "failed",

                "error": (
                    "User message is empty."
                ),

                "steps": []

            }

        try:

            steps = action_planner.plan(
                user_message
            )

        except Exception as e:

            print(
                f"❌ Planning failed: {e}"
            )

            return {

                "status": "failed",

                "error": str(e),

                "steps": []

            }

        if not isinstance(
            steps,
            list
        ):

            return {

                "status": "failed",

                "error": (
                    "Planner returned "
                    "invalid plan."
                ),

                "steps": []

            }

        if not steps:

            return {

                "status": "failed",

                "error": (
                    "Planner produced "
                    "no actions."
                ),

                "steps": []

            }

        print(
            f"\n📋 Generated "
            f"{len(steps)} action(s):"
        )

        for index, step in enumerate(
            steps,
            start=1
        ):

            print(
                f"  {index}. {step}"
            )

        return {

            "status": "success",

            "steps": steps,

            "error": None

        }

    # ========================================================
    # VALIDATE PLAN
    # ========================================================

    def validate_plan(
        self,
        steps
    ):

        if not isinstance(
            steps,
            list
        ):

            return False

        if len(steps) == 0:

            return False

        for step in steps:

            if not isinstance(
                step,
                dict
            ):

                return False

            if not step.get(
                "action"
            ):

                return False

        return True

    # ========================================================
    # EXECUTE ONE ACTION
    # ========================================================

    def execute_action(
        self,
        action
    ):

        print(
            "\n========== ACTION EXECUTION =========="
        )

        print(
            f"Action: {action}"
        )

        try:

            result = recovery_engine.execute(
                [action]
            )

        except Exception as e:

            print(
                f"❌ Action execution error: {e}"
            )

            return {

                "status": "failed",

                "steps": [],

                "failed_step": None,

                "error": str(e),

                "replans_used": 0,

                "replan_history": []

            }

        if not isinstance(
            result,
            dict
        ):

            return {

                "status": "failed",

                "steps": [],

                "failed_step": None,

                "error": (
                    "RecoveryEngine returned "
                    "an invalid result."
                ),

                "replans_used": 0,

                "replan_history": []

            }

        return result

    # ========================================================
    # EXTRACT TELEMETRY FROM RESULT
    # ========================================================

    def _extract_result_telemetry(
        self,
        result
    ):

        current_url = None

        page_title = None

        if not isinstance(
            result,
            dict
        ):

            return (
                current_url,
                page_title
            )

        candidates = []

        # ----------------------------------------------------
        # Main result
        # ----------------------------------------------------

        candidates.append(
            result
        )

        # ----------------------------------------------------
        # Direct data
        # ----------------------------------------------------

        data = result.get(
            "data"
        )

        if isinstance(
            data,
            dict
        ):

            candidates.append(
                data
            )

        # ----------------------------------------------------
        # Nested steps
        # ----------------------------------------------------

        steps = result.get(
            "steps"
        )

        if isinstance(
            steps,
            list
        ):

            for step in steps:

                if not isinstance(
                    step,
                    dict
                ):

                    continue

                nested_result = step.get(
                    "result"
                )

                if isinstance(
                    nested_result,
                    dict
                ):

                    candidates.append(
                        nested_result
                    )

                    nested_data = (
                        nested_result.get(
                            "data"
                        )
                    )

                    if isinstance(
                        nested_data,
                        dict
                    ):

                        candidates.append(
                            nested_data
                        )

        # ----------------------------------------------------
        # Search candidates
        # ----------------------------------------------------

        for item in candidates:

            if not isinstance(
                item,
                dict
            ):

                continue

            if not current_url:

                current_url = (
                    item.get(
                        "current_url"
                    )
                    or
                    item.get(
                        "url"
                    )
                )

            if not page_title:

                page_title = (
                    item.get(
                        "page_title"
                    )
                    or
                    item.get(
                        "title"
                    )
                )

            if (
                current_url
                and
                page_title
            ):

                break

        return (
            current_url,
            page_title
        )

    # ========================================================
    # READ LIVE BROWSER TELEMETRY
    # ========================================================

    def _get_live_browser_telemetry(
        self
    ):

        current_url = None

        page_title = None

        # ====================================================
        # METHOD 1 — get_current_url()
        # ====================================================

        try:

            getter = getattr(
                browser_tools,
                "get_current_url",
                None
            )

            if callable(
                getter
            ):

                url = getter()

                if (
                    isinstance(
                        url,
                        str
                    )
                    and
                    url.strip()
                    and
                    url.strip()
                    != "No active browser session."
                ):

                    current_url = (
                        url.strip()
                    )

                    print(
                        f"🌐 Browser URL detected: "
                        f"{current_url}"
                    )

        except Exception as e:

            print(
                "⚠️ get_current_url() failed: "
                f"{e}"
            )

        # ====================================================
        # METHOD 2 — get_page()
        # ====================================================

        try:

            get_page = getattr(
                browser_tools,
                "get_page",
                None
            )

            page = None

            if callable(
                get_page
            ):

                page = get_page()

            else:

                page = getattr(
                    browser_tools,
                    "page",
                    None
                )

            if page is not None:

                # ------------------------------------------------
                # browser_tools.get_page() returns browser STATE,
                # not a Playwright Page object.
                #
                # Current format:
                #
                # {
                #     "current_url": "...",
                #     "page_title": "..."
                # }
                #
                # Never call page.title() when page is a dict.
                # ------------------------------------------------

                if isinstance(
                    page,
                    dict
                ):

                    if not current_url:

                        url = (
                            page.get(
                                "current_url"
                            )
                            or
                            page.get(
                                "url"
                            )
                        )

                        if (
                            isinstance(
                                url,
                                str
                            )
                            and
                            url.strip()
                        ):

                            current_url = (
                                url.strip()
                            )

                    title = (
                        page.get(
                            "page_title"
                        )
                        or
                        page.get(
                            "title"
                        )
                    )

                    if (
                        isinstance(
                            title,
                            str
                        )
                        and
                        title.strip()
                    ):

                        page_title = (
                            title.strip()
                        )

                else:

                    # ------------------------------------------------
                    # Backward-compatible support for a real
                    # Playwright-like Page object.
                    # ------------------------------------------------

                    if not current_url:

                        try:

                            url = page.url

                            if (
                                isinstance(
                                    url,
                                    str
                                )
                                and
                                url.strip()
                            ):

                                current_url = (
                                    url.strip()
                                )

                        except Exception as e:

                            print(
                                "⚠️ Could not read "
                                f"page.url: {e}"
                            )

                    if not page_title:

                        try:

                            title = page.title()

                            if (
                                isinstance(
                                    title,
                                    str
                                )
                                and
                                title.strip()
                            ):

                                page_title = (
                                    title.strip()
                                )

                        except Exception as e:

                            print(
                                "⚠️ Could not read "
                                f"page.title(): {e}"
                            )

        except Exception as e:

            print(
                "⚠️ Live browser telemetry "
                f"failed: {e}"
            )

        return (
            current_url,
            page_title
        )

    # ========================================================
    # UPDATE AGENT STATE TELEMETRY
    # ========================================================

    def _update_browser_state(
        self,
        state,
        result=None
    ):

        if state is None:

            return {

                "current_url": None,

                "page_title": None

            }

        # ====================================================
        # STEP 1 — RESULT TELEMETRY
        # ====================================================

        (
            current_url,
            page_title
        ) = self._extract_result_telemetry(
            result
        )

        # ====================================================
        # STEP 2 — LIVE BROWSER TELEMETRY
        # ====================================================

        (
            live_url,
            live_title
        ) = self._get_live_browser_telemetry()

        # ----------------------------------------------------
        # Prefer live browser state
        # ----------------------------------------------------

        if live_url:

            current_url = live_url

        if live_title:

            page_title = live_title

        # ====================================================
        # STEP 3 — SAVE TO AGENT STATE
        # ====================================================

        telemetry = {

            "current_url":
                current_url,

            "page_title":
                page_title

        }

        print(
            "\n========== BROWSER TELEMETRY =========="
        )

        print(
            f"URL   : {current_url}"
        )

        print(
            f"TITLE : {page_title}"
        )

        # ====================================================
        # Write directly to AgentState
        # ====================================================

        try:

            state.current_url = (
                current_url
            )

        except Exception as e:

            print(
                f"⚠️ Could not set "
                f"state.current_url: {e}"
            )

        try:

            state.page_title = (
                page_title
            )

        except Exception as e:

            print(
                f"⚠️ Could not set "
                f"state.page_title: {e}"
            )

        # ====================================================
        # ALSO STORE browser_state
        # ====================================================

        try:

            state.browser_state = (
                telemetry.copy()
            )

        except Exception as e:

            print(
                f"⚠️ Could not set "
                f"state.browser_state: {e}"
            )

        # ====================================================
        # USE AgentState METHOD IF AVAILABLE
        # ====================================================

        try:

            updater = getattr(
                state,
                "update_browser_state",
                None
            )

            if callable(
                updater
            ):

                updater(
                    current_url=current_url,
                    page_title=page_title
                )

        except Exception as e:

            print(
                "⚠️ AgentState "
                f"update_browser_state() failed: {e}"
            )

        # ====================================================
        # FINAL VERIFICATION
        # ====================================================

        try:

            print(
                "\n🔍 STATE TELEMETRY VERIFICATION"
            )

            print(
                f"state.current_url : "
                f"{getattr(state, 'current_url', None)}"
            )

            print(
                f"state.page_title  : "
                f"{getattr(state, 'page_title', None)}"
            )

            print(
                f"state.browser_state : "
                f"{getattr(state, 'browser_state', None)}"
            )

        except Exception as e:

            print(
                f"⚠️ State verification failed: {e}"
            )

        return telemetry

    # ========================================================
    # UPDATE STATE FROM ACTION RESULT
    # ========================================================

    def _update_state_from_result(
        self,
        state,
        action,
        result,
        step_number
    ):

        if state is None:

            return

        if not isinstance(
            result,
            dict
        ):

            return

        # ====================================================
        # RECORD OBSERVATION
        # ====================================================

        observation = {

            "action":
                action,

            "status":
                result.get(
                    "status"
                ),

            "message":
                result.get(
                    "message"
                ),

            "data":
                result.get(
                    "data"
                ),

            "error":
                result.get(
                    "error"
                )

        }

        try:

            state.add_observation(
                observation
            )

        except Exception as e:

            print(
                f"⚠️ Observation update failed: {e}"
            )

        # ====================================================
        # SUCCESS
        # ====================================================

        if result.get(
            "status"
        ) == "success":

            try:

                # Record exactly one successfully executed action.
                # Never replace completed_steps with the complete plan.
                completed_steps = getattr(
                    state,
                    "completed_steps",
                    []
                )

                if not isinstance(
                    completed_steps,
                    list
                ):
                    completed_steps = []

                # Prevent duplicate completion records for the same
                # planned step.
                duplicate = False

                current_index = action.get(
                    "step_index"
                )

                for completed in completed_steps:

                    if isinstance(
                        completed,
                        dict
                    ) and current_index is not None:

                        if completed.get(
                            "step_index"
                        ) == current_index:

                            duplicate = True
                            break

                if not duplicate:

                    state.mark_step_completed(
                        step_number,
                        action
                    )

                updated_steps = getattr(
                    state,
                    "completed_steps",
                    []
                )

                print(
                    "\n========== AGENT PROGRESS =========="
                )

                print(
                    f"Completed: "
                    f"{len(updated_steps)} / "
                    f"{len(getattr(state, 'current_plan', []) or [])}"
                )

            except Exception as e:

                print(
                    "⚠️ Could not mark "
                    f"step completed: {e}"
                )

            # ------------------------------------------------
            # ALWAYS capture browser telemetry
            # ------------------------------------------------

            telemetry = (
                self._update_browser_state(
                    state,
                    result
                )
            )

            # ------------------------------------------------
            # Put telemetry into result as well
            # ------------------------------------------------

            try:

                result[
                    "browser_telemetry"
                ] = telemetry

            except Exception:

                pass

            return

        # ====================================================
        # FAILURE
        # ====================================================

        try:

            state.mark_step_failed(
                step_number,
                result.get(
                    "error"
                )
                or
                "Action execution failed."
            )

        except Exception as e:

            print(
                "⚠️ Could not record "
                f"failed step: {e}"
            )

        # ----------------------------------------------------
        # Capture browser state even after failure
        # ----------------------------------------------------

        try:

            telemetry = (
                self._update_browser_state(
                    state,
                    result
                )
            )

            result[
                "browser_telemetry"
            ] = telemetry

        except Exception as e:

            print(
                f"⚠️ Failure telemetry failed: {e}"
            )

    # ========================================================
    # RECOVERY METADATA
    # ========================================================

    def _update_recovery_state(
        self,
        state,
        result
    ):

        if state is None:

            return

        if not isinstance(
            result,
            dict
        ):

            return

        replans_used = result.get(
            "replans_used"
        )

        if isinstance(
            replans_used,
            int
        ):

            state.replans_used = (
                replans_used
            )

        replan_history = result.get(
            "replan_history"
        )

        if isinstance(
            replan_history,
            list
        ):

            state.replan_history = list(
                replan_history
            )

    # ========================================================
    # RUN AUTONOMOUS TASK
    # ========================================================

    def run(
        self,
        user_message: str,
        event_callback=None
    ):

        # ====================================================
        # CREATE STATE
        # ====================================================

        try:

            state = AgentState(
                user_message
            )

        except Exception as e:

            print(
                f"❌ AgentState initialization failed: {e}"
            )

            self._emit_event(
                event_callback,
                "failed",
                "AgentState initialization failed.",
                {
                    "error": str(e)
                }
            )

            return {

                "status": "failed",

                "phase":
                    "state_initialization",

                "user_message":
                    user_message,

                "error":
                    str(e)

            }

        # ====================================================
        # INITIAL STATUS
        # ====================================================

        try:

            state.set_status(
                "planning"
            )

        except Exception:

            state.status = "planning"

        # ====================================================
        # HEADER
        # ====================================================

        print("\n")

        print(
            "=========================================="
        )

        print(
            "        🤖 PAIO AUTONOMOUS AGENT"
        )

        print(
            "=========================================="
        )

        print(
            "\nUser request:"
        )

        print(
            f"  {user_message}"
        )

        # ====================================================
        # EVENT — START
        # ====================================================

        self._emit_event(
            event_callback,
            "plan",
            "Generating execution plan.",
            {
                "user_message":
                    user_message
            }
        )

        # ====================================================
        # STEP 1 — PLAN
        # ====================================================

        planning_result = (
            self.create_plan(
                user_message
            )
        )

        if (
            planning_result.get(
                "status"
            )
            !=
            "success"
        ):

            try:

                state.set_status(
                    "failed"
                )

            except Exception:

                state.status = "failed"

            error = (
                planning_result.get(
                    "error"
                )
            )

            self._emit_event(
                event_callback,
                "failed",
                "Planning failed.",
                {
                    "error": error
                }
            )

            return {

                "status": "failed",

                "phase":
                    "planning",

                "user_message":
                    user_message,

                "error":
                    error,

                "steps": [],

                "state":
                    state

            }

        steps = planning_result[
            "steps"
        ]

        # ====================================================
        # EVENT — PLAN CREATED
        # ====================================================

        self._emit_event(
            event_callback,
            "plan",
            f"Generated {len(steps)} action(s).",
            {
                "steps":
                    steps,

                "count":
                    len(steps)
            }
        )

        # ====================================================
        # STEP 2 — SAVE PLAN
        # ====================================================

        try:

            state.set_plan(
                steps
            )

        except Exception:

            state.current_plan = list(
                steps
            )

        # ====================================================
        # STEP 3 — VALIDATE
        # ====================================================

        try:

            state.set_status(
                "validating"
            )

        except Exception:

            state.status = "validating"

        print(
            "\n========== VALIDATION =========="
        )

        self._emit_event(
            event_callback,
            "validate",
            "Validating execution plan.",
            {
                "steps":
                    steps
            }
        )

        if not self.validate_plan(
            steps
        ):

            try:

                state.set_status(
                    "failed"
                )

            except Exception:

                state.status = "failed"

            self._emit_event(
                event_callback,
                "failed",
                "Execution plan validation failed.",
                {
                    "steps":
                        steps
                }
            )

            return {

                "status": "failed",

                "phase":
                    "validation",

                "user_message":
                    user_message,

                "error":
                    "Invalid action plan.",

                "steps":
                    steps,

                "state":
                    state

            }

        print(
            "✅ Action plan validated."
        )

        self._emit_event(
            event_callback,
            "validate",
            "Execution plan validated.",
            {
                "valid":
                    True,

                "count":
                    len(steps)
            }
        )

        # ====================================================
        # STEP 4 — EXECUTION
        # ====================================================

        try:

            state.set_status(
                "executing"
            )

        except Exception:

            state.status = "executing"

        print(
            "\n========== AUTONOMOUS LOOP =========="
        )

        total_steps = len(
            steps
        )

        max_iterations = (
            total_steps + 2
        )

        iterations = 0

        # ====================================================
        # AUTONOMOUS LOOP
        # ====================================================

        while (
            iterations
            <
            max_iterations
        ):

            iterations += 1

            print("\n")

            print(
                "------------------------------------------"
            )

            print(
                f"🧠 AUTONOMOUS ITERATION "
                f"{iterations}"
            )

            print(
                "------------------------------------------"
            )

            # =================================================
            # EVALUATE
            # =================================================

            self._emit_event(
                event_callback,
                "evaluate",
                "Evaluating current agent state.",
                {
                    "iteration":
                        iterations,

                    "current_step":
                        getattr(
                            state,
                            "current_step",
                            None
                        ),

                    "completed_steps":
                        getattr(
                            state,
                            "completed_steps",
                            []
                        )
                }
            )

            evaluation = (
                agent_evaluator.evaluate(
                    state
                )
            )

            if not isinstance(
                evaluation,
                dict
            ):

                evaluation = {

                    "status":
                        "failed",

                    "reason":
                        (
                            "Evaluator returned "
                            "invalid result."
                        )

                }

            print(
                f"Evaluator: {evaluation}"
            )

            decision = evaluation.get(
                "status"
            )

            # =================================================
            # COMPLETE
            # =================================================

            if decision == "complete":

                # Safety guard: the controller must never terminate a
                # multi-step plan before every planned step succeeded.
                completed_steps = getattr(
                    state,
                    "completed_steps",
                    []
                )

                if not isinstance(
                    completed_steps,
                    list
                ):
                    completed_steps = []

                if len(completed_steps) < total_steps:

                    print(
                        "\n⚠️ EVALUATOR → COMPLETE TOO EARLY"
                    )

                    print(
                        f"Controller progress: "
                        f"{len(completed_steps)} / {total_steps}"
                    )

                    # Ignore the premature completion and continue with
                    # the first plan step that has not been completed.
                    next_index = len(completed_steps)

                    if next_index >= total_steps:
                        next_index = total_steps - 1

                    next_action = steps[
                        next_index
                    ]

                    print(
                        f"🔧 Controller override → "
                        f"CONTINUE: step {next_index + 1}"
                    )

                    decision = "continue"

                else:

                    try:

                        state.set_status(
                            "completed"
                        )

                    except Exception:

                        state.status = "completed"

                    print(
                        "\n🎯 EVALUATOR → COMPLETE"
                    )

                    print(
                        "🎉 TASK COMPLETED SUCCESSFULLY."
                    )

                    # ---------------------------------------------
                    # TASK MEMORY
                    # ---------------------------------------------
                    # Store one task-level outcome only after the
                    # controller has confirmed every planned step.
                    # Browser actions themselves are not persisted
                    # as long-term memory.
                    try:

                        self.knowledge.add_task(
                            task=user_message,
                            status="completed",
                            steps=total_steps,
                            replans_used=getattr(
                                state,
                                "replans_used",
                                0
                            )
                        )

                        print(
                            "🧠 Task outcome saved to memory."
                        )

                    except Exception as memory_error:

                        # Memory must never break an otherwise
                        # successful autonomous task.
                        print(
                            "⚠️ Task memory save failed: "
                            f"{memory_error}"
                        )

                    self._emit_event(
                        event_callback,
                        "complete",
                        "Objective completed successfully.",
                        {
                            "iterations":
                                iterations,

                            "completed_steps":
                                getattr(
                                    state,
                                    "completed_steps",
                                    []
                                ),

                            "replans_used":
                                getattr(
                                    state,
                                    "replans_used",
                                    0
                                )
                        }
                    )

                    return {

                        "status": "success",

                        "phase":
                            "completed",

                        "user_message":
                            user_message,

                        "plan":
                            steps,

                        "execution": {

                            "status":
                                "success",

                            "replans_used":
                                state.replans_used,

                            "replan_history":
                                state.replan_history

                        },

                        "state":
                            state,

                        "error":
                            None

                    }

            # =================================================
            # FAILED
            # =================================================

            if decision == "failed":

                try:

                    state.set_status(
                        "failed"
                    )

                except Exception:

                    state.status = "failed"

                reason = (
                    evaluation.get(
                        "reason"
                    )
                )

                print(
                    "\n❌ EVALUATOR → FAILED"
                )

                print(
                    f"Reason: {reason}"
                )

                self._emit_event(
                    event_callback,
                    "failed",
                    "Agent evaluator reported failure.",
                    {
                        "reason":
                            reason
                    }
                )

                return {

                    "status": "failed",

                    "phase":
                        "evaluation",

                    "user_message":
                        user_message,

                    "plan":
                        steps,

                    "execution":
                        None,

                    "state":
                        state,

                    "error":
                        reason

                }

            # =================================================
            # CONTINUE
            # =================================================

            if decision != "continue":

                try:

                    state.set_status(
                        "failed"
                    )

                except Exception:

                    state.status = "failed"

                error = (
                    "Evaluator returned "
                    f"unexpected status: "
                    f"{decision}"
                )

                self._emit_event(
                    event_callback,
                    "failed",
                    error
                )

                return {

                    "status":
                        "failed",

                    "phase":
                        "evaluation",

                    "user_message":
                        user_message,

                    "plan":
                        steps,

                    "execution":
                        None,

                    "state":
                        state,

                    "error":
                        error

                }

            # =================================================
            # NEXT ACTION
            # =================================================

            next_action = evaluation.get(
                "next_action"
            )

            if next_action is None:

                try:

                    state.set_status(
                        "failed"
                    )

                except Exception:

                    state.status = "failed"

                error = (
                    "Evaluator requested "
                    "CONTINUE without "
                    "a next action."
                )

                self._emit_event(
                    event_callback,
                    "failed",
                    error
                )

                return {

                    "status":
                        "failed",

                    "phase":
                        "evaluation",

                    "user_message":
                        user_message,

                    "plan":
                        steps,

                    "execution":
                        None,

                    "state":
                        state,

                    "error":
                        error

                }

            print(
                "\n🔄 EVALUATOR → CONTINUE"
            )

            print(
                f"➡️ Next action: {next_action}"
            )

            # =================================================
            # EVENT — CONTINUE
            # =================================================

            self._emit_event(
                event_callback,
                "continue",
                "Evaluator requested the next action.",
                {
                    "next_action":
                        next_action,

                    "iteration":
                        iterations
                }
            )

            # =================================================
            # STEP NUMBER
            # =================================================

            try:

                completed_steps = (
                    state.completed_steps
                )

                if isinstance(
                    completed_steps,
                    list
                ):

                    step_number = (
                        len(
                            completed_steps
                        )
                        + 1
                    )

                else:

                    step_number = (
                        int(
                            completed_steps
                        )
                        + 1
                    )

            except Exception:

                step_number = (
                    iterations
                )

            try:

                state.set_current_step(
                    step_number
                )

            except Exception:

                state.current_step = (
                    step_number
                )

            # =================================================
            # EVENT — EXECUTE
            # =================================================

            self._emit_event(
                event_callback,
                "execute",
                "Executing next autonomous action.",
                {
                    "action":
                        next_action,

                    "step":
                        step_number,

                    "total_steps":
                        total_steps
                }
            )

            # =================================================
            # EXECUTE
            # =================================================

            execution_result = (
                self.execute_action(
                    next_action
                )
            )

            print(
                "\nAction result:"
            )

            print(
                execution_result
            )

            # =================================================
            # EVENT — OBSERVE
            # =================================================

            self._emit_event(
                event_callback,
                "observe",
                "Action completed; updating browser and agent state.",
                {
                    "action":
                        next_action,

                    "step":
                        step_number,

                    "result_status":
                        execution_result.get(
                            "status"
                        )
                        if isinstance(
                            execution_result,
                            dict
                        )
                        else None
                }
            )

            # =================================================
            # UPDATE STATE
            # =================================================

            self._update_state_from_result(
                state,
                next_action,
                execution_result,
                step_number
            )

            self._update_recovery_state(
                state,
                execution_result
            )

            # =================================================
            # EMIT OBSERVATION DATA
            # =================================================

            telemetry = (
                execution_result.get(
                    "browser_telemetry"
                )
                if isinstance(
                    execution_result,
                    dict
                )
                else None
            )

            observation_data = {

                "action":
                    next_action,

                "step":
                    step_number,

                "telemetry":
                    telemetry,

                "current_url":
                    getattr(
                        state,
                        "current_url",
                        None
                    ),

                "page_title":
                    getattr(
                        state,
                        "page_title",
                        None
                    )

            }

            self._emit_event(
                event_callback,
                "observe",
                "Agent state updated.",
                observation_data
            )

            # =================================================
            # FAILURE
            # =================================================

            if (
                not isinstance(
                    execution_result,
                    dict
                )
                or
                execution_result.get(
                    "status"
                ) != "success"
            ):

                try:

                    state.set_status(
                        "failed"
                    )

                except Exception:

                    state.status = "failed"

                error = (
                    execution_result.get(
                        "error"
                    )
                    if isinstance(
                        execution_result,
                        dict
                    )
                    else
                    "Action execution failed."
                )

                print(
                    "\n❌ ACTION FAILED."
                )

                self._emit_event(
                    event_callback,
                    "failed",
                    "Action execution failed.",
                    {
                        "action":
                            next_action,

                        "step":
                            step_number,

                        "error":
                            error
                    }
                )

                return {

                    "status":
                        "failed",

                    "phase":
                        "execution",

                    "user_message":
                        user_message,

                    "plan":
                        steps,

                    "execution":
                        execution_result,

                    "state":
                        state,

                    "error":
                        error

                }

            print(
                "✅ Action completed successfully."
            )

            # =================================================
            # EVENT — POST ACTION EVALUATION
            # =================================================

            self._emit_event(
                event_callback,
                "evaluate",
                "Action completed; preparing next evaluation.",
                {
                    "step":
                        step_number,

                    "completed_steps":
                        getattr(
                            state,
                            "completed_steps",
                            []
                        ),

                    "current_url":
                        getattr(
                            state,
                            "current_url",
                            None
                        ),

                    "page_title":
                        getattr(
                            state,
                            "page_title",
                            None
                        )
                }
            )

        # ====================================================
        # LOOP LIMIT
        # ====================================================

        try:

            state.set_status(
                "failed"
            )

        except Exception:

            state.status = "failed"

        error = (
            "Autonomous loop exceeded "
            "maximum iterations."
        )

        self._emit_event(
            event_callback,
            "failed",
            error,
            {
                "iterations":
                    iterations,

                "max_iterations":
                    max_iterations
            }
        )

        return {

            "status":
                "failed",

            "phase":
                "autonomous_loop",

            "user_message":
                user_message,

            "plan":
                steps,

            "execution":
                None,

            "state":
                state,

            "error":
                error

        }


# ============================================================
# GLOBAL INSTANCE
# ============================================================

agent_controller = AgentController()