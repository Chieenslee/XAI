import sqlite3
import os
from datetime import datetime

class DatabaseHelper:
    def __init__(self, db_path="data/patients.db"):
        self.db_path = db_path
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.init_db()

    def _connect(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def init_db(self):
        conn = self._connect()
        cursor = conn.cursor()
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
        conn = self._connect()
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
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM patient_records ORDER BY timestamp DESC')
        records = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return records

    def get_record_by_id(self, record_id):
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM patient_records WHERE id = ?', (record_id,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None

    def delete_record(self, record_id):
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM patient_records WHERE id = ?', (record_id,))
        deleted = cursor.rowcount
        conn.commit()
        conn.close()
        return deleted > 0

    def get_records_paginated(self, page=1, per_page=20):
        conn = self._connect()
        cursor = conn.cursor()
        offset = (page - 1) * per_page

        cursor.execute('SELECT COUNT(*) as total FROM patient_records')
        total = cursor.fetchone()['total']

        cursor.execute('SELECT * FROM patient_records ORDER BY timestamp DESC LIMIT ? OFFSET ?', (per_page, offset))
        records = [dict(row) for row in cursor.fetchall()]
        conn.close()

        return {
            "records": records,
            "total": total,
            "page": page,
            "per_page": per_page,
            "total_pages": (total + per_page - 1) // per_page
        }

    def get_statistics(self):
        conn = self._connect()
        cursor = conn.cursor()

        cursor.execute('SELECT COUNT(*) as total FROM patient_records')
        total = cursor.fetchone()['total']

        cursor.execute("SELECT COUNT(*) as cnt FROM patient_records WHERE prediction_label LIKE '%Tràn dịch%' OR prediction_label LIKE '%Effusion%'")
        effusion = cursor.fetchone()['cnt']

        cursor.execute("SELECT COUNT(*) as cnt FROM patient_records WHERE prediction_label LIKE '%Bình thường%' OR prediction_label LIKE '%Normal%'")
        normal = cursor.fetchone()['cnt']

        cursor.execute("SELECT AVG(confidence_score) as avg_conf FROM patient_records WHERE confidence_score IS NOT NULL")
        row = cursor.fetchone()
        avg_confidence = row['avg_conf'] if row['avg_conf'] else 0.0

        # Lấy 5 bản ghi gần nhất
        cursor.execute('SELECT id, patient_name, prediction_label, confidence_score, timestamp FROM patient_records ORDER BY timestamp DESC LIMIT 5')
        recent = [dict(r) for r in cursor.fetchall()]

        conn.close()
        return {
            "total_records": total,
            "total_effusion": effusion,
            "total_normal": normal,
            "avg_confidence": round(avg_confidence, 2),
            "recent_records": recent
        }


if __name__ == "__main__":
    db = DatabaseHelper()
    print("Database v2.0 initialized — pagination + statistics active.")
    stats = db.get_statistics()
    print(f"Stats: {stats}")
