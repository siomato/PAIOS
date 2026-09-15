import os
import json
import torch

from app.sign_language.pretrained.transformer_model import Transformer
from app.sign_language.pretrained.configs import TransformerConfig

# ============================================================
# PATHS
# ============================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

MODEL_PATH = os.path.join(
    BASE_DIR,
    "include_no_cnn_transformer_small.pth"
)

LABEL_PATH = os.path.join(
    BASE_DIR,
    "label_map_include.json"
)


# ============================================================
# INCLUDE PRETRAINED MODEL
# ============================================================

class INCLUDEModel:

    def __init__(self):

        self.device = torch.device(
            "cuda" if torch.cuda.is_available() else "cpu"
        )

        self.model = None
        self.labels = {}
        self.loaded = False
        self.num_classes = 0
        self.input_size = 134
        self.sequence_length = 200

        self._load_labels()
        self._load_model()


    # ========================================================
    # LOAD LABELS
    # ========================================================

    def _load_labels(self):

        if not os.path.exists(LABEL_PATH):

            raise FileNotFoundError(
                f"INCLUDE label map not found:\n"
                f"{LABEL_PATH}"
            )

        with open(
            LABEL_PATH,
            "r",
            encoding="utf-8"
        ) as file:

            self.labels = json.load(file)

        print(
            f"🏷️ INCLUDE labels loaded: "
            f"{len(self.labels)}"
        )


    # ========================================================
    # LOAD MODEL
    # ========================================================

    def _load_model(self):

        print()
        print("=" * 60)
        print("🧠 PAIOS INCLUDE PRETRAINED MODEL")
        print("=" * 60)
        print()

        print(
            f"📁 Checkpoint:\n"
            f"   {MODEL_PATH}"
        )

        print(
            f"💻 Device: {self.device}"
        )

        if not os.path.exists(MODEL_PATH):

            raise FileNotFoundError(
                f"INCLUDE checkpoint not found:\n"
                f"{MODEL_PATH}"
            )

        print()
        print(
            "⏳ Loading checkpoint..."
        )

        checkpoint = torch.load(
            MODEL_PATH,
            map_location=self.device,
            weights_only=False
        )

        if not isinstance(checkpoint, dict):

            raise RuntimeError(
                "Invalid INCLUDE checkpoint."
            )

        if "model" not in checkpoint:

            raise RuntimeError(
                "Checkpoint does not contain "
                "'model' weights."
            )

        # ----------------------------------------------------
        # Transformer configuration
        # ----------------------------------------------------

        config = TransformerConfig(
            size="small"
        )

        self.model = Transformer(
            config,
            n_classes=len(self.labels)
        )
        self.num_classes = len(self.labels)

        # ----------------------------------------------------
        # Load pretrained weights
        # ----------------------------------------------------

        self.model.load_state_dict(
            checkpoint["model"],
            strict=True
        )

        self.model.to(
            self.device
        )

        self.model.eval()

        self.loaded = True

        print()
        print(
            "✅ INCLUDE Transformer loaded."
        )

        print(
            f"🏷️ Classes: {len(self.labels)}"
        )

        print(
            f"📐 Input size: {config.input_size}"
        )

        print(
            f"🧠 Hidden size: {config.hidden_size}"
        )

        print(
            f"⚡ Device: {self.device}"
        )


    # ========================================================
    # PREDICT
    # ========================================================

    def predict(self, sequence):

        if not self.loaded:

            return {
                "gesture": "UNKNOWN",
                "confidence": 0.0,
                "recognized": False
            }

        if sequence is None:

            return {
                "gesture": "UNKNOWN",
                "confidence": 0.0,
                "recognized": False
            }

        # Convert input to tensor
        tensor = torch.tensor(
            sequence,
            dtype=torch.float32,
            device=self.device
        )

        # Expected:
        #
        # [frames, 134]
        #
        if tensor.ndim == 2:

            tensor = tensor.unsqueeze(0)

        if tensor.ndim != 3:

            raise ValueError(
                "INCLUDE input must have shape "
                "[frames, 134] or [batch, frames, 134]"
            )

        if tensor.shape[-1] != self.input_size:

            raise ValueError(
                f"Expected {self.input_size} features, "
                f"got {tensor.shape[-1]}"
            )

        with torch.no_grad():

            output = self.model(
                tensor
            )

            probabilities = torch.softmax(
                output,
                dim=-1
            )

            confidence, index = torch.max(
                probabilities,
                dim=-1
            )

        confidence = float(
            confidence[0].item()
        )

        index = int(
            index[0].item()
        )

        # Reverse label map
        reverse_labels = {
            int(value): key
            for key, value in self.labels.items()
        }

        gesture = reverse_labels.get(
            index,
            "UNKNOWN"
        )

        return {
            "gesture": gesture,
            "confidence": confidence,
            "recognized": True
        }


# ============================================================
# SINGLETON
# ============================================================

_model = None


def get_model():

    global _model

    if _model is None:

        _model = INCLUDEModel()

    return _model


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    print()
    print("=" * 60)
    print("🧪 PAIOS INCLUDE MODEL TEST")
    print("=" * 60)
    print()

    model = get_model()

    print()
    print("=" * 60)
    print("📊 MODEL STATUS")
    print("=" * 60)

    print(
        f"Loaded      : {model.loaded}"
    )

    print(
        f"Device      : {model.device}"
    )

    print(
        f"Classes     : {len(model.labels)}"
    )

    print()

    # Dummy sequence only to verify
    # model input/output compatibility.

    dummy_sequence = [
        [0.0] * 134
        for _ in range(256)
    ]

    result = model.predict(
        dummy_sequence
    )

    print("=" * 60)
    print("🧪 PREDICTION TEST")
    print("=" * 60)

    print(
        f"Gesture     : {result['gesture']}"
    )

    print(
        f"Confidence  : "
        f"{result['confidence'] * 100:.2f}%"
    )

    print(
        f"Recognized  : "
        f"{result['recognized']}"
    )

    print()
    print(
        "✅ INCLUDE model interface working."
    )