
import json
import threading
import pandas as pd

from pathlib import Path
from datetime import datetime, timezone
from ultralytics import YOLO

from app.core.config import settings
from app.database.session import SessionLocal
from app.database.models import TrainingRun, ModelRecord


class TrainingManager:
    def __init__(self):
        self._active_threads: dict[str, threading.Thread] = {}
        self._stop_events: dict[str, threading.Event] = {}
        self._lock = threading.Lock()

    @staticmethod
    def _timestamp():
        return datetime.now(timezone.utc).strftime("%H:%M:%S")

    def _append_log(self, db, run, logs, message):
        logs.append(f"[{self._timestamp()}] {message}")
        run.logs_text = "\n".join(logs)
        db.commit()

    def start_training(
        self,
        run_id: str,
        run_name: str,
        base_model: str,
        epochs: int,
        batch_size: int,
        img_size: int,
        dataset_yaml_path: str,
    ):
        """Start YOLO training in a managed background thread."""
        with self._lock:
            if run_id in self._active_threads:
                raise RuntimeError(f"Training run {run_id} is already active.")

            stop_event = threading.Event()
            self._stop_events[run_id] = stop_event

            thread = threading.Thread(
                target=self._run_training_worker,
                args=(
                    run_id,
                    run_name,
                    base_model,
                    epochs,
                    batch_size,
                    img_size,
                    dataset_yaml_path,
                    stop_event,
                ),
                daemon=True,
            )

            self._active_threads[run_id] = thread
            thread.start()

    def cancel_training(self, run_id: str) -> bool:
        """Request cancellation; the YOLO callback stops training."""
        with self._lock:
            stop_event = self._stop_events.get(run_id)

        if stop_event is None:
            return False

        stop_event.set()
        return True

    def _run_training_worker(
        self,
        run_id: str,
        run_name: str,
        base_model: str,
        epochs: int,
        batch_size: int,
        img_size: int,
        dataset_yaml_path: str,
        stop_event: threading.Event,
    ):
        db = SessionLocal()
        run = None
        logs = []

        try:
            run = (
                db.query(TrainingRun)
                .filter(TrainingRun.id == run_id)
                .first()
            )

            if run is None:
                return

            run.status = "RUNNING"
            run.current_epoch = 0
            run.error_message = None
            logs = [
                f"[{self._timestamp()}] Initializing training run '{run_name}'.",
                f"Base model: {base_model}",
                f"Epochs: {epochs} | Batch: {batch_size} | Image size: {img_size}",
                f"Dataset YAML: {dataset_yaml_path}",
            ]
            run.logs_text = "\n".join(logs)
            db.commit()

            # Resolve and validate dataset configuration.
            yaml_path = Path(dataset_yaml_path).resolve()

            if not yaml_path.is_file():
                raise FileNotFoundError(
                    f"Dataset YAML file not found: {yaml_path}"
                )

            # Resolve model weights from the configured model directory,
            # then the supplied path, then the default pretrained model.
            models_dir = Path(settings.MODELS_DIR)
            model_path = models_dir / base_model

            if not model_path.is_file():
                supplied_path = Path(base_model)
                if supplied_path.is_file():
                    model_path = supplied_path
                else:
                    # Default Ultralytics pretrained detection model.
                    model_path = Path("yolo26n.pt")

            self._append_log(
                db,
                run,
                logs,
                f"Loading model weights: {model_path}",
            )

            model = YOLO(str(model_path))

            # Fail early if CUDA is unavailable rather than silently
            # running a GPU-requested job on the CPU.
            import torch

            if not torch.cuda.is_available():
                raise RuntimeError(
                    "CUDA is unavailable. Verify your NVIDIA driver "
                    "and CUDA-enabled PyTorch installation."
                )

            gpu_name = torch.cuda.get_device_name(0)

            self._append_log(
                db,
                run,
                logs,
                f"GPU detected: {gpu_name}",
            )

            self._append_log(
                db,
                run,
                logs,
                "Starting YOLO training on GPU device 0.",
            )

            # Keep epoch progress and cancellation synchronized with
            # the background worker.
            def on_train_epoch_end(trainer):
                if stop_event.is_set():
                    trainer.stop = True

                current_epoch = int(trainer.epoch) + 1

                try:
                    run.current_epoch = current_epoch
                    run.logs_text = "\n".join(
                        logs
                        + [
                            f"[{self._timestamp()}] "
                            f"Epoch {current_epoch}/{epochs} completed."
                        ]
                    )
                    db.commit()
                except Exception:
                    db.rollback()
                    raise

            model.add_callback(
                "on_train_epoch_end",
                on_train_epoch_end,
            )

            results = model.train(
                data=str(yaml_path),
                epochs=epochs,
                batch=batch_size,
                imgsz=img_size,
                project=str(settings.RUNS_DIR),
                name=run_id,
                device=0,
                exist_ok=True,
                verbose=True,
                workers=0,
            )

            if stop_event.is_set():
                run.status = "CANCELLED"
                run.finished_at = datetime.now(timezone.utc)

                self._append_log(
                    db,
                    run,
                    logs,
                    "Training cancellation requested; stopped at an epoch boundary.",
                )
                return

            output_dir = Path(settings.RUNS_DIR) / run_id
            best_pt = output_dir / "weights" / "best.pt"
            last_pt = output_dir / "weights" / "last.pt"

            target_weight = (
                best_pt if best_pt.is_file()
                else last_pt if last_pt.is_file()
                else None
            )

            if target_weight is not None:
                run.best_weight_path = str(target_weight.resolve())

            # Extract actual metrics from results.csv.
            csv_path = output_dir / "results.csv"
            metrics_data = {
                "mAP50": 0.0,
                "mAP50_95": 0.0,
                "precision": 0.0,
                "recall": 0.0,
                "final_box_loss": 0.0,
                "history": [],
            }

            if csv_path.is_file():
                try:
                    df = pd.read_csv(csv_path)
                    df.columns = df.columns.str.strip()

                    if not df.empty:
                        latest = df.iloc[-1]

                        def metric(row, key):
                            value = row.get(key, 0.0)
                            return (
                                0.0
                                if pd.isna(value)
                                else float(value)
                            )

                        metrics_data.update({
                            "mAP50": round(
                                metric(latest, "metrics/mAP50(B)"), 4
                            ),
                            "mAP50_95": round(
                                metric(latest, "metrics/mAP50-95(B)"), 4
                            ),
                            "precision": round(
                                metric(latest, "metrics/precision(B)"), 4
                            ),
                            "recall": round(
                                metric(latest, "metrics/recall(B)"), 4
                            ),
                            "final_box_loss": round(
                                metric(latest, "train/box_loss"), 4
                            ),
                        })

                        for index, row in df.iterrows():
                            metrics_data["history"].append({
                                "epoch": int(
                                    metric(row, "epoch") or index + 1
                                ),
                                "train_box_loss": round(
                                    metric(row, "train/box_loss"), 4
                                ),
                                "val_box_loss": round(
                                    metric(row, "val/box_loss"), 4
                                ),
                                "precision": round(
                                    metric(row, "metrics/precision(B)"), 4
                                ),
                                "recall": round(
                                    metric(row, "metrics/recall(B)"), 4
                                ),
                                "mAP50": round(
                                    metric(row, "metrics/mAP50(B)"), 4
                                ),
                                "mAP50_95": round(
                                    metric(row, "metrics/mAP50-95(B)"), 4
                                ),
                            })

                except Exception as exc:
                    self._append_log(
                        db,
                        run,
                        logs,
                        f"Warning: could not parse results.csv: {exc}",
                    )

            else:
                result_dict = getattr(results, "results_dict", {}) or {}

                metrics_data.update({
                    "mAP50": round(
                        float(result_dict.get("metrics/mAP50(B)", 0.0)), 4
                    ),
                    "mAP50_95": round(
                        float(result_dict.get("metrics/mAP50-95(B)", 0.0)), 4
                    ),
                    "precision": round(
                        float(result_dict.get("metrics/precision(B)", 0.0)), 4
                    ),
                    "recall": round(
                        float(result_dict.get("metrics/recall(B)", 0.0)), 4
                    ),
                    "final_box_loss": round(
                        float(result_dict.get("train/box_loss", 0.0)), 4
                    ),
                })

            run.metrics_json = json.dumps(metrics_data)
            run.current_epoch = epochs
            run.status = "COMPLETED"
            run.finished_at = datetime.now(timezone.utc)

            # Register the resulting checkpoint in the model registry.
            if target_weight is not None and target_weight.is_file():
                saved_model = ModelRecord(
                    name=f"Fine-Tuned {run_name}",
                    version=f"v{run_id[:6]}",
                    checkpoint_path=str(target_weight.resolve()),
                    base_family="YOLO26-Disaster",
                    map50=metrics_data["mAP50"],
                    map50_95=metrics_data["mAP50_95"],
                    precision=metrics_data["precision"],
                    recall=metrics_data["recall"],
                    is_active=False,
                    training_run_id=run.id,
                )
                db.add(saved_model)

            self._append_log(
                db,
                run,
                logs,
                "Training completed successfully.",
            )

        except Exception as exc:
            db.rollback()

            if run is not None:
                try:
                    run.status = (
                        "CANCELLED" if stop_event.is_set() else "FAILED"
                    )
                    run.error_message = str(exc)
                    run.finished_at = datetime.now(timezone.utc)

                    logs.append(
                        f"[{self._timestamp()}] "
                        f"{'Training cancelled' if stop_event.is_set() else 'ERROR'}: "
                        f"{exc}"
                    )
                    run.logs_text = "\n".join(logs)
                    db.commit()
                except Exception:
                    db.rollback()

        finally:
            db.close()

            with self._lock:
                self._active_threads.pop(run_id, None)
                self._stop_events.pop(run_id, None)


training_manager = TrainingManager()