"use strict";

/* ============================================================
   PAIOS COMMAND CENTER
   REAL-TIME SSE VERSION
   ============================================================ */


/* ============================================================
   CONFIG
   ============================================================ */

const CONFIG = {

    API_BASE:
        "http://127.0.0.1:8000",

    STREAM_ENDPOINT:
        "/execute/stream",

    TIMEOUT:
        120000

};


/* ============================================================
   AGENT STATE
   ============================================================ */

const state = {

    status:
        "ready",

    goal:
        "",

    plan:
        [],

    currentStep:
        0,

    completedSteps:
        [],

    observations:
        [],

    currentUrl:
        null,

    pageTitle:
        null,

    failedStep:
        null,

    lastError:
        null,

    retryCount:
        0,

    replansUsed:
        0,

    replanHistory:
        [],

    timeline:
        [],

    executionStage:
        "plan",

    currentAction:
        null,

    streamConnected:
        false

};


/* ============================================================
   DOM HELPERS
   ============================================================ */

function $(selector) {

    return document.querySelector(
        selector
    );

}


function $$(selector) {

    return document.querySelectorAll(
        selector
    );

}


/* ============================================================
   INITIALIZATION
   ============================================================ */

document.addEventListener(
    "DOMContentLoaded",
    () => {

        console.log(
            "PAIOS COMMAND CENTER ONLINE"
        );

        setupCommand();

        setupChips();

        updateUI();

    }
);


/* ============================================================
   COMMAND SETUP
   ============================================================ */

function setupCommand() {

    const input =
        $("#commandInput");

    const button =
        $("#executeButton");


    if (button) {

        button.addEventListener(
            "click",
            execute
        );

    }


    if (input) {

        input.addEventListener(
            "keydown",
            event => {

                if (
                    event.key === "Enter" &&
                    event.ctrlKey
                ) {

                    event.preventDefault();

                    execute();

                }

            }
        );

    }

}


/* ============================================================
   COMMAND CHIPS
   ============================================================ */

function setupChips() {

    $$(".command-chip")
        .forEach(
            chip => {

                chip.addEventListener(
                    "click",
                    () => {

                        const input =
                            $("#commandInput");

                        if (!input) {
                            return;
                        }

                        input.value =
                            chip.dataset.command ||
                            chip.textContent.trim();

                        input.focus();

                    }
                );

            }
        );

}


/* ============================================================
   EXECUTE
   ============================================================ */

async function execute() {

    const input =
        $("#commandInput");


    if (!input) {
        return;
    }


    const goal =
        input.value.trim();


    if (!goal) {

        notify(
            "Enter an objective first."
        );

        return;

    }


    resetState(
        goal
    );


    setExecuting(
        true
    );


    updateUI();


    try {

        /*
         * =====================================================
         * REAL-TIME AGENT STREAM
         * =====================================================
         */

        await executeStream(
            goal
        );


    }
    catch (error) {

        console.error(
            "PAIOS STREAM ERROR:",
            error
        );


        state.status =
            "failed";

        state.lastError =
            error.message;


        setExecutionStage(
            "complete"
        );


        addTimeline(
            "ERROR",
            error.message,
            true
        );


        updateUI();


        notify(
            error.message
        );

    }
    finally {

        state.streamConnected =
            false;

        setExecuting(
            false
        );

        updateUI();

    }

}


/* ============================================================
   RESET STATE
   ============================================================ */

function resetState(
    goal
) {

    state.status =
        "executing";

    state.goal =
        goal;

    state.plan =
        [];

    state.currentStep =
        0;

    state.completedSteps =
        [];

    state.observations =
        [];

    state.currentUrl =
        null;

    state.pageTitle =
        null;

    state.failedStep =
        null;

    state.lastError =
        null;

    state.retryCount =
        0;

    state.replansUsed =
        0;

    state.replanHistory =
        [];

    state.timeline =
        [];

    state.executionStage =
        "plan";

    state.currentAction =
        null;

    state.streamConnected =
        false;

}


/* ============================================================
   REAL-TIME SSE EXECUTION
   ============================================================ */

