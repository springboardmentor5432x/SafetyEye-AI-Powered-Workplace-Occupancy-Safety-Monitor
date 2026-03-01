import os

splits = ['train', 'valid', 'test']

for split in splits:
    img_folder = f'dataset/{split}/images'
    label_folder = f'dataset/{split}/labels'

    img_files = sorted([f for f in os.listdir(img_folder) if f.endswith(('.jpg', '.png', '.jpeg'))])
    label_files = sorted([f for f in os.listdir(label_folder) if f.endswith('.txt')])

    # Remove file extensions for comparison
    img_names = set(os.path.splitext(f)[0] for f in img_files)
    label_names = set(os.path.splitext(f)[0] for f in label_files)

    missing_labels = img_names - label_names
    extra_labels = label_names - img_names

    print(f"\n=== {split.upper()} ===")
    print(f"Images: {len(img_files)}, Labels: {len(label_files)}")
    
    if missing_labels:
        print(f"Images missing labels: {missing_labels}")
    else:
        print("All images have labels ✅")
    
    if extra_labels:
        print(f"Labels without images: {extra_labels}")
    else:
        print("No extra labels ✅")