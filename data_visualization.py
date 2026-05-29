import os
import cv2
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

def visualize_dataset(dataset_dir="data/sample_dataset", output_dir="data/visualizations"):
    os.makedirs(output_dir, exist_ok=True)
    
    classes = ['normal', 'effusion']
    counts = []
    
    plt.style.use('ggplot')
    
    # 1. Bar chart for class distribution
    for cls in classes:
        cls_dir = os.path.join(dataset_dir, cls)
        if os.path.exists(cls_dir):
            counts.append(len(os.listdir(cls_dir)))
        else:
            counts.append(0)
            
    plt.figure(figsize=(8, 6))
    bars = plt.bar(classes, counts, color=['#2E7D32', '#FF6B6B'])
    plt.title('Phân bố nhãn dữ liệu (Class Distribution)', fontsize=16)
    plt.xlabel('Nhãn chẩn đoán', fontsize=12)
    plt.ylabel('Số lượng ảnh', fontsize=12)
    
    for bar in bars:
        yval = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2, yval + 0.1, int(yval), ha='center', va='bottom', fontsize=12)
        
    plt.savefig(os.path.join(output_dir, 'class_distribution.png'), dpi=300, bbox_inches='tight')
    plt.close()
    
    # 2. Histogram of pixel intensities
    plt.figure(figsize=(10, 6))
    
    colors = {'normal': 'green', 'effusion': 'red'}
    for cls in classes:
        cls_dir = os.path.join(dataset_dir, cls)
        if not os.path.exists(cls_dir): continue
        
        images = os.listdir(cls_dir)[:50] # Sample up to 50 images per class
        all_pixels = []
        for img_name in images:
            img_path = os.path.join(cls_dir, img_name)
            img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
            if img is not None:
                all_pixels.extend(img.flatten())
                
        if all_pixels:
            sns.kdeplot(np.array(all_pixels), color=colors[cls], label=cls.capitalize(), fill=True, alpha=0.3)
            
    plt.title('Phân bố phổ màu điểm ảnh (Pixel Intensity Histogram)', fontsize=16)
    plt.xlabel('Cường độ Pixel (0 - 255)', fontsize=12)
    plt.ylabel('Mật độ', fontsize=12)
    plt.legend()
    plt.savefig(os.path.join(output_dir, 'pixel_intensity_histogram.png'), dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"Đã xuất các biểu đồ phân tích dữ liệu tại thư mục: {output_dir}")

if __name__ == "__main__":
    visualize_dataset()