function executeStream(
    goal
) {

    return new Promise(
        (
            resolve,
            reject
        ) => {

            const encodedGoal =
                encodeURIComponent(
                    goal
                );


            const url =
                CONFIG.API_BASE +
                CONFIG.STREAM_ENDPOINT +
                "?goal=" +
                encodedGoal;


            console.log(
                "📡 Connecting to:",
                url
            );


            const eventSource =
                new EventSource(
                    url
                );


            let finished =
                false;


            let timeoutId =
                null;


            /*
             * --------------------------------------------------
             * TIMEOUT
             * --------------------------------------------------
             */

            timeoutId =
                setTimeout(
                    () => {

                        if (finished) {
                            return;
                        }

                        finished = true;

                        eventSource.close();

                        reject(
                            new Error(
                                "PAIOS execution timed out."
                            )
                        );

                    },
                    CONFIG.TIMEOUT
                );


            /*
             * --------------------------------------------------
             * CLEANUP
             * --------------------------------------------------
             */

            function cleanup() {

                clearTimeout(
                    timeoutId
                );

                eventSource.close();

            }


            /*
             * --------------------------------------------------
             * CONNECTED
             * --------------------------------------------------
             */

            eventSource.addEventListener(
                "agent",
                event => {

                    let payload;

                    try {

                        payload =
                            JSON.parse(
                                event.data
                            );

                    }
                    catch (error) {

                        console.error(
                            "Invalid SSE payload:",
                            event.data
                        );

                        return;

                    }


                    console.log(
                        "📡 PAIOS EVENT:",
                        payload
                    );


                    handleAgentEvent(
                        payload
                    );


                    /*
                     * ------------------------------------------------
                     * FINAL RESULT
                     * ------------------------------------------------
                     */

                    if (
                        payload.stage ===
                        "result"
                    ) {

                        if (finished) {
                            return;
                        }

                        finished = true;

                        cleanup();


                        const result =
                            payload.data;


                        if (
                            result &&
                            typeof result ===
                            "object"
                        ) {

                            processResult(
                                result
                            );

                        }
                        else {

                            state.status =
                                "complete";

                            setExecutionStage(
                                "complete"
                            );

                            addTimeline(
                                "COMPLETE",
                                "Objective completed successfully."
                            );

                            updateUI();

                        }


                        resolve(
                            result
                        );

                    }


                    /*
                     * ------------------------------------------------
                     * FAILED
                     * ------------------------------------------------
                     */

                    if (
                        payload.stage ===
                        "failed"
                    ) {

                        /*
                         * Backend normally sends a
                         * final result after execution.
                         *
                         * Only terminate immediately if
                         * the payload contains a direct
                         * error and no result is expected.
                         */

                        if (
                            payload.data &&
                            payload.data.error
                        ) {

                            state.status =
                                "failed";

                            state.lastError =
                                payload.data.error;

                            updateUI();

                        }

                    }

                }
            );


            /*
             * --------------------------------------------------
             * OPEN
             * --------------------------------------------------
             */

            eventSource.onopen =
                () => {

                    console.log(
                        "🟢 PAIOS SSE CONNECTED"
                    );

                    state.streamConnected =
                        true;

                    addTimeline(
                        "SYSTEM",
                        "Connected to PAIOS live execution."
                    );

                    updateUI();

                };


            /*
             * --------------------------------------------------
             * ERROR
             * --------------------------------------------------
             */

            eventSource.onerror =
                error => {

                    console.error(
                        "🔴 SSE CONNECTION ERROR:",
                        error
                    );


                    /*
                     * EventSource automatically attempts
                     * reconnection.
                     *
                     * We only reject if the connection
                     * is already finished or closed.
                     */

                    if (
                        eventSource.readyState ===
                        EventSource.CLOSED &&
                        !finished
                    ) {

                        finished = true;

                        cleanup();

                        reject(
                            new Error(
                                "Lost connection to PAIOS backend."
                            )
                        );

                    }

                };

        }
    );

}


/* ============================================================
   HANDLE AGENT EVENT
   ============================================================ */

