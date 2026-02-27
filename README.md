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
│   ├── preprocessing.py    (Data cleaning and validation)
│   ├── visulalise.py       (Class distribution visualization)
│   └── yolo.py             (Real-time detection script)
├── Output/
│   ├── working/            (Output directory for results)
│   └── intermediate_data/  (Processed data storage)
│       └── annotated.parquet (Cleaned dataset)
├── noteBook/               (Jupyter notebooks for experiments)
├── map.yaml                (Dataset configuration file)
└── requriements.txt        (Python dependencies)
```

**Important**: Place your downloaded `train`, `valid`, and `test` folders inside `Datasets/css-data/` directory.

## Current Work Done

### 1. Data Preprocessing Pipeline (`Scripts/preprocessing.py`)

**Purpose**: Clean and prepare the dataset for training by analyzing annotations and filtering valid data.

**What it does**:
- **Dataset Loading**: Loads all image filenames and label files from train/valid/test splits
- **Annotation Parsing**: Reads YOLO format annotation files (.txt) containing bounding box coordinates
- **Data Validation**: 
  - Identifies empty annotation files (images without objects)
  - Handles single vs multiple object annotations
  - Marks each image as annotated (1) or invalid (-1)
- **Class Counting**: Extracts object class IDs from each annotation to understand class distribution
- **Data Cleaning**: Filters out invalid/unannotated images to create a clean dataset
- **Output**: Saves processed data to `Output/intermediate_data/annotated.parquet` for further analysis

**Why we did this**:
- Ensures training data quality by removing corrupted or empty annotations
- Creates a structured DataFrame for easy data manipulation
- Enables statistical analysis of class distribution across splits
- Prevents training errors from invalid annotation files

**Key Statistics Generated**:
- Total images per split (train: 2605, valid: varies, test: 82)
- Number of valid vs invalid annotations
- Object class frequency per image

### 2. Data Visualization (`Scripts/visulalise.py`)

**Purpose**: Analyze and visualize class distribution across train/valid/test splits to identify data imbalances.

**What it does**:
- **Load Processed Data**: Reads the cleaned dataset from preprocessing step
- **Count Frequency Calculation**: 
  - Converts string representations of counts back to arrays
  - Creates frequency dictionaries for each image (how many of each class)
  - Aggregates counts across entire train/valid/test sets
- **Normalization**: Calculates relative frequencies (percentages) for fair comparison between splits
- **Visualization**: Generates bar chart comparing class distribution across splits
- **Output**: Displays distribution statistics and plots for analysis

**Why we did this**:
- **Identify Class Imbalance**: Some classes (e.g., Person, Safety Vest) may be overrepresented while others (e.g., Mask, Safety Cone) are rare
- **Validate Split Quality**: Ensures train/valid/test splits have similar class distributions
- **Guide Training Strategy**: Helps decide if class weights or data augmentation are needed
- **Detect Data Issues**: Reveals if certain classes are missing from validation/test sets

**Insights from Visualization**:
- Shows which safety equipment is most/least common in the dataset
- Helps understand real-world distribution of PPE violations
- Guides model evaluation strategy (focus on rare but critical classes)

### 3. Real-time Detection (`Scripts/yolo.py`)

**Purpose**: Test YOLOv8 model on live webcam feed for real-time safety monitoring.

**What it does**:
- YOLOv8 model integration with pretrained weights
- Live webcam detection (source=0)
- Confidence threshold: 0.4
- Real-time visualization enabled

**Why we did this**:
- Validates that the model can run in real-time
- Tests inference speed for deployment feasibility
- Provides immediate visual feedback for model performance

### 4. Dataset Configuration (`map.yaml`)

**Purpose**: Define dataset paths and class mappings for YOLOv8 training.

**What it contains**:
- **Dataset Paths**: Points to train/valid/test image directories
- **Class Definitions**: Maps class IDs (0-9) to class names
- **Metadata**: Dataset information, source, and license

**Why we did this**:
- Required by YOLOv8 for training and validation
- Centralizes dataset configuration in one file
- Makes it easy to switch between datasets or update paths
- Documents class mapping for reference

**Class Mapping**:
```
0: Hardhat          - Worker wearing hardhat (compliant)
1: Mask             - Worker wearing mask (compliant)
2: NO-Hardhat       - Worker without hardhat (violation)
3: NO-Mask          - Worker without mask (violation)
4: NO-Safety Vest   - Worker without safety vest (violation)
5: Person           - General person detection
6: Safety Cone      - Traffic/safety cone
7: Safety Vest      - Worker wearing safety vest (compliant)
8: machinery        - Construction machinery/equipment
9: vehicle          - Construction vehicles
```

### 5. Project Structure
- Organized folder structure for datasets, models, scripts, and outputs
- YOLO format label files (class_id x_center y_center width height)
- Pretrained YOLOv8 nano model ready for inference
- Intermediate data storage (`Output/intermediate_data/`) for pipeline efficiency
- Complete dataset configuration (`map.yaml`) ready for training

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
   pip install -r requriements.txt
   ```

