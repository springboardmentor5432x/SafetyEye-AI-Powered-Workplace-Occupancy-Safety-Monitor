# SafetyEye – AI Powered Workplace Occupancy & Safety Monitor

## Milestone 1 Report

**Intern:** Mohammed Ateeq Ur Rahman  
**Program:** Infosys Virtual Internship  
**Project:** SafetyEye – AI Powered Workplace Occupancy & Safety Monitor  
**Framework:** YOLOv8 (Ultralytics)  
**Hardware Used:** NVIDIA GTX 1650 Ti GPU (4GB)  
**Software:** Python, PyTorch, Ultralytics YOLOv8, OpenCV, VS Code  

---

# Project Overview

SafetyEye is an AI-powered workplace monitoring system designed to improve safety compliance in construction and industrial environments. The system uses computer vision and deep learning techniques to automatically detect safety-related objects such as helmets, safety vests, workers, and machinery.

The goal of the system is to monitor workplace environments and identify potential safety violations to improve worker safety.

---

# Milestone 1 Objectives

The main objectives of Milestone 1 were:

- Setting up the development environment
- Exploring and verifying the dataset
- Preparing the dataset for training
- Configuring the YOLOv8 training pipeline
- Performing initial model training

---

# Week 1 – Environment Setup and Dataset Exploration

## Objective

The objective of Week 1 was to set up the development environment, understand the dataset structure, and verify dataset quality to ensure smooth model training.

---

## Environment Setup

The development environment was configured with the following tools and libraries:

- Python  
- Virtual Environment (`venv`)  
- PyTorch  
- Ultralytics YOLOv8  
- OpenCV  
- NumPy  
- Matplotlib  
- VS Code  

A virtual environment was created to maintain project dependencies separately.

---

## GitHub Repository Setup

The project repository was cloned from GitHub and organized into a structured format.

### Repository Structure
dataset/
images/
labels/
scripts/
docs/
notebooks/

This structure helps maintain clean project organization and improves collaboration.

---

## Dataset Exploration

The dataset used in the project is the **Construction Site Safety Dataset** obtained from **Roboflow**.

### Dataset Details

- Total images: **2801**
- Annotation format: **YOLOv8**
- Number of classes: **10**

### Classes in the Dataset

- Hardhat 
- Mask  
- NO-Hardhat 
- NO-Mask 
- Safety Vest  
- NO-Safety Vest
- Safety Cone  
- Person 
- Machinery
- Vehicle

---

## Dataset Verification

Custom scripts were developed to verify dataset quality.

The verification process checked for:

- Missing label files
- Empty label files
- Incorrect label formats

### Dataset Verification Results

| Split      | Images | Labels | Missing Labels | Empty Labels |
| Train      | 1960   | 1960   | 0              | 15           |
| Validation | 560    | 560    | 0              | 7            |
| Test       | 281    | 281    | 0              | 2            |

The dataset was successfully verified and confirmed to be ready for model training.

---

## Image Visualization

OpenCV was used to visualize sample images from the dataset to ensure:

- Images were readable
- Labels corresponded correctly with objects
- Bounding boxes were properly aligned with annotated objects

---

# Week 2 – Dataset Preparation and Initial Training

## Objective

The objective of Week 2 was to finalize dataset preparation and perform the first model training to verify the YOLO training pipeline.

---

## Dataset Splitting

The dataset was divided into three subsets for training and evaluation.

| Dataset Split | Percentage |
| Training      | 70%        |
| Validation    | 20%        |
| Testing       | 10%        |

### Final Dataset Distribution

| Split      | Images |
| Training   | 1960   |
| Validation | 560    |
| Testing    | 281    |

---

## Class Identification

A script was used to scan label files and identify class IDs.

Detected class IDs:
[0,1,2,3,4,5,6,7,8,9]

Total classes detected: **10**

These classes were mapped to their respective class names in the **data.yaml** configuration file.

---

## YOLO Configuration

The dataset configuration file was created as follows:

```yaml
path: dataset
train: images/train
val: images/val
test: images/test

names:
- Hardhat 
- Mask  
- NO-Hardhat 
- NO-Mask 
- Safety Vest  
- NO-Safety Vest
- Safety Cone  
- Person 
- Machinery
- Vehicle


## Initial Model Training

A preliminary training run was executed to verify the YOLO training pipeline.

raining command:
yolo detect train data=dataset/data.yaml model=yolov8n.pt epochs=1 imgsz=640

### Initial Training Result

Metric Value
Precision 0.464
Recall 0.330
mAP50 0.314
mAP50-95 0.170

The results confirmed that the model training pipeline was functioning correctly.

## Milestone 1 Results

### Key Outcomes Achieved During Milestone 1

- Development environment successfully configured  
- Dataset verified and prepared for training  
- Dataset split into training, validation, and testing sets  
- YOLOv8 dataset configuration created  
- Initial model training pipeline verified  

---

### Key Metrics

- **Training images:** 1960  
- **Validation images:** 560  
- **Test images:** 281  

### Initial Training Performance

- **Precision:** 0.464  
- **Recall:** 0.330  
- **mAP@0.5:** 0.314  
- **mAP@0.5:0.95:** 0.170  

---

## Milestone 1 Conclusion

Milestone 1 successfully established the **foundation for the SafetyEye system**. The development environment was configured, the dataset was explored and verified, and the training pipeline was successfully implemented.

The initial YOLOv8 model training confirmed that the system is **ready for further model training, optimization, and performance improvements** in the next