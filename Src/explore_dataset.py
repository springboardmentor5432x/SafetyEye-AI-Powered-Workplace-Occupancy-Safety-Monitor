import cv2
import os
import matplotlib.pyplot as plt

image_path = r"C:/Users/User/Desktop/SafetyAI/Data/raw/archive/css-data/test/images"

images = os.listdir(image_path)

print("Files found:", images[:5])  

img_path = os.path.join(image_path, images[0])
print("Trying to open:", img_path)

img = cv2.imread(img_path)

if img is None:
    print("Image not loaded. Check path!")
else:
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    plt.imshow(img)
    plt.axis("off")
    plt.show()
