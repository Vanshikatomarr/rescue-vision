import json
import uuid
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ultralytics import YOLO
from app.core.config import settings
from app.database.session import get_db
from app.database.models import TrainingRun, DatasetRecord, ModelRecord
from app.schemas.training import TrainingStartRequest
from app.services.training_service import training_manager

router = APIRouter(prefix="/training", tags=["Training"])

@router.get("")
def list_training_runs(db: Session = Depends(get_db)):
    runs = db.query(TrainingRun).order_by(TrainingRun.created_at.desc()).all()
    out = []
    for r in runs:
        try:
            metrics = json.loads(r.metrics_json) if r.metrics_json else {}
        except Exception:
            metrics = {}
        out.append({
            "id": r.id,
            "run_name": r.run_name,
            "base_model": r.base_model,
            "epochs": r.epochs,
            "batch_size": r.batch_size,
            "img_size": r.img_size,
            "dataset_path": r.dataset_path,
            "status": r.status,
            "current_epoch": r.current_epoch,
            "metrics": metrics,
            "best_weight_path": r.best_weight_path,
            "error_message": r.error_message,
            "created_at": r.created_at,
            "finished_at": r.finished_at
        })
    return out

@router.post("/start")
def start_training_run(req: TrainingStartRequest, db: Session = Depends(get_db)):
    dataset = db.query(DatasetRecord).filter(DatasetRecord.id == req.dataset_id).first()
    if not dataset:
        raise HTTPException(status_code=404, detail="Selected dataset not found.")
    if not dataset.is_valid:
        raise HTTPException(status_code=400, detail="Cannot train on an invalid dataset. Please fix YAML and splits first.")

    run_id = str(uuid.uuid4())
    run = TrainingRun(
        id=run_id,
        run_name=req.run_name,
        base_model=req.base_model,
        epochs=req.epochs,
        batch_size=req.batch_size,
        img_size=req.img_size,
        dataset_path=dataset.yaml_path,
        status="QUEUED",
        current_epoch=0,
        metrics_json="{}",
        logs_text=f"Training job queued at UTC {str(uuid.uuid4())[:8]}."
    )
    db.add(run)
    db.commit()
    db.refresh(run)

    # Launch background thread
    training_manager.start_training(
        run_id=run.id,
        run_name=run.run_name,
        base_model=run.base_model,
        epochs=run.epochs,
        batch_size=run.batch_size,
        img_size=run.img_size,
        dataset_yaml_path=dataset.yaml_path
    )

    return {
        "run_id": run.id,
        "run_name": run.run_name,
        "status": "QUEUED",
        "message": "Training job initialized in background thread."
    }

@router.get("/{run_id}")
def get_training_run(run_id: str, db: Session = Depends(get_db)):
    run = db.query(TrainingRun).filter(TrainingRun.id == run_id).first()
    if not run:
        raise HTTPException(status_code=404, detail="Training run not found.")

    try:
        metrics = json.loads(run.metrics_json) if run.metrics_json else {}
    except Exception:
        metrics = {}

    return {
        "id": run.id,
        "run_name": run.run_name,
        "base_model": run.base_model,
        "epochs": run.epochs,
        "batch_size": run.batch_size,
        "img_size": run.img_size,
        "dataset_path": run.dataset_path,
        "status": run.status,
        "current_epoch": run.current_epoch,
        "metrics": metrics,
        "best_weight_path": run.best_weight_path,
        "error_message": run.error_message,
        "logs": run.logs_text,
        "created_at": run.created_at,
        "finished_at": run.finished_at
    }

@router.post("/{run_id}/cancel")
def cancel_training_run(run_id: str, db: Session = Depends(get_db)):
    run = db.query(TrainingRun).filter(TrainingRun.id == run_id).first()
    if not run:
        raise HTTPException(status_code=404, detail="Training run not found.")

    if run.status != "RUNNING":
        return {"success": False, "message": f"Run is in state '{run.status}', not running."}

    cancelled = training_manager.cancel_training(run_id)
    return {"success": cancelled, "message": "Cancellation signal sent."}

@router.post("/{run_id}/evaluate")
def evaluate_training_run(run_id: str, db: Session = Depends(get_db)):
    run = db.query(TrainingRun).filter(TrainingRun.id == run_id).first()
    if not run:
        raise HTTPException(status_code=404, detail="Training run not found.")
    if not run.best_weight_path or not Path(run.best_weight_path).exists():
        raise HTTPException(status_code=400, detail="No checkpoint weight file found for this run.")

    try:
        eval_model = YOLO(run.best_weight_path)
        metrics = eval_model.val(data=run.dataset_path, verbose=False)
        
        map50 = float(metrics.box.map50)
        map50_95 = float(metrics.box.map)
        mp = float(metrics.box.mp)
        mr = float(metrics.box.mr)

        eval_data = {
            "mAP50": round(map50, 4),
            "mAP50_95": round(map50_95, 4),
            "precision": round(mp, 4),
            "recall": round(mr, 4)
        }

        # Update model record if exists
        model_rec = db.query(ModelRecord).filter(ModelRecord.training_run_id == run.id).first()
        if model_rec:
            model_rec.map50 = eval_data["mAP50"]
            model_rec.map50_95 = eval_data["mAP50_95"]
            model_rec.precision = eval_data["precision"]
            model_rec.recall = eval_data["recall"]
            db.commit()

        return {"success": True, "evaluation": eval_data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Model evaluation failed: {str(e)}")
