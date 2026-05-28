import torch
import torch.nn as nn
from torchvision import models
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

class PleuralEffusionModel(nn.Module):
    def __init__(self, pretrained=True):
        super(PleuralEffusionModel, self).__init__()
        
        # Sử dụng DenseNet121 làm backbone (Rất phổ biến trong y khoa như CheXpert)
        logging.info("Khởi tạo mô hình DenseNet121 Backbone...")
        # PyTorch 2.0+ sử dụng weights='DEFAULT' thay cho pretrained=True
        weights = models.DenseNet121_Weights.DEFAULT if pretrained else None
        self.densenet = models.densenet121(weights=weights)
        
        # Lưu lại layer tính năng cuối cùng để sau này dùng cho thuật toán Grad-CAM (XAI)
        # DenseNet feature map cuối cùng nằm ở self.densenet.features
        
        # Thay đổi Fully Connected Layer cuối cùng (classifier)
        # Bài toán phân loại nhị phân (Bình thường vs Tràn dịch) -> 1 output node
        num_ftrs = self.densenet.classifier.in_features
        self.densenet.classifier = nn.Sequential(
            nn.Linear(num_ftrs, 256),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(256, 1) # 1 Output node (Xác suất bị tràn dịch)
        )
        
    def forward(self, x):
        # Trả về raw logits (sẽ dùng Sigmoid hoặc BCEWithLogitsLoss sau)
        return self.densenet(x)
        
    def get_features(self, x):
        """Hàm phụ trợ cho Grad-CAM, lấy feature maps ở layer tích chập cuối"""
        features = self.densenet.features(x)
        return features

if __name__ == "__main__":
    # Test khởi tạo model
    model = PleuralEffusionModel(pretrained=False)
    dummy_input = torch.randn(1, 3, 224, 224)
    output = model(dummy_input)
    print(f"Khởi tạo thành công! Kích thước đầu ra: {output.shape} (Dự kiến: [1, 1])")
