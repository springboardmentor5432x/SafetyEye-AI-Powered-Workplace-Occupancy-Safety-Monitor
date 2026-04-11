# SafetyEye - AI-Powered Workplace Safety Monitor

An AI-powered real-time workplace safety monitoring system that automatically detects PPE (Personal Protective Equipment) violations on construction sites using YOLOv8 computer vision.

---

## Project Overview

SafetyEye uses a trained YOLOv8 model to detect workers and identify safety violations such as missing helmets, safety vests and masks from live video feeds, recorded footage or CCTV streams. The system provides a complete web dashboard with real-time analytics and violation logging.

---

## Tech Stack

| Tool | Purpose |
|---|---|
| Python 3.11.9 | Core programming language |
| YOLOv8 (Ultralytics 8.4.21) | Object detection model |
| OpenCV | Video capture and visualization |
| PyTorch 2.1.0 | Deep learning framework |
| Google Colab (Tesla T4) | GPU training environment |
| Streamlit | Web dashboard |
| SQLite | Violation logging database |
| Pandas | Data processing and analytics |

---

## Dataset

- Source: Roboflow Construction Site Safety Dataset
- Total Images: ~3000 labeled images
- Annotation Format: YOLO format (.txt label files)
- Split: 70% Train / 20% Validation / 10% Test

### Classes (10 Total)

| Class ID | Name | Type |
|---|---|---|
| 0 | Hardhat | Safe PPE |
| 1 | Mask | Safe PPE |
| 2 | NO-Hardhat | Violation |
| 3 | NO-Mask | Violation |
| 4 | NO-Safety Vest | Violation |
| 5 | Person | Detection |
| 6 | Safety Cone | Detection |
| 7 | Safety Vest | Safe PPE |
| 8 | Machinery | Detection |
| 9 | Vehicle | Detection |

---

## Model Performance

### Validation Results
| Metric | Score |
|---|---|
| Precision | 89.1% |
| Recall | 68.8% |
| mAP50 | 78.3% |
| mAP50-95 | 46.7% |

### Test Results (Official)
| Metric | Score |
|---|---|
| Precision | 85.5% |
| Recall | 66.7% |
| mAP50 | 73.3% |
| mAP50-95 | 44.3% |

---

## Project Structure
SafetyEye/
├── reports/
│   ├── Milestone1_Report.docx
│   ├── Milestone2_Report.docx
│   ├── Milestone4_Report.docx
│   └── SafetyEye_Overall_Report.docx
├── src/
│   ├── data_prep.py
│   ├── train.py
│   ├── detect.py
│   ├── database.py
│   └── dashboard.py
├── models/
│   └── best.pt
├── dataset.yaml
├── requirements.txt
└── violations.db

---

## Milestones

| Milestone | Description | Status |
|---|---|---|
| 1 | Data Preparation and Environment Setup | Complete |
| 2 | Model Training and PPE Detection | Complete |
| 3 | Real-Time Detection and Alert System | Complete |
| 4 | Dashboard and Reporting System | Complete |

---

## Features

- Real time PPE violation detection from webcam, video file or CCTV stream
- Green bounding boxes for safe detections
- Red bounding boxes for violations
- 5 second cooldown to prevent duplicate alerts
- Console alerts with timestamps
- Streamlit web dashboard with live video feed
- SQLite database logging all violations
- Bar chart and timeline analytics
- Complete violation log table
- Confidence threshold control

---

## How to Run

```bash
# Clone the repository
git clone https://github.com/preethiguggulla/SafetyEye.git

# Install dependencies
pip install -r requirements.txt

# Run real time detection
python src/detect.py

# Run dashboard
streamlit run src/dashboard.py
```

---

## Reports

- Milestone 1 Report - reports/Milestone1_Report.docx
- Milestone 2 Report - reports/Milestone2_Report.docx
- Milestone 3 Report - reports/Milestone2_Report.docx
- Milestone 4 Report - reports/Milestone4_Report.docx
- Overall Project Report - reports/SafetyEye_Overall_Report.docx

---

## Author

Preethi Guggulla
LinkedIn: linkedin.com/in/guggullapreethivarshitha
