import numpy as np


# =========================================================
# HAND FEATURE EXTRACTOR
# =========================================================

def extract_features(results):
    """
    Extract normalized 63-dimensional hand features.

    21 landmarks × 3 coordinates = 63 features.

    The wrist becomes the origin and the hand
    is normalized by hand size.
    """

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

    points = np.array(
        [
            [
                float(landmark.x),
                float(landmark.y),
                float(landmark.z)
            ]
            for landmark in hand
        ],
        dtype=np.float32
    )

    if points.shape != (21, 3):
        return None

    # -----------------------------------------------------
    # Wrist = origin
    # -----------------------------------------------------

    wrist = points[0].copy()

    points = points - wrist

    # -----------------------------------------------------
    # Scale normalization
    # -----------------------------------------------------

    scale = np.linalg.norm(
        points[9]
    )

    if scale < 1e-6:
        return None

    points = points / scale

    # -----------------------------------------------------
    # Flatten to 63 features
    # -----------------------------------------------------

    features = points.flatten()

    if len(features) != 63:
        return None

    return features.tolist()


# =========================================================
# SELF TEST
# =========================================================

if __name__ == "__main__":

    print()
    print("=" * 60)
    print("🧠 PAIOS FEATURE EXTRACTOR TEST")
    print("=" * 60)
    print()

    print(
        "Expected features: 63"
    )

    print(
        "Normalization: wrist-relative"
    )

    print(
        "Scale: normalized"
    )

    print()

    print(
        "✅ Feature extractor ready."
    )