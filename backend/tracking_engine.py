import cv2
import math
import sys
import os
import time
import threading
from ultralytics import YOLO

# Add main project root to path so it can find scripts
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(PROJECT_ROOT)

from scripts.violation_rules import check_ppe_violations
from database import init_db, log_violation

init_db()

CLASS_NAMES = {
    0: 'Hardhat', 1: 'Mask', 2: 'NO-Hardhat', 3: 'NO-Mask', 4: 'NO-Safety Vest',
    5: 'Person', 6: 'Safety Cone', 7: 'Safety Vest', 8: 'machinery', 9: 'vehicle'
}

# ───── Global Configuration ─────
CONFIDENCE_THRESHOLD = 0.40
AUDIO_ALARMS_ENABLED = True
GRACE_PERIOD = 5
last_alarm_time = 0

# ───── Shared Model (Option B — one model, all cameras share it) ─────
_model = None
_model_lock = threading.Lock()

def load_model():
    global _model
    if _model is None:
        model_path = os.path.join(PROJECT_ROOT, 'runs', 'detect', 'yolov8s_model', 'weights', 'best.pt')
        if not os.path.exists(model_path):
            model_path = os.path.join(PROJECT_ROOT, 'yolov8s.pt')
        _model = YOLO(model_path)
    return _model


# ───── Simple Centroid Tracker ─────
class SimpleTracker:
    """Lightweight tracker using centroid distance matching. One per camera."""
    def __init__(self, max_distance=120, max_disappeared=20):
        self.next_id = 1
        self.tracks = {}       # id -> (cx, cy)
        self.disappeared = {}  # id -> frames_missing_count
        self.max_distance = max_distance
        self.max_disappeared = max_disappeared

    def reset(self):
        self.tracks.clear()
        self.disappeared.clear()
        self.next_id = 1

    def update(self, boxes):
        """
        boxes: list of [x1, y1, x2, y2]
        Returns: list of track_ids, one per input box
        """
        centroids = [((b[0]+b[2])/2, (b[1]+b[3])/2) for b in boxes]

        if len(centroids) == 0:
            # Mark all tracks as disappeared
            for tid in list(self.disappeared.keys()):
                self.disappeared[tid] += 1
                if self.disappeared[tid] > self.max_disappeared:
                    del self.tracks[tid]
                    del self.disappeared[tid]
            return []

        if len(self.tracks) == 0:
            ids = []
            for c in centroids:
                self.tracks[self.next_id] = c
                self.disappeared[self.next_id] = 0
                ids.append(self.next_id)
                self.next_id += 1
            return ids

        track_ids = list(self.tracks.keys())
        track_cents = list(self.tracks.values())

        # Build distance pairs
        pairs = []
        for i, c in enumerate(centroids):
            for j, tc in enumerate(track_cents):
                d = math.sqrt((c[0]-tc[0])**2 + (c[1]-tc[1])**2)
                pairs.append((d, i, j))
        pairs.sort()

        used_dets = set()
        used_trks = set()
        result = [-1] * len(centroids)

        for d, di, ti in pairs:
            if di in used_dets or ti in used_trks:
                continue
            if d > self.max_distance:
                continue
            result[di] = track_ids[ti]
            self.tracks[track_ids[ti]] = centroids[di]
            self.disappeared[track_ids[ti]] = 0
            used_dets.add(di)
            used_trks.add(ti)

        # New tracks for unmatched detections
        for i in range(len(centroids)):
            if i not in used_dets:
                self.tracks[self.next_id] = centroids[i]
                self.disappeared[self.next_id] = 0
                result[i] = self.next_id
                self.next_id += 1

        # Increment disappeared for unmatched existing tracks
        for j in range(len(track_ids)):
            if j not in used_trks:
                tid = track_ids[j]
                self.disappeared[tid] += 1
                if self.disappeared[tid] > self.max_disappeared:
                    del self.tracks[tid]
                    del self.disappeared[tid]

        return result


