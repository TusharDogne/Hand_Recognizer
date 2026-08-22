"""
Quick manual test for the /ws/hand-tracking WebSocket.

Usage:
    pip install websockets   # if not already installed
    python test_websocket.py path/to/a/photo_with_a_hand.jpg

What it does:
    1. Reads the image file, base64-encodes it.
    2. Connects to ws://localhost:8000/ws/hand-tracking
    3. Sends one frame.
    4. Prints the JSON response (hands, gestures, command).

Use a real photo that clearly shows one or two hands (e.g. a selfie holding
up a fist or open palm) — a blank/empty image will correctly return an empty
"hands" list, which just means no hand was detected, not that something is
broken.
"""

import asyncio
import base64
import json
import sys

import websockets

WS_URL = "ws://localhost:8000/ws/hand-tracking"


async def test(image_path: str):
    with open(image_path, "rb") as f:
        img_bytes = f.read()
    b64 = base64.b64encode(img_bytes).decode("utf-8")

    async with websockets.connect(WS_URL) as ws:
        print(f"Connected to {WS_URL}")
        await ws.send(json.dumps({"frame": f"data:image/jpeg;base64,{b64}"}))
        response = await ws.recv()
        data = json.loads(response)

        print("\n--- Response ---")
        print(f"Hands detected: {len(data.get('hands', []))}")
        for i, hand in enumerate(data.get("hands", [])):
            print(
                f"  Hand {i + 1}: {hand['handedness']} | "
                f"gesture={hand['gesture']} | confidence={hand['confidence']:.2f}"
            )
        print(f"Command: {data.get('command')}")
        print(f"Timestamp: {data.get('timestamp')}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python test_websocket.py path/to/image.jpg")
        sys.exit(1)

    asyncio.run(test(sys.argv[1]))