import os
import csv
import random

def generate_multimodal_dataset(dataset_dir="data/sample_dataset", output_csv="data/multimodal_dataset.csv"):
    normal_notes = [
        "Bệnh nhân tỉnh, tiếp xúc tốt. Phổi thông khí đều hai bên, không nghe rales.",
        "Hình ảnh X-quang tim phổi thẳng trong giới hạn bình thường. Góc sườn hoành hai bên nhọn, sáng.",
        "Bóng tim không to. Hai trường phổi sáng, không thấy tổn thương khu trú.",
        "Bệnh nhân đến khám sức khỏe định kỳ. Hiện tại không ho, không khó thở. Hình ảnh X-quang bình thường.",
        "Màng phổi hai bên không thấy dày, không thấy mức nước mức hơi. Nhu mô phổi bình thường."
    ]
    
    effusion_notes = [
        "Bệnh nhân có triệu chứng khó thở khi nằm. X-quang cho thấy mờ đồng đều ở đáy phổi, góc sườn hoành tù.",
        "Nghi ngờ tràn dịch màng phổi lượng vừa. Bệnh nhân than đau tức ngực trái, ho khan nhiều về đêm.",
        "Phổi có rales ẩm ở đáy. Hình ảnh X-quang: mờ góc sườn hoành, đường cong Ellis Damoiseau dương tính.",
        "Tràn dịch màng phổi phải. Bệnh nhân sốt nhẹ, khó thở tăng dần trong 3 ngày nay.",
        "Mờ toàn bộ 1/3 dưới phế trường phải, mất góc sườn hoành. Theo dõi tràn dịch màng phổi do viêm."
    ]
    
    with open(output_csv, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['filename', 'label', 'clinical_note'])
        
        classes = ['normal', 'effusion']
        for cls in classes:
            cls_dir = os.path.join(dataset_dir, cls)
            if not os.path.exists(cls_dir): continue
            
            for img_name in os.listdir(cls_dir):
                note = random.choice(normal_notes) if cls == 'normal' else random.choice(effusion_notes)
                label = 0 if cls == 'normal' else 1
                writer.writerow([img_name, label, note])
                
    print(f"Đã tạo file dữ liệu đa phương thức (Ảnh + Text) tại: {output_csv}")

if __name__ == "__main__":
    generate_multimodal_dataset()
