# SafetyEye – AI Powered Workplace Occupancy & Safety Monitor

## Overview
SafetyEye is an AI-based system designed to monitor workplace occupancy and enforce safety compliance using computer vision techniques powered by YOLOv8.

The system focuses on:
- Real-time people detection
- Personal Protective Equipment (PPE) detection
- Safety compliance monitoring (Hardhat, Mask, Safety Vest)
- Construction site safety monitoring
- Occupancy counting and alert generation

## Dataset Information

### Dataset Source
This project uses the **Construction Site Safety** dataset from Roboflow Universe.
- **License**: CC BY 4.0
- **Classes**: 10 object classes
  - Hardhat
  - Mask
  - NO-Hardhat
  - NO-Mask
  - NO-Safety Vest
  - Person
  - Safety Cone
  - Safety Vest
  - machinery
  - vehicle

### Dataset Structure After Download

After downloading the dataset, organize it in the following structure:

```
SafetyEye/
├── Datasets/
│   └── css-data/
│       ├── train/
│       │   ├── images/     (2605 training images)
│       │   └── labels/     (2605 YOLO format .txt files)
│       ├── valid/
│       │   ├── images/     (validation images)
│       │   └── labels/     (validation labels)
│       └── test/
│           ├── images/     (82 test images)
│           └── labels/     (82 test labels)
├── Models/
│   └── yolov8n.pt          (YOLOv8 nano pretrained model)
├── Scripts/
│   ├── main.py             (Data exploration script)
│   └── yolo.py             (Real-time detection script)
├── Output/
│   └── working/            (Output directory for results)
├── noteBook/               (Jupyter notebooks for experiments)
├── map.yaml                (Dataset configuration file)
└── requriement.txt          (Python dependencies)
```

**Important**: Place your downloaded `train`, `valid`, and `test` folders inside `Datasets/css-data/` directory.

## Current Work Done

### 1. Data Exploration (`Scripts/main.py`)
- Dataset loading and validation
- Annotation file parsing (YOLO format)
- Data statistics and distribution analysis
- Class distribution counting
- Invalid annotation detection
- DataFrame creation for train/valid/test splits



### 3. Project Structure
- Organized folder structure for datasets, models, scripts, and outputs
- YOLO format label files (class_id x_center y_center width height)
- Pretrained YOLOv8 nano model ready for inference

## Environment Setup

### Prerequisites
- Python 3.8 or higher
- pip package manager
- Webcam (for real-time detection)

### Installation Steps

1. **Clone or download this repository**
   ```bash
   cd SafetyEye
   ```

2. **Create a virtual environment (recommended)**
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On Linux/Mac
   source venv/bin/activate
   ```

3. **Install required packages**
   ```bash
   pip install -r requriment.txt
   ```

### Required Packages
The `requriment.txt` includes:
- `ultralytics` - YOLOv8 framework
- `opencv-python` - Computer vision operations
- `numpy` - Numerical computations
- `pandas` - Data manipulation
- `streamlit` - Web app framework (for future dashboard)
- `python-dotenv` - Environment variable management
- `loguru` - Advanced logging

4. **Download the YOLOv8 model**
   The YOLOv8 nano model (`yolov8n.pt`) should be placed in the `Models/` directory.
   It will be automatically downloaded on first run if not present.

5. **Download and organize the dataset**
   - Download the Construction Site Safety dataset from Roboflow
   - Extract and place `train`, `valid`, and `test` folders in `Datasets/css-data/`
   - Ensure each folder contains `images` and `labels` subdirectories

## Things to Change/Improve

### High Priority
1. **Complete `map.yaml` configuration**
   - Currently empty - needs dataset paths and class names
   - Required format:
     ```yaml
     train: ../Datasets/css-data/train/images
     val: ../Datasets/css-data/valid/images
     test: ../Datasets/css-data/test/images
     
     nc: 10  # number of classes
     names: ['Hardhat', 'Mask', 'NO-Hardhat', 'NO-Mask', 'NO-Safety Vest', 
             'Person', 'Safety Cone', 'Safety Vest', 'machinery', 'vehicle']
     ```

2. **Model Training Script**
   - Create training script to fine-tune YOLOv8 on construction safety dataset
   - Add hyperparameter configuration
   - Implement training callbacks and logging

### Medium Priority
4. **Validation Script**
   - Create validation/evaluation script for model performance
   - Add metrics: mAP, precision, recall, F1-score
   - Generate confusion matrix

5. **Inference Pipeline**
   - Enhance `yolo.py` for video file processing
   - Add batch image processing
   - Implement result saving functionality

6. **Safety Alert System**
   - Detect PPE violations (NO-Hardhat, NO-Mask, NO-Safety Vest)
   - Implement alert triggers
   - Add logging for safety violations

### Low Priority
7. **Streamlit Dashboard**
   - Create web interface for monitoring
   - Real-time statistics display
   - Historical data visualization



## Usage

### Run Data Exploration
```bash
cd Scripts
python main.py
```



### Train Custom Model (TODO)
```bash
# After creating training script
python Scripts/train.py --data map.yaml --epochs 100 --batch 16
```

## Project Status
- ✅ Dataset downloaded and organized
- ✅ Basic data exploration implemented
- ⏳ Model training pipeline (pending)
- ⏳ Validation and metrics (pending)
- ⏳ Safety alert system (pending)
- ⏳ Web dashboard (pending)

## License
Dataset: CC BY 4.0

## Acknowledgments
- Dataset from Roboflow Universe - Construction Site Safety
- YOLOv8 by Ultralytics
