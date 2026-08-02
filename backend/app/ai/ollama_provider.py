import requests

from app.config import (
    OLLAMA_URL,
    AI_MODEL,
    SYSTEM_DESCRIPTION,
)


def generate_response(user_prompt: str):

    final_prompt = f"""
{SYSTEM_DESCRIPTION}

User:
{user_prompt}

Assistant:
"""

    response = requests.post(
        OLLAMA_URL,
        json={
            "model": AI_MODEL,
            "prompt": final_prompt,
            "stream": False
        }
    )

    data = response.json()

    return data["response"]