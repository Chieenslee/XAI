import cv2
import numpy as np
import logging

logger = logging.getLogger("XAI.OOD")

class OODDetector:
    """
    Out of Distribution (OOD) Detector nâng cấp cho ảnh X-quang.
    
    Bộ lọc 4 tầng:
      1. Kích thước quá nhỏ (< 100x100)
      2. Tỷ lệ khung hình bất thường (> 4:1)
      3. Ảnh đồng nhất (entropy quá thấp = 1 màu)
      4. Ảnh màu tự nhiên (color variance cao) hoặc nền trắng (brightness cao)
    """

    def __init__(self):
        pass

    def is_ood(self, image_path: str, color_variance_threshold=15.0) -> bool:
        """
        Kiểm tra xem ảnh có phải là ảnh X-quang hợp lệ hay không.
        Trả về True nếu là OOD (Không hợp lệ), False nếu OK.
        """
        img = cv2.imread(image_path)
        if img is None:
            logger.warning(f"OOD: Không đọc được file {image_path}")
            return True

        h, w = img.shape[:2]

        # --- Tầng 1: Kích thước quá nhỏ ---
        if h < 100 or w < 100:
            logger.info(f"OOD REJECT: Ảnh quá nhỏ ({w}x{h}px). Yêu cầu tối thiểu 100x100.")
            return True

        # --- Tầng 2: Tỷ lệ khung hình bất thường ---
        aspect_ratio = max(w, h) / max(min(w, h), 1)
        if aspect_ratio > 4.0:
            logger.info(f"OOD REJECT: Tỷ lệ khung hình bất thường ({aspect_ratio:.1f}:1).")
            return True

        # --- Tầng 3: Ảnh đồng nhất (entropy thấp) ---
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        hist = cv2.calcHist([gray], [0], None, [256], [0, 256])
        hist = hist.flatten() / hist.sum()
        # Loại bỏ các bin = 0 trước khi tính entropy
        hist_nonzero = hist[hist > 0]
        entropy = -np.sum(hist_nonzero * np.log2(hist_nonzero))

        if entropy < 1.5:
            logger.info(f"OOD REJECT: Entropy quá thấp ({entropy:.2f}). Ảnh gần như đồng nhất 1 màu.")
            return True

        # --- Tầng 4a: Ảnh màu tự nhiên ---
        b, g, r = cv2.split(img)
        diff_bg = np.mean(np.abs(b.astype(int) - g.astype(int)))
        diff_gr = np.mean(np.abs(g.astype(int) - r.astype(int)))
        diff_rb = np.mean(np.abs(r.astype(int) - b.astype(int)))
        avg_diff = (diff_bg + diff_gr + diff_rb) / 3.0

        if avg_diff > color_variance_threshold:
            logger.info(f"OOD REJECT: Ảnh màu (avg_diff={avg_diff:.1f} > {color_variance_threshold}).")
            return True

        # --- Tầng 4b: Nền quá sáng (tài liệu / nền trắng) ---
        mean_brightness = np.mean(gray)
        if mean_brightness > 180:
            logger.info(f"OOD REJECT: Nền quá sáng (brightness={mean_brightness:.0f}).")
            return True

        logger.debug(f"OOD PASS: {image_path} (entropy={entropy:.2f}, color_diff={avg_diff:.1f}, brightness={mean_brightness:.0f})")
        return False


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    detector = OODDetector()
    print("OOD Detector v2.0 initialized — 4-layer filtering active.")
