# Requirements Document

## Introduction

The SafetyEye Safety Dashboard is a real-time monitoring interface for construction site safety. It integrates with the existing `capture.py` detection pipeline to display a live annotated video feed, log all detection events, alert operators to PPE and scenario-based violations, escalate unacknowledged alerts, send violation reports via email to supervisors, and deliver OS-level desktop notifications.

---

## Glossary

- **Dashboard**: The Streamlit-based web UI that serves as the primary operator interface.
- **Detector**: The component wrapping `capture.py` that runs YOLOv8 inference and produces annotated frames and detection events.
- **Violation**: A detected safety hazard — either a PPE violation (NO-Hardhat, NO-Mask, NO-Safety Vest) or a scenario-based hazard (person near vehicle, vehicle over safety cone, two vehicles approaching each other).
- **Alert**: An on-screen warning message displayed when a Violation is detected.
- **Escalated Alert**: An emergency-level on-screen warning triggered when an Alert has not been acknowledged within 5 seconds.
- **Logger**: The component responsible for writing detection events to rotating log files using loguru.
- **Log File**: A file that records detection events for a single hour of activity.
- **Notifier**: The component that sends OS-level desktop notifications.
- **Mailer**: The component that composes and sends violation report emails.
- **Supervisor**: The designated email recipient who receives violation reports.
- **Violation Report**: An email containing the violation log excerpt, a screenshot of the violation frame, and the date and timestamp of the event.
- **Timestamp**: A human-readable date-time string in ISO 8601 format (e.g., `2024-07-15 14:32:05`).
- **Frame**: A single image captured from the webcam at 640×480 resolution.
- **Confidence Threshold**: The minimum detection confidence score of 0.50 required for a detection to be treated as a Violation.

---

## Requirements

### Requirement 1: Live Video Feed Display

**User Story:** As an operator, I want to see the live annotated video feed in the Dashboard, so that I can monitor the site in real time.

#### Acceptance Criteria

1. WHEN the Dashboard starts, THE Detector SHALL begin capturing frames from the webcam at 640×480 resolution.
2. WHILE the Dashboard is running, THE Dashboard SHALL display the most recently annotated Frame at a refresh rate of at least 10 frames per second.
3. WHILE the Dashboard is running, THE Dashboard SHALL overlay a Timestamp on each displayed Frame showing the current date and time.
4. WHEN the Detector identifies a Violation in a Frame, THE Detector SHALL draw a red bounding box and label around the detected object before the Frame is displayed.
5. IF the webcam feed becomes unavailable, THEN THE Dashboard SHALL display a "Feed Unavailable" message in place of the video feed.

---

### Requirement 2: Hourly Rotating Log Files

**User Story:** As a safety manager, I want detection events written to hourly log files, so that I can audit activity for any given hour.

#### Acceptance Criteria

1. WHEN the Dashboard starts, THE Logger SHALL create a new Log File for the current hour.
2. WHEN a Violation is detected, THE Logger SHALL write a log entry containing the Violation type, confidence score, and Timestamp to the current Log File within 1 second of detection.
3. WHEN a new clock hour begins, THE Logger SHALL rotate to a new Log File without dropping any log entries.
4. THE Logger SHALL name each Log File using the pattern `safetye_YYYY-MM-DD_HH.log` where `HH` is the UTC hour the file covers.
5. IF a log write fails, THEN THE Logger SHALL retry the write once and, if the retry also fails, SHALL write an error entry to the system stderr.

---

### Requirement 3: Violation Alert Display

**User Story:** As an operator, I want an on-screen warning when a violation is detected, so that I can take immediate corrective action.

#### Acceptance Criteria

1. WHEN a Violation is detected, THE Dashboard SHALL display a visible warning Alert banner identifying the Violation type within 1 second of detection.
2. WHILE an unacknowledged Alert is active, THE Dashboard SHALL keep the Alert banner visible on every UI refresh cycle.
3. WHEN the operator acknowledges an Alert, THE Dashboard SHALL remove the Alert banner within 1 second of acknowledgement.
4. WHEN an Alert has been active for 5 seconds without acknowledgement, THE Dashboard SHALL replace the warning Alert with an Escalated Alert displaying an emergency-level message.
5. WHILE an Escalated Alert is active, THE Dashboard SHALL display the Escalated Alert banner on every UI refresh cycle until the operator acknowledges it.

