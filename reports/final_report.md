# SafetyEye: AI-Based Workplace Safety Monitoring System

## Final Report

**Project Title:** SafetyEye - AI-Based Workplace Occupancy and Safety Monitor   
**Platform:** Python, YOLOv8, OpenCV, Streamlit  

---

## Abstract

SafetyEye is a workplace-safety monitoring prototype built around YOLOv8, OpenCV, and Streamlit. Its purpose is to detect workers and PPE-related objects, estimate whether the detected people appear compliant, and present the results through a live dashboard with simple analytics and stored evidence.

In its current form, the project combines four connected stages: dataset preparation, detector training, real-time violation detection, and dashboard integration. The application works with a webcam or uploaded video, writes events to CSV logs, saves screenshots for review, and visualizes recent activity through charts and summary panels.

This report explains the problem the project addresses, the dataset and tools used, the milestone-by-milestone build process, the final system structure, the evaluation results, and the practical limits of the current prototype.

**Keywords:** workplace safety, PPE detection, YOLOv8, Streamlit, computer vision, violation monitoring, dashboard analytics

---

## 1. Introduction

Construction and industrial workplaces require strict compliance with safety protocols, especially the use of PPE such as helmets and reflective safety vests. In many environments, safety supervision is still done manually, which can be slow, inconsistent, and difficult to scale across multiple workers or sites.

SafetyEye was developed as an academic prototype to explore how computer vision can assist with this problem. The core idea is to monitor a video stream, detect workers and PPE items, determine whether required equipment is missing, and present the results through an interactive dashboard. The project is structured milestone by milestone so that each stage builds toward a complete end-to-end monitoring system.

The final application demonstrates a practical workflow:

**Video Input -> Object Detection -> PPE Rule Evaluation -> Violation Logging -> Dashboard Analytics**

---

## 2. Problem Statement

Manual supervision alone is often insufficient for real-time workplace safety enforcement. Supervisors may miss violations in crowded scenes, during busy work periods, or when multiple work areas must be monitored at once. This creates a need for an automated system that can:

- observe live or recorded workplace video,
- detect people and PPE objects,
- identify missing required safety equipment,
- highlight violations clearly,
- store incident records for review, and
- present the information in an easy-to-use dashboard.

SafetyEye addresses this need by combining object detection with simple safety rules and dashboard-based analytics.

---

## 3. Objectives

The main objectives of the project are:

1. Build a dataset-ready development environment for safety monitoring experiments.
2. Train a YOLOv8 model for PPE and safety-related object detection.
3. Develop a real-time detection and alert pipeline for video input.
4. Build a dashboard for live monitoring, analytics, and incident review.
5. Store detected violations for future reporting and analysis.
6. Integrate all project modules into a single working application.

---

## 4. Milestone-Wise Development

### 4.1 Milestone 1: Environment Setup and Dataset Preparation

Milestone 1 focused on setting up the project structure, installing the required Python libraries, downloading the construction safety dataset, and preparing the data in YOLOv8 format.

The SafetyEye project was organized using the following main folders:

```text
SafetyEye/
├── dataset/
├── scripts/
├── models/
├── notebooks/
```

The dataset was arranged into standard YOLOv8 training directories:

```text
dataset/
├── images/
│   ├── train/
│   ├── val/
│   └── test/
├── labels/
│   ├── train/
│   ├── val/
│   └── test/
└── data.yaml
```

The final split counts in the current repository are:

- Train: 1960 images and 1960 labels
- Validation: 560 images and 560 labels
- Test: 281 images and 281 labels

This milestone also included helper scripts for checking annotations and verifying dataset structure before training.

### 4.2 Milestone 2: Model Training and PPE Detection

Milestone 2 originally concluded with a stable submission run preserved under `runs/detect/train4/`. That milestone run used:

- YOLOv8 small model (`yolov8s.pt`)
- 25 epochs
- image size 640
- CPU device

The final row of `runs/detect/train4/results.csv` records:

- Precision: 0.87522
- Recall: 0.72093
- mAP@0.5: 0.80358
- mAP@0.5:0.95: 0.54729

After the milestone submission, the project continued training experiments. The repository also contains a later improved run under `runs/detect/train7/` with:

- YOLOv8 small model (`yolov8s.pt`)
- 200 epochs
- image size 800
- batch size 16
- AdamW optimizer

The final row of `runs/detect/train7/results.csv` records:

- Precision: 0.91709
- Recall: 0.76071
- mAP@0.5: 0.84172
- mAP@0.5:0.95: 0.59459

The deployed application loads packaged weights from `models/best.pt`, while the later `train7` record is used in this report to summarize the best documented training metrics preserved in the repository.

### 4.3 Milestone 3: Real-Time Detection and Alert System

Milestone 3 extended the project from image-based detection to live monitoring. The real-time implementation is centered around:

- `scripts/main_detection.py`
- `scripts/violation_rules.py`
- `scripts/alert_system.py`

