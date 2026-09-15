from app.core.memory_engine import memory_engine
from app.memory.ai_extractor import extract_facts
from app.core.knowledge_engine import knowledge_engine


class SessionEngine:

    def prepare(
        self,
        user_message: str
    ):

        # =================================================
        # SAFETY CHECK
        # =================================================

        if not isinstance(
            user_message,
            str
        ):

            user_message = str(
                user_message
            )

        user_message = user_message.strip()

        if not user_message:

            print(
                "⚠️ SESSION: Empty user message."
            )

            return

        # =================================================
        # DETECT SIGN LANGUAGE INPUT
        # =================================================

        is_sign_language = (
            user_message.startswith(
                "[SIGN LANGUAGE]"
            )
        )

        # =================================================
        # SAVE CONVERSATION
        # =================================================

        print(
            "🟡 SESSION: Saving user message..."
        )

        try:

            memory_engine.remember_user(
                user_message
            )

        except Exception as error:

            print(
                "⚠️ SESSION: "
                f"Failed to save user message: {error}"
            )

        print(
            "🟢 SESSION: User message saved."
        )

        # =================================================
        # SIGN LANGUAGE PATH
        # =================================================

        if is_sign_language:

            print(
                "🤟 SESSION: "
                "Sign-language input detected."
            )

            print(
                "🤟 SESSION: "
                "Skipping fact extraction."
            )

            return

        # =================================================
        # NORMAL TEXT PATH
        # =================================================

        print(
            "🟡 SESSION: Extracting facts..."
        )

        try:

            facts = extract_facts(
                user_message
            )

        except Exception as error:

            print(
                "⚠️ SESSION: "
                f"Fact extraction failed: {error}"
            )

            return

        print(
            "🟢 SESSION: Fact extraction complete."
        )

        # =================================================
        # VALIDATE FACT RESULT
        # =================================================

        if not isinstance(
            facts,
            dict
        ):

            print(
                "⚠️ SESSION: "
                "Fact extractor returned invalid data."
            )

            return

        # =================================================
        # SAVE NAME
        # =================================================

        if facts.get(
            "name"
        ):

            try:

                knowledge_engine.save_name(
                    facts["name"]
                )

            except Exception as error:

                print(
                    "⚠️ SESSION: "
                    f"Failed to save name: {error}"
                )

        # =================================================
        # SAVE NICKNAME
        # =================================================

        if facts.get(
            "nickname"
        ):

            try:

                knowledge_engine.save_preference(
                    "nickname",
                    facts["nickname"]
                )

            except Exception as error:

                print(
                    "⚠️ SESSION: "
                    f"Failed to save nickname: {error}"
                )

        # =================================================
        # SAVE FAVORITE LANGUAGE
        # =================================================

        if facts.get(
            "favorite_language"
        ):

            try:

                knowledge_engine.save_preference(
                    "favorite_language",
                    facts["favorite_language"]
                )

            except Exception as error:

                print(
                    "⚠️ SESSION: "
                    f"Failed to save favorite language: {error}"
                )

        # =================================================
        # SAVE PROJECT
        # =================================================

        if facts.get(
            "project"
        ):

            try:

                knowledge_engine.add_project(
                    facts["project"]
                )

            except Exception as error:

                print(
                    "⚠️ SESSION: "
                    f"Failed to save project: {error}"
                )


# =============================================================
# DEFAULT INSTANCE
# =============================================================

session_engine = SessionEngine()