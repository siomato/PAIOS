import cv2
import mediapipe as mp
import numpy as np


# ============================================================
# CONFIGURATION
# ============================================================

WINDOW_NAME = "PAIOS - ISL MediaPipe Test"

POSE_POINTS = 25
HAND_POINTS = 21

FEATURE_SIZE = (
    POSE_POINTS * 2
    + HAND_POINTS * 2
    + HAND_POINTS * 2
)

assert FEATURE_SIZE == 134


# ============================================================
# MEDIAPIPE
# ============================================================

mp_holistic = mp.solutions.holistic
mp_drawing = mp.solutions.drawing_utils


# ============================================================
# LANDMARK EXTRACTION
# ============================================================

def extract_landmarks(results):
    """
    Extract exactly 134 values:

        Pose       = 25 × 2 = 50
        Left hand  = 21 × 2 = 42
        Right hand = 21 × 2 = 42

        Total = 134
    """

    # --------------------------------------------------------
    # Pose
    # --------------------------------------------------------

    pose = []

    if results.pose_landmarks:

        landmarks = results.pose_landmarks.landmark

        # INCLUDE expects 25 pose landmarks.
        # MediaPipe Pose provides 33.
        # Use the first 25 to maintain the required shape.
        for landmark in landmarks[:POSE_POINTS]:

            pose.extend([
                landmark.x,
                landmark.y
            ])

    else:

        pose = [0.0] * (POSE_POINTS * 2)


    # Safety
    if len(pose) < POSE_POINTS * 2:
        pose.extend(
            [0.0] * (
                POSE_POINTS * 2 - len(pose)
            )
        )

    pose = pose[:POSE_POINTS * 2]


    # --------------------------------------------------------
    # Left hand
    # --------------------------------------------------------

    left_hand = []

    if results.left_hand_landmarks:

        for landmark in results.left_hand_landmarks.landmark:

            left_hand.extend([
                landmark.x,
                landmark.y
            ])

    else:

        left_hand = [0.0] * (HAND_POINTS * 2)


    # --------------------------------------------------------
    # Right hand
    # --------------------------------------------------------

    right_hand = []

    if results.right_hand_landmarks:

        for landmark in results.right_hand_landmarks.landmark:

            right_hand.extend([
                landmark.x,
                landmark.y
            ])

    else:

        right_hand = [0.0] * (HAND_POINTS * 2)


    # --------------------------------------------------------
    # Combine
    # --------------------------------------------------------

    features = (
        pose
        + left_hand
        + right_hand
    )

    features = np.asarray(
        features,
        dtype=np.float32
    )


    # --------------------------------------------------------
    # Final safety check
    # --------------------------------------------------------

    if features.shape != (134,):

        raise RuntimeError(
            f"Expected 134 features, "
            f"got {features.shape}"
        )

    return features


# ============================================================
# MAIN
# ============================================================

def main():

    print()
    print("=" * 60)
    print("🧪 PAIOS ISL MEDIAPIPE TEST")
    print("=" * 60)
    print()

    print("Expected features : 134")
    print("Pose features     : 50")
    print("Left hand         : 42")
    print("Right hand        : 42")
    print()

    # --------------------------------------------------------
    # Camera
    # --------------------------------------------------------

    camera = cv2.VideoCapture(0)

    if not camera.isOpened():

        print("❌ Could not open webcam.")
        return

    print("✅ Webcam opened.")
    print("📷 Show your upper body and hands.")
    print("⌨️ Press Q to quit.")
    print()

    # --------------------------------------------------------
    # MediaPipe Holistic
    # --------------------------------------------------------

    with mp_holistic.Holistic(
        static_image_mode=False,
        model_complexity=1,
        smooth_landmarks=True,
        enable_segmentation=False,
        refine_face_landmarks=False,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5,
    ) as holistic:

        while True:

            success, frame = camera.read()

            if not success:

                print("⚠️ Failed to read webcam frame.")
                continue


            # ------------------------------------------------
            # Mirror camera
            # ------------------------------------------------

            frame = cv2.flip(frame, 1)


            # ------------------------------------------------
            # BGR → RGB
            # ------------------------------------------------

            rgb = cv2.cvtColor(
                frame,
                cv2.COLOR_BGR2RGB
            )

            rgb.flags.writeable = False


            # ------------------------------------------------
            # MediaPipe
            # ------------------------------------------------

            results = holistic.process(rgb)


            # ------------------------------------------------
            # Extract 134 features
            # ------------------------------------------------

            try:

                features = extract_landmarks(results)

                feature_count = len(features)

                status = "134 FEATURES OK"

            except Exception as error:

                feature_count = 0

                status = f"ERROR: {error}"


            # ------------------------------------------------
            # Draw landmarks
            # ------------------------------------------------

            if results.pose_landmarks:

                mp_drawing.draw_landmarks(
                    frame,
                    results.pose_landmarks,
                    mp_holistic.POSE_CONNECTIONS
                )


            if results.left_hand_landmarks:

                mp_drawing.draw_landmarks(
                    frame,
                    results.left_hand_landmarks,
                    mp_holistic.HAND_CONNECTIONS
                )


            if results.right_hand_landmarks:

                mp_drawing.draw_landmarks(
                    frame,
                    results.right_hand_landmarks,
                    mp_holistic.HAND_CONNECTIONS
                )


            # ------------------------------------------------
            # Status
            # ------------------------------------------------

            cv2.putText(
                frame,
                f"Features: {feature_count}/134",
                (20, 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (0, 255, 0),
                2
            )

            cv2.putText(
                frame,
                status,
                (20, 75),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 255, 0),
                2
            )

            cv2.putText(
                frame,
                "Q = Quit",
                (20, 110),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (255, 255, 255),
                2
            )


            # ------------------------------------------------
            # Display
            # ------------------------------------------------

            cv2.imshow(
                WINDOW_NAME,
                frame
            )


            # ------------------------------------------------
            # Quit
            # ------------------------------------------------

            key = cv2.waitKey(1) & 0xFF

            if key == ord("q"):

                break


    # --------------------------------------------------------
    # Cleanup
    # --------------------------------------------------------

    camera.release()

    cv2.destroyAllWindows()

    print()
    print("=" * 60)
    print("✅ MEDIAPIPE TEST FINISHED")
    print("=" * 60)
    print()


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()