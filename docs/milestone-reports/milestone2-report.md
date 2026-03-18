# SafetyEye – AI Powered Workplace Occupancy & Safety Monitor

## Milestone 2 Report

**Intern:** Mohammed Ateeq Ur Rahman  
**Program:** Infosys Virtual Internship  
**Project:** SafetyEye – AI Powered Workplace Occupancy & Safety Monitor  
**Framework:** YOLOv8 (Ultralytics)  
**Hardware Used:** NVIDIA GTX 1650 Ti GPU (4GB)  
**Software:** Python, PyTorch, Ultralytics YOLOv8, OpenCV, VS Code  

---

# Milestone 2 Objectives

The main objectives of Milestone 2 were:

- Perform full model training using the prepared dataset  
- Evaluate model performance using standard detection metrics  
- Improve model performance through experimentation and hyperparameter tuning  
- Identify the best-performing model configuration  

---

# Week 3 – Full Model Training and Evaluation

## Objective

The goal of Week 3 was to perform **full model training** using the YOLOv8 model and evaluate its performance using detection metrics such as precision, recall, and mean Average Precision (mAP).

---

## Model Training

The **YOLOv8 Nano (YOLOv8n)** model was trained for **50 epochs** using GPU acceleration.

### Training Configuration

| Parameter  | Value              |
| Model      | YOLOv8n            |
| Epochs     | 50                 |
| Image Size | 640                |
| Hardware   | NVIDIA GTX 1650 Ti |

---

## Training Results

| Metric    | Value |
| Precision | 0.857 |
| Recall    | 0.683 |
| mAP50     | 0.763 |
| mAP50-95  | 0.506 |

These results showed a **significant improvement compared to the initial training performed in Milestone 1**.

---

## Training Metrics Analysis

### Precision
Precision measures how many predicted objects are correctly detected.

**Precision achieved:** 0.857

### Recall
Recall measures how many actual objects were successfully detected.

**Recall achieved:** 0.683

### mAP@0.5
Mean Average Precision at 0.5 IoU threshold measures overall detection performance.

**mAP@0.5 = 0.763**

### mAP@0.5:0.95
This metric evaluates bounding box accuracy across multiple thresholds.

**mAP@0.5:0.95 = 0.506**

---

## Model Validation

The trained model was validated on the **validation dataset**, confirming stable performance across multiple object classes.

---

## Test Predictions

The trained model was tested on unseen test images to evaluate generalization.

The system successfully detected objects such as:

- Person
- Helmet
- Safety Vest
- Machinery
- Safety Cone

---

# Week 4 – Model Optimization and Performance Improvement

## Objective

The objective of Week 4 was to improve model performance through **hyperparameter tuning and model experimentation**.

---

# Experiment 1 – Increase Epochs

### Configuration

| Parameter  | Value   |
| Model      | YOLOv8n |
| Epochs     | 100     |
| Image Size | 640     |

### Results

| Metric    | Value |
| Precision | 0.873 |
| Recall    | 0.723 |
| mAP50     | 0.795 |
| mAP50-95  | 0.542 |

Increasing the number of epochs improved the **model's learning capability**.

---

# Experiment 2 – Increase Image Resolution

### Configuration

| Parameter  | Value   |
| Model      | YOLOv8n |
| Epochs     | 50      |
| Image Size | 800     |

### Results

| Metric    | Value |
| Precision | 0.845 |
| Recall    | 0.685 |
| mAP50     | 0.766 |
| mAP50-95  | 0.484 |

Increasing image resolution increased computational cost but did not significantly improve detection accuracy.

---

# Experiment 3 – Larger Model

### Configuration

| Parameter  | Value   |
| Model      | YOLOv8s |
| Epochs     | 50      |
| Image Size | 640     |

### Results

| Metric    | Value |
| Precision | 0.885 |
| Recall    | 0.730 |
| mAP50     | 0.802 |
| mAP50-95  | 0.536 |

The larger model achieved the **best detection performance** among all experiments.

---

# Data Augmentation Experiment

### Augmentation Techniques Applied

- Mosaic  
- Horizontal Flip  
- Brightness Adjustment  
- Saturation Variation  

### Results

| Metric    | Value |
| Precision | 0.874 |
| Recall    | 0.727 |
| mAP50     | 0.803 |
| mAP50-95  | 0.536 |

Data augmentation slightly improved the **generalization capability of the model**.

---

# Final Model Selection

The best performing configuration was:

| Parameter  | Value   |
| Model      | YOLOv8s |
| Epochs     | 50      |
| Image Size | 640     |
| Precision  | 0.885   |
| Recall     | 0.730   |
| mAP50      | 0.802   |

---

# Error Analysis

Some limitations were observed during prediction:

1. Small objects such as **gloves** were sometimes missed.  
2. Helmet detection occasionally failed when the helmet was **partially occluded**.  
3. **Crowded scenes** caused overlapping bounding boxes.  
4. **Low lighting conditions** reduced detection accuracy.

---

# Possible Improvements

- Increasing dataset size  
- Collecting more **small object samples**  
- Using **higher resolution training**  
- Training with larger models such as **YOLOv8m**

---

# Experiment Comparison Table

| Experiment        | Model   | Epochs | Image Size | Precision | Recall | mAP50 | mAP50-95 |
| Baseline (Week 3) | YOLOv8n | 50     | 640        | 0.857     | 0.683  | 0.763 | 0.506    |
| Experiment 1      | YOLOv8n | 100    | 640        | 0.873     | 0.723  | 0.795 | 0.542    |
| Experiment 2      | YOLOv8n | 50     | 800        | 0.845     | 0.685  | 0.766 | 0.484    |
| Experiment 3      | YOLOv8s | 50     | 640        | 0.885     | 0.730  | 0.802 | 0.536    |
| Augmentation      | YOLOv8s | 50     | 640        | 0.874     | 0.727  | 0.803 | 0.536    |

---

# Milestone 2 Results

Key outcomes achieved during Milestone 2:

- Full YOLOv8 model training completed  
- Model performance evaluated using precision, recall, and mAP  
- Multiple optimization experiments performed  
- Best-performing model configuration identified  

---

# Milestone 2 Conclusion

Milestone 2 focused on **model training, evaluation, and optimization**. The YOLOv8 model was trained using the prepared dataset and evaluated using standard object detection metrics.

Several experiments were conducted to improve performance, including increasing training epochs, modifying image resolution, using a larger model architecture, and applying data augmentation techniques.

Among all configurations, the **YOLOv8s model with 50 epochs and 640 image size achieved the best performance**, providing strong precision and detection accuracy. This optimized model will be used for the next stage of the project, which involves implementing **real-time detection and safety violation monitoring**.