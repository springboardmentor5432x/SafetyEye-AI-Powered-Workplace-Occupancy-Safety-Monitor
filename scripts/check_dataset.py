import os
import cv2
import random

# Path to training images
image_folder = "../dataset/css-data/train/images"

# Get all image files
images = [f for f in os.listdir(image_folder) if f.endswith(('.jpg', '.png'))]

# Select 3 random images
sample_images = random.sample(images, 3)

for img_name in sample_images:
    img_path = os.path.join(image_folder, img_name)
    image = cv2.imread(img_path)

    if image is None:
        print(f"Failed to load {img_name}")
        continue

    cv2.imshow("Sample Image", image)
    cv2.waitKey(0)

cv2.destroyAllWindows()