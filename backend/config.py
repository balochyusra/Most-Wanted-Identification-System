"""
Most-Wanted Identification System
Backend Configuration
"""
import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # MongoDB
    MONGO_URI: str = "mongodb://localhost:27017"
    MONGO_DB_NAME: str = "most_wanted_db"

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = True

    # Paths (strings, not Path objects — avoids pydantic coercion issues)
    PHOTOS_DIR: str = "data/photos"
    SNAPSHOTS_DIR: str = "data/snapshots"
    LOGS_DIR: str = "data/logs"

    # Face Recognition
    FACE_TOLERANCE: float = 0.5
    CAMERA_INDEX: int = 0

    # Alert
    ALERT_SOUND: bool = False


settings = Settings()

# Ensure data directories exist on import
for _d in [settings.PHOTOS_DIR, settings.SNAPSHOTS_DIR, settings.LOGS_DIR]:
    Path(_d).mkdir(parents=True, exist_ok=True)
