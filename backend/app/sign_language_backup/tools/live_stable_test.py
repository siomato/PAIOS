import cv2

from app.sign_language.camera import Camera
from app.sign_language.hand_tracker import HandTracker
from app.sign_language.feature_extractor import extract_features
from app.sign_language.gesture_model import GestureModel
from app.sign_language.stabilizer import GestureStabilizer


# =========================================================
# CONFIGURATION
# =========================================================

CAMERA_INDEX = 0

HAND_MODEL_PATH = (
    "app/sign_language/models/hand_landmarker.task"
)

MODEL_PATH = (
    "app/sign_language/models/gesture_model.joblib"
)

CONFIDENCE_THRESHOLD = 0.50


# =========================================================
# MAIN
# =========================================================

def main():

    print()
    print("=" * 60)
    print("🧠 PAIOS LIVE SIGN LANGUAGE RECOGNITION")
    print("=" * 60)
    print()

    camera = None
    tracker = None

    try:

        # -------------------------------------------------
        # CAMERA
        # -------------------------------------------------

        print("📷 Initializing camera...")

        camera = Camera(
            camera_index=CAMERA_INDEX
        )

        camera.start()

        print("✅ Camera initialized.")

        # -------------------------------------------------
        # HAND TRACKER
        # -------------------------------------------------

        print("🖐️ Initializing hand tracker...")

        tracker = HandTracker(
            model_path=HAND_MODEL_PATH
        )

        print("✅ Hand tracker initialized.")

        # -------------------------------------------------
        # GESTURE MODEL
        # -------------------------------------------------

        print("🤖 Loading trained gesture model...")

        model = GestureModel(
            model_path=MODEL_PATH,
            confidence_threshold=CONFIDENCE_THRESHOLD
        )

        print("✅ Gesture model loaded.")

        # -------------------------------------------------
        # STABILIZER
        # -------------------------------------------------

        print("⏳ Initializing stabilizer...")

        stabilizer = GestureStabilizer()

        print("✅ Stabilizer initialized.")

        print()
        print("=" * 60)
        print("🚀 PAIOS LIVE RECOGNITION READY")
        print("=" * 60)
        print()
        print("🟢 Green hand skeleton : ACTIVE")
        print("🧠 ML recognition      : ACTIVE")
        print("⏳ Stabilizer           : ACTIVE")
        print()
        print("Hold a gesture in front of the camera.")
        print("Press Q to quit.")
        print()

        # =================================================
        # CAMERA LOOP
        # =================================================

        while True:

            frame = camera.read()

            if frame is None:
                continue

            # -------------------------------------------------
            # HAND DETECTION
            # -------------------------------------------------

            results = tracker.detect(
                frame
            )

            # -------------------------------------------------
            # GREEN SKELETON
            # -------------------------------------------------

            frame = tracker.draw(
                frame,
                results
            )

            # -------------------------------------------------
            # FEATURE EXTRACTION
            # -------------------------------------------------

            features = extract_features(
                results
            )

            # Default state

            gesture = "UNKNOWN"
            confidence = 0.0
            recognized = False

            # -------------------------------------------------
            # ML RECOGNITION
            # -------------------------------------------------

            if features is not None:

                prediction = model.predict(
                    features
                )

                gesture = prediction.get(
                    "gesture",
                    "UNKNOWN"
                )

                confidence = float(
                    prediction.get(
                        "confidence",
                        0.0
                    )
                )

                recognized = bool(
                    prediction.get(
                        "recognized",
                        False
                    )
                )

            # -------------------------------------------------
            # STABILIZER
            #
            # IMPORTANT:
            # Your stabilizer accepts ONE argument.
            #
            # Therefore we pass a dictionary.
            # -------------------------------------------------

            stabilizer_input = {

                "gesture": (
                    gesture
                    if recognized
                    else "UNKNOWN"
                ),

                "confidence": (
                    confidence
                    if recognized
                    else 0.0
                )
            }

            stable_result = stabilizer.update(
                stabilizer_input
            )

            # -------------------------------------------------
            # READ STABLE RESULT
            # -------------------------------------------------

            stable_gesture = stable_result.get(
                "gesture",
                "UNKNOWN"
            )

            stable_confidence = float(
                stable_result.get(
                    "confidence",
                    0.0
                )
            )

            confirmed = bool(
                stable_result.get(
                    "confirmed",
                    False
                )
            )

            # -------------------------------------------------
            # STATUS
            # -------------------------------------------------

            if confirmed:

                status = "CONFIRMED"

            elif recognized:

                status = "STABILIZING"

            else:

                status = "NO GESTURE"

            # -------------------------------------------------
            # UI PANEL
            # -------------------------------------------------

            height, width = frame.shape[:2]

            cv2.rectangle(
                frame,
                (0, 0),
                (width, 135),
                (0, 0, 0),
                -1
            )

            # -------------------------------------------------
            # TITLE
            # -------------------------------------------------

            cv2.putText(
                frame,
                "PAIOS | SIGN LANGUAGE",
                (20, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.65,
                (255, 255, 255),
                2,
                cv2.LINE_AA
            )

            # -------------------------------------------------
            # GESTURE
            # -------------------------------------------------

            cv2.putText(
                frame,
                f"GESTURE : {stable_gesture}",
                (20, 65),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.65,
                (0, 255, 0),
                2,
                cv2.LINE_AA
            )

            # -------------------------------------------------
            # CONFIDENCE
            # -------------------------------------------------

            cv2.putText(
                frame,
                f"CONFIDENCE : {stable_confidence * 100:.1f}%",
                (20, 95),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.55,
                (255, 255, 255),
                2,
                cv2.LINE_AA
            )

            # -------------------------------------------------
            # STATUS
            # -------------------------------------------------

            if confirmed:

                status_color = (
                    0,
                    255,
                    0
                )

            elif recognized:

                status_color = (
                    0,
                    200,
                    255
                )

            else:

                status_color = (
                    0,
                    0,
                    255
                )

            cv2.putText(
                frame,
                f"STATUS : {status}",
                (20, 122),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.50,
                status_color,
                2,
                cv2.LINE_AA
            )

            # -------------------------------------------------
            # DISPLAY
            # -------------------------------------------------

            cv2.imshow(
                "PAIOS | SIGN LANGUAGE",
                frame
            )

            # -------------------------------------------------
            # KEYBOARD
            # -------------------------------------------------

            key = (
                cv2.waitKey(1)
                &
                0xFF
            )

            if key == ord("q"):

                break

    except KeyboardInterrupt:

        print()
        print("⚠️ Interrupted by user.")

    except Exception as error:

        print()
        print("=" * 60)
        print("❌ LIVE RECOGNITION ERROR")
        print("=" * 60)
        print()
        print(error)
        print()

    finally:

        print()
        print("🧹 Shutting down...")

        if camera is not None:

            camera.stop()

        if tracker is not None:

            tracker.close()

        cv2.destroyAllWindows()

        print("✅ PAIOS live recognition stopped.")
        print()


# =========================================================
# ENTRY POINT
# =========================================================

if __name__ == "__main__":

    main()