function handleAgentEvent(
    payload
) {

    if (!payload) {
        return;
    }


    const stage =
        String(
            payload.stage ||
            ""
        ).toLowerCase();


    const message =
        payload.message ||
        "";


    const data =
        payload.data ||
        {};


    console.log(
        `🤖 ${stage.toUpperCase()}:`,
        message,
        data
    );


    /* ========================================================
       CONNECTED
       ======================================================== */

    if (
        stage ===
        "connected"
    ) {

        state.streamConnected =
            true;

        return;

    }


    /* ========================================================
       PLAN
       ======================================================== */

    if (
        stage ===
        "plan"
    ) {

        state.status =
            "executing";

        setExecutionStage(
            "plan"
        );


        if (
            Array.isArray(
                data.steps
            )
        ) {

            state.plan =
                data.steps;

        }


        if (
            Array.isArray(
                data.plan
            )
        ) {

            state.plan =
                data.plan;

        }


        const count =
            data.count ||
            state.plan.length;


        addTimeline(
            "PLAN",
            message ||
            `${count} autonomous action(s) generated.`
        );


        updateUI();

        return;

    }


    /* ========================================================
       VALIDATE
       ======================================================== */

    if (
        stage ===
        "validate"
    ) {

        addTimeline(
            "VALIDATE",
            message ||
            "Execution plan validated."
        );


        updateUI();

        return;

    }


    /* ========================================================
       EVALUATE
       ======================================================== */

    if (
        stage ===
        "evaluate"
    ) {

        state.status =
            "executing";


        setExecutionStage(
            "evaluate"
        );


        addTimeline(
            "EVALUATE",
            message ||
            "Evaluating current agent state."
        );


        updateUI();

        return;

    }


    /* ========================================================
       CONTINUE
       ======================================================== */

    if (
        stage ===
        "continue"
    ) {

        state.status =
            "executing";


        /*
         * CONTINUE is a decision between
         * EVALUATE and EXECUTE.
         *
         * We therefore display the decision
         * in the timeline but keep the graph
         * at the evaluation stage until the
         * actual EXECUTE event arrives.
         */

        const nextAction =
            data.next_action ||
            data.action ||
            null;


        state.currentAction =
            nextAction;


        let displayMessage =
            message ||
            "Agent decided to continue.";


        if (
            nextAction
        ) {

            displayMessage +=
                ` Next action: ${formatAction(nextAction)}`;

        }


        addTimeline(
            "CONTINUE",
            displayMessage
        );


        updateUI();

        return;

    }


    /* ========================================================
       EXECUTE
       ======================================================== */

    if (
        stage ===
        "execute"
    ) {

        state.status =
            "executing";


        setExecutionStage(
            "execute"
        );


        if (
            data.step !==
            undefined
        ) {

            state.currentStep =
                Number(
                    data.step
                );

        }


        if (
            data.action
        ) {

            state.currentAction =
                data.action;

        }


        const action =
            data.action ||
            "autonomous action";


        addTimeline(
            "EXECUTE",
            message ||
            `Executing ${formatAction(action)}.`
        );


        updateUI();

        return;

    }


    /* ========================================================
       OBSERVE
       ======================================================== */

    if (
        stage ===
        "observe"
    ) {

        state.status =
            "executing";


        setExecutionStage(
            "observe"
        );


        /*
         * Browser telemetry
         */

        if (
            data.current_url
        ) {

            state.currentUrl =
                data.current_url;

        }


        if (
            data.page_title
        ) {

            state.pageTitle =
                data.page_title;

        }


        if (
            data.telemetry
        ) {

            applyTelemetry(
                data.telemetry
            );

        }


        /*
         * Observation data
         */

        if (
            data.observation
        ) {

            addObservation(
                data.observation
            );

        }


        const action =
            data.action ||
            state.currentAction;


        if (
            message
        ) {

            addTimeline(
                "OBSERVE",
                message
            );

        }
        else {

            addTimeline(
                "OBSERVE",
                action
                    ? `Observed result of ${formatAction(action)}.`
                    : "Browser state updated."
            );

        }


        /*
         * Successful step
         */

        if (
            data.step !==
            undefined &&
            data.result_status ===
            "success"
        ) {

            const step =
                Number(
                    data.step
                );


            if (
                !state.completedSteps.includes(
                    step
                )
            ) {

                state.completedSteps.push(
                    step
                );

            }

        }


        updateUI();

        return;

    }


    /* ========================================================
       COMPLETE
       ======================================================== */

    if (
        stage ===
        "complete"
    ) {

        state.status =
            "complete";


        setExecutionStage(
            "complete"
        );


        if (
            Array.isArray(
                data.completed_steps
            )
        ) {

            state.completedSteps =
                data.completed_steps;

        }


        if (
            data.replans_used !==
            undefined
        ) {

            state.replansUsed =
                Number(
                    data.replans_used
                );

        }


        addTimeline(
            "COMPLETE",
            message ||
            "Objective completed successfully."
        );


        notify(
            "PAIOS completed the objective."
        );


        updateUI();

        return;

    }


    /* ========================================================
       FAILED
       ======================================================== */

    if (
        stage ===
        "failed"
    ) {

        state.status =
            "failed";


        state.lastError =
            data.error ||
            data.reason ||
            message ||
            "Agent execution failed.";


        addTimeline(
            "RECOVERY",
            state.lastError,
            true
        );


        updateUI();

        return;

    }


    /* ========================================================
       RESULT
       ======================================================== */

    if (
        stage ===
        "result"
    ) {

        /*
         * Final result is processed by
         * executeStream().
         */

        return;

    }

}


