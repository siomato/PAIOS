from collections import deque


class GestureStabilizer:
    """
    PAIOS Gesture Stabilizer.

    Converts noisy frame-by-frame gesture predictions
    into a stable, confirmed gesture.

    Example:

        THREE
        THREE
        UNKNOWN
        THREE
        THREE

    becomes:

        THREE → CONFIRMED

    A confirmed gesture is emitted only once until
    the user changes the gesture or removes their hand.
    """

    def __init__(
        self,
        history_size=7,
        required_count=5,
        confidence_threshold=0.60,
    ):

        self.history_size = history_size
        self.required_count = required_count
        self.confidence_threshold = confidence_threshold

        self.history = deque(
            maxlen=history_size
        )

        self.last_confirmed = None
        self.last_emitted = None

        print(
            "⏳ GESTURE STABILIZER INITIALIZED"
        )

    # =====================================================
    # UPDATE
    # =====================================================

    def update(
        self,
        recognition_result
    ):

        # -------------------------------------------------
        # Invalid result
        # -------------------------------------------------

        if not isinstance(
            recognition_result,
            dict
        ):

            return self._empty_result()

        gesture = recognition_result.get(
            "gesture",
            "UNKNOWN"
        )

        confidence = float(
            recognition_result.get(
                "confidence",
                0.0
            )
        )

        recognized = recognition_result.get(
            "recognized",
            False
        )

        # -------------------------------------------------
        # Ignore weak / unknown predictions
        # -------------------------------------------------

        if (
            not recognized
            or
            gesture == "UNKNOWN"
            or
            confidence <
            self.confidence_threshold
        ):

            return {
                "gesture": (
                    self.last_confirmed
                    or "UNKNOWN"
                ),
                "confidence": confidence,
                "stable": False,
                "confirmed": False,
                "new": False,
            }

        # -------------------------------------------------
        # Add prediction
        # -------------------------------------------------

        self.history.append(
            gesture
        )

        # -------------------------------------------------
        # Find most common gesture
        # -------------------------------------------------

        counts = {}

        for item in self.history:

            counts[item] = (
                counts.get(item, 0) + 1
            )

        if not counts:

            return self._empty_result()

        dominant_gesture = max(
            counts,
            key=counts.get
        )

        dominant_count = counts[
            dominant_gesture
        ]

        # -------------------------------------------------
        # Not stable yet
        # -------------------------------------------------

        if (
            dominant_count <
            self.required_count
        ):

            return {
                "gesture": dominant_gesture,
                "confidence": confidence,
                "stable": False,
                "confirmed": False,
                "new": False,
                "count": dominant_count,
                "required": self.required_count,
            }

        # -------------------------------------------------
        # Stable gesture
        # -------------------------------------------------

        self.last_confirmed = (
            dominant_gesture
        )

        # -------------------------------------------------
        # Only emit once
        # -------------------------------------------------

        is_new = (
            dominant_gesture
            != self.last_emitted
        )

        if is_new:

            self.last_emitted = (
                dominant_gesture
            )

        return {
            "gesture": dominant_gesture,
            "confidence": confidence,
            "stable": True,
            "confirmed": True,
            "new": is_new,
            "count": dominant_count,
            "required": self.required_count,
        }

    # =====================================================
    # RESET
    # =====================================================

    def reset(self):

        self.history.clear()

        self.last_confirmed = None

        self.last_emitted = None

        print(
            "🔄 GESTURE STABILIZER RESET"
        )

    # =====================================================
    # HAND LOST
    # =====================================================

    def hand_lost(self):

        """
        Call this when no hand is detected.

        This allows the same gesture to be emitted again
        after the user removes their hand and shows it again.
        """

        self.history.clear()

        self.last_confirmed = None

        self.last_emitted = None

    # =====================================================
    # EMPTY RESULT
    # =====================================================

    @staticmethod
    def _empty_result():

        return {
            "gesture": "UNKNOWN",
            "confidence": 0.0,
            "stable": False,
            "confirmed": False,
            "new": False,
        }

    # =====================================================
    # STATUS
    # =====================================================

    def get_status(self):

        return {
            "history_size": len(
                self.history
            ),
            "max_history": self.history_size,
            "last_confirmed": (
                self.last_confirmed
            ),
            "last_emitted": (
                self.last_emitted
            ),
        }


# =========================================================
# DEFAULT INSTANCE
# =========================================================

stabilizer = GestureStabilizer()


# =========================================================
# SELF TEST
# =========================================================

if __name__ == "__main__":

    print()
    print("=" * 60)
    print(
        "⏳ PAIOS GESTURE STABILIZER TEST"
    )
    print("=" * 60)
    print()

    test_sequence = [

        "THREE",
        "THREE",
        "UNKNOWN",
        "THREE",
        "THREE",
        "THREE",
        "THREE",

    ]

    test_stabilizer = GestureStabilizer(
        history_size=7,
        required_count=5
    )

    print(
        "Testing noisy THREE sequence:"
    )

    print()

    for index, gesture in enumerate(
        test_sequence,
        start=1
    ):

        if gesture == "UNKNOWN":

            result = test_stabilizer.update(
                {
                    "gesture": "UNKNOWN",
                    "confidence": 0.0,
                    "recognized": False,
                }
            )

        else:

            result = test_stabilizer.update(
                {
                    "gesture": gesture,
                    "confidence": 0.90,
                    "recognized": True,
                }
            )

        print(
            f"Frame {index}: "
            f"{gesture:8} → "
            f"{result}"
        )

    print()
    print(
        "Removing hand..."
    )

    test_stabilizer.hand_lost()

    print(
        test_stabilizer.get_status()
    )

    print()
    print(
        "✅ Stabilizer test completed."
    )