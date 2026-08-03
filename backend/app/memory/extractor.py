import re

from app.memory.knowledge_manager import KnowledgeManager

knowledge = KnowledgeManager()


def extract_information(user_message: str):

    text = user_message.strip()

    # -------------------------
    # Name Extraction
    # -------------------------

    name_patterns = [
        r"my name is (.+)",
        r"i am (.+)",
        r"i'm (.+)"
    ]

    for pattern in name_patterns:

        match = re.search(pattern, text, re.IGNORECASE)

        if match:

            name = match.group(1).strip().title()

            # Ignore sentences that are clearly not names
            if len(name.split()) <= 3:
                knowledge.save_name(name)

            break

    # -------------------------
    # Project Extraction
    # -------------------------

    project_patterns = [
        r"i am building (.+)",
        r"i'm building (.+)",
        r"my project is (.+)"
    ]

    for pattern in project_patterns:

        match = re.search(pattern, text, re.IGNORECASE)

        if match:

            project = match.group(1).strip()

            knowledge.add_project(project)

            break

    # -------------------------
    # Favorite Programming Language
    # -------------------------

    language_patterns = [
        r"my favorite programming language is (.+)",
        r"my favourite programming language is (.+)",
        r"i like programming in (.+)"
    ]

    for pattern in language_patterns:

        match = re.search(pattern, text, re.IGNORECASE)

        if match:

            language = match.group(1).strip().title()

            knowledge.save_preference(
                "favorite_language",
                language
            )

            break

    # -------------------------
    # Nickname
    # -------------------------

    nickname_patterns = [
        r"call me (.+)"
    ]

    for pattern in nickname_patterns:

        match = re.search(pattern, text, re.IGNORECASE)

        if match:

            nickname = match.group(1).strip().title()

            knowledge.save_preference(
                "nickname",
                nickname
            )

            break