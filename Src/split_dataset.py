import os
import random
import shutil

# ====== CHANGE THESE PATHS ONLY IF NEEDED ======
base_path = r"C:/Users/User/Desktop/SafetyAI/Data/raw/archive/css-data"
output_path = "data/raw/safety_dataset"  # where YOLO dataset will go
# ==============================================

images_path = os.path.join(base_path, "images")
labels_path = os.path.join(base_path, "labels")

images = [f for f in os.listdir(images_path) if f.endswith(('.jpg', '.png', '.jpeg'))]

random.shuffle(images)

total = len(images)

train_split = int(0.7 * total)
val_split = int(0.2 * total)

train_files = images[:train_split]
val_files = images[train_split:train_split + val_split]
test_files = images[train_split + val_split:]

def move_files(file_list, split):
    for file in file_list:
        image_src = os.path.join(images_path, file)
        label_src = os.path.join(labels_path, file.replace('.jpg', '.txt').replace('.png', '.txt').replace('.jpeg', '.txt'))

        image_dst = os.path.join(output_path, "images", split, file)
        label_dst = os.path.join(output_path, "labels", split, file.replace('.jpg', '.txt').replace('.png', '.txt').replace('.jpeg', '.txt'))

        if os.path.exists(label_src):
            shutil.copy(image_src, image_dst)
            shutil.copy(label_src, label_dst)

move_files(train_files, "train")
move_files(val_files, "val")
move_files(test_files, "test")

print("Dataset split completed successfully!")
print(f"Total images: {total}")
print(f"Train: {len(train_files)}")
print(f"Val: {len(val_files)}")
print(f"Test: {len(test_files)}")