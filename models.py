"""
Model - กำหนดโครงสร้างฐานข้อมูลสำหรับระบบติดตามข่าวลือ
"""
import sqlite3
from datetime import datetime

class Database:
    def __init__(self, db_name='rumor_tracking.db'):
        self.db_name = db_name
        
    def get_connection(self):
        return sqlite3.connect(self.db_name)
    
    def execute_query(self, query, params=()):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(query, params)
        conn.commit()
        conn.close()
        
    def fetch_all(self, query, params=()):
        conn = self.get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(query, params)
        results = cursor.fetchall()
        conn.close()
        return results
    
    def fetch_one(self, query, params=()):
        conn = self.get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(query, params)
        result = cursor.fetchone()
        conn.close()
        return result


class RumourModel:
    """Model สำหรับข่าวลือ"""
    
    @staticmethod
    def calculate_credibility_score(rumour_id):
        """คำนวณคะแนนความน่าเชื่อถือจากข้อมูลจริง
        สูตร: (จำนวนผู้รายงานว่าน่าเชื่อถือ ÷ จำนวนผู้รายงานทั้งหมด) × 100
        """
        db = Database()
        # นับจำนวนรายงานทั้งหมด
        query_total = "SELECT COUNT(*) as total FROM Report WHERE rumour_id = ?"
        total_result = db.fetch_one(query_total, (rumour_id,))
        total_reports = total_result['total'] if total_result else 0
        
        if total_reports == 0:
            return 0.0
        
        # นับจำนวนรายงานที่เป็น "น่าเชื่อถือ"
        query_credible = "SELECT COUNT(*) as credible FROM Report WHERE rumour_id = ? AND report_type = 'น่าเชื่อถือ'"
        credible_result = db.fetch_one(query_credible, (rumour_id,))
        credible_reports = credible_result['credible'] if credible_result else 0
        
        # คำนวณคะแนน
        score = (credible_reports / total_reports) * 100
        return round(score, 2)
    
    @staticmethod
    def update_credibility_score(rumour_id):
        """อัปเดตคะแนนความน่าเชื่อถือในฐานข้อมูล"""
        score = RumourModel.calculate_credibility_score(rumour_id)
        db = Database()
        query = "UPDATE Rumour SET credibility_score = ? WHERE rumour_id = ?"
        db.execute_query(query, (score, rumour_id))
    
    @staticmethod
    def get_all_rumours():
        """ดึงข่าวลือทั้งหมด เรียงตามจำนวนรายงาน (ความร้อนแรง)"""
        db = Database()
        query = """
            SELECT r.*, COUNT(rep.report_id) as report_count
            FROM Rumour r
            LEFT JOIN Report rep ON r.rumour_id = rep.rumour_id
            GROUP BY r.rumour_id
            ORDER BY report_count DESC, r.created_date DESC
        """
        return db.fetch_all(query)
    
    @staticmethod
    def get_rumour_by_id(rumour_id):
        """ดึงข่าวลือตาม ID"""
        db = Database()
        query = """
            SELECT r.*, u.name as verifier_name, u.verifier_code
            FROM Rumour r
            LEFT JOIN Users u ON r.verified_by = u.user_id
            WHERE r.rumour_id = ?
        """
        return db.fetch_one(query, (rumour_id,))
    
    @staticmethod
    def get_rumour_report_count(rumour_id):
        """นับจำนวนรายงานของข่าวลือ"""
        db = Database()
        query = "SELECT COUNT(*) as count FROM Report WHERE rumour_id = ?"
        result = db.fetch_one(query, (rumour_id,))
        return result['count'] if result else 0
    
    @staticmethod
    def update_status_to_panic(rumour_id):
        """เปลี่ยนสถานะเป็น panic"""
        db = Database()
        query = "UPDATE Rumour SET status = 'panic' WHERE rumour_id = ?"
        db.execute_query(query, (rumour_id,))
    
    @staticmethod
    def verify_rumour(rumour_id, verification_result, verified_by):
        """ตรวจสอบและยืนยันข่าวลือโดยผู้ตรวจสอบ"""
        db = Database()
        query = """
            UPDATE Rumour 
            SET is_verified = 1, 
                verification_result = ?,
                verified_by = ?
            WHERE rumour_id = ?
        """
        db.execute_query(query, (verification_result, verified_by, rumour_id))
    
    @staticmethod
    def get_panic_rumours():
        """ดึงข่าวลือที่เข้าสู่สถานะ panic"""
        db = Database()
        query = """
            SELECT r.*, COUNT(rep.report_id) as report_count
            FROM Rumour r
            LEFT JOIN Report rep ON r.rumour_id = rep.rumour_id
            WHERE r.status = 'panic'
            GROUP BY r.rumour_id
            ORDER BY report_count DESC
        """
        return db.fetch_all(query)


class ReportModel:
    """Model สำหรับการรายงานข่าว"""
    
    @staticmethod
    def create_report(user_id, rumour_id, report_type):
        """สร้างรายงานใหม่"""
        db = Database()
        query = """
            INSERT INTO Report (user_id, rumour_id, report_date, report_type)
            VALUES (?, ?, ?, ?)
        """
        report_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        db.execute_query(query, (user_id, rumour_id, report_date, report_type))
    
    @staticmethod
    def check_duplicate_report(user_id, rumour_id):
        """ตรวจสอบว่าผู้ใช้เคยรายงานข่าวนี้แล้วหรือไม่"""
        db = Database()
        query = "SELECT COUNT(*) as count FROM Report WHERE user_id = ? AND rumour_id = ?"
        result = db.fetch_one(query, (user_id, rumour_id))
        return result['count'] > 0
    
    @staticmethod
    def get_reports_by_rumour(rumour_id):
        """ดึงรายงานทั้งหมดของข่าวลือ พร้อมรหัสผู้ใช้"""
        db = Database()
        query = """
            SELECT rep.*, u.username, u.name
            FROM Report rep
            JOIN Users u ON rep.user_id = u.user_id
            WHERE rep.rumour_id = ?
            ORDER BY rep.report_date DESC
        """
        return db.fetch_all(query, (rumour_id,))


class UserModel:
    """Model สำหรับผู้ใช้งาน"""
    
    @staticmethod
    def get_all_users():
        """ดึงผู้ใช้ทั้งหมด"""
        db = Database()
        query = "SELECT * FROM Users ORDER BY user_id"
        return db.fetch_all(query)
    
    @staticmethod
    def get_verifiers():
        """ดึงข้อมูลผู้ตรวจสอบทั้งหมด"""
        db = Database()
        query = "SELECT * FROM Users WHERE verifier_code IS NOT NULL ORDER BY username"
        return db.fetch_all(query)
    
    @staticmethod
    def get_user_by_id(user_id):
        """ดึงผู้ใช้ตาม ID"""
        db = Database()
        query = "SELECT * FROM Users WHERE user_id = ?"
        return db.fetch_one(query, (user_id,))
