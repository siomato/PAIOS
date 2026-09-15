"""Reliable INCLUDE inference wrapper."""
from __future__ import annotations

import numpy as np

from .preprocessing import preprocess_clip
from .pretrained_model import get_model


class INCLUDEPredictor:
    def __init__(self, confidence_threshold: float = 0.35):
        self.model = get_model()
        self.confidence_threshold = confidence_threshold

    def predict_raw(self, raw_clip):
        sequence = preprocess_clip(raw_clip)
        result = self.model.predict(sequence)
        result["sequence_shape"] = list(sequence.shape)
        return result

    def predict(self, raw_clip):
        result = self.predict_raw(raw_clip)
        result["accepted"] = bool(
            result.get("recognized") and
            float(result.get("confidence", 0.0)) >= self.confidence_threshold
        )
        return result
