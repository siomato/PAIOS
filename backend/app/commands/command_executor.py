import time

from app.commands.command_schema import (
    PAIOSCommand,
    CommandType,
)

from app.tools.browser_tools import browser_tools


class CommandExecutor:

    # =========================================================
    # EXECUTE PAIOS COMMAND
    # =========================================================

    def execute(
        self,
        command: PAIOSCommand
    ):

        print(
            f"\n⚙️ Executing: {command.command}"
        )

        # =====================================================
        # OPEN
        # =====================================================

        if command.command == CommandType.OPEN:

            if not command.url:
                raise ValueError(
                    "OPEN command requires a URL."
                )

            return browser_tools.open_url(
                command.url
            )

        # =====================================================
        # OBSERVE
        # =====================================================

        if command.command == CommandType.OBSERVE:

            print(
                "\n========== OBSERVE =========="
            )

            return browser_tools.get_page()

        # =====================================================
        # READ
        # =====================================================

        if command.command == CommandType.READ:

            print(
                "\n========== READ =========="
            )

            return browser_tools.read_page()

        # =====================================================
        # FIND
        # =====================================================

        if command.command == CommandType.FIND:

            if not command.target:
                raise ValueError(
                    "FIND command requires a target."
                )

            return browser_tools.find(
                command.target
            )

        # =====================================================
        # CLICK
        # =====================================================

        if command.command == CommandType.CLICK:

            if not command.target:
                raise ValueError(
                    "CLICK command requires a target."
                )

            return browser_tools.click(
                command.target
            )

        # =====================================================
        # SEARCH
        # =====================================================

        if command.command == CommandType.SEARCH:

            if not command.query:
                raise ValueError(
                    "SEARCH command requires a query."
                )

            return browser_tools.search(
                command.query
            )

        # =====================================================
        # FILL
        # =====================================================

        if command.command == CommandType.FILL:

            if not command.target:
                raise ValueError(
                    "FILL command requires a target."
                )

            if command.text is None:
                raise ValueError(
                    "FILL command requires text."
                )

            return browser_tools.fill_from_command(
                command.target,
                command.text
            )

        # =====================================================
        # PRESS
        # =====================================================

        if command.command == CommandType.PRESS:

            if not command.key:
                raise ValueError(
                    "PRESS command requires a key."
                )

            return browser_tools.press_key(
                command.key
            )

        # =====================================================
        # WAIT
        # =====================================================

        if command.command == CommandType.WAIT:

            seconds = (
                command.seconds
                if command.seconds is not None
                else 1.0
            )

            if seconds < 0:
                raise ValueError(
                    "WAIT seconds cannot be negative."
                )

            time.sleep(seconds)

            return {
                "status": "success",
                "message": (
                    f"Waited {seconds} seconds."
                ),
                "seconds": seconds,
                "error": None,
            }

        # =====================================================
        # UNKNOWN COMMAND
        # =====================================================

        raise ValueError(
            f"Unsupported PAIOS command: "
            f"{command.command}"
        )


# =============================================================
# GLOBAL COMMAND EXECUTOR
# =============================================================

command_executor = CommandExecutor()