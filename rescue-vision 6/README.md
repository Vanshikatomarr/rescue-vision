# Rescue Vision — AI-Based Human Body Detection for Disaster Response

[![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.14-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.143.0-green.svg)](https://fastapi.tiangolo.com)
[![Ultralytics YOLO](https://img.shields.io/badge/YOLO-Ultralytics%20YOLO26-orange.svg)](https://docs.ultralytics.com)
[![React](https://img.shields.io/badge/React-18-cyan.svg)](https://react.dev)
[![Vite](https://img.shields.io/badge/Vite-5.4-purple.svg)](https://vitejs.dev)
[![TailwindCSS](https://img.shields.io/badge/Tailwind-3.4-38bdf8.svg)](https://tailwindcss.com)

**Rescue Vision** is a complete, full-stack, AI-assisted computer vision web application designed to help search and rescue teams (SAR) identify possible human presence in challenging disaster environments such as collapsed buildings, earthquake rubble, flood zones, landslide debris, and aerial drone sweeps.

---

## 🌟 Core Features & Pages

- **Mission Dashboard (`/dashboard`)**:
  - Real-time telemetry: media analyzed, human candidates found, open incidents, and mean latency.
  - Historical detections timeline area chart powered by Recharts.
  - Live system status pills (device CPU/CUDA and loaded checkpoint).
- **Tactical Detection Workspace (`/detect`)**:
  - Image detection (JPG, PNG, WEBP) with side-by-side original and annotated output previews.
  - Video analysis (MP4, AVI, MOV) with unique person ID tracking and frame-level statistics.
  - Configurable confidence threshold (10% - 90%) and image resolution settings (320px, 640px, 1280px).
  - JSON and CSV metadata export for incident reports.
- **Incident Geo-Management (`/incidents`)**:
  - Full CRUD for rescue incidents with priority, severity, and status tagging.
  - OpenStreetMap & Leaflet interactive map with custom tactical pins.
  - CSV export for on-site rescue team briefings.
- **Custom Model Training Center (`/training`)**:
  - YOLO dataset structure validator and sample dataset provisioner.
  - Non-blocking background training worker using Ultralytics PyTorch API.
  - Real-time epoch progress bar, loss/mAP convergence curves, and terminal stdout logs.
- **Model Registry & Hot-Swapping (`/models`)**:
  - Register, evaluate, and inspect model checkpoints with validation mAP scores.
  - Safe one-click activation with runtime weight verification.
- **Operational Analytics (`/analytics`)**:
  - Stored database ground truth analytics and model benchmark comparisons.
- **Application Settings (`/settings`)**:
  - Inference heuristics, device diagnostics, and interactive Swagger OpenAPI link (`/docs`).

---

## 🏗️ Architecture & Technology Stack

- **Frontend**: React 18, Vite, TypeScript, Tailwind CSS, Recharts, Lucide React, React Router 6, Axios, Leaflet.
- **Backend**: FastAPI, Uvicorn ASGI, Ultralytics YOLO (`yolo26n.pt`), OpenCV, Pillow, PyTorch.
- **Database**: SQLite with SQLAlchemy ORM (stored in `backend/rescue_vision.db`).
- **Storage**: Managed local disk storage (`backend/storage/uploads`, `backend/storage/results`, `backend/storage/videos`).

---

## 🚀 Quick Start (Windows)

### Prerequisites
- **Python**: Version 3.10, 3.11, or compatible (tested with Python 3.14 / 3.11). Ensure "Add Python to PATH" was selected during install.
- **Node.js**: Version 18+ (tested with Node 20 / 24). Includes `npm`.

---

### Method 1: One-Click Master Launcher (Recommended)

1. Extract the downloaded `RescueVision-Complete-Project.zip` archive into any folder.
2. Double-click `start_rescue_vision.bat` in the project root.
3. The script will:
   - Check Python and Node.js.
   - Automatically initialize backend environment and frontend packages if needed.
   - Launch the FastAPI Backend on `http://127.0.0.1:8000` in one console.
   - Launch the Vite Frontend on `http://127.0.0.1:5173` in a second console.
   - Automatically open `http://127.0.0.1:5173/` in your browser.

---

### Method 2: Launching Services Separately

#### 1. Backend Terminal:
```cmd
cd rescue-vision
start_backend.bat
```
- **Backend Base URL**: `http://127.0.0.1:8000`
- **Interactive Swagger Docs**: `http://127.0.0.1:8000/docs`

#### 2. Frontend Terminal:
```cmd
cd rescue-vision
start_frontend.bat
```
- **Frontend Dashboard URL**: `http://127.0.0.1:5173/`

---

## 🧪 Testing the Application

1. Open `http://127.0.0.1:5173/detect` in your browser.
2. Drag and drop or browse to select an image (`.jpg`, `.png`, `.webp`) or video (`.mp4`).
3. Set your desired **Confidence Threshold** (e.g. 25%) and **Image Size** (640px).
4. Click **"Execute Detection"**.
5. The tactical HUD displays:
   - Side-by-side original and annotated output with neon orange bounding boxes for human candidates.
   - Inference latency in milliseconds and total detection count.
   - Candidate coordinate and confidence table.
   - Options to download the annotated image/video or export metadata as JSON/CSV.

---

## 🔧 Troubleshooting Guide

| Issue | Cause | Solution |
|---|---|---|
| **"Cannot reach backend at http://127.0.0.1:8000"** | The FastAPI backend server is not running or crashed. | Run `start_backend.bat` or check console window for python errors. |
| **Port 8000 or 5173 already in use** | A previous instance is still running in the background. | Run `check_setup.bat` to see which ports are active, or close lingering python/node processes in Task Manager. |
| **Missing model weights `yolo26n.pt`** | Model weights file not found in `backend/models/`. | Ensure `backend/models/yolo26n.pt` exists (included in this package) or allow Ultralytics to auto-download on first run. |
| **CORS errors in browser console** | Origin mismatch between frontend and backend. | Verify `backend/app/core/config.py` allows `http://localhost:5173` and `http://127.0.0.1:5173` (pre-configured). |

---

## ⚠️ Operational Disclaimer

Rescue Vision provides **candidate decision-support leads** to human search and rescue operators. Conventional RGB optical computer vision cannot penetrate opaque solid rubble, detect biological vital signs, or assess vital state. All detections must be physically verified by qualified rescue personnel.
