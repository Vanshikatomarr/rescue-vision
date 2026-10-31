import json
import shutil
from pathlib import Path
from typing import Optional
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from sqlalchemy.orm import Session
from app.core.config import settings
from app.core.security import sanitize_filename, safe_extract_zip
from app.database.session import get_db
from app.database.models import DatasetRecord
from app.schemas.training import DatasetValidationResult
from app.services.dataset_service import dataset_service

router = APIRouter(prefix="/datasets", tags=["Datasets"])

@router.get("")
def list_datasets(db: Session = Depends(get_db)):
    datasets = db.query(DatasetRecord).order_by(DatasetRecord.created_at.desc()).all()
    results = []
    for d in datasets:
        try:
            classes = json.loads(d.classes_json)
        except Exception:
            classes = []
        results.append({
            "id": d.id,
            "name": d.name,
            "folder_path": d.folder_path,
            "yaml_path": d.yaml_path,
            "train_count": d.train_count,
            "val_count": d.val_count,
            "test_count": d.test_count,
            "classes": classes,
            "is_valid": d.is_valid,
            "validation_details": d.validation_details,
            "created_at": d.created_at
        })
    return results

@router.post("/validate", response_model=DatasetValidationResult)
def validate_dataset_path(path: str = Form(...)):
    p = Path(path)
    if not p.is_absolute():
        p = settings.DATASETS_DIR / path
        
    res = dataset_service.validate_dataset(p)
    return res

@router.post("/upload")
async def upload_dataset_archive(
    file: UploadFile = File(...),
    dataset_name: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    if not file.filename.endswith(".zip"):
        raise HTTPException(status_code=400, detail="Only .zip dataset archives are supported.")

    name = dataset_name or Path(file.filename).stem
    safe_folder_name = sanitize_filename(name).replace(".", "_")
    target_dir = settings.DATASETS_DIR / safe_folder_name
    target_dir.mkdir(parents=True, exist_ok=True)

    zip_tmp = target_dir / "upload.zip"
    contents = await file.read()
    with open(zip_tmp, "wb") as f:
        f.write(contents)

    try:
        safe_extract_zip(zip_tmp, target_dir)
    finally:
        if zip_tmp.exists():
            zip_tmp.unlink()

    # If extraction created a single top-level folder, adjust target_dir
    subdirs = [p for p in target_dir.iterdir() if p.is_dir() and (p / "data.yaml").exists()]
    actual_dir = subdirs[0] if subdirs else target_dir

    # Validate
    validation = dataset_service.validate_dataset(actual_dir)

    record = DatasetRecord(
        name=name,
        folder_path=str(actual_dir.resolve()),
        yaml_path=validation["yaml_path"],
        train_count=validation["train_images"],
        val_count=validation["val_images"],
        test_count=validation["test_images"],
        classes_json=json.dumps(validation["classes"]),
        is_valid=validation["is_valid"],
        validation_details="; ".join(validation["errors"] + validation["warnings"]) or "Valid YOLO dataset."
    )
    db.add(record)
    db.commit()
    db.refresh(record)

    return {
        "dataset_id": record.id,
        "name": record.name,
        "validation": validation
    }

@router.post("/generate-sample")
def generate_sample_dataset(db: Session = Depends(get_db)):
    """Generate the built-in disaster response scenario dataset."""
    sample_dir = dataset_service.create_sample_disaster_dataset()
    val = dataset_service.validate_dataset(sample_dir)

    # Check if already in DB
    existing = db.query(DatasetRecord).filter(DatasetRecord.name == "Disaster Response Sample").first()
    if not existing:
        existing = DatasetRecord(
            name="Disaster Response Sample",
            folder_path=str(sample_dir.resolve()),
            yaml_path=val["yaml_path"],
            train_count=val["train_images"],
            val_count=val["val_images"],
            test_count=val["test_images"],
            classes_json=json.dumps(val["classes"]),
            is_valid=val["is_valid"],
            validation_details="Built-in disaster search & rescue scenario dataset."
        )
        db.add(existing)
        db.commit()
        db.refresh(existing)

    return {
        "dataset_id": existing.id,
        "name": existing.name,
        "validation": val
    }
