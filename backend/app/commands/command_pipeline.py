from app.commands.command_translator import command_translator
from app.commands.command_executor import command_executor


class CommandPipeline:

    def execute(self, user_command: str):

        if not user_command or not user_command.strip():
            raise ValueError(
                "User command cannot be empty."
            )

        print("\n========== COMMAND PIPELINE ==========")
        print(f"USER: {user_command}")

        # ---------------------------------
        # 1. Translate natural language
        # ---------------------------------

        commands = command_translator.translate(
            user_command
        )

        print("\nAI COMMANDS:")

        for command in commands:
            print(command)

        # ---------------------------------
        # 2. Execute commands
        # ---------------------------------

        results = []

        for command in commands:

            print(
                f"\n⚙️ Executing: {command.command}"
            )

            result = command_executor.execute(
                command
            )

            results.append(result)

        print("\n========== PIPELINE COMPLETE ==========")

        return results


command_pipeline = CommandPipeline()