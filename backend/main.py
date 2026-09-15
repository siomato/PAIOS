from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app.tts_router import router as tts_router
from app.qa_router import router as qa_router
from app.routes.chat import router as chat_router
from app.core.agent_controller import agent_controller


# ============================================================
# PAIOS FASTAPI APPLICATION
# ============================================================

app = FastAPI(
    title="PAIOS",
    version="0.1.0",
    description="Personal AI Operating System",
)


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5500",
        "http://localhost:5500",

        "http://127.0.0.1:3000",
        "http://localhost:3000",

        "http://127.0.0.1:5173",
        "http://localhost:5173",
    ],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# ROUTERS
# ============================================================

app.include_router(qa_router)
app.include_router(tts_router)
app.include_router(chat_router)


# ============================================================
# REQUEST MODELS
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
        "version": "0.1.0",
    }


# ============================================================
# HEALTH
# ============================================================

@app.get("/health")
def health():
    return {
        "status": "healthy",
        "system": "PAIOS",
    }


# ============================================================
# AGENT STATE SERIALIZATION
# ============================================================

def serialize_agent_state(state):
    """
    Convert AgentState into a JSON-safe dictionary.

    PAIOS may return an AgentState object from the autonomous
    execution pipeline. This helper prevents FastAPI from
    failing when that object is not directly serializable.
    """

    if state is None:
        return None

    if isinstance(state, dict):
        return state

    return {
        "status": getattr(
            state,
            "status",
            None,
        ),

        "user_goal": getattr(
            state,
            "user_goal",
            None,
        ),

        "current_plan": getattr(
            state,
            "current_plan",
            [],
        ),

        "current_step": getattr(
            state,
            "current_step",
            None,
        ),

        "completed_steps": getattr(
            state,
            "completed_steps",
            [],
        ),

        "failed_step": getattr(
            state,
            "failed_step",
            None,
        ),

        "last_error": getattr(
            state,
            "last_error",
            None,
        ),

        "current_url": getattr(
            state,
            "current_url",
            None,
        ),

        "page_title": getattr(
            state,
            "page_title",
            None,
        ),

        "observations": getattr(
            state,
            "observations",
            [],
        ),

        "retry_count": getattr(
            state,
            "retry_count",
            0,
        ),

        "replans_used": getattr(
            state,
            "replans_used",
            0,
        ),

        "replan_history": getattr(
            state,
            "replan_history",
            [],
        ),
    }


# ============================================================
# EXECUTE AUTONOMOUS AGENT
# ============================================================

@app.post("/execute")
def execute_agent(request: ExecuteRequest):

    goal = request.goal.strip()

    # --------------------------------------------------------
    # VALIDATE GOAL
    # --------------------------------------------------------

    if not goal:
        return {
            "status": "failed",
            "error": "Goal cannot be empty.",
        }

    print()
    print("=" * 60)
    print("PAIOS API EXECUTION")
    print("=" * 60)
    print(f"Goal: {goal}")
    print()

    # --------------------------------------------------------
    # RUN AGENT
    # --------------------------------------------------------

    try:

        result = agent_controller.run(goal)

        # ----------------------------------------------------
        # NORMALIZE RESULT
        # ----------------------------------------------------

        if result is None:

            result = {
                "status": "completed",
                "message": "Agent completed without returning a result.",
            }

        elif not isinstance(result, dict):

            result = {
                "status": "completed",
                "result": str(result),
            }

        else:

            # Make a copy so we don't mutate an object owned
            # by another PAIOS subsystem.
            result = dict(result)

        # ----------------------------------------------------
        # SERIALIZE AGENT STATE
        # ----------------------------------------------------

        if "state" in result:

            result["state"] = serialize_agent_state(
                result["state"]
            )

    except Exception as exc:

        print()
        print("PAIOS EXECUTION ERROR")
        print(str(exc))
        print()

        return {
            "status": "failed",
            "error": str(exc),
            "goal": goal,
        }

    # --------------------------------------------------------
    # FINISHED
    # --------------------------------------------------------

    print()
    print("PAIOS API EXECUTION FINISHED")
    print("=" * 60)
    print()

    return result


# ============================================================
# SERVER STARTUP
# ============================================================

if __name__ == "__main__":

    import uvicorn

    print()
    print("=" * 60)
    print("PAIOS SERVER STARTING")
    print("=" * 60)
    print("System : PAIOS")
    print("Version: 0.1.0")
    print("Host   : 127.0.0.1")
    print("Port   : 8000")
    print()
    print("API    : http://127.0.0.1:8000")
    print("Health : http://127.0.0.1:8000/health")
    print("Docs   : http://127.0.0.1:8000/docs")
    print("=" * 60)
    print()

    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8000,
        reload=False,
    )