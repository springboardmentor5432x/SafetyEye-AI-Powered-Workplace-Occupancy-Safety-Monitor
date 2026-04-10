import cv2
import argparse
import math
import sys
import os
from ultralytics import YOLO

# Add current directory to path so it can find violation_rules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from violation_rules import check_ppe_violations

# Based on data.yaml class IDs:
CLASS_NAMES = {
    0: 'Hardhat', 1: 'Mask', 2: 'NO-Hardhat', 3: 'NO-Mask', 4: 'NO-Safety Vest',
    5: 'Person', 6: 'Safety Cone', 7: 'Safety Vest', 8: 'machinery', 9: 'vehicle'
}

def main():
    parser = argparse.ArgumentParser(description="Real-Time Detection & Alert System")
    parser.add_argument('--source', type=str, default='0', help="Path to video file or '0' for webcam")
    parser.add_argument('--model', type=str, default='runs/detect/yolov8s_model/weights/best.pt', help="Path to trained YOLOv8 model")
    parser.add_argument('--output', type=str, default='output_videos/result.mp4', help="Path to save processed video")
    args = parser.parse_args()

    # Load YOLO model
    print(f"[INFO] Loading YOLOv8 model from: {args.model}...")
    try:
        model = YOLO(args.model)
    except FileNotFoundError:
        print(f"[ERROR] Model file '{args.model}' not found.")
        print("Please provide the correct path to your trained model using the --model argument.")
        print(r"Example: python scripts\main_detection.py --source videos\my_video.mp4 --model models\best.pt")
        return

    # Check if source is digit for webcam
    source = int(args.source) if args.source.isdigit() else args.source
    
    print(f"[INFO] Opening video source: {source}")
    cap = cv2.VideoCapture(source)
    
    if not cap.isOpened():
        print(f"[ERROR] Could not open video source '{source}'")
        return

    # Check and create output directory
    output_dir = os.path.dirname(args.output)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
        
    # Setup VideoWriter
    fps = cap.get(cv2.CAP_PROP_FPS) if source != 0 else 20.0
    if fps == 0 or math.isnan(fps): fps = 20.0
    out = cv2.VideoWriter(args.output, cv2.VideoWriter_fourcc(*'mp4v'), int(fps), (1020, 600))
    print(f"[INFO] Processed video will be saved to: {args.output}")

    print("[INFO] Starting real-time detection. Press 'q' on your keyboard to quit the window.")

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            print("[INFO] End of video stream or cannot fetch frame.")
            break

        # Resize for performance and consistent viewing window
        frame = cv2.resize(frame, (1020, 600))
        
        # Run YOLO inference
        results = model(frame, stream=True, verbose=False)
        
        person_boxes = []
        no_hardhat_boxes = []
        no_vest_boxes = []
        no_mask_boxes = []
        
        drawn_boxes = []

        for r in results:
            boxes = r.boxes
            for box in boxes:
                x1, y1, x2, y2 = box.xyxy[0]
                x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
                
                conf = math.ceil((box.conf[0] * 100)) / 100
                if conf < 0.4:  # Minimum confidence threshold (40%) to reduce ghost boxes
                    continue
                    
                cls = int(box.cls[0])
                class_name = CLASS_NAMES.get(cls, str(cls))
                
                box_coords = [x1, y1, x2, y2]
                if cls == 5: # Person
                    person_boxes.append(box_coords)
                elif cls == 2: # NO-Hardhat
                    no_hardhat_boxes.append(box_coords)
                elif cls == 4: # NO-Safety Vest
                    no_vest_boxes.append(box_coords)
                elif cls == 3: # NO-Mask
                    no_mask_boxes.append(box_coords)
                
                drawn_boxes.append({
                    'coords': box_coords,
                    'class_name': class_name,
                    'conf': conf,
                    'cls': cls
                })
        
        # 1. Evaluate Rule Engine Violations
        ppe_dict = {'no_hardhats': no_hardhat_boxes, 'no_vests': no_vest_boxes, 'no_masks': no_mask_boxes}
        violations = check_ppe_violations(person_boxes, ppe_dict)
        
        alarm_triggered = False
        
        # 2. Draw non-person items first (gear)
        for d in drawn_boxes:
            if d['cls'] != 5: # Not a person
                text = f"{d['class_name']} {d['conf']}"
                # Draw Cyan bounding box for standard gear
                cv2.rectangle(frame, (d['coords'][0], d['coords'][1]), (d['coords'][2], d['coords'][3]), (255, 255, 0), 2)
                cv2.putText(frame, text, (d['coords'][0], d['coords'][1] - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 2)

        # 3. Draw Person boxes (Color-coded based on safety compliance)
        for v in violations:
            px1, py1, px2, py2 = v['person_box']
            if v['missing_hardhat'] or v['missing_vest'] or v['missing_mask']:
                # VIOLATION DETECTED - Red Highlight
                color = (0, 0, 255) # BGR Red
                label = "VIOLATION:"
                if v['missing_hardhat']: label += " No Helm"
                if v['missing_vest']: label += " No Vest"
                if v['missing_mask']: label += " No Mask"
                
                # Console Alarm
                print(f"[ALARM] {label} detected at {px1}, {py1}")
                alarm_triggered = True
            else:
                # COMPLIANT - Green Highlight
                color = (0, 255, 0) # BGR Green
                label = "SAFE"
                
            cv2.rectangle(frame, (px1, py1), (px2, py2), color, 3)
            cv2.putText(frame, label, (px1, py1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
            
        # 4. Trigger Global Visual Alarm Header if any violation was found
        if alarm_triggered:
            height, width = frame.shape[:2]
            cv2.rectangle(frame, (0, height - 35), (width, height), (0, 0, 255), -1)
            cv2.putText(frame, "WARNING: SAFETY VIOLATION DETECTED!", (20, height - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

        # 5. Display the feed
        cv2.imshow("SafetyEye - Live Monitor", frame)
        out.write(frame)
        
        # Standard OpenCV wait key to render window & listen for 'q' to quit
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    out.release()
    cv2.destroyAllWindows()
    print("[INFO] Video stream stopped.")

if __name__ == "__main__":
    main()
