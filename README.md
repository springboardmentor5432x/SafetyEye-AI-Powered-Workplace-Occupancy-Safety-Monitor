SafetyEye – AI-Powered Workplace Occupancy & Safety Monitor
Project Overview

SafetyEye is an AI-based computer vision system designed to monitor workplace safety compliance using YOLOv8 object detection.

The system detects:

 Helmet

 Safety Vest

 Person

 no-helmet
   
 no-vest

 machinery

The goal is to ensure safety compliance at construction or industrial sites by identifying whether workers are wearing required protective equipment.

 Project Progress
 Week 1 – Environment Setup & Dataset Preparation
1️ Development Environment Setup

Installed Python (3.10+)

Installed Visual Studio Code

Created main project folder: SafetyEye

Created subfolders:

dataset/
scripts/
models/
notebooks/

Created and activated virtual environment:

python -m venv venv
2️ Installed Required Libraries

The following libraries were installed:

ultralytics (YOLOv8)

torch

torchvision

opencv-python

numpy

pandas

matplotlib

scikit-learn

PyYAML

All libraries were verified using:

pip list

YOLO installation verified using:

yolo
3️ Dataset Download & Verification

Downloaded Construction Site Safety Dataset from Kaggle

Extracted dataset into dataset/ folder

Verified:

Each image has a corresponding .txt label file

Label format follows YOLO annotation format

A test Python script using OpenCV was used to verify image loading and display functionality.

 Week 2 – Dataset Organization for YOLOv8
1️ YOLOv8 Folder Structure Created

Inside dataset/, the following structure was created:

dataset/
│
├── images/
│   ├── train/
│   ├── val/
│   └── test/
│
├── labels/
│   ├── train/
│   ├── val/
│   └── test/
2️ Dataset Split

The dataset was split into:

70% → Training

20% → Validation

10% → Testing

All images were moved along with their corresponding label files.
Image names and label names were verified to match exactly.

3️ Created data.yaml

A data.yaml file was created inside the dataset folder:

path: dataset
train: images/train
val: images/val
test: images/test

names:
  0: helmet
  1: vest
  2: person

This file configures YOLOv8 for training.

4️ Dataset Verification via Training

A test training run was performed to verify configuration:

yolo task=detect mode=train model=yolov8n.pt data=dataset/data.yaml epochs=1

✔ Training started successfully
✔ No dataset errors
✔ Model completed 1 epoch

This confirmed the dataset is properly configured and ready for full training.

 Current Project Status

✔ Environment fully configured
✔ Dataset prepared in YOLO format
✔ Training pipeline verified
✔ Ready for full model training and evaluation

Completed Milestone 2 of the SafetyEye project.

Week 3:
- Trained YOLOv8 model for PPE detection.
- Generated model weights and training metrics.

Week 4:
- Tested trained model using prediction mode.
- Verified PPE detection results.

The trained model demonstrates PPE compliance detection for workplace safety monitoring.
