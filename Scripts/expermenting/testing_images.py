import cv2
from ultralytics import YOLO
import os
# load trained model
model = YOLO("Models/secondbest.pt")

folder_path = "Datasets/css-data/test/images/"

images = [f for f in os.listdir(folder_path) if f.lower().endswith(('.png','.jpg','.jpeg'))]

index = 0 


while True :
    img = cv2.imread(os.path.join(folder_path,images[index]))
#     scale_percent = 0.5 
#     width = int(img.shape[1] * scale_percent)
#     height = int(img.shape[0] * scale_percent)
#     dim = (width, height)

# # Resize using INTER_AREA (best for shrinking)
#     resized = cv2.resize(img, dim, interpolation=cv2.INTER_AREA)

    res = model(img)
    anoot = res[0].plot()
    cv2.imshow('images',anoot)

    key = cv2.waitKey(0)

    if key == ord('d'):
        index = (index+1)%len(images)
    elif key ==ord('a'):
        index = (index-1)%len(images)

    elif key == ord('q'):
        break
cv2.destroyAllWindows()