from __future__ import annotations

import shutil
import zipfile
from pathlib import Path


PPTX = Path(r"D:\My\XAI\Doc\XAI_Medical_Sieu_Vip_PPT_Master.pptx")
BACKUP = PPTX.with_name("XAI_Medical_Sieu_Vip_PPT_Master.before_ground_truth_update.pptx")
OUTPUT = PPTX.with_name("XAI_Medical_Sieu_Vip_PPT_Master_GroundTruth.pptx")


REPLACEMENTS = {
    # Slide 3
    "Dataset y khoa": "4 dataset huấn luyện",
    "Nguồn ảnh X-quang lớn giúp học đặc trưng tổn thương phổi.": "NIH ChestX-ray14, CheXpert, MIMIC-CXR và PadChest trong weights all.",
    "ChestX-ray14, CheXpert, MIMIC-CXR": "NIH 112.120 + CheXpert 224.316 + MIMIC 377.110 + PadChest ~160.000",
    "CNN y sinh": "DenseNet-121 XRV",
    "DenseNet và 3D CNN chứng minh hiệu quả trong nhận diện ảnh y tế.": "Backbone dùng xrv.models.DenseNet weights densenet121-res224-all.",
    "CheXNet, TorchXRayVisi": "TorchXRayVision pretrained",
    "o": "o",
    "n": "n",
    "Giải thích XAI": "Grad-CAM",
    "Grad-CAM biến đặc trưng sâu thành bản đồ vùng ảnh quan trọng.": "Target layer denseblock4, giữ 1024 kênh đặc trưng và tránh lỗi ReLU inplace ở norm5.",
    "Grad-CAM, Grad-CAM++": "denseblock4, 1024 channels",
    "Khoảng trống sản phẩm": "Fine-tune Effusion",
    "Nhiều nghiên cứu dừng ở mô hình; sản phẩm này tích hợp API, giao diện và báo cáo.": "Nạp pleural_effusion_model_best.pth và extract riêng nhãn Effusion từ mô hình multi-label.",
    "Triển khai end-to-end": "Không dùng AI thứ hai",
    "Sản phẩm kết hợp học sâu, XAI và workflow báo cáo để tăng tính kiểm chứng trong hỗ trợ chẩn đoán.": "Hệ thống giữ backbone đã huấn luyện, chỉ hậu xử lý heatmap bằng OpenCV/alpha blending và xuất báo cáo.",
    # Slide 4
    "Resize về kích thước chuẩn, chuyển grayscale/RGB theo mô hình, chuẩn hóa pixel.": "Bắt buộc grayscale, resize bằng XRayResizer(224), normalize bằng xrv.datasets.normalize(img_np, 255).",
    "Mục tiêu: giảm sai khác do nguồn ảnh và máy chụp.": "Pixel từ [0,255] được đưa về chuẩn X-ray [-1024,1024], không dùng mean/std ImageNet.",
    "Thiết kế train, validation, test giúp kiểm tra khả năng tổng quát.": "Kịch bản fine-tuning Cloud: 70% Train, 10% Validation, 20% Test.",
    "Theo dõi accuracy, recall, F1-score, AUC.": "Hold-out test set Kaggle: Accuracy 81.46%, AUC 0.87.",
    # Slide 5
    "Kiến trúc nhận dạng ảnh X-quang": "DenseNet-121 và classifier Effusion",
    "224 x 224": "Grayscale 224 x 224",
    "Block 1": "Stem",
    "Block 2": "Dense blocks",
    "Block 3": "denseblock4",
    "softmax / sigmoid": "Sigmoid output",
    "CNN học đặc trưng hình thái từ ảnh, sau đó lớp phân loại đưa ra xác suất bệnh lý. Feature maps cuối được dùng cho Grad-CAM.": "Pretrained DenseNet-121 được fine-tune classifier Effusion bằng AdamW, LR 1e-4, 5 epochs, BCELoss và AMP GradScaler.",
    # Slide 8
    "Bộ chỉ số đánh giá chất lượng mô hình": "Kết quả fine-tuning và ngưỡng vận hành",
    "0.88": "81.46%",
    "0.91": "0.87",
    "Recall": "AUC",
    "0.87": "6.82%",
    "F1-score": "Threshold",
    "So sánh chỉ số mô hình": "Số liệu đã xác nhận",
    "Acc": "Acc",
    "F1": "Thr",
    "88%": "81.46%",
    "91%": "0.87",
    "87%": "0.0682",
    "90%": "Kaggle",
    "Cách đọc kết quả": "Cách đọc đúng",
    "Recall cao giúp giảm bỏ sót ca nghi ngờ. F1-score cân bằng giữa phát hiện và cảnh báo sai.": "Threshold 0.0682 được chọn bằng Youden's J trên ROC để giảm bỏ sót bệnh, không dùng 50% mặc định.",
    "Các số liệu trình bày theo dạng minh họa kiểm thử sản phẩm; khi huấn luyện thực tế cần báo cáo kèm tập test độc lập.": "Accuracy 81.46% và AUC 0.87 đo trên hold-out test set khi fine-tuning Cloud, không phải bộ 50 ảnh COVID/Pneumonia.",
    "Metric đề xuất: Accuracy, Recall, Precision, F1-score, AUC, IoU hoặc mAP cho bài toán định vị vùng tổn thương.": "Chưa có TP/FP/TN/FN export cứng; nếu cần nghiệm thu học thuật phải bổ sung confusion matrix và ROC artifact.",
}


NOTE_REPLACEMENTS = {
    "Slide 3": "Slide 3 cập nhật: mô hình gốc dùng weights densenet121-res224-all, học từ NIH ChestX-ray14, CheXpert, MIMIC-CXR và PadChest; tổng quy mô hơn 800.000 ảnh X-quang.",
    "Slide 4": "Slide 4 cập nhật: input bắt buộc grayscale, resize XRayResizer(224), normalize theo chuẩn TorchXRayVision; split fine-tuning Cloud là 70/10/20.",
    "Slide 5": "Slide 5 cập nhật: backbone DenseNet-121 pretrained, fine-tune classifier Effusion bằng AdamW LR 1e-4, 5 epochs, BCELoss và AMP GradScaler.",
    "Slide 8": "Slide 8 cập nhật: Accuracy 81.46%, AUC 0.87, threshold vận hành 0.0682 theo Youden's J; chưa có confusion matrix export cứng.",
}


def replace_all(text: str, replacements: dict[str, str]) -> str:
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text


def main() -> None:
    if not PPTX.exists():
        raise FileNotFoundError(PPTX)
    if not BACKUP.exists():
        shutil.copy2(PPTX, BACKUP)

    with zipfile.ZipFile(PPTX, "r") as zin, zipfile.ZipFile(OUTPUT, "w", zipfile.ZIP_DEFLATED) as zout:
        for item in zin.infolist():
            data = zin.read(item.filename)
            if item.filename.startswith("ppt/slides/slide") and item.filename.endswith(".xml"):
                text = data.decode("utf-8")
                text = replace_all(text, REPLACEMENTS)
                data = text.encode("utf-8")
            elif item.filename.startswith("ppt/notesSlides/notesSlide") and item.filename.endswith(".xml"):
                text = data.decode("utf-8")
                text = replace_all(text, NOTE_REPLACEMENTS)
                data = text.encode("utf-8")
            zout.writestr(item, data)

    print(f"Updated: {OUTPUT}")
    print(f"Backup: {BACKUP}")


if __name__ == "__main__":
    main()
