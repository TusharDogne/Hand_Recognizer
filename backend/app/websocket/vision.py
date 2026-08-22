import json
import logging
import time

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.services.hand_tracker import HandTracker
from app.services.gesture_recognizer import classify_gesture
from app.services.interaction_engine import resolve_command

logger = logging.getLogger("hand-pattern-ai.vision")

router = APIRouter()


@router.websocket("/ws/hand-tracking")
async def hand_tracking_ws(websocket: WebSocket):
    """
    Client -> Server, per message (JSON text):
        { "frame": "<base64 jpeg/png, optionally with data: prefix>" }

    Server -> Client, per message (JSON):
        {
          "hands": [
            {
              "handedness": "Left" | "Right",
              "confidence": 0.98,
              "landmarks": [ { "x":0.1, "y":0.2, "z":0.0 }, ... 21 points ],
              "gesture": "Pinch"
            }
          ],
          "command": {
            "command": "scale" | "rotate" | "select" | "reset" | "lock" | null,
            "left_gesture": "Pinch" | null,
            "right_gesture": "Pinch" | null
          },
          "timestamp": 1699999999.123
        }
    """
    await websocket.accept()
    tracker = HandTracker(max_hands=2)
    logger.info("Client connected to /ws/hand-tracking")

    try:
        while True:
            raw = await websocket.receive_text()

            try:
                payload = json.loads(raw)
                frame_b64 = payload.get("frame")
            except json.JSONDecodeError:
                # Fallback: allow sending the raw base64 string directly.
                frame_b64 = raw

            if not frame_b64:
                continue

            frame = tracker.decode_frame(frame_b64)
            if frame is None:
                await websocket.send_json({"error": "Could not decode frame"})
                continue

            raw_hands = tracker.process(frame)

            hands_out = []
            left_gesture = None
            right_gesture = None

            for hand in raw_hands:
                gesture = classify_gesture(hand["landmarks"])
                hands_out.append(
                    {
                        "handedness": hand["handedness"],
                        "confidence": hand["confidence"],
                        "landmarks": hand["landmarks"],
                        "gesture": gesture,
                    }
                )
                if hand["handedness"] == "Left":
                    left_gesture = gesture
                elif hand["handedness"] == "Right":
                    right_gesture = gesture

            command = resolve_command(left_gesture, right_gesture)

            await websocket.send_json(
                {
                    "hands": hands_out,
                    "command": {
                        "command": command,
                        "left_gesture": left_gesture,
                        "right_gesture": right_gesture,
                    },
                    "timestamp": time.time(),
                }
            )

    except WebSocketDisconnect:
        logger.info("Client disconnected from /ws/hand-tracking")
    finally:
        tracker.close()