"""
Most-Wanted Identification System
FastAPI Application Entry Point
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import uvicorn
from pathlib import Path

from backend.database import connect_db, close_db
from backend.routes import criminals, detection, logs
from backend.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await connect_db()
    yield
    # Shutdown
    await close_db()


app = FastAPI(
    title="Most-Wanted Identification System",
    description="AI-powered offline surveillance system for identifying most-wanted criminals using facial recognition.",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS — allow React dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files (photos / snapshots)
Path("data/photos").mkdir(parents=True, exist_ok=True)
Path("data/snapshots").mkdir(parents=True, exist_ok=True)
app.mount("/data", StaticFiles(directory="data"), name="data")

# Routers
app.include_router(criminals.router, prefix="/api/criminals", tags=["Criminals"])
app.include_router(detection.router, prefix="/api/detection", tags=["Detection"])
app.include_router(logs.router, prefix="/api/logs", tags=["Logs"])


@app.get("/")
async def root():
    return {
        "system": "Most-Wanted Identification System",
        "status": "online",
        "version": "1.0.0",
    }


@app.get("/api/health")
async def health():
    return {"status": "ok"}


if __name__ == "__main__":
    uvicorn.run(
        "backend.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
    )
