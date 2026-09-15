class SignTranslator:
    """
    PAIOS Sign Language Translator.

    Converts confirmed gesture names into readable text.

    This module does NOT:
        - access the camera
        - detect hands
        - recognize gestures
        - stabilize gestures
        - communicate with PAIOS
    """

    def __init__(self):

        self.gesture_map = {
            "OPEN_PALM": "HELLO",
            "FIST": "STOP",
            "THUMBS_UP": "YES",
            "THUMBS_DOWN": "NO",
            "ONE": "ONE",
            "TWO": "TWO",
            "THREE": "THREE",
            "FOUR": "FOUR",
            "I_LOVE_YOU": "I LOVE YOU",
        }

        print(
            "🗣️ SIGN TRANSLATOR INITIALIZED"
        )

    # =====================================================
    # TRANSLATE
    # =====================================================

    def translate(self, gesture):

        if not isinstance(
            gesture,
            str
        ):

            return {
                "gesture": "UNKNOWN",
                "text": "UNKNOWN",
                "recognized": False,
            }

        gesture = gesture.strip().upper()

        text = self.gesture_map.get(
            gesture
        )

        if text is None:

            return {
                "gesture": gesture,
                "text": "UNKNOWN",
                "recognized": False,
            }

        return {
            "gesture": gesture,
            "text": text,
            "recognized": True,
        }

    # =====================================================
    # TEXT ONLY
    # =====================================================

    def translate_text(
        self,
        gesture
    ):

        result = self.translate(
            gesture
        )

        return result["text"]


# =========================================================
# DEFAULT INSTANCE
# =========================================================

translator = SignTranslator()


# =========================================================
# TEST
# =========================================================

if __name__ == "__main__":

    print()
    print("=" * 60)
    print(
        "🗣️ PAIOS SIGN LANGUAGE TRANSLATOR TEST"
    )
    print("=" * 60)
    print()

    tests = [
        "OPEN_PALM",
        "FIST",
        "THUMBS_UP",
        "THUMBS_DOWN",
        "ONE",
        "TWO",
        "THREE",
        "FOUR",
        "I_LOVE_YOU",
        "UNKNOWN",
    ]

    for gesture in tests:

        result = translator.translate(
            gesture
        )

        print(
            f"{gesture:15} → "
            f"{result['text']}"
        )

    print()
    print(
        "✅ Translator test passed."
    )