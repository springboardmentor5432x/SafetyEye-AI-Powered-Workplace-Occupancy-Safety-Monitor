import os

def check_split(split):
    img_dir = f"dataset/images/{split}"
    lbl_dir = f"dataset/labels/{split}"

    img_exts = (".jpg", ".jpeg", ".png")

    images = [f for f in os.listdir(img_dir) if f.lower().endswith(img_exts)]
    labels = set(os.listdir(lbl_dir))

    missing_labels = []
    empty_labels = []
    bad_format = []

    for img in images:
        base = os.path.splitext(img)[0]
        lbl = base + ".txt"

        if lbl not in labels:
            missing_labels.append(img)
        else:
            # Check label content
            path = os.path.join(lbl_dir, lbl)
            try:
                with open(path, "r") as f:
                    lines = [l.strip() for l in f if l.strip()]
                if len(lines) == 0:
                    empty_labels.append(lbl)
                else:
                    for line in lines:
                        parts = line.split()
                        if len(parts) != 5:
                            bad_format.append(lbl)
                            break
                        # Optional: check numeric
                        try:
                            float_vals = list(map(float, parts))
                        except:
                            bad_format.append(lbl)
                            break
            except Exception:
                bad_format.append(lbl)

    print(f"\n=== {split.upper()} ===")
    print("Images:", len(images))
    print("Labels:", len(labels))
    print("Missing labels:", len(missing_labels))
    print("Empty labels:", len(empty_labels))
    print("Bad format labels:", len(bad_format))

    if missing_labels[:5]:
        print("Example missing:", missing_labels[:5])
    if bad_format[:5]:
        print("Example bad format:", bad_format[:5])

for s in ["train", "val", "test"]:
    check_split(s)