/* ============================================================
   APPLY TELEMETRY
   ============================================================ */

function applyTelemetry(
    telemetry
) {

    if (!telemetry) {
        return;
    }


    if (
        telemetry.current_url
    ) {

        state.currentUrl =
            telemetry.current_url;

    }


    if (
        telemetry.url
    ) {

        state.currentUrl =
            telemetry.url;

    }


    if (
        telemetry.page_title
    ) {

        state.pageTitle =
            telemetry.page_title;

    }


    if (
        telemetry.title
    ) {

        state.pageTitle =
            telemetry.title;

    }

}


/* ============================================================
   ADD OBSERVATION
   ============================================================ */

function addObservation(
    observation
) {

    if (!observation) {
        return;
    }


    if (
        !state.observations.includes(
            observation
        )
    ) {

        state.observations.push(
            observation
        );

    }

}


/* ============================================================
   PROCESS FINAL RESULT
   ============================================================ */

function processResult(
    result
) {

    if (!result) {

        throw new Error(
            "Backend returned no result."
        );

    }


    console.log(
        "PAIOS FINAL RESULT:",
        result
    );


    /*
     * --------------------------------------------------------
     * AGENT STATE
     * --------------------------------------------------------
     */

    const agentState =
        result.state ||
        result.agent_state ||
        result.agentState ||
        result.snapshot ||
        null;


    if (agentState) {

        readAgentState(
            agentState
        );

    }


    /*
     * --------------------------------------------------------
     * PLAN
     * --------------------------------------------------------
     */

    const plan =
        result.plan ||
        result.current_plan ||
        agentState?.current_plan ||
        [];


    if (
        Array.isArray(
            plan
        )
    ) {

        state.plan =
            plan;

    }


    /*
     * --------------------------------------------------------
     * OBSERVATIONS
     * --------------------------------------------------------
     */

    const observations =
        result.observations ||
        result.execution?.observations ||
        agentState?.observations ||
        [];


    if (
        Array.isArray(
            observations
        )
    ) {

        state.observations =
            observations;

    }


    /*
     * --------------------------------------------------------
     * EXECUTION
     * --------------------------------------------------------
     */

    const execution =
        result.execution ||
        result.result ||
        result.execution_result ||
        null;


    if (execution) {

        readExecution(
            execution
        );

    }


    /*
     * --------------------------------------------------------
     * FINAL STATUS
     * --------------------------------------------------------
     */

    if (
        result.status
    ) {

        state.status =
            normalizeStatus(
                result.status
            );

    }


    /*
     * --------------------------------------------------------
     * BROWSER TELEMETRY
     * --------------------------------------------------------
     */

    if (
        result.browser_telemetry
    ) {

        applyTelemetry(
            result.browser_telemetry
        );

    }


    /*
     * --------------------------------------------------------
     * ERROR
     * --------------------------------------------------------
     */

    if (
        result.error
    ) {

        state.lastError =
            result.error;

    }


    /*
     * --------------------------------------------------------
     * FINAL UI STATE
     * --------------------------------------------------------
     */

    if (
        state.status ===
        "failed"
    ) {

        setExecutionStage(
            "complete"
        );


        addTimeline(
            "RECOVERY",
            state.lastError ||
            "Agent execution failed.",
            true
        );


    }
    else {

        state.status =
            "complete";


        setExecutionStage(
            "complete"
        );


        /*
         * Only add COMPLETE if the
         * event hasn't already done so.
         */

        const alreadyComplete =
            state.timeline.some(
                item =>
                    item.title ===
                    "COMPLETE"
            );


        if (!alreadyComplete) {

            addTimeline(
                "COMPLETE",
                "Objective completed successfully."
            );

        }


        notify(
            "PAIOS completed the objective."
        );

    }


    updateUI();

}


/* ============================================================
   READ AGENT STATE
   ============================================================ */