This stage added:

- webcam or video stream processing with OpenCV
- real-time inference using the trained YOLO model
- person-level PPE rule checks
- on-screen detection overlays
- alert logging and screenshot capture

The alert system saves evidence into `violation_screenshots/` and writes text logs to `violations.log`.

### 4.4 Milestone 4: Dashboard and Final Integration

The final stage integrated the earlier work into a browser-based dashboard. The current final application lives in:

- `app.py`

The implemented dashboard is a single Streamlit page that combines:

- live monitoring output
- a right-side status and metrics panel
- violation charts
- a recent-log table

This final system adds CSV-based logging, screenshot evidence, analytics charts, and a more polished interface suitable for demonstration.

---

## 5. Dataset Description

The project uses the Construction Site Safety dataset, which contains labeled construction-site images for PPE and related object detection.

The current dataset configuration file, `dataset/data.yaml`, defines 10 classes:

1. Hardhat
2. Mask
3. NO-Hardhat
4. NO-Mask
5. NO-Safety Vest
6. Person
7. Safety Cone
8. Safety Vest
9. machinery
10. vehicle

This class structure is useful because it allows the system to learn both normal PPE objects and explicit violation-related labels.

---

## 6. Technology Stack

The final system uses the following technologies:

- Python for implementation
- Ultralytics YOLOv8 for object detection
- PyTorch as the deep learning backend
- OpenCV for video capture and frame processing
- Streamlit for the dashboard
- Pandas for tabular data handling
- NumPy for numerical operations
- Plotly for interactive analytics charts
- CSV-based logging using Pandas and Python file I/O

### Development Environment

- Operating System: macOS 26.4 arm64
- Python Version: 3.10.11
- GPU: not explicitly configured in the current final app

---

## 7. Final System Architecture

The final SafetyEye architecture consists of five main layers:

### 7.1 Input Layer

The system accepts video input from:

- webcam
- uploaded video file

### 7.2 Detection Layer

The YOLOv8 model performs object detection and returns:

- class labels
- confidence scores
- bounding boxes

### 7.3 Safety Rule Layer

Detected PPE items are matched to each detected person using overlap and position-based logic. This allows the system to estimate whether a worker is compliant or violating the PPE rules.

### 7.4 Storage Layer

The current application stores operational outputs in local files:

- `violations.csv` for dashboard log records
- `violations.log` for text-based alert history from the OpenCV pipeline
- `violation_screenshots/` for saved evidence images

### 7.5 Dashboard Layer

The dashboard displays:

- live detection output
- current violation status
- summary metrics
- analytics charts
- recent historical logs

---

## 8. Methodology

### 8.1 Object Detection

Each incoming frame is passed through the trained YOLOv8 model. The model identifies people, PPE items, and other construction-related objects.

### 8.2 Detection Parsing

The root dashboard converts YOLO results into a simplified list of labels, confidence scores, and bounding boxes before applying the PPE rules. This keeps the monitoring logic easier to manage inside the Streamlit app.

### 8.3 PPE-to-Person Matching

The project uses person-level reasoning instead of only frame-level reasoning. For each detected worker, the system checks whether a helmet or vest overlaps the appropriate body region. This reduces the chance of marking the whole frame compliant simply because one item exists somewhere in the scene.

### 8.4 Violation Creation

If a required PPE item is missing, the current root dashboard creates a violation event that can be logged with:

- timestamp
- violation type
- confidence
- source information
- screenshot path

### 8.5 Debouncing and Logging

Repeated detections across consecutive frames can create duplicate alerts. To reduce noise, the system applies a debouncing mechanism before writing violations to storage.

---

## 9. Dashboard Implementation

The current dashboard is implemented as a single Streamlit page.

It includes:

- a live monitoring panel that displays the processed video frame with boxes, labels, FPS, people count, compliance percentage, and active warnings
- a status section showing the active source, current people count, current compliance, and active alerts
- summary metrics for total logged violations, hardhat-related violations, and vest-related violations
- a violation-type bar chart and a timeline chart grouped by minute
- a recent-log table sourced from `violations.csv`

---

## 10. Results

The repository preserves two important detector-result checkpoints:

- Original Milestone 2 submission run (`runs/detect/train4/`): precision 0.87522, recall 0.72093, mAP@0.5 0.80358, mAP@0.5:0.95 0.54729
- Later improved training run (`runs/detect/train7/results.csv`): precision 0.91709, recall 0.76071, mAP@0.5 0.84172, mAP@0.5:0.95 0.59459

The first set reflects the original milestone submission. The second reflects post-milestone training improvements that were preserved in the repository and are used in this final-project writeup.

Together, these values indicate that the detector performs well enough to support a real-time academic prototype. Precision is especially strong, which suggests that most reported detections are correct. Recall is lower than precision, meaning some true objects may still be missed in challenging scenes.

