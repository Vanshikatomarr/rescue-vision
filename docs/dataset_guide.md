# Dataset Preparation Guide for Disaster Response Object Detection

## 1. Directory Structure
Rescue Vision enforces the standardized Ultralytics YOLO object detection dataset layout:

```
disaster-dataset/
├── data.yaml
├── images/
│   ├── train/
│   │   ├── rubble_001.jpg
│   │   └── flood_002.jpg
│   └── val/
│       ├── test_001.jpg
│       └── test_002.jpg
└── labels/
    ├── train/
    │   ├── rubble_001.txt
    │   └── flood_002.txt
    └── val/
        ├── test_001.txt
        └── test_002.txt
```

---

## 2. YAML Configuration (`data.yaml`)
Create a `data.yaml` file in the root of your dataset directory:

```yaml
path: /absolute/path/to/disaster-dataset # or relative to workspace
train: images/train
val: images/val
test: images/test # optional

names:
  0: person
  1: first_responder
  2: trapped_survivor
```

---

## 3. Label File Format
For every image in `images/`, a corresponding text file with the same base name must reside in `labels/`.
Each line defines one object candidate in normalized coordinates:

`<class_id> <x_center> <y_center> <width> <height>`

Example (`rubble_001.txt`):
```text
0 0.452100 0.612400 0.125000 0.284000
2 0.781200 0.354000 0.092000 0.180000
```
- Coordinates must be normalized floats between `0.0` and `1.0`.
- `x_center` and `y_center` define the center of the bounding box.
- `width` and `height` define dimensions relative to the full image.

---

## 4. Special Considerations in Disaster Imagery
1. **Partial Occlusion**: When a person is partially covered by debris or rubble, draw the bounding box tightly around the visible body segment.
2. **Dust & Low Contrast**: Do not discard low-visibility images; augment training data with synthetic brightness and dust simulation.
3. **Drone & Aerial Perspective**: Include high-altitude angles to improve detection from UAV reconnaissance feeds.
