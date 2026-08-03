import requests

from app.memory.conversation import memory

from app.config import (
    OLLAMA_URL,
    AI_MODEL,
    SYSTEM_DESCRIPTION,
)


def generate_response(user_prompt: str):

    # -----------------------------
    # Debug: Print Memory
    # -----------------------------
    print("\n========== MEMORY ==========")
    print(memory.get_history())
    print("============================\n")

    # -----------------------------
    # Build Conversation History
    # -----------------------------
    history = ""

    for message in memory.get_history():

        if message["role"] == "user":
            history += f"User: {message['content']}\n"

        elif message["role"] == "assistant":
            history += f"PAIOS: {message['content']}\n"

    # -----------------------------
    # Final Prompt
    # -----------------------------
    final_prompt = f"""
{SYSTEM_DESCRIPTION}

You have persistent conversation memory.

The following is your memory from this conversation.

================ MEMORY ================

{history}

========================================

Rules:

- The conversation above is your memory.
- Treat every fact in memory as true unless corrected later.
- Never repeat the conversation history.
- Never explain your memory unless asked.
- If the answer already exists in memory, answer directly.
- If memory is insufficient, answer using your own reasoning.
- Remain completely in character as PAIOS.
- Never identify yourself as Phi-3, Microsoft, Ollama, or a language model.
- Speak like an advanced AI Operating System.
- Be calm, logical, concise, and confident.

Current User Message:

{user_prompt}

PAIOS:
"""

    # -----------------------------
    # Send Request to Ollama
    # -----------------------------
    response = requests.post(
        OLLAMA_URL,
        json={
            "model": AI_MODEL,
            "prompt": final_prompt,
            "stream": False
        }
    )

    response.raise_for_status()

    data = response.json()

    reply = data["response"].strip()

    return reply