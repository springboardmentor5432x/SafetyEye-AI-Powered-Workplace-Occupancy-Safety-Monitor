"""
Detector component for the Safety Dashboard.
Wraps YOLOv8 inference in a background thread, produces annotated frames
and ViolationEvent objects consumed by the Streamlit dashboard.
"""

import math
import threading
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple, Union

import cv2
import numpy as np
from ultralytics import YOLO

# ── Class map ─────────────────────────────────────────────────────────────────
# 0: Hardhat, 1: Mask, 2: NO-Hardhat, 3: NO-Mask, 4: NO-Safety Vest,
# 5: Person, 6: Safety Cone, 7: Safety Vest, 8: machinery, 9: vehicle
HAZARD_CLASSES = {"NO-Hardhat", "NO-Mask", "NO-Safety Vest"}
HAZARD_COLOR = (0, 0, 255)    # BGR red  — violations
SAFE_COLOR   = (0, 255, 0)    # BGR green — compliant / person with vest
PERSON_COLOR = (255, 165, 0)  # BGR orange — person (no vest context)

FRAME_SKIP = 2
DEFAULT_CONFIDENCE = 0.50
DEFAULT_RESOLUTION = (640, 480)


# ── Task 2.2 — ViolationEvent dataclass ───────────────────────────────────────

@dataclass
class ViolationEvent:
    violation_type: str        # e.g. "NO-Hardhat", "Person Near Vehicle"
    confidence: float          # 0.0–1.0 (use 1.0 for scenario violations)
    timestamp: datetime        # UTC datetime
    frame_snapshot: np.ndarray # annotated 640x480 BGR frame


# ── Geometry helpers ──────────────────────────────────────────────────────────

def _centroid(box: Tuple[int, int, int, int]) -> Tuple[float, float]:
    """Return (cx, cy) for a box given as (x1, y1, x2, y2)."""
    x1, y1, x2, y2 = box
    return (x1 + x2) / 2.0, (y1 + y2) / 2.0


def _centroid_distance(a: Tuple[int, int, int, int],
                       b: Tuple[int, int, int, int]) -> float:
    """Euclidean distance between centroids of two boxes."""
    ax, ay = _centroid(a)
    bx, by = _centroid(b)
    return math.hypot(ax - bx, ay - by)


def _iou(a: Tuple[int, int, int, int],
         b: Tuple[int, int, int, int]) -> float:
    """Intersection-over-Union for two boxes (x1,y1,x2,y2)."""
    ix1 = max(a[0], b[0])
    iy1 = max(a[1], b[1])
    ix2 = min(a[2], b[2])
    iy2 = min(a[3], b[3])
    inter_w = max(0, ix2 - ix1)
    inter_h = max(0, iy2 - iy1)
    inter = inter_w * inter_h
    if inter == 0:
        return 0.0
    area_a = max(0, a[2] - a[0]) * max(0, a[3] - a[1])
    area_b = max(0, b[2] - b[0]) * max(0, b[3] - b[1])
    union = area_a + area_b - inter
    return inter / union if union > 0 else 0.0


# ── Task 2.1 — Detector class ─────────────────────────────────────────────────
import json
from pathlib import Path

EVENT_FILE = Path("event.json")

def write_events(events):
    data = []

    for e in events:
        data.append({
            "type": e.violation_type,
            "confidence": e.confidence,
            "timestamp": e.timestamp.isoformat()
        })

    try:
        EVENT_FILE.write_text(json.dumps(data, indent=2))
        print(data)
    except Exception:
            print("JSON write failed:", e)


