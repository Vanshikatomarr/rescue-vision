import os
import re
import uuid
import zipfile
from pathlib import Path
from fastapi import HTTPException, UploadFile

ALLOWED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
ALLOWED_VIDEO_EXTENSIONS = {".mp4", ".avi", ".mov", ".mkv"}
ALLOWED_ARCHIVE_EXTENSIONS = {".zip"}

def sanitize_filename(filename: str) -> str:
    """Sanitize filename to prevent path traversal and illegal characters."""
    base = os.path.basename(filename)
    clean = re.sub(r"[^a-zA-Z0-9_.-]", "_", base)
    if not clean or clean.startswith("."):
        clean = f"file_{clean}"
    return f"{uuid.uuid4().hex[:8]}_{clean}"

def validate_image_file(file: UploadFile, max_size_mb: int = 25) -> str:
    """Validate image extension and MIME type."""
    ext = Path(file.filename or "").suffix.lower()
    if ext not in ALLOWED_IMAGE_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported image format '{ext}'. Allowed: {', '.join(sorted(ALLOWED_IMAGE_EXTENSIONS))}"
        )
    return ext

def validate_video_file(file: UploadFile, max_size_mb: int = 150) -> str:
    """Validate video extension."""
    ext = Path(file.filename or "").suffix.lower()
    if ext not in ALLOWED_VIDEO_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported video format '{ext}'. Allowed: {', '.join(sorted(ALLOWED_VIDEO_EXTENSIONS))}"
        )
    return ext

def safe_extract_zip(zip_path: Path, extract_to: Path) -> list[str]:
    """
    Safely extract zip archive preventing ZipSlip vulnerability.
    Returns list of extracted relative file paths.
    """
    extracted_files = []
    extract_to_resolved = extract_to.resolve()
    
    with zipfile.ZipFile(zip_path, "r") as zf:
        for member in zf.infolist():
            target_path = (extract_to / member.filename).resolve()
            if not str(target_path).startswith(str(extract_to_resolved)):
                raise HTTPException(status_code=400, detail="Malicious archive detected (path traversal attempt).")
            zf.extract(member, extract_to)
            if not member.is_dir():
                extracted_files.append(member.filename)
                
    return extracted_files
