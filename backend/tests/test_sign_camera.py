import time
import cv2

from app.sign_language.camera import Camera
from app.sign_language.detector import HandDetector


def main():

    camera = Camera()
    detector = HandDetector()

    try:

        camera.start()

        print("=" * 60)
        print(
            "🤟 PAIOS SIGN LANGUAGE — "
            "HAND DETECTION TEST"
        )
        print("=" * 60)

        print(
            "Camera started."
        )

        print(
            "Show your hand to the camera."
        )

        print(
            "Press Q to quit."
        )

        start_time = time.monotonic()

        while True:

            frame = camera.read()

            if frame is None:

                print(
                    "❌ Failed to read "
                    "camera frame."
                )

                break

            # ---------------------------------------------
            # Timestamp in milliseconds
            # ---------------------------------------------

            timestamp_ms = int(
                (
                    time.monotonic()
                    - start_time
                )
                * 1000
            )

            results = detector.detect(
                frame,
                timestamp_ms
            )

            frame = detector.draw(
                frame,
                results
            )

            hand_count = (
                detector.get_hand_count(
                    results
                )
            )

            # ---------------------------------------------
            # UI
            # ---------------------------------------------

            cv2.putText(
                frame,
                f"Hands detected: {hand_count}",
                (20, 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (255, 255, 255),
                2
            )

            cv2.putText(
                frame,
                "PAIOS SIGN LANGUAGE",
                (20, 80),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (255, 255, 255),
                2
            )

            cv2.imshow(
                "PAIOS Sign Language",
                frame
            )

            key = (
                cv2.waitKey(1)
                & 0xFF
            )

            if key == ord("q"):

                break

    except Exception as error:

        print(
            "\n❌ SIGN LANGUAGE TEST FAILED"
        )

        print(
            f"Error: {error}"
        )

    finally:

        detector.close()

        camera.stop()

        print(
            "🤟 Sign language "
            "camera test stopped."
        )


if __name__ == "__main__":

    main()