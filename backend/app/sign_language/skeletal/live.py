"""
PAIOS Skeletal Gesture Command Demo.

Run from:

D:\\PAIOS\\backend

with:

python -m app.sign_language.skeletal.live

Supported gestures:

OPEN PALM    -> STOP
THUMBS UP    -> CONFIRM
THUMBS DOWN  -> REJECT
PEACE        -> NEXT
FIST         -> PAUSE
"""

from __future__ import annotations

import os
import time
from collections import deque

import cv2
import numpy as np

from mediapipe import Image, ImageFormat
from mediapipe.tasks.python import BaseOptions, vision

from .gestures import Gesture
from .recognizer import SkeletalRecognizer


# ============================================================
# CONFIGURATION
# ============================================================

MODEL_PATH = os.path.join(
    os.path.dirname(__file__),
    "..",
    "pretrained",
    "mediapipe_models",
    "holistic_landmarker.task",
)

MODEL_PATH = os.path.abspath(MODEL_PATH)

CAMERA_INDEX = 0

STABLE_FRAMES = 8
COOLDOWN_FRAMES = 20


# ============================================================
# MEDIA PIPE
# ============================================================

def create_landmarker():
    """Create MediaPipe Holistic Landmarker."""

    options = vision.HolisticLandmarkerOptions(
        base_options=BaseOptions(
            model_asset_path=MODEL_PATH
        ),
        running_mode=vision.RunningMode.IMAGE,
    )

    return vision.HolisticLandmarker.create_from_options(
        options
    )


# ============================================================
# LANDMARK CONVERSION
# ============================================================

def landmark_list_to_numpy(landmarks):
    """
    Convert MediaPipe NormalizedLandmark objects into
    an Nx3 numpy array.

    IMPORTANT:
    MediaPipe returns a NormalizedLandmarkList in many APIs.
    We explicitly use .landmark instead of treating the
    NormalizedLandmarkList itself as a sequence.
    """

    if landmarks is None:
        return None

    # MediaPipe NormalizedLandmarkList
    if hasattr(landmarks, "landmark"):
        landmarks = landmarks.landmark

    if landmarks is None:
        return None

    if len(landmarks) != 21:
        return None

    output = []

    for point in landmarks:
        output.append(
            [
                float(point.x),
                float(point.y),
                float(point.z),
            ]
        )

    return np.asarray(
        output,
        dtype=np.float32,
    )


# ============================================================
# DRAWING
# ============================================================

def draw_hand_skeleton(
    frame,
    landmarks,
):
    """Draw the detected hand skeleton."""

    if landmarks is None:
        return

    h, w = frame.shape[:2]

    connections = [
        (0, 1),
        (1, 2),
        (2, 3),
        (3, 4),

        (0, 5),
        (5, 6),
        (6, 7),
        (7, 8),

        (0, 9),
        (9, 10),
        (10, 11),
        (11, 12),

        (0, 13),
        (13, 14),
        (14, 15),
        (15, 16),

        (0, 17),
        (17, 18),
        (18, 19),
        (19, 20),

        (5, 9),
        (9, 13),
        (13, 17),
    ]

    points = []

    for point in landmarks:
        x = int(point[0] * w)
        y = int(point[1] * h)

        points.append((x, y))

        cv2.circle(
            frame,
            (x, y),
            4,
            (0, 255, 255),
            -1,
        )

    for a, b in connections:
        cv2.line(
            frame,
            points[a],
            points[b],
            (255, 255, 255),
            2,
        )


# ============================================================
# TEXT
# ============================================================

