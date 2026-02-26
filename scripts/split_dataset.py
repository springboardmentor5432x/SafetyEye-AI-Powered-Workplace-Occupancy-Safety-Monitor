import os
import random
import shutil

# Source dataset folders
source_folders = [
    "dataset/css-data/train",
    "dataset/css-data/valid",
    "dataset/css-data/test"
]

# Destination folders
dest_images = "dataset/images"
dest_labels = "dataset/labels"

# Create destination folders if not exist
for split in ["train", "val", "test"]:
    os.makedirs(os.path.join(dest_images, split), exist_ok=True)
    os.makedirs(os.path.join(dest_labels, split), exist_ok=True)

# Collect all image paths
all_images = []

for folder in source_folders:
    image_folder = os.path.join(folder, "images")
    for img in os.listdir(image_folder):
        all_images.append(os.path.join(image_folder, img))

# Shuffle images
random.shuffle(all_images)

total = len(all_images)
train_count = int(0.7 * total)
val_count = int(0.2 * total)
test_count = total - train_count - val_count

print(f"Total images: {total}")
print(f"Train: {train_count}, Val: {val_count}, Test: {test_count}")

# Function to move files
def move_files(image_list, split_name):
    for img_path in image_list:
        filename = os.path.basename(img_path)
        label_filename = filename.replace(".jpg", ".txt").replace(".png", ".txt")

        # Find label path
        label_path = None
        for folder in source_folders:
            possible_label = os.path.join(folder, "labels", label_filename)
            if os.path.exists(possible_label):
                label_path = possible_label
                break

        # Move image
        shutil.copy(img_path, os.path.join(dest_images, split_name, filename))

        # Move label if exists
        if label_path:
            shutil.copy(label_path, os.path.join(dest_labels, split_name, label_filename))

# Split and move
move_files(all_images[:train_count], "train")
move_files(all_images[train_count:train_count+val_count], "val")
move_files(all_images[train_count+val_count:], "test")

print("Dataset split completed successfully!")