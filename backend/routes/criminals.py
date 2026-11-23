"""
Criminals CRUD Routes
POST   /api/criminals/           — Add criminal (with photo upload)
GET    /api/criminals/           — List all criminals
GET    /api/criminals/{id}       — Get one criminal
PUT    /api/criminals/{id}       — Update criminal info
DELETE /api/criminals/{id}       — Delete criminal
POST   /api/criminals/{id}/photo — Upload/replace photo
"""
import shutil
from pathlib import Path
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, UploadFile, File, Form, status
from bson import ObjectId

from backend.database import get_db
from backend.models.criminal import CriminalCreate, CriminalOut, CriminalUpdate
from backend.services.face_service import encode_face_from_path
from backend.config import settings

router = APIRouter()


def _serialize(doc: dict) -> dict:
    doc["id"] = str(doc.pop("_id"))
    doc["has_encoding"] = doc.get("encoding") is not None
    doc.pop("encoding", None)  # don't send encoding bytes over API
    return doc


@router.post("/", response_model=CriminalOut, status_code=status.HTTP_201_CREATED)
async def add_criminal(
    name: str = Form(...),
    crime: str = Form(...),
    alias: str = Form(None),
    danger_level: str = Form("medium"),
    nationality: str = Form(None),
    age: int = Form(None),
    description: str = Form(None),
    photo: UploadFile = File(None),
):
    db = get_db()
    photo_path = None
    encoding = None

    # Save photo if provided
    if photo and photo.filename:
        ext = Path(photo.filename).suffix.lower()
        allowed = {".jpg", ".jpeg", ".png", ".webp"}
        if ext not in allowed:
            raise HTTPException(400, "Only jpg/jpeg/png/webp images allowed.")
        photos_dir = Path(settings.PHOTOS_DIR)
        photos_dir.mkdir(parents=True, exist_ok=True)
        fname = f"{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S%f')}{ext}"
        dest = photos_dir / fname
        with open(dest, "wb") as f:
            shutil.copyfileobj(photo.file, f)
        photo_path = str(dest)

        # Try to encode face
        encoding = encode_face_from_path(photo_path)

    doc = {
        "name": name,
        "alias": alias,
        "crime": crime,
        "danger_level": danger_level,
        "nationality": nationality,
        "age": age,
        "description": description,
        "photo_path": photo_path,
        "encoding": encoding,  # list[float] or None
        "added_at": datetime.now(timezone.utc),
    }
    result = await db["criminals"].insert_one(doc)
    created = await db["criminals"].find_one({"_id": result.inserted_id})
    return _serialize(created)


@router.get("/", response_model=list[CriminalOut])
async def list_criminals():
    db = get_db()
    criminals = []
    async for doc in db["criminals"].find():
        criminals.append(_serialize(doc))
    return criminals


@router.get("/{criminal_id}", response_model=CriminalOut)
async def get_criminal(criminal_id: str):
    db = get_db()
    try:
        oid = ObjectId(criminal_id)
    except Exception:
        raise HTTPException(400, "Invalid ID format.")
    doc = await db["criminals"].find_one({"_id": oid})
    if not doc:
        raise HTTPException(404, "Criminal not found.")
    return _serialize(doc)


@router.put("/{criminal_id}", response_model=CriminalOut)
async def update_criminal(criminal_id: str, payload: CriminalUpdate):
    db = get_db()
    try:
        oid = ObjectId(criminal_id)
    except Exception:
        raise HTTPException(400, "Invalid ID format.")
    update_data = {k: v for k, v in payload.model_dump().items() if v is not None}
    if not update_data:
        raise HTTPException(400, "No update fields provided.")
    result = await db["criminals"].find_one_and_update(
        {"_id": oid},
        {"$set": update_data},
        return_document=True,
    )
    if not result:
        raise HTTPException(404, "Criminal not found.")
    return _serialize(result)


@router.delete("/{criminal_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_criminal(criminal_id: str):
    db = get_db()
    try:
        oid = ObjectId(criminal_id)
    except Exception:
        raise HTTPException(400, "Invalid ID format.")
    doc = await db["criminals"].find_one({"_id": oid})
    if not doc:
        raise HTTPException(404, "Criminal not found.")
    # Delete photo file if exists
    if doc.get("photo_path") and Path(doc["photo_path"]).exists():
        Path(doc["photo_path"]).unlink(missing_ok=True)
    await db["criminals"].delete_one({"_id": oid})


@router.post("/{criminal_id}/photo", response_model=CriminalOut)
async def upload_photo(criminal_id: str, photo: UploadFile = File(...)):
    db = get_db()
    try:
        oid = ObjectId(criminal_id)
    except Exception:
        raise HTTPException(400, "Invalid ID format.")
    doc = await db["criminals"].find_one({"_id": oid})
    if not doc:
        raise HTTPException(404, "Criminal not found.")

    ext = Path(photo.filename).suffix.lower()
    if ext not in {".jpg", ".jpeg", ".png", ".webp"}:
        raise HTTPException(400, "Only jpg/jpeg/png/webp images allowed.")

    photos_dir = Path(settings.PHOTOS_DIR)
    photos_dir.mkdir(parents=True, exist_ok=True)
    fname = f"{criminal_id}_{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S%f')}{ext}"
    dest = photos_dir / fname
    with open(dest, "wb") as f:
        shutil.copyfileobj(photo.file, f)

    photo_path = str(dest)
    encoding = encode_face_from_path(photo_path)

    updated = await db["criminals"].find_one_and_update(
        {"_id": oid},
        {"$set": {"photo_path": photo_path, "encoding": encoding}},
        return_document=True,
    )
    return _serialize(updated)
