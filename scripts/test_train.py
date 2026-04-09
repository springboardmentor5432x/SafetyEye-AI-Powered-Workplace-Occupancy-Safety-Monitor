from ultralytics import YOLO

# Load a pre-trained YOLOv8 nano model
model = YOLO('yolov8n.pt')

# Train the model for exactly 1 epoch to test the data.yaml configuration
results = model.train(data='dataset/data.yaml', epochs=1, imgsz=640)
# or we can use yolo task=detect mode=train model=yolov8n.pt data=dataset/data.yaml epochs=1 imgsz=640