import cv2
import os
import random

# Path to training images
image_folder = "dataset/train/images"

# Get all image files
images = [f for f in os.listdir(image_folder) if f.endswith(('.jpg', '.png', '.jpeg'))]

# Randomly select 5 images
sample_images = random.sample(images, 5)

for img_name in sample_images:
    img_path = os.path.join(image_folder, img_name)
    
    img = cv2.imread(img_path)
    
    if img is None:
        print(f"Failed to load {img_name}")
        continue
    
    cv2.imshow("Image", img)
    cv2.waitKey(0)

cv2.destroyAllWindows()