import re

with open('backend/api.py', 'r', encoding='utf-8') as f:
    content = f.read()

old_logic = """        try:
            conn = db._get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM patients")
            count = cursor.fetchone()[0]
            
            cursor.execute("DELETE FROM patients")
            # Reset auto-increment
            cursor.execute("DELETE FROM sqlite_sequence WHERE name='patients'")
            conn.commit()
            conn.close()
            return {"success": True, "deleted_count": count}
        except Exception as e:"""

new_logic = """        try:
            conn = db._connect()
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) as count FROM patient_records")
            count = cursor.fetchone()['count']
            
            cursor.execute("DELETE FROM patient_records")
            # Reset auto-increment
            cursor.execute("DELETE FROM sqlite_sequence WHERE name='patient_records'")
            conn.commit()
            conn.close()
            return {"success": True, "deleted_count": count}
        except Exception as e:"""

content = content.replace(old_logic, new_logic)

with open('backend/api.py', 'w', encoding='utf-8') as f:
    f.write(content)
