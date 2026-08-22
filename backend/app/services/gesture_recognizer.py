import math
from typing import List, Dict

# MediaPipe hand landmark indices
WRIST = 0
THUMB_TIP, THUMB_IP = 4, 3
INDEX_TIP, INDEX_PIP = 8, 6
MIDDLE_TIP, MIDDLE_PIP = 12, 10
RING_TIP, RING_PIP = 16, 14
PINKY_TIP, PINKY_PIP = 20, 18

# Normalized-distance threshold for a "pinch". MediaPipe landmarks are
# normalized to [0, 1] relative to the image, so this needs tuning against
# real camera footage (distance to camera changes the effective scale).
PINCH_THRESHOLD = 0.05


def _dist(a: Dict, b: Dict) -> float:
    return math.sqrt((a["x"] - b["x"]) ** 2 + (a["y"] - b["y"]) ** 2 + (a["z"] - b["z"]) ** 2)


def _finger_extended(landmarks: List[Dict], tip_idx: int, pip_idx: int) -> bool:
    """A finger counts as 'extended' if its tip sits farther from the wrist
    than its pip joint does — a simple, camera-angle-tolerant heuristic."""
    wrist = landmarks[WRIST]
    return _dist(landmarks[tip_idx], wrist) > _dist(landmarks[pip_idx], wrist)


def classify_gesture(landmarks: List[Dict]) -> str:
    """Classify one hand's 21 landmarks into one of the gestures listed in the README:
    Open Palm, Fist, Pinch, Point, Thumbs Up, Peace, OK, Rock."""
    if len(landmarks) != 21:
        return "Unknown"

    thumb_index_dist = _dist(landmarks[THUMB_TIP], landmarks[INDEX_TIP])

    thumb_ext = _finger_extended(landmarks, THUMB_TIP, THUMB_IP)
    index_ext = _finger_extended(landmarks, INDEX_TIP, INDEX_PIP)
    middle_ext = _finger_extended(landmarks, MIDDLE_TIP, MIDDLE_PIP)
    ring_ext = _finger_extended(landmarks, RING_TIP, RING_PIP)
    pinky_ext = _finger_extended(landmarks, PINKY_TIP, PINKY_PIP)

    num_extended = sum([index_ext, middle_ext, ring_ext, pinky_ext])

    # Pinch takes priority over other shapes since thumb+index nearly overlap.
    if thumb_index_dist < PINCH_THRESHOLD:
        if middle_ext and ring_ext and pinky_ext:
            return "OK"
        return "Pinch"

    if num_extended == 0 and not thumb_ext:
        return "Fist"

    if num_extended == 4 and thumb_ext:
        return "Open Palm"

    if index_ext and not middle_ext and not ring_ext and not pinky_ext:
        return "Point"

    if index_ext and middle_ext and not ring_ext and not pinky_ext:
        return "Peace"

    if index_ext and pinky_ext and not middle_ext and not ring_ext:
        return "Rock"

    if thumb_ext and num_extended == 0:
        return "Thumbs Up"

    return "Unknown"