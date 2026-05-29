import torch
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import accuracy_score, recall_score, f1_score, confusion_matrix
from sklearn.manifold import TSNE
import os

# --- Phân loại (Classification Metrics) ---
def calculate_classification_metrics(y_true, y_pred, y_prob):
    """
    y_true: nhãn thực tế
    y_pred: nhãn dự đoán (0 hoặc 1)
    y_prob: xác suất dự đoán (để vẽ biểu đồ nếu cần)
    """
    acc = accuracy_score(y_true, y_pred)
    recall = recall_score(y_true, y_pred)
    f1 = f1_score(y_true, y_pred)
    return acc, recall, f1

def plot_confusion_matrix(y_true, y_pred, output_path="data/visualizations/confusion_matrix.png"):
    cm = confusion_matrix(y_true, y_pred)
    plt.figure(figsize=(6, 5))
    sns.heatmap(cm, annot=True, fmt="d", cmap="Blues", xticklabels=["Normal", "Effusion"], yticklabels=["Normal", "Effusion"])
    plt.title("Ma trận nhầm lẫn (Confusion Matrix)")
    plt.xlabel("Nhãn dự đoán")
    plt.ylabel("Nhãn thực tế")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Đã lưu Confusion Matrix tại {output_path}")

# --- Phân đoạn (Segmentation Metrics) ---
def calculate_iou(pred_mask, true_mask, threshold=0.5):
    """Tính Intersection over Union cho mảng 2D/3D (PyTorch Tensor)"""
    pred_mask = (pred_mask > threshold).float()
    intersection = (pred_mask * true_mask).sum()
    union = pred_mask.sum() + true_mask.sum() - intersection
    if union == 0:
        return 1.0 # Nếu cả hai đều rỗng thì IOU = 1
    return (intersection / union).item()

def calculate_map(pred_masks, true_masks):
    """Giả lập tính Mean Average Precision cho tập masks"""
    ious = []
    for p, t in zip(pred_masks, true_masks):
        ious.append(calculate_iou(p, t))
    return np.mean(ious)

# --- Trực quan hóa Đặc trưng (t-SNE) ---
def plot_tsne(features, labels, output_path="data/visualizations/tsne_plot.png"):
    """
    features: mảng Numpy chứa vector đặc trưng (N, D)
    labels: mảng Numpy chứa nhãn (N,)
    """
    # Nếu dữ liệu quá ít (ví dụ < 2), t-SNE sẽ báo lỗi perplexity
    perplexity = min(30, len(features) - 1)
    if perplexity < 1:
        print("Không đủ dữ liệu để vẽ t-SNE.")
        return
        
    tsne = TSNE(n_components=2, perplexity=perplexity, random_state=42)
    features_2d = tsne.fit_transform(features)
    
    plt.figure(figsize=(8, 6))
    colors = ['#2E7D32', '#FF6B6B']
    target_names = ['Normal', 'Effusion']
    
    for i, color, target_name in zip([0, 1], colors, target_names):
        plt.scatter(features_2d[labels == i, 0], features_2d[labels == i, 1], 
                    color=color, label=target_name, alpha=0.7)
                    
    plt.title("Trực quan hóa Đặc trưng (t-SNE)")
    plt.legend()
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Đã lưu t-SNE plot tại {output_path}")

# --- Hiệu suất Mô hình (Model Efficiency) ---
def calculate_model_efficiency(model, input_tensor, device='cpu'):
    """
    Đo lường độ phức tạp của mô hình: 
    - Số lượng tham số (Parameters)
    - Thời gian suy luận (Inference Time)
    - GFLOPs (Mô phỏng/Ước lượng cơ bản)
    """
    import time
    
    # 1. Tham số (Parameters)
    total_params = sum(p.numel() for p in model.parameters())
    trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
    
    # 2. Thời gian suy luận (Inference Time)
    model.eval()
    model.to(device)
    input_tensor = input_tensor.to(device)
    
    # Warm up
    for _ in range(5):
        with torch.no_grad():
            _ = model(input_tensor)
            
    # Đo thời gian
    start_time = time.time()
    num_runs = 50
    with torch.no_grad():
        for _ in range(num_runs):
            _ = model(input_tensor)
    end_time = time.time()
    
    inference_time_ms = ((end_time - start_time) / num_runs) * 1000
    
    return {
        "Total_Parameters": total_params,
        "Trainable_Parameters": trainable_params,
        "Inference_Time_ms": inference_time_ms
    }

if __name__ == "__main__":
    # Test nhanh các hàm
    print("Testing Metrics Module...")
    y_true = [0, 1, 1, 0, 1]
    y_pred = [0, 1, 0, 0, 1]
    y_prob = [0.1, 0.9, 0.4, 0.2, 0.8]
    
    acc, rec, f1 = calculate_classification_metrics(y_true, y_pred, y_prob)
    print(f"Accuracy: {acc:.2f}, Recall: {rec:.2f}, F1-Score: {f1:.2f}")
    plot_confusion_matrix(y_true, y_pred)
    
    # Fake features cho t-SNE
    fake_features = np.random.rand(50, 256)
    fake_labels = np.random.randint(0, 2, 50)
    plot_tsne(fake_features, fake_labels)
    
    # Test IoU
    pred = torch.rand(1, 1, 224, 224)
    true = torch.randint(0, 2, (1, 1, 224, 224)).float()
    print(f"Sample IoU: {calculate_iou(pred, true):.4f}")
