"""
Face Detection & Recognition Service
Uses mediapipe for face detection (no cmake/dlib needed).
Falls back to opencv haarcascade if mediapipe unavailable.

For production-grade matching, face_recognition (dlib) can be swapped in
by setting USE_DLIB=True in .env after installing cmake + dlib.
"""
from __future__ import annotations
import os
import cv2
import numpy as np
from pathlib import Path
from typing import Optional
from backend.config import settings

# ── Try importing face_recognition (dlib) first, fall back to mediapipe ───
USE_DLIB = os.getenv("USE_DLIB", "false").lower() == "true"
_face_recognition = None
_mp_face = None
_mp_drawing = None

if USE_DLIB:
    try:
        import face_recognition as _face_recognition
        print("[FaceService] Using face_recognition (dlib) backend.")
    except ImportError:
        print("[FaceService] dlib not available, falling back to mediapipe.")
        USE_DLIB = False

if not USE_DLIB:
    try:
        import mediapipe as mp
        _mp_face = mp.solutions.face_detection
        print("[FaceService] Using mediapipe face detection backend.")
    except ImportError:
        print("[FaceService] mediapipe not available, falling back to OpenCV Haar cascade.")

# ── OpenCV Haar cascade as last resort ────────────────────────────────────
_haar_cascade = None


def _get_haar():
    global _haar_cascade
    if _haar_cascade is None:
        cascade_path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
        _haar_cascade = cv2.CascadeClassifier(cascade_path)
    return _haar_cascade


# ══════════════════════════════════════════════════════════════════════════
#  Public API
# ══════════════════════════════════════════════════════════════════════════

def encode_face_from_path(image_path: str) -> Optional[list[float]]:
    """
    Load an image, detect a face, and return its encoding as a list[float].
    Returns None if no face detected or encoding unavailable.
    """
    if USE_DLIB and _face_recognition:
        try:
            img = _face_recognition.load_image_file(image_path)
            encodings = _face_recognition.face_encodings(img)
            if encodings:
                return encodings[0].tolist()
        except Exception as e:
            print(f"[FaceService] dlib encode error: {e}")
        return None

    # mediapipe / haar: return a simple pixel-histogram as a pseudo-encoding
    # (not as accurate as dlib, but functional for demo)
    try:
        img = cv2.imread(image_path)
        if img is None:
            return None
        faces = _detect_faces_cv(img)
        if not faces:
            return None
        x, y, w, h = faces[0]
        face_roi = img[y:y+h, x:x+w]
        face_roi = cv2.resize(face_roi, (64, 64))
        gray = cv2.cvtColor(face_roi, cv2.COLOR_BGR2GRAY)
        # 256-bin histogram as pseudo-encoding
        hist = cv2.calcHist([gray], [0], None, [128], [0, 256])
        cv2.normalize(hist, hist)
        return hist.flatten().tolist()
    except Exception as e:
        print(f"[FaceService] encode error: {e}")
        return None


def identify_face_in_frame(
    frame: np.ndarray,
    criminals: list[dict],
) -> list[dict]:
    """
    Given a BGR frame and list of criminal docs with 'encoding',
    return list of {criminal, confidence} dicts for matches found.
    """
    if not criminals:
        return []

    if USE_DLIB and _face_recognition:
        return _identify_dlib(frame, criminals)

    return _identify_histogram(frame, criminals)


def draw_annotations(
    frame: np.ndarray,
    matches: list[dict],
    face_locations: list,
) -> np.ndarray:
    """Draw bounding boxes + labels on the frame."""
    detected = _detect_faces_cv(frame)
    for i, (x, y, w, h) in enumerate(detected):
        name = matches[i]["criminal"]["name"] if i < len(matches) else "Unknown"
        conf = matches[i]["confidence"] if i < len(matches) else 0
        color = (0, 0, 255)
        cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
        label = f"{name} ({conf:.0f}%)"
        cv2.rectangle(frame, (x, y + h - 24), (x + w, y + h), color, cv2.FILLED)
        cv2.putText(frame, label, (x + 4, y + h - 6),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
    return frame


# ══════════════════════════════════════════════════════════════════════════
#  Internal helpers
# ══════════════════════════════════════════════════════════════════════════

def _detect_faces_cv(frame: np.ndarray) -> list[tuple]:
    """Detect faces using mediapipe or Haar cascade. Returns list of (x,y,w,h)."""
    if _mp_face:
        return _detect_faces_mediapipe(frame)
    return _detect_faces_haar(frame)


def _detect_faces_mediapipe(frame: np.ndarray) -> list[tuple]:
    try:
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w = frame.shape[:2]
        with _mp_face.FaceDetection(model_selection=0, min_detection_confidence=0.5) as det:
            results = det.process(rgb)
        if not results.detections:
            return []
        faces = []
        for det_result in results.detections:
            bb = det_result.location_data.relative_bounding_box
            x = max(0, int(bb.xmin * w))
            y = max(0, int(bb.ymin * h))
            fw = int(bb.width * w)
            fh = int(bb.height * h)
            faces.append((x, y, fw, fh))
        return faces
    except Exception as e:
        print(f"[FaceService] mediapipe error: {e}")
        return []


def _detect_faces_haar(frame: np.ndarray) -> list[tuple]:
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = _get_haar().detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
    if len(faces) == 0:
        return []
    return [tuple(f) for f in faces]


def _identify_dlib(frame: np.ndarray, criminals: list[dict]) -> list[dict]:
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    small = cv2.resize(rgb, (0, 0), fx=0.5, fy=0.5)
    locs = _face_recognition.face_locations(small, model="hog")
    if not locs:
        return []
    encodings = _face_recognition.face_encodings(small, locs)
    known_encs = [np.array(c["encoding"], dtype=np.float64) for c in criminals if c.get("encoding")]
    valid = [c for c in criminals if c.get("encoding")]
    if not known_encs:
        return []
    matches_found = []
    for enc in encodings:
        dists = _face_recognition.face_distance(known_encs, enc)
        idx = int(np.argmin(dists))
        dist = float(dists[idx])
        if dist <= settings.FACE_TOLERANCE:
            matches_found.append({
                "criminal": valid[idx],
                "confidence": (1.0 - dist) * 100.0,
            })
    return matches_found


def _identify_histogram(frame: np.ndarray, criminals: list[dict]) -> list[dict]:
    """Pseudo-matching using histogram correlation (demo quality)."""
    faces = _detect_faces_cv(frame)
    if not faces:
        return []

    matches_found = []
    for (x, y, w, h) in faces:
        roi = frame[y:y+h, x:x+w]
        roi = cv2.resize(roi, (64, 64))
        gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        hist = cv2.calcHist([gray], [0], None, [128], [0, 256])
        cv2.normalize(hist, hist)
        query_enc = hist.flatten()

        best_score = -1.0
        best_criminal = None
        for c in criminals:
            enc = c.get("encoding")
            if enc is None:
                continue
            known = np.array(enc, dtype=np.float32)
            query = query_enc.astype(np.float32)
            score = float(cv2.compareHist(
                known.reshape(-1, 1), query.reshape(-1, 1), cv2.HISTCMP_CORREL
            ))
            if score > best_score:
                best_score = score
                best_criminal = c

        # Threshold: correlation > 0.85 → match
        if best_criminal and best_score > 0.85:
            matches_found.append({
                "criminal": best_criminal,
                "confidence": best_score * 100.0,
            })

    return matches_found
