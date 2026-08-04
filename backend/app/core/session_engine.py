from app.core.memory_engine import memory_engine
from app.memory.ai_extractor import extract_facts
from app.core.knowledge_engine import knowledge_engine


class SessionEngine:

    def prepare(self, user_message: str):

        # Save conversation
        memory_engine.remember_user(user_message)

        # Extract facts
        facts = extract_facts(user_message)

        # Save extracted facts
        if facts.get("name"):
            knowledge_engine.save_name(facts["name"])

        if facts.get("nickname"):
            knowledge_engine.save_preference(
                "nickname",
                facts["nickname"]
            )

        if facts.get("favorite_language"):
            knowledge_engine.save_preference(
                "favorite_language",
                facts["favorite_language"]
            )

        if facts.get("project"):
            knowledge_engine.add_project(
                facts["project"])


session_engine = SessionEngine()