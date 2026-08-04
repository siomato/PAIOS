from app.core.session_engine import session_engine
from app.core.engine_registry import engine_registry
from app.core.reasoner import reasoner
from app.core.memory_engine import memory_engine


class Router:

    def process(self, user_message: str):
        print("========== ROUTER EXECUTED ==========")

        # -------------------------
        # Prepare Session
        # -------------------------

        session_engine.prepare(user_message)

        # -------------------------
        # Find Matching Engine
        # -------------------------

        engine = engine_registry.get_engine(user_message)

        # -------------------------
        # Execute Engine
        # -------------------------

        if engine:

            reply = engine.execute(user_message)

        else:

            reply = reasoner.execute(user_message)

        # -------------------------
        # Save AI Response
        # -------------------------

        memory_engine.remember_ai(reply)

        return reply


router = Router()