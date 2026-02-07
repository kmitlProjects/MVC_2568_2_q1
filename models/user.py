"""
UserModel - Model สำหรับจัดการข้อมูลผู้ใช้
"""
from .database import Database


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
