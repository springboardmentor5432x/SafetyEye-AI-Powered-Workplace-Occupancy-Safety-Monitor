import cv2
import os

# Path to the dataset train images
image_dir = r"C:\Users\Abhinay Chowdary\OneDrive\Desktop\safetyeye_mainfolder\dataset\images\train"

def main():
    if not os.path.exists(image_dir):
        print(f"Error: Directory {image_dir} does not exist.")
        return

    valid_exts = ('.jpg', '.png', '.jpeg')
    image_files = [f for f in os.listdir(image_dir) if f.lower().endswith(valid_exts)]
    
    if not image_files:
        print(f"No images found in {image_dir}")
        return
        
    print(f"Found {len(image_files)} images. Displaying the first 3...")
    for i, img_name in enumerate(image_files[:3]):
        img_path = os.path.join(image_dir, img_name)
        img = cv2.imread(img_path)
        
        if img is not None:
            # Resize image to a predictable size for consistent viewing
            img_resized = cv2.resize(img, (640, 640))
            cv2.imshow(f"Test Image {i+1}", img_resized)
            print(f"Displaying {img_name}... Press any key in the image window to close it and proceed.")
            cv2.waitKey(0)
        else:
            print(f"Failed to load {img_name}")
            
    cv2.destroyAllWindows()
    print("Success: Loaded and displayed images. OpenCV is working correctly.")

if __name__ == "__main__":
    main()
