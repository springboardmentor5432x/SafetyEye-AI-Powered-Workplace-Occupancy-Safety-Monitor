import cv2
import os

image_folder = "dataset/images/train"

files = os.listdir(image_folder)
files = [f for f in files if f.lower().endswith((".jpg", ".jpeg", ".png"))]

print("Total images found:", len(files))

img_path = os.path.join(image_folder, files[0])
print("Displaying:", img_path)

img = cv2.imread(img_path)

if img is None:
    print("Error: Could not read image")
else:
    cv2.imshow("Sample Image", img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
