"""
Helper utilities
"""
from bson import ObjectId


def object_id_to_str(oid) -> str:
    return str(oid) if isinstance(oid, ObjectId) else oid


def normalize_confidence(distance: float) -> float:
    """Convert face distance (0=identical, 1=very different) to % confidence."""
    return max(0.0, (1.0 - distance) * 100.0)


DANGER_COLORS = {
    "low": "#22c55e",
    "medium": "#f59e0b",
    "high": "#ef4444",
    "critical": "#7f1d1d",
}
