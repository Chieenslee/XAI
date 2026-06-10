import os
import io
import base64
import time
import logging
import torch
import numpy as np
import cv2
import psutil
import zipfile
import uuid
import threading
from PIL import Image
from typing import List
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import concurrent.futures

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import torchxrayvision as xrv
import torchvision.transforms as transforms
from models.xai_gradcam import XAIExplainer
from backend.ood_detector import OODDetector
from backend.database import DatabaseHelper

# ── Logging ──────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger("XAI.API")

if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

# ── Constants ────────────────────────────────────────────
MAX_UPLOAD_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB
BATCH_MAX_WORKERS = 4

# ── App ──────────────────────────────────────────────────
app = FastAPI(
    title="Pleural Effusion XAI API",
    description="API Chẩn đoán Tràn dịch Màng phổi tích hợp AI giải thích được (v2.0 SUPER)",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Global State ─────────────────────────────────────────
model = None
explainer = None
device = None
ood_detector = None
db = None
startup_time = None
ai_lock = threading.Lock()
db_lock = threading.Lock()


# ══════════════════════════════════════════════════════════
#  STARTUP
# ══════════════════════════════════════════════════════════
@app.on_event("startup")
async def load_model():
    global model, explainer, device, ood_detector, db, startup_time
    startup_time = time.time()
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    logger.info(f"Khởi động API trên thiết bị: {device}")

    # Load DenseNet-121
    logger.info("Đang tải cấu trúc TorchXRayVision DenseNet-121...")
    model = xrv.models.DenseNet(weights="densenet121-res224-all")

    model_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "models", "pleural_effusion_model_best.pth")
    if os.path.exists(model_path):
        logger.info(f"Tải bộ trọng số Fine-tuned: {os.path.basename(model_path)}")
        model.load_state_dict(torch.load(model_path, map_location=device, weights_only=True))
    else:
        logger.warning("Không tìm thấy model fine-tuned. Sử dụng bộ trọng số gốc.")

    model.to(device)
    model.eval()

    # XAI Explainer
    explainer = XAIExplainer(model=model)

    # System Components
    ood_detector = OODDetector()
    db = DatabaseHelper()

    logger.info(f"API sẵn sàng! (Khởi động trong {time.time() - startup_time:.1f}s)")


# ══════════════════════════════════════════════════════════
#  SHARED PIPELINE (Dùng chung cho cả Single và Batch)
# ══════════════════════════════════════════════════════════
def _preprocess_xray(image_bytes: bytes):
    """
    Pipeline tiền xử lý CHUẨN theo TorchXRayVision.
    Trả về (input_tensor, orig_for_heatmap, effusion_idx)
    """
    image = Image.open(io.BytesIO(image_bytes))

    # Lưu bản copy cho Grad-CAM overlay
    orig_rgb = image.convert("RGB")
    orig_for_heatmap = np.array(orig_rgb).astype(np.float32) / 255.0

    # Tiền xử lý theo chuẩn TorchXRayVision: Grayscale → normalize → resize
    img_l = image.convert("L")
    img_np = np.array(img_l)
    img_np = xrv.datasets.normalize(img_np, 255)  # [0,255] → [-1024, 1024]
    img_np = img_np[None, ...]  # (1, H, W)

    transform = transforms.Compose([
        xrv.datasets.XRayResizer(224)
    ])

    img_tensor = transform(img_np)
    input_tensor = torch.from_numpy(img_tensor).unsqueeze(0).to(device)  # (1, 1, 224, 224)

    effusion_idx = model.pathologies.index("Effusion")

    return input_tensor, orig_for_heatmap, effusion_idx


def _predict_and_explain(input_tensor, orig_for_heatmap, effusion_idx):
    """
    Chạy inference + Grad-CAM. Trả về dict kết quả.
    Đã được bọc khóa luồng (ai_lock) để tránh đụng độ PyTorch Hook.
    """
    with ai_lock:
        with torch.no_grad():
            output = model(input_tensor)

        probability = output[0][effusion_idx].item()

        # Ngưỡng tối ưu từ ROC Curve
        is_effusion = probability >= 0.0682

        # Tính toán Độ tin cậy (Confidence) để hiển thị cho Bác sĩ
        if is_effusion:
            # Nếu chẩn đoán là Có Bệnh -> Hiển thị độ tin cậy của việc Có Bệnh (Từ 50% -> 100%)
            display_prob = 50.0 + ((probability - 0.0682) / (1.0 - 0.0682)) * 50.0
        else:
            # Nếu chẩn đoán là Bình thường -> Hiển thị độ tin cậy của việc Khỏe Mạnh (Từ 50% -> 100%)
            # Xác suất bệnh càng thấp -> Xác suất khỏe mạnh càng cao
            illness_prob = (probability / 0.0682) * 50.0
            display_prob = 100.0 - illness_prob

        prediction_label = "Tràn dịch màng phổi" if is_effusion else "Bình thường"

        # Grad-CAM
        heatmap_img_np, generated_explanation = explainer.generate_heatmap(
            input_tensor, orig_for_heatmap, target_category=effusion_idx, is_abnormal=is_effusion
        )
        heatmap_b64 = _image_to_base64(heatmap_img_np)

        explanation_final = generated_explanation if is_effusion else \
            "Hệ thống AI không phát hiện đám mờ cản quang bất thường. Các góc sườn hoành hai bên sắc nét, vòm hoành bình thường."

        return {
            "prediction": prediction_label,
            "probability": round(display_prob, 2),
            "raw_probability": probability,
            "is_effusion": is_effusion,
            "heatmap_base64": heatmap_b64,
            "explanation": explanation_final
        }


