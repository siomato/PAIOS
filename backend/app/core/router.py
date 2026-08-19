from app.core.session_engine import session_engine
from app.core.engine_registry import engine_registry
from app.core.reasoner import reasoner
from app.core.memory_engine import memory_engine
from app.core.intent_engine import intent_engine
from app.core.memory_context import memory_context


class Router:

    def process(self, user_message: str):

        print("\n========== ROUTER ==========")
        print(
            f"Incoming Message: "
            f"{user_message}"
        )

        # =================================================
        # SAFETY CHECK
        # =================================================

        if not isinstance(
            user_message,
            str
        ):

            print(
                f"⚠️ Router received unexpected type: "
                f"{type(user_message).__name__}"
            )

            user_message = str(
                user_message
            )

        # =================================================
        # PREPARE SESSION
        # =================================================

        session_engine.prepare(
            user_message
        )

        # =================================================
        # DETECT INTENT
        # =================================================

        intent = (
            intent_engine.detect_intent(
                user_message
            )
        )

        print(
            f"Detected Intent: {intent}"
        )

        # =================================================
        # FIND ENGINE
        # =================================================

        engine = (
            engine_registry.get_engine(
                user_message
            )
        )

        # =================================================
        # MEMORY CONTEXT
        # =================================================
        # Only build task-memory context for the
        # conversational Reasoner path. Specialized
        # engines, especially BrowserEngine, remain
        # completely untouched.

        recalled_context = ""

        if engine is None:

            try:

                recalled_context = (
                    memory_context.build(
                        user_message
                    )
                )

                if recalled_context:

                    print(
                        "\n🧠 REASONER MEMORY CONTEXT"
                    )

                    print(
                        recalled_context
                    )

                else:

                    print(
                        "\n🧠 No relevant task memory."
                    )

            except Exception as memory_error:

                # Memory must never break the
                # normal reasoning path.
                recalled_context = ""

                print(
                    "⚠️ Memory context failed: "
                    f"{memory_error}"
                )

        # =================================================
        # EXECUTE
        # =================================================

        if engine is None:

            print(
                "No matching engine."
            )

            reply = reasoner.execute(
                user_message,
                recalled_context
            )

        else:

            print(
                f"Selected Engine: "
                f"{engine.__class__.__name__}"
            )

            # -------------------------------------------------
            # APPLICATION COMMANDS
            # -------------------------------------------------

            if (
                intent.get("intent")
                == "OPEN_APPLICATION"
            ):

                print(
                    "Executing application intent..."
                )

                reply = engine.execute(
                    intent
                )

            # -------------------------------------------------
            # EVERYTHING ELSE
            # -------------------------------------------------

            else:

                # IMPORTANT:
                # Engines such as BrowserEngine expect
                # the ORIGINAL STRING, not the intent dictionary.

                print(
                    "Executing engine with original "
                    "user message..."
                )

                reply = engine.execute(
                    user_message
                )

        # =================================================
        # SAFETY CHECK RESPONSE
        # =================================================

        if reply is None:

            print(
                "⚠️ Engine returned None. "
                "Falling back to reasoner..."
            )

            # If a specialized engine returned None,
            # build memory context here as well because
            # this is now becoming a reasoning request.
            fallback_context = ""

            try:

                fallback_context = (
                    memory_context.build(
                        user_message
                    )
                )

            except Exception as memory_error:

                print(
                    "⚠️ Fallback memory context failed: "
                    f"{memory_error}"
                )

            reply = reasoner.execute(
                user_message,
                fallback_context
            )

        # =================================================
        # SAVE AI RESPONSE
        # =================================================

        memory_engine.remember_ai(
            reply
        )

        print(
            f"Final Reply: {reply}"
        )

        print(
            "============================\n"
        )

        return reply


router = Router()