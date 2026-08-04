from app.memory.knowledge_manager import KnowledgeManager

knowledge = KnowledgeManager()


class KnowledgeEngine:

    # -------------------------
    # Save Methods
    # -------------------------

    def save_name(self, name):
        knowledge.save_name(name)

    def save_preference(self, key, value):
        knowledge.save_preference(key, value)

    def add_project(self, project):
        knowledge.add_project(project)

    # -------------------------
    # Engine Interface
    # -------------------------

    def can_handle(self, user_message: str):

        message = user_message.lower()

        return (
            "what is my name" in message
            or "what's my name" in message
            or "what am i building" in message
            or "what project am i building" in message
        )

    def execute(self, user_message: str):

        message = user_message.lower()

        if "what is my name" in message or "what's my name" in message:

            name = knowledge.get_name()

            if name:
                return f"Your name is {name}."

            return "I do not know your name yet."

        if "what am i building" in message or "what project am i building" in message:

            projects = knowledge.get_projects()

            if projects:
                return f"You are building: {', '.join(projects)}."

            return "I don't know any projects yet."

        return None


knowledge_engine = KnowledgeEngine()