"""
PAIOS training-free skeletal gesture classifier.

Supported gestures:

OPEN_PALM   -> STOP
THUMBS_UP   -> CONFIRM
THUMBS_DOWN -> REJECT
PEACE       -> NEXT
FIST        -> PAUSE
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Sequence

from .geometry import finger_states, thumb_direction


class Gesture(str, Enum):
    UNKNOWN = "UNKNOWN"

    OPEN_PALM = "OPEN_PALM"
    THUMBS_UP = "THUMBS_UP"
    THUMBS_DOWN = "THUMBS_DOWN"
    PEACE = "PEACE"
    FIST = "FIST"


@dataclass(frozen=True)
class GestureResult:
    gesture: Gesture
    confidence: float
    command: str
    states: dict[str, bool]


def classify_gesture(
    landmarks: Sequence[Sequence[float]],
) -> GestureResult:
    """
    Classify one MediaPipe hand skeleton.

    This is deterministic and requires no model training.
    """

    if landmarks is None or len(landmarks) != 21:
        return GestureResult(
            gesture=Gesture.UNKNOWN,
            confidence=0.0,
            command="UNKNOWN",
            states={},
        )

    states = finger_states(landmarks)

    thumb = states["thumb"]
    index = states["index"]
    middle = states["middle"]
    ring = states["ring"]
    pinky = states["pinky"]

    extended_count = sum(states.values())

    # ---------------------------------------------------------
    # OPEN PALM
    # ---------------------------------------------------------

    if extended_count == 5:
        return GestureResult(
            gesture=Gesture.OPEN_PALM,
            confidence=0.98,
            command="STOP",
            states=states,
        )

    # ---------------------------------------------------------
    # FIST
    # ---------------------------------------------------------

    if extended_count == 0:
        return GestureResult(
            gesture=Gesture.FIST,
            confidence=0.97,
            command="PAUSE",
            states=states,
        )

    # ---------------------------------------------------------
    # THUMBS UP / DOWN
    # ---------------------------------------------------------

    if (
        thumb
        and not index
        and not middle
        and not ring
        and not pinky
    ):
        direction = thumb_direction(landmarks)

        if direction == "up":
            return GestureResult(
                gesture=Gesture.THUMBS_UP,
                confidence=0.96,
                command="CONFIRM",
                states=states,
            )

        if direction == "down":
            return GestureResult(
                gesture=Gesture.THUMBS_DOWN,
                confidence=0.96,
                command="REJECT",
                states=states,
            )

    # ---------------------------------------------------------
    # PEACE / V SIGN
    # ---------------------------------------------------------

    if (
        not thumb
        and index
        and middle
        and not ring
        and not pinky
    ):
        return GestureResult(
            gesture=Gesture.PEACE,
            confidence=0.95,
            command="NEXT",
            states=states,
        )

    # ---------------------------------------------------------
    # UNKNOWN
    # ---------------------------------------------------------

    return GestureResult(
        gesture=Gesture.UNKNOWN,
        confidence=0.0,
        command="UNKNOWN",
        states=states,
    )