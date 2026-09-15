"""
PAIOS INCLUDE-compatible preprocessing.

IMPORTANT:
The original AI4Bharat INCLUDE pipeline:
    25 pose landmarks
    21 left/first hand landmarks
    21 right/second hand landmarks

    = 134 x/y features

Original INCLUDE preprocessing:
    1. MediaPipe normalized coordinates
    2. Missing values represented as NaN
    3. Linear interpolation across time
    4. x multiplied by 1920
    5. y multiplied by 1080
    6. zero-padding to 200 frames

This implementation is adapted for the MediaPipe Tasks API used by PAIOS.
"""

from __future__ import annotations

import numpy as np


# ============================================================
# INCLUDE CONTRACT
# ============================================================

FEATURE_SIZE = 134
SEQUENCE_LENGTH = 200

FRAME_WIDTH = 1920.0
FRAME_HEIGHT = 1080.0

POSE_POINTS = 25
HAND_POINTS = 21


# ============================================================
# MEDIA PIPE POSE MAPPING
# ============================================================
#
# MediaPipe Tasks Holistic returns 33 pose landmarks.
#
# The original INCLUDE representation uses 25 pose points.
#
# These indices correspond to the INCLUDE-style 25-point
# representation:
#
# 0   nose
# 2   left eye
# 5   right eye
# 7   left ear
# 8   right ear
# 11  left shoulder
# 12  right shoulder
# 13  left elbow
# 14  right elbow
# 15  left wrist
# 16  right wrist
# 17  left pinky
# 18  right pinky
# 19  left index
# 20  right index
# 21  left thumb
# 22  right thumb
# 23  left hip
# 24  right hip
# 25  left knee
# 26  right knee
# 27  left ankle
# 28  right ankle
# 29  left heel
# 30  right heel
#
# ============================================================

POSE_INDICES = [
    0,
    2,
    5,
    7,
    8,
    11,
    12,
    13,
    14,
    15,
    16,
    17,
    18,
    19,
    20,
    21,
    22,
    23,
    24,
    25,
    26,
    27,
    28,
    29,
    30,
]


# ============================================================
# SAFE MEDIAPIPE LANDMARK EXTRACTION
# ============================================================

def _get_points(container):
    """
    Convert MediaPipe Tasks landmark containers into:

        [NormalizedLandmark, ...]

    Handles both possible structures:

        1. [landmark, landmark, ...]
        2. [[landmark, landmark, ...]]

    The installed PAIOS MediaPipe Tasks API normally uses
    structure #1.
    """

    if container is None:
        return []

    try:
        if len(container) == 0:
            return []

        first = container[0]

        # ----------------------------------------------------
        # Direct landmark list
        #
        # [NormalizedLandmark, NormalizedLandmark, ...]
        # ----------------------------------------------------

        if hasattr(first, "x") and hasattr(first, "y"):
            return list(container)

        # ----------------------------------------------------
        # Nested landmark list
        #
        # [[NormalizedLandmark, ...]]
        # ----------------------------------------------------

        if hasattr(first, "__iter__"):
            nested = list(first)

            if nested and hasattr(nested[0], "x"):
                return nested

    except (TypeError, IndexError):
        return []

    return []


# ============================================================
# CREATE XY ARRAY
# ============================================================

def _xy_from_points(points, count):
    """
    Convert landmarks into:

        [count, 2]

    Missing values are represented as NaN.

    This is intentional because the original INCLUDE
    preprocessing interpolates missing landmarks later.
    """

    output = np.full(
        (count, 2),
        np.nan,
        dtype=np.float32,
    )

    if not points:
        return output

    limit = min(
        count,
        len(points),
    )

    for i in range(limit):
        landmark = points[i]

        try:
            output[i, 0] = float(landmark.x)
            output[i, 1] = float(landmark.y)

        except (AttributeError, TypeError, ValueError):
            continue

    return output


# ============================================================
# POSE
# ============================================================

def _extract_pose(result):
    """
    Extract the INCLUDE 25-point pose representation.
    """

    output = np.full(
        (POSE_POINTS, 2),
        np.nan,
        dtype=np.float32,
    )

    points = _get_points(
        getattr(
            result,
            "pose_landmarks",
            None,
        )
    )

    if not points:
        return output

    for output_index, mp_index in enumerate(POSE_INDICES):

        if mp_index >= len(points):
            continue

        landmark = points[mp_index]

        try:
            output[output_index, 0] = float(
                landmark.x
            )

            output[output_index, 1] = float(
                landmark.y
            )

        except (
            AttributeError,
            TypeError,
            ValueError,
        ):
            continue

    return output


