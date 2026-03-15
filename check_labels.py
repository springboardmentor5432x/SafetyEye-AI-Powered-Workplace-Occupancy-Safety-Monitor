import os

image_dir = "dataset/images/train"
label_dir = "dataset/labels/train"

image_files = {os.path.splitext(f)[0] for f in os.listdir(image_dir)
               if f.lower().endswith((".jpg", ".png", ".jpeg"))}

label_files = {os.path.splitext(f)[0] for f in os.listdir(label_dir)
               if f.lower().endswith(".txt")}

missing_labels = image_files - label_files
extra_labels = label_files - image_files

print(f"Total images: {len(image_files)}")
print(f"Total labels: {len(label_files)}")

if missing_labels:
    print("\n❌ Images missing labels:")
    for name in list(missing_labels)[:10]:
        print(name)
else:
    print("\n✅ All images have labels")

if extra_labels:
    print("\n⚠️ Labels without images:")
    for name in list(extra_labels)[:10]:
        print(name)