import os
import csv
import time
import cv2

from app.sign_language.camera import Camera
from app.sign_language.hand_tracker import HandTracker


# =========================================================
# CONFIGURATION
# =========================================================

DATASET_DIR = os.path.join(
    "app",
    "sign_language",
    "dataset"
)

MODEL_PATH = os.path.join(
    "app",
    "sign_language",
    "models",
    "hand_landmarker.task"
)

# ---------------------------------------------------------
# Gestures to collect
# ---------------------------------------------------------

GESTURES = [
    "FIST",
    "OPEN_PALM",
    "THUMBS_UP",
    "THUMBS_DOWN",
    "ONE",
    "TWO",
    "THREE",
    "FOUR",
    "FIVE",
    "OK",
    "POINT",
    "ROCK",
    "PINCH",
    "CALL_ME",
    "I_LOVE_YOU"
]

# ---------------------------------------------------------
# Number of samples required per gesture
# ---------------------------------------------------------

SAMPLES_PER_GESTURE = 200

# ---------------------------------------------------------
# Minimum time between captures
#
# Prevents one SPACE press / held key from creating
# hundreds of duplicate samples.
# ---------------------------------------------------------

CAPTURE_COOLDOWN = 0.20


# =========================================================
# CSV HEADER
# =========================================================

CSV_HEADER = []

for index in range(21):

    CSV_HEADER.extend([
        f"x{index}",
        f"y{index}",
        f"z{index}"
    ])


# =========================================================
# DIRECTORY SETUP
# =========================================================

def ensure_gesture_directory(
    gesture
):

    gesture_dir = os.path.join(
        DATASET_DIR,
        gesture
    )

    os.makedirs(
        gesture_dir,
        exist_ok=True
    )

    return gesture_dir


# =========================================================
# CSV PATH
# =========================================================

def get_csv_path(
    gesture
):

    gesture_dir = ensure_gesture_directory(
        gesture
    )

    return os.path.join(
        gesture_dir,
        "samples.csv"
    )


# =========================================================
# COUNT EXISTING SAMPLES
# =========================================================

def count_existing_samples(
    gesture
):

    csv_path = get_csv_path(
        gesture
    )

    if not os.path.exists(
        csv_path
    ):

        return 0

    try:

        with open(
            csv_path,
            "r",
            newline=""
        ) as file:

            reader = csv.reader(
                file
            )

            rows = list(
                reader
            )

            if not rows:
                return 0

            return max(
                0,
                len(rows) - 1
            )

    except Exception as error:

        print(
            f"⚠️ Could not read {csv_path}: "
            f"{error}"
        )

        return 0


# =========================================================
# CREATE CSV
# =========================================================

def prepare_csv(
    gesture
):

    csv_path = get_csv_path(
        gesture
    )

    # -----------------------------------------------------
    # If CSV doesn't exist, create it.
    # -----------------------------------------------------

    if not os.path.exists(
        csv_path
    ):

        with open(
            csv_path,
            "w",
            newline=""
        ) as file:

            writer = csv.writer(
                file
            )

            writer.writerow(
                CSV_HEADER
            )

    return csv_path


# =========================================================
# EXTRACT RAW LANDMARKS
# =========================================================

def extract_raw_landmarks(
    results
):

    if results is None:
        return None

    hands = getattr(
        results,
        "hand_landmarks",
        None
    )

    if not hands:
        return None

    # -----------------------------------------------------
    # Use first detected hand
    # -----------------------------------------------------

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
# SAVE SAMPLE
# =========================================================

def save_sample(
    gesture,
    features
):

    if features is None:
        return False

    if len(features) != 63:
        return False

    csv_path = prepare_csv(
        gesture
    )

    try:

        with open(
            csv_path,
            "a",
            newline=""
        ) as file:

            writer = csv.writer(
                file
            )

            writer.writerow(
                features
            )

        return True

    except Exception as error:

        print(
            f"❌ Failed to save sample: "
            f"{error}"
        )

        return False


# =========================================================
# DRAW UI
# =========================================================

