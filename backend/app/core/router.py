from app.core.session_engine import session_engine
from app.core.engine_registry import engine_registry
from app.core.reasoner import reasoner
from app.core.memory_engine import memory_engine
from app.core.intent_engine import intent_engine


class Router:

    def process(self, user_message: str):

        print("\n========== ROUTER ==========")
        print(f"Incoming Message: {user_message}")

        # =================================================
        # SAFETY CHECK
        # =================================================

        if not isinstance(user_message, str):

            print(
                f"⚠️ Router received unexpected type: "
                f"{type(user_message).__name__}"
            )

            user_message = str(user_message)

        # =================================================
        # PREPARE SESSION
        # =================================================

        session_engine.prepare(user_message)

        # =================================================
        # DETECT INTENT
        # =================================================

        intent = intent_engine.detect_intent(user_message)

        print(f"Detected Intent: {intent}")

        # =================================================
        # FIND ENGINE
        # =================================================

        engine = engine_registry.get_engine(user_message)

        # =================================================
        # EXECUTE
        # =================================================

        if engine is None:

            print("No matching engine.")
            reply = reasoner.execute(user_message)

        else:

            print(
                f"Selected Engine: "
                f"{engine.__class__.__name__}"
            )

            # -------------------------------------------------
            # APPLICATION COMMANDS
            # -------------------------------------------------

            if intent.get("intent") == "OPEN_APPLICATION":

                print("Executing application intent...")

                reply = engine.execute(intent)

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

                reply = engine.execute(user_message)

        # =================================================
        # SAFETY CHECK RESPONSE
        # =================================================

        if reply is None:

            print(
                "⚠️ Engine returned None. "
                "Falling back to reasoner..."
            )

            reply = reasoner.execute(user_message)

        # =================================================
        # SAVE AI RESPONSE
        # =================================================

        memory_engine.remember_ai(reply)

        print(f"Final Reply: {reply}")
        print("============================\n")

        return reply


router = Router()