import os

base_path = "dataset"

train_images = len(os.listdir(os.path.join(base_path, "train/images")))
val_images = len(os.listdir(os.path.join(base_path, "valid/images")))
test_images = len(os.listdir(os.path.join(base_path, "test/images")))

total = train_images + val_images + test_images

print("Train images:", train_images)
print("Validation images:", val_images)
print("Test images:", test_images)
print("Total images:", total)

print("\nSplit Percentage:")
print("Train:", round((train_images/total)*100, 2), "%")
print("Validation:", round((val_images/total)*100, 2), "%")
print("Test:", round((test_images/total)*100, 2), "%")