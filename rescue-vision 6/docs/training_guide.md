# Custom Model Fine-Tuning Guide (Rescue Vision)

## 1. Overview
Rescue Vision uses transfer learning starting from Ultralytics YOLO26 (`yolo26n.pt`) weights. Transfer learning retains the foundational visual features learned on extensive generic datasets (COCO) while adjusting feature maps to detect partially buried individuals, dust-veiled figures, and unusual human postures in disaster voids.

---

## 2. Training Execution Flow
1. **Navigate to `/training`** in the Rescue Vision web dashboard.
2. **Select or Upload Dataset**:
   - Use the **"Provision Sample Dataset"** button to automatically initialize synthetic disaster search & rescue training scenarios.
   - Or upload a zipped YOLO dataset archive (`.zip`) containing `data.yaml` and image/label splits.
3. **Configure Hyperparameters**:
   - **Base Checkpoint**: `yolo26n.pt` (Lightweight Nano architecture).
   - **Epochs**: Recommended 5-20 epochs for fine-tuning.
   - **Batch Size**: 4-16 depending on available VRAM / system RAM.
   - **Image Size**: 640px default (or 320px for rapid test cycles).
4. **Execute**:
   - Click **"Launch Background Training Job"**.
   - Monitor live epoch progress, box loss curves, and terminal stdout logs in real-time.
5. **Evaluate & Activate**:
   - Upon completion, click **"Evaluate"** to measure true validation mAP@0.50.
   - Navigate to **`/models`** to activate the fine-tuned checkpoint for live inference.

---

## 3. Hardware Requirements
- **CPU Mode**: Standard x86_64 multi-core processor (supported by default).
- **GPU Acceleration**: NVIDIA GPU with CUDA 11.8+ and PyTorch with CUDA support.
- **RAM**: Minimum 8GB system memory recommended.
