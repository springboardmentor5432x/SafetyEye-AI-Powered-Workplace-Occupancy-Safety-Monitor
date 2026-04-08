from ultralytics import YOLO

model = YOLO('../Models/yolov8n.pt')

model.predict( source =0, show =True,conf=0.4, vid_stride=1)