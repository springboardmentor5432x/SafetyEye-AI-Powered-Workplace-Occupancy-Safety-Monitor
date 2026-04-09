import cv2
import os
import random

RAW_DATA_DIR = "/Users/utkarstdawar/Desktop/SafetyEye/datasets/images"

SAFETY_CLASSES = [
    'Hardhat', 'Mask', 'NO-Hardhat', 'NO-Mask', 'NO-Safety Vest', 
    'Person', 'Safety Cone', 'Safety Vest', 'machinery', 'vehicle'
]

def verify_data():
    """Selects a random image and draws its YOLO bounding boxes with real names."""
    images = [f for f in os.listdir(RAW_DATA_DIR) if f.endswith(('.jpg', '.png', '.jpeg'))]
    if not images:
        print(f"No images found in {RAW_DATA_DIR}.")
        return

    chosen_image = random.choice(images)
    image_path = os.path.join(RAW_DATA_DIR, chosen_image)
    label_path = os.path.join(RAW_DATA_DIR, chosen_image.rsplit('.', 1)[0] + '.txt')

    img = cv2.imread(image_path)
    if img is None:
        print("Could not read image. It might be corrupted.")
        return
        
    h, w, _ = img.shape

    if os.path.exists(label_path):
        with open(label_path, 'r') as file:
            for line in file:
                data = line.strip().split()
                if len(data) == 5:
                    class_id = int(data[0])
                    cx, cy, bw, bh = map(float, data[1:])
                    
                    # Convert normalized YOLO format back to pixel coordinates
                    x1 = int((cx - bw / 2) * w)
                    y1 = int((cy - bh / 2) * h)
                    x2 = int((cx + bw / 2) * w)
                    y2 = int((cy + bh / 2) * h)
                    
                    # Get the actual class name
                    class_name = SAFETY_CLASSES[class_id] if class_id < len(SAFETY_CLASSES) else f"Unknown ({class_id})"
                    
                    cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    cv2.putText(img, class_name, (x1, y1 - 5), 
                                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

    print("Opening image... Press ANY KEY on your keyboard to close the window.")
    cv2.imshow(f"Raw Data Check: {chosen_image}", img)
    cv2.waitKey(0) 
    cv2.destroyAllWindows()

if __name__ == "__main__":
    verify_data()