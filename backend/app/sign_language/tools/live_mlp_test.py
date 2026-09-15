import cv2

from app.sign_language.camera import Camera
from app.sign_language.hand_tracker import HandTracker
from app.sign_language.gesture_model import GestureModel
from app.sign_language.feature_extractor import extract_features


# =========================================================
# CONFIGURATION
# =========================================================

MODEL_PATH = (
    "app/sign_language/models/gesture_model.joblib"
)

HAND_MODEL_PATH = (
    "app/sign_language/models/hand_landmarker.task"
)


# =========================================================
# MAIN
# =========================================================

def main():

    print()
    print("=" * 60)
    print("🧠 PAIOS LIVE MLP GESTURE TEST")
    print("=" * 60)
    print()

    # -----------------------------------------------------
    # CAMERA
    # -----------------------------------------------------

    camera = Camera(
        camera_index=0
    )

    # -----------------------------------------------------
    # HAND TRACKER
    # -----------------------------------------------------

    tracker = HandTracker(
        model_path=HAND_MODEL_PATH
    )

    # -----------------------------------------------------
    # MLP MODEL
    # -----------------------------------------------------

    model = GestureModel(
        model_path=MODEL_PATH,
        confidence_threshold=0.50
    )

    print()
    print("📷 Camera ready")
    print("🟢 Green skeleton active")
    print("🧠 MLP recognition active")
    print()
    print("Show one gesture at a time.")
    print("Hold it steady.")
    print("Press Q to quit.")
    print()

    camera.start()

    try:

        while True:

            frame = camera.read()

            if frame is None:
                continue

            # =================================================
            # HAND TRACKING
            # =================================================

            results = tracker.detect(
                frame
            )

            # =================================================
            # DRAW GREEN SKELETON
            # =================================================

            frame = tracker.draw(
                frame,
                results
            )

            # =================================================
            # FEATURE EXTRACTION
            # =================================================

            features = extract_features(
                results
            )

            # Default values
            gesture = "NO HAND"
            confidence = 0.0

            # =================================================
            # MLP PREDICTION
            # =================================================

            if features is not None:

                prediction = model.predict(
                    features
                )

                gesture = prediction.get(
                    "gesture",
                    "UNKNOWN"
                )

                confidence = prediction.get(
                    "confidence",
                    0.0
                )

            # =================================================
            # DISPLAY
            # =================================================

            cv2.rectangle(
                frame,
                (0, 0),
                (640, 115),
                (0, 0, 0),
                -1
            )

            cv2.putText(
                frame,
                "PAIOS | MLP LIVE",
                (20, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.65,
                (255, 255, 255),
                2,
                cv2.LINE_AA
            )

            cv2.putText(
                frame,
                f"Gesture: {gesture}",
                (20, 65),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.65,
                (0, 255, 0),
                2,
                cv2.LINE_AA
            )

            cv2.putText(
                frame,
                f"Confidence: {confidence * 100:.1f}%",
                (20, 95),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.60,
                (0, 255, 0),
                2,
                cv2.LINE_AA
            )

            cv2.imshow(
                "PAIOS | MLP LIVE TEST",
                frame
            )

            # =================================================
            # KEYBOARD
            # =================================================

            key = (
                cv2.waitKey(1)
                &
                0xFF
            )

            if key == ord("q"):
                break

    except KeyboardInterrupt:

        pass

    finally:

        print()
        print("🧹 Shutting down...")

        camera.stop()

        tracker.close()

        cv2.destroyAllWindows()

        print(
            "✅ Live MLP test stopped."
        )


# =========================================================
# ENTRY POINT
# =========================================================

if __name__ == "__main__":

    main()