from app.ai.ollama_provider import generate_response


def ask_ai(user_message: str):

    reply = generate_response(user_message)

    return reply