function readAgentState(
    agentState
) {

    if (!agentState) {
        return;
    }


    state.goal =
        agentState.user_goal ??
        agentState.goal ??
        state.goal;


    state.status =
        normalizeStatus(
            agentState.status
        );


    state.plan =
        agentState.current_plan ??
        agentState.plan ??
        state.plan;


    state.currentStep =
        Number(
            agentState.current_step ??
            agentState.currentStep ??
            state.currentStep
        );


    state.completedSteps =
        agentState.completed_steps ??
        agentState.completedSteps ??
        state.completedSteps;


    state.observations =
        agentState.observations ??
        state.observations;


    state.failedStep =
        agentState.failed_step ??
        agentState.failedStep ??
        null;


    state.lastError =
        agentState.last_error ??
        agentState.lastError ??
        null;


    state.currentUrl =
        agentState.current_url ??
        agentState.currentUrl ??
        state.currentUrl;


    state.pageTitle =
        agentState.page_title ??
        agentState.pageTitle ??
        state.pageTitle;


    state.retryCount =
        Number(
            agentState.retry_count ??
            agentState.retryCount ??
            0
        );


    state.replansUsed =
        Number(
            agentState.replans_used ??
            agentState.replansUsed ??
            0
        );


    state.replanHistory =
        agentState.replan_history ??
        agentState.replanHistory ??
        [];


    /*
     * Some AgentState implementations may
     * expose browser_state.
     */

    if (
        agentState.browser_state
    ) {

        applyTelemetry(
            agentState.browser_state
        );

    }

}


/* ============================================================
   READ EXECUTION
   ============================================================ */

function readExecution(
    execution
) {

    if (!execution) {
        return;
    }


    if (
        execution.status ===
        "failed"
    ) {

        state.status =
            "failed";

    }


    if (
        execution.current_url
    ) {

        state.currentUrl =
            execution.current_url;

    }


    if (
        execution.url
    ) {

        state.currentUrl =
            execution.url;

    }


    if (
        execution.page_title
    ) {

        state.pageTitle =
            execution.page_title;

    }


    if (
        execution.title
    ) {

        state.pageTitle =
            execution.title;

    }


    if (
        execution.error
    ) {

        state.lastError =
            execution.error;

    }


    if (
        execution.browser_telemetry
    ) {

        applyTelemetry(
            execution.browser_telemetry
        );

    }

}


/* ============================================================
   STATUS
   ============================================================ */

function normalizeStatus(
    status
) {

    if (!status) {

        return state.status;

    }


    const value =
        String(
            status
        ).toLowerCase();


    if (
        value === "completed" ||
        value === "complete" ||
        value === "success" ||
        value === "successful"
    ) {

        return "complete";

    }


    if (
        value === "failed" ||
        value === "failure" ||
        value === "error"
    ) {

        return "failed";

    }


    if (
        value === "executing" ||
        value === "running"
    ) {

        return "executing";

    }


    return "ready";

}


/* ============================================================
   COMPLETION
   ============================================================ */

function isComplete() {

    if (
        state.status ===
        "complete"
    ) {

        return true;

    }


    if (
        state.plan.length > 0 &&
        state.completedSteps.length >=
        state.plan.length
    ) {

        return true;

    }


    return false;

}


/* ============================================================
   FAILURE
   ============================================================ */

function isFailed() {

    return (
        state.status === "failed" ||
        state.failedStep !== null ||
        state.lastError !== null
    );

}


/* ============================================================
   ACTION NAME
   ============================================================ */

function getAction(
    observation
) {

    if (!observation) {

        return "ACTION";

    }


    const action =
        observation.action;


    if (
        typeof action ===
        "string"
    ) {

        return action;

    }


    if (action) {

        return (
            action.action ||
            action.type ||
            "ACTION"
        );

    }


    return "ACTION";

}


/* ============================================================
   FORMAT ACTION
   ============================================================ */

function formatAction(
    action
) {

    if (!action) {

        return "ACTION";

    }


    if (
        typeof action ===
        "string"
    ) {

        return action;

    }


    if (
        typeof action ===
        "object"
    ) {

        if (
            action.action
        ) {

            if (
                action.query
            ) {

                return (
                    `${action.action}: ${action.query}`
                );

            }

            if (
                action.target
            ) {

                return (
                    `${action.action}: ${action.target}`
                );

            }

            if (
                action.url
            ) {

                return (
                    `${action.action}: ${action.url}`
                );

            }

            return action.action;

        }

        try {

            return JSON.stringify(
                action
            );

        }
        catch {

            return "ACTION";

        }

    }


    return String(
        action
    );

}


