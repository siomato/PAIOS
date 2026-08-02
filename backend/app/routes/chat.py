from fastapi import APIRouter
from app.ai.manager import ask_ai

router = APIRouter()


@router.post("/chat")
def chat(message: dict):

    user_message = message["message"]

    reply = ask_ai(user_message)

    return {
        "reply": reply
    }