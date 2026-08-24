from app.qa_router import router as qa_router
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from app.tts_router import router as tts_router

import json
import queue
import threading
import time

from app.core.agent_controller import agent_controller


# ============================================================
# PAIOS APPLICATION
# ============================================================

app = FastAPI(
    title="PAIOS",
    version="0.2.0"
)


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5173",
        "http://localhost:5173",
        "http://127.0.0.1:5500",
        "http://localhost:5500",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(qa_router)
app.include_router(tts_router)



# ============================================================
# REQUEST MODEL
# ============================================================

class ExecuteRequest(BaseModel):

    goal: str


# ============================================================
# ROOT
# ============================================================

@app.get("/")
def root():

    return {
        "system": "PAIOS",
        "status": "ONLINE",
        "version": "0.2.0"
    }


# ============================================================
# HEALTH
# ============================================================

@app.get("/health")
def health():

    return {
        "system": "PAIOS",
        "status": "healthy"
    }


# ============================================================
# SERIALIZE AGENT STATE
# ============================================================

def serialize_state(
    state
):

    if state is None:

        return None

    try:

        return state.snapshot()

    except Exception:

        return {

            "status": getattr(
                state,
                "status",
                None
            ),

            "user_goal": getattr(
                state,
                "user_goal",
                None
            ),

            "current_step": getattr(
                state,
                "current_step",
                0
            ),

            "current_url": getattr(
                state,
                "current_url",
                None
            ),

            "page_title": getattr(
                state,
                "page_title",
                None
            ),

            "current_plan": getattr(
                state,
                "current_plan",
                []
            ),

            "completed_steps": getattr(
                state,
                "completed_steps",
                []
            ),

            "observations": getattr(
                state,
                "observations",
                []
            ),

            "failed_step": getattr(
                state,
                "failed_step",
                None
            ),

            "last_error": getattr(
                state,
                "last_error",
                None
            ),

            "retry_count": getattr(
                state,
                "retry_count",
                0
            ),

            "replans_used": getattr(
                state,
                "replans_used",
                0
            ),

            "replan_history": getattr(
                state,
                "replan_history",
                []
            )

        }


# ============================================================
# NORMAL EXECUTE
#
# Keeps your existing API working.
# ============================================================

@app.post("/execute")
def execute_agent(
    request: ExecuteRequest
):

    goal = request.goal.strip()


    # --------------------------------------------------------
    # Validate
    # --------------------------------------------------------

    if not goal:

        return {

            "status":
                "failed",

            "error":
                "Goal cannot be empty."

        }


    print()

    print(
        "=" * 70
    )

    print(
        "🚀 PAIOS EXECUTION"
    )

    print(
        "=" * 70
    )

    print(
        f"Goal: {goal}"
    )

    print(
        "=" * 70
    )


    # --------------------------------------------------------
    # Execute autonomous agent
    # --------------------------------------------------------

    try:

        result = agent_controller.run(
            goal
        )

    except Exception as error:

        print(
            f"❌ Agent execution failed: {error}"
        )

        return {

            "status":
                "failed",

            "error":
                str(error)

        }


    # --------------------------------------------------------
    # Serialize state
    # --------------------------------------------------------

    if isinstance(
        result,
        dict
    ):

        state = result.get(
            "state"
        )

        if state is not None:

            result["state"] = (
                serialize_state(
                    state
                )
            )


    print()

    print(
        "✅ PAIOS EXECUTION FINISHED"
    )

    print(
        "=" * 70
    )


    return result


# ============================================================
# LIVE EXECUTION STREAM
#
# GET /execute/stream?goal=...
#
# Uses Server-Sent Events.
# ============================================================

