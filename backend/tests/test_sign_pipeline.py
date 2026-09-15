"""
PAIOS Sign Language Pipeline Test

Pipeline:

Camera
   ↓
Hand Detector
   ↓
Hand Landmarks
   ↓
Gesture Recognizer
   ↓
Sign Translator
"""

import time
import cv2

from app.sign_language.camera import Camera
from app.sign_language.detector import HandDetector
from app.sign_language.recognizer import HandRecognizer
from app.sign_language.translator import SignTranslator


def main():

    print()
    print("=" * 60)
    print("🤟 PAIOS SIGN LANGUAGE PIPELINE TEST")
    print("=" * 60)
    print()

    # =====================================================
    # INITIALIZE COMPONENTS
    # =====================================================

    try:

        camera = Camera()

        detector = HandDetector()

        recognizer = HandRecognizer()

        translator = SignTranslator()

    except Exception as e:

        print()
        print("❌ PIPELINE INITIALIZATION FAILED")
        print(f"Error: {e}")
        print()

        return

    print()
    print("✅ All sign-language components initialized.")
    print()

    # =====================================================
    # START CAMERA
    # =====================================================

    try:

        camera.start()

    except Exception as e:

        print()
        print("❌ CAMERA START FAILED")
        print(f"Error: {e}")
        print()

        return

    print("📷 Camera started.")
    print()
    print("Show your hand to the camera.")
    print("Press Q to quit.")
    print()

    # =====================================================
    # MAIN LOOP
    # =====================================================

    try:

        while True:

            # -------------------------------------------------
            # READ CAMERA FRAME
            # -------------------------------------------------

            frame = camera.read()

            if frame is None:

                print(
                    "⚠️ Camera returned an empty frame."
                )

                time.sleep(0.01)

                continue

            # -------------------------------------------------
            # GENERATE MONOTONIC TIMESTAMP
            # -------------------------------------------------

            timestamp_ms = int(
                time.monotonic() * 1000
            )

            # -------------------------------------------------
            # DETECT HAND
            # -------------------------------------------------

            try:

                detection_result = (
                    detector.detect(
                        frame,
                        timestamp_ms
                    )
                )

            except Exception as e:

                print()
                print(
                    f"⚠️ Hand detection error: {e}"
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

                continue

            # -------------------------------------------------
            # NO HAND DETECTED
            # -------------------------------------------------

            if not detection_result:

                cv2.putText(
                    frame,
                    "Show your hand",
                    (20, 40),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.8,
                    (0, 255, 255),
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

                continue

            # -------------------------------------------------
            # EXTRACT LANDMARKS
            # -------------------------------------------------

            landmarks = detection_result

            if isinstance(
                detection_result,
                dict
            ):

                landmarks = (
                    detection_result.get(
                        "landmarks"
                    )
                )

            if not landmarks:

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

                continue

            # -------------------------------------------------
            # RECOGNIZE GESTURE
            # -------------------------------------------------

            try:

                recognition_result = (
                    recognizer.recognize(
                        landmarks
                    )
                )

            except Exception as e:

                print()
                print(
                    f"⚠️ Recognition error: {e}"
                )

                recognition_result = {

                    "gesture":
                        "UNKNOWN",

                    "confidence":
                        0.0
                }

            # -------------------------------------------------
            # TRANSLATE GESTURE
            # -------------------------------------------------

            try:

                translation_result = (
                    translator.translate_result(
                        recognition_result
                    )
                )

            except Exception as e:

                print()
                print(
                    f"⚠️ Translation error: {e}"
                )

                translation_result = {

                    "status":
                        "failed",

                    "gesture":
                        "UNKNOWN",

                    "text":
                        "UNKNOWN",

                    "confidence":
                        0.0,

                    "message":
                        str(e)
                }

            # -------------------------------------------------
            # EXTRACT RESULT
            # -------------------------------------------------

            gesture = (
                translation_result.get(
                    "gesture",
                    "UNKNOWN"
                )
            )

            text = (
                translation_result.get(
                    "text",
                    "UNKNOWN"
                )
            )

            confidence = (
                translation_result.get(
                    "confidence",
                    0.0
                )
            )

            # -------------------------------------------------
            # SAFE CONFIDENCE
            # -------------------------------------------------

            try:

                confidence = float(
                    confidence
                )

            except (
                TypeError,
                ValueError
            ):

                confidence = 0.0

            # -------------------------------------------------
            # TERMINAL OUTPUT
            # -------------------------------------------------

            print(
                f"\r🤟 Gesture: "
                f"{str(gesture):<15} "
                f"| Meaning: "
                f"{str(text):<15} "
                f"| Confidence: "
                f"{confidence:.2f}",
                end="",
                flush=True
            )

            # -------------------------------------------------
            # CAMERA DISPLAY
            # -------------------------------------------------

            display_text = (
                f"{gesture} -> {text}"
            )

            cv2.putText(
                frame,
                display_text,
                (20, 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (0, 255, 0),
                2
            )

            cv2.putText(
                frame,
                f"Confidence: {confidence:.2f}",
                (20, 75),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (255, 255, 255),
                2
            )

            cv2.putText(
                frame,
                "Press Q to quit",
                (20, 110),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (255, 255, 255),
                1
            )

            cv2.imshow(
                "PAIOS Sign Language",
                frame
            )

            # -------------------------------------------------
            # QUIT
            # -------------------------------------------------

            key = (
                cv2.waitKey(1)
                & 0xFF
            )

            if key == ord("q"):

                break

    except KeyboardInterrupt:

        print()
        print()
        print(
            "🛑 Pipeline interrupted by user."
        )

    except Exception as e:

        print()
        print()
        print(
            "❌ PIPELINE RUNTIME ERROR"
        )

        print(
            f"Error: {e}"
        )

    finally:

        # =================================================
        # CAMERA CLEANUP
        # =================================================

        try:

            camera.stop()

        except Exception:
            pass

        cv2.destroyAllWindows()

        print()
        print()
        print("=" * 60)
        print("🤟 SIGN LANGUAGE PIPELINE STOPPED")
        print("=" * 60)
        print()


if __name__ == "__main__":

    main()