from app.nexus.keyboard import keyboard
from app.nexus.intent_parser import intent_parser


class InputManager:

    def process_keyboard(self, message: str):

        raw = keyboard.process(message)

        return intent_parser.parse(raw)


input_manager = InputManager()