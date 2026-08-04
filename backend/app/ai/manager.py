from app.core.router import router


def ask_ai(user_message: str):

    return router.process(user_message)