@app.get("/execute/stream")
def execute_stream(
    goal: str
):

    goal = goal.strip()


    # --------------------------------------------------------
    # Validate
    # --------------------------------------------------------

    if not goal:

        def empty_error():

            payload = {

                "stage":
                    "failed",

                "message":
                    "Goal cannot be empty.",

                "data":
                    {}

            }

            yield (
                "event: agent\n"
                f"data: {json.dumps(payload)}\n\n"
            )


        return StreamingResponse(
            empty_error(),
            media_type="text/event-stream"
        )


    # --------------------------------------------------------
    # Event queue
    # --------------------------------------------------------

    events = queue.Queue()


    finished = threading.Event()


    # --------------------------------------------------------
    # Agent callback
    # --------------------------------------------------------

    def event_callback(
        event
    ):

        try:

            events.put(
                event
            )

        except Exception as error:

            print(
                "⚠️ Could not queue "
                f"agent event: {error}"
            )


    # --------------------------------------------------------
    # Run agent in background thread
    # --------------------------------------------------------

    def run_agent():

        try:

            print()

            print(
                "=" * 70
            )

            print(
                "📡 PAIOS LIVE STREAM STARTED"
            )

            print(
                f"Goal: {goal}"
            )

            print(
                "=" * 70
            )


            result = agent_controller.run(
                goal,
                event_callback=event_callback
            )


            # ------------------------------------------------
            # Serialize final state
            # ------------------------------------------------

            if isinstance(
                result,
                dict
            ):

                state = result.get(
                    "state"
                )

                if state is not None:

                    result["state"] = (
                        serialize_state(
                            state
                        )
                    )


            # ------------------------------------------------
            # FINAL EVENT
            # ------------------------------------------------

            events.put({

                "stage":
                    "result",

                "message":
                    "PAIOS execution finished.",

                "data":
                    result

            })


        except Exception as error:

            print(
                "❌ Live agent execution failed: "
                f"{error}"
            )


            events.put({

                "stage":
                    "failed",

                "message":
                    str(error),

                "data": {

                    "error":
                        str(error)

                }

            })


        finally:

            finished.set()


    worker = threading.Thread(
        target=run_agent,
        daemon=True
    )

    worker.start()


    # --------------------------------------------------------
    # SSE generator
    # --------------------------------------------------------

    def event_generator():

        # -----------------------------------------------
        # Initial connection event
        # -----------------------------------------------

        initial_payload = {

            "stage":
                "connected",

            "message":
                "Connected to PAIOS live execution.",

            "data": {

                "goal":
                    goal

            }

        }


        yield (
            "event: agent\n"
            f"data: {json.dumps(initial_payload)}\n\n"
        )


        # -----------------------------------------------
        # Stream events
        # -----------------------------------------------

        while True:

            try:

                event = events.get(
                    timeout=0.5
                )


                payload = {

                    "stage":
                        event.get(
                            "stage",
                            "unknown"
                        ),

                    "message":
                        event.get(
                            "message",
                            ""
                        ),

                    "data":
                        event.get(
                            "data",
                            {}
                        )

                }


                yield (
                    "event: agent\n"
                    f"data: {json.dumps(payload, default=str)}\n\n"
                )


                # ---------------------------------------
                # Result terminates stream
                # ---------------------------------------

                if (
                    payload["stage"]
                    ==
                    "result"
                ):

                    break


                # ---------------------------------------
                # Failed event can terminate if worker
                # is already finished.
                # ---------------------------------------

                if (
                    payload["stage"]
                    ==
                    "failed"
                    and
                    finished.is_set()
                ):

                    break


            except queue.Empty:

                # ---------------------------------------
                # Keep SSE connection alive.
                # ---------------------------------------

                yield (
                    ": heartbeat\n\n"
                )


                if finished.is_set():

                    # Give queued events a tiny chance
                    # to be consumed.
                    time.sleep(
                        0.05
                    )


                    if events.empty():

                        break


    return StreamingResponse(

        event_generator(),

        media_type=
            "text/event-stream",

        headers={

            "Cache-Control":
                "no-cache",

            "Connection":
                "keep-alive",

            "X-Accel-Buffering":
                "no"

        }

    )