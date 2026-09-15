"""
PAIOS temporal skeletal recognizer.

Provides debounce so a gesture must remain stable for several
frames before PAIOS accepts it as a command.
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from typing import Optional, Sequence

from .gestures import Gesture, GestureResult, classify_gesture


@dataclass(frozen=True)
class RecognitionEvent:
    gesture: Gesture
    command: str
    confidence: float


class SkeletalRecognizer:
    """
    Real-time gesture recognizer.

    Parameters
    ----------
    stable_frames:
        Number of consecutive matching frames required.

    cooldown_frames:
        Number of frames before the same gesture can trigger again.
    """

    def __init__(
        self,
        stable_frames: int = 8,
        cooldown_frames: int = 20,
    ) -> None:

        self.stable_frames = max(1, stable_frames)
        self.cooldown_frames = max(0, cooldown_frames)

        self.history: deque[Gesture] = deque(
            maxlen=self.stable_frames
        )

        self.cooldown = 0

        self.last_gesture = Gesture.UNKNOWN
        self.last_result: Optional[GestureResult] = None

    def reset(self) -> None:
        """Completely reset recognition state."""

        self.history.clear()
        self.cooldown = 0
        self.last_gesture = Gesture.UNKNOWN
        self.last_result = None

    def update(
        self,
        landmarks: Optional[Sequence[Sequence[float]]],
    ) -> Optional[RecognitionEvent]:
        """
        Process one frame.

        Returns an event only when a gesture becomes stable.
        """

        if self.cooldown > 0:
            self.cooldown -= 1

        if landmarks is None or len(landmarks) != 21:
            self.history.clear()
            self.last_result = None
            self.last_gesture = Gesture.UNKNOWN
            return None

        result = classify_gesture(landmarks)

        self.last_result = result

        # Unknown frames break the stability chain.
        if result.gesture == Gesture.UNKNOWN:
            self.history.clear()
            self.last_gesture = Gesture.UNKNOWN
            return None

        self.history.append(result.gesture)

        self.last_gesture = result.gesture

        # Not stable yet.
        if len(self.history) < self.stable_frames:
            return None

        # Every frame in the history must match.
        if len(set(self.history)) != 1:
            return None

        # Cooldown prevents repeated triggering.
        if self.cooldown > 0:
            return None

        self.cooldown = self.cooldown_frames

        return RecognitionEvent(
            gesture=result.gesture,
            command=result.command,
            confidence=result.confidence,
        )

    @property
    def stability(self) -> int:
        """Current number of matching frames."""

        if not self.history:
            return 0

        last = self.history[-1]

        return sum(
            1
            for gesture in self.history
            if gesture == last
        )