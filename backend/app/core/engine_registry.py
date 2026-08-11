from app.core.knowledge_engine import knowledge_engine
from app.core.tool_engine import tool_engine
from app.core.browser_engine import browser_engine


class EngineRegistry:

    def __init__(self):

        self.engines = [
            knowledge_engine,
            tool_engine,
            browser_engine
        ]

    def get_engine(self, user_message: str):

        print("\n========== ENGINE REGISTRY ==========")
        print(f"Incoming Request : {user_message}")
        print("Checking available engines...\n")

        for engine in self.engines:

            engine_name = engine.__class__.__name__

            print(f"Checking {engine_name}...")

            # ---------------------------------
            # Verify engine interface
            # ---------------------------------

            can_handle = getattr(engine, "can_handle", None)

            if not callable(can_handle):

                print(
                    f"⚠️ {engine_name} does not implement can_handle()."
                )

                continue

            # ---------------------------------
            # Ask engine if it can handle request
            # ---------------------------------

            try:

                if can_handle(user_message):

                    print(f"✅ Selected: {engine_name}")
                    print("=====================================\n")

                    return engine

            except Exception as e:

                print(
                    f"⚠️ Error checking {engine_name}: {e}"
                )

                continue

        print("❌ No engine matched.")
        print("=====================================\n")

        return None


engine_registry = EngineRegistry()