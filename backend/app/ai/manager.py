from app.ai.ollama_provider import generate_response

from app.memory.conversation import memory
from app.memory.extractor import extract_information
from app.memory.knowledge_manager import KnowledgeManager

knowledge = KnowledgeManager()


def ask_ai(user_message: str):

    # Save conversation
    memory.add_user_message(user_message)

    # Extract structured knowledge
    extract_information(user_message)

    message = user_message.lower().strip()

    # -------------------------
    # Name
    # -------------------------

    if "what is my name" in message or "what's my name" in message:

        name = knowledge.get_name()

        if name:
            reply = f"Your name is {name}."
        else:
            reply = "I do not know your name yet."

        memory.add_ai_message(reply)
        return reply

    # -------------------------
    # Projects
    # -------------------------

    if "what am i building" in message or "what project am i building" in message:

        projects = knowledge.get_projects()

        if projects:
            reply = f"You are building: {', '.join(projects)}."
        else:
            reply = "I don't know any projects yet."

        memory.add_ai_message(reply)
        return reply

    # -------------------------
    # Favorite Programming Language
    # -------------------------

    if "favorite programming language" in message:

        language = knowledge.get_preference("favorite_language")

        if language:
            reply = f"Your favorite programming language is {language}."
        else:
            reply = "I don't know your favorite programming language yet."

        memory.add_ai_message(reply)
        return reply

    # -------------------------
    # Nickname
    # -------------------------

    if "what do you call me" in message:

        nickname = knowledge.get_preference("nickname")

        if nickname:
            reply = f"I call you {nickname}."
        else:
            reply = "You haven't given me a preferred name yet."

        memory.add_ai_message(reply)
        return reply

    # -------------------------
    # AI Response
    # -------------------------

    reply = generate_response(user_message)

    memory.add_ai_message(reply)

    return reply