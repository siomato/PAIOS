import time
import json
import requests

from app.memory.conversation import memory

from app.config import (
    OLLAMA_URL,
    AI_MODEL,
    SYSTEM_DESCRIPTION,
)


# ============================================================
# NORMAL PAIOS RESPONSE
# ============================================================

def generate_response(user_prompt: str):

    print("\n========== MEMORY ==========")
    print(memory.get_history())
    print("============================\n")

    history = ""

    for message in memory.get_history():

        if message["role"] == "user":
            history += (
                f"User: {message['content']}\n"
            )

        elif message["role"] == "assistant":
            history += (
                f"PAIOS: {message['content']}\n"
            )

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

    response = requests.post(
        OLLAMA_URL,
        json={
            "model": AI_MODEL,
            "prompt": final_prompt,
            "stream": False,
        },
        timeout=120,
    )

    response.raise_for_status()

    data = response.json()

    reply = data.get(
        "response",
        ""
    )

    if not isinstance(reply, str):
        raise RuntimeError(
            "Ollama returned a non-string response."
        )

    reply = reply.strip()

    if not reply:
        raise RuntimeError(
            "Ollama returned an empty response."
        )

    return reply


# ============================================================
# PAIOS COMMAND TRANSLATOR
# ============================================================

def generate_command_response(
    user_prompt: str,
    max_retries: int = 3,
):

    if not user_prompt or not user_prompt.strip():
        raise ValueError(
            "Command prompt cannot be empty."
        )

    # ========================================================
    # COMMAND TRANSLATION PROMPT
    # ========================================================

    prompt = f"""
You are the PAIOS Command Translator.

Your ONLY job is to convert the user's natural-language
instruction into PAIOS machine commands.

You are NOT the browser.

You do NOT execute anything.

You ONLY create the command plan.

DO NOT answer the user.
DO NOT explain anything.
DO NOT use Markdown.
DO NOT use code fences.
DO NOT add comments.
DO NOT add text before or after the JSON.

==================================================
ALLOWED COMMANDS
==================================================

open
observe
read
find
click
search
fill
press
wait

==================================================
COMMAND PARAMETERS
==================================================

open:
    url

observe:
    no parameters

read:
    no parameters

find:
    target

click:
    target

search:
    query

fill:
    target
    text

press:
    key

wait:
    seconds

==================================================
COMMAND MEANINGS
==================================================

OPEN
Open or navigate to a URL.

OBSERVE
Inspect the current page state.

FIND
Locate a specific target on the current page.
FIND does NOT click the target.

CLICK
Interact with a target.

READ
Read the current page.

SEARCH
Perform a search using the requested query.

FILL
Enter text into a specific input element.

PRESS
Press the requested keyboard key.

WAIT
Wait for the requested number of seconds.

==================================================
CRITICAL FILL RULE
==================================================

FILL ALWAYS REQUIRES TWO VALUES:

"target" = the input field that receives the text.

"text" = the actual text that must be entered.

Example:

User:
Fill the search box with Python asyncio tutorial

Correct:
[
    {{
        "command": "fill",
        "target": "search box",
        "text": "Python asyncio tutorial"
    }}
]

WRONG:
[
    {{
        "command": "fill",
        "text": "Python asyncio tutorial"
    }}
]

The text being entered MUST NEVER be used as
the target.

==================================================
CRITICAL PLANNING RULES
==================================================

1. Return ONLY valid JSON.

2. Return a JSON array.

3. Every command MUST contain a "command" field.

4. Use ONLY the allowed commands.

5. Never invent commands.

6. Never generate Python code.

7. Never generate Playwright code.

8. Never execute actions yourself.

9. Preserve URLs exactly.

10. Preserve requested target text exactly whenever possible.

11. Break compound instructions into sequential commands.

12. "Inspect the page" means OBSERVE.

13. "Find", "locate", "identify", or "look for"
    a specific target means FIND.

14. "Click" means CLICK.

15. FIND is a discovery operation.

16. FIND MUST NOT be replaced by CLICK.

17. CLICK is an interaction operation.

18. If the user asks to inspect a page and then
    click a specific target, produce:

    OBSERVE → FIND → CLICK

19. If the user asks to inspect a page and locate
    a target without clicking it, produce:

    OBSERVE → FIND

20. If the user only says "click Documentation"
    without asking for inspection or finding,
    CLICK may be used directly.

21. If a target must be located before interaction,
    FIND must appear before CLICK.

22. Preserve the user's requested execution order.

23. If the user asks to fill an input,
    FILL MUST contain both:

    target
    text

24. Never omit required command parameters.

25. Never use the FILL text as the FILL target.

26. Do not perform actions yourself.

27. Only describe the commands required to
    perform the user's instruction.

==================================================
EXAMPLES
==================================================

User:
Open https://www.python.org

Output:
[
    {{
        "command": "open",
        "url": "https://www.python.org"
    }}
]

--------------------------------------------------

User:
Click Documentation

Output:
[
    {{
        "command": "click",
        "target": "Documentation"
    }}
]

--------------------------------------------------

User:
Inspect the page and click Documentation

Output:
[
    {{
        "command": "observe"
    }},
    {{
        "command": "find",
        "target": "Documentation"
    }},
    {{
        "command": "click",
        "target": "Documentation"
    }}
]

--------------------------------------------------

User:
Inspect the page and find Documentation

Output:
[
    {{
        "command": "observe"
    }},
    {{
        "command": "find",
        "target": "Documentation"
    }}
]

--------------------------------------------------

User:
Open https://www.python.org, inspect the page,
find Documentation, and click it

Output:
[
    {{
        "command": "open",
        "url": "https://www.python.org"
    }},
    {{
        "command": "observe"
    }},
    {{
        "command": "find",
        "target": "Documentation"
    }},
    {{
        "command": "click",
        "target": "Documentation"
    }}
]

--------------------------------------------------

User:
Search Python tutorials

Output:
[
    {{
        "command": "search",
        "query": "Python tutorials"
    }}
]

--------------------------------------------------

User:
Fill the search box with Python asyncio tutorial

Output:
[
    {{
        "command": "fill",
        "target": "search box",
        "text": "Python asyncio tutorial"
    }}
]

--------------------------------------------------

User:
Fill the email field with test@example.com

Output:
[
    {{
        "command": "fill",
        "target": "email field",
        "text": "test@example.com"
    }}
]

--------------------------------------------------

User:
Type hello into the username field

Output:
[
    {{
        "command": "fill",
        "target": "username field",
        "text": "hello"
    }}
]

--------------------------------------------------

User:
Press Enter

Output:
[
    {{
        "command": "press",
        "key": "Enter"
    }}
]

--------------------------------------------------

User:
Wait 2 seconds

Output:
[
    {{
        "command": "wait",
        "seconds": 2
    }}
]

==================================================
USER INSTRUCTION
==================================================

{user_prompt}

==================================================
JSON OUTPUT
==================================================
"""

    # ========================================================
    # OLLAMA REQUEST WITH RETRIES
    # ========================================================

    last_error = None

    for attempt in range(
        1,
        max_retries + 1
    ):

        try:

            print(
                f"\n🤖 Command Translator → Ollama "
                f"(attempt {attempt}/{max_retries})"
            )

            response = requests.post(
                OLLAMA_URL,
                json={
                    "model": AI_MODEL,
                    "prompt": prompt,
                    "stream": False,
                },
                timeout=120,
            )

            response.raise_for_status()

            data = response.json()

            reply = data.get(
                "response",
                ""
            )

            if not isinstance(reply, str):
                raise RuntimeError(
                    "Ollama returned a non-string "
                    "command response."
                )

            reply = reply.strip()

            if not reply:
                raise RuntimeError(
                    "Ollama returned an empty "
                    "command response."
                )

            # =================================================
            # CLEAN OLLAMA MARKDOWN
            # =================================================

            cleaned = reply

            if cleaned.startswith(
                "```json"
            ):

                cleaned = cleaned[
                    len("```json"):
                ].strip()

            elif cleaned.startswith(
                "```"
            ):

                cleaned = cleaned[
                    len("```"):
                ].strip()

            if cleaned.endswith(
                "```"
            ):

                cleaned = cleaned[
                    :-3
                ].strip()

            # =================================================
            # VALIDATE JSON HERE
            # =================================================

            try:

                parsed = json.loads(
                    cleaned
                )

            except json.JSONDecodeError as exc:

                raise RuntimeError(
                    "Ollama returned invalid JSON: "
                    f"{exc}"
                )

            # =================================================
            # VALIDATE COMMAND ARRAY
            # =================================================

            if not isinstance(
                parsed,
                list
            ):

                raise RuntimeError(
                    "Command response must be "
                    "a JSON array."
                )

            # =================================================
            # VALIDATE COMMAND OBJECTS
            # =================================================

            allowed_commands = {
                "open",
                "observe",
                "read",
                "find",
                "click",
                "search",
                "fill",
                "press",
                "wait",
            }

            for item in parsed:

                if not isinstance(
                    item,
                    dict
                ):

                    raise RuntimeError(
                        "Every command must "
                        "be a JSON object."
                    )

                command_name = item.get(
                    "command"
                )

                if command_name not in allowed_commands:

                    raise RuntimeError(
                        f"Unsupported command: "
                        f"{command_name}"
                    )

                # ---------------------------------------------
                # FILL validation
                # ---------------------------------------------

                if command_name == "fill":

                    target = item.get(
                        "target"
                    )

                    text = item.get(
                        "text"
                    )

                    if not target:

                        raise RuntimeError(
                            "FILL command is missing "
                            "'target'."
                        )

                    if text is None:

                        raise RuntimeError(
                            "FILL command is missing "
                            "'text'."
                        )

            # =================================================
            # SUCCESS
            # =================================================

            print(
                "\n========== RAW AI COMMAND RESPONSE =========="
            )

            print(reply)

            print(
                "=============================================="
            )

            print(
                "\n========== CLEANED COMMAND RESPONSE =========="
            )

            print(cleaned)

            print(
                "=============================================="
            )

            return cleaned

        except (
            requests.RequestException,
            ValueError,
            RuntimeError,
        ) as exc:

            last_error = exc

            print(
                f"⚠️ Command translation attempt "
                f"{attempt} failed: {exc}"
            )

            if attempt < max_retries:

                time.sleep(1)

    raise RuntimeError(
        "Ollama command translation failed after "
        f"{max_retries} attempts: {last_error}"
    )