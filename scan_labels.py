import os

labels_path = "dataset/labels"
max_class = 9   # because nc = 10

errors = []

for root, dirs, files in os.walk(labels_path):
    for file in files:
        if file.endswith(".txt"):
            path = os.path.join(root, file)

            with open(path, "r") as f:
                for line in f:
                    parts = line.strip().split()

                    if len(parts) > 0:
                        cls = int(parts[0])

                        if cls > max_class:
                            errors.append((path, cls))

if errors:
    print("Invalid class IDs found:\n")
    for e in errors:
        print(e)
else:
    print("✅ All labels have valid class IDs")