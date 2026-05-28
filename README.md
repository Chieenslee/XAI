# XAI Medical - Pleural Effusion Diagnosis (v8)

Hệ thống Chẩn đoán Tràn dịch Màng phổi tích hợp Trí tuệ Nhân tạo Có thể Giải thích được (Explainable AI - XAI).

## 🚀 Tính năng nổi bật
- **Core AI Mạnh mẽ (v8):** Xây dựng dựa trên kiến trúc `DenseNet-121` của TorchXRayVision, fine-tuned chuyên sâu cho bệnh lý Tràn dịch Màng phổi.
- **Độ chính xác cao:** Độ chính xác (Accuracy) đạt **81.46%**, AUC-ROC đạt **0.8732** trên tập Test Set.
- **Bản đồ nhiệt XAI (Grad-CAM):** Áp dụng XAI Grad-CAM cho phép "nhìn xuyên thấu" tư duy của AI. Bản đồ nhiệt làm nổi bật chính xác các vùng góc sườn hoành - dấu hiệu đặc trưng của tràn dịch màng phổi, giúp bác sĩ dễ dàng kiểm chứng.
- **Giao diện React Hiện đại:** UI siêu mượt mà với hiệu ứng quét Laser (Scan), hiển thị tỉ lệ tin cậy trực quan bằng Gauge, và ghép mượt mà Heatmap lên X-quang gốc giữ nguyên tỉ lệ (aspect ratio).
- **Kiến trúc Tối ưu:** Khắc phục triệt để các lỗi `Double Sigmoid`, loại bỏ hook dư thừa, tự động tìm Optimal Threshold (0.0682) thay vì hardcode.

## 🛠 Cài đặt & Khởi chạy

1. Cài đặt các thư viện cần thiết:
   ```bash
   pip install -r requirements.txt
   cd web && npm install
   ```
2. Khởi chạy toàn bộ hệ thống (Bao gồm Frontend và Backend):
   Sử dụng cấu hình `▶ Run Full System (XAI Medical)` trong VS Code (`launch.json`) hoặc chạy lệnh:
   ```bash
   python run.py
   ```
   Hệ thống sẽ tự động bật FastAPI ở cổng `8000` và React Vite ở cổng `5173`.

## 📝 Nhật ký thay đổi (Changelog)

### v8 - Production Ready (Current)
- Sửa lỗi Double Sigmoid: Dùng `BCELoss` thay vì `BCEWithLogitsLoss`.
- Tối ưu hoá Gradient: Xử lý triệt để lỗi Inplace ReLU bằng cách hook vào `denseblock4`.
- Tự động tìm Threshold tối ưu: 0.0682.
- UI/UX Fix: Fix lỗi méo tỉ lệ Heatmap, khắc phục lỗi chọn file 2 lần.
