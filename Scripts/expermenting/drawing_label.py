import cv2 
import os 
import random


img_dir = '../../Datasets/css-data/train/images'
lbl_dir = '../../Datasets/css-data/train/labels'


file_name = random.choice([f for f in os.listdir(lbl_dir) if f.endswith('.txt')]).replace('.txt','')
image  = cv2.imread(os.path.join(img_dir , f"{file_name}.jpg"))

h, w, _ = image.shape

with open(os.path.join(lbl_dir , f"{file_name}.txt" ),'r') as f:
    for line in f :
        cls_id , x , y , be, bh  = map(float, line.split())
        x1 = int((x - be/2)*w)
        y1 = int((y-bh/2)*h)
        x2 = int(( x+  be/2)*w)
        y2 = int((y + bh/2)*h)

        cv2.rectangle(image , (x1 , y1) , (x2,y2),(0,255,0),2)

        cv2.putText(image , f"ID: {int(cls_id)}",(x1,y1-10),cv2.FONT_HERSHEY_COMPLEX, 0.6 ,(0,255,0),2)
        

cv2.imshow("label check", image)
cv2.waitKey(0)
cv2.destroyAllWindows()