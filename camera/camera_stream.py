"""
camera/camera_stream.py
Standalone script: runs the camera, does real-time face recognition,
prints alerts. Can run independently (without the FastAPI server).

Usage:
    python -m camera.camera_stream
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import asyncio
import cv2
import numpy as np
from datetime import datetime, timezone
from pathlib import Path

from backend.config import settings
from backend.database import connect_db, close_db, get_db
from backend.services.face_service import identify_face_in_frame, draw_annotations
from backend.services.alert_service import trigger_alert


async def load_criminals(db):
    """Load all criminals with encodings from MongoDB."""
    criminals = []
    async for doc in db["criminals"].find({"encoding": {"$ne": None}}):
        criminals.append(doc)
    return criminals


async def run_camera():
    await connect_db()
    db = get_db()

    cap = cv2.VideoCapture(settings.CAMERA_INDEX)
    if not cap.isOpened():
        print(f"[Camera] ERROR: Cannot open camera index {settings.CAMERA_INDEX}")
        await close_db()
        return

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    print(f"[Camera] Started. Press 'q' to quit.")

    frame_count = 0
    criminals = await load_criminals(db)
    print(f"[Camera] Loaded {len(criminals)} criminal(s) with face encodings.")

    while True:
        ret, frame = cap.read()
        if not ret:
            print("[Camera] Failed to grab frame.")
            break

        frame_count += 1
        display_frame = frame.copy()

        # Run recognition every 5 frames
        if frame_count % 5 == 0:
            # Reload criminals list every 50 frames to pick up new additions
            if frame_count % 50 == 0:
                criminals = await load_criminals(db)

            matches = await asyncio.to_thread(identify_face_in_frame, frame, criminals)

            if matches:
                for match in matches:
                    criminal = match["criminal"]
                    confidence = match["confidence"]

                    # Save snapshot
                    snap_dir = Path(settings.SNAPSHOTS_DIR)
                    snap_dir.mkdir(parents=True, exist_ok=True)
                    snap_name = f"{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S%f')}.jpg"
                    snap_path = str(snap_dir / snap_name)
                    cv2.imwrite(snap_path, frame)

                    # Save match log
                    log_doc = {
                        "criminal_id": criminal["_id"],
                        "criminal_name": criminal["name"],
                        "confidence": confidence,
                        "snapshot_path": snap_path,
                        "camera_index": settings.CAMERA_INDEX,
                        "timestamp": datetime.now(timezone.utc),
                    }
                    await db["match_logs"].insert_one(log_doc)

                    # Alert
                    trigger_alert(criminal, confidence)

                # Annotate frame
                display_frame = draw_annotations(display_frame, matches, [])

        # Overlay status
        status_text = f"Watching | Criminals loaded: {len(criminals)}"
        cv2.putText(display_frame, status_text, (10, 20),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
        cv2.putText(display_frame, f"Frame: {frame_count}", (10, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)

        cv2.imshow("Most-Wanted Identification System", display_frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()
    await close_db()
    print("[Camera] Stopped.")


if __name__ == "__main__":
    asyncio.run(run_camera())
