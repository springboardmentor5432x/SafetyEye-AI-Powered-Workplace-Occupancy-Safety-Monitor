# SafetyEye

SafetyEye is a computer-vision project for workplace safety monitoring. It uses a trained YOLO model to detect people, hardhats, safety vests, masks, machinery, and vehicles, then flags PPE violations in live video, uploaded video, or still images. The repository also includes a Streamlit dashboard for reviewing incidents and violation trends.

## What It Does

- Detects workers and safety gear in images, webcam feeds, and videos
- Flags missing hardhats and safety vests
- Logs violations to a CSV file
- Saves screenshot evidence for detected violations
- Shows analytics in a Streamlit dashboard
- Preserves milestone reports and training artifacts for the project lifecycle

## Key Features

### 1. Live Safety Monitoring

The detection scripts run the YOLO model against a webcam or video stream and draw annotated bounding boxes in real time.

### 2. Rule-Based PPE Checks

The rule engine matches detected PPE items to nearby people using overlap heuristics and raises violations when required gear is missing.

### 3. Incident Logging

Violations are recorded in `violations.csv`, and evidence frames are saved under `violation_screenshots/`.

### 4. Dashboard Analytics

The Streamlit app surfaces:

- current people count
- compliance percentage
- recent alerts
- violation history
- charts built from the logged data

## Tech Stack

- Python
- Ultralytics YOLO
- PyTorch
- OpenCV
- Streamlit
- Streamlit WebRTC
- Pandas
- Plotly

## Repository Layout

```text
SafetyEye/
├── app.py                         # Streamlit dashboard
├── requirements.txt               # Python dependencies
├── README.md
├── dataset/
│   ├── data.yaml                  # YOLO dataset config
│   ├── images/
│   └── labels/
├── models/
│   └── best.pt                    # Trained model used by the app
├── scripts/
│   ├── alert_system.py            # Logging and screenshot capture
│   ├── live_detect.py             # Quick image/video/webcam inference
│   ├── main_detection.py          # Main OpenCV-based live monitor
│   ├── milestone_3.py             # Alternate milestone detection pipeline
│   ├── split_data.py              # Train/val/test split helper
│   ├── test_train.py              # 1-epoch training smoke test
│   ├── verify_data.py             # Visual annotation sanity check
│   └── violation_rules.py         # PPE rule engine
├── reports/
│   ├── final_report.md
│   └── milestones/
├── runs/
│   └── detect/                    # Training and prediction artifacts
├── temp_streams/                  # Temporary uploaded videos for dashboard use
└── violation_screenshots/         # Saved evidence frames
```

## Detected Classes

The dataset configuration currently defines these classes:

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

## Setup

### 1. Create and activate a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Confirm model availability

The dashboard and main detection scripts expect the trained weights at:

```text
models/best.pt
```

## Run The Project

### Streamlit dashboard

```bash
streamlit run app.py
```

This opens the main dashboard for:

- webcam monitoring
- uploaded video review
- incident log browsing
- compliance analytics

### OpenCV live monitor

```bash
python3 scripts/main_detection.py
```

This launches the real-time detection window and prints a short session summary after exit.

### Quick image or video detection

```bash
python3 scripts/live_detect.py
```

Before running, set `MODE` and `FILE_PATH` inside [scripts/live_detect.py](scripts/live_detect.py).

### Dataset verification

```bash
python3 scripts/verify_data.py
```

This opens a random annotated image so you can visually confirm label quality.

### Training smoke test

```bash
python3 scripts/test_train.py
```

This runs a 1-epoch YOLO training check using [dataset/data.yaml](dataset/data.yaml).

## Generated Outputs

Running the system creates or updates:

- `violations.csv` for dashboard log records
- `violation_screenshots/` for saved evidence images
- `temp_streams/` for uploaded video processing
- `runs/detect/` for training and prediction artifacts

## Important Notes

- Several helper scripts use hardcoded absolute paths. If this project is moved to another directory or machine, update those paths in:
  - [dataset/data.yaml](dataset/data.yaml)
  - [scripts/live_detect.py](scripts/live_detect.py)
  - [scripts/main_detection.py](scripts/main_detection.py)
  - [scripts/milestone_3.py](scripts/milestone_3.py)
  - [scripts/split_data.py](scripts/split_data.py)
  - [scripts/verify_data.py](scripts/verify_data.py)
- The Streamlit app uses relative paths and is the easiest entry point if you want a unified interface.
- The repository already includes project reports in [reports/final_report.md](reports/final_report.md) and the milestone documents under [reports/milestones](reports/milestones).

## Future Improvements

- Replace hardcoded filesystem paths with config or environment variables
- Add automated tests for the rule engine and logging flow
- Extend violation rules beyond hardhat and vest compliance
- Package the app for easier deployment
