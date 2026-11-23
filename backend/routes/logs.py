"""
Match Logs Routes
GET /api/logs/        — List all match logs (newest first)
GET /api/logs/{id}    — Get single log
DELETE /api/logs/{id} — Delete a log entry
DELETE /api/logs/     — Clear all logs
"""
from fastapi import APIRouter, HTTPException, status
from bson import ObjectId
from datetime import datetime

from backend.database import get_db
from backend.models.log import MatchLogOut

router = APIRouter()


def _serialize(doc: dict) -> dict:
    doc["id"] = str(doc.pop("_id"))
    doc["criminal_id"] = str(doc.get("criminal_id", ""))
    return doc


@router.get("/", response_model=list[MatchLogOut])
async def list_logs(limit: int = 100):
    db = get_db()
    logs = []
    cursor = db["match_logs"].find().sort("timestamp", -1).limit(limit)
    async for doc in cursor:
        logs.append(_serialize(doc))
    return logs


@router.get("/{log_id}", response_model=MatchLogOut)
async def get_log(log_id: str):
    db = get_db()
    try:
        oid = ObjectId(log_id)
    except Exception:
        raise HTTPException(400, "Invalid ID format.")
    doc = await db["match_logs"].find_one({"_id": oid})
    if not doc:
        raise HTTPException(404, "Log not found.")
    return _serialize(doc)


@router.delete("/{log_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_log(log_id: str):
    db = get_db()
    try:
        oid = ObjectId(log_id)
    except Exception:
        raise HTTPException(400, "Invalid ID format.")
    result = await db["match_logs"].delete_one({"_id": oid})
    if result.deleted_count == 0:
        raise HTTPException(404, "Log not found.")


@router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
async def clear_logs():
    db = get_db()
    await db["match_logs"].delete_many({})
