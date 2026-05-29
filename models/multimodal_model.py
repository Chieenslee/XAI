import torch
import torch.nn as nn
from transformers import AutoModel, AutoConfig

class MultimodalModel(nn.Module):
    def __init__(self, image_model, text_model_name="vinai/phobert-base", num_classes=1, hidden_dim=256):
        """
        Kiến trúc Đa phương thức:
        - Image Branch: pretrained DenseNet121 (truyền vào qua tham số image_model)
        - Text Branch: PhoBERT
        - Fusion: Nối đặc trưng (Concatenation) -> Fully Connected -> Output
        """
        super(MultimodalModel, self).__init__()
        
        # 1. Image Branch
        self.image_model = image_model
        # Lấy kích thước vector đặc trưng của Image Branch trước lớp Classifier cuối cùng
        # (Ở PleuralEffusionModel, lớp ẩn cuối cùng là 256)
        self.image_feature_dim = 256
        
        # Sửa đổi lớp classifier của Image Model để xuất ra vector đặc trưng thay vì dự đoán nhị phân
        # Ta giữ lại lớp nn.Linear(num_ftrs, 256) và ReLU
        self.image_model.densenet.classifier = nn.Sequential(
            *list(self.image_model.densenet.classifier.children())[:-2] # Bỏ Dropout và Linear(256, 1)
        )
        
        # 2. Text Branch (PhoBERT)
        config = AutoConfig.from_pretrained(text_model_name)
        self.text_model = AutoModel.from_config(config) # Sử dụng config để test offline nhanh hoặc load pretrained
        self.text_feature_dim = config.hidden_size # 768 cho phobert-base
        
        # 3. Fusion Layer
        self.fusion = nn.Sequential(
            nn.Linear(self.image_feature_dim + self.text_feature_dim, hidden_dim),
            nn.BatchNorm1d(hidden_dim),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(hidden_dim, int(hidden_dim / 2)),
            nn.ReLU(),
            nn.Linear(int(hidden_dim / 2), num_classes)
        )
        
    def forward(self, images, input_ids, attention_mask):
        # Trích xuất đặc trưng ảnh
        img_features = self.image_model(images) # Shape: (batch_size, 256)
        
        # Trích xuất đặc trưng văn bản (từ CLS token của PhoBERT)
        text_outputs = self.text_model(input_ids=input_ids, attention_mask=attention_mask)
        # pooled_output hoặc text_outputs[0][:, 0, :]
        text_features = text_outputs.last_hidden_state[:, 0, :] # Shape: (batch_size, 768)
        
        # Kết hợp hai vector (Concatenation)
        combined_features = torch.cat((img_features, text_features), dim=1) # Shape: (batch_size, 1024)
        
        # Dự đoán
        logits = self.fusion(combined_features)
        return logits

if __name__ == "__main__":
    from core_model import PleuralEffusionModel
    
    print("Đang khởi tạo Multimodal Model...")
    # Tạm tắt pretrained để test nhanh không cần tải weights
    img_model = PleuralEffusionModel(pretrained=False)
    
    # Text model sẽ tự load config của PhoBERT
    try:
        model = MultimodalModel(image_model=img_model)
        
        # Dummy inputs
        batch_size = 2
        dummy_images = torch.randn(batch_size, 3, 224, 224)
        dummy_input_ids = torch.randint(0, 1000, (batch_size, 128))
        dummy_attention_mask = torch.ones(batch_size, 128)
        
        out = model(dummy_images, dummy_input_ids, dummy_attention_mask)
        print(f"Khởi tạo thành công! Output shape: {out.shape}")
    except Exception as e:
        print(f"Lỗi khởi tạo (có thể do chưa tải mô hình PhoBERT): {e}")
