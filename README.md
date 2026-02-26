🚀 SafetyEye – AI Powered Workplace Occupancy & Safety Monitor
📌 Milestone 1 (Week 1–2): Data Preparation & Environment Setup

This milestone focuses on setting up the development environment, preparing and validating the dataset, configuring YOLOv8, and verifying the end-to-end training pipeline.

✅ Week 1 – Environment Setup & Dataset Verification

🔹 1. Environment Configuration

Installed Python and VS Code

Created virtual environment:

python -m venv venv

Installed required dependencies:

pip install ultralytics torch opencv-python numpy matplotlib

Generated requirements file:

pip freeze > requirements.txt

🔹 2. Git Workflow

Cloned project repository

Created feature branch:

git checkout -b yourname-projectname

Configured .gitignore:

venv/
runs/
__pycache__/
*.pt
*.log

🔹 3. Dataset Verification

Downloaded dataset (Construction Site Safety – YOLO format)

Verified:

Image–label one-to-one mapping

No missing labels

No incorrect annotation format

Empty labels identified (valid negative samples)

Dataset integrity confirmed.

🔹 4. OpenCV Visualization

Displayed sample images using OpenCV

Drew bounding boxes from YOLO label files

Visually verified annotation correctness

Result: Dataset ready for structured training.

✅ Week 2 – Dataset Organization & Pipeline Validation

🔹 1. YOLOv8 Folder Structure

Converted dataset into YOLOv8 compatible format:

dataset/
│
├── images/
│   ├── train/
│   ├── val/
│   └── test/
│
└── labels/
    ├── train/
    ├── val/
    └── test/

🔹 2. Dataset Split (70/20/10)

Implemented automated Python script to:

Randomly shuffle dataset

Split into:

70% Training

20% Validation

10% Testing

Preserve image–label pairing

Final Distribution:

Train: 1960 images

Validation: 560 images

Test: 281 images

🔹 3. Class Verification

Programmatically scanned label files.

Unique class IDs found: 0–9

Total classes: 10

🔹 4. data.yaml Configuration
path: dataset

train: images/train
val: images/val
test: images/test

names:
  0: class_0
  1: class_1
  2: class_2
  3: class_3
  4: class_4
  5: class_5
  6: class_6
  7: class_7
  8: class_8
  9: class_9


🔥 5. YOLOv8 Training Validation (1 Epoch Test)

Command executed:

yolo detect train data=dataset/data.yaml model=yolov8n.pt epochs=1 imgsz=640
📊 Training Output Summary
Epoch Details

Epoch: 1/1

box_loss: 1.413

cls_loss: 2.94

dfl_loss: 1.502

Training Time: ~0.209 hours

Device: CPU

📈 Validation Metrics (Overall)

Images: 560

Instances: 7944

Precision (P): 0.466

Recall (R): 0.329

mAP50: 0.314

mAP50-95: 0.17

📌 Per-Class mAP50
Class	mAP50
class_0	0.484
class_1	0.291
class_2	0.166
class_3	0.089
class_4	0.237
class_5	0.607
class_6	0.223
class_7	0.338
class_8	0.601
class_9	0.106

Note: Performance is expected to be low since training was conducted for only 1 epoch. This run was performed strictly to validate the training pipeline.

🎯 Milestone 1 Status

✔ Environment configured
✔ Dataset validated
✔ Dataset split reproducibly
✔ Class count verified
✔ YOLOv8 configured
✔ Training pipeline successfully executed

Milestone 1 completed successfully.