from app.ai.ollama_provider import generate_response


class Reasoner:

    def execute(self, user_message: str):

        return generate_response(user_message)


reasoner = Reasoner()