class Detector:
    """
    Runs YOLOv8 inference in a background daemon thread.
    Thread-safe access via get_latest_frame() and drain_events().
    """

    def __init__(
        self,
        model_path: str,
        webcam_index: Union[int, str] = 0,
        confidence: float = DEFAULT_CONFIDENCE,
        resolution: Tuple[int, int] = DEFAULT_RESOLUTION,
    ) -> None:
        self._model = YOLO(model_path)
        self._webcam_index = webcam_index
        self._confidence = confidence
        self._resolution = resolution

        self._lock = threading.Lock()
        self._stop_event = threading.Event()
        self._thread: Optional[threading.Thread] = None

        self._latest_frame: Optional[np.ndarray] = None
        self._events: List[ViolationEvent] = []

        # Task 2.7 — feed availability flag
        self._feed_available: bool = True

        # Task 2.6 — previous-frame vehicle centroids for approach detection
        self._prev_vehicle_centroids: List[Tuple[float, float]] = []

    # ── Public interface ──────────────────────────────────────────────────────

    @property
    def feed_available(self) -> bool:
        """True while the webcam is delivering frames successfully."""
        with self._lock:
            return self._feed_available

    def start(self) -> None:
        """Start the background capture/inference thread."""
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        """Signal the background thread to stop and wait for it to finish."""
        self._stop_event.set()
        if self._thread is not None:
            self._thread.join(timeout=5)

    def process_frame(self, frame: np.ndarray):
        
        model = self._model
        # resize if needed
        frame = cv2.resize(frame, self._resolution)

        results = self._model.predict(frame, conf=self._confidence, verbose=False)

        new_events = []

        # PPE detection
        frame, ppe_events = self._process_ppe(frame, results, model.names)
        new_events.extend(ppe_events)

        boxes_by_class = self._group_boxes(results, model.names)

        # Scenario detections
        new_events.extend(self._detect_person_near_vehicle(frame, boxes_by_class))
        new_events.extend(self._detect_vehicle_over_cone(frame, boxes_by_class))
        new_events.extend(self._detect_vehicles_approaching(frame, boxes_by_class))

        return frame, new_events

    def get_latest_frame(self) -> Optional[np.ndarray]:
        """Return the most recently annotated frame, or None if not yet available."""
        with self._lock:
            return self._latest_frame.copy() if self._latest_frame is not None else None

    def drain_events(self) -> List[ViolationEvent]:
        """Return and clear all queued ViolationEvents."""
        with self._lock:
            events, self._events = self._events, []
        return events

    # # ── Background thread ─────────────────────────────────────────────────────
    
    # def _run(self) -> None:
    #     model = YOLO(self._model_path)

    #     cap = cv2.VideoCapture(self._webcam_index)
    #     cap.set(cv2.CAP_PROP_FRAME_WIDTH, self._resolution[0])
    #     cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self._resolution[1])
    #     cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

    #     frame_count = 0
    #     last_results = None

    #     while not self._stop_event.is_set():
    #         ret, frame = cap.read()

    #         # Task 2.7 — handle read failure
    #         if not ret:
    #             with self._lock:
    #                 self._feed_available = False
    #             continue

    #         with self._lock:
    #             self._feed_available = True

    #         # Flip horizontally (mirror)
    #         frame = cv2.flip(frame, 1)
    #         frame_count += 1

    #         # Task 2.1 — frame skip: run inference every 2nd frame only
    #         if frame_count % FRAME_SKIP == 0:
    #             last_results = model.predict(
    #                 frame, conf=self._confidence, verbose=False
    #             )

    #         new_events: List[ViolationEvent] = []

    #         if last_results is not None:
    #             # Task 2.3 — PPE violation detection + annotation
    #             frame, ppe_events = self._process_ppe(frame, last_results, model.names)
    #             new_events.extend(ppe_events)

    #             # Collect per-class boxes for scenario detection
    #             boxes_by_class = self._group_boxes(last_results, model.names)

    #             # Task 2.4 — Person Near Vehicle
    #             new_events.extend(
    #                 self._detect_person_near_vehicle(frame, boxes_by_class)
    #             )

    #             # Task 2.5 — Vehicle Over Safety Cone
    #             new_events.extend(
    #                 self._detect_vehicle_over_cone(frame, boxes_by_class)
    #             )

    #             # Task 2.6 — Vehicles Approaching
    #             new_events.extend(
    #                 self._detect_vehicles_approaching(frame, boxes_by_class)
    #             )

    #         with self._lock:
    #             self._latest_frame = frame
    #             for ev in new_events:
    #                 # Attach the current annotated frame as snapshot
    #                 ev.frame_snapshot = frame.copy()
    #                 self._events.append(ev)
                

    #     cap.release()

    # ── Task 2.3 — PPE violation detection ───────────────────────────────────

    # Classes that get a green "safe" bounding box (no event raised)
    SAFE_DRAW_CLASSES = {"Safety Vest", "Hardhat", "Mask"}
    # Person always gets a box; colour depends on whether they wear a vest
    PERSON_CLASS = "Person"

    def _process_ppe(
        self,
        frame: np.ndarray,
        results,
        names: Dict[int, str],
    ) -> Tuple[np.ndarray, List[ViolationEvent]]:
        """Draw bounding boxes for all relevant detections and raise ViolationEvents for PPE violations."""
        events: List[ViolationEvent] = []

        # First pass — collect all detections above threshold
        detections: List[Tuple[str, float, Tuple[int,int,int,int]]] = []
        for box in results[0].boxes:
            cls_id = int(box.cls[0])
            conf = float(box.conf[0])
            if conf < self._confidence:
                continue
            label = names[cls_id]
            coords = tuple(map(int, box.xyxy[0]))
            detections.append((label, conf, coords))

        # Collect vest boxes to check person overlap
        vest_boxes = [coords for (lbl, _, coords) in detections if lbl == "Safety Vest"]

        def _person_has_vest(p_box: Tuple[int,int,int,int]) -> bool:
            """True if any Safety Vest box overlaps this person box."""
            for v_box in vest_boxes:
                if _iou(p_box, v_box) > 0.0:
                    return True
            return False

        for label, conf, (x1, y1, x2, y2) in detections:
            # Choose colour and decide whether to raise an event
            if label in HAZARD_CLASSES:
                color = HAZARD_COLOR
                raise_event = True
            elif label == self.PERSON_CLASS:
                color = SAFE_COLOR if _person_has_vest((x1, y1, x2, y2)) else PERSON_COLOR
                raise_event = False
            elif label in self.SAFE_DRAW_CLASSES:
                color = SAFE_COLOR
                raise_event = False
            else:
                # Skip classes we don't care about drawing (machinery, vehicle, cone handled elsewhere)
                continue

            text = f"{label} {conf:.0%}"
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            (tw, th), _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.55, 1)
            cv2.rectangle(frame, (x1, y1 - th - 8), (x1 + tw + 4, y1), color, -1)
            cv2.putText(
                frame, text, (x1 + 2, y1 - 4),
                cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 1, cv2.LINE_AA,
            )

            if raise_event:
                events.append(
                    ViolationEvent(
                        violation_type=label,
                        confidence=conf,
                        timestamp=datetime.now(timezone.utc),
                        frame_snapshot=frame,
                    )
                )

        return frame, events

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _group_boxes(
        self, results, names: Dict[int, str]
    ) -> Dict[str, List[Tuple[int, int, int, int]]]:
        """Return {class_name: [(x1,y1,x2,y2), ...]} for detections above threshold."""
        grouped: Dict[str, List[Tuple[int, int, int, int]]] = {}
        for box in results[0].boxes:
            cls_id = int(box.cls[0])
            conf = float(box.conf[0])
            if conf < self._confidence:
                continue
            label = names[cls_id]
            coords = tuple(map(int, box.xyxy[0]))  # (x1,y1,x2,y2)
            grouped.setdefault(label, []).append(coords)
        return grouped

    # ── Task 2.4 — Person Near Vehicle ───────────────────────────────────────

    def _detect_person_near_vehicle(
        self,
        frame: np.ndarray,
        boxes_by_class: Dict[str, List[Tuple[int, int, int, int]]],
    ) -> List[ViolationEvent]:
        persons = boxes_by_class.get("Person", [])
        vehicles = boxes_by_class.get("vehicle", [])
        events: List[ViolationEvent] = []

        for p_box in persons:
            for v_box in vehicles:
                if _centroid_distance(p_box, v_box) <= 50.0:
                    events.append(
                        ViolationEvent(
                            violation_type="Person Near Vehicle",
                            confidence=1.0,
                            timestamp=datetime.now(timezone.utc),
                            frame_snapshot=frame,
                        )
                    )
                    # One event per person-vehicle pair is enough
                    break

        return events

    # ── Task 2.5 — Vehicle Over Safety Cone ──────────────────────────────────

    def _detect_vehicle_over_cone(
        self,
        frame: np.ndarray,
        boxes_by_class: Dict[str, List[Tuple[int, int, int, int]]],
    ) -> List[ViolationEvent]:
        vehicles = boxes_by_class.get("vehicle", [])
        cones = boxes_by_class.get("Safety Cone", [])
        events: List[ViolationEvent] = []

        for v_box in vehicles:
            for c_box in cones:
                if _iou(v_box, c_box) > 0:
                    events.append(
                        ViolationEvent(
                            violation_type="Vehicle Over Safety Cone",
                            confidence=1.0,
                            timestamp=datetime.now(timezone.utc),
                            frame_snapshot=frame,
                        )
                    )
                    break

        return events

    # ── Task 2.6 — Vehicles Approaching ──────────────────────────────────────

    def _detect_vehicles_approaching(
        self,
        frame: np.ndarray,
        boxes_by_class: Dict[str, List[Tuple[int, int, int, int]]],
    ) -> List[ViolationEvent]:
        vehicles = boxes_by_class.get("vehicle", [])
        curr_centroids = [_centroid(b) for b in vehicles]
        events: List[ViolationEvent] = []

        prev = self._prev_vehicle_centroids

        # Need at least two vehicles in both current and previous frame
        if len(curr_centroids) >= 2 and len(prev) >= 2:
            # Check every pair of current vehicles against closest previous centroids
            for i in range(len(curr_centroids)):
                for j in range(i + 1, len(curr_centroids)):
                    ca, cb = curr_centroids[i], curr_centroids[j]
                    curr_dist = math.hypot(ca[0] - cb[0], ca[1] - cb[1])

                    # Find the closest previous centroid for each current centroid
                    pa = min(prev, key=lambda p: math.hypot(p[0] - ca[0], p[1] - ca[1]))
                    pb = min(prev, key=lambda p: math.hypot(p[0] - cb[0], p[1] - cb[1]))

                    if pa == pb:
                        continue  # both matched to same previous centroid — skip

                    prev_dist = math.hypot(pa[0] - pb[0], pa[1] - pb[1])

                    if curr_dist < prev_dist:
                        events.append(
                            ViolationEvent(
                                violation_type="Vehicles Approaching",
                                confidence=1.0,
                                timestamp=datetime.now(timezone.utc),
                                frame_snapshot=frame,
                            )
                        )
                        # One event per frame is sufficient
                        self._prev_vehicle_centroids = curr_centroids
                        return events

        self._prev_vehicle_centroids = curr_centroids
        return events
