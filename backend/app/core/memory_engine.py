from app.memory.conversation import memory


class MemoryEngine:

    def remember_user(self, message):

        memory.add_user_message(message)

    def remember_ai(self, message):

        memory.add_ai_message(message)

    def history(self):

        return memory.get_history()

    def clear(self):

        memory.clear()


memory_engine = MemoryEngine()