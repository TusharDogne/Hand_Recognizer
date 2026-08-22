from typing import Optional, Dict, Tuple

# Maps (left_gesture, right_gesture) -> command, matching the README's
# dual-hand interaction table.
DUAL_HAND_COMMANDS: Dict[Tuple[str, str], str] = {
    ("Pinch", "Pinch"): "scale",
    ("Open Palm", "Pinch"): "rotate",
    ("Point", "Point"): "select",
    ("Fist", "Open Palm"): "reset",
    ("Fist", "Fist"): "lock",
}


def resolve_command(left_gesture: Optional[str], right_gesture: Optional[str]) -> Optional[str]:
    """Look up the interaction command for a pair of hand gestures.
    Returns None if a hand is missing or the combo isn't mapped to a command."""
    if left_gesture is None or right_gesture is None:
        return None
    return DUAL_HAND_COMMANDS.get((left_gesture, right_gesture))