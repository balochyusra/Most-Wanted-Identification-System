"""
Match Log Pydantic Models
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class MatchLogOut(BaseModel):
    id: str
    criminal_id: str
    criminal_name: str
    confidence: float          # percentage 0-100
    snapshot_path: Optional[str] = None
    camera_index: int = 0
    timestamp: datetime

    class Config:
        from_attributes = True


class AlertPayload(BaseModel):
    """Sent over WebSocket when a match is found"""
    event: str = "ALERT"
    criminal_id: str
    criminal_name: str
    alias: Optional[str] = None
    crime: str
    danger_level: str
    confidence: float
    snapshot_path: Optional[str] = None
    timestamp: str
