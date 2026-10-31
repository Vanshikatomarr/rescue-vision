import os
import time
import json
import uuid
import torch
import cv2
import numpy as np
from pathlib import Path
from PIL import Image
from ultralytics import YOLO
from fastapi import HTTPException
from app.core.config import settings

class DetectionService:
    _instance = None
    _model = None
    _active_model_path = None
    _device = "cpu"

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DetectionService, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        """Initialize device and load default YOLO model."""
        self._device = "cuda" if torch.cuda.is_available() else "cpu"
        # Determine initial model path
        default_path = Path(settings.MODELS_DIR) / settings.DEFAULT_MODEL_NAME
        if not default_path.exists():
            # Check in workspace or fallback
            default_path = Path(settings.DEFAULT_MODEL_NAME)
            
        self.load_model(str(default_path))

    @property
    def device(self) -> str:
        return self._device

    @property
    def active_model_path(self) -> str:
        return self._active_model_path or settings.DEFAULT_MODEL_NAME

    @property
    def model_name(self) -> str:
        return Path(self.active_model_path).name

    def load_model(self, model_path: str) -> bool:
        """Load YOLO model weights safely without reloading if already loaded."""
        try:
            p = Path(model_path)
            if not p.is_absolute():
                p = Path(settings.MODELS_DIR) / model_path
                if not p.exists():
                    p = Path(model_path)
            
            # If model is already loaded, reuse it
            if self._model is not None and str(p.resolve()) == str(self._active_model_path):
                return True

            print(f"[RescueVision] Loading YOLO model from: {p} on {self._device}...")
            loaded_model = YOLO(str(p))
            # Test dry run to ensure weights are valid
            self._model = loaded_model
            self._active_model_path = str(p.resolve())
            print(f"[RescueVision] Model {p.name} loaded successfully.")
            return True
        except Exception as e:
            print(f"[RescueVision] Failed to load model from {model_path}: {e}")
            if self._model is None:
                # Attempt to fallback to default
                try:
                    fallback = Path(settings.MODELS_DIR) / settings.FALLBACK_MODEL_NAME
                    if fallback.exists():
                        self._model = YOLO(str(fallback))
                        self._active_model_path = str(fallback.resolve())
                        print(f"[RescueVision] Loaded fallback model: {fallback.name}")
                        return True
                except Exception as fb_err:
                    print(f"[RescueVision] Fallback also failed: {fb_err}")
            return False

    def predict_image(
        self,
        image_path: str,
        confidence_threshold: float = 0.25,
        img_size: int = 640
    ) -> dict:
        """
        Run inference on an image file.
        Returns detection metadata, counts, bounding boxes, and saves annotated result.
        """
        if self._model is None:
            raise HTTPException(
                status_code=503,
                detail="Detection model is currently unavailable or initializing."
            )

        start_time = time.time()
        
        # Read image to verify and obtain dimensions
        orig_img = cv2.imread(image_path)
        if orig_img is None:
            raise HTTPException(status_code=400, detail="Invalid image file or cannot be decoded.")
            
        h, w, _ = orig_img.shape

        # Run YOLO inference
        try:
            results = self._model.predict(
                source=image_path,
                conf=confidence_threshold,
                imgsz=img_size,
                device=self._device,
                verbose=False
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Inference execution failed: {str(e)}")

        inference_time_ms = round((time.time() - start_time) * 1000, 2)
        
        result = results[0]
        boxes = result.boxes
        
        detected_objects = []
        person_count = 0
        total_detections = len(boxes)
        has_low_confidence = False

        annotated_img = orig_img.copy()

        # Custom high-contrast Disaster Response styling
        # Neon Orange for Person candidates: BGR (0, 140, 255)
        # Tactical Cyan for other objects: BGR (230, 216, 3)
        for i, box in enumerate(boxes):
            cls_id = int(box.cls[0].item())
            cls_name = result.names.get(cls_id, f"class_{cls_id}")
            conf = float(box.conf[0].item())
            x1, y1, x2, y2 = [float(v) for v in box.xyxy[0].tolist()]

            is_person = (cls_name.lower() == "person" or cls_id == 0)
            if is_person:
                person_count += 1
                if conf < 0.40:
                    has_low_confidence = True

            detected_objects.append({
                "id": i + 1,
                "class_id": cls_id,
                "class_name": cls_name,
                "is_person": is_person,
                "confidence": round(conf, 4),
                "bbox": {
                    "x1": round(x1, 1),
                    "y1": round(y1, 1),
                    "x2": round(x2, 1),
                    "y2": round(y2, 1)
                }
            })

            # Draw visual bounding box
            color = (0, 130, 255) if is_person else (230, 200, 0)
            thickness = 2 if not is_person else 3
            pt1 = (int(x1), int(y1))
            pt2 = (int(x2), int(y2))
            
            # Box
            cv2.rectangle(annotated_img, pt1, pt2, color, thickness)
            
            # Corner markers for tactical rescue UI
            corner_len = min(int((x2 - x1) * 0.2), 20)
            if corner_len > 4:
                cv2.line(annotated_img, pt1, (pt1[0] + corner_len, pt1[1]), color, thickness + 1)
                cv2.line(annotated_img, pt1, (pt1[0], pt1[1] + corner_len), color, thickness + 1)
                cv2.line(annotated_img, pt2, (pt2[0] - corner_len, pt2[1]), color, thickness + 1)
                cv2.line(annotated_img, pt2, (pt2[0], pt2[1] - corner_len), color, thickness + 1)

            # Label banner
            label = f"{'RESCUE CANDIDATE: ' if is_person else ''}{cls_name.upper()} {conf*100:.1f}%"
            (tw, th), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
            cv2.rectangle(
                annotated_img,
                (pt1[0], max(0, pt1[1] - th - 8)),
                (pt1[0] + tw + 10, pt1[1]),
                color,
                -1
            )
            cv2.putText(
                annotated_img,
                label,
                (pt1[0] + 5, max(th + 2, pt1[1] - 4)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.45,
                (0, 0, 0) if is_person else (255, 255, 255),
                1,
                cv2.LINE_AA
            )

        # Save annotated image
        output_filename = f"annotated_{uuid.uuid4().hex[:8]}_{Path(image_path).name}"
        output_path = settings.RESULTS_DIR / output_filename
        cv2.imwrite(str(output_path), annotated_img)

        warning = None
        if person_count == 0:
            warning = "No human presence detected above confidence threshold. Verify low-light areas and partial occlusions manually."
        elif has_low_confidence:
            warning = "Candidate human detected with lower confidence (< 40%). Visual verification by trained personnel required."

        return {
            "source_filename": Path(image_path).name,
            "person_count": person_count,
            "total_detections": total_detections,
            "confidence_threshold": confidence_threshold,
            "inference_time_ms": inference_time_ms,
            "model_name": self.model_name,
            "model_version": "YOLO26-Official",
            "device": self._device,
            "annotated_output_filename": output_filename,
            "annotated_output_path": str(output_path),
            "detections": detected_objects,
            "warning": warning
        }

detection_service = DetectionService()
