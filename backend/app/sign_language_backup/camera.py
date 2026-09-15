import cv2


class Camera:
    """
    PAIOS Sign Language Camera

    Responsibility:
        - Open webcam
        - Read frames
        - Release webcam

    This class does NOT handle:
        - Hand detection
        - Gesture recognition
        - Translation
        - PAIOS communication
    """

    def __init__(
        self,
        camera_index=0,
        width=640,
        height=480,
        fps=30
    ):

        self.camera_index = camera_index
        self.width = width
        self.height = height
        self.fps = fps

        self.capture = None
        self.started = False

    # =====================================================
    # START CAMERA
    # =====================================================

    def start(self):

        if self.started and self.capture is not None:

            return True

        print(
            f"📷 Opening camera {self.camera_index}..."
        )

        self.capture = cv2.VideoCapture(
            self.camera_index,
            cv2.CAP_DSHOW
        )

        # -------------------------------------------------
        # Fallback if DirectShow cannot open the camera
        # -------------------------------------------------

        if not self.capture.isOpened():

            print(
                "⚠️ DirectShow failed."
            )

            print(
                "🔄 Trying default OpenCV backend..."
            )

            self.capture.release()

            self.capture = cv2.VideoCapture(
                self.camera_index
            )

        # -------------------------------------------------
        # Final check
        # -------------------------------------------------

        if not self.capture.isOpened():

            self.capture = None

            raise RuntimeError(
                f"❌ Could not open camera "
                f"{self.camera_index}"
            )

        # -------------------------------------------------
        # Camera configuration
        # -------------------------------------------------

        self.capture.set(
            cv2.CAP_PROP_FRAME_WIDTH,
            self.width
        )

        self.capture.set(
            cv2.CAP_PROP_FRAME_HEIGHT,
            self.height
        )

        self.capture.set(
            cv2.CAP_PROP_FPS,
            self.fps
        )

        self.started = True

        actual_width = int(
            self.capture.get(
                cv2.CAP_PROP_FRAME_WIDTH
            )
        )

        actual_height = int(
            self.capture.get(
                cv2.CAP_PROP_FRAME_HEIGHT
            )
        )

        actual_fps = self.capture.get(
            cv2.CAP_PROP_FPS
        )

        print(
            "✅ Camera opened successfully"
        )

        print(
            f"📐 Resolution: "
            f"{actual_width}x{actual_height}"
        )

        print(
            f"🎞️ FPS: {actual_fps:.1f}"
        )

        return True

    # =====================================================
    # READ FRAME
    # =====================================================

    def read(self):

        if not self.started:

            raise RuntimeError(
                "❌ Camera has not been started."
            )

        if self.capture is None:

            raise RuntimeError(
                "❌ Camera capture is unavailable."
            )

        success, frame = (
            self.capture.read()
        )

        if not success:

            print(
                "⚠️ Failed to read camera frame."
            )

            return None

        return frame

    # =====================================================
    # CHECK CAMERA
    # =====================================================

    def is_opened(self):

        if self.capture is None:

            return False

        return self.capture.isOpened()

    # =====================================================
    # STOP CAMERA
    # =====================================================

    def stop(self):

        if self.capture is not None:

            print(
                "📷 Releasing camera..."
            )

            self.capture.release()

            self.capture = None

        self.started = False

        print(
            "✅ Camera released."
        )

    # =====================================================
    # CONTEXT MANAGER SUPPORT
    # =====================================================

    def __enter__(self):

        self.start()

        return self

    def __exit__(
        self,
        exc_type,
        exc_value,
        traceback
    ):

        self.stop()


# =========================================================
# SIMPLE CAMERA TEST
# =========================================================

def camera_test():

    camera = Camera()

    try:

        camera.start()

        print()
        print(
            "📷 LIVE CAMERA TEST"
        )

        print(
            "Press Q to quit."
        )

        while True:

            frame = camera.read()

            if frame is None:

                continue

            # -------------------------------------------------
            # Mirror the webcam
            # -------------------------------------------------

            frame = cv2.flip(
                frame,
                1
            )

            # -------------------------------------------------
            # Camera information
            # -------------------------------------------------

            cv2.putText(
                frame,
                "PAIOS CAMERA",
                (20, 35),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (0, 255, 0),
                2
            )

            cv2.putText(
                frame,
                "Camera: ONLINE",
                (20, 70),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (0, 255, 0),
                2
            )

            cv2.putText(
                frame,
                "Press Q to quit",
                (20, 105),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (255, 255, 255),
                2
            )

            cv2.imshow(
                "PAIOS CAMERA TEST",
                frame
            )

            key = (
                cv2.waitKey(1)
                & 0xFF
            )

            if key == ord("q"):

                break

    except KeyboardInterrupt:

        print(
            "\n🛑 Camera test interrupted."
        )

    except Exception as error:

        print()
        print(
            "❌ CAMERA ERROR:"
        )

        print(
            error
        )

    finally:

        camera.stop()

        cv2.destroyAllWindows()

        print(
            "✅ Camera test finished."
        )


# =========================================================
# MAIN
# =========================================================

if __name__ == "__main__":

    camera_test()