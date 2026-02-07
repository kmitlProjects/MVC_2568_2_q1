"""
Config - การตั้งค่าระบบ
"""

class Config:
    """การตั้งค่าพื้นฐานของระบบ"""
    # Database
    DATABASE_NAME = 'rumor_tracking.db'
    
    # Flask
    SECRET_KEY = 'rumor_tracking_secret_key_2568'
    DEBUG = True
    
    # Business Rules
    PANIC_THRESHOLD = 5  # จำนวนรายงานขั้นต่ำที่ทำให้เป็น PANIC
    
    # Server
    HOST = '127.0.0.1'
    PORT = 5000
