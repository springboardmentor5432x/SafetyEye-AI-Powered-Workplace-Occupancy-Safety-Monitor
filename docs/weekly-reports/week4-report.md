# SafetyEye – AI Powered Workplace Occupancy & Safety Monitor

## Weekly Progress Report (Week 4)

**Intern:** Mohammed Ateeq Ur Rahman  
**Program:** Infosys Virtual Internship  
**Project:** SafetyEye – AI Powered Workplace Occupancy & Safety Monitor  
**Framework:** YOLOv8 (Ultralytics)  
**Hardware Used:** NVIDIA GTX 1650 Ti GPU (4GB)  
**Software:** Python, PyTorch, Ultralytics YOLOv8, OpenCV, VS Code  

---

## Week 4 – Model Optimization and Performance Improvement

### Objective

The goal of Week 4 was to improve the model through **hyperparameter tuning and model experimentation**.

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

Increasing image resolution slightly increased **computational cost** but did not significantly improve performance.

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

The larger model provided the **best detection performance**.

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

Data augmentation slightly improved the **generalization ability of the model**.

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
2. **Helmet detection** occasionally failed when the helmet was partially hidden.  
3. **Crowded scenes** caused overlapping bounding boxes.  
4. **Low lighting conditions** reduced detection accuracy.

### Possible Improvements

- Increasing dataset size  
- Collecting more **small object samples**  
- Using **higher resolution training**  
- Training with larger models such as **YOLOv8m**

---

# Week 4 Experiment Comparison Table

| Experiment        | Model   | Epochs | Image Size | Precision | Recall | mAP50 | mAP50-95 |
| Baseline (Week 3) | YOLOv8n | 50     | 640        | 0.857     | 0.683  | 0.763 | 0.506    |
| Experiment 1      | YOLOv8n | 100    | 640        | 0.873     | 0.723  | 0.795 | 0.542    |
| Experiment 2      | YOLOv8n | 50     | 800        | 0.845     | 0.685  | 0.766 | 0.484    |
| Experiment 3      | YOLOv8s | 50     | 640        | 0.885     | 0.730  | 0.802 | 0.536    |
| Augmentation      | YOLOv8s | 50     | 640        | 0.874     | 0.727  | 0.803 | 0.536    |

---

# Conclusion

Week 4 focused on **model optimization and performance improvement** through multiple experiments such as increasing epochs, modifying image resolution, using a larger model architecture, and applying data augmentation techniques.

Among all experiments, the **YOLOv8s model with 50 epochs and 640 image size provided the best balance between accuracy and performance**. These experiments helped improve the detection capability of the SafetyEye system and provided insights into model limitations and potential improvements.

---

# Key Results

- Best Model: **YOLOv8s**
- Training Epochs: **50**
- Image Size: **640**
- Precision: **0.885**
- Recall: **0.730**
- mAP@0.5: **0.802**
- mAP@0.5:0.95: **0.536**