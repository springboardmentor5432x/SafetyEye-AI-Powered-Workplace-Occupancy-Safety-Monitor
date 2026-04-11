from ultralytics import YOLO

model = YOLO("yolov8n.pt")

results = model.train(
    data="dataset.yaml",
    epochs=50,
    imgsz=640,
    batch=16,
    device='cuda',
    project="runs",
    name="safetyeye_v1",
    verbose=True
)

print("Training complete!")
```
4. Commit message:
```
Add training script