In addition to model-level results, the repository also contains real log files and stored outputs:

- `violations.csv`
- `violations.log`
- `violations/`
- `violation_screenshots/`

These artifacts show that the system is not only able to detect violations but also store and review them after runtime.

---

## 11. Testing and Validation

The current project validation is based on a combination of dataset checks, training metrics, code verification, and environment checks.

### 11.1 Dataset Validation

The dataset split was verified to ensure matching image and label counts in each directory.

### 11.2 Training Validation

Training validation was reviewed against both `runs/detect/train4/` for the original Milestone 2 submission result and `runs/detect/train7/` for the later improved experiment preserved in the repository.

### 11.3 Code Verification

As part of the final consolidation, the Python files were successfully compiled using:

```bash
python3 -m py_compile app.py scripts/*.py
```

This confirmed that the current codebase is free of syntax errors.

### 11.4 Environment Verification

The repository requirements were reviewed against the current dashboard implementation. In the current workspace:

- syntax compilation passed for `app.py` and `scripts/*.py`
- the root dashboard code expects `models/best.pt`, Streamlit, OpenCV, Pandas, Plotly, Ultralytics, and PyTorch
- full inference and dashboard runtime still depend on a working local PyTorch and Streamlit installation

### 11.5 Practical Validation

The presence of populated CSV logs, stored violation screenshots, and saved alert outputs indicates that the system has already been structured for real monitoring outputs and historical review.

---

## 12. Challenges Faced

Several practical challenges appeared during the project:

### 12.1 Dataset Preparation

Preparing the dataset in YOLOv8 format required ensuring that:

- every image had a matching label file
- label IDs matched the configured classes
- directory structure was correct for training

### 12.2 Model Accuracy vs. Speed

Training and inference both required trade-offs between:

- image size
- model size
- processing speed
- detection quality

### 12.3 Person-to-PPE Association

In crowded or overlapping scenes, it is difficult to accurately determine which PPE item belongs to which person.

### 12.4 Real-Time Responsiveness

Continuous inference on live frames can slow down the system on limited hardware. This required careful decisions about FPS, frame skip, and debouncing.

### 12.5 Final Integration

Combining model inference, rule logic, persistent logging, analytics, and dashboard rendering into a single application was more complex than developing each component separately.

---

## 13. Limitations

The current SafetyEye prototype still has a number of limitations:

- detection quality depends heavily on training data quality
- difficult lighting or occlusion can reduce accuracy
- dense multi-person scenes make PPE matching harder
- the system is currently a local prototype, not a production deployment
- advanced alert channels such as email or messaging are not yet integrated in the final root app

---

## 14. Future Scope

The project can be improved in several ways:

1. Add more PPE classes such as gloves, goggles, and safety shoes with stronger model support.
2. Integrate person tracking across frames to improve per-worker consistency.
3. Add automated notification channels such as email, SMS, or messaging alerts.
4. Support multi-camera centralized monitoring.
5. Add downloadable PDF compliance summaries and scheduled reports.
6. Move storage to a cloud database for remote monitoring and access control.
7. Improve deployment readiness for industrial use.

---

## 15. Conclusion

SafetyEye shows how a modest but well-structured computer-vision pipeline can support workplace safety monitoring. The project progressed from dataset preparation and model training into real-time detection, alerting, and finally a dashboard workflow that makes the outputs easier to inspect and present.

The current system combines:

- trained YOLOv8 detection
- person-level PPE checking
- incident logging
- analytics and trends
- a browser-based monitoring dashboard

As an academic prototype, SafetyEye achieves the main objective of building an AI-assisted safety monitoring platform. With additional optimization and deployment work, the system can be extended into a stronger real-world solution.

---

## 16. References

1. Ultralytics YOLOv8 Documentation  
2. OpenCV Documentation  
3. Streamlit Documentation  
4. Plotly Documentation  
5. Construction Site Safety Image Dataset (Roboflow / Kaggle)  

---

## 17. Annexure

### Annexure A: Main Project Files

- `app.py` - final integrated dashboard application
- `scripts/main_detection.py` - OpenCV-based real-time detection pipeline
- `scripts/violation_rules.py` - PPE rule engine
- `scripts/alert_system.py` - alert logging and screenshot support
- `requirements.txt` - project runtime dependencies
- `dataset/data.yaml` - dataset configuration
- `models/best.pt` - trained model weights
- `reports/milestones/` - milestone PDFs and drafts
- `reports/final_report.md` - final report

### Annexure B: Useful Output Files

- `violations.csv`
- `violations.log`
- `violations/`
- `violation_screenshots/`

### Annexure C: Suggested Screenshots for Submission

1. Main dashboard showing the live monitor and status panel
2. Dashboard charts section with violation bar chart and timeline
3. Recent log table section populated from `violations.csv`
4. Detection frame with visible violation highlight
5. Training metrics plots from `runs/detect/train4/` and `runs/detect/train7/`
