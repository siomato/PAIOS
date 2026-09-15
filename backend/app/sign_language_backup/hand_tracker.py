import cv2
import mediapipe as mp

from mediapipe.tasks import python
from mediapipe.tasks.python import vision


class HandTracker:
    """
    PAIOS Hand Tracker.

    Responsibility:
        Camera frame
            ↓
        MediaPipe
            ↓
        21 hand landmarks

    This class does NOT:
        - recognize gestures
        - translate signs
        - communicate with PAIOS
    """

    def __init__(
        self,
        model_path="app/sign_language/models/hand_landmarker.task",
        max_hands=2,
        detection_confidence=0.5,
        presence_confidence=0.5,
        tracking_confidence=0.5,
    ):

        self.model_path = model_path
        self.max_hands = max_hands

        self.detection_confidence = (
            detection_confidence
        )

        self.presence_confidence = (
            presence_confidence
        )

        self.tracking_confidence = (
            tracking_confidence
        )

        self.detector = None
        self.last_timestamp_ms = 0

        self._initialize()

    # =====================================================
    # INITIALIZE
    # =====================================================

    def _initialize(self):

        print(
            "🖐️ Initializing MediaPipe Hand Tracker..."
        )

        base_options = python.BaseOptions(
            model_asset_path=self.model_path
        )

        options = vision.HandLandmarkerOptions(
            base_options=base_options,
            running_mode=vision.RunningMode.VIDEO,
            num_hands=self.max_hands,
            min_hand_detection_confidence=(
                self.detection_confidence
            ),
            min_hand_presence_confidence=(
                self.presence_confidence
            ),
            min_tracking_confidence=(
                self.tracking_confidence
            ),
        )

        self.detector = (
            vision.HandLandmarker.create_from_options(
                options
            )
        )

        print(
            "✅ HAND TRACKER INITIALIZED"
        )

    # =====================================================
    # DETECT
    # =====================================================

    def detect(
        self,
        frame
    ):

        if frame is None:

            return None

        if self.detector is None:

            raise RuntimeError(
                "Hand tracker is not initialized."
            )

        # -------------------------------------------------
        # Timestamp MUST continuously increase
        # -------------------------------------------------

        timestamp_ms = int(
            cv2.getTickCount()
            /
            cv2.getTickFrequency()
            *
            1000
        )

        if timestamp_ms <= self.last_timestamp_ms:

            timestamp_ms = (
                self.last_timestamp_ms + 1
            )

        self.last_timestamp_ms = timestamp_ms

        # -------------------------------------------------
        # OpenCV BGR → RGB
        # -------------------------------------------------

        rgb_frame = cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2RGB
        )

        # -------------------------------------------------
        # MediaPipe image
        # -------------------------------------------------

        image = mp.Image(
            image_format=mp.ImageFormat.SRGB,
            data=rgb_frame
        )

        # -------------------------------------------------
        # Detect
        # -------------------------------------------------

        try:

            results = (
                self.detector.detect_for_video(
                    image,
                    timestamp_ms
                )
            )

            return results

        except Exception as error:

            print(
                f"⚠️ Hand tracking error: {error}"
            )

            return None

    # =====================================================
    # DRAW
    # =====================================================

    def draw(
        self,
        frame,
        results
    ):

        if frame is None:

            return frame

        if results is None:

            return frame

        hands = getattr(
            results,
            "hand_landmarks",
            None
        )

        if not hands:

            return frame

        height, width = (
            frame.shape[:2]
        )

        # Green
        GREEN = (0, 255, 0)

        # -------------------------------------------------
        # MediaPipe hand connections
        # -------------------------------------------------

        connections = [

            # Thumb
            (0, 1),
            (1, 2),
            (2, 3),
            (3, 4),

            # Index
            (0, 5),
            (5, 6),
            (6, 7),
            (7, 8),

            # Middle
            (0, 9),
            (9, 10),
            (10, 11),
            (11, 12),

            # Ring
            (0, 13),
            (13, 14),
            (14, 15),
            (15, 16),

            # Pinky
            (0, 17),
            (17, 18),
            (18, 19),
            (19, 20),

            # Palm
            (5, 9),
            (9, 13),
            (13, 17),
            (0, 5),
            (0, 17),
        ]

        # -------------------------------------------------
        # Draw every detected hand
        # -------------------------------------------------

        for hand in hands:

            points = []

            for landmark in hand:

                x = int(
                    landmark.x * width
                )

                y = int(
                    landmark.y * height
                )

                x = max(
                    0,
                    min(width - 1, x)
                )

                y = max(
                    0,
                    min(height - 1, y)
                )

                points.append(
                    (x, y)
                )

            # ---------------------------------------------
            # Skeleton
            # ---------------------------------------------

            for start, end in connections:

                if (
                    start < len(points)
                    and
                    end < len(points)
                ):

                    cv2.line(
                        frame,
                        points[start],
                        points[end],
                        GREEN,
                        2,
                        cv2.LINE_AA
                    )

            # ---------------------------------------------
            # Landmark points
            # ---------------------------------------------

            for point in points:

                cv2.circle(
                    frame,
                    point,
                    5,
                    GREEN,
                    -1,
                    cv2.LINE_AA
                )

                cv2.circle(
                    frame,
                    point,
                    2,
                    (0, 0, 0),
                    -1,
                    cv2.LINE_AA
                )

        return frame

    # =====================================================
    # GET LANDMARKS
    # =====================================================

    def get_landmarks(
        self,
        results
    ):

        if results is None:

            return []

        hands = getattr(
            results,
            "hand_landmarks",
            None
        )

        if not hands:

            return []

        return hands

    # =====================================================
    # HAND COUNT
    # =====================================================

    def hand_count(
        self,
        results
    ):

        return len(
            self.get_landmarks(results)
        )

    # =====================================================
    # CLOSE
    # =====================================================

    def close(self):

        if self.detector is not None:

            try:

                self.detector.close()

            except Exception as error:

                print(
                    f"⚠️ Tracker close error: {error}"
                )

            finally:

                self.detector = None

        print(
            "🖐️ HAND TRACKER CLOSED"
        )


