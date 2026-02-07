"""
Main Application - จุดเริ่มต้นของระบบ Rumor Tracking MVC
โครงสร้าง: MVC Pattern ที่ชัดเจน แยกโฟลเดอร์
- models/: ชั้น Model - จัดการข้อมูลและ business logic
- templates/: ชั้น View - จัดการการแสดงผล
- app.py: ชั้น Controller - จัดการ routing และ request/response
- config/: การตั้งค่าระบบ
"""
from flask import Flask, render_template, request, redirect, url_for, flash
from models import RumourModel, ReportModel, UserModel
from config.settings import Config

app = Flask(__name__)
app.secret_key = Config.SECRET_KEY

# กำหนดค่า threshold สำหรับเปลี่ยนสถานะเป็น panic
PANIC_THRESHOLD = Config.PANIC_THRESHOLD


@app.route('/')
def index():
    """หน้ารวมข่าวลือ - แสดงข่าวลือทั้งหมด เรียงตามจำนวนรายงาน"""
    rumours = RumourModel.get_all_rumours()
    return render_template('index.html', rumours=rumours)


@app.route('/detail/<int:rumour_id>')
def detail(rumour_id):
    """หน้ารายละเอียดข่าวลือ - แสดงรายละเอียดข่าวและจำนวนรายงาน"""
    rumour = RumourModel.get_rumour_by_id(rumour_id)
    if not rumour:
        flash('ไม่พบข่าวลือที่ค้นหา', 'error')
        return redirect(url_for('index'))
    
    reports = ReportModel.get_reports_by_rumour(rumour_id)
    report_count = len(reports)
    users = UserModel.get_all_users()
    verifiers = UserModel.get_verifiers()
    
    return render_template('detail.html', 
                         rumour=rumour, 
                         reports=reports, 
                         report_count=report_count,
                         users=users,
                         verifiers=verifiers)


@app.route('/summary')
def summary():
    """หน้าสรุปผล - แสดงข่าวลือที่เข้าสู่สถานะ panic และข่าวที่ถูกตรวจสอบแล้ว"""
    panic_rumours = RumourModel.get_panic_rumours()
    all_rumours = RumourModel.get_all_rumours()
    total_rumours = len(all_rumours)
    
    # นับจำนวนข่าวที่ตรวจสอบแล้ว (ทั้งระบบ)
    verified_count = sum(1 for rumour in all_rumours if rumour['is_verified'])
    # นับจำนวนข่าว PANIC (ไม่สนใจว่าตรวจสอบแล้วหรือยัง)
    panic_count = len(panic_rumours)
    # คำนวณข่าวรอการตรวจสอบ = ทั้งหมด - ตรวจสอบแล้ว
    pending_count = total_rumours - verified_count
    
    return render_template('summary.html', 
                         panic_rumours=panic_rumours, 
                         total_rumours=total_rumours,
                         verified_count=verified_count,
                         panic_count=panic_count,
                         pending_count=pending_count)


