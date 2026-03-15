# SafetyEye – AI Powered Workplace Occupancy & Safety Monitor

## Project Overview

SafetyEye is an AI-based workplace monitoring system designed to improve safety in construction and industrial environments. The system uses computer vision and deep learning to automatically detect whether workers are wearing proper Personal Protective Equipment (PPE). It can identify safety violations such as missing helmets, masks, or safety vests and help supervisors ensure compliance with workplace safety regulations.

The system is built using the YOLOv8 object detection framework and is capable of detecting multiple objects including workers, PPE equipment, machinery, and vehicles in real time.

---

## Key Features

* PPE detection using YOLOv8
* Detection of safety equipment such as helmets, masks, and safety vests
* Identification of safety violations (missing PPE)
* Detection of workers, machinery, vehicles, and safety cones
* Real-time detection using webcam
* Image-based testing and prediction

---

## Detected Classes

The model is trained to detect the following classes:

* Hardhat
* Mask
* NO-Hardhat
* NO-Mask
* Safety Vest
* NO-Safety Vest
* Person
* Machinery
* Vehicle
* Cone

---

## Technology Stack

* Python
* YOLOv8 (Ultralytics)
* PyTorch
* OpenCV
* NumPy

---

## Project Structure

```
SafetyEye_AI/
│
├── dataset/
│   └── data.yaml
│
├── scripts/
│
├── train.py
├── detect.py
├── webcam_detect.py
├── test_images.py
├── check_labels.py
├── scan_labels.py
├── gpu_test.py
│
├── requirements.txt
└── README.md
```

---

## Dataset

The dataset consists of labeled images of construction sites containing workers and safety equipment. Each image is annotated using YOLO format with bounding boxes representing PPE items and other objects.

Dataset classes include helmets, masks, safety vests, workers, machinery, vehicles, and safety cones.

Due to repository size limitations, the full dataset images are not included in this repository.

---

## Model Training

The PPE detection model was trained using the YOLOv8 framework with multiple experimental configurations.

Training experiments included:

* Baseline model training
* Increased training epochs
* Higher image resolution
* Larger YOLOv8 model architecture

These experiments were performed to improve detection accuracy and model performance.

---

## Evaluation Metrics

Model performance was evaluated using standard object detection metrics:

* Precision
* Recall
* mAP@0.5
* mAP@0.5:0.95

These metrics help evaluate how accurately the model detects PPE equipment and safety violations.

---

## Running the Project

### Install dependencies

```
pip install -r requirements.txt
```

### Train the model

```
python train.py
```

### Run detection on images

```
python detect.py
```

### Run real-time webcam detection

```
python webcam_detect.py
```

---

## Applications

* Construction site safety monitoring
* Industrial workplace safety compliance
* Automated PPE detection systems
* Smart surveillance systems

---

## Future Improvements

* Real-time alert system for safety violations
* Integration with CCTV monitoring systems
* Deployment on edge devices
* Dashboard for safety analytics

---

## Author

Lakshmi Pravallika
SafetyEye AI Project – Workplace Occupancy & Safety Monitoring System
