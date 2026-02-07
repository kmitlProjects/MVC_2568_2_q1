"""
ReportModel - Model สำหรับจัดการข้อมูลการรายงานข่าวลือ
"""
from datetime import datetime
from .database import Database


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
