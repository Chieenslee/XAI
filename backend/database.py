import sqlite3
import os
from datetime import datetime

class DatabaseHelper:
    def __init__(self, db_path="data/patients.db"):
        self.db_path = db_path
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.init_db()

    def init_db(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Tạo bảng lưu trữ hồ sơ bệnh nhân và lịch sử chẩn đoán
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS patient_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_name TEXT,
            clinical_notes TEXT,
            image_path TEXT,
            mask_path TEXT,
            heatmap_path TEXT,
            prediction_label TEXT,
            confidence_score REAL,
            timestamp DATETIME
        )
        ''')
        
        conn.commit()
        conn.close()

    def insert_record(self, patient_name, clinical_notes, image_path, mask_path, heatmap_path, prediction_label, confidence_score):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        cursor.execute('''
        INSERT INTO patient_records (patient_name, clinical_notes, image_path, mask_path, heatmap_path, prediction_label, confidence_score, timestamp)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (patient_name, clinical_notes, image_path, mask_path, heatmap_path, prediction_label, confidence_score, timestamp))
        
        record_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return record_id

    def get_all_records(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM patient_records ORDER BY timestamp DESC')
        records = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        return records

if __name__ == "__main__":
    db = DatabaseHelper()
    print("Khởi tạo Database thành công.")
