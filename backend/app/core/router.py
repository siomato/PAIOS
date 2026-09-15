from app.core.session_engine import session_engine
from app.core.engine_registry import engine_registry
from app.core.reasoner import reasoner
from app.core.memory_engine import memory_engine
from app.core.intent_engine import intent_engine
from app.core.memory_context import memory_context
from app.ai.ollama_provider import generate_qa_response
class Router:
    def process(self,user_message):
        message=str(user_message or '').strip()
        if not message:return ''
        try: session_engine.prepare(message)
        except Exception as e: print('session warning:',e)
        intent=intent_engine.detect_intent(message); engine=engine_registry.get_engine(message)
        # Fast path: ordinary chat bypasses the heavy router/reasoner path.
        if engine is None and intent.get('intent')=='CHAT':
            return generate_qa_response(message)
        if engine is not None:
            try:
                reply=engine.execute(message)
                if reply is not None:
                    try: memory_engine.remember_ai(reply)
                    except Exception: pass
                    return reply
            except Exception as e:
                print('Specialized engine failed:',e)
                raise
        ctx=''
        try: ctx=memory_context.build(message)
        except Exception: pass
        reply=reasoner.execute(message,ctx)
        try: memory_engine.remember_ai(reply)
        except Exception: pass
        return reply
router=Router()
