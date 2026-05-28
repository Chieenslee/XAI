import os
import io
import base64
import torch
import numpy as np
from PIL import Image
from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import torchxrayvision as xrv
import torchvision.transforms as transforms
from models.xai_gradcam import XAIExplainer

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Pleural Effusion XAI API",
    description="API Chẩn đoán Tràn dịch Màng phổi tích hợp AI giải thích được",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Cho phép React gọi từ localhost:5173
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Biến toàn cục để lưu model trên RAM (Tránh load lại nhiều lần)
model = None
explainer = None
preprocessor = None
device = None

@app.on_event("startup")
async def load_model():
    global model, explainer, preprocessor, device
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"Khởi động API trên {device}...")
    
    # 2. Load Core Model
    print("Đang khởi tạo cấu trúc TorchXRayVision (DenseNet-121)...")
    model = xrv.models.DenseNet(weights="densenet121-res224-all")
    
    model_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "models", "pleural_effusion_model_best.pth")
    if os.path.exists(model_path):
        print(f"✅ Đang tải bộ trọng số Fine-tuned Y khoa ({os.path.basename(model_path)})...")
        model.load_state_dict(torch.load(model_path, map_location=device, weights_only=True))
    else:
        print("⚠️ CẢNH BÁO: Không tìm thấy model fine-tuned. Đang sử dụng bộ trọng số gốc.")
        
    model.to(device)
    model.eval()
    
    # 3. Load XAI Explainer
    explainer = XAIExplainer(model=model)
    print("Sẵn sàng phục vụ!")

def image_to_base64(img_array: np.ndarray) -> str:
    """Chuyển đổi mảng numpy RGB thành chuỗi base64 jpg"""
    img = Image.fromarray(img_array)
    buffered = io.BytesIO()
    img.save(buffered, format="JPEG")
    return base64.b64encode(buffered.getvalue()).decode("utf-8")

@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Vui lòng tải lên định dạng hình ảnh hợp lệ (JPEG/PNG).")
    
    try:
        # 1. Đọc ảnh
        image_bytes = await file.read()
        image = Image.open(io.BytesIO(image_bytes))
        
        # Lưu lại bản copy numpy array của ảnh RGB để vẽ heatmap (GIỮ NGUYÊN KÍCH THƯỚC GỐC)
        orig_rgb = image.convert("RGB")
        orig_resized = np.array(orig_rgb).astype(np.float32) / 255.0
        
        # 2. Tiền xử lý theo chuẩn TorchXRayVision (Ảnh xám, dải [-1024, 1024])
        img_l = image.convert("L")
        img_np = np.array(img_l)
        img_np = xrv.datasets.normalize(img_np, 255) # convert 8-bit to [-1024, 1024]
        img_np = img_np[None, ...] # (1, H, W)
        
        transform = transforms.Compose([
            # Bỏ XRayCenterCrop để tránh việc AI bị mất đi phần đáy phổi nếu ảnh là hình chữ nhật dài
            xrv.datasets.XRayResizer(224)
        ])
        
        img_tensor = transform(img_np)
        input_tensor = torch.from_numpy(img_tensor).unsqueeze(0).to(device) # (1, 1, 224, 224)
        
        # 3. Dự đoán với Core AI
        with torch.no_grad():
            output = model(input_tensor)
            
        effusion_idx = model.pathologies.index("Effusion")
        probability = output[0][effusion_idx].item()
            
        # 4. Sinh Heatmap với XAI Grad-CAM
        heatmap_img_np = explainer.generate_heatmap(input_tensor, orig_resized, target_category=effusion_idx)
        
        # Chuyển đổi kết quả
        heatmap_b64 = image_to_base64(heatmap_img_np)
        
        # Ngưỡng tối ưu (Optimal Threshold) tìm được từ ROC Curve là 0.0682
        is_effusion = probability >= 0.0682
        
        # Rescale xác suất hiển thị UI (Nếu >= 0.0682 thì ánh xạ lên 50%-100%, nếu < 0.0682 thì 0-50%)
        # Điều này giúp UI hiển thị % hợp lý với kỳ vọng của người dùng (50% là ngưỡng chuẩn)
        if is_effusion:
            display_prob = 50.0 + ((probability - 0.0682) / (1.0 - 0.0682)) * 50.0
        else:
            display_prob = (probability / 0.0682) * 50.0
            
        return {
            "success": True,
            "prediction": "Tràn dịch màng phổi" if is_effusion else "Bình thường",
            "probability": round(display_prob, 2),
            "raw_probability": probability,
            "heatmap_base64": heatmap_b64
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api:app", host="127.0.0.1", port=8000, reload=True)
