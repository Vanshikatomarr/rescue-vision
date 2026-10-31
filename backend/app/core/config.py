
import os
from pathlib import Path
from pydantic import BaseModel, Field

BASE_DIR = Path(__file__).resolve().parent.parent.parent


class Settings(BaseModel):
    PROJECT_NAME: str = "Rescue Vision API"
    VERSION: str = "1.0.0"
    API_PREFIX: str = "/api"

    # Storage directories
    STORAGE_DIR: Path = BASE_DIR / "storage"
    UPLOADS_DIR: Path = STORAGE_DIR / "uploads"
    RESULTS_DIR: Path = STORAGE_DIR / "results"
    VIDEOS_DIR: Path = STORAGE_DIR / "videos"
    DATASETS_DIR: Path = BASE_DIR / "datasets"
    RUNS_DIR: Path = BASE_DIR / "runs"
    MODELS_DIR: Path = BASE_DIR / "models"

    # Model configuration
    DEFAULT_MODEL_NAME: str = "rescue_person_best.pt"
    FALLBACK_MODEL_NAME: str = "yolo26n.pt"
    ACTIVE_MODEL_PATH: str = str(
        BASE_DIR / "models" / "rescue_person_best.pt"
    )

    # Inference defaults
    CONFIDENCE_THRESHOLD: float = 0.25
    IOU_THRESHOLD: float = 0.45
    IMG_SIZE: int = 640
    DEVICE: str = "cpu"  # Auto-detected on startup

    # Database
    DATABASE_URL: str = f"sqlite:///{BASE_DIR}/rescue_vision.db"

    # CORS
    CORS_ORIGINS: list[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
    ]

    # Limits
    MAX_IMAGE_SIZE_MB: int = 25
    MAX_VIDEO_SIZE_MB: int = 150
    MAX_VIDEO_FRAMES: int = 900


settings = Settings()

# Ensure directories exist
for folder in [
    settings.STORAGE_DIR,
    settings.UPLOADS_DIR,
    settings.RESULTS_DIR,
    settings.VIDEOS_DIR,
    settings.DATASETS_DIR,
    settings.RUNS_DIR,
    settings.MODELS_DIR,
]:
    folder.mkdir(parents=True, exist_ok=True)
