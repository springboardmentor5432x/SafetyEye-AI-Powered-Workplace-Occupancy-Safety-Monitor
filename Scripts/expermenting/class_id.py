import os

label_dir = '../Datasets/css-data/train/labels'

unique_classes = set()


for file in os.listdir(label_dir):
    if file.endswith(".txt"):
        with open(os.path.join(label_dir , file),"r") as f:

            for line in f :

                unique_classes.add(int(line.split()[0]))
print(f"Your unique Class IDs are: {sorted(list(unique_classes))}")

# 9. Counts how many unique IDs were found (this is your 'nc' value).
print(f"Set 'nc' in your yaml to: {len(unique_classes)}")