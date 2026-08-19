import json
from typing import List

from app.ai.ollama_provider import generate_command_response
from app.commands.command_schema import PAIOSCommand


class CommandTranslator:

    def _clean_response(self, raw_response: str) -> str:

        if not isinstance(raw_response, str):
            raise ValueError(
                "Ollama command response must be a string."
            )

        cleaned = raw_response.strip()

        if not cleaned:
            raise ValueError(
                "Ollama returned an empty command response."
            )

        # -----------------------------------------
        # Remove Markdown code fences
        # -----------------------------------------

        if cleaned.startswith("```"):

            lines = cleaned.splitlines()

            # Remove first line: ``` or ```json
            if lines and lines[0].strip().startswith("```"):
                lines = lines[1:]

            # Remove final ```
            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]

            cleaned = "\n".join(lines).strip()

        return cleaned

    def translate(
        self,
        user_command: str
    ) -> List[PAIOSCommand]:

        if not user_command or not user_command.strip():
            raise ValueError(
                "User command cannot be empty."
            )

        # -----------------------------------------
        # Ask Ollama to translate
        # -----------------------------------------

        raw_response = generate_command_response(
            user_command
        )

        print("\n========== RAW AI COMMAND RESPONSE ==========")
        print(raw_response)
        print("==============================================")

        # -----------------------------------------
        # Normalize model output
        # -----------------------------------------

        cleaned_response = self._clean_response(
            raw_response
        )

        print("\n========== CLEANED COMMAND RESPONSE ==========")
        print(cleaned_response)
        print("==============================================")

        # -----------------------------------------
        # Parse JSON
        # -----------------------------------------

        try:

            data = json.loads(
                cleaned_response
            )

        except json.JSONDecodeError as e:

            raise ValueError(
                f"Ollama returned invalid JSON: {e}"
            )

        # -----------------------------------------
        # Validate top-level structure
        # -----------------------------------------

        if not isinstance(data, list):

            raise ValueError(
                "Command translator must return "
                "a JSON list."
            )

        if not data:

            raise ValueError(
                "Command translator returned "
                "no commands."
            )

        # -----------------------------------------
        # Convert dictionaries into PAIOSCommand
        # -----------------------------------------

        commands = []

        for index, item in enumerate(data):

            if not isinstance(item, dict):

                raise ValueError(
                    f"Command at index {index} "
                    f"must be a JSON object."
                )

            try:

                command = PAIOSCommand(
                    **item
                )

            except Exception as e:

                raise ValueError(
                    f"Invalid PAIOS command at "
                    f"index {index}: {e}"
                )

            commands.append(command)

        return commands


command_translator = CommandTranslator()