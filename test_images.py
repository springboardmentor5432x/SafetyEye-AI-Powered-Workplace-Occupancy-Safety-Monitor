import cv2
import os
import random

# Path to training images
IMAGE_DIR = "dataset/images/train"

# Get all image files
image_files = [
    f for f in os.listdir(IMAGE_DIR)
    if f.lower().endswith((".jpg", ".png", ".jpeg"))
]

# Select 5 random images
sample_images = random.sample(image_files, min(5, len(image_files)))

for img_name in sample_images:
    img_path = os.path.join(IMAGE_DIR, img_name)

    # Load image
    img = cv2.imread(img_path)

    if img is None:
        print(f"❌ Failed to load: {img_name}")
        continue

    print(f"✅ Loaded image: {img_name}, shape: {img.shape}")

    # Display image
    cv2.imshow("Image Test", img)
    cv2.waitKey(0)  # Press any key to move to next image

cv2.destroyAllWindows()