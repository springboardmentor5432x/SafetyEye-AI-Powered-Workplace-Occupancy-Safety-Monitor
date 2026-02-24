import os
import random
import shutil

# Paths
base_path = "dataset"
img_base = os.path.join(base_path, "images")
lbl_base = os.path.join(base_path, "labels")

# Temporary combined folder
all_images = []
splits = ["train", "val", "test"]

# Collect all image paths
for split in splits:
    img_dir = os.path.join(img_base, split)
    for file in os.listdir(img_dir):
        if file.lower().endswith((".jpg", ".jpeg", ".png")):
            all_images.append((file, split))

print("Total images found:", len(all_images))

# Shuffle images
random.shuffle(all_images)

# Calculate split indices
total = len(all_images)
train_end = int(0.7 * total)
val_end = int(0.9 * total)

train_files = all_images[:train_end]
val_files = all_images[train_end:val_end]
test_files = all_images[val_end:]

print("Train:", len(train_files))
print("Val:", len(val_files))
print("Test:", len(test_files))

def move_files(file_list, target_split):
    for filename, old_split in file_list:
        old_img_path = os.path.join(img_base, old_split, filename)
        old_lbl_path = os.path.join(lbl_base, old_split, os.path.splitext(filename)[0] + ".txt")

        new_img_path = os.path.join(img_base, target_split, filename)
        new_lbl_path = os.path.join(lbl_base, target_split, os.path.splitext(filename)[0] + ".txt")

        shutil.move(old_img_path, new_img_path)

        if os.path.exists(old_lbl_path):
            shutil.move(old_lbl_path, new_lbl_path)

# Move files
move_files(train_files, "train")
move_files(val_files, "val")
move_files(test_files, "test")

print("Dataset successfully split into 70/20/10")