@app.route('/report/<int:rumour_id>', methods=['POST'])
def report_rumour(rumour_id):
    """สร้างรายงานข่าวลือ - ตรวจสอบ business rules"""
    user_id = request.form.get('user_id', type=int)
    report_type = request.form.get('report_type')
    
    # ตรวจสอบว่ามีข้อมูลครบหรือไม่
    if not user_id or not report_type:
        flash('กรุณาเลือกผู้ใช้และประเภทรายงาน', 'error')
        return redirect(url_for('detail', rumour_id=rumour_id))
    
    # ตรวจสอบว่าข่าวลือถูกตรวจสอบแล้วหรือไม่ (Rule 4.3)
    rumour = RumourModel.get_rumour_by_id(rumour_id)
    if rumour['is_verified']:
        flash('ข่าวลือนี้ถูกตรวจสอบแล้ว ไม่สามารถรายงานเพิ่มได้', 'warning')
        return redirect(url_for('detail', rumour_id=rumour_id))
    
    # ตรวจสอบว่าผู้ใช้เคยรายงานข่าวนี้แล้วหรือไม่ (Rule 4.1)
    if ReportModel.check_duplicate_report(user_id, rumour_id):
        user = UserModel.get_user_by_id(user_id)
        flash(f'⚠️ ผู้ใช้ "{user["name"]}" เคยรายงานข่าวนี้ไปแล้ว กรุณาเลือกผู้ใช้ท่านอื่นที่ยังไม่เคยรายงาน', 'warning')
        return redirect(url_for('detail', rumour_id=rumour_id))
    
    # สร้างรายงาน
    ReportModel.create_report(user_id, rumour_id, report_type)
    
    # อัปเดตคะแนนความน่าเชื่อถือ
    RumourModel.update_credibility_score(rumour_id)
    
    user = UserModel.get_user_by_id(user_id)
    flash(f'✅ รายงานข่าวลือสำเร็จ! ผู้รายงาน: {user["name"]} | ประเภท: {report_type}', 'success')
    
    # ตรวจสอบจำนวนรายงาน และเปลี่ยนสถานะเป็น panic ถ้าเกิน threshold (Rule 4.2)
    report_count = RumourModel.get_rumour_report_count(rumour_id)
    if report_count >= PANIC_THRESHOLD and rumour['status'] == 'ปกติ':
        RumourModel.update_status_to_panic(rumour_id)
        flash(f'ข่าวลือนี้มีรายงาน {report_count} รายงาน เปลี่ยนสถานะเป็น PANIC!', 'danger')
    
    return redirect(url_for('detail', rumour_id=rumour_id))


@app.route('/verify/<int:rumour_id>', methods=['POST'])
def verify_rumour(rumour_id):
    """ตรวจสอบและยืนยันข่าวลือโดยผู้ตรวจสอบ"""
    verifier_id = request.form.get('verifier_id', type=int)
    verification_result = request.form.get('verification_result')
    
    # ตรวจสอบว่ามีข้อมูลครบหรือไม่
    if not verifier_id or not verification_result:
        flash('กรุณาเลือกผู้ตรวจสอบและผลการตรวจสอบ', 'error')
        return redirect(url_for('detail', rumour_id=rumour_id))
    
    # ตรวจสอบว่าผู้ใช้เป็นผู้ตรวจสอบหรือไม่
    verifier = UserModel.get_user_by_id(verifier_id)
    if not verifier or not verifier['verifier_code']:
        flash('ผู้ใช้นี้ไม่มีสิทธิ์เป็นผู้ตรวจสอบ', 'error')
        return redirect(url_for('detail', rumour_id=rumour_id))
    
    # ตรวจสอบว่าข่าวลือถูกตรวจสอบแล้วหรือไม่ (Rule 4.4)
    rumour = RumourModel.get_rumour_by_id(rumour_id)
    if rumour['is_verified']:
        flash('ข่าวลือนี้ถูกตรวจสอบแล้ว', 'warning')
        return redirect(url_for('detail', rumour_id=rumour_id))
    
    # บันทึกผลการตรวจสอบ
    RumourModel.verify_rumour(rumour_id, verification_result, verifier_id)
    flash(f'ตรวจสอบข่าวลือสำเร็จ: {verification_result}', 'success')
    
    return redirect(url_for('detail', rumour_id=rumour_id))


if __name__ == '__main__':
    print("=" * 60)
    print("  ระบบติดตามข่าวลือบนสื่อสังคมออนไลน์")
    print("  Rumor Tracking System (MVC Pattern)")
    print("=" * 60)
    print("\n📍 เปิดเว็บไซต์ที่: http://{}:{}".format(Config.HOST, Config.PORT))
    print("\n📄 หน้าจอทั้ง 3 หน้า:")
    print("  1. หน้ารวมข่าวลือ:      http://{}:{}/".format(Config.HOST, Config.PORT))
    print("  2. หน้ารายละเอียด:       http://{}:{}/detail/<รหัสข่าว>".format(Config.HOST, Config.PORT))
    print("  3. หน้าสรุปผล:           http://{}:{}/summary".format(Config.HOST, Config.PORT))
    print("\n⚠️  กด Ctrl+C เพื่อหยุดโปรแกรม")
    print("=" * 60)
    app.run(debug=Config.DEBUG, host=Config.HOST, port=Config.PORT)