### Required Packages
The `requriements.txt` includes:
- `ultralytics` - YOLOv8 framework
- `opencv-python` - Computer vision operations
- `numpy` - Numerical computations
- `pandas` - Data manipulation and analysis
- `matplotlib` - Data visualization and plotting
- `tqdm` - Progress bars for data processing
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

6. **Verify dataset configuration**
   - The `map.yaml` file is already configured with correct paths
   - Verify paths match your dataset location
   - No changes needed if following the recommended structure

## Things to Change/Improve

### High Priority
1. **Model Training Script** ⚠️ NEXT STEP
   - Create `Scripts/train.py` to fine-tune YOLOv8 on construction safety dataset
   - Use the completed `map.yaml` configuration
   - Add hyperparameter configuration (epochs, batch size, image size)
   - Implement training callbacks and logging
   - Save best model weights to `Models/` directory
   
   Example training command:
   ```python
   from ultralytics import YOLO
   
   model = YOLO('Models/yolov8n.pt')
   results = model.train(
       data='map.yaml',
       epochs=100,
       imgsz=640,
       batch=16,
       name='safety_model'
   )
   ```

2. **Create `Output/intermediate_data/` directory**
   - Required for preprocessing pipeline to save cleaned data
   - Ensure directory exists before running preprocessing.py

### Medium Priority
3. **Validation Script**
   - Create validation/evaluation script for model performance
   - Add metrics: mAP, precision, recall, F1-score
   - Generate confusion matrix
   - Compare performance across different classes (especially PPE violations)

4. **Inference Pipeline Enhancement**
   - Enhance `yolo.py` for video file processing
   - Add batch image processing
   - Implement result saving functionality
   - Add bounding box visualization with class labels

5. **Safety Alert System**
   - Detect PPE violations (NO-Hardhat, NO-Mask, NO-Safety Vest)
   - Implement alert triggers based on violation count/frequency
   - Add logging for safety violations with timestamps
   - Generate violation reports

### Low Priority
6. **Streamlit Dashboard**
   - Create web interface for monitoring
   - Real-time statistics display
   - Historical data visualization
   - Live camera feed integration

7. **Documentation Enhancement**
   - Add code comments and docstrings
   - Create usage examples
   - Add model performance benchmarks after training
   - Document API endpoints (if applicable)



## Usage

### Data Processing Pipeline

1. **Run Data Preprocessing** (Clean and validate dataset)
```bash
cd Scripts
python preprocessing.py
```
This will:
- Load all train/valid/test annotations
- Validate annotation files
- Filter out invalid data
- Save cleaned data to `Output/intermediate_data/annotated.parquet`

2. **Run Data Visualization** (Analyze class distribution)
```bash
cd Scripts
python visulalise.py
```
This will:
- Load processed data
- Calculate class frequencies
- Display distribution statistics
- Show bar chart comparing train/valid/test splits

### Real-time Detection

3. **Run Live Webcam Detection**
```bash
cd Scripts
python yolo.py
```



### Train Custom Model

Once you've completed the preprocessing and have the `map.yaml` configured:

```bash
cd Scripts
python train.py --data ../map.yaml --epochs 100 --batch 16 --imgsz 640
```

Or use the YOLOv8 CLI directly:
```bash
yolo train data=map.yaml model=Models/yolov8n.pt epochs=100 batch=16 imgsz=640
```

Training outputs will be saved to `runs/detect/train/` by default.

## Project Status
- ✅ Dataset downloaded and organized
- ✅ Data preprocessing pipeline implemented
- ✅ Data validation and cleaning completed
- ✅ Class distribution analysis and visualization
- ✅ Dataset configuration file (`map.yaml`) created
- ✅ Real-time detection working
- ⏳ Model training pipeline (ready to implement)
- ⏳ Custom model training (pending)
- ⏳ Validation and metrics (pending)
- ⏳ Safety alert system (pending)
- ⏳ Web dashboard (pending)

## License
Dataset: CC BY 4.0

## Acknowledgments
- Dataset from Roboflow Universe - Construction Site Safety
- YOLOv8 by Ultralytics
