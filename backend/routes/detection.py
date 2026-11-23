"""
Detection Routes
POST /api/detection/identify  — Upload an image, check against DB
GET  /ws/stream               — WebSocket: real-time camera stream + alerts
"""
import base64
import json
import asyncio
from datetime import datetime, timezone
from pathlib import Path

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, UploadFile, File, HTTPException
from bson import ObjectId
import cv2
import numpy as np

from backend.database import get_db
from backend.services.face_service import identify_face_in_frame, encode_face_from_path
from backend.services.alert_service import trigger_alert
from backend.config import settings

router = APIRouter()


# ── REST: identify a single uploaded image ──────────────────────────────────
@router.post("/identify")
async def identify_image(photo: UploadFile = File(...)):
    """Upload an image and check if any face matches a criminal in the DB."""
    db = get_db()
    contents = await photo.read()
    nparr = np.frombuffer(contents, np.uint8)
    frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    if frame is None:
        raise HTTPException(400, "Could not decode image.")

    criminals = []
    async for doc in db["criminals"].find({"encoding": {"$ne": None}}):
        criminals.append(doc)

    matches = await asyncio.to_thread(identify_face_in_frame, frame, criminals)

    if not matches:
        return {"matched": False, "results": []}

    results = []
    for match in matches:
        results.append({
            "criminal_id": str(match["criminal"]["_id"]),
            "criminal_name": match["criminal"]["name"],
            "confidence": round(match["confidence"], 2),
        })

    return {"matched": True, "results": results}


# ── WebSocket: real-time camera stream ──────────────────────────────────────
active_connections: list[WebSocket] = []


@router.websocket("/ws/stream")
async def websocket_stream(websocket: WebSocket):
    await websocket.accept()
    active_connections.append(websocket)
    db = get_db()
    cap = None

    try:
        cap = cv2.VideoCapture(settings.CAMERA_INDEX)
        if not cap.isOpened():
            await websocket.send_json({"event": "ERROR", "message": "Cannot open camera."})
            return

        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

        frame_count = 0

        while True:
            ret, frame = cap.read()
            if not ret:
                await asyncio.sleep(0.1)
                continue

            frame_count += 1

            # Encode frame to JPEG → base64
            _, buffer = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 70])
            b64_frame = base64.b64encode(buffer).decode("utf-8")

            payload: dict = {
                "event": "FRAME",
                "frame": b64_frame,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

            # Run face recognition every 5 frames to reduce CPU load
            if frame_count % 5 == 0:
                criminals = []
                async for doc in db["criminals"].find({"encoding": {"$ne": None}}):
                    criminals.append(doc)

                if criminals:
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

                            # Save match log to DB
                            log_doc = {
                                "criminal_id": criminal["_id"],
                                "criminal_name": criminal["name"],
                                "confidence": confidence,
                                "snapshot_path": snap_path,
                                "camera_index": settings.CAMERA_INDEX,
                                "timestamp": datetime.now(timezone.utc),
                            }
                            await db["match_logs"].insert_one(log_doc)

                            # Trigger alert
                            await asyncio.to_thread(trigger_alert, criminal, confidence)

                            # Build alert payload
                            alert = {
                                "event": "ALERT",
                                "criminal_id": str(criminal["_id"]),
                                "criminal_name": criminal["name"],
                                "alias": criminal.get("alias"),
                                "crime": criminal["crime"],
                                "danger_level": criminal.get("danger_level", "medium"),
                                "confidence": round(confidence, 2),
                                "snapshot_path": snap_path,
                                "timestamp": datetime.now(timezone.utc).isoformat(),
                            }
                            payload["alert"] = alert

            await websocket.send_json(payload)
            await asyncio.sleep(0.033)  # ~30 FPS

    except WebSocketDisconnect:
        pass
    finally:
        if cap:
            cap.release()
        if websocket in active_connections:
            active_connections.remove(websocket)
