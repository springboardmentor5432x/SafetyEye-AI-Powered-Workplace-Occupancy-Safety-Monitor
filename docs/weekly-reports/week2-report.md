# SafetyEye – AI Powered Workplace Occupancy & Safety Monitor

## Weekly Progress Report (Week 2)

**Intern:** Mohammed Ateeq Ur Rahman  
**Program:** Infosys Virtual Internship  
**Project:** SafetyEye – AI Powered Workplace Occupancy & Safety Monitor  
**Framework:** YOLOv8 (Ultralytics)  
**Hardware Used:** NVIDIA GTX 1650 Ti GPU (4GB)  
**Software:** Python, PyTorch, Ultralytics YOLOv8, OpenCV, VS Code  

---

## Week 2 – Dataset Preparation and Initial Training

### Objective

The main goal of Week 2 was to finalize dataset preparation, verify label correctness, and perform the first model training.

---

## Dataset Splitting

The dataset was split into three parts:

| Dataset Split | Percentage |
| Training      | 70% |
| Validation    | 20% |
| Testing       | 10% |

### Final Dataset Distribution

| Split | Images |
|------|-------|
| Training | 1960 |
| Validation | 560 |
| Testing | 281 |

---

## Class Identification

A script was used to scan all label files and identify class IDs.

**Detected Classes**
[0,1,2,3,4,5,6,7,8,9]

**Total Classes:** 10  

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
- person
- helmet
- safety_vest
- head
- machinery
- safety_cone
- gloves
- boots
- face_mask
- tools

--

Initial Training

A preliminary training run was executed to verify the training pipeline.

Training command:
yolo detect train data=dataset/data.yaml model=yolov8n.pt epochs=1 imgsz=640

Initial Training Result

Metric    | Value |
Precision | 0.464 |
Recall    | 0.330 |
mAP50     | 0.314 |
mAP50-95  | 0.170 |

This confirmed that the model training pipeline was functioning correctly.

Conclusion:

In Week 2, the dataset preparation process was finalized by splitting the dataset into
training, validation, and testing sets. The YOLO configuration file (data.yaml) was
created to define dataset paths and class names. A preliminary training run was
performed using YOLOv8n to confirm that the training pipeline was functioning
correctly.

Key Results:
• Dataset split ratio: 70% Train, 20% Validation, 10% Test
• Training images: 1960
• Validation images: 560
• Test images: 281
• Initial training results:
o Precision: 0.464
o Recall: 0.330
o mAP@0.5: 0.314
o mAP@0.5:0.95: 0.170