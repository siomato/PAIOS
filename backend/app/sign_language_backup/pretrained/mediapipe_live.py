"""
PAIOS INCLUDE — Reliable Live ISL Recognition

This module:
    1. Loads the official INCLUDE Transformer checkpoint.
    2. Loads MediaPipe Holistic.
    3. Extracts exactly 134 features:
           25 pose landmarks × 2 = 50
           21 left-hand landmarks × 2 = 42
           21 right-hand landmarks × 2 = 42
           TOTAL                  = 134
    4. Collects a 200-frame sequence.
    5. Runs INCLUDE prediction.
    6. Displays the result on the webcam.
    7. Handles MediaPipe Tasks API landmark containers safely.

Controls:
    Q = Quit
    R = Reset sequence
"""

from __future__ import annotations

import os
import traceback
from collections import deque

import cv2
import numpy as np

from mediapipe import Image, ImageFormat
from mediapipe.tasks.python import BaseOptions, vision

from app.sign_language.pretrained.pretrained_model import get_model


# ============================================================
# CONFIGURATION
# ============================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

MODEL_PATH = os.path.join(
    BASE_DIR,
    "mediapipe_models",
    "holistic_landmarker.task",
)

FEATURE_SIZE = 134
SEQUENCE_LENGTH = 200
NUM_CLASSES = 263

CAMERA_INDEX = 0

# Run prediction every N frames after
# the sequence becomes full.
PREDICT_EVERY = 5

# Minimum confidence used by the display.
CONFIDENCE_THRESHOLD = 0.20


# ============================================================
# INCLUDE POSE MAPPING
# ============================================================

"""
MediaPipe Pose contains 33 landmarks.

INCLUDE expects 25 pose landmarks.

25 × 2 = 50 features
21 × 2 = 42 left hand features
21 × 2 = 42 right hand features

50 + 42 + 42 = 134
"""

POSE_INDICES = [
    0,      # nose

    2,      # left eye
    5,      # right eye

    7,      # left ear
    8,      # right ear

    11,     # left shoulder
    12,     # right shoulder

    13,     # left elbow
    14,     # right elbow

    15,     # left wrist
    16,     # right wrist

    17,     # left pinky
    18,     # right pinky

    19,     # left index
    20,     # right index

    21,     # left thumb
    22,     # right thumb

    23,     # left hip
    24,     # right hip

    25,     # left knee
    26,     # right knee

    27,     # left ankle
    28,     # right ankle

    29,     # left heel
    30,     # right heel
]


# ============================================================
# MEDIAPIPE LANDMARK CONTAINER HANDLING
# ============================================================

def get_landmark_list(container):
    """
    Safely convert MediaPipe Tasks landmark output
    into a normal Python list of landmarks.

    IMPORTANT:

    Depending on the MediaPipe Tasks API version,
    landmark containers can appear in different forms.

    Possible forms:

        None

        [NormalizedLandmark, ...]

        [[NormalizedLandmark, ...]]

        NormalizedLandmark

    This function normalizes all of them.
    """

    if container is None:
        return []

    # --------------------------------------------------------
    # CASE 1:
    # The supplied object itself is a landmark.
    # --------------------------------------------------------

    if (
        hasattr(container, "x")
        and hasattr(container, "y")
    ):
        return [container]

    # --------------------------------------------------------
    # CASE 2:
    # Convert iterable container to list.
    # --------------------------------------------------------

    try:
        items = list(container)
    except (TypeError, ValueError):
        return []

    if not items:
        return []

    # --------------------------------------------------------
    # CASE 3:
    # Normal:
    #
    # [landmark, landmark, ...]
    # --------------------------------------------------------

    if (
        hasattr(items[0], "x")
        and hasattr(items[0], "y")
    ):
        return items

    # --------------------------------------------------------
    # CASE 4:
    # Nested:
    #
    # [[landmark, landmark, ...]]
    # --------------------------------------------------------

    try:
        first = items[0]

        if (
            hasattr(first, "__iter__")
            and not hasattr(first, "x")
        ):
            nested = list(first)

            if nested and (
                hasattr(nested[0], "x")
                and hasattr(nested[0], "y")
            ):
                return nested

    except (TypeError, ValueError, IndexError):
        pass

    return []


