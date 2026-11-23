# ⚠️ Most-Wanted Identification System

An AI-powered offline surveillance system that detects and identifies most-wanted criminals in real-time using facial recognition.

---

## 🏗 Architecture

```
Camera (Webcam/CCTV)
        │
        ▼
Face Detection (OpenCV + face_recognition / dlib)
        │
        ▼
Face Recognition → Match with MongoDB criminal encodings
        │
        ├── Match Found → Alert System (console + log) → Dashboard WebSocket alert
        │
        └── MongoDB (store match logs, snapshots)
        │
        ▼
FastAPI Backend ◄──► React Dashboard (live feed + alerts + criminal DB)
```

---

## 📁 Project Structure

```
D:\Python Project\
├── requirements.txt          ← Python dependencies
├── .env.example              ← Environment variable template
├── README.md
│
├── backend/
│   ├── main.py               ← FastAPI app entry point
│   ├── config.py             ← Settings (reads .env)
│   ├── database.py           ← MongoDB async connection (Motor)
│   ├── models/
│   │   ├── criminal.py       ← Criminal Pydantic models
│   │   └── log.py            ← MatchLog Pydantic models
│   ├── routes/
│   │   ├── criminals.py      ← CRUD API for criminals
│   │   ├── detection.py      ← Face detection + WebSocket stream
│   │   └── logs.py           ← Match logs API
│   ├── services/
│   │   ├── face_service.py   ← face_recognition + OpenCV logic
│   │   └── alert_service.py  ← Alert/notification logic
│   └── utils/
│       └── helpers.py
│
├── camera/
│   └── camera_stream.py      ← Standalone camera script (no browser needed)
│
├── data/                     ← Auto-created at runtime
│   ├── photos/               ← Criminal face photos
│   ├── snapshots/            ← Match snapshots
│   └── logs/                 ← Alert logs
│
└── frontend/
    ├── package.json
    ├── public/index.html
    └── src/
        ├── App.js            ← Main app + routing
        ├── App.css           ← Dark theme styles
        ├── index.js
        ├── components/
        │   ├── Dashboard.js  ← Live dashboard (stats + camera + logs)
        │   ├── CameraFeed.js ← Real-time WebSocket camera
        │   ├── CriminalList.js ← Criminal management
        │   ├── AddCriminal.js  ← Add criminal form
        │   └── LogTable.js   ← Match logs table
        └── services/
            └── api.js        ← Axios + WebSocket helpers
```

---

## ⚙️ Prerequisites

| Requirement | Version |
|-------------|---------|
| Python      | 3.10 – 3.12 |
| Node.js     | 18+ |
| MongoDB     | 6+ (running locally) |
| CMake       | (required to build dlib) |
| Visual C++ Build Tools | Windows only, for dlib |

---

## 🚀 Setup & Installation

### 1. Install dlib build prerequisites (Windows)

```powershell
# Install CMake from https://cmake.org/download/
# Install Visual Studio Build Tools from https://aka.ms/vs/17/release/vs_BuildTools.exe
# (select "Desktop development with C++")
```

### 2. Create virtual environment & install Python dependencies

```powershell
cd "D:\Python Project"
python -m venv .venv
.\.venv\Scripts\activate

pip install -r requirements.txt
```

> **Note:** `dlib` and `face_recognition` may take several minutes to compile.

### 3. Configure environment

```powershell
copy .env.example .env
# Edit .env as needed (MongoDB URI, camera index, etc.)
```

### 4. Start MongoDB

```powershell
# If installed as a service:
net start MongoDB

# Or run directly:
mongod --dbpath C:\data\db
```

### 5. Start the FastAPI backend

```powershell
cd "D:\Python Project"
.\.venv\Scripts\activate
python -m backend.main
# API: http://localhost:8000
# Docs: http://localhost:8000/docs
```

### 6. Start the React frontend

```powershell
cd "D:\Python Project\frontend"
npm install
npm start
# Dashboard: http://localhost:3000
```

---

## 📡 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/criminals/` | List all criminals |
| `POST` | `/api/criminals/` | Add criminal (multipart with photo) |
| `PUT` | `/api/criminals/{id}` | Update criminal info |
| `DELETE` | `/api/criminals/{id}` | Delete criminal |
| `POST` | `/api/criminals/{id}/photo` | Upload/replace face photo |
| `POST` | `/api/detection/identify` | Identify faces in uploaded image |
| `WS` | `/ws/stream` | Real-time camera stream + alerts |
| `GET` | `/api/logs/` | List match logs |
| `DELETE` | `/api/logs/` | Clear all logs |
| `GET` | `/docs` | Swagger API docs |

---

## 🎥 Standalone Camera Mode (no browser)

```powershell
cd "D:\Python Project"
.\.venv\Scripts\activate
python -m camera.camera_stream
# Press 'q' to quit the OpenCV window
```

---

## 🔧 Configuration (.env)

| Variable | Default | Description |
|----------|---------|-------------|
| `MONGO_URI` | `mongodb://localhost:27017` | MongoDB connection string |
| `MONGO_DB_NAME` | `most_wanted_db` | Database name |
| `FACE_TOLERANCE` | `0.5` | Match threshold (lower = stricter) |
| `CAMERA_INDEX` | `0` | Webcam index (0 = default) |
| `HOST` | `0.0.0.0` | Server host |
| `PORT` | `8000` | Server port |

---

## 🛡 Tech Stack

| Layer | Technology |
|-------|-----------|
| Face Detection | OpenCV + face_recognition (dlib) |
| Backend API | FastAPI + Uvicorn |
| Database | MongoDB (via Motor async driver) |
| Real-time Stream | WebSocket |
| Frontend | React 18 |
| Styling | Custom dark-theme CSS |

---

## 📌 Notes

- **100% Offline** — no internet required after setup
- Face encodings are stored as 128-dimension float vectors in MongoDB
- Snapshots of detections are saved to `data/snapshots/`
- Alert logs are written to `data/logs/alerts.log`
