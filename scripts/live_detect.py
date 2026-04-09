import cv2
import time
import os
from ultralytics import YOLO

# Configuration
MODE = "webcam" # Options: "webcam", "video", or "image"
#FILE_PATH = '/Users/utkarstdawar/Desktop/SafetyEye/demo/indianworkers.mp4'
FILE_PATH = '/Users/utkarstdawar/Desktop/SafetyEye/demo/construction-safety.jpg'

print(f"Starting SafetyEye in {MODE.upper()} mode...")
model = YOLO('/Users/utkarstdawar/Desktop/SafetyEye/models/best.pt')

cooldown_seconds = 5
last_alert_time = 0

def process_frame(frame, alert_timer):
    """Processes a single frame and returns the annotated frame and updated timer."""
    results = model.predict(frame, conf=0.5, stream=True, verbose=False, device='mps')
    annotated_frame = frame 
    
    for r in results:
        annotated_frame = r.plot() 
        missing_gear = [] 
        
        for box in r.boxes:
            class_id = int(box.cls[0])
            class_name = model.names[class_id]
            
            # Track missing safety gear
            if class_name in ["NO-Hardhat", "NO-Mask", "NO-Safety Vest"]:
                clean_name = class_name.replace("NO-", "")
                missing_gear.append(clean_name)
                
    if len(missing_gear) > 0:
        warning_text = f"WARNING: Missing {', '.join(missing_gear)}"
        cv2.putText(annotated_frame, warning_text, (40, 80), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)
        
        # Audio alert with cooldown
        current_time = time.time()
        if current_time - alert_timer > cooldown_seconds:
            print(f"[URGENT] {warning_text}")
            
            # Play audio only in webcam/video mode
            '''if MODE != "image": 
                os.system(f"say 'Safety violation! Missing {missing_gear[0]}' &")
            alert_timer = current_time'''
    else:
        cv2.putText(annotated_frame, "STATUS: FULLY COMPLIANT & SAFE", (40, 80), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 3)

    return annotated_frame, alert_timer

# Execute based on selected mode
if MODE == "image":
    frame = cv2.imread(FILE_PATH)
    if frame is None:
        print("Error: Could not load the image.")
    else:
        final_frame, _ = process_frame(frame, last_alert_time)
        cv2.imshow("SafetyEye - Image Mode", final_frame)
        
        output_path = '/Users/utkarstdawar/Desktop/SafetyEye/output_result.jpg'
        cv2.imwrite(output_path, final_frame)
        print(f"Saved annotated image to: {output_path}")
        
        cv2.waitKey(0) # Wait for key press to close

else:
    if MODE == "webcam":
        cap = cv2.VideoCapture(0)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    else:
        cap = cv2.VideoCapture(FILE_PATH)

    while True:
        success, frame = cap.read()
        if not success:
            print("End of stream.")
            break
            
        final_frame, last_alert_time = process_frame(frame, last_alert_time)
        cv2.imshow(f"SafetyEye - {MODE.upper()}", final_frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()

cv2.destroyAllWindows()