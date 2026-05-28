import os
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, Dataset
from torchvision import transforms
from PIL import Image
import logging
from tqdm import tqdm
import sys

# Thêm thư mục gốc vào sys.path để import model
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models.core_model import PleuralEffusionModel
from backend.preprocess import ImagePreprocessor

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

class DummyXRayDataset(Dataset):
    """Dataset tạm thời để load ảnh từ thư mục sample_dataset phục vụ test luồng code."""
    def __init__(self, data_dir, transform=None):
        self.data_dir = data_dir
        self.transform = transform
        self.images = []
        self.labels = []
        
        # Đọc dữ liệu (Bình thường: 0, Tràn dịch: 1)
        normal_dir = os.path.join(data_dir, 'normal')
        effusion_dir = os.path.join(data_dir, 'effusion')
        
        for img_name in os.listdir(normal_dir):
            self.images.append(os.path.join(normal_dir, img_name))
            self.labels.append(0.0)
            
        for img_name in os.listdir(effusion_dir):
            self.images.append(os.path.join(effusion_dir, img_name))
            self.labels.append(1.0)
            
    def __len__(self):
        return len(self.images)
        
    def __getitem__(self, idx):
        img_path = self.images[idx]
        image = Image.open(img_path).convert('RGB')
        label = torch.tensor([self.labels[idx]], dtype=torch.float32)
        
        if self.transform:
            image = self.transform(image)
        return image, label

def train_model():
    # 1. Khởi tạo môi trường
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    logging.info(f"Đang sử dụng thiết bị: {device}")
    
    # 2. Chuẩn bị Dữ liệu
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(base_dir, 'data', 'sample_dataset')
    
    # Sử dụng pipeline transform mặc định (Không dùng CLAHE ở bước train này để test nhanh)
    # Trong môi trường thực tế, ta sẽ build một pipeline Augmentation riêng ở đây
    transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])
    
    dataset = DummyXRayDataset(data_dir, transform=transform)
    dataloader = DataLoader(dataset, batch_size=2, shuffle=True) # Batch size nhỏ cho bộ test
    
    # 3. Khởi tạo Mô hình, Optimizer & Loss
    model = PleuralEffusionModel(pretrained=False).to(device)
    criterion = nn.BCEWithLogitsLoss()
    optimizer = torch.optim.AdamW(model.parameters(), lr=1e-4)
    
    # 4. Huấn luyện với Mixed Precision (AMP) - Tối ưu cho RTX 3050
    scaler = torch.cuda.amp.GradScaler() if torch.cuda.is_available() else None
    
    epochs = 5
    logging.info("Bắt đầu quá trình huấn luyện...")
    for epoch in range(epochs):
        model.train()
        running_loss = 0.0
        
        # Tqdm tạo thanh tiến trình hiển thị trên terminal
        pbar = tqdm(dataloader, desc=f"Epoch {epoch+1}/{epochs}")
        for inputs, labels in pbar:
            inputs, labels = inputs.to(device), labels.to(device)
            optimizer.zero_grad()
            
            if scaler:
                # Chạy với Mixed Precision (FP16)
                with torch.cuda.amp.autocast():
                    outputs = model(inputs)
                    loss = criterion(outputs, labels)
                scaler.scale(loss).backward()
                scaler.step(optimizer)
                scaler.update()
            else:
                # Chạy với CPU (FP32)
                outputs = model(inputs)
                loss = criterion(outputs, labels)
                loss.backward()
                optimizer.step()
                
            running_loss += loss.item()
            pbar.set_postfix({'Loss': f"{loss.item():.4f}"})
            
        epoch_loss = running_loss / len(dataloader)
        logging.info(f"Epoch {epoch+1} hoàn tất - Average Loss: {epoch_loss:.4f}")
        
    # Lưu trọng số mô hình
    save_path = os.path.join(base_dir, 'models', 'pleural_effusion_model_best.pth')
    torch.save(model.state_dict(), save_path)
    logging.info(f"Đã lưu trọng số mô hình tại: {save_path}")

if __name__ == "__main__":
    train_model()
