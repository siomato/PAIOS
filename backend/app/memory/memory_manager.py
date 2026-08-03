import json
from pathlib import Path


class MemoryManager:

    def __init__(self):

        self.memory_file = Path("memory.json")

        self.history = []

        self.load_memory()

    def load_memory(self):

        if self.memory_file.exists():

            with open(self.memory_file, "r", encoding="utf-8") as file:

                data = json.load(file)

                self.history = data.get("history", [])

        else:

            self.history = []

    def save_memory(self):

        data = {
            "history": self.history
        }

        with open(self.memory_file, "w", encoding="utf-8") as file:

            json.dump(data, file, indent=4)

    def add_user_message(self, message: str):

        self.history.append({
            "role": "user",
            "content": message
        })

        self.save_memory()

    def add_ai_message(self, message: str):

        self.history.append({
            "role": "assistant",
            "content": message
        })

        self.save_memory()

    def get_history(self):

        return self.history

    def clear(self):

        self.history = []

        self.save_memory()