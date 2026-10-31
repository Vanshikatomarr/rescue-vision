from datetime import datetime
from typing import Optional, Any
from pydantic import BaseModel, Field, ConfigDict

class TrainingStartRequest(BaseModel):
    run_name: str = Field(..., min_length=1, max_length=100)
    base_model: str = "yolo26n.pt"
    epochs: int = Field(default=5, ge=1, le=100)
    batch_size: int = Field(default=8, ge=1, le=64)
    img_size: int = Field(default=640, ge=320, le=1280)
    dataset_id: str

class TrainingRunOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    run_name: str
    base_model: str
    epochs: int
    batch_size: int
    img_size: int
    dataset_path: str
    status: str
    current_epoch: int
    metrics: dict[str, Any]
    best_weight_path: Optional[str] = None
    error_message: Optional[str] = None
    logs: Optional[str] = None
    created_at: datetime
    finished_at: Optional[datetime] = None

class DatasetValidationResult(BaseModel):
    is_valid: bool
    dataset_name: str
    dataset_path: str
    yaml_path: str
    train_images: int
    val_images: int
    test_images: int
    classes: list[str]
    errors: list[str]
    warnings: list[str]
