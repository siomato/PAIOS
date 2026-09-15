"""
Geometry utilities for MediaPipe hand landmarks.

MediaPipe hand landmarks contain 21 points:

0  = WRIST

Thumb:
1  = CMC
2  = MCP
3  = IP
4  = TIP

Index:
5  = MCP
6  = PIP
7  = DIP
8  = TIP

Middle:
9  = MCP
10 = PIP
11 = DIP
12 = TIP

Ring:
13 = MCP
14 = PIP
15 = DIP
16 = TIP

Pinky:
17 = MCP
18 = PIP
19 = DIP
20 = TIP
"""

from __future__ import annotations

import math
from typing import Sequence


Point = Sequence[float]


def distance(a: Point, b: Point) -> float:
    """Euclidean distance between two points."""

    dx = float(a[0]) - float(b[0])
    dy = float(a[1]) - float(b[1])

    return math.sqrt(dx * dx + dy * dy)


def angle(a: Point, b: Point, c: Point) -> float:
    """
    Return angle ABC in degrees.

    180 degrees = almost straight.
    90 degrees  = right angle.
    """

    ax = float(a[0]) - float(b[0])
    ay = float(a[1]) - float(b[1])

    cx = float(c[0]) - float(b[0])
    cy = float(c[1]) - float(b[1])

    magnitude_a = math.sqrt(ax * ax + ay * ay)
    magnitude_c = math.sqrt(cx * cx + cy * cy)

    if magnitude_a < 1e-8 or magnitude_c < 1e-8:
        return 0.0

    cosine = (
        (ax * cx) + (ay * cy)
    ) / (magnitude_a * magnitude_c)

    cosine = max(-1.0, min(1.0, cosine))

    return math.degrees(math.acos(cosine))


def is_finger_extended(
    landmarks: Sequence[Point],
    mcp: int,
    pip: int,
    dip: int,
    tip: int,
    wrist: int = 0,
) -> bool:
    """
    Determine whether a non-thumb finger is extended.

    Uses both:
    - joint straightness
    - distance from wrist

    This is considerably more stable than using only Y coordinates.
    """

    pip_angle = angle(
        landmarks[mcp],
        landmarks[pip],
        landmarks[dip],
    )

    dip_angle = angle(
        landmarks[pip],
        landmarks[dip],
        landmarks[tip],
    )

    tip_distance = distance(
        landmarks[wrist],
        landmarks[tip],
    )

    pip_distance = distance(
        landmarks[wrist],
        landmarks[pip],
    )

    straight = pip_angle > 150.0 and dip_angle > 150.0
    farther = tip_distance > pip_distance * 1.08

    return straight and farther


def is_thumb_extended(
    landmarks: Sequence[Point],
) -> bool:
    """
    Determine whether the thumb is extended.

    Thumb:
    1 = CMC
    2 = MCP
    3 = IP
    4 = TIP
    """

    mcp_angle = angle(
        landmarks[1],
        landmarks[2],
        landmarks[3],
    )

    ip_angle = angle(
        landmarks[2],
        landmarks[3],
        landmarks[4],
    )

    tip_distance = distance(
        landmarks[0],
        landmarks[4],
    )

    mcp_distance = distance(
        landmarks[0],
        landmarks[2],
    )

    straight = mcp_angle > 145.0 and ip_angle > 145.0
    farther = tip_distance > mcp_distance * 1.12

    return straight and farther


def thumb_direction(
    landmarks: Sequence[Point],
) -> str:
    """
    Estimate thumb direction relative to the wrist.

    Image coordinates:
        smaller Y = upward
        larger Y = downward
    """

    wrist = landmarks[0]
    tip = landmarks[4]

    dy = float(tip[1]) - float(wrist[1])

    # Require meaningful displacement.
    if abs(dy) < 0.04:
        return "neutral"

    if dy < 0:
        return "up"

    return "down"


def finger_states(
    landmarks: Sequence[Point],
) -> dict[str, bool]:
    """Return extension state for all five fingers."""

    return {
        "thumb": is_thumb_extended(landmarks),
        "index": is_finger_extended(
            landmarks, 5, 6, 7, 8
        ),
        "middle": is_finger_extended(
            landmarks, 9, 10, 11, 12
        ),
        "ring": is_finger_extended(
            landmarks, 13, 14, 15, 16
        ),
        "pinky": is_finger_extended(
            landmarks, 17, 18, 19, 20
        ),
    }