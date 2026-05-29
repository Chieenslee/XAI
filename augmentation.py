import os
import cv2
import numpy as np

def apply_clahe(img):
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    return clahe.apply(img)

def augment_image(img_path, output_dir, prefix="aug_"):
    img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        return
        
    filename = os.path.basename(img_path)
    os.makedirs(output_dir, exist_ok=True)
    
    # 1. CLAHE (Contrast Limited Adaptive Histogram Equalization)
    img_clahe = apply_clahe(img)
    cv2.imwrite(os.path.join(output_dir, f"{prefix}clahe_{filename}"), img_clahe)
    
    # 2. Rotation (-15 to 15 degrees)
    rows, cols = img.shape
    M = cv2.getRotationMatrix2D((cols/2, rows/2), 15, 1)
    img_rot = cv2.warpAffine(img, M, (cols, rows))
    cv2.imwrite(os.path.join(output_dir, f"{prefix}rot_{filename}"), img_rot)
    
    # 3. Random Crop and Resize back
    start_x = int(cols * 0.1)
    start_y = int(rows * 0.1)
    img_crop = img[start_y:rows-start_y, start_x:cols-start_x]
    img_crop = cv2.resize(img_crop, (cols, rows))
    cv2.imwrite(os.path.join(output_dir, f"{prefix}crop_{filename}"), img_crop)

def augment_dataset(dataset_dir="data/sample_dataset", output_dir="data/augmented_dataset"):
    classes = ['normal', 'effusion']
    for cls in classes:
        cls_dir = os.path.join(dataset_dir, cls)
        out_cls_dir = os.path.join(output_dir, cls)
        if not os.path.exists(cls_dir): continue
        
        images = os.listdir(cls_dir)[:20] # Demo augmentation on first 20 images
        for img_name in images:
            img_path = os.path.join(cls_dir, img_name)
            # Copy original
            os.makedirs(out_cls_dir, exist_ok=True)
            img = cv2.imread(img_path)
            if img is not None:
                cv2.imwrite(os.path.join(out_cls_dir, img_name), img)
            
            # Apply Augmentations
            augment_image(img_path, out_cls_dir)

if __name__ == "__main__":
    augment_dataset()
