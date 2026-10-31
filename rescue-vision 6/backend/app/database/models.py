import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, Text
from app.database.session import Base

def generate_uuid() -> str:
    return str(uuid.uuid4())

def get_utc_now():
    return datetime.now(timezone.utc)

class DetectionRecord(Base):
    __tablename__ = "detection_records"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    source_filename = Column(String(255), nullable=False)
    media_type = Column(String(32), default="image")  # image or video
    person_count = Column(Integer, default=0)
    total_detections = Column(Integer, default=0)
    confidence_threshold = Column(Float, default=0.25)
    inference_time_ms = Column(Float, default=0.0)
    model_name = Column(String(128), default="yolo26n")
    model_version = Column(String(64), default="v1.0")
    input_path = Column(String(512), nullable=False)
    output_path = Column(String(512), nullable=False)
    detections_json = Column(Text, default="[]")  # List of objects: class, conf, bbox
    device = Column(String(32), default="cpu")
    incident_id = Column(String(36), nullable=True)
    created_at = Column(DateTime, default=get_utc_now)

class Incident(Base):
    __tablename__ = "incidents"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    title = Column(String(255), nullable=False)
    description = Column(Text, default="")
    location_name = Column(String(255), default="")
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    status = Column(String(32), default="OPEN")  # OPEN, IN_PROGRESS, RESOLVED, CLOSED
    severity = Column(String(32), default="MEDIUM")  # LOW, MEDIUM, HIGH, CRITICAL
    detection_count = Column(Integer, default=0)
    source_filename = Column(String(255), default="")
    associated_detection_id = Column(String(36), nullable=True)
    notes = Column(Text, default="")
    created_at = Column(DateTime, default=get_utc_now)
    updated_at = Column(DateTime, default=get_utc_now, onupdate=get_utc_now)

class DatasetRecord(Base):
    __tablename__ = "datasets"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(255), nullable=False)
    folder_path = Column(String(512), nullable=False)
    yaml_path = Column(String(512), nullable=False)
    train_count = Column(Integer, default=0)
    val_count = Column(Integer, default=0)
    test_count = Column(Integer, default=0)
    classes_json = Column(Text, default="[]")
    is_valid = Column(Boolean, default=False)
    validation_details = Column(Text, default="")
    created_at = Column(DateTime, default=get_utc_now)

class TrainingRun(Base):
    __tablename__ = "training_runs"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    run_name = Column(String(255), nullable=False)
    base_model = Column(String(128), default="yolo26n.pt")
    epochs = Column(Integer, default=10)
    batch_size = Column(Integer, default=8)
    img_size = Column(Integer, default=640)
    dataset_path = Column(String(512), nullable=False)
    status = Column(String(32), default="QUEUED")  # QUEUED, RUNNING, COMPLETED, FAILED, CANCELLED
    current_epoch = Column(Integer, default=0)
    metrics_json = Column(Text, default="{}")  # Epoch curves & final eval metrics
    best_weight_path = Column(String(512), nullable=True)
    error_message = Column(Text, default="")
    logs_text = Column(Text, default="")
    created_at = Column(DateTime, default=get_utc_now)
    finished_at = Column(DateTime, nullable=True)

class ModelRecord(Base):
    __tablename__ = "model_records"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(255), nullable=False)
    version = Column(String(64), default="1.0")
    checkpoint_path = Column(String(512), nullable=False)
    base_family = Column(String(64), default="YOLO26")
    map50 = Column(Float, nullable=True)
    map50_95 = Column(Float, nullable=True)
    precision = Column(Float, nullable=True)
    recall = Column(Float, nullable=True)
    is_active = Column(Boolean, default=False)
    training_run_id = Column(String(36), nullable=True)
    created_at = Column(DateTime, default=get_utc_now)

class AppSetting(Base):
    __tablename__ = "app_settings"

    key = Column(String(128), primary_key=True)
    value = Column(Text, nullable=False)
