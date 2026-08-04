class KeyboardInput:

    def process(self, message: str):

        return {
            "source": "keyboard",
            "data": message
        }


keyboard = KeyboardInput()