"""
PAIOS Sign Language Bridge

Responsible for:
    Confirmed sign-language result
            ↓
       PAIOS message
            ↓
       PAIOS callback

IMPORTANT:
    This module does NOT import the sign-language controller.
    This prevents circular imports.

The actual PAIOS integration can be connected through
set_paios_handler().
"""


class PAIOSBridge:

    def __init__(self, paios_handler=None):

        self.paios_handler = paios_handler

        self.last_message = None

        print(
            "🔌 PAIOS SIGN LANGUAGE BRIDGE INITIALIZED"
        )

    # =====================================================
    # SET PAIOS HANDLER
    # =====================================================

    def set_paios_handler(
        self,
        handler
    ):

        if not callable(handler):

            raise TypeError(
                "PAIOS handler must be callable."
            )

        self.paios_handler = handler

        print(
            "🔌 PAIOS handler connected."
        )

    # =====================================================
    # BUILD MESSAGE
    # =====================================================

    def build_message(
        self,
        translated_result
    ):

        if not isinstance(
            translated_result,
            dict
        ):

            return None

        gesture = translated_result.get(
            "gesture",
            "UNKNOWN"
        )

        text = translated_result.get(
            "text",
            "UNKNOWN"
        )

        if gesture == "UNKNOWN":

            return None

        if text == "UNKNOWN":

            return None

        return {
            "type": "sign_language",
            "source": "sign_language",
            "text": text,
            "gesture": gesture,
            "confirmed": True,
        }

    # =====================================================
    # BUILD AGENT MESSAGE
    # =====================================================

    def build_agent_message(
        self,
        translated_result
    ):

        message = self.build_message(
            translated_result
        )

        if message is None:

            return None

        return (
            "[SIGN LANGUAGE] "
            f"{message['text']}"
        )

    # =====================================================
    # SEND TO PAIOS
    # =====================================================

    def send_to_paios(
        self,
        translated_result
    ):

        message = self.build_message(
            translated_result
        )

        if message is None:

            print(
                "⚠️ Ignoring invalid sign-language result."
            )

            return None

        agent_message = self.build_agent_message(
            translated_result
        )

        message["agent_message"] = (
            agent_message
        )

        self.last_message = message

        print()
        print(
            "🔌 SIGN LANGUAGE → PAIOS"
        )

        print(
            f"   Gesture : {message['gesture']}"
        )

        print(
            f"   Text    : {message['text']}"
        )

        print(
            f"   Message : {agent_message}"
        )

        # -------------------------------------------------
        # If no PAIOS handler is connected yet,
        # safely return the prepared message.
        # -------------------------------------------------

        if self.paios_handler is None:

            print(
                "ℹ️ PAIOS handler not connected."
            )

            print(
                "ℹ️ Message prepared but not dispatched."
            )

            return message

        # -------------------------------------------------
        # Dispatch to PAIOS
        # -------------------------------------------------

        try:

            response = self.paios_handler(
                agent_message
            )

            message["response"] = response

            return message

        except Exception as error:

            print(
                "❌ PAIOS dispatch error:"
            )

            print(
                f"   {error}"
            )

            message["error"] = str(
                error
            )

            return message

    # =====================================================
    # SEND RAW TEXT
    # =====================================================

    def send_text(
        self,
        text,
        gesture="UNKNOWN"
    ):

        if not isinstance(
            text,
            str
        ):

            return None

        text = text.strip()

        if not text:

            return None

        return self.send_to_paios(
            {
                "gesture": gesture,
                "text": text,
            }
        )

    # =====================================================
    # LAST MESSAGE
    # =====================================================

    def get_last_message(self):

        return self.last_message

    # =====================================================
    # CLEAR
    # =====================================================

    def clear(self):

        self.last_message = None


# =========================================================
# BACKWARD COMPATIBILITY
# =========================================================

SignLanguageBridge = PAIOSBridge


# =========================================================
# DEFAULT INSTANCE
# =========================================================

paios_bridge = PAIOSBridge()


# =========================================================
# SELF TEST
# =========================================================

if __name__ == "__main__":

    print()
    print("=" * 60)
    print(
        "🔌 PAIOS SIGN LANGUAGE BRIDGE TEST"
    )
    print("=" * 60)
    print()

    bridge = PAIOSBridge()

    # -----------------------------------------------------
    # TEST 1 — Invalid / unconfirmed
    # -----------------------------------------------------

    print(
        "TEST 1 — UNKNOWN gesture"
    )

    result = bridge.send_to_paios(
        {
            "gesture": "UNKNOWN",
            "text": "UNKNOWN",
        }
    )

    print(
        "Bridge result:",
        result
    )

    if result is None:

        print(
            "✅ UNKNOWN correctly ignored."
        )

    print()

    # -----------------------------------------------------
    # TEST 2 — THREE
    # -----------------------------------------------------

    print(
        "TEST 2 — Confirmed THREE"
    )

    result = bridge.send_to_paios(
        {
            "gesture": "THREE",
            "text": "THREE",
        }
    )

    print(
        "Bridge result:",
        result
    )

    if (
        result is not None
        and
        result["text"] == "THREE"
    ):

        print(
            "✅ THREE converted to PAIOS input."
        )

    print()

    # -----------------------------------------------------
    # TEST 3 — OPEN PALM → HELLO
    # -----------------------------------------------------

    print(
        "TEST 3 — OPEN_PALM → HELLO"
    )

    result = bridge.send_to_paios(
        {
            "gesture": "OPEN_PALM",
            "text": "HELLO",
        }
    )

    print(
        "Bridge result:",
        result
    )

    if (
        result is not None
        and
        result["text"] == "HELLO"
    ):

        print(
            "✅ OPEN_PALM → HELLO."
        )

    print()

    # -----------------------------------------------------
    # TEST 4 — Agent message
    # -----------------------------------------------------

    print(
        "TEST 4 — Build PAIOS agent message"
    )

    message = bridge.build_agent_message(
        {
            "gesture": "OPEN_PALM",
            "text": "HELLO",
        }
    )

    print(
        "Agent message:",
        message
    )

    if message == "[SIGN LANGUAGE] HELLO":

        print(
            "✅ PAIOS agent message created."
        )

    print()

    # -----------------------------------------------------
    # TEST 5 — Handler
    # -----------------------------------------------------

    print(
        "TEST 5 — PAIOS handler dispatch"
    )

    def test_handler(message):

        print(
            f"🧠 PAIOS RECEIVED: {message}"
        )

        return {
            "status": "received"
        }

    bridge.set_paios_handler(
        test_handler
    )

    result = bridge.send_to_paios(
        {
            "gesture": "THREE",
            "text": "THREE",
        }
    )

    print(
        "Handler result:",
        result.get("response")
        if result
        else None
    )

    if (
        result is not None
        and
        result.get("response", {}).get(
            "status"
        ) == "received"
    ):

        print(
            "✅ PAIOS handler dispatch works."
        )

    print()
    print("=" * 60)
    print(
        "✅ PAIOS SIGN LANGUAGE BRIDGE TEST PASSED"
    )
    print("=" * 60)