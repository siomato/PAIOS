"""Activity-based segmentation for the isolated-sign INCLUDE model."""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from .preprocessing import SEQUENCE_LENGTH, hand_present


@dataclass
class SignSegmenter:
    max_frames: int = SEQUENCE_LENGTH
    end_grace_frames: int = 8
    min_frames: int = 12
    frames: list[np.ndarray] = field(default_factory=list)
    missing_count: int = 0
    active: bool = False

    def reset(self):
        self.frames.clear()
        self.missing_count = 0
        self.active = False

    def push(self, frame: np.ndarray):
        """Push a raw frame. Returns a completed raw clip or None."""
        present = hand_present(frame)
        if present:
            if not self.active:
                self.active = True
                self.frames.clear()
                self.missing_count = 0
            self.frames.append(np.asarray(frame, dtype=np.float32).copy())
            self.missing_count = 0
        elif self.active:
            self.frames.append(np.asarray(frame, dtype=np.float32).copy())
            self.missing_count += 1

        if not self.active:
            return None

        if len(self.frames) >= self.max_frames:
            return self._finish()

        if self.missing_count >= self.end_grace_frames:
            return self._finish()

        return None

    def _finish(self):
        clip = self.frames.copy()
        self.reset()
        if len(clip) < self.min_frames:
            return None
        return np.asarray(clip, dtype=np.float32)