# ───── Camera Stream Class ─────
class CameraStream:
    """One independent camera with its own video source, tracker, and violation state."""
    def __init__(self, cam_id):
        self.cam_id = cam_id
        self.cap = None
        self.source = None
        self.is_detecting = False
        self.tracked_states = {}
        self.tracker = SimpleTracker()
        self.lock = threading.Lock()

    def set_source(self, source):
        """Open a video source (webcam index, file path, or URL)."""
        if isinstance(source, str):
            if source.isdigit():
                source = int(source)
            else:
                source = source.strip('\"\' ')
                if source.startswith(('http://', 'https://', 'rtsp://')):
                    pass
                else:
                    source = os.path.normpath(source)
                    if not os.path.isabs(source):
                        source = os.path.join(PROJECT_ROOT, source)

        with self.lock:
            if self.cap is not None:
                try: self.cap.release()
                except: pass

            temp_cap = cv2.VideoCapture(source)
            if temp_cap.isOpened():
                self.cap = temp_cap
                self.source = source
                self.is_detecting = False
                self.tracked_states = {}
                self.tracker.reset()
                return True
            else:
                temp_cap.release()
                return False

    def disconnect(self):
        """Release the camera and reset state."""
        with self.lock:
            if self.cap is not None:
                try: self.cap.release()
                except: pass
                self.cap = None
            self.source = None
            self.is_detecting = False
            self.tracked_states = {}
            self.tracker.reset()

    def get_status(self):
        """Return camera status dict."""
        with self.lock:
            connected = self.cap is not None and self.cap.isOpened()
        return {
            'cam_id': self.cam_id,
            'connected': connected,
            'source': str(self.source) if self.source is not None else None,
            'detecting': self.is_detecting,
        }

    def generate_frames(self):
        """Main frame generator with YOLO inference using shared model."""
        global last_alarm_time

        with self.lock:
            if self.cap is None or not self.cap.isOpened():
                return

        model = load_model()

        frame_count = 0
        skip_interval = 3
        last_annotated_frame = None
        encode_params = [cv2.IMWRITE_JPEG_QUALITY, 65]

        while True:
            with self.lock:
                if self.cap is None or not self.cap.isOpened():
                    break
                ret, frame = self.cap.read()

            if not ret:
                with self.lock:
                    if self.cap is None:
                        break
                    if isinstance(self.source, str) and self.source != '0':
                        self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                        continue
                    else:
                        break

            frame = cv2.resize(frame, (800, 480))

            # Camera label overlay
            cv2.putText(frame, self.cam_id.upper(), (frame.shape[1] - 80, 25),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (100, 200, 255), 2)

            if not self.is_detecting:
                cv2.putText(frame, "DETECTION: PAUSED", (10, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 165, 255), 2)
                ret, buffer = cv2.imencode('.jpg', frame, encode_params)
                frame_bytes = buffer.tobytes()
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
                continue

            frame_count += 1

            if frame_count % skip_interval != 0 and last_annotated_frame is not None:
                ret, buffer = cv2.imencode('.jpg', last_annotated_frame, encode_params)
                frame_bytes = buffer.tobytes()
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
                continue

            # ── YOLO Inference (shared model, lock prevents simultaneous use) ──
            try:
                with _model_lock:
                    results = model.predict(frame, verbose=False, imgsz=480,
                                            conf=CONFIDENCE_THRESHOLD)
            except Exception as e:
                print(f"[WARN] YOLO error on {self.cam_id}: {e}")
                ret, buffer = cv2.imencode('.jpg', frame, encode_params)
                frame_bytes = buffer.tobytes()
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
                continue

            # ── Parse Detections ──
            person_boxes = []
            no_hardhat_boxes = []
            no_vest_boxes = []
            no_mask_boxes = []
            drawn_boxes = []

            if results and results[0].boxes is not None:
                for box in results[0].boxes:
                    cls = int(box.cls[0])
                    conf = float(box.conf[0])
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    class_name = CLASS_NAMES.get(cls, f'cls_{cls}')
                    box_coords = [x1, y1, x2, y2]

                    if cls == 5:
                        person_boxes.append(box_coords)
                    elif cls == 2: no_hardhat_boxes.append(box_coords)
                    elif cls == 4: no_vest_boxes.append(box_coords)
                    elif cls == 3: no_mask_boxes.append(box_coords)

                    drawn_boxes.append({
                        'coords': box_coords, 'class_name': class_name,
                        'conf': conf, 'cls': cls
                    })

            # ── Tracking (our simple tracker assigns IDs) ──
            person_track_ids = self.tracker.update(person_boxes)

            # ── PPE Violation Check ──
            ppe_dict = {'no_hardhats': no_hardhat_boxes, 'no_vests': no_vest_boxes, 'no_masks': no_mask_boxes}
            violations = check_ppe_violations(person_boxes, ppe_dict)

            # Draw PPE items
            for d in drawn_boxes:
                if d['cls'] != 5:
                    cv2.rectangle(frame, (d['coords'][0], d['coords'][1]),
                                  (d['coords'][2], d['coords'][3]), (255, 255, 0), 2)
                    cv2.putText(frame, d['class_name'], (d['coords'][0], d['coords'][1] - 5),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 0), 1)

            logs_to_create = []
            alarm_triggered = False

            for i, v in enumerate(violations):
                px1, py1, px2, py2 = v['person_box']
                track_id = person_track_ids[i] if i < len(person_track_ids) else -1

                if track_id != -1:
                    if track_id not in self.tracked_states:
                        self.tracked_states[track_id] = {
                            'logged_hardhat': False, 'logged_vest': False, 'logged_mask': False,
                            'pending_hardhat': None, 'pending_vest': None, 'pending_mask': None,
                        }

                    state = self.tracked_states[track_id]
                    now = time.time()

                    violation_checks = [
                        ('missing_hardhat', 'pending_hardhat', 'logged_hardhat', 'Missing Hardhat', 'hardhat'),
                        ('missing_vest',    'pending_vest',    'logged_vest',    'Missing Safety Vest', 'vest'),
                        ('missing_mask',    'pending_mask',    'logged_mask',    'Missing Mask',   'mask'),
                    ]

                    for viol_key, pend_key, log_key, log_type, suffix in violation_checks:
                        if v[viol_key]:
                            if not state[log_key]:
                                if state[pend_key] is None:
                                    state[pend_key] = now
                                elif now - state[pend_key] >= GRACE_PERIOD:
                                    logs_to_create.append({'track_id': track_id, 'type': log_type, 'suffix': suffix})
                                    state[log_key] = True
                                    state[pend_key] = None
                        else:
                            if not state[log_key]:
                                state[pend_key] = None

                # ── Visual Labels ──
                has_active = v['missing_hardhat'] or v['missing_vest'] or v['missing_mask']
                is_confirmed = False
                is_pending = False
                pending_elapsed = 0

                if track_id != -1 and track_id in self.tracked_states:
                    st = self.tracked_states[track_id]
                    if st.get('logged_hardhat') or st.get('logged_vest') or st.get('logged_mask'):
                        is_confirmed = True
                    for pk in ['pending_hardhat', 'pending_vest', 'pending_mask']:
                        if st.get(pk) is not None:
                            is_pending = True
                            pending_elapsed = max(pending_elapsed, time.time() - st[pk])

                if is_confirmed and has_active:
                    color = (0, 0, 255)
                    label = f"ID:{track_id} VIOLATION!"
                    alarm_triggered = True
                elif is_pending:
                    remaining = max(0, GRACE_PERIOD - pending_elapsed)
                    color = (0, 165, 255)
                    label = f"ID:{track_id} CONFIRMING {remaining:.0f}s"
                    alarm_triggered = True
                elif has_active:
                    color = (0, 165, 255)
                    label = f"ID:{track_id} CHECKING..."
                    alarm_triggered = True
                else:
                    color = (0, 255, 0)
                    label = f"ID:{track_id} SAFE"

                cv2.rectangle(frame, (px1, py1), (px2, py2), color, 3)
                cv2.putText(frame, label, (px1, py1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

            if alarm_triggered:
                last_alarm_time = time.time()
                h, w = frame.shape[:2]
                cv2.rectangle(frame, (0, h - 30), (w, h), (0, 0, 255), -1)
                cv2.putText(frame, "WARNING: SAFETY VIOLATION DETECTED", (10, h - 8),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

            # Save snapshots and log
            for log_data in logs_to_create:
                timestamp = time.strftime("%Y%m%d-%H%M%S")
                filename = f"snapshot_{self.cam_id}_{log_data['track_id']}_{log_data['suffix']}_{timestamp}.jpg"
                filepath = os.path.join(PROJECT_ROOT, "backend", "snapshots", filename)
                cv2.imwrite(filepath, frame)
                log_violation(log_data['track_id'], log_data['type'], filename)

            last_annotated_frame = frame.copy()

            ret, buffer = cv2.imencode('.jpg', frame, encode_params)
            frame_bytes = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')


# ───── Camera Manager ─────
cameras = {}  # cam_id -> CameraStream

def get_camera(cam_id):
    """Get or create a camera stream by ID."""
    if cam_id not in cameras:
        cameras[cam_id] = CameraStream(cam_id)
    return cameras[cam_id]

def get_all_camera_statuses():
    """Return status of all 4 camera slots."""
    statuses = []
    for cid in ['cam1', 'cam2', 'cam3', 'cam4']:
        if cid in cameras:
            statuses.append(cameras[cid].get_status())
        else:
            statuses.append({'cam_id': cid, 'connected': False, 'source': None, 'detecting': False})
    return statuses


# ───── Legacy API (backward compatible) ─────
def set_video_source(source):
    """Legacy: sets source on cam1."""
    cam = get_camera('cam1')
    return cam.set_source(source)

def set_detection_state(state):
    """Legacy: toggles detection on cam1."""
    cam = get_camera('cam1')
    cam.is_detecting = state
    return state

def generate_frames():
    """Legacy: generates frames from cam1."""
    cam = get_camera('cam1')
    return cam.generate_frames()
