import React, { useMemo, useRef, useState } from "react";
import "./App.css";

const API_BASE =
  import.meta.env.VITE_API_BASE || "http://127.0.0.1:8000";

const INITIAL_STATE = {
  status: "ready",
  stage: "plan",
  goal: "",
  currentStep: 0,
  totalSteps: 0,
  observations: [],
  retries: 0,
  replans: 0,
  currentUrl: "",
  pageTitle: "",
  decision: "WAITING",
  decisionText: "No active autonomous decision.",
  timeline: [],
  error: "",
  result: null,
};

const STAGES = [
  ["plan", "PLAN", "Generate strategy"],
  ["execute", "EXECUTE", "Perform action"],
  ["observe", "OBSERVE", "Inspect result"],
  ["evaluate", "EVALUATE", "Decide next action"],
  ["complete", "COMPLETE", "Finish objective"],
];

function App() {
  const [goal, setGoal] = useState(
    "Search for Python tutorials and click the first search result"
  );

  const [state, setState] = useState(INITIAL_STATE);
  const [running, setRunning] = useState(false);

  // ============================================================
  // PAIOS QUESTION CONSOLE
  // Kept completely separate from execution state so running a
  // browser task can never reset or erase the chat answer.
  // ============================================================
  const [question, setQuestion] = useState("");
  const [questionBusy, setQuestionBusy] = useState(false);
  const [isListening, setIsListening] = useState(false);
  const [isCommandListening, setIsCommandListening] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false);

  const recognitionRef = useRef(null);
  const commandRecognitionRef = useRef(null);
  const audioRef = useRef(null);
  const audioUrlRef = useRef(null);
  const [questionMessages, setQuestionMessages] = useState([
    {
      id: "welcome",
      role: "agent",
      text: "Ask me a normal question. This console is separate from browser automation.",
      time: new Date().toLocaleTimeString(),
    },
  ]);

  const eventSourceRef = useRef(null);

  const progress = useMemo(() => {
    if (!state.totalSteps) {
      return state.status === "complete" ? 100 : 0;
    }

    return Math.min(
      100,
      Math.round((state.currentStep / state.totalSteps) * 100)
    );
  }, [state.currentStep, state.totalSteps, state.status]);

  function addTimeline(type, message, failed = false) {
    setState((prev) => ({
      ...prev,
      timeline: [
        ...prev.timeline,
        {
          id: `${Date.now()}-${Math.random()}`,
          type,
          message: String(message || ""),
          failed,
          time: new Date().toLocaleTimeString(),
        },
      ],
    }));
  }

  function addQuestionMessage(role, text) {
    setQuestionMessages((prev) => [
      ...prev,
      {
        id: `${Date.now()}-${Math.random()}`,
        role,
        text: String(text ?? ""),
        time: new Date().toLocaleTimeString(),
      },
    ]);
  }

  function stopPAIOSVoice() {
    if (recognitionRef.current) { try { recognitionRef.current.abort(); } catch {} recognitionRef.current = null; }
    if (audioRef.current) { try { audioRef.current.pause(); audioRef.current.currentTime = 0; } catch {} audioRef.current = null; }
    if (audioUrlRef.current) { URL.revokeObjectURL(audioUrlRef.current); audioUrlRef.current = null; }
    setIsListening(false);
    setIsSpeaking(false);
  }

  function startVoiceInput() {
    if (questionBusy || isListening) return;
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) { addQuestionMessage("error", "Voice input is not supported by this browser. Use Chrome or Edge."); return; }
    const recognition = new SpeechRecognition();
    recognition.lang = "en-US";
    recognition.continuous = false;
    recognition.interimResults = true;
    recognition.maxAlternatives = 1;
    recognitionRef.current = recognition;
    recognition.onstart = () => setIsListening(true);
    recognition.onresult = (event) => {
      let transcript = "";
      for (let i = event.resultIndex; i < event.results.length; i += 1) transcript += event.results[i][0].transcript;
      if (transcript.trim()) setQuestion(transcript.trim());
    };
    recognition.onerror = (event) => {
      console.error("PAIOS VOICE INPUT ERROR:", event.error);
      if (event.error === "not-allowed") addQuestionMessage("error", "Microphone permission was denied. Allow microphone access and try again.");
      else if (event.error !== "aborted") addQuestionMessage("error", `Voice input error: ${event.error}`);
      setIsListening(false); recognitionRef.current = null;
    };
    recognition.onend = () => { setIsListening(false); recognitionRef.current = null; };
    try { recognition.start(); } catch (error) { console.error("PAIOS VOICE START ERROR:", error); setIsListening(false); recognitionRef.current = null; }
  }

  function startCommandVoiceInput() {
    if (running || isCommandListening) {
      return;
    }

    const SpeechRecognition =
      window.SpeechRecognition ||
      window.webkitSpeechRecognition;

    if (!SpeechRecognition) {
      addTimeline(
        "VOICE",
        "Voice input is not supported by this browser. Use Chrome or Edge.",
        true
      );
      return;
    }

    if (commandRecognitionRef.current) {
      try {
        commandRecognitionRef.current.abort();
      } catch {
        // Ignore.
      }
    }

    const recognition = new SpeechRecognition();

    recognition.lang = "en-US";
    recognition.continuous = false;
    recognition.interimResults = true;
    recognition.maxAlternatives = 1;

    commandRecognitionRef.current = recognition;

    recognition.onstart = () => {
      setIsCommandListening(true);
      addTimeline("VOICE", "Listening for a PAIOS command...");
    };

    recognition.onresult = (event) => {
      let finalTranscript = "";

      for (
        let i = event.resultIndex;
        i < event.results.length;
        i += 1
      ) {
        const result = event.results[i];

        if (result.isFinal) {
          finalTranscript += result[0].transcript;
        }
      }

      const command = finalTranscript.trim();

      if (!command) {
        return;
      }

      setGoal(command);

      addTimeline(
        "VOICE",
        `Command recognized: "${command}"`
      );
    };

    recognition.onerror = (event) => {
      console.error(
        "PAIOS COMMAND VOICE INPUT ERROR:",
        event.error
      );

      if (event.error === "not-allowed") {
        addTimeline(
          "VOICE",
          "Microphone permission was denied for command voice input.",
          true
        );
      } else if (event.error !== "aborted") {
        addTimeline(
          "VOICE",
          `Command voice input error: ${event.error}`,
          true
        );
      }

      setIsCommandListening(false);
      commandRecognitionRef.current = null;
    };

    recognition.onend = () => {
      setIsCommandListening(false);

      if (commandRecognitionRef.current === recognition) {
        commandRecognitionRef.current = null;
      }
    };

    try {
      recognition.start();
    } catch (error) {
      console.error(
        "PAIOS COMMAND VOICE START ERROR:",
        error
      );

      setIsCommandListening(false);
      commandRecognitionRef.current = null;
    }
  }

  async function speakPAIOS(text) {
    const cleanText = String(text || "").trim();
    if (!cleanText) return;
    try {
      if (audioRef.current) { try { audioRef.current.pause(); } catch {} }
      if (audioUrlRef.current) { URL.revokeObjectURL(audioUrlRef.current); audioUrlRef.current = null; }
      const response = await fetch(`${API_BASE}/speak`, { method: "POST", headers: { Accept: "audio/mpeg", "Content-Type": "application/json" }, body: JSON.stringify({ text: cleanText }) });
      if (!response.ok) { let detail = `PAIOS voice request failed with HTTP ${response.status}.`; try { const payload = await response.json(); detail = payload?.detail || payload?.message || detail; } catch {} throw new Error(detail); }
      const blob = await response.blob();
      if (!blob.size) throw new Error("PAIOS received empty voice audio.");
      const audioUrl = URL.createObjectURL(blob);
      audioUrlRef.current = audioUrl;
      const audio = new Audio(audioUrl);
      audio.preload = "auto";
      audioRef.current = audio;
      audio.onplay = () => setIsSpeaking(true);
      audio.onended = () => { setIsSpeaking(false); if (audioUrlRef.current === audioUrl) { URL.revokeObjectURL(audioUrl); audioUrlRef.current = null; } if (audioRef.current === audio) audioRef.current = null; };
      audio.onerror = () => { setIsSpeaking(false); if (audioUrlRef.current === audioUrl) { URL.revokeObjectURL(audioUrl); audioUrlRef.current = null; } if (audioRef.current === audio) audioRef.current = null; };
      await audio.play();
    } catch (error) { setIsSpeaking(false); console.error("PAIOS VOICE OUTPUT ERROR:", error); addQuestionMessage("error", error?.message || "PAIOS could not play the voice response."); }
  }

  React.useEffect(() => () => {
    if (commandRecognitionRef.current) {
      try {
        commandRecognitionRef.current.abort();
      } catch {}
    }

    if (recognitionRef.current) { try { recognitionRef.current.abort(); } catch {} }
    if (audioRef.current) { try { audioRef.current.pause(); } catch {} }
    if (audioUrlRef.current) URL.revokeObjectURL(audioUrlRef.current);

    if (eventSourceRef.current) {
      try {
        eventSourceRef.current.close();
      } catch {}
      eventSourceRef.current = null;
    }
  }, []);

  async function askQuestion(questionText = question) {
    const cleanQuestion = String(questionText || "").trim();

    if (!cleanQuestion || questionBusy) return;

    setQuestion(cleanQuestion);
    addQuestionMessage("user", cleanQuestion);
    setQuestion("");
    setQuestionBusy(true);

    try {
      const response = await fetch(`${API_BASE}/ask`, {
        method: "POST",
        headers: {
          Accept: "application/json",
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ question: cleanQuestion }),
      });

      const raw = await response.text();
      let payload = raw;

      try {
        payload = raw ? JSON.parse(raw) : {};
      } catch {
        // Plain text is accepted as a valid answer.
      }

      if (!response.ok) {
        const detail =
          payload?.detail ||
          payload?.answer ||
          payload?.message ||
          `Q&A request failed with HTTP ${response.status}.`;
        throw new Error(String(detail));
      }

      const answer =
        typeof payload === "string"
          ? payload
          : payload?.answer ||
            payload?.response ||
            payload?.message ||
            payload?.text ||
            payload?.content ||
            "PAIOS returned an empty answer.";

      addQuestionMessage("agent", answer);
      await speakPAIOS(answer);
    } catch (error) {
      addQuestionMessage(
        "error",
        error?.message || "PAIOS could not answer the question."
      );
    } finally {
      setQuestionBusy(false);
    }
  }

  function handleQuestionKeyDown(event) {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      askQuestion();
    }
  }

  function extractData(payload) {
    if (!payload || typeof payload !== "object") {
      return {};
    }

    return payload;
  }

  function applyEvent(eventName, payload) {
    const data = extractData(payload);

    const event = String(
      eventName ||
        data.event ||
        data.type ||
        data.stage ||
        ""
    ).toUpperCase();

    console.log("📥 PAIOS EVENT:", event, data);

    /* ============================================================
       PLAN
       ============================================================ */

    if (event === "PLAN") {
      const actions =
        data.actions ||
        data.plan ||
        data.steps ||
        data.data?.actions ||
        data.data?.steps ||
        [];

      const total =
        Number(
          data.total_steps ||
            data.totalSteps ||
            data.data?.total_steps ||
            data.data?.totalSteps ||
            (Array.isArray(actions) ? actions.length : 0)
        ) || 0;

      setState((prev) => ({
        ...prev,
        status: "executing",
        stage: "plan",
        totalSteps: total || prev.totalSteps,
        decision: "PLANNING",
        decisionText:
          data.message || "Execution plan generated.",
      }));

      addTimeline(
        "PLAN",
        data.message ||
          `Execution plan generated${
            total ? ` with ${total} step(s).` : "."
          }`
      );

      return;
    }

    /* ============================================================
       VALIDATION
       ============================================================ */

    if (
      event === "VALIDATE" ||
      event === "VALIDATION"
    ) {
      setState((prev) => ({
        ...prev,
        stage: "plan",
        decision: "VALIDATING",
        decisionText:
          data.message ||
          "Validating execution plan.",
      }));

      addTimeline(
        "VALIDATE",
        data.message ||
          "Execution plan validated."
      );

      return;
    }

    /* ============================================================
       EXECUTE
       ============================================================ */

    if (event === "EXECUTE") {
      const action =
        data.action ||
        data.current_action ||
        data.data?.action ||
        data.data?.current_action;

      const step =
        Number(
          data.step ||
            data.step_index ||
            data.current_step ||
            data.data?.step ||
            data.data?.step_index ||
            0
        ) || 0;

      const total =
        Number(
          data.total_steps ||
            data.totalSteps ||
            data.data?.total_steps ||
            data.data?.totalSteps ||
            0
        ) || 0;

      setState((prev) => ({
        ...prev,
        status: "executing",
        stage: "execute",
        currentStep:
          step || prev.currentStep,
        totalSteps:
          total || prev.totalSteps,
        decision: "EXECUTING",
        decisionText:
          data.message ||
          (action
            ? `Executing ${
                typeof action === "string"
                  ? action
                  : "next action"
              }.`
            : "Executing next action."),
      }));

      addTimeline(
        "EXECUTE",
        data.message ||
          (action
            ? `Executing ${
                typeof action === "string"
                  ? action
                  : "action"
              }.`
            : "Executing next action.")
      );

      return;
    }

    /* ============================================================
       OBSERVE
       ============================================================ */

    if (event === "OBSERVE") {
      const observation =
        data.observation ||
        data.message ||
        data.data?.observation ||
        data.data?.message;

      const currentUrl =
        data.current_url ||
        data.url ||
        data.data?.current_url ||
        data.data?.url;

      const pageTitle =
        data.page_title ||
        data.title ||
        data.data?.page_title ||
        data.data?.title;

      setState((prev) => ({
        ...prev,
        status: "executing",
        stage: "observe",

        observations: observation
          ? [
              ...prev.observations,
              String(observation),
            ]
          : prev.observations,

        currentUrl:
          currentUrl || prev.currentUrl,

        pageTitle:
          pageTitle || prev.pageTitle,

        decision: "OBSERVING",

        decisionText:
          data.message ||
          "Inspecting execution result.",
      }));

      addTimeline(
        "OBSERVE",
        data.message ||
          observation ||
          "Browser state observed."
      );

      return;
    }

    /* ============================================================
       EVALUATE
       ============================================================ */

    if (event === "EVALUATE") {
      setState((prev) => ({
        ...prev,
        status: "executing",
        stage: "evaluate",
        decision:
          data.status ||
          "EVALUATING",
        decisionText:
          data.reason ||
          data.message ||
          data.data?.reason ||
          "Evaluating the current agent state.",
      }));

      addTimeline(
        "EVALUATE",
        data.reason ||
          data.message ||
          "Evaluating next action."
      );

      return;
    }

    /* ============================================================
       RECOVERY / REPLAN
       ============================================================ */

    if (
      event === "REPLAN" ||
      event === "RECOVERY"
    ) {
      const replans =
        Number(
          data.replans_used ||
            data.replansUsed ||
            data.data?.replans_used ||
            data.data?.replansUsed ||
            0
        ) || 0;

      const retries =
        Number(
          data.retry_count ||
            data.retryCount ||
            data.data?.retry_count ||
            data.data?.retryCount ||
            0
        ) || 0;

      setState((prev) => ({
        ...prev,
        status: "executing",
        replans:
          replans || prev.replans,
        retries:
          retries || prev.retries,
        decision: event,
        decisionText:
          data.message ||
          data.reason ||
          `PAIOS ${event.toLowerCase()} in progress.`,
      }));

      addTimeline(
        event,
        data.message ||
          data.reason ||
          `PAIOS ${event.toLowerCase()} event received.`
      );

      return;
    }

    /* ============================================================
       COMPLETE
       ============================================================ */

    if (
      event === "COMPLETE" ||
      event === "COMPLETED" ||
      data.status === "completed" ||
      data.status === "complete"
    ) {
      const result =
        data.result ||
        data.data ||
        data;

      const currentStep =
        Number(
          data.current_step ||
            data.step ||
            data.data?.current_step ||
            data.data?.step ||
            state.totalSteps
        ) || state.totalSteps;

      const totalSteps =
        Number(
          data.total_steps ||
            data.totalSteps ||
            data.data?.total_steps ||
            data.data?.totalSteps ||
            state.totalSteps
        ) || state.totalSteps;

      const currentUrl =
        data.current_url ||
        data.url ||
        data.data?.current_url ||
        data.data?.url ||
        "";

      const pageTitle =
        data.page_title ||
        data.title ||
        data.data?.page_title ||
        data.data?.title ||
        "";

      setState((prev) => ({
        ...prev,

        status: "complete",

        stage: "complete",

        currentStep:
          currentStep || prev.currentStep,

        totalSteps:
          totalSteps || prev.totalSteps,

        currentUrl:
          currentUrl || prev.currentUrl,

        pageTitle:
          pageTitle || prev.pageTitle,

        decision: "COMPLETE",

        decisionText:
          data.message ||
          "Objective completed successfully.",

        error: "",

        result,
      }));

      addTimeline(
        "COMPLETE",
        data.message ||
          "Objective completed successfully."
      );

      return;
    }

    /* ============================================================
       ERROR
       ============================================================ */

    if (
      event === "ERROR" ||
      event === "FAILED" ||
      data.status === "failed" ||
      data.error
    ) {
      const message =
        data.error ||
        data.message ||
        data.data?.error ||
        "PAIOS execution failed.";

      setState((prev) => ({
        ...prev,
        status: "failed",
        decision: "FAILED",
        decisionText: message,
        error: message,
        result: data,
      }));

      addTimeline(
        "ERROR",
        message,
        true
      );

      return;
    }

    /* ============================================================
       GENERIC EVENT
       ============================================================ */

    if (event || data.message) {
      addTimeline(
        event || "EVENT",
        data.message ||
          JSON.stringify(data)
      );
    }
  }

  function processSSEBlock(block) {
    if (!block || !block.trim()) {
      return;
    }

    const lines =
      block.split(/\r?\n/);

    let eventName = "";
    const dataLines = [];

    for (const line of lines) {
      if (line.startsWith("event:")) {
        eventName =
          line.slice(6).trim();
      }

      if (line.startsWith("data:")) {
        dataLines.push(
          line.slice(5).trimStart()
        );
      }
    }

    if (!dataLines.length) {
      return;
    }

    const raw =
      dataLines.join("\n");

    let payload = raw;

    try {
      payload = JSON.parse(raw);
    } catch {
      payload = {
        message: raw,
      };
    }

    applyEvent(
      eventName,
      payload
    );
  }

  function handleCommandKeyDown(event) {
    if (event.key !== "Enter" || event.shiftKey) {
      return;
    }

    event.preventDefault();

    const command =
      typeof goal === "string"
        ? goal.trim()
        : "";

    if (!command || running) {
      return;
    }

    executeGoal(command);
  }

  async function executeGoal(goalText = null) {
    // Never allow a React event/object to become the execution goal.
    // Manual execution uses the current text state; voice execution
    // passes an explicit string command.
    const sourceGoal =
      typeof goalText === "string"
        ? goalText
        : goal;

    const cleanGoal =
      typeof sourceGoal === "string"
        ? sourceGoal.trim()
        : "";

    if (
      !cleanGoal ||
      cleanGoal === "[object Object]" ||
      cleanGoal === "undefined" ||
      cleanGoal === "null" ||
      running
    ) {
      console.error(
        "❌ PAIOS rejected invalid execution goal:",
        goalText
      );
      return;
    }

    if (goal !== cleanGoal) {
      setGoal(cleanGoal);
    }

    /* ------------------------------------------------------------
       Reset execution state
       ------------------------------------------------------------ */

    setRunning(true);

    setState({
      ...INITIAL_STATE,
      status: "executing",
      stage: "plan",
      goal: cleanGoal,
      decision: "PLANNING",
      decisionText:
        "Generating execution plan.",
    });

    addTimeline(
      "START",
      "PAIOS execution started."
    );

    const encodedGoal =
      encodeURIComponent(
        cleanGoal
      );

    const streamUrl =
      `${API_BASE}/execute/stream?goal=${encodedGoal}`;

    console.log(
      "🚀 PAIOS EXECUTION GOAL:",
      JSON.stringify(cleanGoal)
    );

    console.log(
      "📡 Connecting to PAIOS SSE:",
      streamUrl
    );

    const eventSource =
      new EventSource(
        streamUrl
      );

    eventSourceRef.current =
      eventSource;

    /* ------------------------------------------------------------
       Close stream
       ------------------------------------------------------------ */

    const closeStream = () => {
      try {
        eventSource.close();
      } catch {
        // Ignore close errors.
      }

      if (
        eventSourceRef.current ===
        eventSource
      ) {
        eventSourceRef.current =
          null;
      }

      setRunning(false);
    };

    /* ------------------------------------------------------------
       Connection opened
       ------------------------------------------------------------ */

    eventSource.onopen = () => {
      console.log(
        "✅ PAIOS SSE connection established"
      );

      setState((prev) => ({
        ...prev,
        decision: "CONNECTED",
        decisionText:
          "Connected to PAIOS execution stream.",
      }));

      addTimeline(
        "CONNECT",
        "Connected to PAIOS execution stream."
      );
    };

    /* ------------------------------------------------------------
       Standard SSE messages
       ------------------------------------------------------------ */

    eventSource.onmessage =
      (event) => {
        try {
          const payload =
            JSON.parse(
              event.data
            );

          console.log(
            "📥 SSE MESSAGE:",
            payload
          );

          applyEvent(
            payload.stage ||
              payload.event ||
              payload.type ||
              "",
            payload
          );
        } catch (error) {
          console.error(
            "❌ SSE parse error:",
            error,
            event.data
          );
        }
      };

    /* ------------------------------------------------------------
       IMPORTANT:
       Backend sends:

       event: agent
       data: {...}

       Therefore EventSource.onmessage alone is NOT enough.
       ------------------------------------------------------------ */

    eventSource.addEventListener(
      "agent",
      (event) => {
        try {
          const payload =
            JSON.parse(
              event.data
            );

          console.log(
            "📡 AGENT EVENT:",
            payload
          );

          applyEvent(
            payload.stage ||
              payload.event ||
              payload.type ||
              "",
            payload
          );
        } catch (error) {
          console.error(
            "❌ AGENT SSE parse error:",
            error,
            event.data
          );
        }
      }
    );

    /* ------------------------------------------------------------
       Connection error
       ------------------------------------------------------------ */

    eventSource.onerror =
      (error) => {
        console.error(
          "❌ PAIOS SSE ERROR:",
          error
        );

        /*
         * Very important:
         *
         * The backend may close the SSE connection
         * after COMPLETE.
         *
         * Do NOT overwrite COMPLETE with CONNECTION ERROR.
         */

        setState((prev) => {
          if (
            prev.status ===
              "complete" ||
            prev.stage ===
              "complete"
          ) {
            return prev;
          }

          return {
            ...prev,
            status: "failed",
            decision:
              "CONNECTION ERROR",
            decisionText:
              "Connection to PAIOS execution stream was lost.",
            error:
              "Connection to PAIOS execution stream was lost.",
          };
        });

        setRunning(
          (currentRunning) => {
            if (
              currentRunning
            ) {
              addTimeline(
                "ERROR",
                "Connection to PAIOS execution stream was lost.",
                true
              );
            }

            return false;
          }
        );

        closeStream();
      };
  }

  function stopExecution() {
    if (
      eventSourceRef.current
    ) {
      try {
        eventSourceRef.current.close();
      } catch {
        // Ignore.
      }

      eventSourceRef.current =
        null;
    }

    setRunning(false);

    setState((prev) => ({
      ...prev,
      status: "stopped",
      decision: "STOPPED",
      decisionText:
        "Execution stopped by user.",
    }));

    addTimeline(
      "STOP",
      "Execution stopped by user."
    );
  }

  function clearExecution() {
    if (running) {
      return;
    }

    setState({
      ...INITIAL_STATE,
      timeline: [],
      observations: [],
    });

    setGoal("");
  }

  const stageIndex =
    STAGES.findIndex(
      ([key]) =>
        key === state.stage
    );

  return (
    <div className="app-shell">

      {/* ========================================================
          TOP BAR
          ======================================================== */}

      <header className="topbar">

        <div className="brand">

          <div className="brand-mark">
            P
          </div>

          <div>
            <div className="brand-name">
              PAIOS
            </div>

            <div className="brand-subtitle">
              AUTONOMOUS INTELLIGENCE OPERATING SYSTEM
            </div>
          </div>

        </div>

        <div className="top-title">
          AI COMMAND CENTER
        </div>

        <div className="online">
          <span />
          ONLINE
        </div>

      </header>


      {/* ========================================================
          DASHBOARD
          ======================================================== */}

      <main className="dashboard">

        {/* ======================================================
            LEFT COLUMN
            ====================================================== */}

        <aside className="left-column">

          <Panel
            title="SYSTEM"
            code="SYS-01"
          >

            <div className="core-orbit">

              <div className="orbit orbit-a" />

              <div className="orbit orbit-b" />

              <div className="core-letter">
                P
              </div>

            </div>

            <div className="core-title">
              PAIOS CORE
            </div>

            <div className="core-status">
              OPERATIONAL
            </div>

            <div className="system-list">

              <SystemRow
                name="FASTAPI"
                value="ONLINE"
              />

              <SystemRow
                name="BROWSER"
                value="READY"
              />

              <SystemRow
                name="AGENT STATE"
                value="ACTIVE"
              />

              <SystemRow
                name="EVALUATOR"
                value="ACTIVE"
              />

            </div>

          </Panel>


          <Panel
            title="AGENT STATUS"
            code="AGT-02"
          >

            <div
              className={`large-status ${state.status}`}
            >
              {state.status.toUpperCase()}
            </div>

            <div className="status-message">
              {state.decisionText}
            </div>

            <div className="mini-label">

              TASK PROGRESS

              <span>
                {progress}%
              </span>

            </div>

            <div className="progress">

              <div
                style={{
                  width:
                    `${progress}%`,
                }}
              />

            </div>

          </Panel>


          <Panel
            title="TELEMETRY"
            code="TEL-03"
          >

            <div className="metric-grid">

              <Metric
                label="STEP"
                value={`${state.currentStep}/${state.totalSteps}`}
              />

              <Metric
                label="OBS"
                value={
                  state.observations.length
                }
              />

              <Metric
                label="RETRY"
                value={
                  state.retries
                }
              />

              <Metric
                label="REPLAN"
                value={
                  state.replans
                }
              />

            </div>

          </Panel>

        </aside>


        {/* ======================================================
            CENTER COLUMN
            ====================================================== */}

        <section className="center-column">

          <Panel
            title="AUTONOMOUS COMMAND INTERFACE"
            status={
              running
                ? "EXECUTING"
                : "READY"
            }
          >

            <h1>
              What should PAIOS accomplish?
            </h1>

            <div className="command-box">

              <span>
                &gt;
              </span>

              <textarea
                value={
                  typeof goal === "string"
                    ? goal
                    : ""
                }
                onChange={(event) => {
                  setGoal(
                    event.currentTarget.value
                  );
                }}
                onKeyDown={handleCommandKeyDown}
                disabled={running}
                spellCheck={false}
                autoComplete="off"
                autoCorrect="off"
                autoCapitalize="off"
                placeholder="Enter a command for PAIOS..."
              />

            </div>

            <div className="command-actions">

              <button
                type="button"
                className={`voice-input-button ${
                  isCommandListening ? "listening" : ""
                }`}
                onClick={startCommandVoiceInput}
                disabled={running}
                title={
                  isCommandListening
                    ? "Listening for a command..."
                    : "Speak a command to PAIOS"
                }
              >
                {isCommandListening
                  ? "🎙 LISTENING"
                  : "🎙 COMMAND"}
              </button>


              <button
                type="button"
                onClick={() =>
                  setGoal(
                    "Search for Python tutorials and click the first search result"
                  )
                }
              >
                SEARCH
              </button>

              <button
                type="button"
                onClick={() =>
                  setGoal(
                    "Open https://www.python.org"
                  )
                }
              >
                OPEN URL
              </button>

              <button
                type="button"
                onClick={() =>
                  setGoal(
                    "Open https://www.python.org then click Documentation"
                  )
                }
              >
                MULTI-STEP
              </button>

              <button
                type="button"
                className="clear-button"
                onClick={clearExecution}
                disabled={running}
              >
                CLEAR
              </button>

              <div className="execute-group">

                {running && (
                  <button
                    type="button"
                    className="stop-button"
                    onClick={
                      stopExecution
                    }
                  >
                    STOP
                  </button>
                )}

                <button
                  type="button"
                  className="execute-button"
                  onClick={() =>
                    executeGoal(
                      typeof goal === "string"
                        ? goal
                        : ""
                    )
                  }
                  disabled={
                    running ||
                    typeof goal !== "string" ||
                    !goal.trim()
                  }
                >
                  {running
                    ? "EXECUTING"
                    : "EXECUTE"}

                  <span>
                    →
                  </span>

                </button>

              </div>

            </div>

          </Panel>


          {/* ======================================================
              PAIOS QUESTION CONSOLE
              ====================================================== */}
          <Panel
            title="PAIOS QUESTION CONSOLE"
            status="AI"
          >
            <div className="question-messages">
              {questionMessages.map((message) => (
                <div
                  className={`question-message question-${message.role}`}
                  key={message.id}
                >
                  <div className="question-avatar">
                    {message.role === "user" ? "YOU" : message.role === "error" ? "!" : "AI"}
                  </div>
                  <div className="question-bubble">
                    <div className="question-name">
                      {message.role === "user" ? "YOU" : message.role === "error" ? "PAIOS / ERROR" : "PAIOS"}
                    </div>
                    <div className="question-text">{message.text}</div>
                    <div className="question-meta">{message.time}</div>
                  </div>
                </div>
              ))}
            </div>

            <div className="question-suggestions">
              <button
                type="button"
                onClick={() => askQuestion("What is Python?")}
                disabled={questionBusy}
              >
                WHAT IS PYTHON?
              </button>
              <button
                type="button"
                onClick={() => askQuestion("What is the difference between Java and Python?")}
                disabled={questionBusy}
              >
                JAVA vs PYTHON
              </button>
              <button
                type="button"
                onClick={() => askQuestion("Explain recursion in simple terms.")}
                disabled={questionBusy}
              >
                EXPLAIN RECURSION
              </button>
            </div>

            <div className="question-input-row">
              <textarea
                value={question}
                onChange={(event) => setQuestion(event.target.value)}
                onKeyDown={handleQuestionKeyDown}
                disabled={questionBusy}
                rows={2}
                spellCheck={false}
                placeholder="Ask PAIOS a question..."
              />
              <button
                type="button"
                className={`voice-input-button ${isListening ? "listening" : ""}`}
                onClick={startVoiceInput}
                disabled={questionBusy}
                title={isListening ? "Listening..." : "Speak to PAIOS"}
              >
                {isListening ? "🎙 LISTENING" : "🎙 VOICE"}
              </button>

              <button
                type="button"
                className={`question-send ${isSpeaking ? "speaking" : ""}`}
                onClick={() => askQuestion()}
                disabled={questionBusy || !question.trim()}
              >
                {questionBusy ? "THINKING" : isSpeaking ? "SPEAKING" : "ASK"}
                <span>→</span>
              </button>
            </div>

            <div className="question-hint">
              🎙 VOICE = SPEAK&nbsp;&nbsp; • &nbsp;&nbsp;ENTER = ASK&nbsp;&nbsp; • &nbsp;&nbsp;SHIFT+ENTER = NEW LINE
            </div>
          </Panel>

          <Panel
            title="CURRENT OBJECTIVE"
            code="OBJ-01"
          >

            <div className="objective">

              {state.goal ||
                "No active objective."}

            </div>

          </Panel>


          <Panel
            title="AUTONOMOUS EXECUTION"
            status={
              state.status.toUpperCase()
            }
          >

            <div className="stage-track">

              {STAGES.map(
                (
                  [
                    key,
                    label,
                    sub,
                  ],
                  index
                ) => {

                  const active =
                    index ===
                    stageIndex;

                  const done =
                    index <
                      stageIndex ||
                    state.status ===
                      "complete";

                  return (
                    <React.Fragment
                      key={key}
                    >

                      <div
                        className={`stage ${
                          active
                            ? "active"
                            : ""
                        } ${
                          done
                            ? "done"
                            : ""
                        }`}
                      >

                        <div className="stage-number">
                          {String(
                            index + 1
                          ).padStart(
                            2,
                            "0"
                          )}
                        </div>

                        <div>

                          <strong>
                            {label}
                          </strong>

                          <small>
                            {sub}
                          </small>

                        </div>

                      </div>

                      {index <
                        STAGES.length -
                          1 && (
                        <div className="stage-line" />
                      )}

                    </React.Fragment>
                  );
                }
              )}

            </div>

          </Panel>


          <Panel
            title="AGENT ACTIVITY"
            status="LIVE"
          >

            <div className="timeline">

              {state.timeline.length ===
              0 ? (
                <div className="empty">
                  No execution events yet.
                </div>
              ) : (
                [...state.timeline]
                  .reverse()
                  .map(
                    (item) => (
                      <div
                        className={`timeline-item ${
                          item.failed
                            ? "failed"
                            : ""
                        }`}
                        key={item.id}
                      >

                        <div className="timeline-dot" />

                        <div className="timeline-content">

                          <div className="timeline-head">

                            <strong>
                              {item.type}
                            </strong>

                            <span>
                              {item.time}
                            </span>

                          </div>

                          <div>
                            {item.message}
                          </div>

                        </div>

                      </div>
                    )
                  )
              )}

            </div>

          </Panel>

        </section>


        {/* ======================================================
            RIGHT COLUMN
            ====================================================== */}

        <aside className="right-column">

          <Panel
            title="LIVE BROWSER"
            status="CONNECTED"
          >

            <div className="browser-meta">

              <span>
                URL
              </span>

              <strong>
                {state.currentUrl ||
                  "—"}
              </strong>

              <span>
                PAGE
              </span>

              <strong>
                {state.pageTitle ||
                  "—"}
              </strong>

            </div>

            <div className="browser-window">

              <div className="browser-dots">
                <i />
                <i />
                <i />
              </div>

              <div className="browser-body">

                <div className="browser-icon">
                  ◉
                </div>

                <strong>
                  {state.currentUrl
                    ? "BROWSER ACTIVE"
                    : "BROWSER READY"}
                </strong>

                <span>
                  {state.currentUrl
                    ? "Navigation detected"
                    : "Waiting for navigation"}
                </span>

              </div>

            </div>

          </Panel>


          <Panel
            title="OBSERVATIONS"
            code="OBS-05"
          >

            <div className="observation-list">

              {state.observations.length ===
              0 ? (
                <div className="empty">
                  No observations recorded.
                </div>
              ) : (
                state.observations
                  .slice(-8)
                  .reverse()
                  .map(
                    (
                      item,
                      index
                    ) => (
                      <div
                        className="observation"
                        key={`${item}-${index}`}
                      >
                        {item}
                      </div>
                    )
                  )
              )}

            </div>

          </Panel>


          <Panel
            title="AGENT DECISION"
            code="DEC-06"
          >

            <div className="decision-orbit">
              <span>
                AI
              </span>
            </div>

            <div
              className={`decision-title ${state.status}`}
            >
              {state.decision}
            </div>

            <div className="decision-text">
              {state.decisionText}
            </div>

          </Panel>

        </aside>

      </main>

    </div>
  );
}


/* ================================================================
   PANEL
   ================================================================ */

function Panel({
  title,
  code,
  status,
  children,
}) {
  return (
    <section className="panel">

      <div className="panel-heading">

        <div>
          {title}
        </div>

        {status ? (
          <span className="panel-status">
            {status}
          </span>
        ) : (
          <span className="panel-code">
            {code}
          </span>
        )}

      </div>

      <div className="panel-content">
        {children}
      </div>

    </section>
  );
}


/* ================================================================
   SYSTEM ROW
   ================================================================ */

function SystemRow({
  name,
  value,
}) {
  return (
    <div className="system-row">

      <span className="indicator" />

      <span>
        {name}
      </span>

      <small>
        {value}
      </small>

    </div>
  );
}


/* ================================================================
   METRIC
   ================================================================ */

function Metric({
  label,
  value,
}) {
  return (
    <div className="metric">

      <span>
        {label}
      </span>

      <strong>
        {value}
      </strong>

    </div>
  );
}


export default App;