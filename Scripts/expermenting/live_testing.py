import cv2
from ultralytics import YOLO
import threading


frame = None
running = True
# load trained model

def capture_frame():
    global frame, running
    cap = cv2.VideoCapture(0)
    while running:
        success, img = cap.read()
        if success:
            frame = img
    # Move release outside the loop
    cap.release() 


thread = threading.Thread(target=capture_frame , daemon=True)
thread.start()


model = YOLO("Models/secondbest.pt" )

# open webcam

while True:


    if frame is not None:
        frame = cv2.flip(frame , 1)
    # run YOLO inference
        results = model.predict(frame,stream=True , conf=0.5)

        # draw detections
        annotated_frame = next(results).plot()
        # show frame
        cv2.imshow("YOLO Live Detection", annotated_frame)

    # press q to exit
    if cv2.waitKey(1) & 0xFF == ord("q"):
        running = False
        break


cv2.destroyAllWindows()