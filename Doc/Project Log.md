# Nhật ký Phát triển Dự án (Project Log)

File này sẽ ghi lại chi tiết các bước đã thực hiện, quyết định kỹ thuật và kết quả đạt được sau mỗi phiên làm việc.

## Ngày 28/05/2026

- **Hành động 1:** Nhận yêu cầu từ Bác sĩ/Khách hàng về dự án phát hiện Tràn dịch màng phổi sử dụng XAI. Đã soạn thảo bản kế hoạch chi tiết bao gồm 4 giai đoạn, tầm nhìn và hướng giải quyết vấn đề "hộp đen" của AI.
- **Quyết định Kỹ thuật 1:** Đã thống nhất sử dụng hoàn toàn hệ sinh thái Python chạy local.
- **Hành động 2:** Nhận yêu cầu nâng cấp giao diện UI/UX chuyên nghiệp.
- **Hành động 3:** Khởi tạo sơ đồ công việc chi tiết.
- **Hành động 4:** Tạo cấu trúc thư mục dự án (`backend`, `frontend`, `data/sample_dataset`, `models`). Khởi tạo kho lưu trữ Git.
- **Hành động 5:** Tạo file `requirements.txt` bao gồm `fastapi`, `streamlit`, `torch`, `grad-cam`, v.v.
- **Hành động 6:** Viết script Python sinh ảnh giả lập (dummy dataset) gồm 5 ảnh Bình thường và 5 ảnh Tràn dịch để test pipeline. Đã chạy thành công.
- **Hành động 7:** Chuyển file nhật ký sang vị trí `d:\My\XAI\Doc\Project Log.md` theo yêu cầu của người dùng.
- **Hành động 8:** Xây dựng module tiền xử lý ảnh chuyên dụng cho Y khoa tại `backend/preprocess.py`. Sử dụng thuật toán `CLAHE` (Contrast Limited Adaptive Histogram Equalization) qua thư viện OpenCV để tăng cường làm rõ cấu trúc xương và màng phổi, chuẩn bị đầu vào kích thước 224x224 và đưa về phân phối chuẩn (Normalize) cho Transfer Learning.
- **Hành động 9:** Hủy cài đặt thư viện ở môi trường Python global (theo nhắc nhở của người dùng) để đảm bảo chuẩn mực. Khởi tạo môi trường ảo bằng `python -m venv venv`.
- **Hành động 10:** Chạy lại lệnh cài đặt thư viện (`venv\Scripts\pip install -r requirements.txt`) vào trong thư mục môi trường ảo.
- **Hành động 11:** Thiết kế và code giao diện UI/UX chuyên nghiệp tại `frontend/app.py` bằng Streamlit kết hợp Custom CSS. Giao diện bao gồm:
  - Sidebar Menu điều hướng với các icon y khoa.
  - Dashboard thống kê chuyên nghiệp (hiển thị % chính xác, lượt chẩn đoán).
  - Khu vực tải ảnh với Layout Side-by-side (Ảnh X-quang gốc vs XAI Heatmap).
  - Tích hợp style Dark/Light Mode.
- **Hành động 12:** Khởi tạo kiến trúc **Core AI** tại `models/core_model.py`. Sử dụng `DenseNet121` của PyTorch làm Backbone (vì cấu trúc DenseBlock giúp truyền luồng gradient tốt cho ảnh y khoa). Thay đổi layer phân loại cuối (Classifier) thành 1 nốt Binary Classification, sẵn sàng cho bài toán Tràn dịch màng phổi.
- **Hành động 13:** Viết script huấn luyện `backend/train.py`. Đã cài cắm kỹ thuật **Mixed Precision (AMP)** qua `torch.cuda.amp.GradScaler` để tối ưu VRAM cho card RTX 3050, kết hợp Loss Function `BCEWithLogitsLoss` và thuật toán tối ưu `AdamW`.
- **Hành động 14:** Bắt đầu **Giai đoạn 4 (XAI)**. Khởi tạo module XAI tại `models/xai_gradcam.py` sử dụng thư viện `pytorch-grad-cam`. Target layer được chọn là feature cuối cùng của DenseNet121 để khoanh vùng vị trí tràn dịch màng phổi chính xác nhất. Đã viết xong hàm sinh Heatmap và chèn đè lên ảnh gốc.
- **Hành động 15:** Hoàn thiện **Giai đoạn 5 (Cuối cùng)**. 
  - Khởi tạo FastAPI server tại `backend/api.py`. API hỗ trợ load Core AI và XAI Explainer trực tiếp lên RAM lúc startup để tăng tốc dự đoán. Endpoint `/predict` cho phép nhận ảnh X-quang, chạy xử lý và trả về JSON chứa mức độ tin cậy và ảnh Heatmap (chuẩn Base64).
  - Cập nhật UI tại `frontend/app.py`: Kết nối nút "Phân tích ảnh với AI" gọi trực tiếp sang FastAPI qua `requests`. Giao diện tự động xử lý Base64 thành ảnh trực quan và hiển thị side-by-side.

**--- DỰ ÁN HOÀN TẤT VÀ SẴN SÀNG SỬ DỤNG ---**
