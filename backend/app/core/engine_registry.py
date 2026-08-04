"""
PAIOS Engine Registry

Maintains all available engines and selects the appropriate
engine to handle a user request.
"""

from app.core.knowledge_engine import knowledge_engine
from app.core.tool_engine import tool_engine


class EngineRegistry:

    def __init__(self):

        # Register all available engines here
        self.engines = [
            knowledge_engine,
            tool_engine,
        ]

    def get_engine(self, user_message: str):

        print("\n========== ENGINE REGISTRY ==========")
        print(f"Incoming Request : {user_message}")
        print("Checking available engines...\n")

        for engine in self.engines:

            print(f"Checking {engine.__class__.__name__}...")

            if engine.can_handle(user_message):

                print(f"✅ Selected: {engine.__class__.__name__}")
                print("=====================================\n")

                return engine

        print("❌ No engine matched.")
        print("➡ Falling back to Reasoner.")
        print("=====================================\n")

        return None

    def register(self, engine):

        self.engines.append(engine)

        print(f"Registered Engine: {engine.__class__.__name__}")


engine_registry = EngineRegistry()