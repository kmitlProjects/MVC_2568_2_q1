# 🏗️ MVC Architecture Explanation
## Model-View-Controller Pattern Implementation

โปรเจกต์นี้ใช้ MVC Pattern อย่างเคร่งครัดและแยกชัดเจน

---

## 📊 สถาปัตยกรรม MVC

```
┌────────────────────────────────────────────────────┐
│                   USER (Browser)                    │
└─────────────────┬──────────────────────────────────┘
                  │
                  ▼
┌────────────────────────────────────────────────────┐
│              VIEW (templates/*.html)                │
│  - index.html      (หน้ารวมข่าวลือ)               │
│  - detail.html     (หน้ารายละเอียด)                │
│  - summary.html    (หน้าสรุปผล)                    │
│                                                      │
│  📝 หน้าที่: แสดงผล UI และรับ Input จากผู้ใช้     │
└─────────────────┬──────────────────────────────────┘
                  │
                  ▼
┌────────────────────────────────────────────────────┐
│              CONTROLLER (app.py)                    │
│                                                      │
│  Routes:                                             │
│  @app.route('/')           → index()                │
│  @app.route('/detail/<id>') → detail()              │
│  @app.route('/summary')    → summary()              │
│  @app.route('/report/<id>') → report_rumour()       │
│                                                      │
│  📝 หน้าที่:                                        │
│  - รับ Request จาก View                             │
│  - ตรวจสอบ Business Rules                           │
│  - เรียก Model เพื่อ CRUD                          │
│  - ส่งข้อมูลกลับไปยัง View                         │
└─────────────────┬──────────────────────────────────┘
                  │
                  ▼
┌────────────────────────────────────────────────────┐
│               MODEL (models.py)                     │
│                                                      │
│  Classes:                                            │
│  - Database        (Connection Management)          │
│  - RumourModel     (ข่าวลือ CRUD)                  │
│  - ReportModel     (รายงาน CRUD)                   │
│  - UserModel       (ผู้ใช้ CRUD)                   │
│                                                      │
│  📝 หน้าที่:                                        │
│  - จัดการข้อมูลกับ Database                        │
│  - Business Logic ที่เกี่ยวกับข้อมูล              │
│  - ไม่มี UI Logic เลย                              │
└─────────────────┬──────────────────────────────────┘
                  │
                  ▼
┌────────────────────────────────────────────────────┐
│           DATABASE (rumor_tracking.db)              │
│                    SQLite                            │
│                                                      │
│  Tables:                                             │
│  - Rumour   (ข่าวลือ)                              │
│  - Report   (การรายงาน)                            │
│  - Users    (ผู้ใช้งาน)                            │
└────────────────────────────────────────────────────┘
```

---

## 🔄 Data Flow Example: การรายงานข่าวลือ

### 1. User Action (VIEW)
```html
<!-- detail.html -->
<form method="POST" action="/report/12345678">
    <select name="user_id">...</select>
    <select name="report_type">...</select>
    <button type="submit">รายงานข่าวลือนี้</button>
</form>
```

### 2. Controller Processing (CONTROLLER)
```python
# app.py
@app.route('/report/<int:rumour_id>', methods=['POST'])
def report_rumour(rumour_id):
    # รับข้อมูลจาก Form
    user_id = request.form.get('user_id', type=int)
    report_type = request.form.get('report_type')
    
    # ตรวจสอบ Business Rule: ข่าวถูกตรวจสอบแล้วหรือไม่?
    rumour = RumourModel.get_rumour_by_id(rumour_id)
    if rumour['is_verified']:
        flash('ข่าวนี้ตรวจสอบแล้ว ไม่สามารถรายงานได้')
        return redirect(url_for('detail', rumour_id=rumour_id))
    
    # ตรวจสอบ Business Rule: ผู้ใช้เคยรายงานแล้วหรือไม่?
    if ReportModel.check_duplicate_report(user_id, rumour_id):
        flash('คุณเคยรายงานข่าวนี้แล้ว')
        return redirect(url_for('detail', rumour_id=rumour_id))
    
    # เรียก Model เพื่อบันทึกข้อมูล
    ReportModel.create_report(user_id, rumour_id, report_type)
    
    # ตรวจสอบ Business Rule: ถึง threshold panic หรือไม่?
    report_count = RumourModel.get_rumour_report_count(rumour_id)
    if report_count >= PANIC_THRESHOLD:
        RumourModel.update_status_to_panic(rumour_id)
    
    # Redirect กลับไป View
    return redirect(url_for('detail', rumour_id=rumour_id))
```