def _image_to_base64(img_array: np.ndarray) -> str:
    img = Image.fromarray(img_array)
    buffered = io.BytesIO()
    img.save(buffered, format="JPEG")
    return base64.b64encode(buffered.getvalue()).decode("utf-8")


# ══════════════════════════════════════════════════════════
#  ENDPOINTS
# ══════════════════════════════════════════════════════════

# ── Health Check ─────────────────────────────────────────
@app.get("/health")
async def health_check():
    mem = psutil.virtual_memory()
    return {
        "status": "online",
        "model_loaded": model is not None,
        "device": str(device) if device else "unknown",
        "uptime_seconds": round(time.time() - startup_time, 1) if startup_time else 0,
        "ram_used_gb": round(mem.used / (1024**3), 2),
        "ram_total_gb": round(mem.total / (1024**3), 2),
        "ram_percent": mem.percent,
        "db_records": db.get_statistics()["total_records"] if db else 0
    }


# ── Statistics ───────────────────────────────────────────
@app.get("/stats")
async def get_stats():
    if db is None:
        raise HTTPException(status_code=503, detail="Database chưa khởi tạo.")
    return {"success": True, **db.get_statistics()}


# ── Single Predict ───────────────────────────────────────
@app.post("/predict")
async def predict(file: UploadFile = File(...), clinical_notes: str = Form("Không có")):
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Vui lòng tải lên định dạng hình ảnh hợp lệ (JPEG/PNG).")

    try:
        image_bytes = await file.read()

        # File size check
        if len(image_bytes) > MAX_UPLOAD_SIZE_BYTES:
            raise HTTPException(status_code=400, detail=f"Kích thước file vượt quá giới hạn {MAX_UPLOAD_SIZE_BYTES // (1024*1024)}MB.")

        # OOD Detection
        temp_path = f"temp_upload_{uuid.uuid4().hex}.jpg"
        with open(temp_path, "wb") as f:
            f.write(image_bytes)

        if ood_detector.is_ood(temp_path):
            os.remove(temp_path)
            raise HTTPException(status_code=400, detail="Ảnh tải lên không hợp lệ. Vui lòng tải lên ảnh X-quang phổi trắng đen (Grayscale). Hệ thống từ chối ảnh tự nhiên (OOD).")
        os.remove(temp_path)

        # Pipeline chuẩn
        input_tensor, orig_for_heatmap, effusion_idx = _preprocess_xray(image_bytes)
        result = _predict_and_explain(input_tensor, orig_for_heatmap, effusion_idx)

        # Lưu DB an toàn đa luồng
        try:
            with db_lock:
                db.insert_record(
                    patient_name="Bệnh nhân Ẩn danh",
                    clinical_notes=clinical_notes,
                    image_path=file.filename,
                    mask_path="N/A",
                    heatmap_path=result["heatmap_base64"],
                    prediction_label=result["prediction"],
                    confidence_score=result["probability"]
                )
        except Exception as e:
            logger.error(f"Lỗi lưu DB: {e}")

        return {"success": True, **result}

    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Lỗi trong /predict")
        raise HTTPException(status_code=500, detail=str(e))


# ── Batch Predict (Đa luồng) ────────────────────────────
def _process_single_image_worker(file_bytes: bytes, filename: str):
    """Worker chạy trên thread riêng. Dùng chung pipeline với /predict."""
    try:
        base_name = os.path.splitext(filename)[0]
        patient_name = base_name.replace('_', ' ').replace('-', ' ')

        # OOD
        temp_path = f"temp_batch_{uuid.uuid4().hex}_{filename}"
        with open(temp_path, "wb") as f:
            f.write(file_bytes)

        if ood_detector.is_ood(temp_path):
            os.remove(temp_path)
            return {
                "filename": filename,
                "patient_name": patient_name,
                "success": False,
                "is_ood": True,
                "message": "Ảnh tải lên không hợp lệ (OOD). Không phải ảnh X-quang chuẩn."
            }
        os.remove(temp_path)

        # Dùng chung pipeline chuẩn
        input_tensor, orig_for_heatmap, effusion_idx = _preprocess_xray(file_bytes)
        result = _predict_and_explain(input_tensor, orig_for_heatmap, effusion_idx)

        # Lưu DB an toàn đa luồng
        try:
            with db_lock:
                db.insert_record(
                    patient_name=patient_name,
                    clinical_notes="Chẩn đoán hàng loạt (Batch)",
                    image_path=filename,
                    mask_path="N/A",
                    heatmap_path=result["heatmap_base64"],
                    prediction_label=result["prediction"],
                    confidence_score=result["probability"]
                )
        except Exception:
            pass

        return {
            "filename": filename,
            "patient_name": patient_name,
            "success": True,
            "is_ood": False,
            **result
        }
    except Exception as e:
        logger.error(f"Batch worker error [{filename}]: {e}")
        return {
            "filename": filename,
            "patient_name": filename,
            "success": False,
            "is_ood": False,
            "message": str(e)
        }