/* ============================================================
   EXECUTION STAGE
   ============================================================ */

function setExecutionStage(
    stage
) {

    const allowedStages = [

        "plan",

        "execute",

        "observe",

        "evaluate",

        "complete"

    ];


    /*
     * CONTINUE is a real backend event,
     * but the graph has no CONTINUE node.
     *
     * We therefore keep the graph at
     * EVALUATE until EXECUTE arrives.
     */

    if (
        !allowedStages.includes(
            stage
        )
    ) {

        stage =
            "evaluate";

    }


    state.executionStage =
        stage;


    updateExecutionGraph();

}


/* ============================================================
   EXECUTION GRAPH
   ============================================================ */

function updateExecutionGraph() {

    const graph =
        $("#executionGraph");


    if (!graph) {
        return;
    }


    const nodes =
        graph.querySelectorAll(
            ".execution-node"
        );


    const connectors =
        graph.querySelectorAll(
            ".execution-connector"
        );


    if (!nodes.length) {
        return;
    }


    const stages = [

        "plan",

        "execute",

        "observe",

        "evaluate",

        "complete"

    ];


    let activeIndex =
        stages.indexOf(
            state.executionStage
        );


    if (
        activeIndex < 0
    ) {

        activeIndex =
            0;

    }


    /*
     * --------------------------------------------------------
     * NODE STATE
     * --------------------------------------------------------
     */

    nodes.forEach(
        (
            node,
            index
        ) => {

            node.classList.remove(
                "active",
                "completed"
            );


            if (
                index <
                activeIndex
            ) {

                node.classList.add(
                    "completed"
                );

            }


            if (
                index ===
                activeIndex
            ) {

                node.classList.add(
                    "active"
                );

            }


            if (
                state.status ===
                "complete"
            ) {

                node.classList.remove(
                    "active"
                );

                node.classList.add(
                    "completed"
                );

            }


            if (
                state.status ===
                "failed" &&
                index ===
                activeIndex
            ) {

                node.classList.remove(
                    "active"
                );

                node.classList.add(
                    "active"
                );

            }

        }
    );


    /*
     * --------------------------------------------------------
     * CONNECTORS
     * --------------------------------------------------------
     */

    connectors.forEach(
        (
            connector,
            index
        ) => {

            connector.classList.remove(
                "completed"
            );


            if (
                index <
                activeIndex
            ) {

                connector.classList.add(
                    "completed"
                );

            }


            if (
                state.status ===
                "complete"
            ) {

                connector.classList.add(
                    "completed"
                );

            }

        }
    );


    /*
     * --------------------------------------------------------
     * EXECUTION STATE LABEL
     * --------------------------------------------------------
     */

    const executionState =
        $("#executionState");


    if (executionState) {

        const labels = {

            plan:
                "PLANNING",

            execute:
                "EXECUTING",

            observe:
                "OBSERVING",

            evaluate:
                "EVALUATING",

            complete:
                "COMPLETE"

        };


        if (
            state.status ===
            "failed"
        ) {

            executionState.textContent =
                "RECOVERY";

        }
        else {

            executionState.textContent =
                labels[
                    state.executionStage
                ] ||
                "STANDBY";

        }

    }

}


/* ============================================================
   TIMELINE
   ============================================================ */

function addTimeline(
    title,
    message,
    error = false
) {

    /*
     * Prevent accidental duplicate
     * messages from SSE + final result.
     */

    const last =
        state.timeline[
            state.timeline.length - 1
        ];


    if (
        last &&
        last.title === title &&
        last.message === String(message)
    ) {

        return;

    }


    state.timeline.push({

        title:
            title,

        message:
            String(message),

        error:
            error,

        time:
            new Date()

    });


    renderTimeline();

}


/* ============================================================
   RENDER TIMELINE
   ============================================================ */

