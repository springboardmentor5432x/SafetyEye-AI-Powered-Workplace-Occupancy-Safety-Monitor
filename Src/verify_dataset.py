import os

base_path = r"C:/Users/User/Desktop/SafetyAI/Data/raw/safety_dataset"

splits = ["train", "val", "test"]

for split in splits:
    images = os.listdir(os.path.join(base_path, "images", split))
    labels = os.listdir(os.path.join(base_path, "labels", split))

    print(f"{split.upper()}")
    print("Images:", len(images))
    print("Labels:", len(labels))
    print("-" * 30)