# ============================================================
# MEDIAPIPE INITIALIZATION
# ============================================================

def create_landmarker():
    """
    Create MediaPipe Holistic Landmarker.
    """

    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError(
            "MediaPipe model not found:\n"
            f"{MODEL_PATH}"
        )

    options = vision.HolisticLandmarkerOptions(
        base_options=BaseOptions(
            model_asset_path=MODEL_PATH
        ),
        running_mode=vision.RunningMode.IMAGE,
    )

    return (
        vision.HolisticLandmarker
        .create_from_options(options)
    )


# ============================================================
# FEATURE EXTRACTION
# ============================================================

def extract_landmarks(
    result,
    previous_features=None,
):
    """
    Extract the 134-dimensional INCLUDE feature vector.

    Output:

        Pose:
            25 landmarks × 2 = 50

        Left hand:
            21 landmarks × 2 = 42

        Right hand:
            21 landmarks × 2 = 42

        TOTAL:
            134
    """

    # ========================================================
    # INITIALIZE EMPTY ARRAYS
    # ========================================================

    pose = np.zeros(
        (25, 2),
        dtype=np.float32,
    )

    left_hand = np.zeros(
        (21, 2),
        dtype=np.float32,
    )

    right_hand = np.zeros(
        (21, 2),
        dtype=np.float32,
    )

    # ========================================================
    # POSE
    # ========================================================

    pose_landmarks = get_landmark_list(
        result.pose_landmarks
    )

    for output_index, mp_index in enumerate(
        POSE_INDICES
    ):

        if mp_index >= len(pose_landmarks):
            continue

        landmark = pose_landmarks[mp_index]

        pose[output_index, 0] = float(
            landmark.x
        )

        pose[output_index, 1] = float(
            landmark.y
        )

    # ========================================================
    # LEFT HAND
    # ========================================================

    left_landmarks = get_landmark_list(
        result.left_hand_landmarks
    )

    for i in range(
        min(
            21,
            len(left_landmarks),
        )
    ):

        landmark = left_landmarks[i]

        left_hand[i, 0] = float(
            landmark.x
        )

        left_hand[i, 1] = float(
            landmark.y
        )

    # ========================================================
    # RIGHT HAND
    # ========================================================

    right_landmarks = get_landmark_list(
        result.right_hand_landmarks
    )

    for i in range(
        min(
            21,
            len(right_landmarks),
        )
    ):

        landmark = right_landmarks[i]

        right_hand[i, 0] = float(
            landmark.x
        )

        right_hand[i, 1] = float(
            landmark.y
        )

    # ========================================================
    # COMBINE
    # ========================================================

    features = np.concatenate(
        [
            pose.reshape(-1),
            left_hand.reshape(-1),
            right_hand.reshape(-1),
        ]
    ).astype(np.float32)

    # ========================================================
    # HARD SAFETY CHECK
    # ========================================================

    if features.shape != (
        FEATURE_SIZE,
    ):

        raise RuntimeError(
            "Invalid INCLUDE feature vector.\n"
            f"Got: {features.shape}\n"
            f"Expected: ({FEATURE_SIZE},)"
        )

    # ========================================================
    # TEMPORARY HAND-LOSS RECOVERY
    # ========================================================

    if previous_features is not None:

        previous_features = np.asarray(
            previous_features,
            dtype=np.float32,
        )

        if previous_features.shape == (
            FEATURE_SIZE,
        ):

            # Left hand
            current_left = features[50:92]

            previous_left = (
                previous_features[50:92]
            )

            # Right hand
            current_right = features[92:134]

            previous_right = (
                previous_features[92:134]
            )

            # ------------------------------------------------
            # MediaPipe temporarily lost left hand.
            # ------------------------------------------------

            if np.all(
                current_left == 0
            ):

                features[50:92] = (
                    previous_left
                )

            # ------------------------------------------------
            # MediaPipe temporarily lost right hand.
            # ------------------------------------------------

            if np.all(
                current_right == 0
            ):

                features[92:134] = (
                    previous_right
                )

    return features


