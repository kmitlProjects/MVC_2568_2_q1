"""
Database - จัดการการเชื่อมต่อและทำงานกับฐานข้อมูล SQLite
"""
import sqlite3
from config.settings import Config

class Database:
    """คลาสสำหรับจัดการการเชื่อมต่อฐานข้อมูล"""
    
    def __init__(self, db_name=None):
        self.db_name = db_name or Config.DATABASE_NAME
        
    def get_connection(self):
        """สร้างการเชื่อมต่อกับฐานข้อมูล"""
        return sqlite3.connect(self.db_name)
    
    def execute_query(self, query, params=()):
        """ประมวลผล query ที่เปลี่ยนแปลงข้อมูล (INSERT, UPDATE, DELETE)"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(query, params)
        conn.commit()
        conn.close()
        
    def fetch_all(self, query, params=()):
        """ดึงข้อมูลทั้งหมดจาก query"""
        conn = self.get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(query, params)
        results = cursor.fetchall()
        conn.close()
        return results
    
    def fetch_one(self, query, params=()):
        """ดึงข้อมูลหนึ่งแถวจาก query"""
        conn = self.get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(query, params)
        result = cursor.fetchone()
        conn.close()
        return result
