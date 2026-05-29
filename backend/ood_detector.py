import cv2
import numpy as np

class OODDetector:
    def __init__(self):
        """
        Out of Distribution (OOD) Detector cho ảnh X-quang.
        Trong thực tế, nên dùng một mô hình CNN nhỏ (VD: MobileNet) phân loại X-ray vs Natural Image.
        Để mô phỏng nhanh cho demo, chúng ta dùng Heuristic:
        - X-quang thường là ảnh xám (Grayscale). Nếu ảnh màu (sự chênh lệch giữa các kênh R, G, B lớn) 
          => Dễ là ảnh tự nhiên (OOD).
        """
        pass

    def is_ood(self, image_path: str, color_variance_threshold=15.0) -> bool:
        """
        Kiểm tra xem ảnh có phải là ảnh màu tự nhiên hay không.
        Trả về True nếu là OOD (Không phải X-quang), False nếu hợp lệ.
        """
        # Đọc ảnh màu (BGR)
        img = cv2.imread(image_path)
        if img is None:
            return True # Không đọc được cũng coi là không hợp lệ
            
        # Tính phương sai giữa 3 kênh màu B, G, R
        b, g, r = cv2.split(img)
        
        # Nếu là ảnh grayscale chuẩn (nhưng lưu RGB), thì B, G, R sẽ gần như giống hệt nhau
        # Tính độ lệch trung bình giữa các kênh
        diff_bg = np.mean(np.abs(b.astype(int) - g.astype(int)))
        diff_gr = np.mean(np.abs(g.astype(int) - r.astype(int)))
        diff_rb = np.mean(np.abs(r.astype(int) - b.astype(int)))
        
        avg_diff = (diff_bg + diff_gr + diff_rb) / 3.0
        
        if avg_diff > color_variance_threshold:
            return True # Là ảnh màu -> OOD
            
        return False

if __name__ == "__main__":
    detector = OODDetector()
    # Test
    # Nếu truyền ảnh màu vào sẽ ra True, ảnh xám ra False.
    print("OOD Detector initialized.")
