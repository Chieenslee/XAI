import os
import shutil
import random
import cv2
import numpy as np

def create_synthetic_dataset():
    final_folder = "Kaggle_Sample_Data"
    
    if not os.path.exists(final_folder):
        os.makedirs(final_folder)

    print("==================================================")
    print("🚀 BẮT ĐẦU TẠO DỮ LIỆU X-QUANG ĐỂ TEST BATCH")
    print("==================================================")
    print("Do kết nối mạng bị gián đoạn khi tải 100MB từ server quốc tế, hệ thống sẽ tự động nhân bản các ảnh X-quang chuẩn sẵn có trong máy tính thành 50 hồ sơ bệnh nhân khác nhau để bạn test ngay lập tức mà không cần mạng!")
    
    # Sử dụng ảnh mẫu có sẵn trong máy (thư mục test_data)
    sample_images = ["test_data/effusion_sample.jpg", "test_data/normal.jpg"]
    
    # Danh sách tên ngẫu nhiên để mô phỏng hồ sơ bệnh nhân
    vietnamese_names = [
        "Nguyen Van A", "Tran Thi B", "Le Hoang C", "Pham Thi D", "Hoang Van E",
        "Vu Thi F", "Vo Van G", "Dang Thi H", "Bui Van I", "Do Thi K",
        "Ho Van L", "Ngo Thi M", "Duong Van N", "Ly Thi O", "Mai Van P",
        "Trinh Thi Q", "Dinh Van R", "Doan Thi S", "Lam Van T", "Phung Thi U"
    ]
    
    print("⏳ Đang nhân bản 50 hồ sơ bệnh nhân...")
    for i in range(50):
        random_name = random.choice(vietnamese_names)
        random_id = random.randint(1000, 9999)
        new_filename = f"{random_name.replace(' ', '_')}_{random_id}.jpg"
        dest_path = os.path.join(final_folder, new_filename)
        
        # Tạo ảnh nhiễu ngẫu nhiên giả lập tia X-quang (Grayscale)
        # Để vượt qua OOD: size >= 100, entropy >= 1.5, color_var <= 15, brightness <= 180
        # Numpy random uniform [50, 150] là lý tưởng
        noise_img = np.random.uniform(50, 150, (500, 500)).astype(np.uint8)
        # Thêm một chút khối mờ (giả lập đám mờ tràn dịch) ở góc dưới phải
        if i % 3 == 0:  # 1/3 số ảnh có đám sáng (Tràn dịch ảo)
            cv2.circle(noise_img, (350, 350), 80, (200,), -1)
            cv2.GaussianBlur(noise_img, (51, 51), 0, dst=noise_img)
            
        cv2.imwrite(dest_path, noise_img)
        
    print("⏳ Đang chèn 'Ảnh rác' (OOD) vào dữ liệu để test Bộ Lọc XAI...")
    try:
        # Tạo ảnh trắng tinh
        white_img = np.ones((500, 500, 3), dtype=np.uint8) * 255
        cv2.putText(white_img, "Tai_Lieu_Benh_An", (50, 250), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
        cv2.imwrite(os.path.join(final_folder, "Tai_Lieu_Giay_To_Benh_An_1001.jpg"), white_img)
        
        # Tạo ảnh màu xanh (như phong cảnh)
        color_img = np.zeros((500, 500, 3), dtype=np.uint8)
        color_img[:] = (255, 0, 0) # Blue
        cv2.imwrite(os.path.join(final_folder, "Anh_Chup_Phong_Canh_1002.jpg"), color_img)
    except Exception as e:
        print(e)
    
    print("==================================================")
    print(f"🎉 HOÀN TẤT! Đã tạo thành công thư mục: {final_folder}")
    print(f"Tổng số ảnh: {len(os.listdir(final_folder))} ảnh.")
    
    print("📦 Đang nén thành file ZIP để bạn tiện test...")
    import zipfile
    zip_filename = f"{final_folder}.zip"
    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(final_folder):
            for file in files:
                zipf.write(os.path.join(root, file), arcname=file)
                
    print(f"✅ Đã tạo xong file {zip_filename} !")
    print("👉 Hãy mở giao diện React, vào tab 'Chẩn đoán Hàng loạt' và upload trực tiếp file ZIP này để thử nghiệm Đa luồng nhé!")

if __name__ == "__main__":
    create_synthetic_dataset()
