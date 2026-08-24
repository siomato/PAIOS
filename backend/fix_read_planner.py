from pathlib import Path


path = Path("app/core/action_planner.py")

text = path.read_text(
    encoding="utf-8"
)


old = """            if lower_step in (
                "read",
                "read page",
                "read the page",
                "read current page",
            ):
"""


new = """            if lower_step in (
                "read",
                "read page",
                "read the page",
                "read current page",
                "read the current page",
                "read documentation",
                "read the documentation",
                "read current documentation",
                "read the current documentation",
            ):
"""


if text.count(old) != 1:

    raise RuntimeError(
        "Expected exactly one READ rule, found "
        f"{text.count(old)}."
    )


text = text.replace(
    old,
    new,
    1
)


path.write_text(
    text,
    encoding="utf-8"
)


print(
    "READ planner vocabulary updated successfully."
)