function renderTimeline() {

    const container =
        $("#timelineContainer");


    if (!container) {
        return;
    }


    if (
        state.timeline.length === 0
    ) {

        container.innerHTML = `

            <div class="timeline-empty">

                <span class="empty-symbol">
                    ◉
                </span>

                <span>
                    Awaiting autonomous execution
                </span>

            </div>

        `;

        return;

    }


    container.innerHTML =
        state.timeline
            .map(
                event => {

                    const time =
                        event.time
                            .toLocaleTimeString();


                    return `

                        <div class="
                            timeline-event
                            ${event.error
                                ? "timeline-error"
                                : ""}
                        ">

                            <div class="timeline-icon">

                                ${
                                    event.error
                                        ? "!"
                                        : "✓"
                                }

                            </div>

                            <div>

                                <div class="timeline-title">

                                    ${escapeHTML(
                                        event.title
                                    )}

                                </div>

                                <div class="timeline-message">

                                    ${escapeHTML(
                                        event.message
                                    )}

                                </div>

                                <div class="timeline-time">

                                    ${time}

                                </div>

                            </div>

                        </div>

                    `;

                }
            )
            .join("");


    container.scrollTop =
        container.scrollHeight;

}


/* ============================================================
   UI UPDATE
   ============================================================ */

function updateUI() {

    updateStatus();

    updateObjective();

    updateTelemetry();

    updateProgress();

    updateBrowser();

    updateObservations();

    updateDecision();

    updateExecutionGraph();

    renderTimeline();

}


/* ============================================================
   STATUS UI
   ============================================================ */

function updateStatus() {

    const title =
        $("#agentStatus");

    const subtitle =
        $("#agentStatusText");

    const execution =
        $("#executionState");


    const values = {

        ready: [

            "READY",

            "Awaiting command",

            "STANDBY"

        ],

        executing: [

            "EXECUTING",

            "PAIOS is operating autonomously",

            "ACTIVE"

        ],

        complete: [

            "COMPLETE",

            "Objective successfully completed",

            "SUCCESS"

        ],

        failed: [

            "RECOVERY",

            "Execution requires recovery",

            "ERROR"

        ]

    };


    const current =
        values[
            state.status
        ] ||
        values.ready;


    if (title) {

        title.textContent =
            current[0];

    }


    if (subtitle) {

        subtitle.textContent =
            current[1];

    }


    if (execution) {

        if (
            state.status ===
            "executing"
        ) {

            execution.textContent =
                getExecutionLabel();

        }
        else {

            execution.textContent =
                current[2];

        }

    }

}


/* ============================================================
   EXECUTION LABEL
   ============================================================ */

function getExecutionLabel() {

    const labels = {

        plan:
            "PLANNING",

        execute:
            "EXECUTING",

        observe:
            "OBSERVING",

        evaluate:
            "EVALUATING",

        complete:
            "COMPLETE"

    };


    return (
        labels[
            state.executionStage
        ] ||
        "ACTIVE"
    );

}


/* ============================================================
   OBJECTIVE
   ============================================================ */

function updateObjective() {

    const element =
        $("#goalDisplay");


    if (!element) {
        return;
    }


    element.textContent =
        state.goal ||
        "No active objective.";

}


/* ============================================================
   TELEMETRY
   ============================================================ */

function updateTelemetry() {

    const total =
        state.plan.length;


    const current =
        Math.min(
            state.currentStep,
            total
        );


    setText(
        "#stepCount",
        `${current}/${total}`
    );


    setText(
        "#observationCount",
        state.observations.length
    );


    setText(
        "#retryCount",
        state.retryCount
    );


    setText(
        "#replanCount",
        state.replansUsed
    );


    setText(
        "#bottomStep",
        `${String(current).padStart(2, "0")}/${String(total).padStart(2, "0")}`
    );


    setText(
        "#bottomObservations",
        String(
            state.observations.length
        ).padStart(
            2,
            "0"
        )
    );


    setText(
        "#bottomRetries",
        String(
            state.retryCount
        ).padStart(
            2,
            "0"
        )
    );


    setText(
        "#bottomReplans",
        String(
            state.replansUsed
        ).padStart(
            2,
            "0"
        )
    );

}


/* ============================================================
   PROGRESS
   ============================================================ */

function updateProgress() {

    const total =
        state.plan.length;


    const completed =
        state.completedSteps.length;


    let percentage =
        0;


    if (
        total > 0
    ) {

        percentage =
            Math.min(
                100,
                Math.round(
                    completed /
                    total *
                    100
                )
            );

    }


    if (
        state.status ===
        "complete"
    ) {

        percentage =
            100;

    }


    const bar =
        $("#progressBar");


    const text =
        $("#progressText");


    if (bar) {

        bar.style.width =
            `${percentage}%`;

    }


    if (text) {

        text.textContent =
            `${percentage}%`;

    }

}


/* ============================================================
   BROWSER
   ============================================================ */

function updateBrowser() {

    setText(
        "#currentUrl",
        state.currentUrl ||
        "—"
    );


    setText(
        "#pageTitle",
        state.pageTitle ||
        "—"
    );

}


