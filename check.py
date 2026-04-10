import cv2
path = r"output_videos\my_first_test.mp4"
cap = cv2.VideoCapture(path)
print("Is opened:", cap.isOpened())
if cap.isOpened():
    ret, frame = cap.read()
    print("Read success:", ret)
cap.release()
