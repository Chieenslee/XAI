import cv2
import numpy as np
from PIL import Image
import torch
from torchvision import transforms
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

class ImagePreprocessor:
    def __init__(self, target_size=(224, 224)):
        """
        Khởi tạo Image Preprocessor cho mô hình AI y khoa.
        Kích thước mặc định 224x224 phù hợp với DenseNet / ResNet pre-trained.
        """
        self.target_size = target_size
        # Khởi tạo thuật toán CLAHE (Contrast Limited Adaptive Histogram Equalization)
        # Giúp làm rõ các cấu trúc xương sườn và màng phổi bị mờ
        self.clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        
        # Pipeline chuẩn hóa của PyTorch (đưa về phân phối chuẩn của ImageNet)
        self.torch_transform = transforms.Compose([
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])

    def apply_clahe(self, image: Image.Image) -> Image.Image:
        """
        Áp dụng CLAHE để tăng cường độ tương phản cho ảnh X-quang.
        """
        # Chuyển đổi sang numpy array và định dạng grayscale (nếu cần)
        img_np = np.array(image.convert('L'))
        
        # Áp dụng CLAHE
        enhanced_img_np = self.clahe.apply(img_np)
        
        # Chuyển đổi lại về RGB vì các mô hình pre-trained yêu cầu đầu vào 3 kênh màu (RGB)
        enhanced_rgb = cv2.cvtColor(enhanced_img_np, cv2.COLOR_GRAY2RGB)
        return Image.fromarray(enhanced_rgb)

    def preprocess_for_inference(self, image: Image.Image) -> torch.Tensor:
        """
        Tiền xử lý hoàn chỉnh một ảnh đầu vào để sẵn sàng cho mô hình dự đoán.
        """
        logging.info("Đang tiền xử lý ảnh đầu vào...")
        
        # 1. Tăng cường độ tương phản CLAHE
        enhanced_img = self.apply_clahe(image)
        
        # 2. Thay đổi kích thước (Resize)
        resized_img = enhanced_img.resize(self.target_size, Image.Resampling.LANCZOS)
        
        # 3. Chuyển đổi sang PyTorch Tensor và Chuẩn hóa (Normalize)
        tensor_img = self.torch_transform(resized_img)
        
        # 4. Thêm batch dimension (B, C, H, W)
        tensor_img = tensor_img.unsqueeze(0)
        
        logging.info(f"Hoàn thành tiền xử lý. Kích thước tensor đầu ra: {tensor_img.shape}")
        return tensor_img

# Test nhanh module nếu chạy file này trực tiếp
if __name__ == "__main__":
    try:
        # Tạo ảnh giả lập để test
        dummy_img = Image.fromarray(np.random.randint(0, 255, (512, 512), dtype=np.uint8), mode='L')
        preprocessor = ImagePreprocessor()
        output_tensor = preprocessor.preprocess_for_inference(dummy_img)
        print("Module tiền xử lý hoạt động bình thường!")
    except Exception as e:
        print(f"Lỗi: {e}")