# =========================================================
# STANDALONE TEST
# =========================================================

def tracker_test():

    camera = None
    tracker = None

    try:

        from app.sign_language.camera import Camera

        camera = Camera()

        tracker = HandTracker()

        camera.start()

        print()
        print("=" * 60)
        print("🖐️ PAIOS HAND TRACKER TEST")
        print("=" * 60)
        print()
        print("Show your hand to the camera.")
        print("Green landmarks should appear.")
        print("Press Q to quit.")
        print()

        while True:

            frame = camera.read()

            if frame is None:

                continue

            frame = cv2.flip(
                frame,
                1
            )

            results = tracker.detect(
                frame
            )

            tracker.draw(
                frame,
                results
            )

            count = tracker.hand_count(
                results
            )

            cv2.putText(
                frame,
                f"Hands: {count}",
                (20, 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (0, 255, 0),
                2
            )

            cv2.putText(
                frame,
                "PAIOS HAND TRACKER",
                (20, 75),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.65,
                (255, 255, 255),
                2
            )

            cv2.putText(
                frame,
                "Press Q to quit",
                (20, 110),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (255, 255, 255),
                2
            )

            cv2.imshow(
                "PAIOS HAND TRACKER TEST",
                frame
            )

            key = (
                cv2.waitKey(1)
                & 0xFF
            )

            if key == ord("q"):

                break

    except Exception as error:

        print()
        print(
            "❌ TRACKER TEST ERROR:"
        )

        print(error)

    finally:

        if camera is not None:

            camera.stop()

        if tracker is not None:

            tracker.close()

        cv2.destroyAllWindows()

        print(
            "✅ HAND TRACKER TEST FINISHED"
        )


# =========================================================
# MAIN
# =========================================================

if __name__ == "__main__":

    tracker_test()