# ============================================================
# HAND
# ============================================================

def _extract_hand(result, attribute_name):
    """
    Extract one 21-point hand.

    MediaPipe Tasks provides semantic:

        left_hand_landmarks
        right_hand_landmarks

    INCLUDE uses two hand blocks:

        hand1
        hand2

    PAIOS maps:

        left  -> hand1
        right -> hand2
    """

    points = _get_points(
        getattr(
            result,
            attribute_name,
            None,
        )
    )

    return _xy_from_points(
        points,
        HAND_POINTS,
    )


# ============================================================
# RAW FRAME EXTRACTION
# ============================================================

def extract_frame(result) -> np.ndarray:
    """
    Extract one MediaPipe frame into the raw INCLUDE
    134-dimensional representation.

    Layout:

        [0:50]     = 25 pose landmarks × 2
        [50:92]    = 21 left-hand landmarks × 2
        [92:134]   = 21 right-hand landmarks × 2

    Missing landmarks remain NaN.

    Returns:
        np.ndarray shape (134,), dtype float32
    """

    pose = _extract_pose(
        result
    )

    left_hand = _extract_hand(
        result,
        "left_hand_landmarks",
    )

    right_hand = _extract_hand(
        result,
        "right_hand_landmarks",
    )

    features = np.concatenate(
        [
            pose.reshape(-1),
            left_hand.reshape(-1),
            right_hand.reshape(-1),
        ]
    ).astype(
        np.float32
    )

    if features.shape != (
        FEATURE_SIZE,
    ):
        raise RuntimeError(
            "Invalid INCLUDE feature vector: "
            f"{features.shape}; "
            f"expected ({FEATURE_SIZE},)"
        )

    return features


# ============================================================
# TEMPORAL INTERPOLATION
# ============================================================

def _interpolate(arr):
    """
    Reproduce INCLUDE's temporal interpolation.

    Missing values are filled using linear interpolation.

    At the beginning/end of a sequence, the nearest valid
    value is carried outward.

    If an entire feature is missing, it becomes zero.
    """

    arr = np.asarray(
        arr,
        dtype=np.float32,
    )

    if arr.ndim != 2:
        raise ValueError(
            f"Expected 2-D array, got {arr.shape}"
        )

    if arr.shape[0] == 0:
        return arr.copy()

    output = np.empty_like(
        arr
    )

    time_index = np.arange(
        arr.shape[0],
        dtype=np.float32,
    )

    for column in range(
        arr.shape[1]
    ):

        values = arr[:, column]

        valid = np.isfinite(
            values
        )

        # ----------------------------------------------------
        # Entire feature missing
        # ----------------------------------------------------

        if not valid.any():

            output[:, column] = 0.0

            continue

        # ----------------------------------------------------
        # Only one valid value
        # ----------------------------------------------------

        if valid.sum() == 1:

            value = values[
                valid
            ][0]

            output[:, column] = value

            continue

        # ----------------------------------------------------
        # Normal interpolation
        # ----------------------------------------------------

        output[:, column] = np.interp(
            time_index,
            time_index[valid],
            values[valid],
        ).astype(
            np.float32
        )

    return output


# ============================================================
# INCLUDE PREPROCESSING
# ============================================================

