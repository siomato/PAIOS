"""PAIOS-facing adapter for the INCLUDE sign recognizer.

Model loading is lazy so importing FastAPI routes does not immediately load
46 MB of checkpoint weights.
"""
from __future__ import annotations

from app.sign_language.pretrained.predictor import INCLUDEPredictor


class SignLanguageAdapter:
    def __init__(self, confidence_threshold=0.35):
        self.confidence_threshold = confidence_threshold
        self._predictor = None
        self.last_result = None

    @property
    def predictor(self):
        if self._predictor is None:
            self._predictor = INCLUDEPredictor(self.confidence_threshold)
        return self._predictor

    def predict(self, raw_clip):
        result = self.predictor.predict(raw_clip)
        self.last_result = result
        return result

    def status(self):
        if self._predictor is None:
            return {
                "loaded": False,
                "classes": 263,
                "input_size": 134,
                "sequence_length": 200,
                "device": None,
                "last_result": self.last_result,
            }
        model = self.predictor.model
        return {
            "loaded": bool(model.loaded),
            "classes": len(model.labels),
            "input_size": 134,
            "sequence_length": 200,
            "device": str(model.device),
            "last_result": self.last_result,
        }