### 3. Model Operations (MODEL)
```python
# models.py
class ReportModel:
    @staticmethod
    def create_report(user_id, rumour_id, report_type):
        db = Database()
        query = """
            INSERT INTO Report (user_id, rumour_id, report_date, report_type)
            VALUES (?, ?, ?, ?)
        """
        report_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        db.execute_query(query, (user_id, rumour_id, report_date, report_type))
    
    @staticmethod
    def check_duplicate_report(user_id, rumour_id):
        db = Database()
        query = "SELECT COUNT(*) as count FROM Report WHERE user_id = ? AND rumour_id = ?"
        result = db.fetch_one(query, (user_id, rumour_id))
        return result['count'] > 0
```

### 4. Database Operation (DATABASE)
```sql
-- ฐานข้อมูล SQLite
INSERT INTO Report (user_id, rumour_id, report_date, report_type)
VALUES (1, 12345678, '2026-02-07 11:30:00', 'ข้อมูลเท็จ');

-- ตรวจสอบจำนวนรายงาน
SELECT COUNT(*) FROM Report WHERE user_id = 1 AND rumour_id = 12345678;
```

---

## ✅ ข้อดีของ MVC Pattern ในโปรเจกต์นี้

### 1. Separation of Concerns
- **Model**: จัดการข้อมูลเท่านั้น ไม่เกี่ยวกับ UI
- **View**: แสดงผลเท่านั้น ไม่มี Business Logic
- **Controller**: ประสานงานระหว่าง Model และ View

### 2. Code Reusability
```python
# Model สามารถใช้ซ้ำได้หลาย Controller
rumours = RumourModel.get_all_rumours()  # ใช้ในหน้า index
panic_rumours = RumourModel.get_panic_rumours()  # ใช้ในหน้า summary
```

### 3. Easy Testing
```python
# สามารถ Test Model แยกจาก View/Controller
def test_duplicate_report():
    # Test Business Logic โดยตรง
    result = ReportModel.check_duplicate_report(1, 12345678)
    assert result == True
```

### 4. Maintainability
- เปลี่ยน UI → แก้ View เท่านั้น
- เปลี่ยน Business Logic → แก้ Controller เท่านั้น
- เปลี่ยน Database → แก้ Model เท่านั้น

### 5. Scalability
- เพิ่ม View ใหม่ได้ง่าย (เช่น API JSON)
- เพิ่ม Model ใหม่ได้ง่าย (เช่น CommentModel)
- เพิ่ม Controller ใหม่ได้ง่าย (เช่น AdminController)

---

## 📚 สรุปการแยก Responsibility

| Component | Responsibility | ห้ามทำ |
|-----------|---------------|--------|
| **Model** | - Query Database<br>- Data Validation<br>- Business Logic (Data) | - ไม่แสดง HTML<br>- ไม่รับ HTTP Request |
| **View** | - แสดง HTML<br>- Form Input<br>- CSS/JavaScript | - ไม่ Query Database<br>- ไม่มี Business Logic |
| **Controller** | - รับ HTTP Request<br>- Business Logic (Flow)<br>- เรียก Model<br>- ส่งข้อมูลไป View | - ไม่ Query Database โดยตรง<br>- ไม่มี HTML |

---

## 🎓 Best Practices ที่ใช้ในโปรเจกต์

1. ✅ **Single Responsibility Principle**
   - แต่ละ Class/Function ทำหน้าที่เดียว

2. ✅ **Don't Repeat Yourself (DRY)**
   - Code ที่ใช้บ่อยอยู่ใน Model (Reusable)

3. ✅ **Separation of Concerns**
   - แยก Logic ออกจากกันอย่างชัดเจน

4. ✅ **Fat Models, Skinny Controllers**
   - Business Logic อยู่ใน Model มากกว่า Controller

5. ✅ **Template Inheritance** (Jinja2)
   - View ใช้ base template ร่วมกัน (Navbar, Footer)

---