def preprocess_clip(
    frames,
) -> np.ndarray:
    """
    Convert raw MediaPipe frames:

        [T, 134]

    into INCLUDE model input:

        [200, 134]

    Processing:

        raw normalized coordinates
                    ↓
        temporal interpolation
                    ↓
        x × 1920
        y × 1080
                    ↓
        zero padding
                    ↓
        [200, 134]
    """

    data = np.asarray(
        frames,
        dtype=np.float32,
    )

    if data.ndim != 2:

        raise ValueError(
            "Expected [T, 134] input, "
            f"got {data.shape}"
        )

    if data.shape[1] != FEATURE_SIZE:

        raise ValueError(
            "Expected 134 features, "
            f"got {data.shape[1]}"
        )

    if data.shape[0] == 0:

        raise ValueError(
            "Cannot preprocess empty clip."
        )

    # --------------------------------------------------------
    # Interpolate missing landmarks
    # --------------------------------------------------------

    data = _interpolate(
        data
    )

    # --------------------------------------------------------
    # Convert:
    #
    # 134 = 67 landmarks × 2 coordinates
    # --------------------------------------------------------

    data = data.reshape(
        data.shape[0],
        67,
        2,
    )

    # --------------------------------------------------------
    # EXACT INCLUDE SCALING
    # --------------------------------------------------------

    data[:, :, 0] *= FRAME_WIDTH
    data[:, :, 1] *= FRAME_HEIGHT

    data = data.reshape(
        data.shape[0],
        FEATURE_SIZE,
    )

    # --------------------------------------------------------
    # Sequence length
    # --------------------------------------------------------

    if data.shape[0] > SEQUENCE_LENGTH:

        data = data[
            :SEQUENCE_LENGTH
        ]

    # --------------------------------------------------------
    # Zero padding
    #
    # Same behavior as original INCLUDE dataset.py
    # --------------------------------------------------------

    output = np.zeros(
        (
            SEQUENCE_LENGTH,
            FEATURE_SIZE,
        ),
        dtype=np.float32,
    )

    output[
        :data.shape[0]
    ] = data

    return output


# ============================================================
# HAND DETECTION
# ============================================================

def hand_present(
    frame: np.ndarray,
) -> bool:
    """
    Determine whether at least one hand contains
    valid landmark coordinates.

    Raw frame must contain NaN for missing landmarks.
    """

    frame = np.asarray(
        frame
    )

    if frame.shape != (
        FEATURE_SIZE,
    ):
        raise ValueError(
            f"Expected ({FEATURE_SIZE},), "
            f"got {frame.shape}"
        )

    hand_features = frame[
        50:134
    ]

    return bool(
        np.isfinite(
            hand_features
        ).any()
    )


# ============================================================
# DEBUG INFORMATION
# ============================================================

def feature_statistics(
    frame: np.ndarray,
):
    """
    Useful diagnostic information for live testing.

    Returns:
        {
            "pose_points": ...,
            "left_hand_points": ...,
            "right_hand_points": ...,
            "finite_features": ...,
            "feature_size": 134
        }
    """

    frame = np.asarray(
        frame
    )

    if frame.shape != (
        FEATURE_SIZE,
    ):
        raise ValueError(
            f"Expected ({FEATURE_SIZE},), "
            f"got {frame.shape}"
        )

    pose = frame[
        :50
    ]

    left = frame[
        50:92
    ]

    right = frame[
        92:134
    ]

    return {
        "pose_points": int(
            np.isfinite(
                pose
            ).sum() // 2
        ),
        "left_hand_points": int(
            np.isfinite(
                left
            ).sum() // 2
        ),
        "right_hand_points": int(
            np.isfinite(
                right
            ).sum() // 2
        ),
        "finite_features": int(
            np.isfinite(
                frame
            ).sum()
        ),
        "feature_size": FEATURE_SIZE,
    }


# ============================================================
# SELF TEST
# ============================================================

if __name__ == "__main__":

    print("=" * 60)
    print("🧪 PAIOS INCLUDE PREPROCESSING TEST")
    print("=" * 60)

    # Create a fake raw sequence containing valid
    # normalized coordinates.

    dummy = np.full(
        (
            20,
            FEATURE_SIZE,
        ),
        np.nan,
        dtype=np.float32,
    )

    # Put some valid coordinates into the hand area.

    dummy[
        :,
        50
    ] = 0.5

    dummy[
        :,
        51
    ] = 0.5

    print()
    print(
        f"Raw shape       : {dummy.shape}"
    )

    processed = preprocess_clip(
        dummy
    )

    print(
        f"Processed shape : {processed.shape}"
    )

    print(
        f"Processed dtype : {processed.dtype}"
    )

    print(
        f"Expected shape  : "
        f"({SEQUENCE_LENGTH}, {FEATURE_SIZE})"
    )

    # 0.5 × 1920 = 960
    # 0.5 × 1080 = 540

    print()
    print(
        f"Scaled X        : "
        f"{processed[0, 50]:.1f}"
    )

    print(
        f"Scaled Y        : "
        f"{processed[0, 51]:.1f}"
    )

    assert processed.shape == (
        SEQUENCE_LENGTH,
        FEATURE_SIZE,
    )

    assert processed.dtype == np.float32

    assert abs(
        processed[0, 50] - 960.0
    ) < 0.001

    assert abs(
        processed[0, 51] - 540.0
    ) < 0.001

    print()
    print("✅ Preprocessing test PASSED")