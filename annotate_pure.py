import cv2
import numpy as np
import os
import glob
import math

# Global variables
circles = []
image = None
clone = None
drawing = False
center_pt = None

def redraw_image():
    global image, clone, circles
    image_copy = clone.copy()
    for c_pt, c_r in circles:
        cv2.circle(image_copy, c_pt, c_r, (0, 255, 0), -1)
    return image_copy

def mouse_callback(event, x, y, flags, param):
    global circles, image, clone, drawing, center_pt
    if event == cv2.EVENT_LBUTTONDOWN:
        drawing = True
        center_pt = (x, y)
    elif event == cv2.EVENT_MOUSEMOVE:
        if drawing:
            r = int(math.hypot(x - center_pt[0], y - center_pt[1]))
            image_copy = redraw_image()
            cv2.circle(image_copy, center_pt, r, (0, 255, 0), 2)
            cv2.imshow("Annotator", image_copy)
    elif event == cv2.EVENT_LBUTTONUP:
        if drawing:
            drawing = False
            r = int(math.hypot(x - center_pt[0], y - center_pt[1]))
            if r > 0:
                circles.append((center_pt, r))
            image = redraw_image()
            cv2.imshow("Annotator", image)

def process_folder(folder_name):
    global circles, image, clone, drawing, center_pt
    
    input_dir = folder_name
    output_dir = f"{folder_name}_mask"
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    image_paths = []
    for ext in ['*.jpg', '*.jpeg', '*.png']:
        image_paths.extend(glob.glob(os.path.join(input_dir, ext)))
        
    for img_path in image_paths:
        filename = os.path.basename(img_path)
        name, _ = os.path.splitext(filename)
        mask_path = os.path.join(output_dir, f"{name}.png")
        
        if os.path.exists(mask_path):
            print(f"Skipping {filename}, already annotated.")
            continue
            
        print(f"Processing: {filename}")
        print("Controls: [Click & Drag] Draw circle | [d] Done & Save | [c] Clear | [s] Skip | [q] Quit")
        
        image = cv2.imread(img_path)
        if image is None:
            continue
            
        clone = image.copy()
        circles = []
        drawing = False
        center_pt = None
        
        cv2.namedWindow("Annotator")
        cv2.setMouseCallback("Annotator", mouse_callback)
        
        while True:
            cv2.imshow("Annotator", image)
            key = cv2.waitKey(1) & 0xFF
            
            if key == ord('d'):
                if len(circles) > 0:
                    mask = np.zeros(image.shape[:2], dtype=np.uint8)
                    for c_pt, c_r in circles:
                        cv2.circle(mask, c_pt, c_r, 255, -1)
                    cv2.imwrite(mask_path, mask)
                    print(f"Saved mask to {mask_path}")
                else:
                    print("No circles drawn, skipped saving.")
                break
            elif key == ord('c'):
                circles = []
                image = clone.copy()
                print("Cleared circles")
            elif key == ord('s'):
                print("Skipped")
                break
            elif key == ord('q'):
                print("Quitting...")
                cv2.destroyAllWindows()
                return False
                
    cv2.destroyAllWindows()
    return True

if __name__ == "__main__":
    folders = ['pure']
    for folder in folders:
        print(f"--- Starting folder: {folder} ---")
        if os.path.exists(folder):
            if not process_folder(folder):
                break
        else:
            print(f"Folder {folder} not found in current directory.")
