import base64
from typing import List, Dict, Optional

import cv2
import numpy as np
import mediapipe as mp

mp_hands = mp.solutions.hands


class HandTracker:
    """Wraps MediaPipe Hands to turn a raw camera frame into 21-point landmark data."""

    def __init__(
        self,
        max_hands: int = 2,
        detection_confidence: float = 0.6,
        tracking_confidence: float = 0.5,
    ):
        self.hands = mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=max_hands,
            min_detection_confidence=detection_confidence,
            min_tracking_confidence=tracking_confidence,
        )

    def decode_frame(self, base64_data: str) -> Optional[np.ndarray]:
        """Decode a base64 JPEG/PNG frame (with or without a data: URL prefix) into a BGR numpy array."""
        try:
            if "," in base64_data:
                base64_data = base64_data.split(",", 1)[1]
            img_bytes = base64.b64decode(base64_data)
            np_arr = np.frombuffer(img_bytes, dtype=np.uint8)
            frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
            return frame
        except Exception:
            return None

    def process(self, frame: np.ndarray) -> List[Dict]:
        """Run detection on a BGR frame. Returns a list of hands, each with
        handedness label, confidence, and 21 normalized (x, y, z) landmarks.

        Note: MediaPipe's Left/Right label assumes a non-mirrored (i.e. not
        selfie-view) image. If the frontend sends a mirrored webcam frame,
        flip the frame here (cv2.flip(frame, 1)) or swap the label before
        sending it back, so it visually matches the user's actual hand.
        """
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(rgb_frame)

        hands_data: List[Dict] = []
        if results.multi_hand_landmarks and results.multi_handedness:
            for hand_landmarks, handedness in zip(
                results.multi_hand_landmarks, results.multi_handedness
            ):
                landmarks = [
                    {"x": lm.x, "y": lm.y, "z": lm.z} for lm in hand_landmarks.landmark
                ]
                hands_data.append(
                    {
                        "handedness": handedness.classification[0].label,
                        "confidence": handedness.classification[0].score,
                        "landmarks": landmarks,
                    }
                )
        return hands_data

    def close(self):
        self.hands.close()