# ============================================================
# DRAW TEXT
# ============================================================

def draw_text(
    frame,
    text,
    position,
    scale=0.7,
    thickness=2,
):
    """
    Draw readable text with a dark outline.

    The outline makes the text visible
    against both bright and dark backgrounds.
    """

    text = str(text)

    x, y = position

    # --------------------------------------------------------
    # Black outline
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # White foreground
    # --------------------------------------------------------

    cv2.putText(
        frame,
        text,
        (x, y),
        cv2.FONT_HERSHEY_SIMPLEX,
        scale,
        (255, 255, 255),
        thickness,
        cv2.LINE_AA,
    )


# ============================================================
# DRAW LANDMARKS
# ============================================================

def draw_landmarks(
    frame,
    result,
):
    """
    Draw detected pose and hand landmarks.
    """

    height, width = frame.shape[:2]

    # ========================================================
    # POSE
    # ========================================================

    pose_landmarks = get_landmark_list(
        result.pose_landmarks
    )

    for landmark in pose_landmarks:

        x = int(
            landmark.x * width
        )

        y = int(
            landmark.y * height
        )

        if (
            0 <= x < width
            and
            0 <= y < height
        ):

            cv2.circle(
                frame,
                (x, y),
                2,
                (255, 255, 255),
                -1,
            )

    # ========================================================
    # LEFT HAND
    # ========================================================

    left_landmarks = get_landmark_list(
        result.left_hand_landmarks
    )

    for landmark in left_landmarks:

        x = int(
            landmark.x * width
        )

        y = int(
            landmark.y * height
        )

        if (
            0 <= x < width
            and
            0 <= y < height
        ):

            cv2.circle(
                frame,
                (x, y),
                3,
                (0, 255, 0),
                -1,
            )

    # ========================================================
    # RIGHT HAND
    # ========================================================

    right_landmarks = get_landmark_list(
        result.right_hand_landmarks
    )

    for landmark in right_landmarks:

        x = int(
            landmark.x * width
        )

        y = int(
            landmark.y * height
        )

        if (
            0 <= x < width
            and
            0 <= y < height
        ):

            cv2.circle(
                frame,
                (x, y),
                3,
                (0, 0, 255),
                -1,
            )


# ============================================================
# DRAW STATUS PANEL
# ============================================================