@app.post("/predict_batch")
async def predict_batch(files: List[UploadFile] = File(...)):
    if not files:
        raise HTTPException(status_code=400, detail="Không có tệp nào được tải lên.")

    file_data_list = []
    for file in files:
        if file.filename.lower().endswith('.zip') or (file.content_type and 'zip' in file.content_type):
            data = await file.read()
            try:
                with zipfile.ZipFile(io.BytesIO(data)) as z:
                    for zinfo in z.infolist():
                        basename = os.path.basename(zinfo.filename)
                        if (not zinfo.is_dir() and
                            basename.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp')) and
                            not basename.startswith('.') and
                            zinfo.file_size > 0):
                            
                            if zinfo.file_size <= MAX_UPLOAD_SIZE_BYTES:
                                zdata = z.read(zinfo.filename)
                                file_data_list.append((zdata, basename))
                            else:
                                logger.warning(f"Batch: Bỏ qua ảnh quá lớn trong ZIP: {zinfo.filename}")
            except zipfile.BadZipFile:
                logger.error(f"Batch: File ZIP không hợp lệ: {file.filename}")
        elif file.content_type and file.content_type.startswith("image/"):
            data = await file.read()
            if len(data) <= MAX_UPLOAD_SIZE_BYTES:
                file_data_list.append((data, file.filename))
            else:
                logger.warning(f"Batch: Bỏ qua file quá lớn: {file.filename}")

    if not file_data_list:
        raise HTTPException(status_code=400, detail="Không tìm thấy ảnh hợp lệ trong danh sách.")

    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=BATCH_MAX_WORKERS) as executor:
        future_map = {
            executor.submit(_process_single_image_worker, data, fname): fname
            for data, fname in file_data_list
        }
        for future in concurrent.futures.as_completed(future_map):
            results.append(future.result())

    return {"success": True, "results": results}


# ── History ──────────────────────────────────────────────
@app.get("/history")
async def get_history():
    if db is None:
        return {"success": False, "detail": "Database chưa được khởi tạo."}

    records = db.get_all_records()
    for r in records:
        if 'heatmap_path' in r and len(str(r.get('heatmap_path', ''))) > 100:
            r['heatmap_path'] = "[BASE64_DATA_HIDDEN]"
        if 'mask_path' in r and len(str(r.get('mask_path', ''))) > 100:
            r['mask_path'] = "[BASE64_DATA_HIDDEN]"

    return {"success": True, "data": records}


# ── Record CRUD ──────────────────────────────────────────
@app.get("/record/{record_id}")
async def get_record(record_id: int):
    record = db.get_record_by_id(record_id)
    if not record:
        raise HTTPException(status_code=404, detail="Không tìm thấy bản ghi.")
    return {"success": True, "data": record}


@app.delete("/record/{record_id}")
async def delete_record(record_id: int):
    deleted = db.delete_record(record_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Không tìm thấy bản ghi để xóa.")
    return {"success": True, "message": f"Đã xóa bản ghi #{record_id}"}



from fastapi.responses import FileResponse

# ── Admin Operations (Backup / Cleanup) ──────────────────
@app.get("/admin/backup-db")
async def backup_db():
    if db is None:
        raise HTTPException(status_code=503, detail="Database chưa khởi tạo.")
    
    db_path = db.db_path
    if not os.path.exists(db_path):
        raise HTTPException(status_code=404, detail="File DB không tồn tại.")
        
    return FileResponse(path=db_path, filename="patients_backup.db", media_type="application/octet-stream")

@app.delete("/admin/clear-db")
async def clear_db():
    if db is None:
        raise HTTPException(status_code=503, detail="Database chưa khởi tạo.")
    
    with db_lock:
        try:
            conn = db._get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM patients")
            count = cursor.fetchone()[0]
            
            cursor.execute("DELETE FROM patients")
            # Reset auto-increment
            cursor.execute("DELETE FROM sqlite_sequence WHERE name='patients'")
            conn.commit()
            conn.close()
            return {"success": True, "deleted_count": count}
        except Exception as e:
            logger.error(f"Lỗi khi xóa DB: {e}")
            raise HTTPException(status_code=500, detail=str(e))

# ── Main ─────────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api:app", host="127.0.0.1", port=8000, reload=True)
