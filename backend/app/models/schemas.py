from typing import List, Optional
from pydantic import BaseModel


class Landmark(BaseModel):
    x: float
    y: float
    z: float


class HandData(BaseModel):
    handedness: str  # "Left" | "Right"
    confidence: float
    landmarks: List[Landmark]  # 21 points, MediaPipe order
    gesture: str


class InteractionCommand(BaseModel):
    command: Optional[str] = None
    left_gesture: Optional[str] = None
    right_gesture: Optional[str] = None


class TrackingResult(BaseModel):
    hands: List[HandData]
    command: InteractionCommand
    timestamp: float