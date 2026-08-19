from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app.routes.chat import router
from app.core.agent_controller import agent_controller


# ============================================================
# PAIOS FASTAPI APPLICATION
# ============================================================

app = FastAPI(
    title="PAIOS",
    version="0.1.0"
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
# EXISTING CHAT ROUTER
# ============================================================

app.include_router(router)


# ============================================================
# EXECUTE REQUEST
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
        "version": "0.1.0"
    }


# ============================================================
# HEALTH
# ============================================================

@app.get("/health")
def health():

    return {
        "status": "healthy",
        "system": "PAIOS"
    }


# ============================================================
# EXECUTE AUTONOMOUS AGENT
# ============================================================

@app.post("/execute")
def execute_agent(
    request: ExecuteRequest
):

    goal = request.goal.strip()

    # --------------------------------------------------------
    # Validate goal
    # --------------------------------------------------------

    if not goal:

        return {
            "status": "failed",
            "error": "Goal cannot be empty."
        }

    print()
    print("=" * 60)
    print("🚀 PAIOS API EXECUTION")
    print("=" * 60)

    print(
        f"Goal: {goal}"
    )

    # --------------------------------------------------------
    # RUN AGENT
    # --------------------------------------------------------

    try:

        result = agent_controller.run(
            goal
        )

    except Exception as e:

        print(
            f"❌ Agent execution failed: {e}"
        )

        return {
            "status": "failed",
            "error": str(e)
        }

    # --------------------------------------------------------
    # SERIALIZE AGENT STATE
    # --------------------------------------------------------

    if isinstance(result, dict):

        state = result.get("state")

        if state is not None:

            try:

                result["state"] = state.snapshot()

            except Exception as e:

                print(
                    f"⚠️ Could not serialize AgentState: {e}"
                )

                result["state"] = {

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

                    "current_plan": getattr(
                        state,
                        "current_plan",
                        []
                    ),

                    "current_step": getattr(
                        state,
                        "current_step",
                        None
                    ),

                    "completed_steps": getattr(
                        state,
                        "completed_steps",
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

                    "observations": getattr(
                        state,
                        "observations",
                        []
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

    print()
    print("✅ PAIOS API EXECUTION FINISHED")
    print("=" * 60)

    return result