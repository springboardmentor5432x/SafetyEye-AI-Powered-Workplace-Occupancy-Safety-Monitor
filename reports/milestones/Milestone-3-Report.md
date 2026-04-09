# Milestone 3 Report 

## Title

SafetyEye: Real-Time Detection and Alert System


## 1. Objective

Milestone 3 was the point where SafetyEye stopped being only a trained detector and started behaving like a monitoring system. The main goal was to run inference on live video, interpret the detections in real time, and create a usable alert loop for missing PPE.

## 2. Real-Time Video Pipeline

The real-time monitoring pipeline was implemented using OpenCV and the trained YOLOv8 model. The main implementation is available in:

- `scripts/main_detection.py`

This pipeline:

- opens a webcam or video file
- captures frames continuously
- runs YOLOv8 inference on incoming frames
- stores detections from the most recent processed frame
- redraws annotations on every frame for smooth display

In the current workspace, the real-time scripts load the packaged trained weights located at:

- `models/best.pt`

This allowed the real-time module to reuse the PPE detector carried forward from the Milestone 2 training phase without depending on a specific intermediate training folder.

## 3. Detected Classes and Visualization

The system draws different colors for different object types to improve readability:

- Person: yellow
- Hardhat: green
- Safety Vest: teal-green
- Mask: cyan
- NO-Hardhat: red
- NO-Safety Vest: dark red
- Machinery and Vehicle: neutral shades

For each detected object, the application displays:

- bounding box
- class label
- confidence score

The video window also shows:

- FPS
- people count
- a warning banner when active violations are present

## 4. Violation Detection Logic

The violation logic was implemented in:

- `scripts/violation_rules.py`

The system does not rely only on direct `NO-Hardhat` or `NO-Safety Vest` predictions. It also applies rule-based reasoning:

1. Separate persons, hardhats, and vests from the detections
2. For each detected person, check whether a hardhat overlaps the person box
3. For helmets, use both IoU and a top-half heuristic to handle imperfect box placement
4. For vests, check overlap using IoU
5. If PPE is not found for a person, create a violation message

This rule engine improves practical reliability because it reasons about whether a detected PPE item belongs to a specific person rather than only checking whether the item exists somewhere in the frame.

## 5. Alert System

The alerting component was implemented in:

- `scripts/alert_system.py`

The alert system performs three functions:

- prints console warnings
- appends entries to `violations.log`
- saves screenshots of the violating frame into `violation_screenshots/`

This creates a useful record of safety incidents that can be reviewed later.

To reduce repeated alerts, the real-time system uses a cooldown mechanism. The same violation is not triggered continuously on every frame. Instead, the system waits before saving another alert of the same type, which reduces spam and makes the output easier to manage.

## 6. System Flow

The Milestone 3 real-time flow works as follows:

1. Load the trained YOLOv8 model
2. Open webcam or video input
3. Read each frame
4. Run inference every alternate frame for speed optimization
5. Parse detections and store labels, boxes, and confidences
6. Apply safety violation rules
7. Draw detection boxes and statistics
8. Display a warning banner for active violations
9. Trigger alert logging and screenshot saving
10. Continue until the user exits the application

This pipeline made the system capable of functioning as a practical live safety monitor instead of only an offline detector.

## 7. Outputs Produced

Milestone 3 produced visible and persistent outputs:

- real-time annotated video feed
- violation banners in the live window
- console alerts
- text log file: `violations.log`
- screenshot evidence in `violation_screenshots/`

These outputs demonstrate that the model could be deployed in a working monitoring loop.

## 8. Practical Enhancements

Several practical improvements were added in this milestone:

- processing every second frame to improve performance
- showing a short-lived warning banner to avoid blinking
- tracking recent alerts with cooldown timers
- summarizing total violations at the end of the run

These improvements made the real-time experience more stable and more suitable for demonstration.

## 9. Challenges Faced

The major challenges in Milestone 3 included:

- maintaining acceptable FPS during real-time inference
- reducing false or repeated alerts
- matching PPE detections to the correct person
- keeping the warning display visible and readable
- handling live or unreliable video sources

These were addressed by combining model predictions with rule-based logic and by adding cooldown and persistence mechanisms in the UI.

## 10. Conclusion

Milestone 3 turned the trained model into something operational. By the end of this phase, SafetyEye could process live video, mark detections on screen, identify likely PPE violations, and save alert evidence. That real-time loop became the backbone for the later dashboard and reporting work.
