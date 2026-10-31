import io
import json
import csv
from pathlib import Path
from typing import Optional
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, Response
from fastapi.responses import JSONResponse, PlainTextResponse
from sqlalchemy.orm import Session
from app.core.config import settings
from app.core.security import sanitize_filename, validate_image_file, validate_video_file
from app.database.session import get_db
from app.database.models import DetectionRecord, Incident
from app.schemas.detection import DetectionResponse, VideoDetectionResponse
from app.services.detection_service import detection_service
from app.services.video_service import video_service

router = APIRouter(prefix="/detect", tags=["Detection"])

@router.post("/image")
async def detect_image(
    file: UploadFile = File(...),
    confidence: float = Form(0.25),
    img_size: int = Form(640),
    incident_id: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    if not file or not file.filename:
        raise HTTPException(status_code=400, detail="No image file provided.")

    validate_image_file(file)
    safe_name = sanitize_filename(file.filename)
    upload_path = settings.UPLOADS_DIR / safe_name

    # Save uploaded bytes safely
    contents = await file.read()
    if len(contents) > settings.MAX_IMAGE_SIZE_MB * 1024 * 1024:
        raise HTTPException(
            status_code=413,
            detail=f"Image size exceeds limit of {settings.MAX_IMAGE_SIZE_MB}MB."
        )

    with open(upload_path, "wb") as f:
        f.write(contents)

    # Perform YOLO prediction
    result = detection_service.predict_image(
        image_path=str(upload_path),
        confidence_threshold=confidence,
        img_size=img_size
    )

    # Persist in DB
    record = DetectionRecord(
        source_filename=file.filename,
        media_type="image",
        person_count=result["person_count"],
        total_detections=result["total_detections"],
        confidence_threshold=confidence,
        inference_time_ms=result["inference_time_ms"],
        model_name=result["model_name"],
        model_version=result["model_version"],
        input_path=f"/storage/uploads/{safe_name}",
        output_path=f"/storage/results/{result['annotated_output_filename']}",
        detections_json=json.dumps(result["detections"]),
        device=result["device"],
        incident_id=incident_id
    )
    db.add(record)

    # Link to incident if provided
    if incident_id:
        incident = db.query(Incident).filter(Incident.id == incident_id).first()
        if incident:
            incident.detection_count = (incident.detection_count or 0) + result["person_count"]
            incident.associated_detection_id = record.id
            if not incident.source_filename:
                incident.source_filename = file.filename

    db.commit()
    db.refresh(record)

    return {
        "detection_id": record.id,
        "source_filename": record.source_filename,
        "media_type": "image",
        "person_count": record.person_count,
        "total_detections": record.total_detections,
        "confidence_threshold": record.confidence_threshold,
        "inference_time_ms": record.inference_time_ms,
        "model_name": record.model_name,
        "model_version": record.model_version,
        "device": record.device,
        "annotated_image_url": record.output_path,
        "original_image_url": record.input_path,
        "detections": result["detections"],
        "warning": result["warning"],
        "created_at": record.created_at
    }

@router.post("/video")
async def detect_video(
    file: UploadFile = File(...),
    confidence: float = Form(0.25),
    img_size: int = Form(640),
    enable_tracking: bool = Form(True),
    db: Session = Depends(get_db)
):
    if not file or not file.filename:
        raise HTTPException(status_code=400, detail="No video file provided.")

    validate_video_file(file)
    safe_name = sanitize_filename(file.filename)
    upload_path = settings.UPLOADS_DIR / safe_name

    contents = await file.read()
    if len(contents) > settings.MAX_VIDEO_SIZE_MB * 1024 * 1024:
        raise HTTPException(
            status_code=413,
            detail=f"Video exceeds maximum size limit of {settings.MAX_VIDEO_SIZE_MB}MB."
        )

    with open(upload_path, "wb") as f:
        f.write(contents)

    # Run frame-by-frame tracking
    res = video_service.process_video(
        video_path=str(upload_path),
        confidence_threshold=confidence,
        img_size=img_size,
        enable_tracking=enable_tracking
    )

    record = DetectionRecord(
        source_filename=file.filename,
        media_type="video",
        person_count=res["unique_tracked_people"],
        total_detections=res["total_detections_count"],
        confidence_threshold=confidence,
        inference_time_ms=res["inference_time_ms"],
        model_name=res["model_name"],
        model_version="YOLO26-Official",
        input_path=f"/storage/uploads/{safe_name}",
        output_path=f"/storage/videos/{res['annotated_video_filename']}",
        detections_json=json.dumps(res["frame_statistics"]),
        device=res["device"]
    )
    db.add(record)
    db.commit()
    db.refresh(record)

    return {
        "detection_id": record.id,
        "source_filename": record.source_filename,
        "media_type": "video",
        "total_frames_processed": res["total_frames_processed"],
        "fps": res["fps"],
        "duration_seconds": res["duration_seconds"],
        "total_detections_count": res["total_detections_count"],
        "unique_tracked_people": res["unique_tracked_people"],
        "inference_time_ms": res["inference_time_ms"],
        "annotated_video_url": record.output_path,
        "frame_statistics": res["frame_statistics"],
        "model_name": res["model_name"],
        "device": res["device"],
        "warning": res["warning"]
    }

@router.get("/history")
def get_detections_history(
    limit: int = 50,
    media_type: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(DetectionRecord).order_by(DetectionRecord.created_at.desc())
    if media_type:
        query = query.filter(DetectionRecord.media_type == media_type)
    
    records = query.limit(limit).all()
    return [
        {
            "id": r.id,
            "source_filename": r.source_filename,
            "media_type": r.media_type,
            "person_count": r.person_count,
            "total_detections": r.total_detections,
            "confidence_threshold": r.confidence_threshold,
            "inference_time_ms": r.inference_time_ms,
            "model_name": r.model_name,
            "input_path": r.input_path,
            "output_path": r.output_path,
            "created_at": r.created_at,
            "incident_id": r.incident_id
        }
        for r in records
    ]

@router.get("/{detection_id}")
def get_detection_detail(detection_id: str, db: Session = Depends(get_db)):
    record = db.query(DetectionRecord).filter(DetectionRecord.id == detection_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Detection record not found.")

    detections = []
    try:
        detections = json.loads(record.detections_json)
    except Exception:
        pass

    return {
        "id": record.id,
        "source_filename": record.source_filename,
        "media_type": record.media_type,
        "person_count": record.person_count,
        "total_detections": record.total_detections,
        "confidence_threshold": record.confidence_threshold,
        "inference_time_ms": record.inference_time_ms,
        "model_name": record.model_name,
        "model_version": record.model_version,
        "device": record.device,
        "original_image_url": record.input_path,
        "annotated_image_url": record.output_path,
        "detections": detections,
        "created_at": record.created_at,
        "incident_id": record.incident_id
    }

@router.get("/{detection_id}/export/json")
def export_detection_json(detection_id: str, db: Session = Depends(get_db)):
    record = db.query(DetectionRecord).filter(DetectionRecord.id == detection_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Record not found.")

    data = {
        "detection_id": record.id,
        "filename": record.source_filename,
        "person_count": record.person_count,
        "total_detections": record.total_detections,
        "confidence_threshold": record.confidence_threshold,
        "inference_time_ms": record.inference_time_ms,
        "model_name": record.model_name,
        "device": record.device,
        "created_at": str(record.created_at),
        "detections": json.loads(record.detections_json)
    }

    return JSONResponse(
        content=data,
        headers={"Content-Disposition": f"attachment; filename=detection_{record.id[:8]}.json"}
    )

@router.get("/{detection_id}/export/csv")
def export_detection_csv(detection_id: str, db: Session = Depends(get_db)):
    record = db.query(DetectionRecord).filter(DetectionRecord.id == detection_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Record not found.")

    detections = json.loads(record.detections_json)
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["ID", "Class Name", "Is Person", "Confidence", "x1", "y1", "x2", "y2"])

    for item in detections:
        bbox = item.get("bbox", {})
        writer.writerow([
            item.get("id"),
            item.get("class_name"),
            item.get("is_person"),
            item.get("confidence"),
            bbox.get("x1"),
            bbox.get("y1"),
            bbox.get("x2"),
            bbox.get("y2"),
        ])

    return PlainTextResponse(
        content=output.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=detection_{record.id[:8]}.csv"}
    )
