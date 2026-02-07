"""
Database - สร้างฐานข้อมูลและข้อมูลตัวอย่าง
"""
import sqlite3
import random
from datetime import datetime, timedelta

def init_database():
    """สร้างตารางในฐานข้อมูล"""
    conn = sqlite3.connect('rumor_tracking.db')
    cursor = conn.cursor()
    
    # สร้างตาราง Users
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            name TEXT NOT NULL,
            role TEXT NOT NULL CHECK(role IN ('ผู้ใช้ทั่วไป', 'ผู้ตรวจสอบ')),
            verifier_code TEXT
        )
    ''')
    
    # สร้างตาราง Rumour
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Rumour (
            rumour_id INTEGER PRIMARY KEY CHECK(rumour_id >= 10000000 AND rumour_id <= 99999999),
            title TEXT NOT NULL,
            content TEXT,
            source TEXT NOT NULL,
            created_date TEXT NOT NULL,
            credibility_score REAL DEFAULT 50.0,
            status TEXT NOT NULL DEFAULT 'ปกติ' CHECK(status IN ('ปกติ', 'panic')),
            is_verified INTEGER DEFAULT 0,
            verification_result TEXT,
            verified_by INTEGER,
            FOREIGN KEY (verified_by) REFERENCES Users(user_id)
        )
    ''')
    
    # สร้างตาราง Report
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Report (
            report_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            rumour_id INTEGER NOT NULL,
            report_date TEXT NOT NULL,
            report_type TEXT NOT NULL CHECK(report_type IN ('บิดเบือน', 'ปลุกปั่น', 'ข้อมูลเท็จ', 'น่าเชื่อถือ')),
            FOREIGN KEY (user_id) REFERENCES Users(user_id),
            FOREIGN KEY (rumour_id) REFERENCES Rumour(rumour_id),
            UNIQUE(user_id, rumour_id)
        )
    ''')
    
    conn.commit()
    conn.close()
    print("✓ สร้างตารางฐานข้อมูลสำเร็จ")


def insert_sample_data():
    """เพิ่มข้อมูลตัวอย่าง"""
    conn = sqlite3.connect('rumor_tracking.db')
    cursor = conn.cursor()
    
    # ตรวจสอบว่ามีข้อมูลอยู่แล้วหรือไม่
    cursor.execute("SELECT COUNT(*) FROM Users")
    if cursor.fetchone()[0] > 0:
        print("✓ มีข้อมูลในฐานข้อมูลอยู่แล้ว")
        conn.close()
        return
    
    # เพิ่มผู้ใช้งาน 13 คน (10 ผู้ใช้ทั่วไป + 3 ผู้ตรวจสอบ)
    users = [
        ('user001', 'นายสมชาย ใจดี', 'ผู้ใช้ทั่วไป', None),
        ('user002', 'นางสาวสมหญิง รักดี', 'ผู้ใช้ทั่วไป', None),
        ('user003', 'นายวิชัย เรียนดี', 'ผู้ใช้ทั่วไป', None),
        ('user004', 'นางสาวมานี ทำดี', 'ผู้ใช้ทั่วไป', None),
        ('user005', 'นายประเสริฐ สุขใจ', 'ผู้ใช้ทั่วไป', None),
        ('user006', 'นางสาวพิมพ์ รักษา', 'ผู้ใช้ทั่วไป', None),
        ('user007', 'นายสุรชัย มั่นคง', 'ผู้ใช้ทั่วไป', None),
        ('user008', 'นายธนากร ศรีสุข', 'ผู้ใช้ทั่วไป', None),
        ('user009', 'นางสาวกัลยา อารีย์', 'ผู้ใช้ทั่วไป', None),
        ('user010', 'นายอนุชา วงศ์ใหญ่', 'ผู้ใช้ทั่วไป', None),
        ('verifier001', 'Dr. สมชาย วิทยาศาสตร์', 'ผู้ตรวจสอบ', 'V001'),
        ('verifier002', 'ผศ. สมหญิง เทคโนโลยี', 'ผู้ตรวจสอบ', 'V002'),
        ('verifier003', 'รศ. ดร. วิชัย คอมพิวเตอร์', 'ผู้ตรวจสอบ', 'V003')
    ]
    cursor.executemany('INSERT INTO Users (username, name, role, verifier_code) VALUES (?, ?, ?, ?)', users)
    
    # เพิ่มข่าวลือ 8 ข่าว (เพิ่ม content)
    base_date = datetime.now()
    rumours = [
        (12345678, 'มีการแจกเงินฟรี 10,000 บาท ผ่านแอพพลิเคชั่น', 
         'มีข่าวแพร่ระบาดว่ารัฐบาลจะแจกเงิน 10,000 บาทให้ทุกคนผ่านแอพพลิเคชั่นใหม่ โดยให้กรอกข้อมูลส่วนตัวและเลขบัญชี อย่างไรก็ตาม ยังไม่มีการยืนยันจากหน่วยงานราชการใดๆ',
         'Facebook', (base_date - timedelta(days=5)).strftime('%Y-%m-%d %H:%M:%S'), 30.0, 'ปกติ', 0, None, None),
        
        (23456789, 'พบยาวิเศษรักษามะเร็งหายใน 3 วัน', 
         'มีการโฆษณายาสมุนไพรที่อ้างว่าสามารถรักษามะเร็งได้ภายใน 3 วัน โดยไม่ต้องเข้ารับการรักษาทางการแพทย์ มีการขายในราคาแพงมาก แต่ไม่มีหลักฐานทางวิทยาศาสตร์รองรับ',
         'LINE กลุ่ม', (base_date - timedelta(days=4)).strftime('%Y-%m-%d %H:%M:%S'), 20.0, 'panic', 0, None, None),
        
        (34567890, 'รัฐบาลจะเก็บภาษีเงินในบัญชีธนาคารทุกคน 50%', 
         'มีข้อความแพร่สะพัดว่ารัฐบาลจะออกกฎหมายใหม่เก็บภาษีเงินฝากธนาคารทุกบัญชีในอัตรา 50% เพื่อแก้ปัญหาหนี้สาธารณะ ทำให้ประชาชนตื่นตระหนกถอนเงินออกจากธนาคารจำนวนมาก',
         'Twitter', (base_date - timedelta(days=3)).strftime('%Y-%m-%d %H:%M:%S'), 15.0, 'panic', 0, None, None),
        
        (45678901, 'น้ำประปาในกรุงเทพฯ มีสารพิษ อันตรายต่อสุขภาพ', 
         'มีรายงานว่าน้ำประปาในพื้นที่กรุงเทพฯและปริมณฑลปนเปื้อนสารเคมีอันตราย ทำให้ไม่สามารถดื่มหรือใช้ประกอบอาหารได้ แนะนำให้ซื้อน้ำดื่มมาใช้แทน',
         'TikTok', (base_date - timedelta(days=2)).strftime('%Y-%m-%d %H:%M:%S'), 25.0, 'ปกติ', 0, None, None),
        
        (56789012, 'พายุใหญ่จะเข้าไทย ทำให้เกิดมหาอุทกภัยทั่วประเทศ', 
         'กรมอุตุนิยมวิทยาเตือนว่าจะมีพายุใหญ่เข้าไทยในสัปดาห์หน้า คาดว่าจะทำให้เกิดน้ำท่วมใหญ่ทั่วประเทศ แนะนำให้ประชาชนเตรียมพร้อมอพยพ',
         'Facebook', (base_date - timedelta(days=1)).strftime('%Y-%m-%d %H:%M:%S'), 35.0, 'ปกติ', 0, None, None),
        
        (67890123, 'มีการปล่อยไวรัสใหม่ที่อันตรายกว่า COVID-19', 
         'มีรายงานว่ามีการระบาดของไวรัสสายพันธุ์ใหม่ที่มีอัตราการติดต่อและอัตราการเสียชีวิตสูงกว่า COVID-19 หลายเท่า กระจายตัวอย่างรวดเร็วในหลายประเทศ หลังจากตรวจสอบพบว่าเป็นข้อมูลเท็จ',
         'LINE', (base_date - timedelta(hours=12)).strftime('%Y-%m-%d %H:%M:%S'), 10.0, 'panic', 1, 'ข้อมูลเท็จ', 3),
        
        (78901234, 'ธนาคารใหญ่จะล้มละลาย ให้รีบถอนเงินด่วน', 
         'มีข่าวลือว่าธนาคารชั้นนำของประเทศกำลังจะล้มละลาย เนื่องจากปัญหาสภาพคล่อง แนะนำให้ลูกค้ารีบถอนเงินออกทั้งหมดก่อนที่จะเกิดปัญหา',
         'WhatsApp', (base_date - timedelta(hours=6)).strftime('%Y-%m-%d %H:%M:%S'), 18.0, 'ปกติ', 0, None, None),
        
        (89012345, 'อาหารยี่ห้อดังมีสารก่อมะเร็ง ห้ามกินโดยเด็ดขาด', 
         'พบว่าผลิตภัณฑ์อาหารยี่ห้อดังที่ขายในห้างสรรพสินค้ามีส่วนผสมของสารก่อมะเร็ง FDA ได้ออกคำเตือนให้หยุดบริโภคทันที',
         'Facebook', base_date.strftime('%Y-%m-%d %H:%M:%S'), 28.0, 'ปกติ', 0, None, None),
        
        (90123456, 'โครงการปลูกต้นไม้ให้ฟรีทั่วประเทศ', 
         'มีโครงการแจกต้นไม้ฟรีให้ทุกคนทั่วประเทศ โดยอ้างว่าเป็นโครงการของรัฐบาลช่วยประชาชน แต่ต้องกรอกข้อมูลส่วนตัวและหมายเลขบัตรประชาชน',
         'LINE กลุ่ม', (base_date - timedelta(hours=3)).strftime('%Y-%m-%d %H:%M:%S'), 22.0, 'ปกติ', 0, None, None),
        
        (10234567, 'พบทองคำวิเศษในป่าสามารถรักษาโรคทุกชนิด', 
         'มีการเผยแพร่ว่ามีการค้นพบทองคำวิเศษในป่าที่สามารถรักษาโรคได้ทุกชนิด โดยไม่ต้องไปโรงพยาบาล',
         'Facebook', (base_date - timedelta(hours=8)).strftime('%Y-%m-%d %H:%M:%S'), 35.0, 'ปกติ', 0, None, None)
    ]
    cursor.executemany('''
        INSERT INTO Rumour (rumour_id, title, content, source, created_date, credibility_score, status, is_verified, verification_result, verified_by)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', rumours)
    
    # เพิ่มรายงานให้บางข่าวมีจำนวนมากจนเป็น panic (>= 5 ครั้ง)
    reports = []
    report_types = ['บิดเบือน', 'ปลุกปั่น', 'ข้อมูลเท็จ', 'น่าเชื่อถือ']
    
    # ข่าว 23456789 - มีรายงาน 7 รายงาน (panic)
    for i in range(1, 8):
        reports.append((i, 23456789, (base_date - timedelta(days=4, hours=i)).strftime('%Y-%m-%d %H:%M:%S'), 
                       random.choice(report_types)))
    
    # ข่าว 34567890 - มีรายงาน 6 รายงาน (panic)
    for i in range(1, 7):
        reports.append((i, 34567890, (base_date - timedelta(days=3, hours=i)).strftime('%Y-%m-%d %H:%M:%S'), 
                       random.choice(report_types)))
    
    # ข่าว 67890123 - มีรายงาน 5 รายงาน (panic + verified)
    for i in range(1, 6):
        reports.append((i, 67890123, (base_date - timedelta(hours=12+i)).strftime('%Y-%m-%d %H:%M:%S'), 
                       random.choice(report_types)))
    
    # ข่าว 12345678 - มีรายงาน 3 รายงาน (ปกติ - ยังไม่ถึง threshold) - ผสมทั้งน่าเชื่อถือและไม่น่าเชื่อถือ
    reports.append((1, 12345678, (base_date - timedelta(days=5, hours=1)).strftime('%Y-%m-%d %H:%M:%S'), 'ข้อมูลเท็จ'))
    reports.append((2, 12345678, (base_date - timedelta(days=5, hours=2)).strftime('%Y-%m-%d %H:%M:%S'), 'น่าเชื่อถือ'))
    reports.append((3, 12345678, (base_date - timedelta(days=5, hours=3)).strftime('%Y-%m-%d %H:%M:%S'), 'บิดเบือน'))
    
    # ข่าว 45678901 - มีรายงาน 2 รายงาน (ปกติ)
    for i in range(1, 3):
        reports.append((i, 45678901, (base_date - timedelta(days=2, hours=i)).strftime('%Y-%m-%d %H:%M:%S'), 
                       random.choice(report_types)))
    
    # ข่าว 89012345 - มีรายงาน 1 รายงาน (ปกติ)
    reports.append((1, 89012345, base_date.strftime('%Y-%m-%d %H:%M:%S'), 'ข้อมูลเท็จ'))
    
    cursor.executemany('''
        INSERT INTO Report (user_id, rumour_id, report_date, report_type)
        VALUES (?, ?, ?, ?)
    ''', reports)
    
    conn.commit()
    conn.close()
    print("✓ เพิ่มข้อมูลตัวอย่างสำเร็จ")
    print("  - ผู้ใช้งาน: 13 คน (10 ผู้ใช้ทั่วไป + 3 ผู้ตรวจสอบ)")
    print("  - ข่าวลือ: 10 ข่าว")
    print("  - มีข่าวที่เข้าสู่ panic: 3 ข่าว (รายงาน >= 5 ครั้ง)")
    print("  - มีข่าวที่ถูกตรวจสอบแล้ว: 1 ข่าว")


if __name__ == '__main__':
    print("กำลังสร้างฐานข้อมูล...")
    init_database()
    insert_sample_data()
    print("\n✓ เสร็จสิ้น!")
