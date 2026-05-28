import os
import urllib.request
import logging
import csv
import glob

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

def fetch_normal_images():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    normal_dir = os.path.join(base_dir, 'sample_dataset', 'normal')

    os.makedirs(normal_dir, exist_ok=True)

    # 1. Xóa ảnh dummy cũ
    dummy_files = glob.glob(os.path.join(normal_dir, 'dummy_*.jpg'))
    for f in dummy_files:
        try:
            os.remove(f)
            logging.info(f"Đã xóa ảnh nhiễu dummy: {os.path.basename(f)}")
        except:
            pass

    # 2. Tải metadata.csv từ IEEE dataset
    csv_url = "https://raw.githubusercontent.com/ieee8023/covid-chestxray-dataset/master/metadata.csv"
    csv_path = os.path.join(base_dir, "metadata.csv")
    
    try:
        urllib.request.urlretrieve(csv_url, csv_path)
    except Exception as e:
        logging.error(f"Lỗi tải CSV: {e}")
        return

    # 3. Lọc ra 3 ảnh thuộc loại Normal hoặc Pneumonia (không phải Effusion)
    images_to_download = []
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            finding = row.get('finding', '').lower()
            if 'effusion' not in finding and 'covid' not in finding:
                images_to_download.append(row.get('filename'))
            if len(images_to_download) >= 4:
                break
                
    # 4. Tải các ảnh này về thư mục normal
    base_img_url = "https://raw.githubusercontent.com/ieee8023/covid-chestxray-dataset/master/images/"
    for i, filename in enumerate(images_to_download):
        if not filename: continue
        url = base_img_url + filename
        file_path = os.path.join(normal_dir, f"real_normal_{i}.jpg")
        try:
            urllib.request.urlretrieve(url, file_path)
            logging.info(f"Đã tải thành công ảnh Normal: {filename}")
        except Exception as e:
            logging.error(f"Lỗi tải {filename}: {e}")

if __name__ == "__main__":
    fetch_normal_images()
