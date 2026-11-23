"""
Criminal Pydantic Models
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class CriminalCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100, description="Full name of the criminal")
    alias: Optional[str] = Field(None, description="Known alias or nickname")
    crime: str = Field(..., description="Crime(s) committed")
    danger_level: str = Field("medium", description="low | medium | high | critical")
    nationality: Optional[str] = None
    age: Optional[int] = None
    description: Optional[str] = None


class CriminalOut(BaseModel):
    id: str
    name: str
    alias: Optional[str] = None
    crime: str
    danger_level: str = "medium"
    nationality: Optional[str] = None
    age: Optional[int] = None
    description: Optional[str] = None
    photo_path: Optional[str] = None
    has_encoding: bool = False
    added_at: datetime

    class Config:
        from_attributes = True


class CriminalUpdate(BaseModel):
    name: Optional[str] = None
    alias: Optional[str] = None
    crime: Optional[str] = None
    danger_level: Optional[str] = None
    nationality: Optional[str] = None
    age: Optional[int] = None
    description: Optional[str] = None