/* ============================================================
   OBSERVATIONS
   ============================================================ */

function updateObservations() {

    const container =
        $("#observationsContainer");


    if (!container) {
        return;
    }


    if (
        state.observations.length === 0
    ) {

        container.innerHTML = `

            <div class="observation-empty">

                No observations recorded.

            </div>

        `;

        return;

    }


    container.innerHTML =
        state.observations
            .map(
                observation => {

                    const action =
                        getAction(
                            observation
                        );


                    const message =
                        observation.message ||
                        observation.error ||
                        "Action completed.";


                    const success =
                        observation.status ===
                        "success";


                    return `

                        <div class="
                            observation
                            ${success
                                ? "success"
                                : ""}
                        ">

                            <div class="observation-action">

                                ${escapeHTML(
                                    action.toUpperCase()
                                )}

                            </div>

                            <div class="observation-message">

                                ${escapeHTML(
                                    message
                                )}

                            </div>

                        </div>

                    `;

                }
            )
            .join("");

}


/* ============================================================
   DECISION
   ============================================================ */

function updateDecision() {

    const title =
        $("#decisionTitle");

    const text =
        $("#decisionText");


    if (
        !title ||
        !text
    ) {

        return;

    }


    if (
        state.status ===
        "complete"
    ) {

        title.textContent =
            "COMPLETE";


        text.textContent =
            "No additional action is required.";

        return;

    }


    if (
        state.status ===
        "failed"
    ) {

        title.textContent =
            "RECOVERY";


        text.textContent =
            state.lastError ||
            "Agent execution failed.";

        return;

    }


    if (
        state.status ===
        "executing"
    ) {

        const labels = {

            plan:
                [
                    "PLAN",
                    "PAIOS is generating the execution strategy."
                ],

            execute:
                [
                    "EXECUTE",
                    "PAIOS is performing the planned action."
                ],

            observe:
                [
                    "OBSERVE",
                    "PAIOS is inspecting the result."
                ],

            evaluate:
                [
                    "EVALUATE",
                    "PAIOS is evaluating the current state."
                ],

            complete:
                [
                    "COMPLETE",
                    "Objective execution is complete."
                ]

        };


        const current =
            labels[
                state.executionStage
            ] ||
            labels.plan;


        title.textContent =
            current[0];


        text.textContent =
            current[1];


        return;

    }


    title.textContent =
        "WAITING";


    text.textContent =
        "No active autonomous decision.";

}


/* ============================================================
   EXECUTE BUTTON
   ============================================================ */

function setExecuting(
    executing
) {

    const button =
        $("#executeButton");


    if (!button) {
        return;
    }


    button.disabled =
        executing;


    if (executing) {

        button.innerHTML = `

            <span>
                EXECUTING
            </span>

            <span>
                ◌
            </span>

        `;

    }
    else {

        button.innerHTML = `

            <span>
                EXECUTE
            </span>

            <span>
                →
            </span>

        `;

    }

}


/* ============================================================
   HELPERS
   ============================================================ */

function setText(
    selector,
    value
) {

    const element =
        $(selector);


    if (element) {

        element.textContent =
            value;

    }

}


function escapeHTML(
    value
) {

    return String(
        value ??
        ""
    )
        .replaceAll(
            "&",
            "&amp;"
        )
        .replaceAll(
            "<",
            "&lt;"
        )
        .replaceAll(
            ">",
            "&gt;"
        )
        .replaceAll(
            '"',
            "&quot;"
        )
        .replaceAll(
            "'",
            "&#039;"
        );

}


/* ============================================================
   NOTIFICATIONS
   ============================================================ */

function notify(
    message
) {

    const container =
        $("#notificationContainer");


    if (!container) {
        return;
    }


    const notification =
        document.createElement(
            "div"
        );


    notification.className =
        "notification";


    notification.textContent =
        message;


    container.appendChild(
        notification
    );


    setTimeout(
        () => {

            notification.remove();

        },
        4000
    );

}


/* ============================================================
   DEBUG API
   ============================================================ */

window.PAIOS = {

    state:
        state,

    execute:
        execute,

    updateUI:
        updateUI,

    setExecutionStage:
        setExecutionStage,

    executeStream:
        executeStream,

    handleAgentEvent:
        handleAgentEvent

};


console.log(
    "PAIOS AI COMMAND CENTER READY."
);