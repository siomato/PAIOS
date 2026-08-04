import json
import requests

from app.config import (
    OLLAMA_URL,
    AI_MODEL,
)


def extract_facts(message: str):

    prompt = f"""
You are an information extraction engine.

Extract ONLY long-term useful information.

Return ONLY valid JSON.

Schema:

{{
    "name": null,
    "nickname": null,
    "favorite_language": null,
    "project": null
}}

If a field is unknown,
return null.

User message:

{message}
"""

    response = requests.post(

        OLLAMA_URL,

        json={
            "model": AI_MODEL,
            "prompt": prompt,
            "stream": False
        }

    )

    response.raise_for_status()

    data = response.json()

    try:

        return json.loads(data["response"])

    except Exception:

        return {
            "name": None,
            "nickname": None,
            "favorite_language": None,
            "project": None
        }