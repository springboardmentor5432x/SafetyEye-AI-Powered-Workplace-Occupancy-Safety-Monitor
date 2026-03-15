from ultralytics import YOLO

def main():
    # Load YOLOv8 nano model (best for CPU / beginners)
    model = YOLO("yolov8n.pt")

    # Train the model
    model.train(
        data="data.yaml",   # path to data.yaml
        epochs=50,         
        imgsz=640,
        batch=8,            # reduce to 4 if RAM is low
        device="cpu",       # use CPU
        workers=2
    )

if __name__ == "__main__":
    main()
