class ToolEngine:

    def can_handle(self, user_message: str):

        message = user_message.lower()

        return (
            message.startswith("open ")
            or message.startswith("create ")
            or message.startswith("delete ")
            or message.startswith("run ")
        )

    def execute(self, user_message: str):

        return (
            "Tool execution is not implemented yet.\n"
            f"Command: {user_message}"
        )


tool_engine = ToolEngine()