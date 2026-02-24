import os

label_dir = "dataset/labels/train"

class_ids = set()

for file in os.listdir(label_dir):
    if file.endswith(".txt"):
        with open(os.path.join(label_dir, file), "r") as f:
            for line in f:
                if line.strip():
                    class_id = int(line.split()[0])
                    class_ids.add(class_id)

print("Classes found:", sorted(class_ids))
print("Total classes:", len(class_ids))