from __future__ import annotations

from collections import deque, Counter


class TemporalSmoother:
    """Debounce segment-level predictions; never alters confidence."""
    def __init__(self, window=3, required=2):
        self.history = deque(maxlen=window)
        self.required = required

    def clear(self):
        self.history.clear()

    def update(self, label: str, confidence: float):
        self.history.append((label, float(confidence)))
        counts = Counter(x[0] for x in self.history)
        candidate, count = counts.most_common(1)[0]
        if count < self.required:
            return {"stable": False, "label": candidate, "confidence": float(confidence)}
        vals = [c for l, c in self.history if l == candidate]
        return {"stable": True, "label": candidate, "confidence": sum(vals) / len(vals)}
