from ultralytics import YOLO

# load trained model
model = YOLO("best.pt")

# run detection
results = model.predict(
    source="test.jpg", 
    save=True,
    show=True
)