# Đề xuất Nâng cấp Hệ thống XAI Medical (v9 & Beyond)

Dựa trên kiến trúc hiện tại, để hệ thống đạt đến mức độ **Production-Ready cho Bệnh viện (Clinical Grade)**, dưới đây là các đề xuất nâng cấp chia theo từng mảng:

## 1. Nâng cấp Core AI & XAI (Trí tuệ Nhân tạo)

### 1.1. Cải thiện Mô hình Cốt lõi
- **Chuyển đổi kiến trúc**: Hiện tại đang dùng `DenseNet-121`. Có thể thử nghiệm nghiệm các kiến trúc ViT (Vision Transformer) hoặc `ConvNeXt` vốn đang là SOTA cho phân loại ảnh Y khoa hiện tại.
- **Multimodal AI**: Tích hợp thêm module xử lý ngôn ngữ tự nhiên (BioBERT/PhoBERT). Kết hợp ảnh X-quang và Text (Ghi chú lâm sàng) tạo ra một Embedding không gian chung (như kiến trúc CLIP), để ra quyết định chính xác hơn.

### 1.2. Nâng cấp XAI (Explainable AI)
- **Hạn chế của Grad-CAM**: Bản đồ nhiệt hiện tại (Grad-CAM) đôi khi bị nhiễu do độ phân giải heatmap thấp (feature map của layer cuối nhỏ). 
- **Đề xuất**: Nâng cấp lên **Grad-CAM++** hoặc **HiResCAM** để khoanh vùng vị trí tổn thương màng phổi rõ nét hơn. Tích hợp thêm **LIME** (Local Interpretable Model-agnostic Explanations) để bác sĩ có thêm góc nhìn thứ hai.

## 2. Nâng cấp Backend (Hạ tầng Server)

### 2.1. Quản lý Cache & Database
- Hiện tại `DatabaseHelper` có vẻ đang sử dụng SQLite (file tĩnh) hoặc in-memory.
- **Đề xuất**: Chuyển sang sử dụng **PostgreSQL** để đảm bảo tính toàn vẹn dữ liệu cho bệnh án. Tích hợp **Redis Cache** cho các kết quả ảnh chuẩn đoán (giảm tải inference các ảnh trùng lặp).

### 2.2. Xử lý Bất đồng bộ Cao cấp
- Endpoint `/predict_batch` hiện tại đang dùng ThreadPoolExecutor. Nếu xử lý hàng nghìn ảnh, RAM sẽ bị quá tải (do load tensor vào CUDA nhiều lần).
- **Đề xuất**: Tích hợp **Celery + RabbitMQ / Redis** làm message broker. Backend sẽ đẩy job vào queue và trả về `job_id`, Frontend sẽ call API polling hoặc dùng **WebSockets** để theo dõi tiến trình xử lý real-time mà không làm chết Server.

## 3. Nâng cấp Giao diện (Frontend & UX)

### 3.1. Tính năng Dành cho Bác sĩ (Clinical Tools)
- **Công cụ đo lường**: Thêm công cụ vẽ (bounding box / polygon) và thước đo (ruler) trực tiếp trên ảnh X-quang để bác sĩ đo kích thước vùng tràn dịch trên Frontend.
- **Lưu trữ & Phê duyệt**: Bác sĩ có thể chỉnh sửa kết quả của AI (ví dụ: AI báo bệnh nhưng bác sĩ thấy bình thường), lưu lại trạng thái `Reviewed` để sau này retraining mô hình bằng Dữ liệu do chính chuyên gia gán nhãn lại (Active Learning).

### 3.2. Responsive & PWA
- Hệ thống cần được tối ưu hiển thị cho máy tính bảng (iPad) – thiết bị bác sĩ thường dùng đi buồng bệnh. 
- Đóng gói frontend dưới dạng **PWA (Progressive Web App)** để cài đặt trực tiếp lên thiết bị di động.

## 4. Bảo mật Y tế (Security & Compliance)
- **Chuẩn HIPAA / GDPR**: Bệnh án X-quang cần ẩn danh hóa thông tin (Anonymization). Cần có script gỡ bỏ metadata DICOM (nếu support DICOM sau này) trước khi lưu trữ vào DB.
- **Cơ chế Phân quyền (RBAC)**: Tích hợp OAuth2/JWT phân biệt các role: Admin (Quản trị hệ thống), Doctor (Xem/Review chẩn đoán), AI Researcher (Tải data đã gán nhãn).
