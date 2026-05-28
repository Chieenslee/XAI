import os
import urllib.request
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

def download_real_github_images():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    effusion_dir = os.path.join(base_dir, 'sample_dataset', 'effusion')

    os.makedirs(effusion_dir, exist_ok=True)

    # Lấy dữ liệu ảnh lâm sàng thật trực tiếp từ Github (không bị chặn)
    base_url = "https://raw.githubusercontent.com/ieee8023/covid-chestxray-dataset/master/images/"
    images = ["000001-266.jpg", "000001-272.jpg", "000002-268.jpg", "000003-285.jpg"]

    logging.info("Đang tải ảnh X-quang THẬT từ Kho Y tế Github (Raw Githubusercontent)...")
    for filename in images:
        file_path = os.path.join(effusion_dir, f"real_{filename}")
        try:
            url = base_url + filename
            urllib.request.urlretrieve(url, file_path)
            logging.info(f"Đã tải thành công ảnh thật: {filename}")
        except Exception as e:
            logging.error(f"Lỗi tải {filename}: {e}")

if __name__ == "__main__":
    download_real_github_images()
