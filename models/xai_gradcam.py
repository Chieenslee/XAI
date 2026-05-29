import torch
import cv2
import numpy as np
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")

class XAIExplainer:
    def __init__(self, model):
        self.model = model
        self.model.eval()
        # Không dùng norm5 vì kết quả norm5 bị đưa vào ReLU(inplace=True) gây lỗi autograd của PyTorch
        # Dùng denseblock4 là an toàn nhất (vẫn giữ được toàn bộ 1024 kênh đặc trưng)
        self.target_layer = self.model.features.denseblock4
        self.feature_map = None
        self.gradient = None
        self._fwd_handle = None
        self._bwd_handle = None
        self._register_hooks()
        logging.info("Khoi tao module XAI: Grad-CAM thu cong san sang.")

    def _register_hooks(self):
        def forward_hook(module, input, output):
            self.feature_map = output.detach()
        def backward_hook(module, grad_input, grad_output):
            self.gradient = grad_output[0].detach()
        
        self._fwd_handle = self.target_layer.register_forward_hook(forward_hook)
        self._bwd_handle = self.target_layer.register_full_backward_hook(backward_hook)

    def remove_hooks(self):
        if self._fwd_handle:
            self._fwd_handle.remove()
        if self._bwd_handle:
            self._bwd_handle.remove()

    def generate_heatmap(self, input_tensor, original_image_np, target_category=None):
        input_req = input_tensor.detach().requires_grad_(True)
        self.model.zero_grad()
        output = self.model(input_req)
        
        if target_category is None:
            target_category = output.argmax(dim=1).item()
            
        score = output[0, target_category]
        score.backward()
        
        if self.gradient is None or self.feature_map is None:
            raise RuntimeError("Hook không bắt được gradient hoặc feature map. Kiểm tra lại target_layer.")
            
        weights = self.gradient.mean(dim=[2, 3], keepdim=True)
        cam = (weights * self.feature_map).sum(dim=1, keepdim=True)
        cam = torch.relu(cam)
        cam_np = cam.squeeze().cpu().numpy()
        
        cam_min, cam_max = cam_np.min(), cam_np.max()
        if cam_max - cam_min > 1e-8:
            cam_np = (cam_np - cam_min) / (cam_max - cam_min)
        else:
            cam_np = np.zeros_like(cam_np)
            logging.warning("CAM toàn 0 — layer có thể không hoạt động hoặc hook bị lỗi.")
            
        h, w = original_image_np.shape[:2]
        cam_resized = cv2.resize(cam_np, (w, h), interpolation=cv2.INTER_CUBIC)
        
        if original_image_np.dtype in (np.float32, np.float64):
            orig_uint8 = np.clip(original_image_np * 255, 0, 255).astype(np.uint8)
        else:
            orig_uint8 = original_image_np.astype(np.uint8)
            
        heatmap_bgr = cv2.applyColorMap(np.uint8(255 * cam_resized), cv2.COLORMAP_JET)
        heatmap_rgb = cv2.cvtColor(heatmap_bgr, cv2.COLOR_BGR2RGB)
        overlay = cv2.addWeighted(orig_uint8, 0.5, heatmap_rgb, 0.5, 0)
        
        # Khoanh vùng nóng (heatmap >= 0.6) bằng viền đen
        threshold = 0.6
        mask = (cam_resized >= threshold).astype(np.uint8) * 255
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cv2.drawContours(overlay, contours, -1, (10, 10, 10), 4, lineType=cv2.LINE_AA)
        
        # Phân tích vị trí (Textual Explanation)
        explanation = "Không phát hiện dấu hiệu bất thường rõ rệt."
        if target_category == 1 or len(contours) > 0: # Effusion
            # Tìm vùng có diện tích lớn nhất
            if contours:
                c = max(contours, key=cv2.contourArea)
                M = cv2.moments(c)
                if M["m00"] != 0:
                    cX = int(M["m10"] / M["m00"])
                    cY = int(M["m01"] / M["m00"])
                    
                    # Phân loại vị trí dựa trên tọa độ tâm (Chia ảnh làm 9 vùng 3x3)
                    # Tuy nhiên với phổi, quan tâm: Trái/Phải và Trên/Dưới
                    vertical_pos = "vùng đỉnh phổi"
                    if cY > h * 2 / 3:
                        vertical_pos = "vùng góc sườn hoành (đáy phổi)"
                    elif cY > h / 3:
                        vertical_pos = "vùng giữa phế trường"
                        
                    horizontal_pos = "trái" if cX > w / 2 else "phải" # X-quang: bên phải ảnh là phổi trái
                    
                    area_ratio = (cv2.contourArea(c) / (w * h)) * 100
                    
                    explanation = f"Mô hình phân tích ảnh phát hiện vùng cản quang bất thường tập trung tại {vertical_pos} bên {horizontal_pos}. Diện tích vùng tổn thương chiếm khoảng {area_ratio:.1f}% vùng khảo sát. Đặc điểm này phù hợp với dấu hiệu tụ dịch màng phổi."
        
        logging.info("Sinh Heatmap thanh cong!")
        return overlay, explanation

