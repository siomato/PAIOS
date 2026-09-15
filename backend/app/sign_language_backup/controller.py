"""
PAIOS Sign Language Controller
==============================

Pipeline:

Camera
   ↓
Hand Tracker
   ↓
Green Hand Skeleton
   ↓
Gesture Model
   ↓
Gesture Stabilizer
   ↓
Translator
   ↓
PAIOS Bridge
"""

import time
import cv2

from app.sign_language.camera import Camera
from app.sign_language.hand_tracker import HandTracker
from app.sign_language.gesture_model import GestureModel
from app.sign_language.stabilizer import GestureStabilizer
from app.sign_language.translator import SignTranslator
from app.sign_language.paios_bridge import PAIOSBridge


class SignLanguageController:

    # =====================================================
    # INITIALIZATION
    # =====================================================

    def __init__(
        self,
        camera_index=0,
        model_path=(
            "app/sign_language/models/"
            "hand_landmarker.task"
        ),
    ):

        self.camera_index = camera_index
        self.model_path = model_path

        self.camera = None
        self.hand_tracker = None
        self.gesture_model = None
        self.stabilizer = None
        self.translator = None
        self.paios_bridge = None

        self.running = False

        self.current_gesture = "UNKNOWN"
        self.current_text = ""
        self.current_confidence = 0.0
        self.hand_count = 0

        self.fps = 0.0
        self.previous_frame_time = None

        print(
            "🎛️ PAIOS SIGN LANGUAGE CONTROLLER"
        )

    # =====================================================
    # INITIALIZE
    # =====================================================

    def initialize(self):

        print()
        print("=" * 60)
        print(
            "🚀 INITIALIZING PAIOS SIGN LANGUAGE SYSTEM"
        )
        print("=" * 60)
        print()

        # -------------------------------------------------
        # CAMERA
        # -------------------------------------------------

        print("📷 Starting camera...")

        self.camera = Camera(
            self.camera_index
        )

        self.camera.start()

        print(
            "✅ Camera initialized."
        )

        # -------------------------------------------------
        # HAND TRACKER
        # -------------------------------------------------

        print(
            "🖐️ Starting hand tracker..."
        )

        self.hand_tracker = HandTracker(
            model_path=self.model_path
        )

        print(
            "✅ Hand tracker initialized."
        )

        # -------------------------------------------------
        # GESTURE MODEL
        # -------------------------------------------------

        print(
            "🤖 Starting gesture model..."
        )

        self.gesture_model = GestureModel()

        print(
            "✅ Gesture model initialized."
        )

        # -------------------------------------------------
        # STABILIZER
        # -------------------------------------------------

        print(
            "⏳ Starting stabilizer..."
        )

        self.stabilizer = GestureStabilizer()

        print(
            "✅ Stabilizer initialized."
        )

        # -------------------------------------------------
        # TRANSLATOR
        # -------------------------------------------------

        print(
            "🗣️ Starting translator..."
        )

        self.translator = SignTranslator()

        print(
            "✅ Translator initialized."
        )

        # -------------------------------------------------
        # PAIOS BRIDGE
        # -------------------------------------------------

        print(
            "🔌 Starting PAIOS bridge..."
        )

        self.paios_bridge = PAIOSBridge()

        print(
            "✅ PAIOS bridge initialized."
        )

        self.previous_frame_time = time.time()

        print()
        print("=" * 60)
        print(
            "✅ PAIOS SIGN LANGUAGE SYSTEM READY"
        )
        print("=" * 60)
        print()

    # =====================================================
    # PROCESS FRAME
    # =====================================================

    def process_frame(self, frame):

        if frame is None:
            return frame

        # -------------------------------------------------
        # HAND DETECTION
        #
        # IMPORTANT:
        # HandTracker.detect() accepts ONLY frame.
        # -------------------------------------------------

        try:

            results = (
                self.hand_tracker.detect(
                    frame
                )
            )

        except Exception as error:

            print(
                "⚠️ Hand tracking error:",
                error
            )

            return frame

        # -------------------------------------------------
        # DRAW GREEN SKELETON
        # -------------------------------------------------

        try:

            frame = (
                self.hand_tracker.draw(
                    frame,
                    results
                )
            )

        except Exception as error:

            print(
                "⚠️ Skeleton drawing error:",
                error
            )

        # -------------------------------------------------
        # DIRECTLY COUNT HANDS
        #
        # Do NOT use get_hand_count().
        # We use the actual MediaPipe result.
        # -------------------------------------------------

        hand_landmarks = getattr(
            results,
            "hand_landmarks",
            None
        )

        if hand_landmarks:

            self.hand_count = len(
                hand_landmarks
            )

        else:

            self.hand_count = 0

        # -------------------------------------------------
        # NO HAND
        # -------------------------------------------------

        if self.hand_count == 0:

            self.current_gesture = (
                "NO HAND"
            )

            self.current_text = ""

            self.current_confidence = 0.0

            # Reset stabilizer when hand disappears.

            try:

                self.stabilizer.hand_lost()

            except Exception:

                pass

            return frame

        # -------------------------------------------------
        # LANDMARK SAFETY CHECK
        # -------------------------------------------------

        if not hand_landmarks:

            return frame

        # -------------------------------------------------
        # FIRST HAND
        # -------------------------------------------------

        landmarks = (
            hand_landmarks[0]
        )

        # -------------------------------------------------
        # GESTURE RECOGNITION
        # -------------------------------------------------

        try:

            recognition = (
                self.gesture_model.classify(
                    landmarks
                )
            )

        except Exception as error:

            print(
                "⚠️ Gesture recognition error:",
                error
            )

            recognition = {
                "gesture": "UNKNOWN",
                "confidence": 0.0,
            }

        # -------------------------------------------------
        # STABILIZER
        # -------------------------------------------------

        try:

            stable_result = (
                self.stabilizer.update(
                    recognition
                )
            )

        except Exception as error:

            print(
                "⚠️ Stabilizer error:",
                error
            )

            stable_result = {
                "gesture": "UNKNOWN",
                "confidence": 0.0,
                "stable": False,
                "confirmed": False,
                "new": False,
            }

        # -------------------------------------------------
        # EXTRACT STABILIZED RESULT
        # -------------------------------------------------

        gesture = stable_result.get(
            "gesture",
            "UNKNOWN"
        )

        confidence = stable_result.get(
            "confidence",
            0.0
        )

        confirmed = stable_result.get(
            "confirmed",
            False
        )

        is_new = stable_result.get(
            "new",
            False
        )

        self.current_gesture = (
            gesture
        )

        try:

            self.current_confidence = float(
                confidence
            )

        except (
            TypeError,
            ValueError
        ):

            self.current_confidence = 0.0

        # -------------------------------------------------
        # TRANSLATION
        # -------------------------------------------------

        if confirmed:

            try:

                translated = (
                    self.translator.translate(
                        gesture
                    )
                )

                self.current_text = (
                    translated.get(
                        "text",
                        "UNKNOWN"
                    )
                )

            except Exception as error:

                print(
                    "⚠️ Translation error:",
                    error
                )

                self.current_text = (
                    "UNKNOWN"
                )

        else:

            self.current_text = ""

        # -------------------------------------------------
        # SEND ONLY NEW CONFIRMED GESTURES
        #
        # This prevents:
        #
        # THREE
        # THREE
        # THREE
        # THREE
        #
        # being sent continuously.
        # -------------------------------------------------

        if (
            confirmed
            and
            is_new
            and
            gesture != "UNKNOWN"
        ):

            try:

                translated = (
                    self.translator.translate(
                        gesture
                    )
                )

                self.paios_bridge.send_to_paios(
                    translated
                )

            except Exception as error:

                print()
                print(
                    "⚠️ PAIOS bridge error:",
                    error
                )

        return frame

    # =====================================================
    # FPS
    # =====================================================

    def update_fps(self):

        current_time = time.time()

        if self.previous_frame_time is None:

            self.previous_frame_time = (
                current_time
            )

            return

        delta = (
            current_time
            -
            self.previous_frame_time
        )

        self.previous_frame_time = (
            current_time
        )

        if delta <= 0:

            return

        instant_fps = 1.0 / delta

        if self.fps <= 0:

            self.fps = instant_fps

        else:

            self.fps = (
                self.fps * 0.90
                +
                instant_fps * 0.10
            )

    # =====================================================
    # DRAW UI
    # =====================================================

    def draw_ui(self, frame):

        if frame is None:

            return frame

        height, width = (
            frame.shape[:2]
        )

        # -------------------------------------------------
        # HEADER
        # -------------------------------------------------

        cv2.rectangle(
            frame,
            (0, 0),
            (width, 65),
            (0, 0, 0),
            -1
        )

        cv2.putText(
            frame,
            "PAIOS | SIGN LANGUAGE",
            (20, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.72,
            (255, 255, 255),
            2,
            cv2.LINE_AA
        )

        # LIVE indicator

        cv2.putText(
            frame,
            "● LIVE",
            (width - 105, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.60,
            (0, 255, 0),
            2,
            cv2.LINE_AA
        )

        # -------------------------------------------------
        # BOTTOM PANEL
        # -------------------------------------------------

        panel_height = 115

        panel_top = (
            height
            -
            panel_height
        )

        cv2.rectangle(
            frame,
            (0, panel_top),
            (width, height),
            (0, 0, 0),
            -1
        )

        # -------------------------------------------------
        # GESTURE
        # -------------------------------------------------

        cv2.putText(
            frame,
            (
                f"GESTURE: "
                f"{self.current_gesture}"
            ),
            (20, panel_top + 32),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.65,
            (255, 255, 255),
            2,
            cv2.LINE_AA
        )

        # -------------------------------------------------
        # MEANING
        # -------------------------------------------------

        meaning = (
            self.current_text
            if self.current_text
            else "---"
        )

        cv2.putText(
            frame,
            f"MEANING: {meaning}",
            (20, panel_top + 65),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.65,
            (255, 255, 255),
            2,
            cv2.LINE_AA
        )

        # -------------------------------------------------
        # CONFIDENCE
        # -------------------------------------------------

        cv2.putText(
            frame,
            (
                "CONFIDENCE: "
                f"{self.current_confidence:.2f}"
            ),
            (20, panel_top + 94),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.50,
            (180, 180, 180),
            1,
            cv2.LINE_AA
        )

        # -------------------------------------------------
        # HANDS
        # -------------------------------------------------

        cv2.putText(
            frame,
            f"HANDS: {self.hand_count}",
            (width - 180, panel_top + 32),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.50,
            (180, 180, 180),
            1,
            cv2.LINE_AA
        )

        # -------------------------------------------------
        # FPS
        # -------------------------------------------------

        cv2.putText(
            frame,
            f"FPS: {self.fps:.1f}",
            (width - 180, panel_top + 60),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.50,
            (180, 180, 180),
            1,
            cv2.LINE_AA
        )

        # -------------------------------------------------
        # EXIT
        # -------------------------------------------------

        cv2.putText(
            frame,
            "Q = EXIT",
            (width - 180, panel_top + 90),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.50,
            (150, 150, 150),
            1,
            cv2.LINE_AA
        )

        return frame

    # =====================================================
    # MAIN LOOP
    # =====================================================

    def run(self):

        try:

            self.initialize()

        except Exception as error:

            print()
            print(
                "❌ SYSTEM INITIALIZATION FAILED:"
            )

            print(
                f"   {error}"
            )

            self.shutdown()

            return

        self.running = True

        print(
            "📷 LIVE SIGN LANGUAGE CAMERA STARTED"
        )

        print(
            "🟢 Green hand skeleton is active."
        )

        print(
            "Press Q to quit."
        )

        print()

        try:

            while self.running:

                # -----------------------------------------
                # READ CAMERA FRAME
                # -----------------------------------------

                frame = (
                    self.camera.read()
                )

                if frame is None:

                    print(
                        "⚠️ Camera frame unavailable."
                    )

                    time.sleep(
                        0.01
                    )

                    continue

                # -----------------------------------------
                # PROCESS
                # -----------------------------------------

                frame = (
                    self.process_frame(
                        frame
                    )
                )

                # -----------------------------------------
                # FPS
                # -----------------------------------------

                self.update_fps()

                # -----------------------------------------
                # UI
                # -----------------------------------------

                frame = (
                    self.draw_ui(
                        frame
                    )
                )

                # -----------------------------------------
                # DISPLAY
                # -----------------------------------------

                cv2.imshow(
                    "PAIOS SIGN LANGUAGE",
                    frame
                )

                # -----------------------------------------
                # KEYBOARD
                # -----------------------------------------

                key = (
                    cv2.waitKey(1)
                    &
                    0xFF
                )

                if key == ord("q"):

                    print()
                    print(
                        "🛑 Q pressed."
                    )

                    self.running = False

        except KeyboardInterrupt:

            print()
            print(
                "🛑 Keyboard interrupt."
            )

        except Exception as error:

            print()
            print(
                "❌ CONTROLLER ERROR:"
            )

            print(
                f"   {error}"
            )

        finally:

            self.shutdown()

    # =====================================================
    # SHUTDOWN
    # =====================================================

    def shutdown(self):

        self.running = False

        print()
        print(
            "🧹 SHUTTING DOWN PAIOS SIGN LANGUAGE..."
        )

        # -------------------------------------------------
        # CAMERA
        # -------------------------------------------------

        if self.camera is not None:

            try:

                print(
                    "📷 Releasing camera..."
                )

                self.camera.stop()

                print(
                    "✅ Camera released."
                )

            except Exception as error:

                print(
                    "⚠️ Camera shutdown error:",
                    error
                )

            finally:

                self.camera = None

        # -------------------------------------------------
        # HAND TRACKER
        # -------------------------------------------------

        if self.hand_tracker is not None:

            try:

                self.hand_tracker.close()

                print(
                    "✅ Hand tracker closed."
                )

            except Exception as error:

                print(
                    "⚠️ Hand tracker shutdown error:",
                    error
                )

            finally:

                self.hand_tracker = None

        # -------------------------------------------------
        # OPENCV
        # -------------------------------------------------

        try:

            cv2.destroyAllWindows()

        except Exception:

            pass

        print()
        print(
            "✅ PAIOS SIGN LANGUAGE STOPPED."
        )


# =========================================================
# ENTRY POINT
# =========================================================

def main():

    controller = (
        SignLanguageController()
    )

    controller.run()


if __name__ == "__main__":

    main()