def draw_interface(
    frame,
    gesture,
    current_count,
    hand_detected,
    message,
    gesture_index
):

    height, width = frame.shape[:2]

    # -----------------------------------------------------
    # Top panel
    # -----------------------------------------------------

    cv2.rectangle(
        frame,
        (0, 0),
        (width, 145),
        (0, 0, 0),
        -1
    )

    # -----------------------------------------------------
    # Title
    # -----------------------------------------------------

    cv2.putText(
        frame,
        "PAIOS | DATASET COLLECTOR",
        (20, 30),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.70,
        (255, 255, 255),
        2,
        cv2.LINE_AA
    )

    # -----------------------------------------------------
    # Current gesture
    # -----------------------------------------------------

    cv2.putText(
        frame,
        f"GESTURE: {gesture}",
        (20, 65),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.70,
        (0, 255, 0),
        2,
        cv2.LINE_AA
    )

    # -----------------------------------------------------
    # Progress
    # -----------------------------------------------------

    progress_text = (
        f"SAMPLES: "
        f"{current_count}/"
        f"{SAMPLES_PER_GESTURE}"
    )

    cv2.putText(
        frame,
        progress_text,
        (20, 95),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.60,
        (255, 255, 255),
        2,
        cv2.LINE_AA
    )

    # -----------------------------------------------------
    # Hand status
    # -----------------------------------------------------

    hand_text = (
        "HAND DETECTED"
        if hand_detected
        else "NO HAND"
    )

    hand_color = (
        (0, 255, 0)
        if hand_detected
        else (0, 0, 255)
    )

    cv2.putText(
        frame,
        hand_text,
        (280, 95),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.55,
        hand_color,
        2,
        cv2.LINE_AA
    )

    # -----------------------------------------------------
    # Message
    # -----------------------------------------------------

    cv2.putText(
        frame,
        message,
        (20, 125),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.50,
        (0, 200, 255),
        2,
        cv2.LINE_AA
    )

    # -----------------------------------------------------
    # Bottom controls
    # -----------------------------------------------------

    bottom_y = height - 45

    cv2.rectangle(
        frame,
        (0, height - 75),
        (width, height),
        (0, 0, 0),
        -1
    )

    controls = (
        "SPACE: CAPTURE    "
        "N: NEXT GESTURE    "
        "Q: QUIT"
    )

    cv2.putText(
        frame,
        controls,
        (20, bottom_y),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.55,
        (255, 255, 255),
        2,
        cv2.LINE_AA
    )

    # -----------------------------------------------------
    # Gesture number
    # -----------------------------------------------------

    gesture_number = (
        f"{gesture_index + 1}/"
        f"{len(GESTURES)}"
    )

    cv2.putText(
        frame,
        gesture_number,
        (
            width - 100,
            35
        ),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.55,
        (255, 255, 255),
        2,
        cv2.LINE_AA
    )

    return frame


# =========================================================
# MAIN
# =========================================================

