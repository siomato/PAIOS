from app.core.knowledge_engine import knowledge_engine
from app.core.tool_engine import tool_engine
from app.core.browser_engine import browser_engine
class EngineRegistry:
    def __init__(self): self.engines=[tool_engine,browser_engine,knowledge_engine]
    def get_engine(self,message):
        for e in self.engines:
            try:
                if e.can_handle(message): return e
            except Exception as ex: print(f'Engine check failed: {ex}')
        return None
engine_registry=EngineRegistry()
