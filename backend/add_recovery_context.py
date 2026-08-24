from pathlib import Path


path = Path("app/memory/knowledge_manager.py")

text = path.read_text(
    encoding="utf-8"
)


marker = """    # =================================================
    # GET TASKS
    # =================================================

    def get_tasks(self):
"""


method = '''    # =================================================
    # TASK RECOVERY CONTEXT
    # =================================================

    def get_task_recovery_context(
        self,
        query,
        limit=5
    ):
        """
        Return previous task attempts that may help
        recover or improve a new execution.
        """

        if not isinstance(
            query,
            str
        ):

            return []

        query = query.strip()

        if not query:

            return []

        try:

            limit = max(
                1,
                int(limit)
            )

        except (
            TypeError,
            ValueError
        ):

            limit = 5

        matches = self.find_tasks(
            query,
            limit=limit
        )

        recovery_context = []

        for task in matches:

            if not isinstance(
                task,
                dict
            ):

                continue

            status = str(
                task.get(
                    "status",
                    ""
                )
            ).strip().lower()

            if status not in {
                "failed",
                "running",
                "recovered"
            }:

                continue

            recovery_context.append(
                {
                    "task":
                        task.get(
                            "task",
                            ""
                        ),

                    "status":
                        status,

                    "steps":
                        int(
                            task.get(
                                "steps",
                                0
                            )
                            or 0
                        ),

                    "replans_used":
                        int(
                            task.get(
                                "replans_used",
                                0
                            )
                            or 0
                        ),

                    "timestamp":
                        task.get(
                            "timestamp"
                        ),

                    "occurrences":
                        int(
                            task.get(
                                "occurrences",
                                1
                            )
                            or 1
                        )
                }
            )

        return recovery_context


'''


if text.count(marker) != 1:

    raise RuntimeError(
        "Expected exactly one GET TASKS "
        "insertion point, found "
        f"{text.count(marker)}."
    )


if "def get_task_recovery_context(" in text:

    raise RuntimeError(
        "Recovery context method already exists."
    )


text = text.replace(
    marker,
    method + marker,
    1
)


path.write_text(
    text,
    encoding="utf-8"
)


print(
    "Task recovery context added successfully."
)