def put_text(
    frame,
    text,
    position,
    scale=0.7,
    color=(255, 255, 255),
    thickness=2,
):
    """
    Draw readable text with a black outline.
    """

    x, y = position

    # Black outline.
    cv2.putText(
        frame,
        text,
        (x + 2, y + 2),
        cv2.FONT_HERSHEY_SIMPLEX,
        scale,
        (0, 0, 0),
        thickness + 3,
        cv2.LINE_AA,
    )

    # Main text.
    cv2.putText(
        frame,
        text,
        (x, y),
        cv2.FONT_HERSHEY_SIMPLEX,
        scale,
        color,
        thickness,
        cv2.LINE_AA,
    )


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 64)
    print("🧠 PAIOS SKELETAL GESTURE COMMAND ENGINE")
    print("=" * 64)

    print()
    print("Training        : NONE")
    print("Input           : MediaPipe 21-point hand skeleton")
    print(f"Stable frames   : {STABLE_FRAMES}")
    print(f"Cooldown frames : {COOLDOWN_FRAMES}")
    print()

    print("GESTURES")
    print("-" * 64)
    print("✋ OPEN PALM    -> STOP")
    print("👍 THUMBS UP    -> CONFIRM")
    print("👎 THUMBS DOWN  -> REJECT")
    print("✌️  PEACE        -> NEXT")
    print("✊ FIST         -> PAUSE")
    print("-" * 64)

    print()
    print("Q = Quit")
    print("R = Reset")
    print()

    # --------------------------------------------------------
    # Load MediaPipe
    # --------------------------------------------------------

    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError(
            f"MediaPipe model not found:\n{MODEL_PATH}"
        )

    print("⏳ Loading MediaPipe Holistic...")

    landmarker = create_landmarker()

    print("✅ MediaPipe loaded")

    # --------------------------------------------------------
    # Recognizer
    # --------------------------------------------------------

    recognizer = SkeletalRecognizer(
        stable_frames=STABLE_FRAMES,
        cooldown_frames=COOLDOWN_FRAMES,
    )

    # --------------------------------------------------------
    # Webcam
    # --------------------------------------------------------

    print()
    print("🎥 Opening webcam...")

    cap = cv2.VideoCapture(
        CAMERA_INDEX,
        cv2.CAP_DSHOW,
    )

    if not cap.isOpened():
        cap.release()

        cap = cv2.VideoCapture(
            CAMERA_INDEX
        )

    if not cap.isOpened():
        landmarker.close()
        raise RuntimeError(
            "Could not open webcam."
        )

    print("✅ Webcam opened")
    print()

    # --------------------------------------------------------
    # Runtime state
    # --------------------------------------------------------

    frame_count = 0

    current_gesture = Gesture.UNKNOWN
    current_command = "WAITING"
    current_confidence = 0.0

    event_count = 0

    fps_history = deque(maxlen=30)
    previous_time = time.perf_counter()

    # --------------------------------------------------------
    # Main loop
    # --------------------------------------------------------

    try:

        while True:

            ok, frame = cap.read()

            if not ok:
                continue

            frame_count += 1

            # Mirror camera.
            frame = cv2.flip(
                frame,
                1,
            )

            # ------------------------------------------------
            # MediaPipe
            # ------------------------------------------------

            rgb = cv2.cvtColor(
                frame,
                cv2.COLOR_BGR2RGB,
            )

            mp_image = Image(
                image_format=ImageFormat.SRGB,
                data=rgb,
            )

            result = landmarker.detect(
                mp_image
            )

            # ------------------------------------------------
            # Select hand
            #
            # Prefer right hand, otherwise left.
            # ------------------------------------------------

            hand = None
            hand_name = "NONE"

            if result.right_hand_landmarks:

                hand = result.right_hand_landmarks[0]
                hand_name = "RIGHT"

            elif result.left_hand_landmarks:

                hand = result.left_hand_landmarks[0]
                hand_name = "LEFT"

            landmarks = landmark_list_to_numpy(
                hand
            )

            # ------------------------------------------------
            # Draw skeleton
            # ------------------------------------------------

            draw_hand_skeleton(
                frame,
                landmarks,
            )

            # ------------------------------------------------
            # Recognition
            # ------------------------------------------------

            event = recognizer.update(
                landmarks
            )

            if event is not None:

                event_count += 1

                current_gesture = event.gesture
                current_command = event.command
                current_confidence = event.confidence

                print()
                print("=" * 64)
                print("🤟 GESTURE COMMAND")
                print("=" * 64)
                print(
                    f"Gesture    : {event.gesture.value}"
                )
                print(
                    f"Command    : {event.command}"
                )
                print(
                    f"Confidence : {event.confidence * 100:.1f}%"
                )
                print(
                    "Status     : EXECUTED"
                )
                print("=" * 64)

            # ------------------------------------------------
            # FPS
            # ------------------------------------------------

            now = time.perf_counter()

            dt = now - previous_time
            previous_time = now

            if dt > 0:
                fps_history.append(
                    1.0 / dt
                )

            fps = (
                sum(fps_history)
                / len(fps_history)
                if fps_history
                else 0.0
            )

            # ------------------------------------------------
            # UI
            # ------------------------------------------------

            # Header.
            put_text(
                frame,
                "PAIOS SKELETAL CONTROL",
                (20, 40),
                scale=0.9,
                color=(255, 255, 255),
                thickness=2,
            )

            # Gesture.
            gesture_text = (
                current_gesture.value
                if current_gesture != Gesture.UNKNOWN
                else "WAITING..."
            )

            put_text(
                frame,
                f"Gesture: {gesture_text}",
                (20, 85),
                scale=0.75,
                color=(0, 255, 255),
                thickness=2,
            )

            # Command.
            put_text(
                frame,
                f"Command: {current_command}",
                (20, 125),
                scale=0.75,
                color=(0, 255, 0),
                thickness=2,
            )

            # Confidence.
            put_text(
                frame,
                f"Confidence: {current_confidence * 100:.1f}%",
                (20, 165),
                scale=0.65,
                color=(255, 255, 255),
                thickness=2,
            )

            # Hand.
            put_text(
                frame,
                f"Hand: {hand_name}",
                (20, 200),
                scale=0.60,
                color=(255, 255, 255),
                thickness=2,
            )

            # Stability.
            put_text(
                frame,
                f"Stability: {recognizer.stability}/{STABLE_FRAMES}",
                (20, 235),
                scale=0.60,
                color=(255, 255, 255),
                thickness=2,
            )

            # FPS.
            put_text(
                frame,
                f"FPS: {fps:.1f}",
                (20, 270),
                scale=0.60,
                color=(255, 255, 255),
                thickness=2,
            )

            # Events.
            put_text(
                frame,
                f"Commands executed: {event_count}",
                (20, 305),
                scale=0.60,
                color=(255, 255, 255),
                thickness=2,
            )

            # Instructions.
            h = frame.shape[0]

            put_text(
                frame,
                "✋ STOP   👍 CONFIRM   👎 REJECT   ✌ NEXT   ✊ PAUSE",
                (20, h - 50),
                scale=0.52,
                color=(255, 255, 255),
                thickness=1,
            )

            put_text(
                frame,
                "R = RESET    Q = QUIT",
                (20, h - 20),
                scale=0.50,
                color=(255, 255, 255),
                thickness=1,
            )

            # ------------------------------------------------
            # Display
            # ------------------------------------------------

            cv2.imshow(
                "PAIOS - Skeletal Command Control",
                frame,
            )

            key = cv2.waitKey(1) & 0xFF

            if key == ord("q"):
                break

            if key == ord("r"):

                recognizer.reset()

                current_gesture = Gesture.UNKNOWN
                current_command = "WAITING"
                current_confidence = 0.0

                print(
                    "\n🔄 Recognition reset."
                )

    finally:

        cap.release()

        cv2.destroyAllWindows()

        landmarker.close()

        print()
        print("=" * 64)
        print("✅ PAIOS SKELETAL TEST FINISHED")
        print("=" * 64)
        print(
            f"Frames processed : {frame_count}"
        )
        print(
            f"Commands executed: {event_count}"
        )
        print(
            f"Last gesture     : {current_gesture.value}"
        )
        print(
            f"Last command     : {current_command}"
        )
        print("=" * 64)


if __name__ == "__main__":
    main()