def draw_status_panel(
    frame,
    sequence_length,
    last_prediction,
    last_confidence,
    pose_count,
    left_count,
    right_count,
    prediction_count,
):
    """
    Draw the PAIOS status information.
    """

    height, width = frame.shape[:2]

    # --------------------------------------------------------
    # Semi-transparent panel
    # --------------------------------------------------------

    overlay = frame.copy()

    panel_height = 330

    cv2.rectangle(
        overlay,
        (10, 10),
        (
            min(470, width - 10),
            min(panel_height, height - 10),
        ),
        (0, 0, 0),
        -1,
    )

    frame[:] = cv2.addWeighted(
        overlay,
        0.60,
        frame,
        0.40,
        0,
    )

    # ========================================================
    # TITLE
    # ========================================================

    draw_text(
        frame,
        "PAIOS INCLUDE / ISL",
        (25, 45),
        0.85,
        2,
    )

    # ========================================================
    # SEQUENCE
    # ========================================================

    draw_text(
        frame,
        f"Frames: {sequence_length}/{SEQUENCE_LENGTH}",
        (25, 82),
        0.65,
        2,
    )

    # ========================================================
    # PREDICTION
    # ========================================================

    if sequence_length < SEQUENCE_LENGTH:

        draw_text(
            frame,
            "Status: Collecting...",
            (25, 120),
            0.65,
            2,
        )

    else:

        if (
            last_confidence
            >= CONFIDENCE_THRESHOLD
        ):

            draw_text(
                frame,
                f"Sign: {last_prediction}",
                (25, 120),
                0.82,
                2,
            )

            draw_text(
                frame,
                (
                    "Confidence: "
                    f"{last_confidence:.1%}"
                ),
                (25, 158),
                0.68,
                2,
            )

        else:

            draw_text(
                frame,
                "Sign: Uncertain",
                (25, 120),
                0.82,
                2,
            )

            draw_text(
                frame,
                (
                    "Prediction: "
                    f"{last_prediction}"
                ),
                (25, 158),
                0.62,
                2,
            )

    # ========================================================
    # LANDMARK STATUS
    # ========================================================

    draw_text(
        frame,
        f"Pose: {pose_count}",
        (25, 200),
        0.60,
        2,
    )

    draw_text(
        frame,
        f"Left hand: {left_count}",
        (25, 232),
        0.60,
        2,
    )

    draw_text(
        frame,
        f"Right hand: {right_count}",
        (25, 264),
        0.60,
        2,
    )

    draw_text(
        frame,
        f"Predictions: {prediction_count}",
        (25, 296),
        0.60,
        2,
    )


# ============================================================
# EXTRACT PREDICTION
# ============================================================

