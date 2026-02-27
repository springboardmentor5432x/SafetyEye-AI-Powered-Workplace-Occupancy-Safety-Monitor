import os
import shutil

# === ORIGINAL DATASET PATH ===
base_path = r"C:/Users/User/Desktop/SafetyAI/Data/raw/archive/css-data"

# === NEW YOLO DATASET PATH ===
output_path = r"C:/Users/User/Desktop/SafetyAI/Data/raw/safety_dataset"

mapping = {
    "train": "train",
    "valid": "val",   # IMPORTANT: rename valid → val
    "test": "test"
}

for original_folder, new_folder in mapping.items():
    print(f"Processing {original_folder}...")

    # Image paths
    image_src = os.path.join(base_path, original_folder, "images")
    label_src = os.path.join(base_path, original_folder, "labels")

    image_dst = os.path.join(output_path, "images", new_folder)
    label_dst = os.path.join(output_path, "labels", new_folder)

    # Copy images
    for file in os.listdir(image_src):
        shutil.copy(os.path.join(image_src, file), image_dst)

    # Copy labels
    for file in os.listdir(label_src):
        shutil.copy(os.path.join(label_src, file), label_dst)

print("Dataset organization completed successfully!")