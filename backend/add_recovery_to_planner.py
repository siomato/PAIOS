from pathlib import Path


path = Path("app/core/agent_controller.py")

text = path.read_text(
    encoding="utf-8"
)


old = """        memory_matches = []

        try:

            memory_matches = self.knowledge.find_tasks(
                user_message
            )

            if not isinstance(
                memory_matches,
                list
            ):
                memory_matches = []

            print(
                "\\n🧠 MEMORY RECALL"
            )

            print(
                f"Relevant previous task(s): "
                f"{len(memory_matches)}"
            )

            for memory_item in memory_matches[:5]:

                if isinstance(
                    memory_item,
                    dict
                ):

                    print(
                        "  ↳ "
                        f"{memory_item.get('task', '')}"
                    )

        except Exception as memory_error:

            # Memory recall must never prevent planning.
            memory_matches = []

            print(
                "⚠️ Memory recall failed: "
                f"{memory_error}"
            )
"""


new = """        memory_matches = []

        recovery_context = []

        try:

            memory_matches = self.knowledge.find_tasks(
                user_message
            )

            if not isinstance(
                memory_matches,
                list
            ):
                memory_matches = []

            recovery_context = (
                self.knowledge.get_task_recovery_context(
                    user_message
                )
            )

            if not isinstance(
                recovery_context,
                list
            ):
                recovery_context = []

            print(
                "\\n🧠 MEMORY RECALL"
            )

            print(
                f"Relevant previous task(s): "
                f"{len(memory_matches)}"
            )

            for memory_item in memory_matches[:5]:

                if isinstance(
                    memory_item,
                    dict
                ):

                    print(
                        "  ↳ "
                        f"{memory_item.get('task', '')}"
                    )

            print(
                "🧠 RECOVERY CONTEXT"
            )

            print(
                f"Previous recoverable attempt(s): "
                f"{len(recovery_context)}"
            )

            for recovery_item in recovery_context[:5]:

                if isinstance(
                    recovery_item,
                    dict
                ):

                    print(
                        "  ↳ "
                        f"{recovery_item.get('status', '')}: "
                        f"{recovery_item.get('task', '')}"
                    )

        except Exception as memory_error:

            # Memory recall must never prevent planning.
            memory_matches = []
            recovery_context = []

            print(
                "⚠️ Memory recall failed: "
                f"{memory_error}"
            )
"""


if text.count(old) != 1:

    raise RuntimeError(
        "Expected exactly one MEMORY RECALL "
        "block, found "
        f"{text.count(old)}."
    )


if "recovery_context = []" in text:

    raise RuntimeError(
        "Recovery context integration already exists."
    )


text = text.replace(
    old,
    new,
    1
)


old_return = """            "memory_recall": memory_matches[:5],

            "error": None
"""


new_return = """            "memory_recall": memory_matches[:5],

            "recovery_context": recovery_context[:5],

            "error": None
"""


if text.count(old_return) != 1:

    raise RuntimeError(
        "Expected exactly one planning return "
        "block, found "
        f"{text.count(old_return)}."
    )


text = text.replace(
    old_return,
    new_return,
    1
)


path.write_text(
    text,
    encoding="utf-8"
)


print(
    "Recovery context integrated into "
    "create_plan() successfully."
)