---

### Requirement 4: Violation Report Email

**User Story:** As a supervisor, I want to receive an email report when a violation occurs, so that I can review incidents and take follow-up action.

#### Acceptance Criteria

1. WHEN a Violation is detected, THE Mailer SHALL send a Violation Report email to the configured Supervisor email address within 30 seconds of detection.
2. THE Mailer SHALL include in the Violation Report: the Violation type, the Timestamp of the event, a screenshot of the annotated Frame in which the Violation was detected, and the relevant log excerpt from the current Log File.
3. THE Mailer SHALL read the Supervisor email address, SMTP host, SMTP port, and SMTP credentials from environment variables defined in a `.env` file.
4. IF the email send attempt fails, THEN THE Mailer SHALL retry the send up to 3 times with a 10-second interval between attempts.
5. IF all retry attempts fail, THEN THE Mailer SHALL log the failure with the Violation details to the current Log File so the event is not lost.
6. THE Mailer SHALL attach the violation screenshot as a PNG file named `violation_YYYY-MM-DD_HH-MM-SS.png`.

---

### Requirement 5: Desktop Notifications

**User Story:** As an operator, I want OS-level desktop notifications when a violation is detected, so that I am alerted even if the Dashboard window is not in focus.

#### Acceptance Criteria

1. WHEN a Violation is detected, THE Notifier SHALL send an OS-level desktop notification within 2 seconds of detection.
2. THE Notifier SHALL include in the notification: the Violation type and the Timestamp of the event.
3. WHERE the operating system is Windows, THE Notifier SHALL use Windows Toast notifications.
4. WHERE the operating system is macOS or Linux, THE Notifier SHALL use a compatible OS notification mechanism (e.g., `plyer` or `notify-send`).
5. IF the desktop notification system is unavailable, THEN THE Notifier SHALL log a warning to the current Log File and continue Dashboard operation without interruption.

---

### Requirement 6: Scenario-Based Hazard Detection

**User Story:** As a safety manager, I want the Dashboard to detect scenario-based hazards beyond individual PPE violations, so that complex site dangers are also captured.

#### Acceptance Criteria

1. WHEN a Person detection and a vehicle detection overlap or are within a proximity threshold of 50 pixels in the same Frame, THE Detector SHALL raise a Violation of type "Person Near Vehicle".
2. WHEN a vehicle detection bounding box overlaps with a Safety Cone detection bounding box in the same Frame, THE Detector SHALL raise a Violation of type "Vehicle Over Safety Cone".
3. WHEN two vehicle detections are present in the same Frame and their bounding boxes are moving toward each other across consecutive Frames, THE Detector SHALL raise a Violation of type "Vehicles Approaching".
4. THE Detector SHALL apply the Confidence Threshold of 0.50 to all individual object detections used in scenario evaluation.
5. WHEN a scenario-based Violation is raised, THE Dashboard SHALL process it identically to a PPE Violation for alerting, logging, email reporting, and desktop notification purposes.

---

### Requirement 7: Dashboard Configuration

**User Story:** As a developer, I want all configurable parameters stored in a `.env` file, so that the Dashboard can be deployed to different environments without code changes.

#### Acceptance Criteria

1. THE Dashboard SHALL read the following settings from a `.env` file at startup: webcam device index, model path, confidence threshold, SMTP host, SMTP port, SMTP username, SMTP password, Supervisor email address, and log output directory.
2. IF a required environment variable is missing at startup, THEN THE Dashboard SHALL log a descriptive error message identifying the missing variable and exit with a non-zero status code.
3. THE Dashboard SHALL provide a `.env.example` file listing all required environment variables with placeholder values and inline comments describing each variable.
