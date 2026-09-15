import os
import joblib
import numpy as np


class GestureModel:
    """
    PAIOS MLP Sign Language Recognition Model.

    Input:
        21 hand landmarks × (x, y, z)
        = 63 normalized features

    Output:
        Gesture
        Confidence
        Recognition status
    """

    def __init__(
        self,
        model_path=None,
        confidence_threshold=0.50
    ):

        if model_path is None:

            model_path = os.path.join(
                os.path.dirname(
                    os.path.abspath(__file__)
                ),
                "models",
                "gesture_model.joblib"
            )

        self.model_path = model_path

        self.confidence_threshold = (
            float(confidence_threshold)
        )

        self.model = None

        self._load()

    # =====================================================
    # LOAD MODEL
    # =====================================================

    def _load(self):

        if not os.path.isfile(
            self.model_path
        ):

            raise FileNotFoundError(
                "Gesture model not found:\n"
                f"{self.model_path}"
            )

        try:

            self.model = joblib.load(
                self.model_path
            )

        except Exception as error:

            raise RuntimeError(
                "Failed to load gesture model:\n"
                f"{error}"
            ) from error

        print(
            "🧠 MLP GESTURE MODEL LOADED"
        )

        print(
            f"📁 {self.model_path}"
        )

    # =====================================================
    # FEATURE VALIDATION
    # =====================================================

    @staticmethod
    def _validate_features(features):

        if features is None:
            return False

        try:

            values = np.asarray(
                features,
                dtype=np.float32
            )

        except Exception:

            return False

        if values.size != 63:
            return False

        if not np.all(
            np.isfinite(values)
        ):
            return False

        return True

    # =====================================================
    # PREDICT
    # =====================================================

    def predict(self, features):

        if self.model is None:

            raise RuntimeError(
                "Gesture model is not loaded."
            )

        if not self._validate_features(
            features
        ):

            return {
                "gesture": "UNKNOWN",
                "confidence": 0.0,
                "recognized": False
            }

        try:

            feature_array = np.asarray(
                features,
                dtype=np.float32
            ).reshape(1, -1)

            # -------------------------------------------------
            # Prediction
            # -------------------------------------------------

            prediction = self.model.predict(
                feature_array
            )[0]

            gesture = str(
                prediction
            )

            # -------------------------------------------------
            # Probability
            # -------------------------------------------------

            confidence = 0.0

            if hasattr(
                self.model,
                "predict_proba"
            ):

                probabilities = (
                    self.model.predict_proba(
                        feature_array
                    )[0]
                )

                confidence = float(
                    np.max(
                        probabilities
                    )
                )

            else:

                confidence = 1.0

            # -------------------------------------------------
            # Confidence gate
            # -------------------------------------------------

            recognized = (
                confidence
                >=
                self.confidence_threshold
            )

            if not recognized:

                return {
                    "gesture": "UNKNOWN",
                    "confidence": confidence,
                    "recognized": False
                }

            return {
                "gesture": gesture,
                "confidence": confidence,
                "recognized": True
            }

        except Exception as error:

            print(
                "⚠️ Gesture prediction error:"
            )

            print(
                f"   {error}"
            )

            return {
                "gesture": "UNKNOWN",
                "confidence": 0.0,
                "recognized": False
            }

    # =====================================================
    # GET CLASSES
    # =====================================================

    def get_classes(self):

        if self.model is None:
            return []

        try:

            # Pipeline → classifier
            classifier = (
                self.model.named_steps[
                    "classifier"
                ]
            )

            classes = getattr(
                classifier,
                "classes_",
                []
            )

            return [
                str(item)
                for item in classes
            ]

        except Exception:

            classes = getattr(
                self.model,
                "classes_",
                []
            )

            return [
                str(item)
                for item in classes
            ]

    # =====================================================
    # MODEL INFORMATION
    # =====================================================

    def info(self):

        return {
            "model_path": self.model_path,
            "classes": self.get_classes(),
            "confidence_threshold":
                self.confidence_threshold
        }

    # =====================================================
    # SELF TEST
    # =====================================================

    def test(self):

        print()
        print("=" * 60)
        print(
            "🧠 PAIOS MLP GESTURE MODEL TEST"
        )
        print("=" * 60)
        print()

        print(
            f"📁 Model:"
        )

        print(
            f"   {self.model_path}"
        )

        print()

        print(
            f"🏷️ Classes:"
        )

        print(
            f"   {self.get_classes()}"
        )

        print()

        print(
            f"🎯 Confidence threshold:"
        )

        print(
            f"   {self.confidence_threshold:.2f}"
        )

        print()

        print(
            "🧠 Model type:"
        )

        print(
            "   MLP Neural Network"
        )

        print()

        print(
            "✅ Gesture model loaded successfully."
        )

        print()


# =========================================================
# ENTRY POINT
# =========================================================

if __name__ == "__main__":

    model = GestureModel()

    model.test()