import os
import random
import shutil

# Paths
images_path = "/Users/utkarstdawar/Desktop/SafetyEye/datasets/images"
labels_path = "/Users/utkarstdawar/Desktop/SafetyEye/datasets/labels"

# Output folders
output_path = "dataset_split"

# Split ratios
train_ratio = 0.7
val_ratio = 0.2
test_ratio = 0.1

# Get image files
images = [f for f in os.listdir(images_path) if f.endswith(('.jpg','.png','.jpeg'))]

# Shuffle images
random.shuffle(images)

# Calculate split sizes
total = len(images)
train_size = int(total * train_ratio)
val_size = int(total * val_ratio)

train_images = images[:train_size]
val_images = images[train_size:train_size+val_size]
test_images = images[train_size+val_size:]

# Function to move files
def move_files(image_list, split):
    
    os.makedirs(f"{output_path}/images/{split}", exist_ok=True)
    os.makedirs(f"{output_path}/labels/{split}", exist_ok=True)

    for img in image_list:
        
        label = img.rsplit('.',1)[0] + ".txt"
        
        img_src = os.path.join(images_path, img)
        label_src = os.path.join(labels_path, label)

        img_dst = os.path.join(output_path, "images", split, img)
        label_dst = os.path.join(output_path, "labels", split, label)

        shutil.copy(img_src, img_dst)

        if os.path.exists(label_src):
            shutil.copy(label_src, label_dst)

# Move files
move_files(train_images, "train")
move_files(val_images, "val")
move_files(test_images, "test")

print("Dataset split completed!")