def main():

    print()
    print("=" * 60)
    print(
        "🧠 PAIOS SIGN LANGUAGE DATASET COLLECTOR"
    )
    print("=" * 60)
    print()

    print(
        f"📊 Gestures: {len(GESTURES)}"
    )

    print(
        f"📸 Samples per gesture: "
        f"{SAMPLES_PER_GESTURE}"
    )

    print()

    print(
        "CONTROLS:"
    )

    print(
        "  SPACE → capture sample"
    )

    print(
        "  N     → next gesture"
    )

    print(
        "  Q     → quit"
    )

    print()

    # -----------------------------------------------------
    # Make dataset directory
    # -----------------------------------------------------

    os.makedirs(
        DATASET_DIR,
        exist_ok=True
    )

    # -----------------------------------------------------
    # Camera
    # -----------------------------------------------------

    camera = Camera(
        camera_index=0
    )

    # -----------------------------------------------------
    # Hand tracker
    # -----------------------------------------------------

    tracker = HandTracker(
        model_path=MODEL_PATH
    )

    # -----------------------------------------------------
    # Current gesture
    # -----------------------------------------------------

    gesture_index = 0

    current_gesture = GESTURES[
        gesture_index
    ]

    current_count = count_existing_samples(
        current_gesture
    )

    prepare_csv(
        current_gesture
    )

    # -----------------------------------------------------
    # Capture timing
    # -----------------------------------------------------

    last_capture_time = 0.0

    # -----------------------------------------------------
    # Message shown on screen
    # -----------------------------------------------------

    message = (
        "Make the gesture and press SPACE"
    )

    camera.start()

    print()
    print(
        "📷 Camera started."
    )

    print(
        f"🤟 Current gesture: "
        f"{current_gesture}"
    )

    print()
    print(
        "🟢 Green skeleton active."
    )

    print(
        "Press SPACE to capture."
    )

    print(
        "Press N to move to the next gesture."
    )

    print(
        "Press Q to quit."
    )

    print()

    try:

        while True:

            # -------------------------------------------------
            # Read frame
            # -------------------------------------------------

            frame = camera.read()

            if frame is None:

                continue

            # -------------------------------------------------
            # Detect hand
            # -------------------------------------------------

            results = tracker.detect(
                frame
            )

            # -------------------------------------------------
            # Draw green skeleton
            # -------------------------------------------------

            frame = tracker.draw(
                frame,
                results
            )

            # -------------------------------------------------
            # Extract raw landmarks
            # -------------------------------------------------

            features = extract_raw_landmarks(
                results
            )

            hand_detected = (
                features is not None
            )

            # -------------------------------------------------
            # Draw UI
            # -------------------------------------------------

            frame = draw_interface(
                frame,
                current_gesture,
                current_count,
                hand_detected,
                message,
                gesture_index
            )

            # -------------------------------------------------
            # Show camera
            # -------------------------------------------------

            cv2.imshow(
                "PAIOS | DATASET COLLECTOR",
                frame
            )

            # -------------------------------------------------
            # Keyboard
            # -------------------------------------------------

            key = (
                cv2.waitKey(1)
                &
                0xFF
            )

            # =================================================
            # QUIT
            # =================================================

            if key == ord("q"):

                print()
                print(
                    "🛑 Collection stopped."
                )

                break

            # =================================================
            # CAPTURE
            # =================================================

            elif key == 32:

                now = time.time()

                # ---------------------------------------------
                # Cooldown protection
                # ---------------------------------------------

                if (
                    now - last_capture_time
                    <
                    CAPTURE_COOLDOWN
                ):

                    continue

                last_capture_time = now

                # ---------------------------------------------
                # Need a hand
                # ---------------------------------------------

                if features is None:

                    message = (
                        "⚠️ No hand detected"
                    )

                    print(
                        "⚠️ Capture ignored: "
                        "no hand detected."
                    )

                    continue

                # ---------------------------------------------
                # Don't exceed target
                # ---------------------------------------------

                if (
                    current_count
                    >=
                    SAMPLES_PER_GESTURE
                ):

                    message = (
                        "✅ Gesture complete. "
                        "Press N."
                    )

                    continue

                # ---------------------------------------------
                # Save
                # ---------------------------------------------

                success = save_sample(
                    current_gesture,
                    features
                )

                if success:

                    current_count += 1

                    message = (
                        "✓ SAMPLE CAPTURED"
                    )

                    print(
                        f"📸 "
                        f"{current_gesture}: "
                        f"{current_count}/"
                        f"{SAMPLES_PER_GESTURE}"
                    )

                    # -----------------------------------------
                    # Automatic completion notification
                    # -----------------------------------------

                    if (
                        current_count
                        >=
                        SAMPLES_PER_GESTURE
                    ):

                        message = (
                            "✅ COMPLETE — "
                            "Press N for next"
                        )

            # =================================================
            # NEXT GESTURE
            # =================================================

            elif key == ord("n"):

                # ---------------------------------------------
                # Move only when current gesture is complete
                # ---------------------------------------------

                if (
                    current_count
                    <
                    SAMPLES_PER_GESTURE
                ):

                    message = (
                        f"⚠️ Need "
                        f"{SAMPLES_PER_GESTURE - current_count} "
                        f"more samples"
                    )

                    print(
                        f"⚠️ {current_gesture} "
                        f"is not complete."
                    )

                    continue

                # ---------------------------------------------
                # Last gesture
                # ---------------------------------------------

                if (
                    gesture_index
                    >=
                    len(GESTURES) - 1
                ):

                    message = (
                        "🎉 ALL GESTURES COMPLETE"
                    )

                    print()
                    print(
                        "=" * 60
                    )

                    print(
                        "🎉 DATASET COLLECTION COMPLETE"
                    )

                    print(
                        "=" * 60
                    )

                    print()

                    break

                # ---------------------------------------------
                # Next gesture
                # ---------------------------------------------

                gesture_index += 1

                current_gesture = GESTURES[
                    gesture_index
                ]

                current_count = (
                    count_existing_samples(
                        current_gesture
                    )
                )

                prepare_csv(
                    current_gesture
                )

                message = (
                    "Make the gesture and "
                    "press SPACE"
                )

                print()
                print(
                    f"➡️ NEXT GESTURE: "
                    f"{current_gesture}"
                )

                print(
                    f"📊 Existing samples: "
                    f"{current_count}/"
                    f"{SAMPLES_PER_GESTURE}"
                )

    except KeyboardInterrupt:

        print()
        print(
            "🛑 Collection interrupted."
        )

    finally:

        print()
        print(
            "🧹 Shutting down collector..."
        )

        camera.stop()

        tracker.close()

        cv2.destroyAllWindows()

        print(
            "✅ Dataset collector stopped."
        )

        print()


# =========================================================
# ENTRY POINT
# =========================================================

if __name__ == "__main__":

    main()