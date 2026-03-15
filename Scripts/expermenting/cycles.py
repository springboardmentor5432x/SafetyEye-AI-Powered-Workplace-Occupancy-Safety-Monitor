import os
import cv2


folder_path = "first_training/safety_monitor/"

images = [f for f in os.listdir(folder_path) if f.lower().endswith(('.png','.jpg','.jpeg'))]

index = 0 


while True :
    img = cv2.imread(os.path.join(folder_path,images[index]))
    scale_percent = 0.5 
    width = int(img.shape[1] * scale_percent)
    height = int(img.shape[0] * scale_percent)
    dim = (width, height)

# Resize using INTER_AREA (best for shrinking)
    resized = cv2.resize(img, dim, interpolation=cv2.INTER_AREA)

    cv2.imshow('images',resized)

    key = cv2.waitKey(0)

    if key == ord('d'):
        index = (index+1)%len(images)
    elif key ==ord('a'):
        index = (index-1)%len(images)

    elif key == ord('q'):
        break
cv2.destroyAllWindows()