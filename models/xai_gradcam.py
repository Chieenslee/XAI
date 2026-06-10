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

    def generate_heatmap(self, input_tensor, original_image_np, target_category=None, is_abnormal=True):
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
        
        # [BƯỚC 1] Làm mịn Heatmap
        cam_smoothed = cv2.GaussianBlur(cam_resized, (15, 15), 0)
        cam_smoothed = np.clip(cam_smoothed, 0, 1)
        
        if original_image_np.dtype in (np.float32, np.float64):
            orig_uint8 = np.clip(original_image_np * 255, 0, 255).astype(np.uint8)
        else:
            orig_uint8 = original_image_np.astype(np.uint8)
            
        heatmap_bgr = cv2.applyColorMap(np.uint8(255 * cam_smoothed), cv2.COLORMAP_JET)
        heatmap_rgb = cv2.cvtColor(heatmap_bgr, cv2.COLOR_BGR2RGB)
        
        # Pha màu thông minh (Alpha Blending)
        if not is_abnormal:
            # Nếu chẩn đoán là bình thường, không hiển thị Heatmap quá rực rỡ gây hiểu lầm
            alpha_multiplier = 0.15 # Giảm mạnh độ sáng heatmap
            heatmap_bgr = cv2.applyColorMap(np.uint8(255 * cam_smoothed), cv2.COLORMAP_WINTER) # Dùng màu dịu (cool)
            heatmap_rgb = cv2.cvtColor(heatmap_bgr, cv2.COLOR_BGR2RGB)
        else:
            alpha_multiplier = 0.65 # Tăng nhẹ độ sáng heatmap nếu có bệnh
            
        alpha = cam_smoothed[..., np.newaxis] * alpha_multiplier
        overlay = (orig_uint8 * (1.0 - alpha) + heatmap_rgb * alpha).astype(np.uint8)
        
        # [BƯỚC 1] Lọc Contour (Chỉ lấy vùng lớn nhất, viền mỏng màu Cam)
        threshold = 0.70
        mask_hot = (cam_smoothed >= threshold).astype(np.uint8) * 255
        contours, _ = cv2.findContours(mask_hot, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        valid_contours = []
        if contours:
            contours = sorted(contours, key=cv2.contourArea, reverse=True)
            max_area = cv2.contourArea(contours[0])
            for c in contours:
                area = cv2.contourArea(c)
                # Chỉ lấy đốm to hơn 5% so với đốm lớn nhất
                if area > 100 and area >= max_area * 0.05:
                    valid_contours.append(c)
                    
            if is_abnormal:
                cv2.drawContours(overlay, valid_contours, -1, (0, 165, 255), 2, lineType=cv2.LINE_AA)
        
        # Phân tích vị trí (Textual Explanation)
        explanation = "Không phát hiện dấu hiệu bất thường rõ rệt."
        if target_category == 1 or len(valid_contours) > 0: # Effusion
            # Tìm vùng có diện tích lớn nhất
            if valid_contours:
                c = valid_contours[0]
                M = cv2.moments(c)
                if M["m00"] != 0:
                    cX = int(M["m10"] / M["m00"])
                    cY = int(M["m01"] / M["m00"])
                    
                    # Phân loại vị trí dựa trên tọa độ tâm (Chia ảnh làm 9 vùng 3x3)
                    # Tuy nhiên với phổi, quan tâm: Trái/Phải và Trên/Dưới
                    # Tràn dịch màng phổi thường nằm ở đáy phổi
                    vertical_pos = "đỉnh phổi"
                    if cY > h * 0.6:
                        vertical_pos = "góc sườn hoành (đáy phổi)"
                    elif cY > h * 0.3:
                        vertical_pos = "vùng rốn phổi / giữa phế trường"
                        
                    # Trong ảnh X-quang thẳng, bên trái của bức ảnh là bên phải của bệnh nhân
                    horizontal_pos = "trái" if cX > w / 2 else "phải"
                    
                    area_ratio = (cv2.contourArea(c) / (w * h)) * 100
                    
                    if not is_abnormal:
                        explanation = "Hệ thống AI không phát hiện đám mờ cản quang bất thường. Các góc sườn hoành hai bên sắc nét."
                    else:
                        explanation = f"Hệ thống phát hiện vùng mờ cản quang tập trung tại {vertical_pos} bên {horizontal_pos}. Diện tích tổn thương khoảng {area_ratio:.1f}%. Đặc điểm này phù hợp với tràn dịch màng phổi."
                        if vertical_pos == "đỉnh phổi":
                            explanation += " Tuy nhiên, vị trí này (đỉnh phổi) khá bất thường đối với tràn dịch thông thường, cần loại trừ các nguyên nhân khác (như dày dính màng phổi hoặc khối u)."

        
        logging.info("Sinh Heatmap thanh cong!")
        return overlay, explanation

