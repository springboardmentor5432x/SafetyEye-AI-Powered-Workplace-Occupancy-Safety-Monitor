# Tasks: Safety Dashboard

## Task List

- [x] 1. Project scaffolding and configuration
  - [x] 1.1 Create `Scripts/config.py` — load and validate all `.env` variables, exit with descriptive error on missing variable
  - [x] 1.2 Create `.env.example` with all required variables and inline comments
  - [x] 1.3 Add new dependencies to `requriements.txt`: `plyer`, `hypothesis`, `pytest`

- [x] 2. Detector component
  - [x] 2.1 Create `Scripts/detector.py` — refactor `capture.py` into a `Detector` class with `start()`, `stop()`, `get_latest_frame()`, `drain_events()` and a background capture thread
  - [x] 2.2 Define `ViolationEvent` dataclass (`violation_type`, `confidence`, `timestamp`, `frame_snapshot`)
  - [x] 2.3 Implement PPE violation detection (NO-Hardhat, NO-Mask, NO-Safety Vest) producing `ViolationEvent` objects
  - [x] 2.4 Implement scenario detection: Person Near Vehicle (centroid distance ≤ 50px)
  - [x] 2.5 Implement scenario detection: Vehicle Over Safety Cone (IoU > 0)
  - [x] 2.6 Implement scenario detection: Vehicles Approaching (centroids converging across consecutive frames)
  - [x] 2.7 Handle webcam unavailability — set `feed_available = False` flag when `cap.read()` fails

- [x] 3. Logger component
  - [x] 3.1 Create `Scripts/logger.py` — `SafetyLogger` class using loguru with `rotation="1 hour"` and filename pattern `safetye_{time:YYYY-MM-DD_HH}.log`
  - [x] 3.2 Implement `log_violation(event)` — writes violation type, confidence, and timestamp within the log entry
  - [x] 3.3 Implement `get_recent_excerpt(n_lines)` — returns last N lines from current log file for email inclusion
  - [x] 3.4 Implement retry-once on write failure; write to `sys.stderr` if retry also fails

- [x] 4. Alerter component
  - [x] 4.1 Create `Scripts/alerter.py` — `AlertState` dataclass and `Alerter` class
  - [x] 4.2 Implement `add_violation(event)` — adds alert to active list
  - [x] 4.3 Implement `tick(escalation_seconds=5)` — escalates alerts that have been active ≥ 5 seconds without acknowledgement
  - [x] 4.4 Implement `acknowledge(violation_type)` — removes matching alert from active list
  - [x] 4.5 Implement `active_alerts()` — returns list of non-acknowledged `AlertState` objects

- [x] 5. Mailer component
  - [x] 5.1 Create `Scripts/mailer.py` — `Mailer` class reading SMTP config from `AppConfig`
  - [x] 5.2 Implement `send_violation_report(event)` — composes email with violation type, timestamp, log excerpt, and PNG screenshot attachment
  - [x] 5.3 Implement attachment filename format: `violation_YYYY-MM-DD_HH-MM-SS.png`
  - [x] 5.4 Implement retry logic: up to 3 retries with 10-second intervals in a background thread
  - [x] 5.5 On retry exhaustion, log failure with violation details to current log file

- [x] 6. Notifier component
  - [x] 6.1 Create `Scripts/notifier.py` — `Notifier` class with `notify(event)` method
  - [x] 6.2 Implement Windows path using `winotify` or `win10toast`
  - [x] 6.3 Implement macOS/Linux path using `plyer`
  - [x] 6.4 Catch notification failures, log warning, and continue without interruption

- [-] 7. Streamlit Dashboard
  - [x] 7.1 Create `Scripts/dashboard.py` — Streamlit entry point
  - [x] 7.2 Initialise all components in `st.session_state` on first run; start Detector background thread
  - [x] 7.3 Render live annotated video feed with timestamp overlay; show "Feed Unavailable" when feed is down
  - [ ] 7.4 On each rerun: drain `ViolationEvent` objects, update Alerter, trigger Mailer and Notifier for new events
  - [ ] 7.5 Render alert banners (warning and escalated) with acknowledge buttons
  - [ ] 7.6 Call `alerter.tick()` on each rerun to drive escalation

- [ ] 8. Tests
  - [ ] 8.1 Create `tests/test_config.py` — unit tests for valid config load and each missing-variable exit case
  - [ ] 8.2 Create `tests/test_alerter.py` — unit tests for add, tick, acknowledge, escalation timing
  - [ ] 8.3 Create `tests/test_detector.py` — unit tests for `draw_hazards` (hazard vs non-hazard classes) and scenario detection functions with known box inputs
  - [ ] 8.4 Create `tests/test_mailer.py` — unit tests for attachment filename format and retry count (mock SMTP)
  - [ ] 8.5 Create `tests/test_logger.py` — unit tests for log entry content and file naming pattern
  - [ ] 8.6 Create `tests/test_properties.py` — Hypothesis property-based tests for all 10 correctness properties (minimum 100 iterations each, tagged with `Feature: safety-dashboard, Property N: ...`)
