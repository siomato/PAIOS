import cv2

from app.sign_language.camera import Camera
from app.sign_language.hand_tracker import HandTracker
from app.sign_language.gesture_model import GestureModel


# =========================================================
# FEATURE EXTRACTION
# =========================================================

def extract_landmarks(results):

    if results is None:
        return None

    hands = getattr(
        results,
        "hand_landmarks",
        None
    )

    if not hands:
        return None

    hand = hands[0]

    if len(hand) != 21:
        return None

    features = []

    for landmark in hand:

        features.extend([
            float(landmark.x),
            float(landmark.y),
            float(landmark.z)
        ])

    if len(features) != 63:
        return None

    return features


# =========================================================
# MAIN
# =========================================================

def main():

    print()
    print("=" * 60)
    print("🧠 PAIOS LIVE GESTURE MODEL TEST")
    print("=" * 60)
    print()

    camera = Camera(
        camera_index=0
    )

    tracker = HandTracker(
        model_path=(
            "app/sign_language/models/"
            "hand_landmarker.task"
        )
    )

    model = GestureModel(
        confidence_threshold=0.60
    )

    print()
    print(
        f"🏷️ Classes: {model.get_classes()}"
    )

    print()
    print(
        "📷 Starting live test..."
    )

    print(
        "🟢 Green skeleton active."
    )

    print(
        "Press Q to quit."
    )

    print()

    camera.start()

    try:

        while True:

            frame = camera.read()

            if frame is None:
                continue

            # ---------------------------------------------
            # Detect hand
            # ---------------------------------------------

            results = tracker.detect(
                frame
            )

            # ---------------------------------------------
            # Draw green skeleton
            # ---------------------------------------------

            frame = tracker.draw(
                frame,
                results
            )

            # ---------------------------------------------
            # Extract 63 features
            # ---------------------------------------------

            features = extract_landmarks(
                results
            )

            if features is not None:

                prediction = model.predict(
                    features
                )

                gesture = prediction[
                    "gesture"
                ]

                confidence = prediction[
                    "confidence"
                ]

                recognized = prediction[
                    "recognized"
                ]

                if recognized:

                    label = (
                        f"{gesture} "
                        f"{confidence * 100:.1f}%"
                    )

                    text_color = (
                        0,
                        255,
                        0
                    )

                else:

                    label = (
                        f"UNKNOWN "
                        f"{confidence * 100:.1f}%"
                    )

                    text_color = (
                        0,
                        165,
                        255
                    )

            else:

                label = "NO HAND"

                text_color = (
                    0,
                    0,
                    255
                )

            # ---------------------------------------------
            # Display prediction
            # ---------------------------------------------

            cv2.rectangle(
                frame,
                (0, 0),
                (640, 75),
                (0, 0, 0),
                -1
            )

            cv2.putText(
                frame,
                "PAIOS LIVE ML",
                (20, 28),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.65,
                (255, 255, 255),
                2,
                cv2.LINE_AA
            )

            cv2.putText(
                frame,
                label,
                (20, 60),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.70,
                text_color,
                2,
                cv2.LINE_AA
            )

            cv2.imshow(
                "PAIOS | LIVE ML TEST",
                frame
            )

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

        camera.stop()

        tracker.close()

        cv2.destroyAllWindows()

        print()
        print(
            "🛑 Live ML test stopped."
        )


# =========================================================
# ENTRY POINT
# =========================================================

if __name__ == "__main__":

    main()