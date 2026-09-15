"""
PAIOS Skeletal Gesture Command Engine.

Training-free hand gesture recognition using MediaPipe
21-point hand landmarks.
"""

from .gestures import Gesture, GestureResult
from .recognizer import SkeletalRecognizer

__all__ = [
    "Gesture",
    "GestureResult",
    "SkeletalRecognizer",
]