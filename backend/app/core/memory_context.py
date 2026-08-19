from app.memory.knowledge_manager import KnowledgeManager


class MemoryContext:

    def __init__(self):

        self.knowledge = KnowledgeManager()

    # =================================================
    # BUILD CONTEXT
    # =================================================

    def build(self, user_message: str):

        if not isinstance(
            user_message,
            str
        ):
            return ""

        message = user_message.strip()

        if not message:
            return ""

        try:

            tasks = self.knowledge.find_tasks(
                message
            )

        except Exception as error:

            print(
                f"⚠️ Memory context retrieval failed: "
                f"{error}"
            )

            return ""

        if not tasks:

            return ""

        # Keep context deliberately small.
        # This prevents memory from becoming noisy
        # or consuming excessive prompt space.
        tasks = tasks[:5]

        lines = [
            "Relevant previous PAIOS task memory:"
        ]

        for task in tasks:

            if not isinstance(
                task,
                dict
            ):
                continue

            task_text = task.get(
                "task",
                ""
            )

            status = task.get(
                "status",
                "unknown"
            )

            steps = task.get(
                "steps",
                0
            )

            replans = task.get(
                "replans_used",
                0
            )

            if not task_text:
                continue

            lines.append(
                (
                    f"- Task: {task_text} | "
                    f"Status: {status} | "
                    f"Steps: {steps} | "
                    f"Replans: {replans}"
                )
            )

        if len(lines) == 1:

            return ""

        return "\n".join(
            lines
        )


memory_context = MemoryContext()