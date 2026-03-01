# SafetyEye  
# AI-Powered Workplace Occupancy & Safety Monitoring System  

---

## Project Overview

SafetyEye is an AI-powered computer vision system designed to monitor construction sites and workplaces for safety compliance and occupancy monitoring. The system detects Personal Protective Equipment (PPE) usage and identifies unsafe conditions in real time using object detection models.

The primary objective of this project is to:

- Detect PPE compliance (Hardhat, Mask, Safety Vest)
- Identify safety violations (NO-Hardhat, NO-Mask, NO-Safety Vest)
- Detect persons, machinery, vehicles, and safety cones
- Build a structured and reproducible training pipeline using YOLOv8
- Prepare the foundation for a real-time workplace safety monitoring system

This project is being developed as part of the internship milestone tasks.

---

# Milestone 1: Data Preparation & Environment Setup

Milestone 1 focused on dataset preparation, validation, class identification, environment configuration, and pipeline verification.

All Week 1 and Week 2 tasks under Milestone 1 have been successfully completed.

---

## Week 1 Tasks – Dataset Preparation & Understanding

### 1. Dataset Source

The dataset used for this project is the "Construction Site Safety Image Dataset" obtained from Kaggle.

The dataset contains annotated construction site images for detecting Personal Protective Equipment (PPE) and other safety-related objects.

---

### 2. Dataset Structure

The dataset follows the YOLO object detection format.

Directory structure:

dataset/
│
├── train/
│   ├── images/
│   └── labels/
│
├── valid/
│   ├── images/
│   └── labels/
│
├── test/
│   ├── images/
│   └── labels/
│
└── data.yaml

Each image has a corresponding label file in YOLO format:

<class_id> <x_center> <y_center> <width> <height>

- class_id represents the object class index.
- Bounding box coordinates are normalized between 0 and 1.

---

### 3. Class Identification

Label files were inspected to determine the number of object classes.

- Class IDs range from 0 to 9
- Total number of classes = 10

The dataset contains the following 10 safety-related classes:

0: Hardhat  
1: Mask  
2: NO-Hardhat  
3: NO-Mask  
4: NO-Safety Vest  
5: Person  
6: Safety Cone  
7: Safety Vest  
8: Machinery  
9: Vehicle  

These class definitions were obtained from the official dataset source and confirmed inside `data.yaml`.

---

### 4. Dataset Split Verification

The dataset was programmatically verified and reorganized into the required academic split ratio.

Total images: 2801  

Final split:

- Train: 1960 images (70%)
- Validation: 560 images (20%)
- Test: 281 images (10%)

The dataset is now cleanly structured and aligned with the required 70-20-10 split.

---

## Week 2 Tasks – Verification, Testing & Environment Setup

### 5. Data Verification

The following verification steps were performed:

- Verified YOLO label format consistency
- Confirmed class IDs range from 0 to 9
- Confirmed each image has a corresponding .txt label file
- Opened and displayed sample images using OpenCV
- Validated bounding box alignment visually
- Successfully ran a YOLOv8 training pipeline test

---

### 6. Training Pipeline Validation

A 1-epoch training test was executed using YOLOv8 to verify:

- Dataset configuration
- data.yaml correctness
- Model compatibility
- Training pipeline functionality

Training was successfully completed for 1 epoch and model weights were generated inside:

runs/detect/train/

Validation metrics were successfully computed, confirming that the dataset and configuration are correct.

Inference was also performed successfully on test images.

This confirms that the full training and inference pipeline is functioning properly.

---

### 7. Data Cleaning & Organization

- Removed unnecessary extracted folders (results_yolo_v8, source_files)
- Ensured only required dataset folders remain
- Maintained structured project organization

Current project structure:

- dataset/
- scripts/
- models/
- notebooks/
- runs/
- venv/

The project architecture is clean and reproducible.

---

### 8. Environment Setup

Development Environment:

- Python 3.10.11
- Virtual environment created using venv
- Visual Studio Code

Installed Libraries:

- ultralytics (YOLOv8)
- torch (PyTorch)
- opencv-python
- numpy
- pandas
- scikit-learn
- matplotlib

Verification:

- YOLOv8 installed successfully
- `yolo` command runs correctly
- Training pipeline executes without errors
- Model weights generated successfully
- 1 epoch training test completed successfully

---

# Milestone 1 Completion Status

All Week 1 and Week 2 tasks have been completed:

- Dataset downloaded and organized
- 70-20-10 split implemented
- YOLO format verified
- Classes identified and confirmed
- Environment configured
- Training pipeline validated
- 1 epoch training test executed successfully
- Inference verified

Milestone 1 is successfully completed.