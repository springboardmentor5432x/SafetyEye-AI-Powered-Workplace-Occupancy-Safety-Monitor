# Milestone 4 Report

## Title

SafetyEye: Monitoring Dashboard, Analytics, Logging, and Final System Integration


## 1. Objective

Milestone 4 focused on packaging the earlier training and detection work into a single demonstration-ready application. The emphasis here was less about inventing a new model component and more about making the project easier to use, easier to review, and easier to present through a dashboard-driven workflow.

The milestone covered these tasks:

1. Design a browser-based monitoring dashboard
2. Integrate live video monitoring with YOLO detection output
3. Visualize safety violations clearly at person level
4. Add safety-compliance analytics
5. Implement persistent logging and export support
6. Integrate earlier milestone components into one workflow
7. Validate the final system
8. Prepare milestone documentation and demo support files

## 2. Dashboard Design

The Milestone 4 dashboard was implemented with Streamlit.

In the current workspace, the active dashboard entrypoint is:

- `app.py`

The implemented dashboard is a single-page layout rather than a multi-page app. It combines:

- a live monitoring frame
- a right-side status and metrics panel
- two analytics charts
- a recent-log table

The sidebar allows the user to choose the video source, upload a video file when needed, and adjust:

- detection confidence threshold
- log cooldown
- frame refresh delay

## 3. Live Video Feed Integration

The dashboard supports two input modes:

- webcam
- uploaded video file

The application automatically selects the best available trained model path from the repository. In the current workspace, the default path resolves to:

- `models/best.pt`

Each processed frame goes through the following flow:

1. capture a frame from the selected source
2. run YOLOv8 inference
3. parse detections into labels, confidences, and boxes
4. evaluate person-level PPE compliance
5. draw boxes, warnings, and live metrics
6. log violations to CSV and save screenshot evidence

This completes the milestone requirement of connecting the detector to a dashboard-driven monitoring experience.

## 4. Safety Violation Visualization

Milestone 4 uses person-level reasoning rather than simple frame-level checks. The system does not only ask whether a helmet or vest exists somewhere in the scene. Instead, it evaluates each detected person separately.

The logic performs the following steps:

1. detect persons and PPE-related objects
2. separate person, hardhat, vest, and direct negative detections from the parsed results
3. match PPE items to each person using overlap and center-position checks
4. mark a violation when required PPE is missing for that person

Violations are visualized using:

- detected-object bounding boxes
- a top-left info panel showing FPS, people count, and compliance percentage
- a frame-level warning banner when active violations are present
- live counts for people, compliance percentage, and active alerts

This makes the output more interpretable and useful for demonstration than a pure frame-level alarm.

## 5. Safety Compliance Analytics

The current dashboard includes lightweight built-in analytics drawn directly from the CSV log file.

The implemented analytics include:

- total logged violations
- hardhat-related violation count
- vest-related violation count
- violation-type bar chart
- violation timeline grouped by minute
- recent-record table

These analytics are generated from `violations.csv` using Pandas and Plotly inside the root dashboard app.

## 6. Violation Logging System

Persistent logging in the current workspace is handled directly inside `app.py` through helper functions that:

- append new rows to `violations.csv`
- save screenshot evidence into `violation_screenshots/`
- reuse a cooldown timer to reduce duplicate logs

Each new log row written by the root dashboard stores:

- timestamp
- violation type
- confidence
- source
- screenshot path

The dashboard displays recent log records in a table and uses the same CSV file as the source for the charts.

## 7. Full System Integration

Milestone 4 combines the earlier project work into one application:

- Milestone 1 prepared the dataset and environment
- Milestone 2 produced the trained YOLOv8 PPE model
- Milestone 3 added real-time detection and alert logic
- Milestone 4 wrapped the system in a dashboard with persistence and analytics

The final integrated workflow is:

**Video Source -> YOLO Detection -> Person-Level PPE Reasoning -> CSV Logging -> Dashboard Charts**

This stage completes the end-to-end SafetyEye pipeline from live input to stored safety insight.

## 8. System Testing and Performance Evaluation

The current workspace does not include a separate `milestone4/test_system.py` validation script. Practical validation for this stage instead relies on:

- model-path availability through `models/best.pt`
- preserved training metrics under `runs/detect/`
- successful syntax compilation of `app.py` and the `scripts/` modules
- live dashboard execution in a working local Streamlit environment

The repository preserves two training-result checkpoints that are relevant for this milestone:

- Original Milestone 2 submission run (`runs/detect/train4/`): precision 0.87522, recall 0.72093, mAP@0.5 0.80358, mAP@0.5:0.95 0.54729
- Later extended training experiment used in the final-project analysis (`runs/detect/train7/results.csv`): precision 0.91709, recall 0.76071, mAP@0.5 0.84172, mAP@0.5:0.95 0.59459

The first set reflects the original milestone submission result, while the second reflects post-milestone training improvements preserved in the repository. Together they show that the trained detector was strong enough to support the Milestone 4 dashboard demonstration.

## 9. Documentation and Demo Support

To support milestone submission and dashboard demos, the repository now includes:

- `app.py` as the top-level dashboard entrypoint
- `scripts/main_detection.py` for OpenCV-based real-time monitoring
- `scripts/violation_rules.py` for PPE rule evaluation
- `scripts/alert_system.py` for alert logging and screenshot capture
- `demo/` assets for dashboard and detection demonstrations
- updated milestone reports

The current root dashboard can generate charts directly from `violations.csv`, so fresh screenshots can be captured from live runs without a separate sample-data script.

## 10. Challenges Faced

The main challenges in Milestone 4 were:

- integrating a YOLO video pipeline into a dashboard workflow
- keeping the monitoring loop responsive in a web UI
- converting raw detections into person-level safety decisions
- building a logging format that supports both live review and later analytics
- aligning the final documentation with the actual implemented files

These were handled by consolidating the current implementation into a single Streamlit dashboard and a small set of supporting detection scripts.

## 11. Conclusion

Milestone 4 brought the project together in a more presentable form. The result is a browser-based workflow that combines live monitoring, person-level PPE checks, CSV logging, screenshot evidence, and quick analytics in one place. For an academic prototype, this stage marks the shift from separate experiments to a usable end-to-end demo.
