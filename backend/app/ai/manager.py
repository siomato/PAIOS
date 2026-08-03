from app.ai.ollama_provider import generate_response
from app.memory.conversation import memory


def ask_ai(user_message: str):

    memory.add_user_message(user_message)

    reply = generate_response(user_message)

    memory.add_ai_message(reply)

    return reply