def parse_prediction(
    prediction,
):
    """
    Normalize different possible INCLUDE
    prediction return formats.

    Returns:

        label
        confidence
    """

    label = "unknown"
    confidence = 0.0

    # ========================================================
    # DICTIONARY
    # ========================================================

    if isinstance(
        prediction,
        dict,
    ):

        label = prediction.get(
            "label",
            prediction.get(
                "gesture",
                prediction.get(
                    "class",
                    "unknown",
                ),
            ),
        )

        confidence = prediction.get(
            "confidence",
            prediction.get(
                "score",
                0.0,
            ),
        )

    # ========================================================
    # TUPLE / LIST
    # ========================================================

    elif isinstance(
        prediction,
        (tuple, list),
    ):

        if len(prediction) > 0:
            label = prediction[0]

        if len(prediction) > 1:
            confidence = prediction[1]

    # ========================================================
    # RAW VALUE
    # ========================================================

    else:

        label = str(
            prediction
        )

    # ========================================================
    # SAFE CONVERSION
    # ========================================================

    try:
        confidence = float(
            confidence
        )
    except (
        TypeError,
        ValueError,
    ):
        confidence = 0.0

    # --------------------------------------------------------
    # Handle percentage-style confidence.
    #
    # If a model returns 80 instead of 0.80,
    # normalize it.
    # --------------------------------------------------------

    if confidence > 1.0:

        confidence /= 100.0

    confidence = max(
        0.0,
        min(
            1.0,
            confidence,
        ),
    )

    return (
        str(label),
        confidence,
    )


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 60)
    print(
        "🧠 PAIOS INCLUDE — "
        "RELIABLE ISL LIVE TEST"
    )
    print("=" * 60)

    print()
    print(
        f"Input features : {FEATURE_SIZE}"
    )

    print(
        f"Sequence length: {SEQUENCE_LENGTH}"
    )

    print(
        f"Classes        : {NUM_CLASSES}"
    )

    print(
        f"MediaPipe     : {MODEL_PATH}"
    )

    print()
    print("=" * 60)

    # ========================================================
    # LOAD MODEL
    # ========================================================

    model = None

    try:

        print()
        print(
            "🧠 Loading INCLUDE model..."
        )

        model = get_model()

        print()
        print(
            "✅ INCLUDE model ready"
        )

    except Exception as e:

        print()
        print(
            "❌ Failed to load INCLUDE model"
        )

        print(
            f"{type(e).__name__}: {e}"
        )

        traceback.print_exc()

        return

    # ========================================================
    # VERIFY MEDIAPIPE MODEL
    # ========================================================

    if not os.path.exists(
        MODEL_PATH
    ):

        print()
        print(
            "❌ MediaPipe model not found:"
        )

        print(
            MODEL_PATH
        )

        return

    # ========================================================
    # LOAD MEDIAPIPE
    # ========================================================

    landmarker = None

    try:

        print()
        print(
            "⏳ Loading MediaPipe Holistic..."
        )

        landmarker = (
            create_landmarker()
        )

        print(
            "✅ MediaPipe Holistic loaded"
        )

    except Exception as e:

        print()
        print(
            "❌ Failed to load MediaPipe"
        )

        print(
            f"{type(e).__name__}: {e}"
        )

        traceback.print_exc()

        return

    # ========================================================
    # OPEN CAMERA
    # ========================================================

    print()
    print(
        "🎥 Opening webcam..."
    )

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

        print(
            "❌ Could not open webcam."
        )

        landmarker.close()

        return

    # ========================================================
    # CAMERA SETTINGS
    # ========================================================

    cap.set(
        cv2.CAP_PROP_FRAME_WIDTH,
        1280,
    )

    cap.set(
        cv2.CAP_PROP_FRAME_HEIGHT,
        720,
    )

    print(
        "✅ Webcam opened"
    )

    print()
    print("-" * 60)
    print(
        "CONTROLS"
    )
    print("-" * 60)
    print(
        "Q = Quit"
    )
    print(
        "R = Reset sequence"
    )
    print("-" * 60)

    # ========================================================
    # SEQUENCE BUFFER
    # ========================================================

    sequence = deque(
        maxlen=SEQUENCE_LENGTH
    )

    previous_features = None

    # ========================================================
    # STATE
    # ========================================================

    frame_count = 0

    prediction_count = 0

    last_prediction = "Waiting..."

    last_confidence = 0.0

    last_pose_count = 0

    last_left_count = 0

    last_right_count = 0

    # ========================================================
    # CAMERA LOOP
    # ========================================================

    try:

        while True:

            # ==================================================
            # READ FRAME
            # ==================================================

            success, frame = cap.read()

            if not success:

                print(
                    "❌ Failed to read webcam frame."
                )

                continue

            frame_count += 1

            # ==================================================
            # MIRROR
            # ==================================================

            frame = cv2.flip(
                frame,
                1,
            )

            # ==================================================
            # BGR → RGB
            # ==================================================

            rgb = cv2.cvtColor(
                frame,
                cv2.COLOR_BGR2RGB,
            )

            # ==================================================
            # MEDIAPIPE IMAGE
            # ==================================================

            mp_image = Image(
                image_format=(
                    ImageFormat.SRGB
                ),
                data=rgb,
            )

            # ==================================================
            # DETECTION
            # ==================================================

            result = (
                landmarker.detect(
                    mp_image
                )
            )

            # ==================================================
            # LANDMARK LISTS
            # ==================================================

            pose_landmarks = (
                get_landmark_list(
                    result.pose_landmarks
                )
            )

            left_landmarks = (
                get_landmark_list(
                    result.left_hand_landmarks
                )
            )

            right_landmarks = (
                get_landmark_list(
                    result.right_hand_landmarks
                )
            )

            last_pose_count = len(
                pose_landmarks
            )

            last_left_count = len(
                left_landmarks
            )

            last_right_count = len(
                right_landmarks
            )

            # ==================================================
            # EXTRACT FEATURES
            # ==================================================

            features = extract_landmarks(
                result,
                previous_features,
            )

            previous_features = (
                features.copy()
            )

            # ==================================================
            # ADD TO SEQUENCE
            # ==================================================

            sequence.append(
                features
            )

            # ==================================================
            # PREDICTION
            # ==================================================

            if (
                len(sequence)
                >= SEQUENCE_LENGTH
                and
                frame_count
                % PREDICT_EVERY
                == 0
            ):

                input_sequence = (
                    np.asarray(
                        sequence,
                        dtype=np.float32,
                    )
                )

                try:

                    prediction = (
                        model.predict(
                            input_sequence
                        )
                    )

                    prediction_count += 1

                    (
                        label,
                        confidence,
                    ) = parse_prediction(
                        prediction
                    )

                    last_prediction = (
                        label
                    )

                    last_confidence = (
                        confidence
                    )

                except Exception as e:

                    print()
                    print(
                        "❌ Prediction error:"
                    )

                    print(
                        f"{type(e).__name__}: {e}"
                    )

            # ==================================================
            # TERMINAL DEBUG
            # ==================================================

            if frame_count % 30 == 0:

                print(
                    f"Frame {frame_count:5d} | "
                    f"Pose: {last_pose_count:2d} | "
                    f"Left hand: {last_left_count:2d} | "
                    f"Right hand: {last_right_count:2d} | "
                    f"Features: {features.shape[0]:3d} | "
                    f"Sequence: "
                    f"{len(sequence):3d}/"
                    f"{SEQUENCE_LENGTH} | "
                    f"Prediction: "
                    f"{last_prediction} | "
                    f"Confidence: "
                    f"{last_confidence:.2%}"
                )

            # ==================================================
            # DRAW LANDMARKS
            # ==================================================

            draw_landmarks(
                frame,
                result,
            )

            # ==================================================
            # DRAW UI
            # ==================================================

            draw_status_panel(
                frame=frame,
                sequence_length=len(
                    sequence
                ),
                last_prediction=(
                    last_prediction
                ),
                last_confidence=(
                    last_confidence
                ),
                pose_count=(
                    last_pose_count
                ),
                left_count=(
                    last_left_count
                ),
                right_count=(
                    last_right_count
                ),
                prediction_count=(
                    prediction_count
                ),
            )

            # ==================================================
            # INSTRUCTIONS
            # ==================================================

            draw_text(
                frame,
                (
                    "Show ONE sign | "
                    "R = Reset | Q = Quit"
                ),
                (
                    20,
                    frame.shape[0] - 25,
                ),
                0.60,
                2,
            )

            # ==================================================
            # DISPLAY
            # ==================================================

            cv2.imshow(
                "PAIOS - INCLUDE ISL",
                frame,
            )

            # ==================================================
            # KEYBOARD
            # ==================================================

            key = (
                cv2.waitKey(1)
                & 0xFF
            )

            # --------------------------------------------------
            # QUIT
            # --------------------------------------------------

            if key == ord("q"):

                break

            # --------------------------------------------------
            # RESET
            # --------------------------------------------------

            if key == ord("r"):

                sequence.clear()

                previous_features = None

                last_prediction = (
                    "Waiting..."
                )

                last_confidence = 0.0

                print()
                print(
                    "🔄 Recognition state reset."
                )

    except KeyboardInterrupt:

        print()
        print(
            "🛑 Interrupted by user."
        )

    except Exception as e:

        print()
        print("=" * 60)
        print(
            "❌ LIVE RECOGNITION ERROR"
        )
        print("=" * 60)

        print(
            f"{type(e).__name__}: {e}"
        )

        traceback.print_exc()

    finally:

        # ========================================================
        # CLEANUP
        # ========================================================

        cap.release()

        cv2.destroyAllWindows()

        if landmarker is not None:

            landmarker.close()

        print()
        print("=" * 60)
        print(
            "✅ PAIOS INCLUDE LIVE TEST FINISHED"
        )
        print("=" * 60)

        print(
            f"Frames processed : {frame_count}"
        )

        print(
            f"Predictions      : {prediction_count}"
        )

        print(
            f"Last prediction   : "
            f"{last_prediction}"
        )

        print(
            f"Last confidence   : "
            f"{last_confidence:.2%}"
        )

        print("=" * 60)


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()