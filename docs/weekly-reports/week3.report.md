# SafetyEye – AI Powered Workplace Occupancy & Safety Monitor

## Weekly Progress Report (Week 3)

**Intern:** Mohammed Ateeq Ur Rahman  
**Program:** Infosys Virtual Internship  
**Project:** SafetyEye – AI Powered Workplace Occupancy & Safety Monitor  
**Framework:** YOLOv8 (Ultralytics)  
**Hardware Used:** NVIDIA GTX 1650 Ti GPU (4GB)  
**Software:** Python, PyTorch, Ultralytics YOLOv8, OpenCV, VS Code  

---

## Week 3 – Full Model Training and Evaluation

### Objective

Week 3 focused on performing full model training and analyzing model performance.

---

## Full Training

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

The results indicated a **significant improvement compared to the initial training**.

---

## Training Metrics Analysis

### Precision

Precision measures how many predicted objects are correct.

**Precision achieved:**  
**0.857**

### Recall

Recall measures how many actual objects were detected.

**Recall achieved:**  
**0.683**

### mAP@0.5

This is the main metric used to evaluate detection performance.

**mAP@0.5 = 0.763**

### mAP@0.5:0.95

This is a stricter metric evaluating bounding box accuracy across multiple thresholds.

**mAP@0.5:0.95 = 0.506**

---

## Model Validation

The trained model was validated on the **validation dataset**.

Validation results confirmed **stable model performance across multiple object classes**.

---

## Test Predictions

The model was tested on **unseen test images** to evaluate generalization.


## Conclusion

Week 3 focused on full model training and evaluation using the **YOLOv8n model**. The model was trained for **50 epochs using GPU acceleration**, which significantly improved the detection performance. Evaluation metrics such as **precision, recall, and mAP** were analyzed to understand model accuracy and performance on the validation dataset.

---

## Key Results

- Model used: **YOLOv8n**
- Training epochs: **50**
- Image size: **640**
- Precision: **0.857**
- Recall: **0.683**
- mAP@0.5: **0.763**
- mAP@0.5:0.95: **0.506**