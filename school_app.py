import streamlit as st
import streamlit.components.v1 as components
import google.generativeai as genai
import pandas as pd
import datetime
import base64
import os
import io
import shutil
import urllib.parse
import time
import random
import webbrowser

st.markdown("""
<style>
/* مین پیج کی اوپر اور سائیڈوں والی فالتو سپیس ختم کرنے کے لیے */
.block-container {
    padding-top: 1rem !important;
    padding-left: 1.5rem !important;   /* بائیں طرف (سائیڈ بار کے ساتھ) خالی جگہ ختم کرنا */
    padding-right: 1.5rem !important;  /* دائیں طرف کی خالی جگہ ختم کرنا */
    max-width: 100% !important;        /* اسکرین کی مکمل چوڑائی استعمال کرنا */
}
    }
/* سائیڈ بار کا بیک گراؤنڈ سفید اور ٹاپ سپیس ختم کرنا */
[data-testid="stSidebar"] {
    background-color: #ffffff !important;
    border-right: 1px solid #f0f0f0;
    top: 0px !important;
}
[data-testid="stSidebar"] > div:first-child {
    padding-top: 0px !important;
}
header[data-testid="stHeader"] {
    background-color: rgba(0,0,0,0) !important;
}

/* ٹیکسٹ کا رنگ ڈارک گرے/بلیک کرنا */
[data-testid="stSidebar"] p, 
[data-testid="stSidebar"] h1, 
[data-testid="stSidebar"] h2, 
[data-testid="stSidebar"] h3,
[data-testid="stSidebar"] span {
    color: #333333 !important;
}

/* ریڈیو بٹن کو تصویر والے مینو جیسا بنانا */
.stRadio > div[role="radiogroup"] {
    gap: 2px;
}
.stRadio > div[role="radiogroup"] > label {
    background: transparent;
    padding: 10px 15px;
    border-radius: 8px;
    margin-bottom: 2px;
    cursor: pointer;
    transition: 0.2s ease;
}
.stRadio > div[role="radiogroup"] > label:hover {
    background-color: #f4f6f8;
}

/* منتخب شدہ (Active) مینو کا سٹائل */
.stRadio > div[role="radiogroup"] > label[aria-checked="true"] {
    background-color: #f4f6f8;
    font-weight: bold;
}
.stRadio > div[role="radiogroup"] > label[aria-checked="true"] p {
    color: #1b5e20 !important;
}

/* 🔴 ریڈیو بٹن کے گول دائرے کو مکمل غائب کرنا */
div[data-baseweb="radio"] div {
    display: none !important;
}
div[data-baseweb="radio"] {
    display: none !important;
}

/* مینو کے ٹیکسٹ کا سٹائل */
.stRadio > div[role="radiogroup"] > label p {
    font-size: 14.5px;
    font-weight: 500;
    color: #4a5568 !important;
}
</style>
""", unsafe_allow_html=True)

# 🟢 اس کے نیچے آپ کا باقی کا پرانا کوڈ چلتا رہے گا...

# ----------------- زبان کنٹرول (Translation Engine) -----------------
if 'ui_lang' not in st.session_state:
    st.session_state.ui_lang = "English"

def tr(ur, en):
    return ur if st.session_state.ui_lang == "اردو" else en

def get_translations(lang):
    if lang == "اردو":
        return {
            "dir": "rtl", "align": "right", "logo_align": "right", "text_align_rev": "left",
            "font": "font-family: 'Jameel Noori Nastaleeq', 'Nafees Web Naskh', 'Arial', sans-serif;",
            "fee_receipt": "فیس کی رسید", "fee_challan": "فیس چالان",
            "issue_date": "تاریخ اجراء:", "adm_no": "داخلہ نمبر:", "name": "نام:", "class": "کلاس / سیکشن:",
            "inv_no": "انوائس نمبر", "desc": "تفصیل", "amount": "رقم",
            "total_paid": "کل ادا شدہ رقم", "total_payable": "کل واجب الادا رقم",
            "cashier": "کیشیئر:", "auth_sign": "مجاز دستخط اور مہر:",
            "tf": "ٹیوشن فیس", "af": "اینول فنڈ", "ef": "امتحانی فیس", "of": "دیگر/جرمانہ", "arr": "بقایا جات",
            "salary_slip": "تنخواہ کی رسید", "month": "مہینہ:", "date": "تاریخ:",
            "desig": "عہدہ:", "remarks": "تفصیلات", "total_salary_paid": "کل ادا شدہ:",
            "emp_sign": "ملازم کے دستخط:", "prin_sign": "پرنسپل کے دستخط:",
            "stu_att": "طلباء کی روزانہ حاضری شیٹ", "stf_att": "سٹاف کی حاضری شیٹ",
            "status": "حاضری", "staff_list": "سٹاف کی فہرست", "staff_id": "سٹاف آئی ڈی",
            "report_date": "تاریخ:", "reg_no": "رول نمبر", "student_name": "طالب علم کا نام",
            "acc_voucher": "اکاؤنٹس واؤچر", "type": "قسم:", "particulars": "تفصیلات",
            "stu_adm_form": "طالب علم کا داخلہ فارم", "stf_rec_form": "سٹاف کا ریکارڈ فارم",
            "gender": "جنس:", "cnic": "شناختی کارڈ:", "mname": "والدہ کا نام:", "mcnic": "شناختی کارڈ:",
            "dob": "تاریخ پیدائش:", "bform": "ب فارم نمبر:", "blood": "بلڈ گروپ:", "address": "مکمل پتہ:",
            "phone": "فون نمبر:", "prev": "سابقہ سکول:", "fee": "مقررہ ماہانہ فیس:", "medical": "میڈیکل ہسٹری:",
            "psign": "والد/سرپرست کے دستخط:", "join": "تاریخ شمولیت:", "fhcnic": "شناختی کارڈ:",
            "edu": "تعلیم:", "sal": "ماہانہ تنخواہ:", "due_date": "آخری تاریخ:",
            "f_prof": "والد کا پیشہ:", "report_date": "تاریخ:"
        }
    else:
        return {
            "dir": "ltr", "align": "left", "logo_align": "left", "text_align_rev": "right",
            "font": "font-family: 'Arial', sans-serif;",
            "fee_receipt": "FEE RECEIPT", "fee_challan": "FEE CHALLAN",
            "issue_date": "Issue Date:", "adm_no": "Reg No:", "name": "Name:", "class": "Class / Sec:",
            "inv_no": "Invoice No", "desc": "Description", "amount": "Amount",
            "total_paid": "Total Paid", "total_payable": "Total Payable",
            "cashier": "Cashier:", "auth_sign": "Auth. Sign & Stamp:",
            "tf": "TUITION FEE", "af": "ANNUAL FUND", "ef": "EXAM FEE", "of": "OTHERS/FINE", "arr": "ARREARS",
            "salary_slip": "SALARY SLIP", "month": "Month:", "date": "Date:",
            "desig": "Designation:", "remarks": "Remarks", "total_salary_paid": "Total Paid:",
            "emp_sign": "Employee Sig:", "prin_sign": "Principal Sig:",
            "stu_att": "STUDENT ATTENDANCE SHEET", "stf_att": "STAFF ATTENDANCE SHEET",
            "status": "Status", "staff_list": "Staff List", "staff_id": "Staff ID",
            "report_date": "Date:", "reg_no": "Reg No", "student_name": "Student Name",
            "acc_voucher": "ACCOUNTS VOUCHER", "type": "Type:", "particulars": "Particulars",
            "stu_adm_form": "STUDENT ADMISSION FORM", "stf_rec_form": "STAFF RECORD FORM",
            "gender": "Gender:", "cnic": "CNIC:", "mname": "Mother's name:", "mcnic": "CNIC:",
            "dob": "DOB:", "bform": "B-Form:", "blood": "Blood Group:", "address": "Address:",
            "phone": "Phone No:", "prev": "Prev School:", "fee": "Monthly Fee:", "medical": "Medical Info:",
            "psign": "Parent Signature:", "join": "Joining Date:", "fhcnic": "CNIC:",
            "edu": "Education:", "sal": "Salary:", "due_date": "Due Date:",
            "f_prof": "Father's Profession:", "report_date": "Date:"
        }

def safe_int(val):
    try: return int(float(val))
    except (ValueError, TypeError): return 0

def get_disp_val(ur_val, en_val):
    ur_str = str(ur_val) if pd.notna(ur_val) and ur_val is not None else ""
    en_str = str(en_val) if pd.notna(en_val) and en_val is not None else ""
    if st.session_state.ui_lang == "English":
        return en_str if en_str.strip() != "" else ur_str
    else:
        return ur_str if ur_str.strip() != "" else en_str

def get_relation_card_label(gender_str, g_type_str):
    lang = st.session_state.ui_lang
    gender_str = str(gender_str).strip()
    g_type_str = str(g_type_str).strip()
    
    if "Husband" in g_type_str or "شوہر" in g_type_str:
        return "زوجہ" if lang == "اردو" else "W/O"
    elif "Guardian" in g_type_str or "سرپرست" in g_type_str: 
        return "سرپرست" if lang == "اردو" else "Guardian"
    elif gender_str in ["Girl", "Female", "لڑکی", "عورت", "female"]: 
        return "بنت" if lang == "اردو" else "D/O"
    else:
        return "ولد" if lang == "اردو" else "S/O"

def get_desig_disp(d_val):
    if st.session_state.ui_lang == "اردو":
        return {"Teacher": "استاد / ٹیچر", "Principal": "پرنسپل", "Clerk": "کلرک", "Maid/Peon": "آیا / چپڑاسی", "Security Guard": "سیکیورٹی گارڈ"}.get(d_val, d_val)
    return d_val

def print_button_js(html_content, btn_text, landscape=False):
    page_css = "@page { size: A4 landscape; margin: 5mm; }" if landscape else "@page { size: A4 portrait; margin: 5mm; }"
    full_html = f"""<!DOCTYPE html>
    <html><head><meta charset="utf-8"><style>
    {page_css} 
    body, html {{ font-family: Arial, sans-serif; margin: 0; padding: 0; background: white; height: auto !important; min-height: 100%; overflow: visible !important; }}
    * {{ -webkit-print-color-adjust: exact !important; print-color-adjust: exact !important; }}
    
    /* 🟢 ملٹی پیج پرنٹنگ کے لیے CSS رولز (تاکہ کوئی لائن نہ کٹے) */
    @media print {{
        body, html {{ height: auto !important; overflow: visible !important; display: block !important; }}
        table {{ page-break-inside: auto; width: 100%; }}
        tr {{ page-break-inside: avoid; page-break-after: auto; }}
        thead {{ display: table-header-group; }}
        tfoot {{ display: table-footer-group; }}
        .page-break {{ page-break-after: always; }}
    }}
    </style></head>
    <body>{html_content}</body></html>"""
    b64 = base64.b64encode(full_html.encode('utf-8')).decode('utf-8')
    js = f"""
    <script>
    function printNewTab() {{
        var win = window.open('', '_blank');
        var binaryString = window.atob('{b64}');
        var bytes = new Uint8Array(binaryString.length);
        for (var i = 0; i < binaryString.length; i++) {{ bytes[i] = binaryString.charCodeAt(i); }}
        var htmlStr = new TextDecoder('utf-8').decode(bytes);
        win.document.write(htmlStr);
        win.document.close();
        win.focus();
        setTimeout(function(){{ win.print(); }}, 1000); 
    }}
    </script>
    <button onclick="printNewTab()" style="padding:10px 20px; background:#1a4f8b; color:white; border:none; border-radius:5px; cursor:pointer; font-weight:bold; width:100%; font-size: 16px; margin-top: 10px;">🖨️ {btn_text}</button>
    """
    components.html(js, height=60)

import os
import psycopg2
from psycopg2 import errors

# ----------------- کلاؤڈ ڈیٹا بیس اور سمارٹ ریپر (Smart Wrapper) -----------------
# یہ کلاؤڈ کنکشن آپ کے پرانے کوڈ کو چھیڑے بغیر اسے Neon کلاؤڈ پر چلائے گا
class PostgresCursorWrapper:
    def __init__(self, cursor):
        self.cursor = cursor
        
    def execute(self, query, params=None):
        # پرانے SQLite کے '?' کو نئے Postgres کے '%s' میں آٹو کنورٹ کرنا
        if '?' in query:
            query = query.replace('?', '%s')
        if params:
            return self.cursor.execute(query, params)
        return self.cursor.execute(query)
        
    def fetchone(self): return self.cursor.fetchone()
    def fetchall(self): return self.cursor.fetchall()
    def fetchmany(self, size=None): return self.cursor.fetchmany(size)
    def close(self): self.cursor.close()
    
    @property
    def description(self): return self.cursor.description
    @property
    def rowcount(self): return self.cursor.rowcount

class PostgresConnWrapper:
    def __init__(self, conn):
        self.conn = conn
    def cursor(self): return PostgresCursorWrapper(self.conn.cursor())
    def commit(self): self.conn.commit()
    def rollback(self): self.conn.rollback()
    def close(self): self.conn.close()

def get_db_connection():
    # آپ کا لائیو Neon Cloud Database Connection
    DB_URL = "postgresql://neondb_owner:npg_foZpA5qyrRB6@ep-frosty-pine-b3xhf87r-pooler.c-4.ap-southeast-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"
    conn = psycopg2.connect(DB_URL)
    return PostgresConnWrapper(conn)

# ----------------- ڈیٹا بیس شروع کرنے کا نیا فنکشن (Cloud Init) -----------------
def init_db():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # SQLite کے BLOB کو Postgres کے BYTEA میں بدل دیا ہے
        cursor.execute('''CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT, blob_value BYTEA)''')
        
        cursor.execute("SELECT value FROM settings WHERE key='password'")
        if not cursor.fetchone():
            cursor.execute("INSERT INTO settings (key, value) VALUES ('password', '1234')")
            
        cursor.execute('''CREATE TABLE IF NOT EXISTS students (reg_id TEXT PRIMARY KEY, name TEXT, fname TEXT, dob TEXT, blood TEXT, class TEXT, section TEXT, bform TEXT, phone TEXT, address TEXT, prev_school TEXT, prev_class TEXT, medical TEXT, monthly_fee REAL, adm_date TEXT, arrears REAL, advance_fee REAL DEFAULT 0, discount REAL DEFAULT 0)''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS staff (staff_id TEXT PRIMARY KEY, name TEXT, fname TEXT, cnic TEXT, dob TEXT, designation TEXT, phone TEXT, address TEXT, joining_date TEXT, salary REAL, advance_salary REAL DEFAULT 0)''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS attendance (date TEXT, type TEXT, person_id TEXT, status TEXT)''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS fees (date TEXT, reg_id TEXT, month TEXT, tuition REAL, arrears_col REAL, total REAL, status TEXT DEFAULT 'Paid', due_date TEXT, invoice_no TEXT)''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS salary_records (date TEXT, staff_id TEXT, month TEXT, amount REAL, remarks TEXT)''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS accounts (date TEXT, type TEXT, description TEXT, amount REAL, head_name TEXT, voucher_no TEXT)''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS account_heads (head_name TEXT PRIMARY KEY, head_type TEXT)''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS subjects (subject_name TEXT PRIMARY KEY)''')
        
        # INTEGER PRIMARY KEY AUTOINCREMENT کو SERIAL PRIMARY KEY سے بدل دیا ہے
        cursor.execute('''CREATE TABLE IF NOT EXISTS timetable (id SERIAL PRIMARY KEY, class TEXT, section TEXT, day TEXT, period TEXT, subject TEXT, teacher_id TEXT)''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS lesson_plan (id SERIAL PRIMARY KEY, date TEXT, class TEXT, section TEXT, subject TEXT, teacher_id TEXT, topic TEXT, status TEXT, plan_type TEXT)''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS exams (exam_name TEXT PRIMARY KEY, start_date TEXT)''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS exam_marks (id SERIAL PRIMARY KEY, exam_name TEXT, reg_id TEXT, subject TEXT, total_marks REAL, obtained_marks REAL)''')
        
        # notices کا ٹیبل آپ کے پرانے کوڈ میں دو بار تھا، میں نے ایک بار کر دیا ہے
        cursor.execute('''CREATE TABLE IF NOT EXISTS notices (id SERIAL PRIMARY KEY, date TEXT, audience TEXT, title TEXT, details TEXT)''')
        
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Database Init Error: {e}")

# ایپ سٹارٹ ہوتے ہی سب سے پہلے ڈیٹا بیس ٹیبلز چیک کرے گا
init_db()    
# 🟢 نیا ٹرانسپورٹ اور جی پی ایس ڈیٹا بیس
    cursor.execute('''CREATE TABLE IF NOT EXISTS transport (vehicle_id TEXT PRIMARY KEY, type TEXT, driver_name TEXT, driver_phone TEXT, route_name TEXT, fare REAL, gps_device_id TEXT)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS transport_members (reg_id TEXT PRIMARY KEY, vehicle_id TEXT)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS live_locations (device_id TEXT PRIMARY KEY, lat REAL, lon REAL, last_updated TEXT, speed REAL)''')
    
    # 🟢 نیا انوینٹری اور ہیلپ ڈیسک ڈیٹا بیس
    cursor.execute('''CREATE TABLE IF NOT EXISTS inventory (id INTEGER PRIMARY KEY AUTOINCREMENT, item_name TEXT, category TEXT, total_qty INTEGER, used_qty INTEGER DEFAULT 0)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS complaints (id INTEGER PRIMARY KEY AUTOINCREMENT, date TEXT, sender_name TEXT, sender_type TEXT, reg_id TEXT, subject TEXT, details TEXT, status TEXT DEFAULT 'Pending', admin_reply TEXT)''')

    # Academic Sessions Table (یہ لائن پہلے سے موجود ہوگی، اسے ایسے ہی رہنے دیں)
    
    # Academic Sessions Table
    cursor.execute('''CREATE TABLE IF NOT EXISTS academic_sessions (session_name TEXT PRIMARY KEY, status TEXT)''')
    cursor.execute("SELECT COUNT(*) FROM academic_sessions")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO academic_sessions VALUES ('2026-27', 'ACTIVE')")
    # 🟢 نئے فیچرز (لائبریری، سیکیورٹی، انوینٹری، ہیلپ ڈیسک) کے ٹیبلز
    cursor.execute('''CREATE TABLE IF NOT EXISTS books (book_id TEXT PRIMARY KEY, title TEXT, author TEXT, category TEXT, total_qty INTEGER, available_qty INTEGER)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS book_issue (id INTEGER PRIMARY KEY AUTOINCREMENT, book_id TEXT, issued_to_type TEXT, reg_id TEXT, issue_date TEXT, due_date TEXT, return_date TEXT, status TEXT DEFAULT 'Issued', fine REAL DEFAULT 0)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS visitors (id INTEGER PRIMARY KEY AUTOINCREMENT, date TEXT, time_in TEXT, time_out TEXT, name TEXT, phone TEXT, purpose TEXT, to_meet TEXT, status TEXT DEFAULT 'Inside')''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS inventory (id INTEGER PRIMARY KEY AUTOINCREMENT, item_name TEXT, category TEXT, total_qty INTEGER, used_qty INTEGER DEFAULT 0)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS complaints (id INTEGER PRIMARY KEY AUTOINCREMENT, date TEXT, sender_name TEXT, sender_type TEXT, reg_id TEXT, subject TEXT, details TEXT, status TEXT DEFAULT 'Pending', admin_reply TEXT)''')
   
    conn.commit()
    return conn

conn = init_db()
cursor = conn.cursor()

def get_active_session():
    cursor.execute("SELECT session_name FROM academic_sessions WHERE status='ACTIVE'")
    row = cursor.fetchone()
    return row[0] if row else "2026-27"

active_session = get_active_session()

# ================= لاگ ان اور سیکیورٹی سسٹم =================
cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE,
                    password TEXT,
                    role TEXT,
                    ref_id TEXT
                )''')

cursor.execute("SELECT COUNT(*) FROM users")
if cursor.fetchone()[0] == 0:
    cursor.execute("INSERT INTO users (username, password, role, ref_id) VALUES ('admin', 'admin123', 'Admin', 'N/A')")
    conn.commit()

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'current_role' not in st.session_state:
    st.session_state.current_role = None
if 'current_user' not in st.session_state:
    st.session_state.current_user = None

if not st.session_state.logged_in:
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown(f"<h1 style='text-align: center; color: #1b5e20;'>🏫 School Management System</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center; color: #555;'>🔐 لاگ ان کریں (Login to Continue)</h3>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.markdown("<div style='background-color: #f1f8e9; padding: 30px; border-radius: 15px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); border: 2px solid #c8e6c9;'>", unsafe_allow_html=True)
        with st.form("login_form"):
            login_user = st.text_input("یوزر نیم (Username)", placeholder="مثال: admin")
            login_pass = st.text_input("پاس ورڈ (Password)", type="password", placeholder="اپنا پاس ورڈ لکھیں")
            submit_login = st.form_submit_button("لاگ ان کریں (Login)", use_container_width=True, type="primary")
            
            if submit_login:
                if login_user.strip() and login_pass.strip():
                    cursor.execute("SELECT role, ref_id FROM users WHERE username=? AND password=?", (login_user.strip(), login_pass.strip()))
                    user_data = cursor.fetchone()
                    
                    if user_data:
                        st.session_state.logged_in = True
                        st.session_state.current_role = user_data[0]
                        st.session_state.current_user = login_user.strip()
                        st.session_state.ref_id = user_data[1]
                        st.success(f"خوش آمدید! آپ بطور {user_data[0]} لاگ ان ہو چکے ہیں۔")
                        st.rerun()
                    else:
                        st.error("❌ غلط یوزر نیم یا پاس ورڈ! دوبارہ کوشش کریں۔")
                else:
                    st.warning("⚠️ براہ کرم یوزر نیم اور پاس ورڈ دونوں درج کریں۔")
        st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# ================= مینوز اور سیٹنگز =================
all_menu_ur = ["ڈیش بورڈ", "پیرنٹ پورٹل", "سکول پروفائل", "طلباء مینجمنٹ", "سٹاف مینجمنٹ", "حاضری سسٹم", "فیس، رسیدیں، سیلری", "اکاؤنٹس", "تعلیمی نظام", "لائبریری", "انوینٹری (سٹاک)", "گیٹ سیکیورٹی", "ٹرانسپورٹ (GPS)", "ہیلپ ڈیسک (شکایات)", "واٹس ایپ نوٹیفیکیشن", "پرفارمنس",  "ڈسپلن اور میرٹ" , "آئی ڈی کارڈ", "نوٹس بورڈ", "رپورٹس", "ڈیٹا بیک اپ", "اے آئی جنریٹر", "پاسورڈ تبدیل"]
all_menu_en = ["Dashboard", "Parent Portal", "School Profile", "Students Mgt", "Staff Mgt", "Attendance", "Fee & Salary", "Accounts", "Academics", "Library", "Inventory", "Gate Security", "Transport", "Helpdesk", "WhatsApp Alerts", "Performance", "Discipline & Merit", "ID Card Maker", "Notice Board", "Reports", "Data Backup", "AI Generator", "Change Password"]
all_menu_icons = ["📊", "👨‍👩‍👦", "🏫", "🎓", "👨‍🏫", "📋", "💵", "💲", "📚", "📖", "📦", "🛡️", "🚌", "🎧", "📱", "📈", "📇", "📢", "📑", "💾", "✦", "🔑", "⭐"]

user_role = st.session_state.current_role

# 🟢 بالکل درست الائنمنٹ اور 'if' کے ساتھ رول بیسڈ مینوز
if user_role == "Admin":
    allowed_menus = all_menu_en
elif user_role == "Operator":
    allowed_menus = ["Dashboard", "Students Mgt", "Attendance", "Fee & Salary", "Library", "Inventory", "Gate Security", "Transport", "Helpdesk", "WhatsApp Alerts", "ID Card Maker", "Notice Board", "Change Password", "Discipline & Merit"]
elif user_role == "Teacher":
    allowed_menus = ["Dashboard", "Attendance", "Academics", "Helpdesk", "Performance", "AI Generator", "WhatsApp Alerts", "Discipline & Merit"]
elif user_role == "Guardian":
    allowed_menus = ["Parent Portal", "Notice Board", "Change Password"]
else:
    allowed_menus = all_menu_en

menu_en, menu_ur, menu_icons = [], [], []
for en, ur, icon in zip(all_menu_en, all_menu_ur, all_menu_icons):
    if en in allowed_menus:
        menu_en.append(en)
        menu_ur.append(ur)
        menu_icons.append(icon)
        
sub_menus_map = {
    "Students Mgt": {"ur": ["نیا داخلہ", "ریکارڈ ایڈٹ کریں", "🔍 تلاش", "🖨️ پرنٹ پروفائل", "🎓 سرٹیفکیٹس", "📥 بلک امپورٹ"], "en": ["New Admission", "Edit Record", "Search", "Print Profile", "Certificates", "Bulk Import"]},
    "Staff Mgt": {"ur": ["سٹاف لسٹ", "نیا سٹاف", "سٹاف ایڈٹ کریں", "سٹاف تلاش کریں", "پروفائل پرنٹ کریں", "یوزر اکاؤنٹس", "🎓 سرٹیفکیٹس", "لیٹرز اور دستاویزات"], "en": ["Staff List", "New Staff", "Edit Staff", "Search Staff", "Print Profile", "User Accounts", "Certificates", "Letters & Documents"]},
    "Attendance": {"ur": ["طالب علم کی حاضری", "سٹاف کی حاضری", "سمارٹ کیو-آر حاضری", "حاضری رپورٹ و پرنٹ", "چھٹی کی درخواستیں"], "en": ["Student Attendance", "Staff Attendance", "Smart QR Attendance", "Attendance Report & Print", "Leave Requests"]},
    "Fee & Salary": {"ur": ["📄 چالان بنائیں", "💰 فیس وصولی", "🔴 بقایا اور ایڈوانس", "🎁 ڈسکاؤنٹ", "📊 سٹاف سیلری", "🖨️ سیلری سلپس"], "en": ["Generate Fee Challans", "Collect Fees", "Arrears & Advance", "Discount Mgt", "Pay Salary", "Salary Slips"]},
    "Accounts": {"ur": ["روزانہ کی رپورٹ", "ماہانہ رپورٹ", "لیجر / کھاتہ"], "en": ["Daily Report", "Monthly Report", "Ledger"]},
    
    # 🟢 Academics کی لسٹ کے آخر میں نیا آپشن "Exam Answer Sheet" شامل کر دیا گیا ہے
    "Academics": {"ur": ["اکیڈمک سیشنز", "کلاسز", "ٹائم ٹیبل", "لیسن پلان", "امتحانات / مارکس", "رزلٹ کارڈ", "پروموشن سسٹم", "امتحانی جوابی کاپی"], "en": ["Academic Sessions", "Classes", "Time Table", "Lesson Plan", "Exams & Marks", "Result Card", "Promotion System", "Exam Answer Sheet"]},
    
    "Library": {"ur": ["کتابوں کا ریکارڈ", "کتاب جاری / واپس کریں", "لائبریری رپورٹس"], "en": ["Manage Books", "Issue / Return Books", "Library Reports"]},
    "Inventory": {"ur": ["نیا سٹاک شامل کریں", "سٹاک کا ریکارڈ"], "en": ["Add New Stock", "Stock Record"]},
    "Gate Security": {"ur": ["نیا وزیٹر (انٹری)", "موجودہ وزیٹرز (آؤٹ)", "وزیٹر ہسٹری"], "en": ["New Visitor (Entry)", "Active Visitors (Out)", "Visitor History"]},
    "Transport": {"ur": ["گاڑیاں اور روٹس", "طلباء کی بکنگ", "لائیو جی پی ایس (لائیو میپ)"], "en": ["Vehicles & Routes", "Student Booking", "Live GPS Map"]},
    "Helpdesk": {"ur": ["تمام شکایات و تجاویز"], "en": ["All Complaints & Feedback"]},
    "Performance": {"ur": ["طلباء کی کارکردگی", "سٹاف کی کارکردگی", "مکمل سکول کا جائزہ"], "en": ["Student Performance", "Staff Performance", "Overall School Performance"]},
    "Notice Board": {"ur": ["نیا نوٹس", "تمام نوٹسز"], "en": ["New Notice", "All Notices"]}
}

if 'active_main_en' not in st.session_state: st.session_state.active_main_en = "Dashboard"
if 'active_sub_en' not in st.session_state: st.session_state.active_sub_en = None

display_options = []
option_mapping = {}
current_index = 0

for main_en, main_ur, icon in zip(menu_en, menu_ur, menu_icons):
    main_disp = f"{icon} {main_ur}" if st.session_state.ui_lang == "اردو" else f"{icon} {main_en}"
    display_options.append(main_disp)
    option_mapping[main_disp] = ("main", main_en, None)
    
    if st.session_state.active_main_en == main_en:
        if main_en in sub_menus_map:
            for sub_en, sub_ur in zip(sub_menus_map[main_en]["en"], sub_menus_map[main_en]["ur"]):
                sub_disp = f" ↳ {sub_ur}" if st.session_state.ui_lang == "اردو" else f" ↳ {sub_en}"
                display_options.append(sub_disp)
                option_mapping[sub_disp] = ("sub", main_en, sub_en)

target_tuple = None
if st.session_state.active_sub_en and st.session_state.active_main_en in sub_menus_map:
    target_tuple = ("sub", st.session_state.active_main_en, st.session_state.active_sub_en)
else:
    target_tuple = ("main", st.session_state.active_main_en, None)

for idx, opt in enumerate(display_options):
    if option_mapping[opt] == target_tuple:
        current_index = idx
        break

today_date = datetime.date.today().strftime("%Y-%m-%d")
classes_list = ["Play Group", "Nursery", "Prep", "One", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight", "Nine", "Ten"]
months_en = ["JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"]

def get_setting(key_name):
    cursor.execute("SELECT value FROM settings WHERE key=?", (key_name,))
    row = cursor.fetchone()
    return row[0] if row and row[0] else ""

school_name = get_setting("school_name") or "DAR-E-KHADIJA SCHOOLS"
school_address = get_setting("school_address") or "Sillanwali, District Sargodha"
school_phone = get_setting("school_phone") or ""
school_whatsapp = get_setting("school_whatsapp") or ""
school_email = get_setting("school_email") or ""
school_website = get_setting("school_website") or ""
school_facebook = get_setting("school_facebook") or ""
school_reg = get_setting("school_reg") or ""

cursor.execute("SELECT blob_value FROM settings WHERE key='school_logo'")
logo_row = cursor.fetchone()
saved_logo_bytes = logo_row[0] if logo_row and logo_row[0] else None

logo_src_b64 = ""
if saved_logo_bytes:
    b64_encoded = base64.b64encode(saved_logo_bytes).decode()
    logo_src_b64 = f"data:image/png;base64,{b64_encoded}"

# سائیڈ بار کے اوپر سے سکول کا نام اور لوگو مکمل ختم کر دیا گیا ہے

with st.sidebar:
# 1. ٹاپ برانڈنگ (لوگو اور سکول کا نام)
    logo_html = f'<img src="{logo_src_b64}" style="width: 55px; height: 55px; object-fit: contain; margin-right: 12px;">' if logo_src_b64 else '<div style="font-size:35px; margin-right: 12px;">🏫</div>'
    
    # 🟢 یہاں padding کو 25px سے کم کر کے 5px کر دیا گیا ہے
    branding_html = f"""
    <div style="display: flex; align-items: center; padding: 5px 10px 20px 10px;">
        {logo_html}
        <div style="line-height: 1.2;">
            <div style="font-size: 16px; font-weight: 800; color: #1a202c; font-family: sans-serif;">{school_name.replace(" ", "<br>", 1) if " " in school_name else school_name}</div>
            <div style="font-size: 12px; color: #a0aec0; margin-top: 3px;">School System</div>
        </div>
    </div>
    """
    st.markdown(branding_html, unsafe_allow_html=True)
    
    # 2. ورک سپیس انڈیکیٹر (Workspace Indicator)
    role_lbl = st.session_state.current_role.upper() if st.session_state.current_role else "ADMIN"
    workspace_html = f"""
    <div style="background-color: #f7fafc; border: 1px solid #edf2f7; border-radius: 8px; padding: 10px 15px; display: flex; align-items: center; justify-content: space-between; margin-bottom: 25px; margin-left: 5px; margin-right: 5px; cursor: pointer;">
        <div style="display: flex; align-items: center;">
            <div style="width: 8px; height: 8px; background-color: #38a169; border-radius: 50%; margin-right: 10px;"></div>
            <div style="font-size: 11px; font-weight: 700; color: #4a5568; letter-spacing: 0.5px;">{role_lbl} WORKSPACE</div>
        </div>
        <div style="color: #a0aec0; font-size: 10px;">▼</div>
    </div>
    """
    st.markdown(workspace_html, unsafe_allow_html=True)
    
    # 3. WORKSPACE کا چھوٹا لیبل
    st.markdown("<div style='font-size: 11px; font-weight: 800; color: #a0aec0; letter-spacing: 1.5px; margin-bottom: 5px; margin-left: 15px;'>WORKSPACE</div>", unsafe_allow_html=True)

    # --- اصل مینو (ریڈیو بٹن) ---
    selected_disp = st.radio("Menu", display_options, index=current_index, label_visibility="collapsed")
    sel_type, sel_main, sel_sub = option_mapping[selected_disp]

    if sel_type == "main" and sel_main != st.session_state.active_main_en:
        st.session_state.active_main_en = sel_main
        if sel_main in sub_menus_map: st.session_state.active_sub_en = sub_menus_map[sel_main]["en"][0]
        else: st.session_state.active_sub_en = None
        st.rerun()
    elif sel_type == "sub" and sel_sub != st.session_state.active_sub_en:
        st.session_state.active_sub_en = sel_sub
        st.rerun()

    core_choice = st.session_state.active_main_en
    sub_choice = st.session_state.active_sub_en

    # ================= سائیڈ بار کے بالکل آخر میں (Bottom Section) =================
    st.markdown("<br><hr style='margin: 10px 0; border: none; border-top: 1px solid #f0f0f0;'>", unsafe_allow_html=True)
    
    # Active Session Indicator
    st.markdown(f"""
    <div style="background-color: #f7fafc; padding: 8px; border-radius: 5px; text-align: center; margin-bottom: 10px; border: 1px solid #edf2f7;">
        <small style="color:#718096; font-size:10px; font-weight:bold;">ACTIVE SESSION</small><br>
        <b style="color:#2d3748; font-size:13px;">📅 {active_session}</b>
    </div>
    """, unsafe_allow_html=True)
    
    # زبان کی سیٹنگ
    st.markdown(f"<div style='font-size: 11px; font-weight: 800; color: #a0aec0; margin-bottom: -5px; margin-left: 5px;'>🌐 LANGUAGE / زبان</div>", unsafe_allow_html=True)
    st.session_state.ui_lang = st.radio("", ["English", "اردو"], index=0 if st.session_state.ui_lang == "English" else 1, label_visibility="collapsed", key="sidebar_lang_bottom")

    st.markdown("<br>", unsafe_allow_html=True)
    
    # یوزر کا نام
    st.markdown(f"<div style='font-size: 13px; color: #4a5568; text-align: center; margin-bottom: 8px;'>👤 <b>{st.session_state.current_user}</b></div>", unsafe_allow_html=True)
    
    # لاگ آؤٹ بٹن
    if st.button("🚪 لاگ آؤٹ (Logout)", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.current_role = None
        st.session_state.current_user = None
        st.rerun()

# ================= 1. ڈیش بورڈ (Dashboard) =================
if core_choice in ["ڈیش بورڈ", "Dashboard"]:
    
    # --- 1. ماڈرن ٹاپ بار / سکول پروفائل ---
    top_bar_logo = f'<img src="{logo_src_b64}" style="width: 35px; height: 35px; object-fit: contain; border-radius: 50%; border: 1px solid #ddd;">' if logo_src_b64 else '<div style="font-size:24px; width: 35px; height: 35px; display: flex; align-items: center; justify-content: center; background:#e2e8f0; border-radius:50%;">🏫</div>'
    
    # خالی لائنیں اور اسپیسز ختم کر دی گئی ہیں تاکہ کوڈ ٹیکسٹ نہ بنے
    top_bar_html = f"""<div style="background-color: #ffffff; border-bottom: 1px solid #edf2f7; border-radius: 12px; padding: 12px 20px; display: flex; justify-content: space-between; align-items: center; box-shadow: 0 1px 3px rgba(0,0,0,0.05); margin-bottom: 25px; flex-wrap: wrap; gap: 15px;">
<div style="display: flex; align-items: center; gap: 15px;">
<div style="font-size: 20px; color: #4a5568; cursor: pointer;">☰</div>
<div>
<div style="font-size: 16px; font-weight: 800; color: #1a202c; font-family: system-ui, sans-serif;">{school_name}</div>
<div style="font-size: 11px; color: #718096; margin-top: 1px;">All Campuses</div>
<div style="font-size: 11px; color: #38a169; font-weight: bold; margin-top: 2px; display: flex; align-items: center; gap: 4px;">
<span style="display: inline-block; width: 6px; height: 6px; background-color: #38a169; border-radius: 50%;"></span>
Active Session {active_session}
</div>
</div>
</div>
<div style="display: flex; align-items: center; gap: 20px; flex-wrap: wrap;">
<div style="display: flex; gap: 12px; color: #718096; font-size: 16px;">
<span title="Support" style="cursor: pointer;">🎧</span>
<span title="Messages" style="cursor: pointer;">💬</span>
</div>
<div style="background-color: #f7fafc; border: 1px solid #edf2f7; border-radius: 6px; padding: 4px 10px; font-size: 11px; color: #4a5568; font-weight: 600; display: flex; align-items: center; gap: 4px;">
🌐 {st.session_state.ui_lang} ▾
</div>
<div style="display: flex; align-items: center; gap: 10px; border-left: 1px solid #e2e8f0; padding-left: 15px;">
{top_bar_logo}
<div style="line-height: 1.2;">
<div style="font-size: 12px; font-weight: bold; color: #2d3748;">{st.session_state.current_user.capitalize()}</div>
<div style="font-size: 10px; color: #718096; text-transform: uppercase; font-weight: 600;">{st.session_state.current_role}</div>
</div>
</div>
</div>
</div>"""
    st.markdown(top_bar_html, unsafe_allow_html=True)

    # --- 2. یوزر ویلکم کارڈ اور الرٹس (کالمز میں) ---
    import datetime
    current_hour = datetime.datetime.now().hour
    if current_hour < 12: greeting_msg = "Good Morning! ☀️"
    elif current_hour < 18: greeting_msg = "Good Afternoon! 🌤️"
    else: greeting_msg = "Good Evening! 🌙"

    if st.session_state.current_role == "Admin": user_icon = "👑"
    elif st.session_state.current_role == "Operator": user_icon = "👨‍💻"
    elif st.session_state.current_role == "Teacher": user_icon = "👨‍🏫"
    else: user_icon = "👤"

    # 🟢 بالکل تصویر کی طرح کالمز کی ترتیب
    col_welcome, col_alerts = st.columns([1.2, 2.8])

    with col_welcome:
        welcome_html = f"""
        <div style="background: linear-gradient(135deg, #e8f5e9 0%, #c8e6c9 100%); padding: 30px 20px; border-radius: 20px; border: 1px solid #a5d6a7; box-shadow: 0 6px 15px rgba(0,0,0,0.04); text-align: center; display: flex; flex-direction: column; align-items: center; justify-content: center; min-height: 330px; margin-bottom: 20px;">
            <div style="font-size: 50px; background: white; width: 85px; height: 85px; border-radius: 50%; display: flex; align-items: center; justify-content: center; box-shadow: 0 4px 8px rgba(0,0,0,0.08); border: 3px solid #81c784; margin-bottom: 15px;">
                {user_icon}
            </div>
            <div style="font-size: 13px; color: #2e7d32; font-weight: bold; margin-bottom: 6px; letter-spacing: 0.5px;">
                {greeting_msg}
            </div>
            <div style="font-size: 22px; font-weight: 900; color: #1b5e20; margin-bottom: 6px; text-transform: uppercase;">
                {st.session_state.current_user}
            </div>
            <div style="font-size: 11px; background: #2e7d32; color: white; padding: 3px 12px; border-radius: 20px; display: inline-block; font-weight: bold; letter-spacing: 0.5px; box-shadow: 0 2px 4px rgba(0,0,0,0.15); margin-bottom: 15px;">
                🛡️ {st.session_state.current_role}
            </div>
            <div style="border-top: 1px solid rgba(46, 125, 50, 0.2); padding-top: 12px; width: 100%;">
                <div style="font-size: 11.5px; color: #2e7d32; font-style: italic; line-height: 1.4;">
                    "Wishing you a productive day! Let's achieve greatness today." ✨
                </div>
            </div>
        </div>
        """
        st.markdown(welcome_html, unsafe_allow_html=True)
        
    with col_alerts:
        # 🟢 نیا فیچر: برتھ ڈے الرٹ (Birthday Alerts)
        try:
            local_conn = get_db_connection()
            today_md = datetime.date.today().strftime("%m-%d")
            bday_students = pd.read_sql(f"SELECT name, name_en, class, section FROM students WHERE dob LIKE '%{today_md}' AND status='Active'", local_conn)
        except Exception:
            try:
                bday_students = pd.read_sql(f"SELECT name, class, section FROM students WHERE dob LIKE '%{today_md}' AND status='Active'", local_conn)
            except Exception:
                import pandas as pd
                bday_students = pd.DataFrame()
            
        try:
            bday_staff = pd.read_sql(f"SELECT name, name_en, designation FROM staff WHERE dob LIKE '%{today_md}'", local_conn)
        except:
            try:
                bday_staff = pd.read_sql(f"SELECT name, designation FROM staff WHERE dob LIKE '%{today_md}'", local_conn)
            except:
                bday_staff = pd.DataFrame()
        
        bday_html = ""
        if not bday_students.empty or not bday_staff.empty:
            bday_html = "<div style='background: linear-gradient(135deg, #ff9a9e 0%, #fecfef 99%, #fecfef 100%); padding: 15px; border-radius: 12px; border: 2px solid #ff758c; box-shadow: 0px 4px 6px rgba(0,0,0,0.1); margin-bottom: 15px; color: #d81b60;'>"
            bday_title = tr("🎂 آج ان کی سالگرہ ہے! (Happy Birthday)", "🎂 Happy Birthday! Today is their special day.")
            bday_html += f"<h4 style='margin:0 0 10px 0; display:flex; align-items:center; gap:8px;'>{bday_title}</h4><ul style='margin:0; padding-left:20px; font-size:14px; font-weight:bold;'>"
            
            for _, r in bday_students.iterrows():
                disp_name = str(r['name'])
                if st.session_state.ui_lang == "English" and 'name_en' in r and pd.notna(r['name_en']) and str(r['name_en']).strip() not in ["", "None"]:
                    disp_name = str(r['name_en'])
                stu_lbl = tr("طالب علم", "Student")
                cls_lbl = tr("کلاس", "Class")
                bday_html += f"<li>🎉 {disp_name} - {stu_lbl} ({cls_lbl} {r['class']} {r['section']})</li>"
                
            for _, r in bday_staff.iterrows():
                disp_name = str(r['name'])
                if st.session_state.ui_lang == "English" and 'name_en' in r and pd.notna(r['name_en']) and str(r['name_en']).strip() not in ["", "None"]:
                    disp_name = str(r['name_en'])
                stf_lbl = tr("سٹاف", "Staff")
                bday_html += f"<li>🎉 {disp_name} - {stf_lbl} ({r['designation']})</li>"
                
            bday_html += "</ul></div>"
            st.markdown(bday_html, unsafe_allow_html=True)
            st.balloons()
            
        # فیس ڈیفالٹرز کا بلنکر الرٹ
        defaulters_html = ""
        try:
            today_str = datetime.date.today().strftime("%Y-%m-%d")
            cursor.execute("SELECT COUNT(DISTINCT reg_id) FROM fees WHERE status='Unpaid' AND due_date < ?", (today_str,))
            defaulters_count = cursor.fetchone()[0]
            
            if defaulters_count > 0:
                alert_text = tr(
                    f"🚨 الرٹ: {defaulters_count} طلباء کی فیس کی مقررہ تاریخ گزر چکی ہے! براہ کرم فیس کا سیکشن چیک کریں۔", 
                    f"🚨 ALERT: The fee due date for {defaulters_count} student(s) has passed! Please check the Fees section."
                )
                defaulters_html = f"""
                <style>
                @keyframes blinker {{ 50% {{ opacity: 0.2; }} }}
                .blink_text {{
                  animation: blinker 1s linear infinite; color: #c62828; background-color: #ffcdd2;
                  padding: 15px; border-radius: 12px; font-weight: bold; font-size: 15px;
                  border: 2px solid #b71c1c; box-shadow: 0px 4px 6px rgba(0,0,0,0.05); margin-bottom: 15px;
                }}
                </style>
                <div class="blink_text">
                    {alert_text}
                </div>
                """
        except: pass
            
        if defaulters_html:
            st.markdown(defaulters_html, unsafe_allow_html=True)
            
        # سکول انفو کارڈ (دائیں کالم میں، تصویر کے مطابق)
        st.markdown(f"""
<div style="background-color: #ffffff; padding: 25px; border-radius: 20px; border: 1px solid #edf2f7; box-shadow: 0 4px 6px rgba(0,0,0,0.02); display: flex; flex-direction: column; justify-content: center; min-height: 330px; margin-bottom: 20px;">
<h2 style="color: #1a4f8b; margin-top: 0; border-bottom: 2px solid #f0f2f6; padding-bottom: 15px; font-family: 'Arial', sans-serif;">🏫 School Information</h2>
<div style="display: flex; flex-wrap: wrap; margin-top: 25px; font-size: 15px;">
<div style="width: 50%; margin-bottom: 20px;">
<span style="color: #d32f2f; font-weight: 900;">📍 Address: </span> 
<span style="color: #555;">{school_address}</span>
</div>
<div style="width: 50%; margin-bottom: 20px;">
<span style="color: #d32f2f; font-weight: 900;">📞 Phone: </span> 
<span style="color: #555;">{school_phone}</span>
</div>
<div style="width: 50%; margin-bottom: 20px;">
<span style="color: #d32f2f; font-weight: 900;">📄 Reg No: </span> 
<span style="color: #555;">{school_reg}</span>
</div>
<div style="width: 50%; margin-bottom: 20px;">
<span style="color: #d32f2f; font-weight: 900;">📧 Email: </span> 
<span style="color: #555;">{school_email}</span>
</div>
</div>
</div>
""", unsafe_allow_html=True)
    st.write("---")
    
    # --- 3. فوری لنکس (Quick Actions) ---
    col_a, col_b, col_c, col_d = st.columns(4)
    if col_a.button("➕ " + tr("نیا طالب علم", "Add Student"), use_container_width=True):
        st.session_state.active_main_en = "Students Mgt"
        st.session_state.active_sub_en = "New Admission"
        st.rerun()
    if col_b.button("👨‍🏫 " + tr("نیا ٹیچر", "Add Teacher"), use_container_width=True):
        st.session_state.active_main_en = "Staff Mgt"
        st.session_state.active_sub_en = "New Staff"
        st.rerun()
    if col_c.button("📅 " + tr("حاضری لگائیں", "Mark Attendance"), use_container_width=True):
        st.session_state.active_main_en = "Attendance"
        st.session_state.active_sub_en = "Student Attendance"
        st.rerun()
    if col_d.button("💵 " + tr("فیس چالان", "Generate Challan"), use_container_width=True):
        st.session_state.active_main_en = "Fee & Salary"
        st.session_state.active_sub_en = "Generate Fee Challans"
        st.rerun()
        
    st.write("---")
    
    # --- 4. اعداد و شمار کارڈز (Metrics) ---
    try: stud_df = pd.read_sql("SELECT * FROM students", conn)
    except: stud_df = pd.DataFrame()
        
    try: staff_df = pd.read_sql("SELECT * FROM staff", conn)
    except: staff_df = pd.DataFrame()
        
    try: acc_df = pd.read_sql("SELECT * FROM accounts", conn)
    except: acc_df = pd.DataFrame()
        
    total_income = int(acc_df[acc_df["type"].isin(["آمدنی", "Income"])]["amount"].sum()) if not acc_df.empty else 0
    total_expense = int(acc_df[acc_df["type"].isin(["خرچ", "Expense"])]["amount"].sum()) if not acc_df.empty else 0
    curr_balance = total_income - total_expense
    
    def make_light_card(title, value, icon, bg_gradient, text_color="#1b5e20"):
        return f"""<div style="background: {bg_gradient}; padding: 25px 20px; border-radius: 18px; box-shadow: 0 8px 20px rgba(0,0,0,0.05); border: 1px solid rgba(255,255,255,0.8); text-align: center; color: {text_color}; position: relative; overflow: hidden; transition: transform 0.3s ease;">
        <div style="position: absolute; right: -10px; top: -20px; font-size: 100px; opacity: 0.1; color: {text_color}; transform: rotate(15deg);">{icon}</div>
        <div style="font-size: 45px; margin-bottom: 5px; text-shadow: 1px 1px 2px rgba(0,0,0,0.05);">{icon}</div>
        <div style="font-size: 15px; font-weight: bold; text-transform: uppercase; letter-spacing: 1px; opacity: 0.85;">{title}</div>
        <div style="font-size: 32px; font-weight: 900; margin-top: 5px;">{value}</div>
        </div>"""
        
    c1, c2, c3, c4 = st.columns(4)
    c1.markdown(make_light_card(tr('کل طلباء', 'Total Students'), len(stud_df), "🎓", "linear-gradient(135deg, #fff8e1 0%, #ffecb3 100%)", "#f57f17"), unsafe_allow_html=True)
    c2.markdown(make_light_card(tr('کل سٹاف', 'Total Staff'), len(staff_df), "👨‍🏫", "linear-gradient(135deg, #f1f8e9 0%, #dcedc8 100%)", "#2e7d32"), unsafe_allow_html=True)
    c3.markdown(make_light_card(tr('کل آمدنی', 'Total Income'), f"Rs {total_income:,}", "💰", "linear-gradient(135deg, #fffde7 0%, #fff59d 100%)", "#827717"), unsafe_allow_html=True)
    c4.markdown(make_light_card(tr('موجودہ بیلنس', 'Current Balance'), f"Rs {curr_balance:,}", "🏦", "linear-gradient(135deg, #e8f5e9 0%, #c8e6c9 100%)", "#1b5e20"), unsafe_allow_html=True)

    st.write("---")
    
    # --- 5. نوٹس بورڈ, گراف اور چارٹس ---
    st.markdown(f"### 📢 {tr('تازہ ترین نوٹس (Recent Notices)', 'Recent Notices')}")
    try:
        notices_df = pd.read_sql("SELECT date, audience, title, details FROM notices ORDER BY id DESC LIMIT 3", conn)
        if not notices_df.empty:
            for _, n_row in notices_df.iterrows():
                st.info(f"**[{n_row['date']}] - {n_row['title']}** ({tr('کے لیے:', 'For:')} {n_row['audience']})\n\n{n_row['details']}")
        else:
            st.write(tr("کوئی نیا نوٹس نہیں۔", "No recent notices."))
    except: pass

    st.write("---")
    st.markdown(f"### 📊 {tr('سافٹ ویئر ڈیش بورڈ جائزہ', 'Software Dashboard Overview')}")
    c_chart1, c_chart2 = st.columns(2)
    
    with c_chart1:
        st.markdown(f"#### 💰 {tr('مالیاتی رپورٹ (آمدنی اور خرچ)', 'Financial Report (Income vs Expense)')}")
        try:
            acc_df_chart = pd.read_sql("SELECT date, type, amount FROM accounts", conn)
            if not acc_df_chart.empty:
                acc_df_chart['type'] = acc_df_chart['type'].apply(lambda x: 'Income' if x in ['آمدنی', 'Income'] else 'Expense')
                acc_pivot = acc_df_chart.groupby(['date', 'type'])['amount'].sum().unstack(fill_value=0)
                st.area_chart(acc_pivot, use_container_width=True)
            else: st.info(tr("مالیاتی ڈیٹا دستیاب نہیں۔", "No financial data available."))
        except: st.info(tr("مالیاتی ڈیٹا دستیاب نہیں۔", "No financial data available."))
            
    with c_chart2:
        st.markdown(f"#### 📈 {tr('حاضری کا رجحان', 'Attendance Trend (Present)')}")
        try:
            att_chart_df = pd.read_sql("SELECT date, type, count(*) as count FROM attendance WHERE status IN ('Present', '🟢 Present', '🟢 حاضر') GROUP BY date, type ORDER BY date DESC LIMIT 30", conn)
            if not att_chart_df.empty:
                att_chart_df['type'] = att_chart_df['type'].apply(lambda x: 'Students' if x in ['طالب علم', 'Student'] else 'Staff')
                att_pivot = att_chart_df.pivot(index='date', columns='type', values='count').fillna(0)
                st.line_chart(att_pivot, use_container_width=True)
            else: st.info(tr("حاضری کا ڈیٹا دستیاب نہیں۔", "No attendance data available."))
        except: st.info(tr("حاضری کا ڈیٹا دستیاب نہیں۔", "No attendance data available."))
            
    st.markdown(f"#### 🏆 {tr('کلاس وار تعلیمی کارکردگی (اوسط مارکس %)', 'Class-wise Academic Performance (Avg %)')}")
    try:
        acad_df = pd.read_sql("SELECT s.class, em.obtained_marks, em.total_marks FROM exam_marks em JOIN students s ON em.reg_id = s.reg_id", conn)
        if not acad_df.empty:
            acad_df['percentage'] = (acad_df['obtained_marks'] / acad_df['total_marks']) * 100
            class_perf = acad_df.groupby('class')['percentage'].mean().reset_index()
            class_perf.set_index('class', inplace=True)
            st.bar_chart(class_perf, use_container_width=True)
        else: st.info(tr("امتحانات کا ڈیٹا دستیاب نہیں۔", "No academic data available."))
    except: st.info(tr("امتحانات کا ڈیٹا دستیاب نہیں۔", "No academic data available."))

# ================= 2. سکول پروفائل =================
elif core_choice == "School Profile":
    st.title("🏫 School Details")
    with st.form("school_profile_form"):
        p_name = st.text_input("Full School Name", value=school_name)
        p_address = st.text_input("Full Address", value=school_address)
        col1, col2, col3 = st.columns(3)
        p_phone = col1.text_input("Phone No", value=school_phone)
        p_whatsapp = col2.text_input("WhatsApp No", value=school_whatsapp)
        p_email = col3.text_input("Email ID", value=school_email)
        col4, col5, col6 = st.columns(3)
        p_website = col4.text_input("Website", value=school_website)
        p_facebook = col5.text_input("Facebook", value=school_facebook)
        p_reg = col6.text_input("Registration No", value=school_reg)
        p_logo = st.file_uploader("Upload Logo", type=["png", "jpg", "jpeg"])
        if st.form_submit_button("Save Details"):
            for k, v in [("school_name", p_name), ("school_address", p_address), ("school_phone", p_phone), ("school_whatsapp", p_whatsapp), ("school_email", p_email), ("school_website", p_website), ("school_facebook", p_facebook), ("school_reg", p_reg)]:
                cursor.execute("DELETE FROM settings WHERE key=?", (k,))
                cursor.execute("INSERT INTO settings (key, value) VALUES (?, ?)", (k, v))
            if p_logo:
                cursor.execute("DELETE FROM settings WHERE key='school_logo'")
                cursor.execute("INSERT INTO settings (key, blob_value) VALUES ('school_logo', ?)", (sqlite3.Binary(p_logo.read()),))
            conn.commit()
            st.success("Details Saved Successfully!")
            st.rerun()

# ================= 3. طلباء مینجمنٹ =================
elif core_choice == "Students Mgt":
    st.markdown(f"<h2>🎓 {tr('طلباء مینجمنٹ', 'Students Management')} - {tr(sub_choice, sub_choice)}</h2>", unsafe_allow_html=True)
    
    def generate_student_profile_html(reg_no):
        stu = pd.read_sql(f"SELECT * FROM students WHERE reg_id='{reg_no}'", conn)
        if stu.empty: return ""
        row = stu.iloc[0]
        try: dob_fmt = datetime.datetime.strptime(row.get("dob", "2015-01-01"), "%Y-%m-%d").strftime("%d-%m-%Y")
        except: dob_fmt = row.get("dob", "")
        try: adm_fmt = datetime.datetime.strptime(row.get("adm_date", "2023-01-01"), "%Y-%m-%d").strftime("%d-%m-%Y")
        except: adm_fmt = row.get("adm_date", "")
        
        photo_data = row.get("photo")
        student_photo_html = '<div style="width:110px; height:130px; border:1px solid #000; text-align:center; line-height:130px; font-size:12px; background:#f9f9f9; color:#999; float:right;">Photo</div>'
        if photo_data:
            b64_photo = base64.b64encode(photo_data).decode()
            student_photo_html = f'<img src="data:image/jpeg;base64,{b64_photo}" style="width:110px; height:130px; object-fit:cover; border:1px solid #000; display:block !important; float:right;">'
        
        t = {"align": "left", "dir": "ltr"} if st.session_state.ui_lang == "English" else {"align": "right", "dir": "rtl"}
        raw_g = str(row.get('g_type', 'Father'))
        lbl_fname = tr("سرپرست کا نام:", "Guardian's name:") if "Guardian" in raw_g or "سرپرست" in raw_g else tr("والد کا نام:", "Father's name:")
        
        raw_gender = str(row.get('gender', 'Boy'))
        disp_gender = tr("لڑکی", "Girl") if "Girl" in raw_gender or "لڑکی" in raw_gender else (tr("دیگر", "Other") if "Other" in raw_gender or "دیگر" in raw_gender else tr("لڑکا", "Boy"))
            
        d_name = get_disp_val(row['name'], row.get('name_en'))
        d_fname = get_disp_val(row['fname'], row.get('fname_en'))
        d_address = get_disp_val(row['address'], row.get('address_en'))
        
        local_logo = logo_src_b64 if 'logo_src_b64' in locals() or 'logo_src_b64' in globals() else ""
        logo_base64_html = f'<img src="{local_logo}" style="width: 50px; height: 50px; object-fit: contain;">' if local_logo else '<div style="font-size:28px;">🏫</div>'
        
        logo_td = f'<td style="width: 20%; vertical-align: middle;">{logo_base64_html}</td>'
        photo_td = f'<td style="width: 20%; vertical-align: middle;">{student_photo_html}</td>'

        return f"""
        <div style="border: 2px solid black; padding: 10px; width: 95%; max-width: 740px; margin: 0 auto; box-sizing: border-box; font-family: Arial, sans-serif;" dir="{t['dir']}">
        <table style="width:100%; border:none;"><tr>{logo_td}
        <td style="width: 60%; text-align: center; vertical-align: middle;"><h2 style="margin: 0; color: #1a4f8b;">{school_name.upper()}</h2>
        <p style="margin: 2px 0 0 0; font-weight: bold; font-size:15px;">{school_address}</p>
        <p style="margin: 2px 0 0 0; text-decoration: underline; font-weight: bold;">{tr('طالب علم کا داخلہ فارم', 'STUDENT ADMISSION FORM')}</p></td>
        {photo_td}</tr></table>
        <table style="width:100%; border-collapse: collapse; margin-top: 10px;" dir="{t['dir']}">
        <tr><td colspan="4" style="background-color:#e0e0e0; text-align:center; font-weight:bold; font-size: 16px; border: 1px solid black;">{tr('ذاتی معلومات', 'Personal Information')}</td></tr>
        <tr><th style="border: 1px solid black; padding: 4px; text-align: {t['align']}; width: 20%;">{tr('نام:', 'Name:')}</th><td style="border: 1px solid black; padding: 4px; text-align: {t['align']}; width: 30%;">{d_name}</td>
        <th style="border: 1px solid black; padding: 4px; text-align: {t['align']}; width: 20%;">{tr('جنس:', 'Gender:')}</th><td style="border: 1px solid black; padding: 4px; text-align: {t['align']}; width: 30%;">{disp_gender}</td></tr>
        <tr><th style="border: 1px solid black; padding: 4px; text-align: {t['align']};">{tr('تاریخ پیدائش:', 'DOB:')}</th><td style="border: 1px solid black; padding: 4px; text-align: {t['align']};">{dob_fmt}</td>
        <th style="border: 1px solid black; padding: 4px; text-align: {t['align']};">{tr('ب فارم نمبر:', 'B-Form:')}</th><td style="border: 1px solid black; padding: 4px; text-align: {t['align']};">{row['bform']}</td></tr>
        <tr><th style="border: 1px solid black; padding: 4px; text-align: {t['align']};">{tr('بلڈ گروپ:', 'Blood Group:')}</th><td style="border: 1px solid black; padding: 4px; text-align: {t['align']};">{row['blood']}</td>
        <th style="border: 1px solid black; padding: 4px; text-align: {t['align']};">{tr('فون نمبر:', 'Phone No:')}</th><td style="border: 1px solid black; padding: 4px; text-align: {t['align']};">{row['phone']}</td></tr>
        <tr><td colspan="4" style="background-color:#e0e0e0; text-align:center; font-weight:bold; font-size: 16px; border: 1px solid black;">{tr('والدین کی معلومات', 'Parents Information')}</td></tr>
        <tr><th style="border: 1px solid black; padding: 4px; text-align: {t['align']};">{lbl_fname}</th><td style="border: 1px solid black; padding: 4px; text-align: {t['align']};">{d_fname}</td>
        <th style="border: 1px solid black; padding: 4px; text-align: {t['align']};">{tr('شناختی کارڈ:', 'CNIC:')}</th><td style="border: 1px solid black; padding: 4px; text-align: {t['align']};">{row['fcnic']}</td></tr>
        <tr><th style="border: 1px solid black; padding: 4px; text-align: {t['align']};">{tr('والدہ کا نام:', "Mother's Name:")}</th><td style="border: 1px solid black; padding: 4px; text-align: {t['align']};">{row['mname']}</td>
        <th style="border: 1px solid black; padding: 4px; text-align: {t['align']};">{tr('شناختی کارڈ:', 'CNIC:')}</th><td style="border: 1px solid black; padding: 4px; text-align: {t['align']};">{row['mcnic']}</td></tr>
        <tr><th style="border: 1px solid black; padding: 4px; text-align: {t['align']};">{tr('والد کا پیشہ:', "Father's Profession:")}</th><td style="border: 1px solid black; padding: 4px; text-align: {t['align']};">{row.get('f_prof', '')}</td>
        <th style="border: 1px solid black; padding: 4px; text-align: {t['align']};">{tr('مکمل پتہ:', 'Address:')}</th><td style="border: 1px solid black; padding: 4px; text-align: {t['align']};">{d_address}</td></tr>
        <tr><td colspan="4" style="background-color:#e0e0e0; text-align:center; font-weight:bold; font-size: 16px; border: 1px solid black;">{tr('دفتری معلومات', 'Office Information')}</td></tr>
        <tr><th style="border: 1px solid black; padding: 4px; text-align: {t['align']};">{tr('داخلہ نمبر:', 'Admission No:')}</th><td style="border: 1px solid black; padding: 4px; text-align: {t['align']};">{row['reg_id']}</td>
        <th style="border: 1px solid black; padding: 4px; text-align: {t['align']};">{tr('تاریخ داخلہ:', 'Admission Date:')}</th><td style="border: 1px solid black; padding: 4px; text-align: {t['align']};">{adm_fmt}</td></tr>
        <tr><th style="border: 1px solid black; padding: 4px; text-align: {t['align']};">{tr('کلاس / سیکشن:', 'Class / Sec:')}</th><td style="border: 1px solid black; padding: 4px; text-align: {t['align']};">{row['class']} ( {row['section']} )</td>
        <th style="border: 1px solid black; padding: 4px; text-align: {t['align']};">{tr('سابقہ سکول:', 'Prev School:')}</th><td style="border: 1px solid black; padding: 4px; text-align: {t['align']};">{row['prev_school']}</td></tr>
        <tr><th style="border: 1px solid black; padding: 4px; text-align: {t['align']};">{tr('مقررہ فیس:', 'Monthly Fee:')}</th><td style="border: 1px solid black; padding: 4px; text-align: {t['align']};">Rs {safe_int(row['monthly_fee'])}</td>
        <th style="border: 1px solid black; padding: 4px; text-align: {t['align']};">{tr('میڈیکل ہسٹری:', 'Medical Info:')}</th><td style="border: 1px solid black; padding: 4px; text-align: {t['align']};">{row['medical']}</td></tr>
        </table>
        <table style="width:100%; border:none; margin-top:20px;" dir="{t['dir']}">
        <tr><td style="text-align: {t['align']}; width: 50%;"><b>{tr('والد/سرپرست کے دستخط:', 'Parent Signature:')}</b> ___________________</td>
        <td style="text-align: {'left' if st.session_state.ui_lang == 'اردو' else 'right'}; width: 50%;"><b>{tr('پرنسپل کے دستخط:', 'Principal Sig:')}</b> ___________________</td></tr>
        </table></div>"""

    if sub_choice == "New Admission":
        with st.form("student_form", clear_on_submit=True):
            stud_count = pd.read_sql("SELECT COUNT(*) FROM students", conn).iloc[0, 0]
            auto_reg_no = "1001" if stud_count == 0 else str(safe_int(pd.read_sql("SELECT MAX(CAST(reg_id AS INTEGER)) FROM students", conn).iloc[0, 0]) + 1)
            st.markdown(f"### {tr('رجسٹریشن نمبر', 'Reg No')}: `{auto_reg_no}`")
            
            c1, c2, c3 = st.columns([1.5, 1, 1])
            name = c1.text_input(tr("طالب علم کا نام *", "Student Name *"))
            gender_disp = c2.selectbox(tr("جنس", "Gender"), [tr("لڑکا", "Boy"), tr("لڑکی", "Girl"), tr("دیگر", "Other")])
            gender = "Boy" if gender_disp in ["لڑکا", "Boy"] else ("Girl" if gender_disp in ["لڑکی", "Girl"] else "Other")
            student_photo = c3.file_uploader(tr("طالب علم کی تصویر", "Student Photo"), type=["jpg", "jpeg", "png"])
            
            c4, c5, c6 = st.columns(3)
            student_dob = c4.date_input(tr("تاریخ پیدائش", "Date of Birth"), min_value=datetime.date(1970, 1, 1), max_value=datetime.date.today(), value=datetime.date(2015, 1, 1))
            blood_disp = c5.selectbox(tr("بلڈ گروپ", "Blood Group"), [tr("نامعلوم", "Unknown"), "A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"])
            blood_group = "Unknown" if blood_disp in ["نامعلوم", "Unknown"] else blood_disp
            b_form = c6.text_input(tr("ب فارم نمبر", "B-Form No"))
            
            c7_1, c7_2, c7_3 = st.columns([1, 1.5, 1.5])
            g_disp = c7_1.selectbox(tr("رشتہ", "Relation"), [tr("والد", "Father"), tr("سرپرست", "Guardian")])
            g_type = "Father" if g_disp in ["والد", "Father"] else "Guardian"
            father_name = c7_2.text_input(tr("والد/سرپرست کا نام", "Father/Guardian Name"))
            fcnic = c7_3.text_input(tr("شناختی کارڈ نمبر", "CNIC No"))
            
            c9, c10, c_prof = st.columns([1, 1, 1])
            mname = c9.text_input(tr("والدہ کا نام", "Mother's Name"))
            mcnic = c10.text_input(tr("والدہ کا شناختی کارڈ", "Mother's CNIC"))
            f_prof = c_prof.text_input(tr("والد کا پیشہ", "Father's Profession"))
            
            c11, c12 = st.columns([1, 2])
            phone = c11.text_input(tr("فون نمبر", "Phone No"))
            address = c12.text_input(tr("مکمل پتہ", "Full Address"))
            
            c13, c14, c15, c16 = st.columns(4)
            student_class = c13.selectbox(tr("موجودہ کلاس", "Current Class"), classes_list)
            student_section = c14.selectbox(tr("سیکشن", "Section"), ["A", "B", "C", "D", "Model"])
            prev_school = c15.text_input(tr("سابقہ سکول", "Previous School"))
            prev_class = c16.text_input(tr("سابقہ کلاس", "Previous Class"))
            
            c17, c18, c19, c20 = st.columns(4)
            fixed_fee = c17.number_input(tr("مقررہ ماہانہ فیس *", "Monthly Fee *"), min_value=0)
            initial_arrears = c18.number_input(tr("سابقہ بقایا جات", "Previous Arrears"), min_value=0, value=0)
            admission_date = c19.date_input(tr("تاریخِ داخلہ", "Admission Date"), max_value=datetime.date.today())
            medical_info = c20.text_input(tr("کوئی میڈیکل پیچیدگی؟", "Any Medical Issue?"))
            
            st.markdown(f"#### 🔒 {tr('والدین کا پورٹل لاگ ان (Parent Portal Login)', 'Parent Portal Login')}")
            c_log1, c_log2 = st.columns(2)
            guardian_username = c_log1.text_input(tr("یوزر نیم (مثلاً ان کا فون نمبر) *", "Username (e.g. Phone No) *"))
            guardian_password = c_log2.text_input(tr("پاسورڈ *", "Password *"), type="password")
            
            submit_btn = st.form_submit_button(tr("طالب علم اور اکاؤنٹ محفوظ کریں", "Save Student & Account"))
            
            if submit_btn:
                if not name:
                    st.error(tr("طالب علم کا نام لکھنا لازمی ہے!", "Student name is required!"))
                elif guardian_username.strip() == "" or guardian_password.strip() == "":
                    st.error(tr("والدین کے لاگ ان کے لیے یوزر نیم اور پاسورڈ لازمی ہیں!", "Parent username and password are required!"))
                else:
                    photo_data = student_photo.read() if student_photo else None
                    n_en = name if st.session_state.ui_lang == "English" else ""
                    fn_en = father_name if st.session_state.ui_lang == "English" else ""
                    ad_en = address if st.session_state.ui_lang == "English" else ""
                    
                    try:
                        cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", 
                                       (guardian_username.strip(), guardian_password.strip(), "Guardian"))
                        
                        cursor.execute("""
                            INSERT INTO students 
                            (reg_id, name, fname, dob, blood, class, section, bform, phone, address, prev_school, prev_class, medical, monthly_fee, adm_date, arrears, gender, mname, fcnic, mcnic, photo, g_type, f_prof, name_en, fname_en, address_en, status) 
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'Active')
                        """, (auto_reg_no, name, father_name, student_dob.strftime("%Y-%m-%d"), blood_group, student_class, student_section, b_form, phone, address, prev_school, prev_class, medical_info, fixed_fee, admission_date.strftime("%Y-%m-%d"), initial_arrears, gender, mname, fcnic, mcnic, photo_data, g_type, f_prof, n_en, fn_en, ad_en))
                        
                        conn.commit()
                        st.success(tr("✅ طالب علم کا داخلہ اور والدین کا اکاؤنٹ کامیابی سے محفوظ ہو گیا!", "Student record and parent account saved successfully!"))
                    except sqlite3.IntegrityError:
                        st.error(tr("⚠️ یہ یوزر نیم پہلے سے موجود ہے۔ برائے مہربانی والدین کے لیے کوئی منفرد نام (جیسے فون نمبر) استعمال کریں۔", "Username already exists. Please use a unique one like a phone number."))
                    except Exception as e: 
                        st.error(f"Error saving student: {e}")

    elif sub_choice == "Edit Record":
        st.markdown("### ✏️ طالب علم کا ریکارڈ ایڈٹ کریں")
        edit_reg = st.text_input(tr("رجسٹریشن نمبر لکھیں (مثلاً: 1001)", "Enter Registration No to Edit"))
        
        if edit_reg:
            stu_match = pd.read_sql(f"SELECT * FROM students WHERE reg_id='{edit_reg}'", conn)
            if not stu_match.empty:
                stu_data = stu_match.iloc[0]
                
                # 🟢 ڈیٹا بیس فکسر (خود کار طور پر مسنگ کالم بنائے گا)
                for col in ['name_en', 'fname_en', 'address_en', 'gender', 'mname', 'fcnic', 'mcnic', 'g_type', 'f_prof', 'bform']:
                    try: 
                        cursor.execute(f"ALTER TABLE students ADD COLUMN {col} TEXT")
                        conn.commit()
                    except: pass

                # 🟢 پیرنٹ کا اکاؤنٹ فائنڈر
                phone_val = str(stu_data.get('phone', '')).strip()
                parent_user = f"parent_{edit_reg}"
                
                cursor.execute("SELECT username, password FROM users WHERE username=? OR (username=? AND username!='')", (parent_user, phone_val))
                user_row = cursor.fetchone()
                
                if user_row:
                    def_u, def_p = user_row[0], user_row[1]
                    acc_status = "<span style='color: green;'>✅ (پہلے سے اکاؤنٹ موجود ہے)</span>"
                else:
                    def_u, def_p = parent_user, "1234"
                    acc_status = "<span style='color: #d69e2e;'>⚠️ (نیا اکاؤنٹ بنے گا)</span>"

                with st.form("edit_student_form"):
                    curr_name = get_disp_val(stu_data.get("name", ""), stu_data.get("name_en", ""))
                    curr_fname = get_disp_val(stu_data.get("fname", ""), stu_data.get("fname_en", ""))
                    curr_address = get_disp_val(stu_data.get("address", ""), stu_data.get("address_en", ""))
                    
                    c1, c2, c3, c4 = st.columns(4)
                    e_name = c1.text_input(tr("نام", "Name"), value=curr_name)
                    e_gender = c2.selectbox(tr("جنس", "Gender"), ["Boy", "Girl", "Other"], index=["Boy", "Girl", "Other"].index(stu_data.get("gender", "Boy") or "Boy"))
                    e_g_type = c3.selectbox(tr("رشتہ", "Relation"), ["Father", "Guardian"], index=["Father", "Guardian"].index(stu_data.get("g_type", "Father") or "Father"))
                    e_fname = c4.text_input(tr("والد/سرپرست کا نام", "Relation Name"), value=curr_fname)
                    
                    c5, c6, c7, c8 = st.columns(4)
                    e_fcnic = c5.text_input(tr("شناختی کارڈ", "CNIC"), value=str(stu_data.get("fcnic", "")))
                    e_mname = c6.text_input(tr("والدہ کا نام", "Mother Name"), value=str(stu_data.get("mname", "")))
                    e_mcnic = c7.text_input(tr("والدہ کا شناختی کارڈ", "Mother CNIC"), value=str(stu_data.get("mcnic", "")))
                    e_bform = c8.text_input(tr("ب فارم نمبر", "B-Form"), value=str(stu_data.get("bform", "")))
                    
                    c_prof_e, c10, c11, c12 = st.columns(4)
                    e_fprof = c_prof_e.text_input(tr("والد کا پیشہ", "Father's Profession"), value=str(stu_data.get("f_prof", "")))
                    bg_opts = ["Unknown", "A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]
                    curr_bg = stu_data.get("blood", "Unknown")
                    e_blood_val = c10.selectbox(tr("بلڈ گروپ", "Blood Group"), bg_opts, index=bg_opts.index(curr_bg) if curr_bg in bg_opts else 0)
                    try: e_dob_val = datetime.datetime.strptime(stu_data.get("dob", "2015-01-01"), "%Y-%m-%d").date()
                    except: e_dob_val = datetime.date(2015, 1, 1)
                    e_dob = c11.date_input(tr("تاریخ پیدائش", "DOB"), value=e_dob_val)
                    e_phone = c12.text_input(tr("فون نمبر", "Phone No"), value=str(stu_data.get("phone", "")))
                    
                    c13, c14, c15, c16 = st.columns(4)
                    e_class = c13.selectbox(tr("کلاس", "Class"), classes_list, index=classes_list.index(stu_data.get("class")) if stu_data.get("class") in classes_list else 0)
                    sections_opts = ["A", "B", "C", "D", "Model"]
                    e_sec = c14.selectbox(tr("سیکشن", "Section"), sections_opts, index=sections_opts.index(stu_data.get("section", "A") or "A"))
                    e_prev_school = c15.text_input(tr("سابقہ سکول", "Prev School"), value=str(stu_data.get("prev_school", "")))
                    e_prev_class = c16.text_input(tr("سابقہ کلاس", "Prev Class"), value=str(stu_data.get("prev_class", "")))
                    
                    c17, c18, c19, c20 = st.columns(4)
                    e_fee = c17.number_input(tr("مقررہ فیس", "Monthly Fee"), value=safe_int(stu_data.get("monthly_fee", 0)))
                    e_arrears = c18.number_input(tr("بقایا جات", "Arrears"), value=safe_int(stu_data.get("arrears", 0)))
                    try: e_adm_val = datetime.datetime.strptime(stu_data.get("adm_date", "2023-01-01"), "%Y-%m-%d").date()
                    except: e_adm_val = datetime.date.today()
                    e_adm_date = c19.date_input(tr("تاریخِ داخلہ", "Adm Date"), value=e_adm_val)
                    e_address = c20.text_input(tr("مکمل پتہ", "Full Address"), value=curr_address)
                    
                    # 🟢 پورٹل لاگ ان اور سیو بٹن
                    st.markdown(f"#### 🔒 {tr('والدین کا پورٹل لاگ ان', 'Parent Portal Login')} {acc_status}", unsafe_allow_html=True)
                    c_log1, c_log2 = st.columns(2)
                    e_username = c_log1.text_input(tr("یوزر نیم (Username)", "Username"), value=def_u)
                    e_password = c_log2.text_input(tr("پاسورڈ (Password)", "Password"), value=def_p)

                    if st.form_submit_button(tr("تبدیلیاں محفوظ کریں", "Save Changes"), type="primary"):
                        try:
                            # 🟢 مضبوط پیرامیٹرائزڈ کیوری (جو کبھی کریش نہیں ہوگی)
                            if st.session_state.ui_lang == "اردو":
                                cursor.execute("""
                                    UPDATE students SET 
                                    name=?, gender=?, mname=?, fcnic=?, mcnic=?, class=?, section=?, 
                                    prev_school=?, prev_class=?, f_prof=?, phone=?, monthly_fee=?, arrears=?, 
                                    adm_date=?, blood=?, bform=?, g_type=?, dob=?, fname=?, address=?
                                    WHERE reg_id=?
                                """, (e_name, e_gender, e_mname, e_fcnic, e_mcnic, e_class, e_sec, e_prev_school, e_prev_class, e_fprof, e_phone, float(e_fee), float(e_arrears), e_adm_date.strftime("%Y-%m-%d"), e_blood_val, e_bform, e_g_type, e_dob.strftime("%Y-%m-%d"), e_fname, e_address, edit_reg))
                            else:
                                cursor.execute("""
                                    UPDATE students SET 
                                    name_en=?, gender=?, mname=?, fcnic=?, mcnic=?, class=?, section=?, 
                                    prev_school=?, prev_class=?, f_prof=?, phone=?, monthly_fee=?, arrears=?, 
                                    adm_date=?, blood=?, bform=?, g_type=?, dob=?, fname_en=?, address_en=?
                                    WHERE reg_id=?
                                """, (e_name, e_gender, e_mname, e_fcnic, e_mcnic, e_class, e_sec, e_prev_school, e_prev_class, e_fprof, e_phone, float(e_fee), float(e_arrears), e_adm_date.strftime("%Y-%m-%d"), e_blood_val, e_bform, e_g_type, e_dob.strftime("%Y-%m-%d"), e_fname, e_address, edit_reg))

                            # 🟢 یوزر اکاؤنٹ اپڈیٹ یا نیا بنانا
                            if e_username.strip():
                                cursor.execute("SELECT id FROM users WHERE username=?", (e_username.strip(),))
                                if cursor.fetchone():
                                    cursor.execute("UPDATE users SET password=?, role='Guardian' WHERE username=?", (e_password.strip(), e_username.strip()))
                                else:
                                    cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, 'Guardian')", (e_username.strip(), e_password.strip()))
                            
                            conn.commit()
                            st.success(tr("✅ ریکارڈ اور پورٹل اکاؤنٹ کامیابی سے اپڈیٹ ہو گئے۔", "Record updated successfully!"))
                            time.sleep(1)
                            st.rerun()
                            
                        except Exception as db_err:
                            st.error(f"🛑 Error: {db_err}")
            else:
                st.warning(tr("اس رجسٹریشن نمبر کا کوئی ریکارڈ نہیں ملا۔", "No record found."))

    elif sub_choice in ["Search", "🔍 تلاش"]:
        st.markdown(f"### &#128269; {tr('طلباء تلاش کریں (Student Search)', 'Search Students')}", unsafe_allow_html=True)
        st.write(tr("یہاں سے آپ طلباء کا ریکارڈ نام، رجسٹریشن نمبر، کلاس اور ب-فارم کے ذریعے باآسانی تلاش کر سکتے ہیں۔", "Search students by Name, Reg No, Class, or B-Form."))
        
        # 🟢 سمارٹ اور ایڈوانسڈ سرچ فلٹرز
        with st.expander(tr("تلاش اور فلٹرز (Search & Filters)", "Search & Filters"), expanded=True):
            c_s1, c_s2, c_s3, c_s4 = st.columns(4)
            
            f_reg = c_s1.text_input(tr("رجسٹریشن نمبر", "Registration No"), placeholder="مثلاً: 1001")
            f_name = c_s2.text_input(tr("طالب علم کا نام", "Student Name"), placeholder="مثلاً: Ali")
            
            try: 
                db_cls = pd.read_sql("SELECT class_name FROM sys_classes", conn)['class_name'].tolist()
            except: 
                db_cls = ["Play Group", "Nursery", "Prep", "1st", "2nd", "3rd", "4th", "5th", "6th", "7th", "8th", "9th", "10th"]
                
            f_class = c_s3.selectbox(tr("کلاس (Class)", "Class"), ["All"] + db_cls)
            f_bform = c_s4.text_input(tr("ب-فارم / CNIC", "B-Form / CNIC"), placeholder="38403-...")
            
            if st.button(tr("فلٹرز صاف کریں (Clear Filters)", "Clear Filters")):
                st.rerun()
                
        # 🟢 ڈائنیمک کیوری (شرائط کے مطابق)
        # ڈیٹا بیس میں کالم b_form یا cnic ہو سکتا ہے، اس لیے ہم محفوظ طریقہ استعمال کریں گے
        try:
            # کالمز چیک کرنے کے لیے
            test_df = pd.read_sql("SELECT * FROM students LIMIT 1", conn)
            bform_col = 'b_form' if 'b_form' in test_df.columns else ('cnic' if 'cnic' in test_df.columns else '')
        except:
            bform_col = 'b_form'

        base_query = f"SELECT reg_id, name, fname, class, section, phone, {bform_col if bform_col else "'' as b_form"}, status FROM students WHERE 1=1"
        
        if f_reg.strip():
            base_query += f" AND reg_id LIKE '%{f_reg.strip()}%'"
        if f_name.strip():
            base_query += f" AND (name LIKE '%{f_name.strip()}%' OR name_en LIKE '%{f_name.strip()}%')"
        if f_class != "All":
            base_query += f" AND class = '{f_class}'"
        if f_bform.strip() and bform_col:
            base_query += f" AND {bform_col} LIKE '%{f_bform.strip()}%'"
            
        base_query += " ORDER BY class, CAST(reg_id AS INTEGER)"
        
        try:
            search_df = pd.read_sql(base_query, conn)
        except Exception as e:
            search_df = pd.DataFrame()
            st.error(f"Error fetching records: {e}")
                
        # 🟢 رزلٹ ظاہر کرنا
        if not search_df.empty:
            st.success(f"✅ {tr('کل', 'Total')} **{len(search_df)}** {tr('طلباء کا ریکارڈ ملا', 'records found')}")
            
            if st.session_state.ui_lang == "اردو":
                search_df.columns = ['رجسٹریشن نمبر', 'طالب علم کا نام', 'والد کا نام', 'کلاس', 'سیکشن', 'موبائل نمبر', 'ب-فارم/CNIC', 'سٹیٹس']
                search_df['سٹیٹس'] = search_df['سٹیٹس'].replace({'Active': 'فعال (Active)', 'Inactive': 'غیر فعال', 'Struck Off': 'خارج شدہ'})
            else:
                search_df.columns = ['Reg No', 'Student Name', 'Father Name', 'Class', 'Section', 'Phone', 'B-Form/CNIC', 'Status']
                
            st.dataframe(search_df, use_container_width=True, hide_index=True)
        else:
            st.info(tr("دی گئی معلومات کے مطابق کوئی طالب علم نہیں ملا۔", "No student found matching the provided criteria."))
                
    elif sub_choice == "Print Profile":
        c_pr1, c_pr2 = st.columns([2, 1])
        print_reg = c_pr1.text_input(tr("رول نمبر درج کریں:", "Enter Reg No to Print:"), key="print_profile_reg")
        if print_reg:
            html_output = generate_student_profile_html(print_reg)
            if html_output: print_button_js(html_output, "Print Admission Form", landscape=False)
            else: st.warning(tr("نمبر نہیں ملا۔", "No record found."))

    elif sub_choice in ["Certificates", "سرٹیفکیٹس", "🎓 سرٹیفکیٹس"]:
        st.markdown(f"### 🎓 {tr('سرٹیفکیٹ اور سند جنریٹر', 'Certificate & Sanad Generator')}")
        st.write(tr("یہاں سے آپ طلباء کے لیے خوبصورت ڈیزائن والے سرٹیفکیٹ اور فارغ التحصیل طلباء کے لیے سند جاری کر سکتے ہیں۔", "Generate beautifully designed certificates and graduation Sanads for students here."))
        
        c_cert1, c_cert2 = st.columns([1, 2])
        cert_type = c_cert1.selectbox(tr("سرٹیفکیٹ کی قسم", "Certificate Type"), ["School Leaving Certificate", "Character Certificate", "Graduation Certificate (سند)"])
        
        all_st_df = pd.read_sql("SELECT reg_id, name, fname, class, gender, bform, g_type FROM students", conn)
        if not all_st_df.empty:
            all_st_df['reg_id'] = all_st_df['reg_id'].astype(str)
            
            stu_list = [f"{r['name']} (S/O {r['fname']}) - Reg: {r['reg_id']} - Class: {r['class']}" for _, r in all_st_df.iterrows()]
            sel_stu = c_cert2.selectbox(tr("طالب علم منتخب کریں", "Select Student"), stu_list)
            
            sel_reg = str(sel_stu.split("Reg: ")[1].split(" - ")[0]).strip()
            
            matching_rows = all_st_df[all_st_df['reg_id'] == sel_reg]
            
            if not matching_rows.empty:
                stu_data = matching_rows.iloc[0]
                
                c_cert3, c_cert4 = st.columns(2)
                issue_date = c_cert3.date_input(tr("تاریخِ اجراء", "Issue Date"), datetime.date.today())
                remarks = c_cert4.text_input(tr("ریمارکس / کردار (Conduct)", "Remarks / Conduct"), value="Excellent and obedient.")
                
                if st.button(tr("سرٹیفکیٹ تیار کریں (Generate Certificate)", "Generate Certificate"), type="primary"):
                    try:
                        g_val = str(stu_data.get('gender', 'Boy')).strip().lower()
                        rel_type = str(stu_data.get('g_type', 'Father')).strip()
                        
                        if g_val in ['girl', 'female', 'عورت', 'لڑکی']:
                            pron_sub = "She"
                            pron_obj = "her"
                            pron_pos = "her"
                            rel_text = "daughter"
                        else:
                            pron_sub = "He"
                            pron_obj = "him"
                            pron_pos = "his"
                            rel_text = "son"
                            
                        if rel_type in ["Guardian", "سرپرست"]:
                            rel_text = "ward"
                        
                        stu_name = str(stu_data['name']).strip()
                        f_name = str(stu_data['fname']).strip()
                        s_class = str(stu_data['class']).strip()
                        s_reg = str(stu_data['reg_id']).strip()
                        
                        s_bform = str(stu_data.get('bform', '-')).strip()
                        if not s_bform or s_bform == 'nan' or s_bform == 'None': s_bform = "N/A"
                        
                        try:
                            photo_query = pd.read_sql(f"SELECT photo FROM students WHERE reg_id='{s_reg}'", conn)
                            photo_data = photo_query.iloc[0]['photo'] if not photo_query.empty else None
                        except: photo_data = None
                        
                        if photo_data:
                            b64_photo = base64.b64encode(photo_data).decode()
                            stu_photo_html = f'<img src="data:image/jpeg;base64,{b64_photo}" style="width: 90px; height: 110px; object-fit: cover; border: 2px solid #1a4f8b; padding: 2px; background: white; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">'
                        else:
                            stu_photo_html = '<div style="width: 90px; height: 110px; border: 2px dashed #1a4f8b; display: flex; align-items: center; justify-content: center; color: #777; font-size: 11px; font-weight: bold; background: #f9f9f9;">Photo</div>'
                        
                        if cert_type == "Graduation Certificate (سند)":
                            title_disp = "CERTIFICATE OF GRADUATION"
                            body_text = f"""This is to proudly certify that <b>{stu_name}</b> {rel_text} of <b>{f_name}</b> 
                            (Reg No: <b>{s_reg}</b>, B-Form: <b>{s_bform}</b>) 
                            has successfully completed {pron_pos} academic journey at our institution up to <b>Class {s_class}</b>.<br><br>
                            Throughout {pron_pos} academic tenure, {pron_pos} performance, dedication, and character remained <b>{remarks}</b>. 
                            {pron_sub} graduates today as a proud alumnus of {school_name}. We wish {pron_obj} a very bright, successful, and prosperous future."""
                        
                        elif cert_type == "Character Certificate":
                            title_disp = "CHARACTER CERTIFICATE"
                            body_text = f"""This is to certify that <b>{stu_name}</b> {rel_text} of <b>{f_name}</b> 
                            (Reg No: <b>{s_reg}</b>, B-Form: <b>{s_bform}</b>) 
                            is/was a bonafide student of this institution studying in <b>Class {s_class}</b>.<br><br>
                            During {pron_pos} stay at the school, {pron_pos} general conduct, moral character, and behavior was found to be <b>{remarks}</b>. 
                            {pron_sub} bears a good moral character and has never taken part in any indisciplinary activities. We wish {pron_obj} success in all future endeavors."""
                        
                        else:
                            title_disp = "SCHOOL LEAVING CERTIFICATE"
                            body_text = f"""This is to certify that <b>{stu_name}</b> {rel_text} of <b>{f_name}</b> 
                            (Reg No: <b>{s_reg}</b>, B-Form: <b>{s_bform}</b>) 
                            was a bonafide student of this institution. {pron_sub} was admitted to this school and studied up to <b>Class {s_class}</b>. 
                            <br><br>
                            During {pron_pos} stay at the school, {pron_pos} general conduct and behavior was <b>{remarks}</b>. 
                            All {pron_pos} dues have been cleared. We wish {pron_obj} all the best for {pron_pos} future endeavors."""

                        cert_html = f"""
                        <div style="padding: 10px; font-family: 'Times New Roman', serif; box-sizing: border-box; width: 100%;">
                            <div style="border: 10px solid #1a4f8b; padding: 4px; background-color: #fcfcfc; box-sizing: border-box; height: 95vh; max-height: 740px; overflow: hidden; position: relative;">
                                <div style="border: 2px solid #d4af37; padding: 20px 40px; height: 100%; box-sizing: border-box; display: flex; flex-direction: column;">
                                    
                                    <div style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); width: 45%; opacity: 0.07; z-index: 0; display: flex; justify-content: center; align-items: center;">
                                        <img src="{logo_src_b64}" style="width: 100%;">
                                    </div>
                                    
                                    <table style="width: 100%; position: relative; z-index: 1;">
                                        <tr>
                                            <td style="width: 20%; text-align: left; vertical-align: middle;">{f'<img src="{logo_src_b64}" style="height: 90px; object-fit: contain;">' if logo_src_b64 else ''}</td>
                                            <td style="width: 60%; text-align: center; vertical-align: middle;">
                                                <h1 style="margin: 0; color: #1a4f8b; font-size: 34px; text-transform: uppercase; font-weight: 900; letter-spacing: 1px;">{school_name}</h1>
                                                <p style="margin: 4px 0; font-size: 15px; font-weight: bold; color: #333;">{school_address}</p>
                                                <p style="margin: 0; font-size: 13px; color: #555;">Reg No: {school_reg} &nbsp;|&nbsp; Ph: {school_phone}</p>
                                            </td>
                                            <td style="width: 20%; text-align: right; vertical-align: middle;">
                                                {stu_photo_html}
                                            </td>
                                        </tr>
                                    </table>
                                    
                                    <div style="border-bottom: 2px solid #d4af37; margin: 15px 0;"></div>
                                    
                                    <div style="text-align: center; margin: 10px 0 20px 0; position: relative; z-index: 1;">
                                        <span style="background-color: #1a4f8b; color: white; padding: 8px 30px; font-size: 22px; font-weight: bold; border-radius: 5px; text-transform: uppercase; letter-spacing: 2px; box-shadow: 0 3px 5px rgba(0,0,0,0.2);">{title_disp}</span>
                                    </div>
                                    
                                    <div style="font-size: 19px; line-height: 1.8; text-align: justify; position: relative; z-index: 1; flex-grow: 1; padding: 0 15px;">
                                        {body_text}
                                    </div>
                                    
                                    <table style="width: 100%; margin-top: auto; font-size: 16px; font-weight: bold; position: relative; z-index: 1; padding-bottom: 10px;">
                                        <tr>
                                            <td style="text-align: left; width: 33%; vertical-align: bottom;">
                                                <span style="font-size: 14px; color: #666; font-weight: normal;">Date of Issue:</span><br>
                                                <span style="font-size: 17px; border-bottom: 1px solid #000; padding-bottom: 2px; display: inline-block; min-width: 150px;">{issue_date.strftime('%d-%b-%Y')}</span>
                                            </td>
                                            <td style="text-align: center; width: 33%; vertical-align: bottom;">
                                                _____________________<br>
                                                <span style="font-size: 14px; color: #666; font-weight: normal;">Clerk / Admin</span>
                                            </td>
                                            <td style="text-align: right; width: 33%; vertical-align: bottom;">
                                                _____________________<br>
                                                <span style="font-size: 14px; color: #666; font-weight: normal;">Principal Signature</span>
                                            </td>
                                        </tr>
                                    </table>
                                    
                                </div>
                            </div>
                        </div>
                        """
                        print_button_js(cert_html, tr("🖨️ سرٹیفکیٹ پرنٹ کریں (Print Certificate)", "🖨️ Print Certificate"), landscape=True)
                        st.success(tr("سرٹیفکیٹ تیار ہے! پرنٹ کے بٹن پر کلک کریں۔", "Certificate is ready! Click the print button."))
                    
                    except Exception as e:
                        st.error(f"Error Generating Certificate: {e}")
            else:
                st.error("طالب علم کا ڈیٹا نہیں ملا۔")
        else:
            st.info(tr("ڈیٹا بیس میں کوئی طالب علم موجود نہیں۔", "No students found in the database."))

    elif sub_choice in ["Bulk Import", "بلک امپورٹ", "📥 بلک امپورٹ"]:
        st.markdown(f"### 📥 {tr('ایکسل سے اکٹھا داخلہ (Bulk Student Import)', 'Bulk Student Import via Excel')}")
        st.info(tr("پہلے نمونے کی فائل (Template) ڈاؤن لوڈ کریں، اس میں تمام طلباء کا ڈیٹا بھریں، اور پھر اسے یہاں اپلوڈ کریں۔", "Download the template first, fill in the student data, and then upload it here."))
        
        sample_df = pd.DataFrame({
            "Student Name": ["Ali Raza", "Ayesha Khan"],
            "Father Name": ["Ahmad Raza", "M. Khan"],
            "Gender": ["Boy", "Girl"],
            "Class": ["One", "Two"],
            "Section": ["A", "A"],
            "Phone": ["03001234567", "03331234567"],
            "Monthly Fee": [1500, 2000],
            "Admission Date": ["2026-04-01", "2026-04-01"]
        })
        
        c_bulk1, c_bulk2 = st.columns([1, 2])
        csv_template = sample_df.to_csv(index=False).encode('utf-8')
        c_bulk1.download_button(tr("📝 نمونے کی فائل (Template) ڈاؤن لوڈ کریں", "📝 Download Template"), data=csv_template, file_name="Student_Bulk_Import_Template.csv", mime="text/csv")
        
        st.write("---")
        uploaded_file = st.file_uploader(tr("بھری ہوئی فائل اپلوڈ کریں (.csv)", "Upload Filled Data File (.csv)"), type=['csv'])
        
        if uploaded_file is not None:
            try:
                df_import = pd.read_csv(uploaded_file)
                st.write(tr("اپلوڈ کیا گیا ڈیٹا (پریویو):", "Uploaded Data Preview:"))
                st.dataframe(df_import, height=200)
                
                if st.button(tr("🚀 ایک کلک سے تمام طلباء کا داخلہ کریں (Import Students)", "🚀 Import Students"), type="primary"):
                    stud_count = pd.read_sql("SELECT COUNT(*) FROM students", conn).iloc[0, 0]
                    current_reg = 1001 if stud_count == 0 else safe_int(pd.read_sql("SELECT MAX(CAST(reg_id AS INTEGER)) FROM students", conn).iloc[0, 0]) + 1
                    
                    success_count = 0
                    for _, row in df_import.iterrows():
                        s_name = str(row.get('Student Name', '')).strip()
                        if not s_name or s_name == 'nan': continue
                        
                        f_name = str(row.get('Father Name', '')).strip()
                        s_gender = str(row.get('Gender', 'Boy')).strip()
                        s_class = str(row.get('Class', 'Play Group')).strip()
                        s_sec = str(row.get('Section', 'A')).strip()
                        s_phone = str(row.get('Phone', '')).strip()
                        s_fee = safe_int(row.get('Monthly Fee', 0))
                        s_date = str(row.get('Admission Date', today_date)).strip()
                        
                        cursor.execute("""
                            INSERT INTO students 
                            (reg_id, name, fname, class, section, gender, phone, monthly_fee, adm_date, status) 
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'Active')
                        """, (str(current_reg), s_name, f_name, s_class, s_sec, s_gender, s_phone, s_fee, s_date))
                        
                        p_username = s_phone if s_phone and s_phone != 'nan' else f"parent_{current_reg}"
                        try:
                            cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", (p_username, "1234", "Guardian"))
                        except: pass
                        
                        current_reg += 1
                        success_count += 1
                        
                    conn.commit()
                    st.success(tr(f"✅ زبردست! {success_count} طلباء کا ریکارڈ اور والدین کے لاگ ان اکاؤنٹس ایک سیکنڈ میں بن گئے۔", f"✅ Success! {success_count} students and parent accounts imported successfully."))
            except Exception as e:
                st.error(f"Error reading file: {e}")

# ================= 4. سٹاف مینجمنٹ (Staff Management) =================
elif core_choice in ["سٹاف مینجمنٹ", "Staff Mgt"]:
    st.markdown(f"<h2>👨‍🏫 {tr('سٹاف مینجمنٹ', 'Staff Management')} - {tr(sub_choice, sub_choice)}</h2>", unsafe_allow_html=True)

    def generate_staff_profile_html(staff_id_val):
        stf = pd.read_sql(f"SELECT * FROM staff WHERE staff_id='{staff_id_val}'", conn)
        if stf.empty: return ""
        row = stf.iloc[0]
        
        try: dob_fmt = datetime.datetime.strptime(row.get("dob", "1990-01-01"), "%Y-%m-%d").strftime("%d-%m-%Y")
        except: dob_fmt = row.get("dob", "")
        try: join_fmt = datetime.datetime.strptime(row.get("joining_date", "2023-01-01"), "%Y-%m-%d").strftime("%d-%m-%Y")
        except: join_fmt = row.get("joining_date", "")
        
        photo_data = row.get("photo")
        staff_photo_html = '<div style="width:110px; height:130px; border:1px solid #000; text-align:center; line-height:130px; font-size:12px; background:#f9f9f9; color:#999; float:right;">Photo</div>'
        if photo_data:
            b64_photo = base64.b64encode(photo_data).decode()
            staff_photo_html = f'<img src="data:image/jpeg;base64,{b64_photo}" style="width:110px; height:130px; object-fit:cover; border:1px solid #000; display:block !important; float:right;">'
        
        t = {"align": "left", "dir": "ltr"} if st.session_state.ui_lang == "English" else {"align": "right", "dir": "rtl"}
        
        d_name = get_disp_val(row['name'], row.get('name_en'))
        d_fname = get_disp_val(row['fname'], row.get('fname_en'))
        d_address = get_disp_val(row['address'], row.get('address_en'))
        
        raw_g = str(row.get('g_type', 'Father'))
        if "Husband" in raw_g or "شوہر" in raw_g:
            lbl_fname = tr("شوہر کا نام:", "Husband's Name:")
        elif "Guardian" in raw_g or "سرپرست" in raw_g:
            lbl_fname = tr("سرپرست کا نام:", "Guardian's Name:")
        else:
            lbl_fname = tr("والد کا نام:", "Father's Name:")
        
        local_logo = logo_src_b64 if 'logo_src_b64' in locals() or 'logo_src_b64' in globals() else ""
        logo_base64_html = f'<img src="{local_logo}" style="width: 50px; height: 50px; object-fit: contain;">' if local_logo else '<div style="font-size:28px;">🏫</div>'
        
        logo_td = f'<td style="width: 20%; vertical-align: middle;">{logo_base64_html}</td>'
        photo_td = f'<td style="width: 20%; vertical-align: middle;">{staff_photo_html}</td>'

        return f"""
        <div style="border: 2px solid black; padding: 10px; width: 95%; max-width: 740px; margin: 0 auto; box-sizing: border-box; font-family: Arial, sans-serif;" dir="{t['dir']}">
        <table style="width:100%; border:none;"><tr>{logo_td}
        <td style="width: 60%; text-align: center; vertical-align: middle;"><h2 style="margin: 0; color: #1a4f8b;">{school_name.upper()}</h2>
        <p style="margin: 2px 0 0 0; font-weight: bold; font-size:15px;">{school_address}</p>
        <p style="margin: 2px 0 0 0; text-decoration: underline; font-weight: bold;">{tr('سٹاف پروفائل فارم', 'STAFF PROFILE FORM')}</p></td>
        {photo_td}</tr></table>
        <table style="width:100%; border-collapse: collapse; margin-top: 10px;" dir="{t['dir']}">
        <tr><td colspan="4" style="background-color:#e0e0e0; text-align:center; font-weight:bold; font-size: 16px; border: 1px solid black;">{tr('ذاتی معلومات', 'Personal Information')}</td></tr>
        <tr><th style="border: 1px solid black; padding: 4px; text-align: {t['align']}; width: 20%;">{tr('نام:', 'Name:')}</th><td style="border: 1px solid black; padding: 4px; text-align: {t['align']}; width: 30%;">{d_name}</td>
        <th style="border: 1px solid black; padding: 4px; text-align: {t['align']}; width: 20%;">{tr('سٹاف ID:', 'Staff ID:')}</th><td style="border: 1px solid black; padding: 4px; text-align: {t['align']}; width: 30%;">{row['staff_id']}</td></tr>
        <tr><th style="border: 1px solid black; padding: 4px; text-align: {t['align']};">{lbl_fname}</th><td style="border: 1px solid black; padding: 4px; text-align: {t['align']};">{d_fname}</td>
        <th style="border: 1px solid black; padding: 4px; text-align: {t['align']};">{tr('شناختی کارڈ:', 'CNIC:')}</th><td style="border: 1px solid black; padding: 4px; text-align: {t['align']};">{row['cnic']}</td></tr>
        <tr><th style="border: 1px solid black; padding: 4px; text-align: {t['align']};">{tr('فون نمبر:', 'Phone No:')}</th><td style="border: 1px solid black; padding: 4px; text-align: {t['align']};">{row['phone']}</td>
        <th style="border: 1px solid black; padding: 4px; text-align: {t['align']};">{tr('تاریخ پیدائش:', 'DOB:')}</th><td style="border: 1px solid black; padding: 4px; text-align: {t['align']};">{dob_fmt}</td></tr>
        <tr><td colspan="4" style="background-color:#e0e0e0; text-align:center; font-weight:bold; font-size: 16px; border: 1px solid black;">{tr('تعلیمی اور دفتری معلومات', 'Office & Education Info')}</td></tr>
        <tr><th style="border: 1px solid black; padding: 4px; text-align: {t['align']};">{tr('عہدہ:', 'Designation:')}</th><td style="border: 1px solid black; padding: 4px; text-align: {t['align']};">{row['designation']}</td>
        <th style="border: 1px solid black; padding: 4px; text-align: {t['align']};">{tr('تنخواہ:', 'Salary:')}</th><td style="border: 1px solid black; padding: 4px; text-align: {t['align']};">Rs {safe_int(row['salary'])}</td></tr>
        <tr><th style="border: 1px solid black; padding: 4px; text-align: {t['align']};">{tr('تاریخ شمولیت:', 'Joining Date:')}</th><td style="border: 1px solid black; padding: 4px; text-align: {t['align']};">{join_fmt}</td>
        <th style="border: 1px solid black; padding: 4px; text-align: {t['align']};">{tr('تعلیم:', 'Education:')}</th><td style="border: 1px solid black; padding: 4px; text-align: {t['align']};">{row.get('education', '')}</td></tr>
        <tr><th style="border: 1px solid black; padding: 4px; text-align: {t['align']};">{tr('مکمل پتہ:', 'Address:')}</th><td colspan="3" style="border: 1px solid black; padding: 4px; text-align: {t['align']};">{d_address}</td></tr>
        </table>
        </div>"""

    if sub_choice == "New Staff":
        try: cursor.execute("ALTER TABLE staff ADD COLUMN assigned_class TEXT")
        except: pass
        try: cursor.execute("ALTER TABLE staff ADD COLUMN assigned_sec TEXT")
        except: pass
        conn.commit()

        with st.form("staff_form", clear_on_submit=True):
            staff_df_check = pd.read_sql("SELECT staff_id FROM staff", conn)
            auto_staff_id = "101" if staff_df_check.empty else str(max([int(x) for x in staff_df_check['staff_id'] if str(x).isdigit()]) + 1)
            st.markdown(f"### {tr('سٹاف ID:', 'Staff ID:')} `{auto_staff_id}`")
            
            st.markdown(f"#### 1. {tr('ذاتی معلومات', 'Personal Info')}")
            c1, c2, c3, c4 = st.columns([1.5, 1, 1.5, 1])
            staff_name = c1.text_input(tr("نام *", "Name *"))
            staff_gender_disp = c2.selectbox(tr("جنس", "Gender"), [tr("مرد", "Male"), tr("عورت", "Female"), tr("دیگر", "Other")])
            staff_gender = "Male" if staff_gender_disp in ["مرد", "Male"] else ("Female" if staff_gender_disp in ["عورت", "Female"] else "Other")
            staff_dob = c3.date_input(tr("تاریخ پیدائش", "Date of Birth"), min_value=datetime.date(1970, 1, 1), max_value=datetime.date.today(), value=datetime.date(1990, 1, 1))
            staff_photo = c4.file_uploader(tr("سٹاف کی تصویر", "Staff Photo"), type=["jpg", "jpeg", "png"])
            
            c4, c5, c6 = st.columns([1, 2, 2])
            g_disp = c4.selectbox(tr("رشتہ", "Relation"), [tr("والد", "Father"), tr("شوہر", "Husband"), tr("سرپرست", "Guardian")])
            g_type = "Father" if g_disp in ["والد", "Father"] else ("Husband" if g_disp in ["شوہر", "Husband"] else "Guardian")
            father_husband_name = c5.text_input(tr("رشتہ دار کا نام", "Relation Name"))
            cnic = c6.text_input(tr("سٹاف شناختی کارڈ", "Staff CNIC"))
            
            st.markdown(f"#### 2. {tr('رابطہ اور دفتری معلومات', 'Contact & Office Info')}")
            c7, c8 = st.columns(2)
            fh_cnic = c7.text_input(tr("رشتہ دار کا شناختی کارڈ", "Relation CNIC No"))
            phone = c8.text_input(tr("فون نمبر", "Phone No"))
            address = st.text_input(tr("پتہ", "Address"))
            
            st.markdown(f"#### 3. {tr('تعلیمی معلومات (ڈگریاں / پروفیشنل ڈپلومہ)', 'Educational Information')}")
            default_edu_df = pd.DataFrame([{"Degree": "Matric", "Custom Entry": "", "Details/Year": ""}, {"Degree": "Intermediate", "Custom Entry": "", "Details/Year": ""}])
            edited_edu = st.data_editor(
                default_edu_df,
                column_config={
                    "Degree": st.column_config.SelectboxColumn(tr("ڈگری / ڈپلومہ", "Degree / Diploma"), options=["None", "Matric", "Intermediate", "Bachelors", "Masters", "M.Phil", "Ph.D", "B.Ed", "M.Ed", "Montessori Diploma", "IT Diploma", "Other (Custom)"], required=True),
                    "Custom Entry": st.column_config.TextColumn(tr("اپنی مرضی کی ڈگری (اگر Other چنا)", "Custom Degree")),
                    "Details/Year": st.column_config.TextColumn(tr("سال، بورڈ / یونیورسٹی", "Year, Board/Uni"))
                }, num_rows="dynamic", use_container_width=True, key="staff_edu_editor"
            )
            
            st.markdown(f"#### 4. {tr('عہدہ، تنخواہ اور کلاس کی ذمہ داری', 'Designation, Salary & Class Assignment')}")
            c11, c12, c13, c14 = st.columns(4)
            base_opts = ["Teacher", "Principal", "Clerk", "Maid/Peon", "Security Guard", "Other (Custom)"]
            desig_disp_opts = [tr("استاد / ٹیچر", "Teacher"), tr("پرنسپل", "Principal"), tr("کلرک", "Clerk"), tr("آیا / چپڑاسی", "Maid/Peon"), tr("سیکیورٹی گارڈ", "Security Guard"), tr("دیگر (خود لکھیں)", "Other (Custom)")]
            
            desig_sel = c11.selectbox(tr("عہدہ منتخب کریں", "Designation"), desig_disp_opts)
            custom_desig = c11.text_input(tr("اگر 'دیگر' چنا ہے تو نیا عہدہ لکھیں *", "If 'Other', enter custom designation"))
            
            joining_date = c12.date_input(tr("تاریخِ شمولیت", "Joining Date"), max_value=datetime.date.today())
            salary = c13.number_input(tr("تنخواہ", "Salary"), min_value=0)
            
            a_cls = c14.selectbox(tr("کلاس الاٹ کریں (صرف ٹیچر کے لیے)", "Assign Class (For Teachers)"), ["None"] + classes_list)
            a_sec = c14.selectbox(tr("سیکشن الاٹ کریں", "Assign Section"), ["None", "A", "B", "C", "D", "Model"])
            
            st.markdown(f"#### 5. {tr('سافٹ ویئر لاگ ان (اکاؤنٹ)', 'Software Login Details')}")
            c_log1, c_log2, c_log3 = st.columns(3)
            staff_username = c_log1.text_input(tr("یوزر نیم (مثلاً: ali_teacher) *", "Username *"))
            staff_password = c_log2.text_input(tr("پاسورڈ *", "Password *"), type="password")
            staff_role = c_log3.selectbox(tr("سسٹم رول (Role)", "System Role"), ["Teacher", "Operator", "Admin"])

            submit_btn = st.form_submit_button(tr("سٹاف اور اکاؤنٹ محفوظ کریں", "Save Staff & Account"))
            
            if submit_btn:
                if not staff_name:
                    st.error(tr("سٹاف کا نام لکھنا لازمی ہے!", "Staff name is required!"))
                elif staff_username.strip() == "" or staff_password.strip() == "":
                    st.error(tr("سافٹ ویئر میں لاگ ان کے لیے یوزر نیم اور پاسورڈ لازمی ہیں!", "Username and password are required for software login!"))
                else:
                    if desig_sel == tr("دیگر (خود لکھیں)", "Other (Custom)"):
                        designation = custom_desig if custom_desig.strip() != "" else "Staff"
                    else:
                        designation = base_opts[desig_disp_opts.index(desig_sel)]

                    edu_list = []
                    for _, r in edited_edu.iterrows():
                        deg = r.get("Degree")
                        cust = r.get("Custom Entry")
                        det = r.get("Details/Year")
                        if pd.isna(deg) or deg == "None": continue
                        final_deg = str(cust).strip() if str(deg) == "Other (Custom)" and pd.notna(cust) and str(cust).strip() != "" else str(deg)
                        final_det = str(det).strip() if pd.notna(det) else ""
                        if final_deg and final_deg != "None":
                            edu_list.append(f"{final_deg} ({final_det})" if final_det else final_deg)

                    education_str = " | ".join(edu_list)
                    photo_data = staff_photo.read() if staff_photo else None
                    n_en = staff_name if st.session_state.ui_lang == "English" else ""
                    fn_en = father_husband_name if st.session_state.ui_lang == "English" else ""
                    ad_en = address if st.session_state.ui_lang == "English" else ""
                    
                    try:
                        cursor.execute("INSERT INTO users (username, password, role, ref_id) VALUES (?, ?, ?, ?)", 
                                       (staff_username.strip(), staff_password.strip(), staff_role, auto_staff_id))
                        
                        cursor.execute("""
                            INSERT INTO staff 
                            (staff_id, name, fname, cnic, dob, designation, phone, address, joining_date, salary, education, fh_cnic, photo, g_type, name_en, fname_en, address_en, gender, assigned_class, assigned_sec) 
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, (auto_staff_id, staff_name, father_husband_name, cnic, staff_dob.strftime("%Y-%m-%d"), designation, phone, address, joining_date.strftime("%Y-%m-%d"), salary, education_str, fh_cnic, photo_data, g_type, n_en, fn_en, ad_en, staff_gender, a_cls, a_sec))
                        
                        conn.commit()
                        st.success(tr("✅ سٹاف کا ریکارڈ اور لاگ ان اکاؤنٹ کامیابی سے محفوظ ہو گیا!", "Staff record and login account saved successfully!"))
                    except sqlite3.IntegrityError:
                        st.error(tr("⚠️ یہ یوزر نیم پہلے سے موجود ہے۔ برائے مہربانی لاگ ان کے لیے کوئی مختلف نام منتخب کریں۔", "Username already exists. Please choose a different one."))
                    except Exception as e: 
                        st.error(f"Error saving staff: {e}")

    elif sub_choice == "Edit Staff":
        st.markdown("### ✏️ سٹاف کا ریکارڈ ایڈٹ کریں")
        edit_staff_id = st.text_input(tr("سٹاف ID درج کریں (مثلاً: 101)", "Enter Staff ID to Edit"))
        
        if edit_staff_id:
            stf_match = pd.read_sql(f"SELECT * FROM staff WHERE staff_id='{edit_staff_id}'", conn)
            if not stf_match.empty:
                stf_data = stf_match.iloc[0]
                
                for col in ['name_en', 'fname_en', 'address_en', 'gender', 'g_type', 'fh_cnic', 'education', 'assigned_class', 'assigned_sec']:
                    try: cursor.execute(f"ALTER TABLE staff ADD COLUMN {col} TEXT")
                    except: pass
                conn.commit()
                
                cursor.execute("SELECT username, password, role FROM users WHERE ref_id=? OR username=?", (edit_staff_id, f"staff_{edit_staff_id}"))
                ex_u = cursor.fetchone()
                
                if ex_u:
                    def_user, def_pass, def_role = ex_u[0], ex_u[1], ex_u[2]
                    acc_status = "<span style='color: green;'>✅ (اکاؤنٹ موجود ہے)</span>"
                else:
                    def_user, def_pass, def_role = f"staff_{edit_staff_id}", "1234", "Teacher"
                    acc_status = "<span style='color: #d69e2e;'>⚠️ (نیا اکاؤنٹ بنے گا)</span>"

                with st.form("edit_staff_form"):
                    st.markdown(f"#### 1. {tr('ذاتی معلومات', 'Personal Info')}")
                    curr_name = get_disp_val(stf_data.get("name", ""), stf_data.get("name_en", ""))
                    curr_fname = get_disp_val(stf_data.get("fname", ""), stf_data.get("fname_en", ""))
                    curr_address = get_disp_val(stf_data.get("address", ""), stf_data.get("address_en", ""))
                    
                    c1, c2, c3, c4 = st.columns([1.5, 1, 1.5, 1])
                    e_name = c1.text_input(tr("نام", "Name"), value=curr_name)
                    
                    curr_g = stf_data.get("gender", "Male") or "Male"
                    g_opts = ["Male", "Female", "Other"]
                    g_idx = g_opts.index(curr_g) if curr_g in g_opts else 0
                    e_gender_disp = c2.selectbox(tr("جنس", "Gender"), [tr("مرد", "Male"), tr("عورت", "Female"), tr("دیگر", "Other")], index=g_idx)
                    e_gender = "Male" if e_gender_disp in ["مرد", "Male"] else ("Female" if e_gender_disp in ["عورت", "Female"] else "Other")
                    
                    try: e_dob_val = datetime.datetime.strptime(stf_data.get("dob", "1970-01-01"), "%Y-%m-%d").date()
                    except: e_dob_val = datetime.date(1970, 1, 1)
                    e_dob = c2.date_input(tr("تاریخ پیدائش", "DOB"), value=e_dob_val)
                    e_photo = c3.file_uploader(tr("نئی تصویر اپلوڈ کریں", "Upload New Photo"), type=["jpg", "jpeg", "png"])
                    
                    c4, c5, c6 = st.columns([1, 2, 2])
                    raw_g = str(stf_data.get("g_type", "Father"))
                    if "Father" in raw_g or "والد" in raw_g: g_idx_stf = 0
                    elif "Husband" in raw_g or "شوہر" in raw_g: g_idx_stf = 1
                    else: g_idx_stf = 2
                    g_disp_e = c4.selectbox(tr("رشتہ", "Relation"), [tr("والد", "Father"), tr("شوہر", "Husband"), tr("سرپرست", "Guardian")], index=g_idx_stf)
                    if g_disp_e in ["والد", "Father"]: e_g_type = "Father"
                    elif g_disp_e in ["شوہر", "Husband"]: e_g_type = "Husband"
                    else: e_g_type = "Guardian"
                    
                    e_fname = c5.text_input(tr("رشتہ دار کا نام", "Relation Name"), value=curr_fname)
                    e_cnic = c6.text_input(tr("سٹاف شناختی کارڈ", "CNIC"), value=str(stf_data.get("cnic", "")))
                    
                    c7, c8 = st.columns(2)
                    e_fh_cnic = c7.text_input(tr("رشتہ دار کا شناختی کارڈ", "Relation CNIC"), value=str(stf_data.get("fh_cnic", "")))
                    e_phone = c8.text_input(tr("فون نمبر", "Phone No"), value=str(stf_data.get("phone", "")))
                    e_address = st.text_input(tr("پتہ", "Address"), value=curr_address)
                    
                    existing_edu_text = stf_data.get("education", "")
                    edu_init_data = []
                    if existing_edu_text:
                        parts = existing_edu_text.split(" | ")
                        for p in parts:
                            if "(" in p and p.endswith(")"):
                                c_deg, c_det = p.rsplit(" (", 1)
                                c_det = c_det[:-1]
                                if c_deg in ["Matric", "Intermediate", "Bachelors", "Masters", "M.Phil", "Ph.D", "B.Ed", "M.Ed", "Montessori Diploma", "IT Diploma"]:
                                    edu_init_data.append({"Degree": c_deg, "Custom Entry": "", "Details/Year": c_det.strip()})
                                else:
                                    edu_init_data.append({"Degree": "Other (Custom)", "Custom Entry": c_deg.strip(), "Details/Year": c_det.strip()})
                            else:
                                if p in ["Matric", "Intermediate", "Bachelors", "Masters", "M.Phil", "Ph.D", "B.Ed", "M.Ed", "Montessori Diploma", "IT Diploma"]:
                                    edu_init_data.append({"Degree": p, "Custom Entry": "", "Details/Year": ""})
                                else:
                                    edu_init_data.append({"Degree": "Other (Custom)", "Custom Entry": p.strip(), "Details/Year": ""})
                    else:
                        edu_init_data = [{"Degree": "Matric", "Custom Entry": "", "Details/Year": ""}, {"Degree": "Intermediate", "Custom Entry": "", "Details/Year": ""}]

                    edit_edu_df = pd.DataFrame(edu_init_data)
                    edited_edu_edit = st.data_editor(
                        edit_edu_df,
                        column_config={
                            "Degree": st.column_config.SelectboxColumn(tr("ڈگری / ڈپلومہ", "Degree / Diploma"), options=["None", "Matric", "Intermediate", "Bachelors", "Masters", "M.Phil", "Ph.D", "B.Ed", "M.Ed", "Montessori Diploma", "IT Diploma", "Other (Custom)"], required=True),
                            "Custom Entry": st.column_config.TextColumn(tr("اپنی مرضی کی ڈگری (اگر Other چنا)", "Custom Degree")),
                            "Details/Year": st.column_config.TextColumn(tr("سال، بورڈ / یونیورسٹی", "Year, Board/Uni"))
                        }, num_rows="dynamic", use_container_width=True, key="staff_edu_editor_edit"
                    )
                    
                    st.markdown(f"#### 4. {tr('عہدہ، تنخواہ اور کلاس کی ذمہ داری', 'Designation, Salary & Class Assignment')}")
                    c11, c12, c13, c14 = st.columns(4)
                    base_opts = ["Teacher", "Principal", "Clerk", "Maid/Peon", "Security Guard", "Other (Custom)"]
                    desig_disp_opts = [tr("استاد / ٹیچر", "Teacher"), tr("پرنسپل", "Principal"), tr("کلرک", "Clerk"), tr("آیا / چپڑاسی", "Maid/Peon"), tr("سیکیورٹی گارڈ", "Security Guard"), tr("دیگر (خود لکھیں)", "Other (Custom)")]
                    curr_desig = stf_data.get("designation")
                    
                    if curr_desig in base_opts and curr_desig != "Other (Custom)":
                        d_idx = base_opts.index(curr_desig)
                        custom_val = ""
                    else:
                        d_idx = 5
                        custom_val = curr_desig if curr_desig else ""
                        
                    e_desig_sel = c11.selectbox(tr("عہدہ منتخب کریں", "Designation"), desig_disp_opts, index=d_idx)
                    if e_desig_sel == tr("دیگر (خود لکھیں)", "Other (Custom)"):
                        e_designation = c11.text_input(tr("اگر 'دیگر' چنا ہے تو نیا عہدہ لکھیں *", "If 'Other', enter custom designation *"), value=custom_val)
                    else:
                        e_designation = base_opts[desig_disp_opts.index(e_desig_sel)]
                        
                    try: e_join_val = datetime.datetime.strptime(stf_data.get("joining_date", "2023-01-01"), "%Y-%m-%d").date()
                    except: e_join_val = datetime.date.today()
                    e_join_date = c12.date_input(tr("تاریخِ شمولیت", "Join Date"), value=e_join_val)
                    e_salary = c13.number_input(tr("تنخواہ", "Salary"), value=safe_int(stf_data.get("salary", 0)))
                    
                    c_opts = ["None"] + classes_list
                    curr_c = stf_data.get("assigned_class", "None")
                    c_idx = c_opts.index(curr_c) if curr_c in c_opts else 0
                    e_a_cls = c14.selectbox(tr("کلاس الاٹ کریں (صرف ٹیچر کے لیے)", "Assign Class"), c_opts, index=c_idx)
                    
                    s_opts = ["None", "A", "B", "C", "D", "Model"]
                    curr_s = stf_data.get("assigned_sec", "None")
                    s_idx = s_opts.index(curr_s) if curr_s in s_opts else 0
                    e_a_sec = c14.selectbox(tr("سیکشن الاٹ کریں", "Assign Section"), s_opts, index=s_idx)
                    
                    st.markdown(f"#### 5. {tr('سافٹ ویئر لاگ ان (اکاؤنٹ)', 'Software Login Details')} {acc_status}", unsafe_allow_html=True)
                    c_log1, c_log2, c_log3 = st.columns(3)
                    e_username = c_log1.text_input(tr("یوزر نیم (Username)", "Username"), value=def_user)
                    e_password = c_log2.text_input(tr("پاسورڈ (Password)", "Password"), value=def_pass)
                    roles_lst = ["Teacher", "Operator", "Admin"]
                    e_role = c_log3.selectbox(tr("سسٹم رول (Role)", "System Role"), roles_lst, index=roles_lst.index(def_role) if def_role in roles_lst else 0)

                    if st.form_submit_button(tr("تبدیلیاں محفوظ کریں", "Save Changes"), type="primary"):
                        try:
                            if e_desig_sel == tr("دیگر (خود لکھیں)", "Other (Custom)"):
                                e_designation = e_designation if e_designation.strip() != "" else curr_desig
                            else:
                                e_designation = base_opts[desig_disp_opts.index(e_desig_sel)]

                            edu_list = []
                            for _, r in edited_edu_edit.iterrows():
                                deg = r.get("Degree")
                                cust = r.get("Custom Entry")
                                det = r.get("Details/Year")
                                if pd.isna(deg) or deg == "None": continue
                                final_deg = str(cust).strip() if str(deg) == "Other (Custom)" and pd.notna(cust) and str(cust).strip() != "" else str(deg)
                                final_det = str(det).strip() if pd.notna(det) else ""
                                if final_deg and final_deg != "None":
                                    edu_list.append(f"{final_deg} ({final_det})" if final_det else final_deg)

                            education_str = " | ".join(edu_list)
                            
                            if st.session_state.ui_lang == "اردو":
                                query = """UPDATE staff SET 
                                    name=?, cnic=?, fh_cnic=?, education=?, phone=?, designation=?, 
                                    joining_date=?, salary=?, g_type=?, dob=?, gender=?, fname=?, address=?, assigned_class=?, assigned_sec=?
                                    WHERE staff_id=?"""
                                val_tuple = (e_name, e_cnic, e_fh_cnic, education_str, e_phone, e_designation, e_join_date.strftime("%Y-%m-%d"), float(e_salary), e_g_type, e_dob.strftime("%Y-%m-%d"), e_gender, e_fname, e_address, e_a_cls, e_a_sec, edit_staff_id)
                            else:
                                query = """UPDATE staff SET 
                                    name_en=?, cnic=?, fh_cnic=?, education=?, phone=?, designation=?, 
                                    joining_date=?, salary=?, g_type=?, dob=?, gender=?, fname_en=?, address_en=?, assigned_class=?, assigned_sec=?
                                    WHERE staff_id=?"""
                                val_tuple = (e_name, e_cnic, e_fh_cnic, education_str, e_phone, e_designation, e_join_date.strftime("%Y-%m-%d"), float(e_salary), e_g_type, e_dob.strftime("%Y-%m-%d"), e_gender, e_fname, e_address, e_a_cls, e_a_sec, edit_staff_id)
                            
                            cursor.execute(query, val_tuple)
                            if e_photo: cursor.execute("UPDATE staff SET photo=? WHERE staff_id=?", (e_photo.read(), edit_staff_id))
                            
                            if e_username.strip():
                                cursor.execute("SELECT id FROM users WHERE username=?", (e_username.strip(),))
                                if cursor.fetchone():
                                    cursor.execute("UPDATE users SET password=?, role=?, ref_id=? WHERE username=?", (e_password.strip(), e_role, edit_staff_id, e_username.strip()))
                                else:
                                    cursor.execute("INSERT INTO users (username, password, role, ref_id) VALUES (?, ?, ?, ?)", (e_username.strip(), e_password.strip(), e_role, edit_staff_id))

                            conn.commit()
                            st.balloons()
                            st.success(tr("✅ سٹاف کا ریکارڈ اور اکاؤنٹ اپڈیٹ ہو گیا!", "Staff record updated successfully!"))
                            import time
                            time.sleep(1.5)
                            st.rerun()
                            
                        except Exception as db_err:
                            st.error(f"🛑 Error: {db_err}")
            else:
                st.warning(tr("اس آئی ڈی کا کوئی سٹاف موجود نہیں۔", "No staff found with this ID."))

    elif sub_choice == "Search Staff":
        s_staff_q = st.text_input(tr("سٹاف کا نام، ID، یا CNIC درج کریں:", "Enter Staff Name, ID, or CNIC:"))
        if s_staff_q:
            res_stf = pd.read_sql(f"SELECT staff_id as 'ID', name as 'Name', name_en as 'Name_EN', education as 'Education', designation as 'Designation', cnic as 'CNIC', phone as 'Phone', salary as 'Salary' FROM staff WHERE name LIKE '%{s_staff_q}%' OR name_en LIKE '%{s_staff_q}%' OR staff_id LIKE '%{s_staff_q}%' OR cnic LIKE '%{s_staff_q}%'", conn)
            if not res_stf.empty:
                res_stf['Final Name'] = res_stf.apply(lambda row: get_disp_val(row['Name'], row.get('Name_EN')), axis=1)
                res_stf = res_stf[['ID', 'Final Name', 'Education', 'Designation', 'CNIC', 'Phone', 'Salary']]
                st.dataframe(res_stf, use_container_width=True)
                
    elif sub_choice == "Print Profile":
        c_pr1, c_pr2 = st.columns([2, 1])
        print_staff_id = c_pr1.text_input(tr("سٹاف ID درج کریں:", "Enter Staff ID to Print:"), key="print_profile_staff")
        if print_staff_id:
            html_output = generate_staff_profile_html(print_staff_id)
            if html_output: print_button_js(html_output, "Print Staff Form Now", landscape=False)
            else: st.warning(tr("نہیں ملا۔", "Not found."))

    elif sub_choice in ["Certificates", "سرٹیفکیٹس", "🎓 سرٹیفکیٹس"]:
        st.markdown(f"### 🎓 {tr('سٹاف سرٹیفکیٹ جنریٹر', 'Staff Certificate Generator')}")
        st.write(tr("یہاں سے آپ سٹاف ممبرز کے لیے تجربہ کا سرٹیفکیٹ (Experience Letter)، فارغ خطی (Relieving Letter) اور تعریفی سند جاری کر سکتے ہیں۔", "Generate Experience, Relieving, and Appreciation letters for staff here."))

        c_cert1, c_cert2 = st.columns([1, 2])
        cert_type = c_cert1.selectbox(tr("سرٹیفکیٹ کی قسم", "Certificate Type"), [
            "Experience Certificate (تجربہ کا سرٹیفکیٹ)", 
            "Relieving Letter (فارغ خطی / NOC)", 
            "Certificate of Appreciation (حسنِ کارکردگی)"
        ])

        all_stf_df = pd.read_sql("SELECT staff_id, name, fname, designation, gender, cnic, joining_date, g_type FROM staff", conn)
        if not all_stf_df.empty:
            all_stf_df['staff_id'] = all_stf_df['staff_id'].astype(str)
            
            stf_list = [f"{r['name']} ({r['designation']}) - ID: {r['staff_id']}" for _, r in all_stf_df.iterrows()]
            sel_stf = c_cert2.selectbox(tr("سٹاف ممبر منتخب کریں", "Select Staff Member"), stf_list)
            
            sel_id = str(sel_stf.split("ID: ")[1]).strip()
            
            matching_rows = all_stf_df[all_stf_df['staff_id'] == sel_id]
            
            if not matching_rows.empty:
                stf_data = matching_rows.iloc[0]
                
                c_cert3, c_cert4 = st.columns(2)
                issue_date = c_cert3.date_input(tr("تاریخِ اجراء", "Issue Date"), datetime.date.today())
                
                def_remarks = "Highly dedicated and hardworking."
                if "Appreciation" in cert_type:
                    def_remarks = "Exceptional contribution to the school's academic success."
                    
                remarks = c_cert4.text_input(tr("ریمارکس / کارکردگی (Remarks)", "Remarks / Performance"), value=def_remarks)
                
                if st.button(tr("سرٹیفکیٹ تیار کریں (Generate Certificate)", "Generate Certificate"), type="primary"):
                    try:
                        g_val = str(stf_data.get('gender', 'Male')).strip()
                        rel_type = str(stf_data.get('g_type', 'Father')).strip()
                        
                        if rel_type in ["Husband", "شوہر"]:
                            rel_text = "Wife"
                            pron_sub = "She"
                            pron_obj = "her"
                            pron_pos = "her"
                        elif g_val in ["Female", "عورت", "Girl", "لڑکی", "female"]:
                            rel_text = "Daughter"
                            pron_sub = "She"
                            pron_obj = "her"
                            pron_pos = "her"
                        else:
                            rel_text = "Son"
                            pron_sub = "He"
                            pron_obj = "him"
                            pron_pos = "his"
                        
                        stf_name = str(stf_data['name']).strip()
                        f_name = str(stf_data['fname']).strip()
                        desig = str(stf_data['designation']).strip()
                        s_id = str(stf_data['staff_id']).strip()
                        s_cnic = str(stf_data.get('cnic', '-')).strip()
                        if not s_cnic or s_cnic == 'nan' or s_cnic == 'None': s_cnic = "N/A"
                        
                        try:
                            join_date = datetime.datetime.strptime(stf_data['joining_date'], "%Y-%m-%d").strftime("%d-%b-%Y")
                        except:
                            join_date = stf_data['joining_date']
                        
                        pron_pos_cap = pron_pos.capitalize()
                        
                        if cert_type == "Experience Certificate (تجربہ کا سرٹیفکیٹ)":
                            title_disp = "EXPERIENCE CERTIFICATE"
                            body_text = f"""This is to certify that <b>{stf_name}</b> {rel_text} of <b>{f_name}</b> 
                            (Staff ID: <b>{s_id}</b>, CNIC: <b>{s_cnic}</b>) has been serving in this institution as a <b>{desig}</b> 
                            since <b>{join_date}</b> up to <b>{issue_date.strftime('%d-%b-%Y')}</b>.<br><br>
                            During {pron_pos} tenure at {school_name}, {pron_pos} professional conduct, character, and dedication to work 
                            were found to be <b>{remarks}</b>. {pron_sub} is a hardworking and sincere individual. We wish {pron_obj} all the best in {pron_pos} future endeavors."""
                            
                        elif cert_type == "Relieving Letter (فارغ خطی / NOC)":
                            title_disp = "RELIEVING LETTER / N.O.C"
                            body_text = f"""This is to certify that <b>{stf_name}</b> {rel_text} of <b>{f_name}</b> 
                            (Staff ID: <b>{s_id}</b>, CNIC: <b>{s_cnic}</b>), who was working in the capacity of <b>{desig}</b> 
                            since <b>{join_date}</b>, has been officially relieved from {pron_pos} duties on <b>{issue_date.strftime('%d-%b-%Y')}</b>.<br><br>
                            All {pron_pos} outstanding dues and accounts have been fully cleared. {pron_sub} bears a good character 
                            and {pron_pos} performance was <b>{remarks}</b>. We wish {pron_obj} success in {pron_pos} future career."""
                            
                        else:
                            title_disp = "CERTIFICATE OF APPRECIATION"
                            body_text = f"""This Certificate of Appreciation is proudly awarded to <b>{stf_name}</b> {rel_text} of <b>{f_name}</b> 
                            (Staff ID: <b>{s_id}</b>, CNIC: <b>{s_cnic}</b>) in highly esteemed recognition of {pron_pos} outstanding dedication, 
                            relentless hard work, and excellent performance as a <b>{desig}</b> at {school_name}.<br><br>
                            {pron_pos_cap} contributions have been <b>{remarks}</b>. {pron_sub} has consistently proven to be a valuable asset 
                            to our institution. We deeply appreciate {pron_pos} services and wish {pron_obj} continued success."""

                        cert_html = f"""
                        <div style="padding: 10px; font-family: 'Times New Roman', serif; box-sizing: border-box; width: 100%;">
                            <div style="border: 10px solid #1a4f8b; padding: 4px; background-color: #fcfcfc; box-sizing: border-box; height: 95vh; max-height: 740px; overflow: hidden; position: relative;">
                                <div style="border: 2px solid #d4af37; padding: 20px 40px; height: 100%; box-sizing: border-box; display: flex; flex-direction: column;">
                                    
                                    <div style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); width: 45%; opacity: 0.07; z-index: 0; display: flex; justify-content: center; align-items: center;">
                                        <img src="{logo_src_b64}" style="width: 100%;">
                                    </div>
                                    
                                    <table style="width: 100%; position: relative; z-index: 1;">
                                        <tr>
                                            <td style="width: 20%; text-align: left; vertical-align: middle;">{f'<img src="{logo_src_b64}" style="height: 90px; object-fit: contain;">' if logo_src_b64 else ''}</td>
                                            <td style="width: 60%; text-align: center; vertical-align: middle;">
                                                <h1 style="margin: 0; color: #1a4f8b; font-size: 34px; text-transform: uppercase; font-weight: 900; letter-spacing: 1px;">{school_name}</h1>
                                                <p style="margin: 4px 0; font-size: 15px; font-weight: bold; color: #333;">{school_address}</p>
                                                <p style="margin: 0; font-size: 13px; color: #555;">Reg No: {school_reg} &nbsp;|&nbsp; Ph: {school_phone}</p>
                                            </td>
                                            <td style="width: 20%;"></td>
                                        </tr>
                                    </table>
                                    
                                    <div style="border-bottom: 2px solid #d4af37; margin: 15px 0;"></div>
                                    
                                    <div style="text-align: center; margin: 10px 0 20px 0; position: relative; z-index: 1;">
                                        <span style="background-color: #1a4f8b; color: white; padding: 8px 30px; font-size: 22px; font-weight: bold; border-radius: 5px; text-transform: uppercase; letter-spacing: 2px; box-shadow: 0 3px 5px rgba(0,0,0,0.2);">{title_disp}</span>
                                    </div>
                                    
                                    <div style="font-size: 19px; line-height: 1.8; text-align: justify; position: relative; z-index: 1; flex-grow: 1; padding: 0 15px;">
                                        {body_text}
                                    </div>
                                    
                                    <table style="width: 100%; margin-top: auto; font-size: 16px; font-weight: bold; position: relative; z-index: 1; padding-bottom: 10px;">
                                        <tr>
                                            <td style="text-align: left; width: 33%; vertical-align: bottom;">
                                                <span style="font-size: 14px; color: #666; font-weight: normal;">Date of Issue:</span><br>
                                                <span style="font-size: 17px; border-bottom: 1px solid #000; padding-bottom: 2px; display: inline-block; min-width: 150px;">{issue_date.strftime('%d-%b-%Y')}</span>
                                            </td>
                                            <td style="text-align: center; width: 33%; vertical-align: bottom;">
                                                
                                            </td>
                                            <td style="text-align: right; width: 33%; vertical-align: bottom;">
                                                _____________________<br>
                                                <span style="font-size: 14px; color: #666; font-weight: normal;">Principal Signature</span>
                                            </td>
                                        </tr>
                                    </table>
                                    
                                </div>
                            </div>
                        </div>
                        """
                        print_button_js(cert_html, tr("🖨️ سرٹیفکیٹ پرنٹ کریں (Print Certificate)", "🖨️ Print Certificate"), landscape=True)
                        st.success(tr("سرٹیفکیٹ تیار ہے! پرنٹ کے بٹن پر کلک کریں۔", "Certificate is ready! Click the print button."))
                    
                    except Exception as e:
                        st.error(f"Error Generating Certificate: {e}")
            else:
                st.error("طالب علم کا ڈیٹا نہیں ملا۔")
        else:
            st.info(tr("ڈیٹا بیس میں کوئی سٹاف موجود نہیں۔", "No staff found in the database."))

    # ================= سٹاف لیٹرز اور دستاویزات (Letters & Documents) =================
    elif sub_choice in ["Letters & Documents", "لیٹرز اور دستاویزات"]:
        st.markdown(f"### 📄 {tr('سٹاف لیٹرز اور آفیشل دستاویزات', 'Staff Letters & Official Documents')}")
        st.write(tr("یہاں سے آپ منتخب سٹاف کے لیے تمام ضروری ایچ آر (HR) دستاویزات جنریٹ کر سکتے ہیں۔", "Generate all necessary HR documents for selected staff."))
        
        is_eng = st.session_state.ui_lang == "English"
        t_dir = "ltr" if is_eng else "rtl"
        t_align = "left" if is_eng else "right"
        t_align_opp = "right" if is_eng else "left"
        
        # 🟢 نستعلیق فونٹ کا ویب لنک تاکہ اردو ہر براؤزر میں پرفیکٹ نظر آئے
        if is_eng:
            font_css = ""
            f_family = "'Arial', sans-serif"
        else:
            font_css = "<style>@import url('https://fonts.googleapis.com/css2?family=Noto+Nastaliq+Urdu:wght@400;700&display=swap');</style>"
            f_family = "'Jameel Noori Nastaliq', 'Noto Nastaliq Urdu', 'Nafees Web Naskh', Arial, sans-serif"

        try: staff_df = pd.read_sql("SELECT * FROM staff", conn)
        except: staff_df = pd.DataFrame()
            
        if not staff_df.empty:
            c_doc1, c_doc2 = st.columns([1, 2])
            
            doc_opts_en = [
                "Employment Contract", 
                "Job Description & Code of Conduct", 
                "Joining Report", 
                "Annual Confidential Report (ACR)", 
                "Salary Certificate", 
                "Warning / Show Cause Notice", 
                "Termination Letter"
            ]
            doc_opts_ur = [
                "معاہدہ ملازمت (Employment Contract)", 
                "ڈیوٹیز اور قواعد و ضوابط (Job Description)", 
                "جوائننگ رپورٹ (Joining Report)", 
                "سالانہ کارکردگی رپورٹ (ACR)", 
                "تنخواہ کا سرٹیفکیٹ (Salary Certificate)", 
                "شوکاز نوٹس (Warning Letter)", 
                "برخاستگی لیٹر (Termination)"
            ]
            doc_opts = doc_opts_en if is_eng else doc_opts_ur
            
            doc_type_sel = c_doc1.selectbox(tr("دستاویز کی قسم (Document Type)", "Document Type"), doc_opts)
            doc_type = doc_opts_en[doc_opts.index(doc_type_sel)]
            
            staff_opts = [f"{get_disp_val(r['name'], r.get('name_en'))} - {r['designation']} (ID: {r['staff_id']})" for _, r in staff_df.iterrows()]
            sel_staff = c_doc2.selectbox(tr("سٹاف ممبر منتخب کریں", "Select Staff Member"), staff_opts)
            
            s_id = sel_staff.split("(ID: ")[1].replace(")", "")
            emp_row = staff_df[staff_df['staff_id'] == s_id].iloc[0]
            
            e_name = get_disp_val(emp_row['name'], emp_row.get('name_en'))
            e_fname = get_disp_val(emp_row.get('fname', ''), emp_row.get('fname_en', ''))
            e_desig = emp_row['designation']
            e_salary = emp_row.get('salary', 0)
            
            try: e_join = datetime.datetime.strptime(emp_row.get('joining_date', '2026-01-01'), "%Y-%m-%d").strftime("%d %B, %Y")
            except: e_join = emp_row.get('joining_date', 'N/A')
            
            school_n_doc = school_name.upper() if school_name else "DAR UL KHADIJA SCHOOL SYSTEM"
            
            g_val = str(emp_row.get('gender', 'Male')).strip().lower()
            rel_type = str(emp_row.get('g_type', 'Father')).strip().lower()
            
            if rel_type in ["husband", "شوہر"]:
                rel_label = "W/O" if is_eng else "زوجہ"
                pron_sub = "She"
                pron_obj = "her"
                pron_pos = "her"
            elif g_val in ["female", "عورت", "girl", "لڑکی", "f"]:
                rel_label = "D/O" if is_eng else "بنتِ"
                pron_sub = "She"
                pron_obj = "her"
                pron_pos = "her"
            else:
                rel_label = "S/O" if is_eng else "ولد"
                pron_sub = "He"
                pron_obj = "him"
                pron_pos = "his"
                
            pron_pos_cap = pron_pos.capitalize()
            
            watermark_html = f"""<div style="position: absolute; top: 0; left: 0; right: 0; bottom: 0; background-image: url('{logo_src_b64}'); background-position: center; background-repeat: no-repeat; background-size: 60%; opacity: 0.08; z-index: 0; pointer-events: none;"></div>""" if logo_src_b64 else ""
            header_logo_html = f'<img src="{logo_src_b64}" style="height: 75px; margin-right: 15px; margin-left: 15px; object-fit: contain;">' if logo_src_b64 else ''

            st.write("---")
            
            # 🟢 1. ایمپلائمنٹ کنٹریکٹ (Employment Contract)
            if doc_type == "Employment Contract":
                st.info(tr("معاہدے کی اضافی تفصیلات درج کریں:", "Enter additional contract details:"))
                cc1, cc2 = st.columns(2)
                contract_dur = cc1.text_input(tr("معاہدے کی مدت", "Contract Duration"), value="1 Year" if is_eng else "ایک سال")
                work_hours = cc2.text_input(tr("اوقاتِ کار", "Working Hours"), value="07:30 AM to 02:00 PM")
                
                if st.button(tr("کنٹریکٹ جنریٹ کریں", "Generate Contract"), type="primary"):
                    title_txt = "EMPLOYMENT CONTRACT" if is_eng else "معاہدہ ملازمت (Employment Contract)"
                    date_lbl = "Date:" if is_eng else "تاریخ:"
                    
                    intro_txt = f'This Employment Contract is made and entered into by and between <b>{school_n_doc}</b> (hereinafter referred to as "the School") and <b>{e_name}</b> {rel_label} <b>{e_fname}</b> (hereinafter referred to as "the Employee").' if is_eng else f'یہ معاہدہ ملازمت <b>{school_n_doc}</b> (جسے بعد میں "سکول" کہا گیا ہے) اور <b>{e_name}</b> {rel_label} <b>{e_fname}</b> (جسے بعد میں "ملازم" کہا گیا ہے) کے درمیان طے پایا ہے۔'
                    
                    h1_txt = "1. Position and Duties" if is_eng else "1. عہدہ اور ذمہ داریاں"
                    p1_txt = f"The Employee is hired for the position of <b>{e_desig}</b>. The Employee agrees to perform the duties and responsibilities associated with this role in a professional and dedicated manner." if is_eng else f"ملازم کو <b>{e_desig}</b> کے عہدے پر تعینات کیا گیا ہے۔ ملازم اپنی تمام ذمہ داریاں انتہائی پیشہ ورانہ اور ایمانداری کے ساتھ نبھانے کا پابند ہوگا۔"
                    
                    h2_txt = "2. Salary and Working Hours" if is_eng else "2. تنخواہ اور اوقاتِ کار"
                    li1_txt = f"<b>Monthly Basic Salary:</b> Rs. {e_salary}/-" if is_eng else f"<b>ماہانہ بنیادی تنخواہ:</b> مبلغ {e_salary}/- روپے"
                    li2_txt = f"<b>Working Hours:</b> {work_hours}" if is_eng else f"<b>اوقاتِ کار:</b> {work_hours}"
                    li3_txt = f"<b>Contract Duration:</b> {contract_dur}" if is_eng else f"<b>معاہدے کی مدت:</b> {contract_dur}"
                    
                    h3_txt = "3. Terms & Conditions" if is_eng else "3. شرائط و ضوابط"
                    p3_txt = "The Employee must strictly follow the rules, regulations, and disciplinary code of the school. Any unapproved absence or professional misconduct may lead to strict disciplinary action or termination. A one-month prior notice is required from either party for the termination of this contract." if is_eng else "ملازم سکول کے تمام قواعد و ضوابط اور ڈسپلن پر سختی سے عمل کرنے کا پابند ہوگا۔ کسی بھی قسم کی غیر منظور شدہ چھٹی یا غیر پیشہ ورانہ رویے پر سخت محکمانہ کارروائی یا ملازمت سے برخاستگی عمل میں لائی جا سکتی ہے۔ معاہدہ ختم کرنے کے لیے فریقین کی جانب سے ایک ماہ قبل نوٹس دینا لازمی ہوگا۔"
                    
                    sign_emp = "Signature of Employee" if is_eng else "دستخط ملازم"
                    sign_prin = "Signature of Principal" if is_eng else "دستخط پرنسپل"

                    doc_html = f"""
                    {font_css}
                    <div style="font-family: {f_family}; padding: 40px; max-width: 800px; margin: 0 auto; border: 2px solid #005b36; outline: 5px solid #f2f7f4; background: white; position: relative; z-index: 1;" dir="{t_dir}">
                        {watermark_html}
                        <div style="position: relative; z-index: 2;">
                            <div style="display: flex; align-items: center; justify-content: center; border-bottom: 2px solid #ccc; padding-bottom: 20px; margin-bottom: 20px;">
                                {header_logo_html}
                                <div style="text-align: center;">
                                    <h1 style="margin: 0; color: #005b36; font-size: 26px; font-family: 'Arial', sans-serif;">{school_n_doc}</h1>
                                </div>
                            </div>
                            <div style="text-align: center;">
                                <h2 style="margin: 10px 0 20px 0; font-size: 22px; text-decoration: underline; color: #005b36;">{title_txt}</h2>
                            </div>
                            <p style="text-align: {t_align_opp}; font-weight: bold;">{date_lbl} {datetime.date.today().strftime("%d %B, %Y")}</p>
                            <p style="line-height: 1.8; font-size: 16px; text-align: justify;">{intro_txt}</p>
                            <h3 style="color: #005b36; margin-top: 30px;">{h1_txt}</h3>
                            <p style="line-height: 1.8; font-size: 16px; text-align: justify;">{p1_txt}</p>
                            <h3 style="color: #005b36;">{h2_txt}</h3>
                            <ul style="line-height: 1.8; font-size: 16px; text-align: {t_align};">
                                <li>{li1_txt}</li><li>{li2_txt}</li><li>{li3_txt}</li>
                            </ul>
                            <h3 style="color: #005b36;">{h3_txt}</h3>
                            <p style="line-height: 1.8; font-size: 16px; text-align: justify;">{p3_txt}</p>
                            <table style="width: 100%; margin-top: 80px; font-size: 16px;">
                                <tr>
                                    <td style="text-align: {t_align}; width: 50%;">_______________________<br><br><b>{sign_emp}</b><br>{e_name}</td>
                                    <td style="text-align: {t_align_opp}; width: 50%;">_______________________<br><br><b>{sign_prin}</b><br>{school_n_doc}</td>
                                </tr>
                            </table>
                        </div>
                    </div>
                    """
                    print_button_js(doc_html, tr("🖨️ پرنٹ کنٹریکٹ", "🖨️ Print Contract"), landscape=False)

            # 🟢 2. جاب ڈسکرپشن اور قواعد (Job Description & Code of Conduct)
            elif doc_type == "Job Description & Code of Conduct":
                st.info(tr("یہ لیٹر ایمپلائی کے عہدے کے حساب سے آٹو جنریٹ ہوگا۔", "This document will auto-generate based on employee designation."))
                if st.button(tr("ڈیوٹیز اور رولز جنریٹ کریں", "Generate Duties & Rules"), type="primary"):
                    
                    e_desig_lower = e_desig.lower()
                    if "teacher" in e_desig_lower or "استاد" in e_desig_lower or "ٹیچر" in e_desig_lower:
                        duties_en = "<li>Plan, prepare and deliver instructional activities to students.</li><li>Maintain discipline in the classroom and school premises.</li><li>Check and grade students' assignments and tests regularly.</li><li>Communicate with parents regarding student progress and behavior.</li>"
                        duties_ur = "<li>سبق کی بہترین منصوبہ بندی کرنا اور کلاس میں موثر انداز میں پڑھانا۔</li><li>کلاس اور سکول میں بچوں کا مکمل ڈسپلن برقرار رکھنا۔</li><li>طلباء کا ہوم ورک اور ٹیسٹ باقاعدگی سے چیک کرنا۔</li><li>والدین کے ساتھ طلباء کی کارکردگی اور رویے کے حوالے سے رابطہ رکھنا۔</li>"
                    elif "principal" in e_desig_lower or "پرنسپل" in e_desig_lower:
                        duties_en = "<li>Oversee day-to-day school operations and administration.</li><li>Monitor and evaluate teaching and non-teaching staff performance.</li><li>Ensure academic excellence and curriculum implementation.</li>"
                        duties_ur = "<li>سکول کے روزمرہ کے انتظامی اور تعلیمی معاملات کی نگرانی کرنا۔</li><li>تمام سٹاف کی کارکردگی کا جائزہ لینا اور رہنمائی فراہم کرنا۔</li><li>نصاب کی بروقت تکمیل اور تعلیمی معیار کو یقینی بنانا۔</li>"
                    elif "clerk" in e_desig_lower or "کلرک" in e_desig_lower or "operator" in e_desig_lower:
                        duties_en = "<li>Maintain accurate student, staff, and financial records.</li><li>Handle fee collection, generate reports, and issue receipts.</li><li>Manage front desk inquiries and official school correspondence.</li>"
                        duties_ur = "<li>طلباء اور سٹاف کا مکمل ریکارڈ اور فائلیں درست حالت میں رکھنا۔</li><li>فیس کی وصولی کرنا، رپورٹس بنانا اور رسیدیں جاری کرنا۔</li><li>آفس میں آنے والے والدین کی رہنمائی اور دفتری خط و کتابت سنبھالنا۔</li>"
                    elif "guard" in e_desig_lower or "گارڈ" in e_desig_lower or "security" in e_desig_lower:
                        duties_en = "<li>Control the main gate and maintain accurate visitor logs.</li><li>Ensure the safety and security of students and school property.</li><li>Monitor students strictly during arrival and departure times.</li>"
                        duties_ur = "<li>مین گیٹ کا کنٹرول سنبھالنا اور آنے جانے والے تمام افراد کا ریکارڈ رکھنا۔</li><li>سکول کی عمارت اور طلباء کی مکمل حفاظت کو یقینی بنانا۔</li><li>چھٹی اور آمد کے وقت طلباء کی بحفاظت روانگی کی نگرانی کرنا۔</li>"
                    elif "maid" in e_desig_lower or "peon" in e_desig_lower or "آیا" in e_desig_lower or "چپڑاسی" in e_desig_lower:
                        duties_en = "<li>Maintain extreme cleanliness of classrooms, offices, and washrooms.</li><li>Serve water/tea to staff and guests.</li><li>Assist teachers in managing and controlling junior students.</li>"
                        duties_ur = "<li>کلاس رومز، آفس اور واش رومز کی صفائی کا اعلیٰ معیار برقرار رکھنا۔</li><li>سٹاف اور مہمانوں کو پانی/چائے وغیرہ پیش کرنا۔</li><li>چھوٹی کلاسز کے بچوں کو سنبھالنے میں ٹیچرز کی مدد کرنا۔</li>"
                    else:
                        duties_en = "<li>Perform all operational duties assigned by the Principal/Administration.</li><li>Maintain a professional approach and integrity towards all tasks.</li><li>Assist colleagues to ensure smooth operations of the school.</li>"
                        duties_ur = "<li>پرنسپل یا انتظامیہ کی طرف سے دی گئی تمام ذمہ داریاں پوری کرنا۔</li><li>اپنے کام کو مکمل ایمانداری اور پیشہ ورانہ انداز میں کرنا۔</li><li>سکول کے کاموں میں دیگر سٹاف ممبران کے ساتھ مکمل تعاون کرنا۔</li>"
                    
                    sel_duties = duties_en if is_eng else duties_ur
                    
                    rules_en = "<li><b>Punctuality:</b> Must arrive at least 15 minutes before school timings.</li><li><b>Leaves:</b> Pre-approval is required for any leave. Uninformed leaves will result in salary deduction.</li><li><b>Weekend Leaves:</b> Taking a leave on Saturday and Monday will be counted as three leaves.</li><li><b>Dress Code:</b> Maintain a highly professional and decent dress code.</li><li><b>Mobile Phones:</b> Unnecessary use of mobile phones during duty hours is strictly prohibited.</li><li><b>Behavior:</b> Show utmost respect to all colleagues, students, and parents.</li><li><b>Disciplinary Action:</b> Failure to comply with these rules will result in the issuance of a warning letter.</li>"
                    rules_ur = "<li><b>وقت کی پابندی:</b> سکول کے مقررہ وقت سے کم از کم 15 منٹ پہلے حاضر ہونا لازمی ہے۔</li><li><b>چھٹی کا اصول:</b> کسی بھی چھٹی کے لیے پیشگی منظوری لازمی ہے۔ بغیر اطلاع چھٹی پر تنخواہ کٹوتی کی جائے گی۔</li><li><b>ہفتہ اور پیر کی چھٹی:</b> ہفتہ اور پیر کو چھٹی کرنے پر اسے تین چھٹیاں شمار کیا جائے گا۔</li><li><b>لباس اور وردی:</b> ڈیوٹی کے دوران باوقار اور مناسب لباس پہننا لازمی ہے۔</li><li><b>موبائل فون:</b> ڈیوٹی اور کلاس کے اوقات میں موبائل فون کا غیر ضروری استعمال سختی سے منع ہے۔</li><li><b>رویہ اور اخلاق:</b> تمام سٹاف، طلباء اور والدین کے ساتھ انتہائی خوش اخلاقی اور عزت سے پیش آنا لازمی ہے۔</li><li><b>تادیبی کارروائی:</b> تمام رولز کو فالو نہ کرنے کی صورت میں وارننگ لیٹر جاری کیا جائے گا۔</li>"
                    
                    sel_rules = rules_en if is_eng else rules_ur
                    
                    title_txt = "JOB DESCRIPTION & CODE OF CONDUCT" if is_eng else "ڈیوٹیز اور قواعد و ضوابط"
                    h1_txt = "Primary Responsibilities (Duties)" if is_eng else "بنیادی ذمہ داریاں (ڈیوٹیز)"
                    h2_txt = "School Rules & Discipline" if is_eng else "سکول کے قواعد و ضوابط (ڈسپلن)"
                    
                    ack_txt = "I have carefully read and understood all my duties and the rules of the institution. I agree to strictly abide by them. I understand that any violation of these rules may lead to strict disciplinary action by the administration." if is_eng else "میں نے اپنی ڈیوٹیز اور سکول کے تمام قواعد و ضوابط کو پڑھ اور سمجھ لیا ہے۔ میں ان پر مکمل عمل کرنے کا پابند رہوں گا/گی۔ خلاف ورزی کی صورت میں سکول انتظامیہ سخت تادیبی کارروائی کا حق محفوظ رکھتی ہے۔"
                    
                    sign_emp = "Employee's Signature" if is_eng else "ملازم کے دستخط"
                    sign_prin = "Principal's Signature" if is_eng else "پرنسپل کے دستخط"

                    # 🟢 سنگل پیج پر فکس کرنے کے لیے پیڈنگ اور مارجنز کو ایڈجسٹ کر دیا گیا ہے
                    doc_html = f"""
                    {font_css}
                    <div style="font-family: {f_family}; padding: 25px 35px; max-width: 800px; margin: 0 auto; border: 2px solid #1a4f8b; background: white; position: relative; z-index: 1; box-sizing: border-box; page-break-inside: avoid;" dir="{t_dir}">
                        {watermark_html}
                        <div style="position: relative; z-index: 2;">
                            <div style="display: flex; align-items: center; justify-content: center; border-bottom: 2px solid #ccc; padding-bottom: 10px; margin-bottom: 15px;">
                                {header_logo_html}
                                <div style="text-align: center;">
                                    <h1 style="margin: 0; color: #1a4f8b; font-size: 24px; font-family: 'Arial', sans-serif;">{school_n_doc}</h1>
                                </div>
                            </div>
                            <div style="text-align: center; margin-bottom: 15px;">
                                <h2 style="margin: 0; font-size: 20px; text-decoration: underline; color: #1a4f8b;">{title_txt}</h2>
                            </div>
                            
                            <table style="width: 100%; border-collapse: collapse; margin-bottom: 10px; font-size: 14px; font-family: 'Arial', sans-serif;" dir="ltr">
                                <tr>
                                    <td style="padding: 3px; width: 50%;"><b>Employee Name:</b> {e_name}</td>
                                    <td style="padding: 3px; width: 50%; text-align: right;"><b>Staff ID:</b> {s_id}</td>
                                </tr>
                                <tr>
                                    <td style="padding: 3px; width: 50%;"><b>Designation:</b> {e_desig}</td>
                                    <td style="padding: 3px; width: 50%; text-align: right;"><b>Date:</b> {datetime.date.today().strftime('%d %b, %Y')}</td>
                                </tr>
                            </table>
                            
                            <h3 style="color: #1a4f8b; margin-top: 10px; margin-bottom: 5px; border-bottom: 1px solid #ccc; padding-bottom: 3px; font-size: 16px;">{h1_txt}</h3>
                            <ul style="line-height: 1.5; font-size: 14px; text-align: justify; padding-left: 20px; padding-right: 20px; margin-top: 5px; margin-bottom: 10px;">
                                {sel_duties}
                            </ul>
                            
                            <h3 style="color: #1a4f8b; margin-top: 10px; margin-bottom: 5px; border-bottom: 1px solid #ccc; padding-bottom: 3px; font-size: 16px;">{h2_txt}</h3>
                            <ul style="line-height: 1.5; font-size: 14px; text-align: justify; padding-left: 20px; padding-right: 20px; margin-top: 5px; margin-bottom: 10px;">
                                {sel_rules}
                            </ul>
                            
                            <div style="margin-top: 15px; padding: 10px; background-color: rgba(240, 240, 240, 0.7); border-radius: 5px; font-size: 13px; text-align: justify; font-weight: bold; border-left: 4px solid #1a4f8b; border-right: 4px solid #1a4f8b;">
                                {ack_txt}
                            </div>
                            
                            <table style="width: 100%; margin-top: 40px; font-size: 15px;">
                                <tr>
                                    <td style="text-align: {t_align}; width: 50%;">_______________________<br><br><b>{sign_emp}</b></td>
                                    <td style="text-align: {t_align_opp}; width: 50%;">_______________________<br><br><b>{sign_prin}</b></td>
                                </tr>
                            </table>
                        </div>
                    </div>
                    """
                    print_button_js(doc_html, tr("🖨️ پرنٹ ڈیوٹیز لیٹر", "🖨️ Print Duties Letter"), landscape=False)

            # 🟢 3. جوائننگ رپورٹ (Joining Report)
            elif doc_type == "Joining Report":
                st.info(tr("جوائننگ رپورٹ کی تفصیلات:", "Joining Report Details:"))
                j_date = st.date_input(tr("جوائننگ کی اصل تاریخ", "Actual Joining Date"), value=datetime.date.today())
                
                if st.button(tr("جوائننگ رپورٹ جنریٹ کریں", "Generate Joining Report"), type="primary"):
                    title_txt = "JOINING REPORT" if is_eng else "جوائننگ رپورٹ"
                    to_txt = "To," if is_eng else "بخدمت،"
                    prin_txt = f"The Principal,<br>{school_n_doc}" if is_eng else f"جناب پرنسپل صاحب،<br>{school_n_doc}"
                    sub_txt = f"Subject: <u>Joining Report as {e_desig}</u>" if is_eng else f"عنوان: <u>جوائننگ رپورٹ بطور {e_desig}</u>"
                    resp_txt = "Respected Sir/Madam," if is_eng else "جنابِ عالی،"
                    
                    p1_txt = f"With reference to my appointment for the post of <b>{e_desig}</b> at your prestigious institution, I, <b>{e_name}</b> {rel_label} <b>{e_fname}</b>, hereby report for duty in the forenoon of <b>{j_date.strftime('%d %B, %Y')}</b>." if is_eng else f"آپ کے موقر ادارے میں <b>{e_desig}</b> کی آسامی پر تقرری کے حوالے سے، میں، <b>{e_name}</b> {rel_label} <b>{e_fname}</b>، آج مورخہ <b>{j_date.strftime('%d %B, %Y')}</b> کو اپنی ڈیوٹی پر باقاعدہ حاضر ہو رہا/رہی ہوں۔"
                    p2_txt = "I assure you that I will perform my duties with full dedication, honesty, and strictly follow all the rules and regulations of the school." if is_eng else "میں یقین دلاتا/دلاتی ہوں کہ میں اپنے فرائض پوری ایمانداری اور لگن سے انجام دوں گا/گی اور سکول کے تمام قواعد و ضوابط کی مکمل پابندی کروں گا/گی۔"
                    
                    thx_txt = "Thanking you," if is_eng else "العارض،"
                    yours_txt = "Yours Sincerely," if is_eng else "آپ کا/کی مخلص،"
                    date_lbl = "Date:" if is_eng else "تاریخ:"
                    id_lbl = "Employee ID:" if is_eng else "سٹاف آئی ڈی:"
                    sign_lbl = "Signature" if is_eng else "دستخط"

                    doc_html = f"""
                    {font_css}
                    <div style="font-family: {f_family}; padding: 40px; max-width: 800px; margin: 0 auto; border: 2px solid #333; background: white; position: relative; z-index: 1;" dir="{t_dir}">
                        {watermark_html}
                        <div style="position: relative; z-index: 2;">
                            <div style="display: flex; align-items: center; justify-content: center; margin-bottom: 20px;">
                                {header_logo_html}
                                <div style="text-align: center;">
                                    <h1 style="margin: 0; color: #333; font-size: 26px; font-family: 'Arial', sans-serif;">{school_n_doc}</h1>
                                </div>
                            </div>
                            <div style="text-align: center; margin-bottom: 30px;">
                                <h2 style="margin: 10px 0 0 0; font-size: 22px; text-decoration: underline;">{title_txt}</h2>
                            </div>
                            <p style="font-weight: bold; margin-bottom: 5px;">{to_txt}</p>
                            <p style="margin-top: 0;">{prin_txt}</p>
                            <p style="font-weight: bold; margin-top: 30px;">{sub_txt}</p>
                            <p style="margin-top: 30px;">{resp_txt}</p>
                            <p style="line-height: 2.0; font-size: 16px; text-align: justify; text-indent: 40px;">{p1_txt}</p>
                            <p style="line-height: 2.0; font-size: 16px; text-align: justify; text-indent: 40px;">{p2_txt}</p>
                            <p style="margin-top: 40px;">{thx_txt}</p>
                            <table style="width: 100%; margin-top: 40px; font-size: 16px;">
                                <tr>
                                    <td style="text-align: {t_align}; width: 50%; vertical-align: bottom;"><b>{date_lbl}</b> {datetime.date.today().strftime("%d %B, %Y")}<br><b>{id_lbl}</b> {s_id}</td>
                                    <td style="text-align: {t_align_opp}; width: 50%;">{yours_txt}<br><br><br>_______________________<br><br><b>{sign_lbl}</b></td>
                                </tr>
                            </table>
                        </div>
                    </div>
                    """
                    print_button_js(doc_html, tr("🖨️ پرنٹ جوائننگ رپورٹ", "🖨️ Print Joining Report"), landscape=False)

            # 🟢 4. اینول کانفیڈینشل رپورٹ (ACR)
            elif doc_type == "Annual Confidential Report (ACR)":
                st.info(tr("سٹاف کی کارکردگی کی درجہ بندی کریں:", "Rate staff performance:"))
                rc1, rc2, rc3 = st.columns(3)
                eval_year = rc1.text_input(tr("تشخیص کا سال (Year)", "Evaluation Year"), value="2026-2027")
                
                perf_opts = ["Excellent", "Good", "Satisfactory", "Poor"] if is_eng else ["بہترین (Excellent)", "اچھا (Good)", "تسلی بخش (Satisfactory)", "ناقص (Poor)"]
                punctuality = rc2.selectbox(tr("وقت کی پابندی", "Punctuality"), perf_opts)
                behavior = rc3.selectbox(tr("اخلاق اور رویہ", "Behavior & Attitude"), perf_opts)
                
                rc4, rc5 = st.columns(2)
                teaching_skills = rc4.selectbox(tr("تدریسی مہارت / کام", "Teaching/Work Skills"), perf_opts)
                grade_opts = ["A+ (Outstanding)", "A (Very Good)", "B (Good)", "C (Average)"] if is_eng else ["A+ (شاندار)", "A (بہت اچھا)", "B (اچھا)", "C (اوسط)"]
                overall_grade = rc5.selectbox(tr("مجموعی گریڈ (Overall)", "Overall Grade"), grade_opts)
                p_remarks = st.text_input(tr("پرنسپل کے ریمارکس", "Principal's Remarks"), placeholder="e.g. Hardworking and dedicated...")
                
                if st.button(tr("ACR جنریٹ کریں", "Generate ACR"), type="primary"):
                    t_title = "Annual Confidential Report (ACR)" if is_eng else "سالانہ خفیہ کارکردگی رپورٹ (ACR)"
                    t_eval = "Evaluation Year:" if is_eng else "تشخیص کا سال:"
                    t_p1 = "PART I: EMPLOYEE DETAILS" if is_eng else "حصہ اول: ملازم کی تفصیلات"
                    t_emp = "Employee Name:" if is_eng else "ملازم کا نام:"
                    t_sid = "Staff ID:" if is_eng else "سٹاف آئی ڈی:"
                    t_desig = "Designation:" if is_eng else "عہدہ:"
                    t_doj = "Date of Joining:" if is_eng else "تاریخِ شمولیت:"
                    
                    t_p2 = "PART II: PERFORMANCE EVALUATION" if is_eng else "حصہ دوم: کارکردگی کا جائزہ"
                    t_th1 = "Evaluation Criteria" if is_eng else "تشخیص کا معیار"
                    t_th2 = "Rating" if is_eng else "درجہ بندی"
                    t_c1 = "1. Punctuality & Regularity" if is_eng else "1. وقت کی پابندی اور حاضری"
                    t_c2 = "2. Behavior & Professional Attitude" if is_eng else "2. اخلاق اور پیشہ ورانہ رویہ"
                    t_c3 = "3. Job / Teaching Skills" if is_eng else "3. دفتری / تدریسی مہارت"
                    
                    t_p3 = "PART III: OVERALL ASSESSMENT" if is_eng else "حصہ سوم: مجموعی جائزہ"
                    t_rem = "Principal's Remarks:" if is_eng else "پرنسپل کے ریمارکس:"
                    t_grad = "Overall Grading:" if is_eng else "مجموعی گریڈنگ:"
                    t_date = "Date of Assessment:" if is_eng else "تاریخِ جائزہ:"
                    t_sign = "Signature of Principal / Authority" if is_eng else "دستخط مجاز افسر / پرنسپل"

                    doc_html = f"""
                    {font_css}
                    <div style="font-family: {f_family}; padding: 40px; max-width: 800px; margin: 0 auto; border: 1px solid #000; background: white; position: relative; z-index: 1;" dir="{t_dir}">
                        {watermark_html}
                        <div style="position: relative; z-index: 2;">
                            <div style="display: flex; align-items: center; justify-content: center; border-bottom: 3px double #000; padding-bottom: 15px; margin-bottom: 20px;">
                                {header_logo_html}
                                <div style="text-align: center;">
                                    <h1 style="margin: 0; color: #000; font-size: 24px; font-family: 'Arial', sans-serif;">{school_n_doc}</h1>
                                    <h2 style="margin: 5px 0 0 0; font-size: 18px;">{t_title}</h2>
                                    <p style="margin: 5px 0 0 0; font-weight: bold; font-size: 14px;">{t_eval} {eval_year}</p>
                                </div>
                            </div>
                            <h3 style="background-color: rgba(240, 240, 240, 0.9); padding: 5px; font-size: 16px;">{t_p1}</h3>
                            <table style="width: 100%; border-collapse: collapse; margin-bottom: 20px; font-size: 15px;">
                                <tr><td style="padding: 8px; border: 1px solid #ccc; width: 50%;"><b>{t_emp}</b> {e_name}</td>
                                    <td style="padding: 8px; border: 1px solid #ccc; width: 50%;"><b>{t_sid}</b> {s_id}</td></tr>
                                <tr><td style="padding: 8px; border: 1px solid #ccc;"><b>{t_desig}</b> {e_desig}</td>
                                    <td style="padding: 8px; border: 1px solid #ccc;"><b>{t_doj}</b> {e_join}</td></tr>
                            </table>
                            <h3 style="background-color: rgba(240, 240, 240, 0.9); padding: 5px; font-size: 16px;">{t_p2}</h3>
                            <table style="width: 100%; border-collapse: collapse; margin-bottom: 20px; font-size: 15px;">
                                <tr style="background-color: rgba(240, 240, 240, 0.5);">
                                    <th style="padding: 8px; border: 1px solid #ccc; text-align: {t_align}; width: 60%;">{t_th1}</th>
                                    <th style="padding: 8px; border: 1px solid #ccc; text-align: center; width: 40%;">{t_th2}</th>
                                </tr>
                                <tr><td style="padding: 8px; border: 1px solid #ccc;">{t_c1}</td><td style="padding: 8px; border: 1px solid #ccc; text-align: center; font-weight:bold;">{punctuality}</td></tr>
                                <tr><td style="padding: 8px; border: 1px solid #ccc;">{t_c2}</td><td style="padding: 8px; border: 1px solid #ccc; text-align: center; font-weight:bold;">{behavior}</td></tr>
                                <tr><td style="padding: 8px; border: 1px solid #ccc;">{t_c3}</td><td style="padding: 8px; border: 1px solid #ccc; text-align: center; font-weight:bold;">{teaching_skills}</td></tr>
                            </table>
                            <h3 style="background-color: rgba(240, 240, 240, 0.9); padding: 5px; font-size: 16px;">{t_p3}</h3>
                            <div style="border: 1px solid #ccc; padding: 15px; font-size: 16px; background-color: rgba(255, 255, 255, 0.7);">
                                <p><b>{t_rem}</b> {p_remarks}</p>
                                <p><b>{t_grad}</b> <span style="font-size: 18px; font-weight: bold;">{overall_grade}</span></p>
                            </div>
                            <table style="width: 100%; margin-top: 60px; font-size: 15px;">
                                <tr>
                                    <td style="text-align: {t_align}; width: 50%;">{t_date} {datetime.date.today().strftime("%d-%m-%Y")}</td>
                                    <td style="text-align: {t_align_opp}; width: 50%;">_______________________<br><br><b>{t_sign}</b></td>
                                </tr>
                            </table>
                        </div>
                    </div>
                    """
                    print_button_js(doc_html, tr("🖨️ پرنٹ ACR", "🖨️ Print ACR"), landscape=False)

            # 🟢 5. سیلری سرٹیفکیٹ (Salary Certificate)
            elif doc_type == "Salary Certificate":
                st.info(tr("مہینہ اور مقصد درج کریں:", "Enter month and purpose:"))
                sc1, sc2 = st.columns(2)
                sal_month = sc1.text_input(tr("مہینہ اور سال", "Month & Year"), value=datetime.date.today().strftime("%B, %Y"))
                sal_purpose = sc2.text_input(tr("مقصد (Purpose)", "Purpose"), value="Bank Loan / Official Purpose" if is_eng else "ذاتی ریکارڈ / بینک لون")
                
                if st.button(tr("سیلری سرٹیفکیٹ جنریٹ کریں", "Generate Salary Certificate"), type="primary"):
                    title_txt = "TO WHOM IT MAY CONCERN" if is_eng else "تصدیق نامہ (جس کے لیے متعلقہ ہو)"
                    date_lbl = "Date:" if is_eng else "تاریخ:"
                    
                    p1_txt = f"This is to certify that <b>{e_name}</b> {rel_label} <b>{e_fname}</b> is a bonafide employee of <b>{school_n_doc}</b>. {'He' if pron_sub=='He' else 'She'} has been working with us in the capacity of <b>{e_desig}</b> since <b>{e_join}</b>." if is_eng else f"یہ تصدیق کی جاتی ہے کہ <b>{e_name}</b> {rel_label} <b>{e_fname}</b> <b>{school_n_doc}</b> کے/کی باقاعدہ ملازم ہیں۔ آپ <b>{e_join}</b> سے بطور <b>{e_desig}</b> ہمارے ادارے میں خدمات انجام دے رہے/رہی ہیں۔"
                    p2_txt = f"{pron_pos_cap} current gross monthly salary for the month of <b>{sal_month}</b> is <b>Rs. {e_salary}/-</b>." if is_eng else f"ان کی موجودہ ماہانہ تنخواہ برائے ماہ <b>{sal_month}</b> مبلغ <b>{e_salary}/- روپے</b> ہے۔"
                    p3_txt = f"This certificate is being issued upon the request of the employee for the purpose of <i>{sal_purpose}</i>. We wish {'him' if pron_obj=='him' else 'her'} all the best." if is_eng else f"یہ سرٹیفکیٹ ملازم کی درخواست پر <i>{sal_purpose}</i> کے مقصد کے لیے جاری کیا جا رہا ہے۔ ہم ان کے روشن مستقبل کے لیے دعا گو ہیں۔"
                    
                    sign_lbl = "Authorized Signatory" if is_eng else "مجاز افسر کے دستخط"

                    doc_html = f"""
                    {font_css}
                    <div style="font-family: {f_family}; padding: 50px; max-width: 800px; margin: 0 auto; border: 2px solid #333; background: white; position: relative; z-index: 1;" dir="{t_dir}">
                        {watermark_html}
                        <div style="position: relative; z-index: 2;">
                            <div style="display: flex; align-items: center; justify-content: center; margin-bottom: 30px;">
                                {header_logo_html}
                                <div style="text-align: center;">
                                    <h1 style="margin: 0; color: #333; font-size: 26px; font-family: 'Arial', sans-serif;">{school_n_doc}</h1>
                                </div>
                            </div>
                            <div style="text-align: center; margin-bottom: 40px;">
                                <h2 style="margin: 10px 0 0 0; font-size: 22px; text-decoration: underline;">{title_txt}</h2>
                            </div>
                            <p style="text-align: {t_align_opp}; font-weight: bold;">{date_lbl} {datetime.date.today().strftime("%d %B, %Y")}</p>
                            <p style="line-height: 2.0; font-size: 16px; text-align: justify; margin-top: 40px;">{p1_txt}</p>
                            <p style="line-height: 2.0; font-size: 16px; text-align: justify;">{p2_txt}</p>
                            <p style="line-height: 2.0; font-size: 16px; text-align: justify;">{p3_txt}</p>
                            <table style="width: 100%; margin-top: 80px; font-size: 16px;">
                                <tr>
                                    <td style="text-align: {t_align}; width: 50%;"></td>
                                    <td style="text-align: {t_align_opp}; width: 50%;">_______________________<br><br><b>{sign_lbl}</b><br>{school_n_doc}</td>
                                </tr>
                            </table>
                        </div>
                    </div>
                    """
                    print_button_js(doc_html, tr("🖨️ پرنٹ سیلری سرٹیفکیٹ", "🖨️ Print Salary Certificate"), landscape=False)

            # 🟢 6. وارننگ لیٹر (Warning Letter)
            elif doc_type == "Warning / Show Cause Notice":
                st.error(tr("وارننگ کی وجہ اور تفصیل درج کریں:", "Enter warning reason and details:"))
                warn_reason = st.text_input(tr("مختصر وجہ (Reason)", "Short Reason"), value="Disciplinary Violation / Unapproved Absences" if is_eng else "ڈسپلن کی خلاف ورزی / غیر منظور شدہ چھٹیاں")
                warn_details = st.text_area(tr("تفصیلات (Details)", "Details"), value="It has been observed that you have violated school policies. You are advised to submit a written explanation within 3 days." if is_eng else "یہ مشاہدہ کیا گیا ہے کہ آپ نے سکول کی پالیسیوں کی خلاف ورزی کی ہے۔ آپ کو ہدایت کی جاتی ہے کہ 3 دن کے اندر تحریری جواب جمع کروائیں۔")
                
                if st.button(tr("وارننگ لیٹر جنریٹ کریں", "Generate Warning Letter"), type="primary"):
                    title_txt = "WARNING / SHOW CAUSE NOTICE" if is_eng else "شوکاز نوٹس / باضابطہ وارننگ"
                    to_txt = "To," if is_eng else "بنام:"
                    sub_txt = f"Subject: <u>Official Warning for {warn_reason}</u>" if is_eng else f"عنوان: <u>باضابطہ وارننگ بوجہ {warn_reason}</u>"
                    
                    p1_txt = f"This letter serves as a formal warning regarding your professional conduct. {warn_details}" if is_eng else f"یہ لیٹر آپ کی پیشہ ورانہ کارکردگی اور رویے کے حوالے سے ایک باضابطہ وارننگ ہے۔ {warn_details}"
                    p2_txt = "We expect you to correct your behavior immediately and adhere strictly to the institution's rules. Any further non-compliance or repetition of such actions will lead to severe disciplinary measures, which may include suspension or termination of your employment." if is_eng else "ہمیں امید ہے کہ آپ فوری طور پر اپنے رویے/کارکردگی کو درست کریں گے اور ادارے کے قوانین پر سختی سے عمل کریں گے۔ بصورتِ دیگر ادارہ سخت محکمانہ کارروائی کا حق محفوظ رکھتا ہے جس میں معطلی یا ملازمت سے برخاستگی شامل ہو سکتی ہے۔"
                    
                    date_lbl = "Date:" if is_eng else "تاریخ:"
                    id_lbl = "Staff ID:" if is_eng else "سٹاف آئی ڈی:"
                    sign_lbl = "Principal / HR Dept." if is_eng else "پرنسپل / ایچ آر ڈیپارٹمنٹ"

                    doc_html = f"""
                    {font_css}
                    <div style="font-family: {f_family}; padding: 40px; max-width: 800px; margin: 0 auto; border: 2px solid #8b0000; background: #fffcfc; position: relative; z-index: 1;" dir="{t_dir}">
                        {watermark_html}
                        <div style="position: relative; z-index: 2;">
                            <div style="display: flex; align-items: center; justify-content: center; margin-bottom: 20px;">
                                {header_logo_html}
                                <div style="text-align: center;">
                                    <h1 style="margin: 0; color: #333; font-size: 26px; font-family: 'Arial', sans-serif;">{school_n_doc}</h1>
                                </div>
                            </div>
                            <div style="text-align: center; margin-bottom: 30px;">
                                <h2 style="margin: 10px 0 0 0; color: #8b0000; font-size: 22px; text-decoration: underline;">{title_txt}</h2>
                            </div>
                            <p style="font-weight: bold; margin-bottom: 5px;">{to_txt}</p>
                            <p style="margin-top: 0;"><b>{e_name}</b><br>{e_desig}<br>{id_lbl} {s_id}</p>
                            <p style="font-weight: bold; margin-top: 30px;">{sub_txt}</p>
                            <p style="line-height: 1.8; font-size: 16px; text-align: justify; margin-top: 30px;">{p1_txt}</p>
                            <p style="line-height: 1.8; font-size: 16px; text-align: justify;">{p2_txt}</p>
                            <table style="width: 100%; margin-top: 60px; font-size: 16px;">
                                <tr>
                                    <td style="text-align: {t_align}; width: 50%; vertical-align: bottom;"><b>{date_lbl}</b> {datetime.date.today().strftime("%d %B, %Y")}</td>
                                    <td style="text-align: {t_align_opp}; width: 50%;">_______________________<br><br><b>{sign_lbl}</b><br>{school_n_doc}</td>
                                </tr>
                            </table>
                        </div>
                    </div>
                    """
                    print_button_js(doc_html, tr("🖨️ پرنٹ وارننگ لیٹر", "🖨️ Print Warning Letter"), landscape=False)

            # 🟢 7. ٹرمینیشن لیٹر (Termination Letter)
            elif doc_type == "Termination Letter":
                st.error(tr("برخاستگی کی تفصیلات درج کریں:", "Enter termination details:"))
                term_date = st.date_input(tr("آخری دن (Effective Date)", "Effective Date"), value=datetime.date.today())
                term_reason = st.text_input(tr("وجہ (Reason)", "Reason"), value="Continuous poor performance and violation of policies." if is_eng else "مسلسل غیر تسلی بخش کارکردگی اور سکول کی پالیسیوں کی خلاف ورزی۔")
                
                if st.button(tr("ٹرمینیشن لیٹر جنریٹ کریں", "Generate Termination Letter"), type="primary"):
                    title_txt = "TERMINATION OF EMPLOYMENT" if is_eng else "ملازمت سے برخاستگی (ٹرمینیشن لیٹر)"
                    to_txt = "To," if is_eng else "بنام:"
                    
                    p1_txt = f"We regret to inform you that your employment with <b>{school_n_doc}</b> as a <b>{e_desig}</b> is being terminated, effective <b>{term_date.strftime('%d %B, %Y')}</b>." if is_eng else f"ہمیں آپ کو یہ بتاتے ہوئے افسوس ہے کہ <b>{school_n_doc}</b> میں بطور <b>{e_desig}</b> آپ کی ملازمت مورخہ <b>{term_date.strftime('%d %B, %Y')}</b> سے ختم کی جا رہی ہے۔"
                    p2_txt = f"This decision has been made due to: <i>{term_reason}</i>." if is_eng else f"یہ فیصلہ درج ذیل وجوہات کی بنا پر کیا گیا ہے: <i>{term_reason}</i>"
                    p3_txt = "You are requested to return all school property, including ID cards, keys, and documents, to the administration immediately. Please contact the Accounts Department to settle your final clearance and outstanding dues." if is_eng else "آپ سے گزارش ہے کہ سکول کی تمام املاک، بشمول شناختی کارڈ، چابیاں، اور دیگر دستاویزات فوری طور پر انتظامیہ کو واپس کر دیں۔ اپنے حتمی واجبات (Clearance) کی ادائیگی کے لیے اکاؤنٹس ڈیپارٹمنٹ سے رابطہ کریں۔"
                    
                    date_lbl = "Date:" if is_eng else "تاریخ:"
                    id_lbl = "Staff ID:" if is_eng else "سٹاف آئی ڈی:"
                    sign_lbl = "Principal / HR Dept." if is_eng else "پرنسپل / ایچ آر ڈیپارٹمنٹ"

                    doc_html = f"""
                    {font_css}
                    <div style="font-family: {f_family}; padding: 40px; max-width: 800px; margin: 0 auto; border: 2px solid #000; background: white; position: relative; z-index: 1;" dir="{t_dir}">
                        {watermark_html}
                        <div style="position: relative; z-index: 2;">
                            <div style="display: flex; align-items: center; justify-content: center; margin-bottom: 20px;">
                                {header_logo_html}
                                <div style="text-align: center;">
                                    <h1 style="margin: 0; color: #333; font-size: 26px; font-family: 'Arial', sans-serif;">{school_n_doc}</h1>
                                </div>
                            </div>
                            <div style="text-align: center; margin-bottom: 30px;">
                                <h2 style="margin: 10px 0 0 0; font-size: 22px; text-decoration: underline;">{title_txt}</h2>
                            </div>
                            <p style="font-weight: bold; margin-bottom: 5px;">{to_txt}</p>
                            <p style="margin-top: 0;"><b>{e_name}</b><br>{e_desig}<br>{id_lbl} {s_id}</p>
                            <p style="line-height: 1.8; font-size: 16px; text-align: justify; margin-top: 30px;">{p1_txt}</p>
                            <p style="line-height: 1.8; font-size: 16px; text-align: justify;">{p2_txt}</p>
                            <p style="line-height: 1.8; font-size: 16px; text-align: justify;">{p3_txt}</p>
                            <table style="width: 100%; margin-top: 60px; font-size: 16px;">
                                <tr>
                                    <td style="text-align: {t_align}; width: 50%; vertical-align: bottom;"><b>{date_lbl}</b> {datetime.date.today().strftime("%d %B, %Y")}</td>
                                    <td style="text-align: {t_align_opp}; width: 50%;">_______________________<br><br><b>{sign_lbl}</b><br>{school_n_doc}</td>
                                </tr>
                            </table>
                        </div>
                    </div>
                    """
                    print_button_js(doc_html, tr("🖨️ پرنٹ ٹرمینیشن لیٹر", "🖨️ Print Termination Letter"), landscape=False)

        else:
            st.warning(tr("ڈیٹا بیس میں کوئی سٹاف موجود نہیں۔", "No staff found in database."))

# ================= 5. حاضری سسٹم =================
elif core_choice == "Attendance":
    st.markdown(f"<h2 class='no-print'>📋 {tr('حاضری مینجمنٹ', 'Attendance Management')} - {tr(sub_choice, sub_choice)}</h2>", unsafe_allow_html=True)
    
    st.markdown("""
    <style>
    /* Present / حاضر رنگ (سبز) */
    div[role="radiogroup"] label:has(input[value="Present"]:checked) div[data-testid="stMarkdownContainer"] p {
        color: #155724 !important;
        font-weight: bold !important;
    }
    /* Absent / غیر حاضر رنگ (سرخ) */
    div[role="radiogroup"] label:has(input[value="Absent"]:checked) div[data-testid="stMarkdownContainer"] p {
        color: #c53030 !important;
        font-weight: bold !important;
    }
    /* Leave / چھٹی رنگ (پیلا/نارنجی) */
    div[role="radiogroup"] label:has(input[value="Leave"]:checked) div[data-testid="stMarkdownContainer"] p {
        color: #b7791f !important;
        font-weight: bold !important;
    }
    </style>
    """, unsafe_allow_html=True)

    def format_stat(stat):
        if st.session_state.ui_lang == "English":
            return "Present" if stat=="Present" else "Absent" if stat=="Absent" else "Leave" if stat=="Leave" else stat
        else:
            return "حاضر" if stat=="Present" else "غیر حاضر" if stat=="Absent" else "چھٹی" if stat=="Leave" else stat

    if sub_choice == "Student Attendance":
        st.markdown(f"### {tr('طلباء کی حاضری لگائیں', 'Mark Student Attendance')}")
        c_att1, c_att2 = st.columns(2)
        att_class = c_att1.selectbox(tr("کلاس منتخب کریں", "Select Class"), classes_list, key="att_stu_cls")
        att_date = c_att2.date_input(tr("تاریخ", "Date"), datetime.date.today(), key="att_stu_date")

        # 🟢 کریش پروف سٹوڈنٹ لسٹ (اگر name_en کالم موجود نہ ہو تو ایپ بند نہیں ہوگی)
        try:
            local_conn = get_db_connection()
            # پہلی کوشش: انگلش نام والے کالم کے ساتھ
            stu_df = pd.read_sql(f"SELECT reg_id, name, name_en FROM students WHERE class='{att_class}' AND status='Active'", local_conn)
        except Exception:
            try:
                # دوسری کوشش: بغیر name_en کے (اگر پرانا ڈیٹا بیس ہے)
                stu_df = pd.read_sql(f"SELECT reg_id, name FROM students WHERE class='{att_class}' AND status='Active'", local_conn)
            except Exception:
                # 🟢 اگر کوئی اور بھی مسئلہ ہو تو کریش ہونے کے بجائے خالی لسٹ بن جائے گی
                import pandas as pd
                stu_df = pd.DataFrame()
        if not stu_df.empty:
            existing_att = pd.read_sql(f"SELECT person_id, status FROM attendance WHERE date='{att_date.strftime('%Y-%m-%d')}' AND type='طالب علم'", conn)
            att_map = dict(zip(existing_att['person_id'], existing_att['status']))

            with st.form("stu_att_form"):
                st.write(f"**Date:** {att_date.strftime('%d-%m-%Y')} | **Class:** {att_class}")
                att_dict = {}
                for _, r in stu_df.iterrows():
                    c1, c2 = st.columns([2, 2])
                    d_name = get_disp_val(r['name'], r.get('name_en'))
                    c1.markdown(f"<div style='padding-top:10px;'>{d_name} (Reg: {r['reg_id']})</div>", unsafe_allow_html=True)
                    
                    def_stat = att_map.get(r['reg_id'], "Present")
                    idx = ["Present", "Absent", "Leave"].index(def_stat) if def_stat in ["Present", "Absent", "Leave"] else 0
                    att_dict[r['reg_id']] = c2.radio("Status", ["Present", "Absent", "Leave"], index=idx, key=f"att_stu_{r['reg_id']}", horizontal=True, label_visibility="collapsed", format_func=format_stat)

                if st.form_submit_button(tr("حاضری محفوظ کریں", "Save Attendance")):
                    for r_id, sts in att_dict.items():
                        cursor.execute("DELETE FROM attendance WHERE date=? AND type='طالب علم' AND person_id=?", (att_date.strftime('%Y-%m-%d'), r_id))
                        cursor.execute("INSERT INTO attendance (date, type, person_id, status) VALUES (?, 'طالب علم', ?, ?)", (att_date.strftime('%Y-%m-%d'), r_id, sts))
                    conn.commit()
                    st.success(tr("طلباء کی حاضری محفوظ ہو گئی!", "Student attendance saved!"))
        else:
            st.info(tr("اس کلاس میں کوئی ایکٹو طالب علم نہیں ہے۔", "No active students in this class."))

    elif sub_choice == "Staff Attendance":
        st.markdown(f"### {tr('سٹاف کی حاضری لگائیں', 'Mark Staff Attendance')}")
        att_date_stf = st.date_input(tr("تاریخ", "Date"), datetime.date.today(), key="att_stf_date")
        stf_df = pd.read_sql("SELECT staff_id, name, name_en, designation FROM staff", conn)

        if not stf_df.empty:
            existing_att_stf = pd.read_sql(f"SELECT person_id, status FROM attendance WHERE date='{att_date_stf.strftime('%Y-%m-%d')}' AND type='سٹاف'", conn)
            att_map_stf = dict(zip(existing_att_stf['person_id'], existing_att_stf['status']))

            with st.form("stf_att_form"):
                st.write(f"**Date:** {att_date_stf.strftime('%d-%m-%Y')} | **Staff Attendance**")
                att_dict_stf = {}
                for _, r in stf_df.iterrows():
                    c1, c2 = st.columns([2, 2])
                    d_name = get_disp_val(r['name'], r.get('name_en'))
                    desig = get_desig_disp(r['designation'])
                    c1.markdown(f"<div style='padding-top:10px;'>{d_name} ({desig})</div>", unsafe_allow_html=True)
                    
                    def_stat = att_map_stf.get(r['staff_id'], "Present")
                    idx = ["Present", "Absent", "Leave"].index(def_stat) if def_stat in ["Present", "Absent", "Leave"] else 0
                    att_dict_stf[r['staff_id']] = c2.radio("Status", ["Present", "Absent", "Leave"], index=idx, key=f"att_stf_{r['staff_id']}", horizontal=True, label_visibility="collapsed", format_func=format_stat)

                if st.form_submit_button(tr("حاضری محفوظ کریں", "Save Attendance")):
                    for s_id, sts in att_dict_stf.items():
                        cursor.execute("DELETE FROM attendance WHERE date=? AND type='سٹاف' AND person_id=?", (att_date_stf.strftime('%Y-%m-%d'), s_id))
                        cursor.execute("INSERT INTO attendance (date, type, person_id, status) VALUES (?, 'سٹاف', ?, ?)", (att_date_stf.strftime('%Y-%m-%d'), s_id, sts))
                    conn.commit()
                    st.success(tr("سٹاف کی حاضری محفوظ ہو گئی!", "Staff attendance saved!"))
        else:
            st.info(tr("سٹاف کا کوئی ریکارڈ نہیں ملا۔", "No staff records found."))

    # 🟢 سمارٹ کیو-آر سکینر حاضری 
    elif sub_choice in ["Smart QR Attendance", "سمارٹ کیو-آر حاضری"]:
        st.markdown(f"### 📷 {tr('کیو-آر کوڈ / بارکوڈ سکینر حاضری', 'QR / Barcode Smart Attendance')}")
        st.info(tr("سکینر سے بچے یا سٹاف کا آئی ڈی کارڈ سکین کریں۔ حاضری خود بخود 'حاضر (Present)' لگ جائے گی۔", "Scan the student/staff ID card. Attendance will be marked as 'Present' automatically."))
        
        # فوکس کو ان پٹ پر رکھنے کے لیے جاوا سکرپٹ (تاکہ سکینر براہ راست کام کرے)
        components.html("""
        <script>
        setTimeout(function() {
            var inputs = window.parent.document.querySelectorAll('input[type="text"]');
            if(inputs.length > 0) {
                inputs[inputs.length - 1].focus();
            }
        }, 500);
        </script>
        """, height=0)
        
        with st.form("qr_att_form", clear_on_submit=True):
            qr_data = st.text_input(tr("یہاں کلک کر کے کارڈ سکین کریں (Click here to scan)", "Scan Card Here"))
            if st.form_submit_button(tr("سکین کریں (Scan)", "Scan"), use_container_width=True):
                if qr_data:
                    today_date_att = datetime.date.today().strftime('%Y-%m-%d')
                    
                    if "Student Reg:" in qr_data:
                        r_id = qr_data.split("Student Reg:")[1].strip()
                        s_data = pd.read_sql(f"SELECT name, name_en, class FROM students WHERE reg_id='{r_id}'", conn)
                        if not s_data.empty:
                            cursor.execute("DELETE FROM attendance WHERE date=? AND type='طالب علم' AND person_id=?", (today_date_att, r_id))
                            cursor.execute("INSERT INTO attendance (date, type, person_id, status) VALUES (?, 'طالب علم', ?, 'Present')", (today_date_att, r_id))
                            conn.commit()
                            s_name_disp = get_disp_val(s_data.iloc[0]['name'], s_data.iloc[0].get('name_en'))
                            st.success(f"✅ {s_name_disp} (Class: {s_data.iloc[0]['class']}) - Present!")
                            st.balloons()
                        else:
                            st.error(tr("یہ رول نمبر درست نہیں۔", "Invalid Registration Number."))
                            
                    elif "Staff ID:" in qr_data:
                        s_id = qr_data.split("Staff ID:")[1].strip()
                        s_data = pd.read_sql(f"SELECT name, name_en, designation FROM staff WHERE staff_id='{s_id}'", conn)
                        if not s_data.empty:
                            cursor.execute("DELETE FROM attendance WHERE date=? AND type='سٹاف' AND person_id=?", (today_date_att, s_id))
                            cursor.execute("INSERT INTO attendance (date, type, person_id, status) VALUES (?, 'سٹاف', ?, 'Present')", (today_date_att, s_id))
                            conn.commit()
                            s_name_disp = get_disp_val(s_data.iloc[0]['name'], s_data.iloc[0].get('name_en'))
                            st.success(f"✅ Staff: {s_name_disp} - Present!")
                        else:
                            st.error(tr("یہ سٹاف آئی ڈی درست نہیں۔", "Invalid Staff ID."))
                    else:
                        st.warning(tr("غلط کیو-آر کوڈ! براہ کرم سکول کا جاری کردہ کارڈ سکین کریں۔", "Invalid QR Code! Please scan the official school ID card."))

    elif sub_choice == "Attendance Report & Print":
        st.markdown(f"### {tr('حاضری کی رپورٹ اور پرنٹ', 'Attendance Report & Print')}")
        st.markdown("<div class='no-print'>", unsafe_allow_html=True)
        r_type = st.radio(tr("رپورٹ کی قسم", "Report Type"), [tr("طلباء (Students)", "Students"), tr("سٹاف (Staff)", "Staff")], horizontal=True)

        c_r1, c_r2 = st.columns(2)
        rep_date = c_r1.date_input(tr("رپورٹ کی تاریخ منتخب کریں", "Select Report Date"), datetime.date.today(), key="rep_date")

        if r_type in ["طلباء (Students)", "Students"]:
            rep_class = c_r2.selectbox(tr("کلاس منتخب کریں", "Select Class"), ["All"] + classes_list, key="rep_cls")
            q_stu = f"SELECT a.date, a.person_id, s.name, s.name_en, s.class, a.status FROM attendance a JOIN students s ON a.person_id = s.reg_id WHERE a.type='طالب علم' AND a.date='{rep_date.strftime('%Y-%m-%d')}'"
            if rep_class != "All": q_stu += f" AND s.class='{rep_class}'"
            
            # 🟢 کریش پروف رپورٹنگ کیوری (Crash-proof Query)
        try:
            local_conn = get_db_connection()
            rep_df = pd.read_sql(q_stu, local_conn)
        except Exception:
            try:
                # 🟢 اگر کوئی خاص کالم نہ ملے، تو سمارٹ طریقے سے موجودہ تمام کالمز نکال لے گا
                import re
                fallback_q = re.sub(r'SELECT.*?FROM', 'SELECT * FROM', q_stu, flags=re.IGNORECASE)
                rep_df = pd.read_sql(fallback_q, local_conn)
            except Exception:
                # 🟢 اگر پھر بھی کوئی مسئلہ ہو تو خالی رپورٹ دکھا دے گا مگر ایپ بند نہیں ہوگی
                import pandas as pd
                rep_df = pd.DataFrame()
            if not rep_df.empty:
                rep_df['Name'] = rep_df.apply(lambda row: get_disp_val(row['name'], row.get('name_en')), axis=1)
                
                if rep_class != "All":
                    print_df = rep_df[['person_id', 'Name', 'status']].copy()
                    print_df.columns = ['Reg No', 'Student Name', 'Status']
                else:
                    print_df = rep_df[['person_id', 'Name', 'class', 'status']].copy()
                    print_df.columns = ['Reg No', 'Student Name', 'Class', 'Status']
                
                print_df['Status'] = print_df['Status'].apply(format_stat)
                st.dataframe(print_df, use_container_width=True)

                html_table = print_df.to_html(index=False, border=1, justify='center', escape=False)
                html_table = html_table.replace('<td>Present</td>', '<td><span style="color:green;font-weight:bold;">Present</span></td>').replace('<td>Absent</td>', '<td><span style="color:red;font-weight:bold;">Absent</span></td>').replace('<td>Leave</td>', '<td><span style="color:orange;font-weight:bold;">Leave</span></td>')
                html_table = html_table.replace('<td>حاضر</td>', '<td><span style="color:green;font-weight:bold;">حاضر</span></td>').replace('<td>غیر حاضر</td>', '<td><span style="color:red;font-weight:bold;">غیر حاضر</span></td>').replace('<td>چھٹی</td>', '<td><span style="color:orange;font-weight:bold;">چھٹی</span></td>')
                
                t = {"align": "left", "dir": "ltr"} if st.session_state.ui_lang == "English" else {"align": "right", "dir": "rtl"}
                
                print_html = f'''
                <div style="width: 100%; font-family: Arial, sans-serif;" dir="{t['dir']}">
                <table style="width:100%; border:none; margin-bottom: 15px;">
                <tr>
                <td style="width: 15%; text-align: {t['align']}; vertical-align: middle;">{logo_base64_html}</td>
                <td style="width: 70%; text-align: center; vertical-align: middle;">
                <h2 style="margin: 0; font-size: 24px; color: #1a4f8b;">{school_name.upper()}</h2>
                <p style="margin: 4px 0; font-weight: bold; font-size: 12px;">{school_address}</p>
                <h3 style="margin: 10px 0 0 0; text-decoration: underline; font-weight: bold; font-size: 18px;">{tr('طلباء کی روزانہ حاضری رپورٹ', 'Daily Student Attendance Report')}</h3>
                <p style="margin: 5px 0 0 0; font-weight:bold; font-size: 14px;">Date: {rep_date.strftime('%d %b %Y')} | Class: {rep_class}</p>
                </td>
                <td style="width: 15%;"></td>
                </tr>
                </table>
                <div style="width:100%; display: flex; justify-content: center; margin-top:20px;" dir="{t['dir']}">
                {html_table.replace('<table', f'<table style="width:100%; border-collapse: collapse; text-align: center; font-size: 14px; border: 2px solid #000;"').replace('<th>', f'<th style="background-color:#eaeaea; border:1px solid #000; padding:8px; text-align:{t["align"]};">').replace('<td>', f'<td style="border:1px solid #000; padding:8px; text-align:{t["align"]};">')}
                </div>
                </div>
                '''
                if st.button("🖨️ " + tr("رپورٹ پرنٹ کریں", "Print Report")):
                    print_button_js(print_html, tr("پرنٹ کریں", "Print Now"), landscape=False)
            else:
                st.warning(tr("اس تاریخ اور کلاس کی کوئی حاضری محفوظ نہیں ہے۔", "No attendance saved for this date and class."))

        else: # Staff
            q_stf = f"SELECT a.date, a.person_id, s.name, s.name_en, s.designation, a.status FROM attendance a JOIN staff s ON a.person_id = s.staff_id WHERE a.type='سٹاف' AND a.date='{rep_date.strftime('%Y-%m-%d')}'"
            rep_df = pd.read_sql(q_stf, conn)
            if not rep_df.empty:
                rep_df['Name'] = rep_df.apply(lambda row: get_disp_val(row['name'], row.get('name_en')), axis=1)
                print_df = rep_df[['person_id', 'Name', 'designation', 'status']].copy()
                print_df.columns = ['Staff ID', 'Staff Name', 'Designation', 'Status']
                
                print_df['Status'] = print_df['Status'].apply(format_stat)
                st.dataframe(print_df, use_container_width=True)

                html_table = print_df.to_html(index=False, border=1, justify='center', escape=False)
                html_table = html_table.replace('<td>Present</td>', '<td><span style="color:green;font-weight:bold;">Present</span></td>').replace('<td>Absent</td>', '<td><span style="color:red;font-weight:bold;">Absent</span></td>').replace('<td>Leave</td>', '<td><span style="color:orange;font-weight:bold;">Leave</span></td>')
                html_table = html_table.replace('<td>حاضر</td>', '<td><span style="color:green;font-weight:bold;">حاضر</span></td>').replace('<td>غیر حاضر</td>', '<td><span style="color:red;font-weight:bold;">غیر حاضر</span></td>').replace('<td>چھٹی</td>', '<td><span style="color:orange;font-weight:bold;">چھٹی</span></td>')
                
                t = {"align": "left", "dir": "ltr"} if st.session_state.ui_lang == "English" else {"align": "right", "dir": "rtl"}
                
                print_html = f'''
                <div style="width: 100%; font-family: Arial, sans-serif;" dir="{t['dir']}">
                <table style="width:100%; border:none; margin-bottom: 15px;">
                <tr>
                <td style="width: 15%; text-align: {t['align']}; vertical-align: middle;">{logo_base64_html}</td>
                <td style="width: 70%; text-align: center; vertical-align: middle;">
                <h2 style="margin: 0; font-size: 24px; color: #1a4f8b;">{school_name.upper()}</h2>
                <p style="margin: 4px 0; font-weight: bold; font-size: 12px;">{school_address}</p>
                <h3 style="margin: 10px 0 0 0; text-decoration: underline; font-weight: bold; font-size: 18px;">{tr('سٹاف کی حاضری رپورٹ', 'Staff Attendance Report')}</h3>
                <p style="margin: 5px 0 0 0; font-weight:bold; font-size: 14px;">Date: {rep_date.strftime('%d %b %Y')}</p>
                </td>
                <td style="width: 15%;"></td>
                </tr>
                </table>
                <div style="width:100%; display: flex; justify-content: center; margin-top:20px;" dir="{t['dir']}">
                {html_table.replace('<table', f'<table style="width:100%; border-collapse: collapse; text-align: center; font-size: 14px; border: 2px solid #000;"').replace('<th>', f'<th style="background-color:#eaeaea; border:1px solid #000; padding:8px; text-align:{t["align"]};">').replace('<td>', f'<td style="border:1px solid #000; padding:8px; text-align:{t["align"]};">')}
                </div>
                </div>
                '''
                if st.button("🖨️ " + tr("رپورٹ پرنٹ کریں", "Print Report")):
                    print_button_js(print_html, tr("پرنٹ کریں", "Print Now"), landscape=False)
            else:
                st.warning(tr("اس تاریخ کی سٹاف کی کوئی حاضری محفوظ نہیں ہے۔", "No staff attendance saved for this date."))

elif core_choice in ["چھٹی کی درخواستیں", "Leave Requests"]:
    st.markdown(f"<h2 class='no-print'>📝 {tr('چھٹی کی درخواستیں', 'Leave Requests')}</h2>", unsafe_allow_html=True)
    
    # 🟢 یہاں کوئی فالتو try نہیں ہے، سیدھا کریش پروف کوڈ شروع ہو رہا ہے
    try:
        local_conn = get_db_connection()
        leave_q = "SELECT lr.id, lr.reg_id, s.name, s.name_en, s.class, s.section, lr.date, lr.reason, lr.status, lr.admin_remarks FROM leave_requests lr JOIN students s ON lr.reg_id = s.reg_id ORDER BY lr.id DESC"
        requests_df = pd.read_sql(leave_q, local_conn)
    except Exception:
        try:
            local_conn = get_db_connection()
            leave_q_fallback = "SELECT lr.id, lr.reg_id, s.name, s.class, lr.date, lr.reason, lr.status, lr.admin_remarks FROM leave_requests lr JOIN students s ON lr.reg_id = s.reg_id ORDER BY lr.id DESC"
            requests_df = pd.read_sql(leave_q_fallback, local_conn)
        except Exception:
            import pandas as pd
            requests_df = pd.DataFrame()
            
            if not req_df.empty:
                pending_reqs = req_df[req_df['status'] == 'Pending']
                history_reqs = req_df[req_df['status'] != 'Pending']
                
                tab_pending, tab_history = st.tabs([f"⏳ {tr('نئی درخواستیں', 'Pending Requests')} ({len(pending_reqs)})", f"📜 {tr('پچھلا ریکارڈ', 'History')} ({len(history_reqs)})"])
                
                with tab_pending:
                    if not pending_reqs.empty:
                        for _, r in pending_reqs.iterrows():
                            stu_name = get_disp_val(r['name'], r.get('name_en'))
                            with st.expander(f"📩 {stu_name} (Class: {r['class']} {r['section']}) - Date: {r['date']}"):
                                st.markdown(f"**{tr('درخواست کی وجہ:', 'Reason for Leave:')}**\n\n<div style='background-color:#f9f9f9; padding:10px; border-left:3px solid #ff9800;'>{r['reason']}</div>", unsafe_allow_html=True)
                                st.write(f"**{tr('رول نمبر:', 'Reg No:')}** {r['reg_id']}")
                                
                                rej_reason = st.text_input(tr("اگر درخواست مسترد کرنی ہو تو وجہ لکھیں (اختیاری):", "If rejecting, write reason (Optional):"), key=f"rej_res_{r['id']}")
                                
                                c_btn1, c_btn2, _ = st.columns([1, 1, 2])
                                if c_btn1.button("✅ " + tr("منظور کریں (Approve)", "Approve"), key=f"app_{r['id']}", type="primary"):
                                    # 1. درخواست کا سٹیٹس اپڈیٹ کرنا
                                    cursor.execute(f"UPDATE leave_requests SET status='Approved', admin_remarks='چھٹی منظور کر لی گئی ہے۔' WHERE id={r['id']}")
                                    
                                    # 2. آٹو حاضری (اس دن کی حاضری میں خودکار چھٹی لگانا)
                                    cursor.execute("DELETE FROM attendance WHERE date=? AND type='طالب علم' AND person_id=?", (r['date'], r['reg_id']))
                                    cursor.execute("INSERT INTO attendance (date, type, person_id, status) VALUES (?, 'طالب علم', ?, 'Leave')", (r['date'], r['reg_id']))
                                    conn.commit()
                                    
                                    st.success(tr("درخواست منظور ہو گئی اور حاضری رجسٹر میں خودکار 'چھٹی' لگ گئی۔", "Approved and automatically marked as Leave in attendance sheet."))
                                    import time
                                    time.sleep(1)
                                    st.rerun()
                                    
                                if c_btn2.button("❌ " + tr("مسترد کریں (Reject)", "Reject"), key=f"rej_{r['id']}"):
                                    final_remark = rej_reason if rej_reason.strip() else "چھٹی کی درخواست نامنظور کر دی گئی ہے۔"
                                    cursor.execute("UPDATE leave_requests SET status='Rejected', admin_remarks=? WHERE id=?", (final_remark, r['id']))
                                    conn.commit()
                                    st.error(tr("درخواست مسترد کر دی گئی۔", "Request Rejected."))
                                    import time
                                    time.sleep(1)
                                    st.rerun()
                    else:
                        st.success(tr("اس وقت کوئی نئی درخواست موجود نہیں۔", "No pending requests at the moment."))
                        
                with tab_history:
                    if not history_reqs.empty:
                        show_df = history_reqs[['date', 'reg_id', 'name', 'class', 'reason', 'status', 'admin_remarks']].copy()
                        if st.session_state.ui_lang == "اردو":
                            show_df.columns = ['تاریخ', 'رول نمبر', 'نام', 'کلاس', 'وجہ', 'سٹیٹس', 'انتظامیہ کا جواب']
                            show_df['سٹیٹس'] = show_df['سٹیٹس'].replace({'Approved': 'منظور شدہ ✅', 'Rejected': 'مسترد شدہ ❌'})
                        else:
                            show_df.columns = ['Date', 'Reg No', 'Name', 'Class', 'Reason', 'Status', 'Admin Remarks']
                            show_df['Status'] = show_df['Status'].replace({'Approved': 'Approved ✅', 'Rejected': 'Rejected ❌'})
                            
                        st.dataframe(show_df, use_container_width=True, hide_index=True)
                    else:
                        st.info(tr("کوئی پرانا ریکارڈ نہیں۔", "No history found."))
                        
        except Exception as e:
            st.error(f"Error loading requests: {e}")

# ================= 6. فیس، رسیدیں، سیلری =================
elif core_choice == "Fee & Salary":
    st.markdown(f"<h2 class='no-print'>💵 {tr('فیس چالان، رسیدیں اور سٹاف سیلری', 'Fee Challan, Receipts & Staff Salary')} - {tr(sub_choice, sub_choice)}</h2>", unsafe_allow_html=True)
    
    # 🟢 اپڈیٹڈ فنکشن: اب یہ ایکسٹرا چارجز (extra_charges_dict) کو بھی وصول کرے گا
    def get_single_challan_row(s_reg, s_name, s_fname, s_class_name, s_section, t_fee, arrears, advance, total_amt, inv_no, issue_dt, due_dt, g_month, g_year, logo_src, school_name, discount_amt, extra_charges_dict):
        instructions_text = "The last date for payment of the monthly fee and other dues will be the 10th of every month.<br>If the dues are paid after the 10th, a late fee of Rs. 10 per day will be charged.<br>Full payment of all outstanding dues is required to receive examination results, certificates, or any other necessary school documents.<br>In case of any genuine difficulty or special circumstances, parents are requested to contact the school administration in advance.<br>Please make sure to obtain a receipt when paying the fee and keep it safe for future reference."
        
        late_fee_amt = max(0, total_amt + 10)
        t_fee_disc = t_fee + discount_amt
        
        # 🟢 نئے شامل کیے گئے چارجز کا HTML بنانا
        extra_rows_html = ""
        if extra_charges_dict:
            for charge_name, charge_amt in extra_charges_dict.items():
                extra_rows_html += f"<tr><td style='border: 1px solid #ccc; padding: 5px;'>{charge_name}</td><td style='border: 1px solid #ccc; padding: 5px; text-align: right;'>{charge_amt} PKR</td></tr>"
        
        html_row = '<table style="width: 100%; table-layout: fixed; border-collapse: separate; border-spacing: 15px; page-break-after: always;"><tr>'
        
        logo_html = f'<img src="{logo_src}" style="height: 25px; float: left; margin-right: 8px; object-fit: contain;">' if logo_src else ''
        
        for copy_name in ["School", "Bank", "Parents"]:
            adv_row_html = f"<tr><td style='border: 1px solid #ccc; padding: 5px; color:#155724;'>Advance Adjusted</td><td style='border: 1px solid #ccc; padding: 5px; text-align: right; color:#155724;'>- {advance} PKR</td></tr>" if advance > 0 else ""
            disc_row_html = f"<tr><td style='border: 1px solid #ccc; padding: 5px; color:#c53030;'>Discount / Concession</td><td style='border: 1px solid #ccc; padding: 5px; text-align: right; color:#c53030;'>- {discount_amt} PKR</td></tr>" if discount_amt > 0 else ""
            
            html_row += f"""<td style="width: 33.33%; vertical-align: top; border: 1px solid #005b36; padding: 0; font-family: Arial, sans-serif; font-size: 11px;">
                <div style="padding: 10px;">
                    <div style="display: flex; align-items: center; border-bottom: 2px solid #d4af37; padding-bottom: 5px; margin-bottom: 5px;">
                        {logo_html}
                        <strong style="font-size: 14px; color: #005b36;">{school_name.upper()}</strong>
                    </div>
                    <div style="background-color: #005b36; color: white; padding: 5px; font-weight: bold; margin-bottom: 5px; display: flex; justify-content: space-between;">
                        <span>Fee Slip</span><span style="color: #d4af37;">Copy for {copy_name}</span>
                    </div>
                    <div style="margin-bottom: 5px; line-height: 1.4;">
                        <div><strong style="color: #005b36;">Student Name:</strong> {s_name}</div>
                        <div><strong style="color: #005b36;">Father / Guardian:</strong> {s_fname}</div>
                    </div>
                    <table style="width: 100%; border-collapse: collapse; margin-bottom: 5px; font-size: 11px;">
                        <tr><td style="border: 1px solid #ccc; padding: 4px;"><strong style="color: #005b36;">Issue Date:</strong></td><td style="border: 1px solid #ccc; padding: 4px;">{issue_dt}</td><td style="border: 1px solid #ccc; padding: 4px;"><strong style="color: #005b36;">Due Date:</strong></td><td style="border: 1px solid #ccc; padding: 4px;">{due_dt}</td></tr>
                        <tr><td style="border: 1px solid #ccc; padding: 4px;"><strong style="color: #005b36;">Challan No:</strong></td><td style="border: 1px solid #ccc; padding: 4px;">{inv_no}</td><td style="border: 1px solid #ccc; padding: 4px;"><strong style="color: #005b36;">Month:</strong></td><td style="border: 1px solid #ccc; padding: 4px;">{g_month}-{g_year}</td></tr>
                        <tr><td style="border: 1px solid #ccc; padding: 4px;"><strong style="color: #005b36;">Class:</strong></td><td style="border: 1px solid #ccc; padding: 4px;">{s_class_name}</td><td style="border: 1px solid #ccc; padding: 4px;"><strong style="color: #005b36;">Section:</strong></td><td style="border: 1px solid #ccc; padding: 4px;">{s_section}</td></tr>
                        <tr><td style="border: 1px solid #ccc; padding: 4px;"><strong style="color: #005b36;">Admission No:</strong></td><td style="border: 1px solid #ccc; padding: 4px;">{s_reg}</td><td style="border: 1px solid #ccc; padding: 4px;"><strong style="color: #005b36;">Fee Payable:</strong></td><td style="border: 1px solid #ccc; padding: 4px;">100%</td></tr>
                    </table>
                    <table style="width: 100%; border-collapse: collapse; font-size: 11px; margin-bottom: 5px;">
                        <tr style="background-color: #005b36; color: white;"><th style="padding: 5px; border: 1px solid #005b36; text-align: left;">Description</th><th style="padding: 5px; border: 1px solid #005b36; text-align: right;">Amount</th></tr>
                        <tr><td style="border: 1px solid #ccc; padding: 5px;">Tuition Fee</td><td style="border: 1px solid #ccc; padding: 5px; text-align: right;">{t_fee_disc} PKR</td></tr>
                        {extra_rows_html}
                        {disc_row_html}{adv_row_html}
                        <tr><td style="border: 1px solid #ccc; padding: 5px;">Arrears</td><td style="border: 1px solid #ccc; padding: 5px; text-align: right;">{arrears} PKR</td></tr>
                        <tr style="color: #005b36; font-weight: bold; background-color: #f2f7f4;"><td style="border: 1px solid #ccc; padding: 5px;">Amount Payable</td><td style="border: 1px solid #ccc; padding: 5px; text-align: right;">{total_amt} PKR</td></tr>
                        <tr><td style="border: 1px solid #ccc; padding: 5px; font-weight: bold;">Paid</td><td style="border: 1px solid #ccc; padding: 5px; text-align: right; font-weight: bold;">0 PKR</td></tr>
                        <tr><td style="border: 1px solid #ccc; padding: 5px;">Pending Amount</td><td style="border: 1px solid #ccc; padding: 5px; text-align: right;">{total_amt} PKR</td></tr>
                        <tr><td style="border: 1px solid #ccc; padding: 5px;">After Due Date</td><td style="border: 1px solid #ccc; padding: 5px; text-align: right;">{late_fee_amt} PKR</td></tr>
                    </table>
                    <table style="width: 100%; font-size: 11px; font-weight: bold; color: #005b36; margin-bottom: 5px; background-color: #f2f7f4;">
                        <tr><td style="padding: 8px;">Received Amount</td><td style="text-align:right; padding: 8px; border-bottom: 1px solid #ccc;"></td></tr>
                        <tr><td style="padding: 8px;">Balance Amount</td><td style="text-align:right; padding: 8px; border-bottom: 1px solid #ccc;"></td></tr>
                    </table>
                    <div style="font-size: 8px; color: #333; line-height: 1.3; margin-top: 5px;"><b>Instructions:</b><br>{instructions_text}</div>
                </div></td>"""
        html_row += '</tr></table>'
        return html_row

    if sub_choice == "Generate Fee Challans":
        c1, c2, c3 = st.columns(3)
        g_class = c1.selectbox(tr("کلاس", "Class"), ["All"] + classes_list)
        g_month = c2.selectbox(tr("مہینہ", "Month"), months_en)
        g_year = c3.text_input("Year", "2026")
        c4, c5 = st.columns(2)
        g_due = c4.date_input(tr("آخری تاریخ", "Due Date"), datetime.date.today() + datetime.timedelta(days=10))
        f_reg = c5.text_input(tr("کسی ایک طالب علم کے لیے رول نمبر (اختیاری)", "Enter Reg No for Single Student (Optional):"))
        
        st.write("---")
        
        # 🟢 نیا فیچر: ڈراپ ڈاؤن چارجز سلیکشن
        st.markdown(f"#### &#128176; {tr('اضافی چارجز شامل کریں (اختیاری)', 'Add Extra Charges (Optional)')}", unsafe_allow_html=True)
        charge_options_ur = ["ٹرانسپورٹ چارجز", "چھٹیوں کا جرمانہ", "لیٹ فیس جرمانہ", "سالانہ فنڈ", "ماہانہ فنڈ", "امتحانی فیس", "کتابیں اور سٹیشنری", "آئی ڈی کارڈ فیس", "سپورٹس فنڈ", "دیگر (خود لکھیں)"]
        charge_options_en = ["Transport Charges", "Absence Fine", "Late Fine", "Annual Fund", "Monthly Fund", "Exam Fee", "Books & Stationery", "ID Card Fee", "Sports Fund", "Other (Custom)"]
        display_opts = charge_options_en if st.session_state.ui_lang == "English" else charge_options_ur
        
        selected_charges = st.multiselect(tr("مزید چارجز منتخب کریں", "Select Extra Charges"), display_opts)
        
        extra_charges_dict = {}
        if selected_charges:
            st.info(tr("منتخب کردہ چارجز کی رقم درج کریں:", "Enter amounts for the selected charges:"))
            cols = st.columns(3)
            col_idx = 0
            
            for charge in selected_charges:
                if charge in ["Other (Custom)", "دیگر (خود لکھیں)"]:
                    # پہلا خانہ: یہاں آپ اپنی مرضی کا نام لکھیں گے (جو چالان پر چھپے گا)
                    cust_name = cols[col_idx % 3].text_input(tr("یہاں چارج کا نام خود لکھیں", "Write Charge Name Here"), placeholder="مثلاً: ٹرپ فیس، پارٹی فنڈ وغیرہ")
                    # دوسرا خانہ: یہاں صرف اس چارج کی رقم لکھی جائے گی
                    cust_amt = cols[col_idx % 3].number_input(tr("اس کی رقم (Rs)", "Charge Amount (Rs)"), min_value=0, value=0, step=50)
                    
                    if cust_name.strip() and cust_amt > 0:
                        extra_charges_dict[cust_name.strip()] = cust_amt
                else:
                    amt = cols[col_idx % 3].number_input(f"{charge}", min_value=0, value=0, step=50)
                    if amt > 0:
                        extra_charges_dict[charge] = amt
                col_idx += 1
                
        st.write("---")
        
        if st.button(tr("چالان جنریٹ کریں (Generate)", "Generate Fee Challans"), type="primary"):
            query = "SELECT * FROM students WHERE 1=1"
            if f_reg: query += f" AND reg_id='{f_reg}'"
            elif g_class != "All": query += f" AND class='{g_class}'"
            students_df = pd.read_sql(query, conn)
            
            if not students_df.empty:
                full_html = ""
                extra_total = sum(extra_charges_dict.values()) # 🟢 اضافی چارجز کا ٹوٹل
                
                for i, row in students_df.iterrows():
                    s_reg, s_class = row['reg_id'], row['class']
                    s_name = get_disp_val(row['name'], row.get('name_en'))
                    s_fname = get_disp_val(row['fname'], row.get('fname_en'))
                    s_sec = row.get('section', 'A')
                    t_fee, arrears = safe_int(row['monthly_fee']), safe_int(row['arrears'])
                    advance, discount_amt = safe_int(row.get('advance_fee', 0)), safe_int(row.get('discount', 0))
                    
                    # 🟢 ٹوٹل فیس میں ایکسٹرا چارجز شامل کیے گئے
                    total_amt = max(0, t_fee + extra_total + arrears - advance)
                    inv_no = f"{g_year}{g_month}{s_reg}"
                    issue_dt = today_date
                    due_dt = g_due.strftime("%d %b %Y")
                    fee_month_str = f"{g_month}-{g_year}"
                    
                    cursor.execute("SELECT status FROM fees WHERE invoice_no=?", (inv_no,))
                    existing_status = cursor.fetchone()
                    
                    cursor.execute("SELECT * FROM fees WHERE reg_id=? AND month=?", (s_reg, fee_month_str))
                    if cursor.fetchone():
                        st.error(f"⚠️ رول نمبر {s_reg} کا {fee_month_str} کے مہینے کا چالان پہلے ہی بن چکا ہے!")
                    else:
                        if not existing_status: 
                            cursor.execute("INSERT INTO fees (date, reg_id, month, tuition, arrears_col, total, status, due_date, invoice_no) VALUES (?, ?, ?, ?, ?, ?, 'Unpaid', ?, ?)", (issue_dt, s_reg, fee_month_str, t_fee, arrears, total_amt, str(g_due), inv_no))
                        elif existing_status[0] == 'Unpaid': 
                            cursor.execute("UPDATE fees SET tuition=?, arrears_col=?, total=?, due_date=?, date=? WHERE invoice_no=?", (t_fee, arrears, total_amt, str(g_due), issue_dt, inv_no))
                        conn.commit()
                        # 🟢 ایکسٹرا چارجز ڈکشنری فنکشن میں بھیجی گئی
                        full_html += get_single_challan_row(s_reg, s_name, s_fname, s_class, s_sec, t_fee, arrears, advance, total_amt, inv_no, issue_dt, due_dt, g_month, g_year, logo_src_b64, school_name, discount_amt, extra_charges_dict)
                
                if full_html != "":
                    print_button_js(full_html, tr("چالان پرنٹ کریں (Print Challans Now)", "Print Challans Now"), landscape=True)
                    st.success(tr(f"✅ {len(students_df)} چالان تیار ہیں!", f"✅ {len(students_df)} Challans Generated! Click the Blue Print button above."))
            else: st.warning(tr("طالب علم نہیں ملا۔", "No students found."))

    elif sub_choice == "Collect Fees":
        tab_collect, tab_ledger = st.tabs(["💰 فیس وصولی (Fee Collection)", "📖 سٹوڈنٹ لیجر کھاتا (Student Ledger)"])
        
        with tab_collect:
            f_col1, f_col2, f_col3, f_col4 = st.columns(4)
            f_class = f_col1.selectbox("Class", ["All"] + classes_list, key="col_fee_cls")
            f_status = f_col2.selectbox("Status", ["Unpaid", "Paid", "All"], key="col_fee_sts")
            f_search = f_col3.text_input("Search Student / Reg No", key="col_fee_srch")
            f_month = f_col4.selectbox("Billing Month", ["All"] + months_en, key="col_fee_mth")

            q = "SELECT f.invoice_no, s.reg_id, s.name, s.fname, s.class, s.section, f.month, f.total, f.status, f.date FROM fees f JOIN students s ON f.reg_id = s.reg_id WHERE 1=1"
            if f_class != "All": q += f" AND s.class='{f_class}'"
            if f_status != "All": q += f" AND f.status='{f_status}'"
            if f_search: q += f" AND (s.name LIKE '%{f_search}%' OR s.reg_id LIKE '%{f_search}%')"
            if f_month != "All": q += f" AND f.month LIKE '{f_month}%'"
            q += " ORDER BY f.rowid DESC"
            inv_df = pd.read_sql(q, conn)
            
            c_mode1, c_mode2 = st.columns([1.2, 1])
            with c_mode1:
                st.markdown(f"#### {tr('تھوک ادائیگی (Bulk Payment)', 'Bulk Payment')}")
                if not inv_df.empty:
                    disp_df = inv_df.copy()
                    disp_df.insert(0, 'Select', False)
                    disp_df['Student'] = disp_df['name'] + " (Reg: " + disp_df['reg_id'].astype(str) + ")"
                    disp_df['Class/Sec'] = disp_df['class'] + " (" + disp_df['section'].fillna('') + ")"
                    
                    if f_class != "All":
                        show_df = disp_df[['Select', 'invoice_no', 'Student', 'month', 'total', 'status']]
                        show_df.columns = ['Select', 'Invoice No', 'Student', 'Billing Month', 'Amount', 'Status']
                        disabled_cols = ['Invoice No', 'Student', 'Billing Month', 'Amount', 'Status']
                    else:
                        show_df = disp_df[['Select', 'invoice_no', 'Student', 'Class/Sec', 'month', 'total', 'status']]
                        show_df.columns = ['Select', 'Invoice No', 'Student', 'Class/Sec', 'Billing Month', 'Amount', 'Status']
                        disabled_cols = ['Invoice No', 'Student', 'Class/Sec', 'Billing Month', 'Amount', 'Status']
                        
                    edited_df = st.data_editor(show_df, hide_index=True, column_config={"Select": st.column_config.CheckboxColumn("Select", default=False)}, disabled=disabled_cols, use_container_width=True, key="bulk_fee_editor")
                    if st.button("✅ Mark Selected As Paid", type="primary"):
                        selected_rows = edited_df[edited_df['Select'] == True]
                        if not selected_rows.empty:
                            for _, row in selected_rows.iterrows():
                                inv, amt, sts = row['Invoice No'], row['Amount'], row['Status']
                                if sts == 'Unpaid':
                                    reg = inv_df[inv_df['invoice_no'] == inv]['reg_id'].iloc[0]
                                    cursor.execute("UPDATE fees SET status='Paid' WHERE invoice_no=?", (inv,))
                                    v_num = pd.read_sql("SELECT COUNT(*) FROM accounts", conn).iloc[0, 0] + 1001
                                    cursor.execute("INSERT INTO accounts (date, type, description, amount, head_name, voucher_no) VALUES (?, 'آمدنی', ?, ?, 'Fee Collection', ?)", (today_date, f"Fee Inv: {inv}", amt, f"V-{v_num}"))
                                    cursor.execute(f"UPDATE students SET arrears=0, advance_fee=0 WHERE reg_id='{reg}'")
                            conn.commit()
                            st.success("Selected invoices have been marked as PAID successfully!")
                            st.rerun()
                else: st.info("No invoices found matching criteria.")
                    
            with c_mode2:
                st.markdown(f"#### {tr('سنگل فیس وصولی اور آٹو بقایا جات', 'Custom Payment & Auto Arrears')}")
                if f_search and not inv_df.empty:
                    selected_inv_row = inv_df.iloc[0]
                    s_reg, s_inv, s_amt_total = selected_inv_row['reg_id'], selected_inv_row['invoice_no'], selected_inv_row['total']
                    stu_info = pd.read_sql(f"SELECT * FROM students WHERE reg_id='{s_reg}'", conn).iloc[0]
                    
                    st.info(f"👤 **طالب علم:** {stu_info['name']} | **کلاس:** {stu_info['class']}\n\n🧾 **انوائس:** {s_inv} | **کل واجبات:** Rs {s_amt_total}")
                    
                    with st.form("custom_fee_form"):
                        received_amt = st.number_input(tr("وصول شدہ رقم لکھیں (Received Amount)", "Enter Received Amount"), min_value=0, value=safe_int(s_amt_total))
                        
                        if received_amt < s_amt_total:
                            st.warning(f"⚠️ طالب علم نے {s_amt_total - received_amt} روپے کم دیئے ہیں۔ یہ رقم خود بخود اگلے مہینے کے بقایا جات (Arrears) میں شامل ہو جائے گی۔")
                        elif received_amt > s_amt_total:
                            st.success(f"💡 طالب علم نے {received_amt - s_amt_total} روپے زیادہ دیئے ہیں۔ یہ رقم خود بخود ایڈوانس فیس میں شامل ہو جائے گی۔")
                            
                        if st.form_submit_button(tr("فیس وصول کریں (Collect Fee)", "Collect Custom Fee"), type="primary"):
                            if received_amt < s_amt_total: new_arrears, new_advance = s_amt_total - received_amt, 0
                            else: new_arrears, new_advance = 0, received_amt - s_amt_total
                            
                            cursor.execute("UPDATE students SET arrears=?, advance_fee=? WHERE reg_id=?", (new_arrears, new_advance, s_reg))
                            cursor.execute("UPDATE fees SET status='Paid', total=? WHERE invoice_no=?", (received_amt, s_inv))
                            v_num = pd.read_sql("SELECT COUNT(*) FROM accounts", conn).iloc[0, 0] + 1001
                            cursor.execute("INSERT INTO accounts (date, type, description, amount, head_name, voucher_no) VALUES (?, 'آمدنی', ?, ?, 'Fee Collection', ?)", (today_date, f"Custom Fee: {s_inv}", received_amt, f"V-{v_num}"))
                            conn.commit()
                            st.success(tr("فیس کامیابی سے جمع ہو گئی اور لیجر اپڈیٹ ہو گیا!", "Fee collected and ledger updated!"))
                            st.rerun()
                else:
                    st.write("فیس وصول کرنے کے لیے پہلے ساتھ والے سرچ باکس میں طالب علم کا رول نمبر لکھیں۔")
                    
        with tab_ledger:
            st.markdown("### 📖 طالب علم کا مالیاتی کھاتا (Student Ledger)")
            l_col1, l_col2 = st.columns([1, 2])
            ledger_class = l_col1.selectbox("کلاس منتخب کریں", classes_list, key="ledg_cls")
            class_students_df = pd.read_sql(f"SELECT reg_id, name, fname FROM students WHERE class='{ledger_class}'", conn)
            
            if not class_students_df.empty:
                stu_names_list = [f"{r['name']} (S/O {r['fname']}) - Reg: {r['reg_id']}" for _, r in class_students_df.iterrows()]
                sel_stu_ledger = l_col2.selectbox("طالب علم کا انتخاب کریں", stu_names_list)
                ledg_reg = sel_stu_ledger.split("Reg: ")[1].strip()
                
                stu_ledg_info = pd.read_sql(f"SELECT arrears, advance_fee FROM students WHERE reg_id='{ledg_reg}'", conn).iloc[0]
                fee_history = pd.read_sql(f"SELECT invoice_no, month, date, status, total FROM fees WHERE reg_id='{ledg_reg}' ORDER BY rowid DESC", conn)
                
                total_billed = pd.read_sql(f"SELECT SUM(total) FROM fees WHERE reg_id='{ledg_reg}'", conn).iloc[0,0] or 0
                total_paid = pd.read_sql(f"SELECT SUM(total) FROM fees WHERE reg_id='{ledg_reg}' AND status='Paid'", conn).iloc[0,0] or 0
                
                m1, m2, m3, m4 = st.columns(4)
                m1.metric("مجموعی واجبات (Total Billed)", f"Rs {total_billed}")
                m2.metric("مجموعی ادائیگی (Total Paid)", f"Rs {total_paid}", delta=f"{total_paid - total_billed} Balance")
                m3.metric("موجودہ بقایا جات (Arrears)", f"Rs {stu_ledg_info['arrears']}")
                m4.metric("ایڈوانس فیس (Advance)", f"Rs {stu_ledg_info.get('advance_fee', 0)}")
                
                st.write("---")
                st.markdown("#### 📜 پچھلے تمام چالان کی تفصیل (Challan History)")
                if not fee_history.empty:
                    fee_history.columns = ['Invoice No', 'Billing Month', 'Issue Date', 'Status', 'Amount']
                    st.dataframe(fee_history, use_container_width=True, hide_index=True)
                else:
                    st.info("اس طالب علم کا کوئی پرانا ریکارڈ موجود نہیں۔")
            else:
                st.warning("اس کلاس میں کوئی طالبعلم موجود نہیں۔")

    elif sub_choice == "Arrears & Advance":
        st.markdown("### ⚠️ سکول کے تمام بقایا جات اور ایڈوانس (All Defaulters & Advance Holders)")
        st.write("یہاں آپ پورے سکول کے ان طالب علموں کی لسٹ دیکھ سکتے ہیں جن کے ذمے پچھلے مہینوں کے بقایا جات ہیں یا جنہوں نے ایڈوانس فیس دی ہوئی ہے۔")
        
        defaulters_df = pd.read_sql("SELECT reg_id as 'Reg No', name as 'Student Name', class as 'Class', arrears as 'Arrears (Rs)', advance_fee as 'Advance (Rs)' FROM students WHERE arrears > 0 OR advance_fee > 0 ORDER BY class", conn)
        
        if not defaulters_df.empty:
            st.dataframe(defaulters_df, use_container_width=True, hide_index=True)
            
            st.write("---")
            st.write("اگر کسی ریکارڈ میں دستی طور پر تبدیلی کرنی ہو تو نیچے رول نمبر لکھیں:")
            c_ea1, c_ea2, c_ea3 = st.columns([1, 1, 2])
            edit_r = c_ea1.text_input("رول نمبر (Reg No):")
            if edit_r:
                stu2 = pd.read_sql(f"SELECT arrears, advance_fee FROM students WHERE reg_id='{edit_r}'", conn)
                if not stu2.empty:
                    new_arr = c_ea2.number_input(tr("نئے بقایا جات", "New Arrears"), value=safe_int(stu2.iloc[0]['arrears']))
                    new_adv = c_ea3.number_input(tr("نئی ایڈوانس فیس", "New Advance Fee"), value=safe_int(stu2.iloc[0].get('advance_fee', 0)))
                    if st.button("ریکارڈ اپڈیٹ کریں", type="primary"):
                        cursor.execute(f"UPDATE students SET arrears={new_arr}, advance_fee={new_adv} WHERE reg_id='{edit_r}'")
                        conn.commit()
                        st.success("اپڈیٹ ہو گیا!")
                        st.rerun()
                else:
                    st.error("طالب علم نہیں ملا۔")
        else:
            st.success("الحمدللہ! کسی طالب علم کے ذمے کوئی بقایا جات نہیں ہیں۔")

    elif sub_choice == "Discount Mgt":
        c_d1, c_d2, c_d3, c_d4 = st.columns(4)
        disc_type = c_d1.selectbox(tr("ڈسکاؤنٹ کی قسم *", "Give discount to *"), ["One student", "Sibling", "Staff Child", "Other"])
        disc_class = c_d2.selectbox(tr("کلاس *", "Class *"), classes_list, key='disc_cls')
        disc_sec = c_d3.selectbox(tr("سیکشن", "Section"), ["All", "A", "B", "C", "D", "Model"], key='disc_sec')
        q_disc = f"SELECT * FROM students WHERE class='{disc_class}'"
        if disc_sec != "All": q_disc += f" AND section='{disc_sec}'"
        stu_df_disc = pd.read_sql(q_disc, conn)
        
        if not stu_df_disc.empty:
            stu_names = [f"{get_disp_val(r['name'], r.get('name_en'))} (Reg: {r['reg_id']})" for _, r in stu_df_disc.iterrows()]
            sel_stu = c_d4.selectbox(tr("طالب علم کا نام *", "Student name *"), stu_names)
            reg_no = sel_stu.split("Reg: ")[1].replace(")", "")
            sel_stu_row = stu_df_disc[stu_df_disc['reg_id'] == reg_no].iloc[0]
            curr_fee = safe_int(sel_stu_row['monthly_fee'])
            curr_disc = safe_int(sel_stu_row.get('discount', 0))
            base_fee = curr_fee + curr_disc
            
            c_d5, c_d6, c_d7 = st.columns(3)
            c_d5.text_input(tr("بنیادی ٹیوشن فیس (Base Tuition)", "Tuition fee (Base)"), value=f"{base_fee} PKR", disabled=True)
            concession = c_d6.number_input(tr("رعایتی فیس لکھیں (Concession/Reduced Tuition)", "Concession (reduced Tuition)"), min_value=0, max_value=base_fee, value=curr_fee)
            calc_disc = base_fee - concession
            c_d7.text_input(tr("ڈسکاؤنٹ کی رقم (آٹو)", "Discount amount (Auto)"), value=f"{calc_disc} PKR", disabled=True)
            
            note = st.text_input(tr("نوٹ (اختیاری)", "Note (optional)"), placeholder=tr("مثال: بہن بھائی کا ڈسکاؤنٹ", "e.g. Staff child discount"))
            update_unpaid = st.checkbox(tr("پہلے سے بنے ہوئے Unpaid چالان بھی اپڈیٹ کریں", "Also update existing unpaid challans"), value=True)
            
            if st.button(tr("محفوظ کریں", "Save Discount"), type="primary"):
                cursor.execute(f"UPDATE students SET monthly_fee={concession}, discount={calc_disc}, discount_note='{note}' WHERE reg_id='{reg_no}'")
                if update_unpaid: cursor.execute(f"UPDATE fees SET tuition={concession}, total=(total - {calc_disc}) WHERE reg_id='{reg_no}' AND status='Unpaid'")
                conn.commit()
                st.success(tr("ڈسکاؤنٹ کامیابی سے لاگو ہو گیا!", "Discount applied successfully!"))
        else: st.warning(tr("اس کلاس میں کوئی طالب علم موجود نہیں۔", "No student found in this class."))

    elif sub_choice == "Pay Salary":
        tab_sal, tab_stf_ledg = st.tabs(["💳 تنخواہ اور ایڈوانس (Pay Salary / Advance)", "📖 سٹاف لیجر (Staff Ledger)"])
        
        with tab_sal:
            c_slm1, c_slm2 = st.columns([1, 2])
            sal_month = c_slm1.selectbox("تنخواہ کا مہینہ (Month)", months_en, key="sm")
            
            staff_list_df = pd.read_sql("SELECT * FROM staff", conn)
            if not staff_list_df.empty:
                paid_staff_ids = pd.read_sql(f"SELECT staff_id FROM salary_records WHERE month='{sal_month}' AND remarks='Salary'", conn)['staff_id'].tolist()
                unpaid_staff = staff_list_df[~staff_list_df['staff_id'].isin(paid_staff_ids)]
                
                col_s1, col_s2 = st.columns(2)
                
                with col_s1:
                    st.markdown("### 💰 ماہانہ تنخواہ کی ادائیگی")
                    if not unpaid_staff.empty:
                        with st.form("pay_staff_salary"):
                            p_sid_name = st.selectbox("سٹاف ممبر منتخب کریں:", unpaid_staff['name'].tolist())
                            m_row = unpaid_staff[unpaid_staff['name'] == p_sid_name].iloc[0]
                            exact_id = m_row['staff_id']
                            stf_base_salary = safe_int(m_row['salary'])
                            stf_advance = safe_int(m_row.get('advance_salary', 0))
                            
                            month_idx = months_en.index(sal_month) + 1
                            month_str_num = f"{month_idx:02d}"
                            current_year = datetime.date.today().year
                            
                            absent_count = pd.read_sql(f"SELECT COUNT(*) FROM attendance WHERE type='سٹاف' AND person_id='{exact_id}' AND status='Absent' AND date LIKE '{current_year}-{month_str_num}-%'", conn).iloc[0,0]
                            
                            per_day_salary = stf_base_salary / 30
                            absent_deduction = int(per_day_salary * absent_count)
                            
                            net_payable = max(0, stf_base_salary - stf_advance - absent_deduction)
                            
                            st.info(f"**بنیادی تنخواہ:** Rs {stf_base_salary} \n\n**غیر حاضریاں (Absents):** {absent_count} دن (- Rs {absent_deduction}) \n\n**پچھلا ایڈوانس:** Rs {stf_advance} \n\n**کل قابلِ ادائیگی (Net Payable): Rs {net_payable}**")
                            
                            if st.form_submit_button("✅ اس مہینے کی تنخواہ کلیئر کریں", type="primary"):
                                cursor.execute("SELECT * FROM salary_records WHERE staff_id=? AND month=? AND remarks='Salary'", (exact_id, sal_month))
                                if cursor.fetchone():
                                    st.error(f"⚠️ اس سٹاف ممبر کی {sal_month} کی تنخواہ پہلے ہی ادا ہو چکی ہے!")
                                else:
                                    v_num = pd.read_sql("SELECT COUNT(*) FROM accounts", conn).iloc[0, 0] + 1001
                                    cursor.execute("INSERT INTO salary_records VALUES (?, ?, ?, ?, ?)", (today_date, exact_id, sal_month, net_payable, "Salary"))
                                    cursor.execute("INSERT INTO accounts (date, type, description, amount, head_name, voucher_no) VALUES (?, 'خرچ', ?, ?, 'Staff Salary', ?)", (today_date, f"Salary - {p_sid_name} ({sal_month})", net_payable, f"V-{v_num}"))
                                    cursor.execute(f"UPDATE staff SET advance_salary=0 WHERE staff_id='{exact_id}'")
                                    conn.commit()
                                    st.success(f"تنخواہ کامیابی سے ادا کر دی گئی! (غیر حاضری کی کٹوتی: Rs {absent_deduction})")
                                    st.rerun()
                        
                with col_s2:
                    st.markdown("### 💵 سٹاف کو ایڈوانس دیں")
                    with st.form("give_advance"):
                        adv_sid_name = st.selectbox("سٹاف ممبر منتخب کریں:", staff_list_df['name'].tolist(), key="adv_stf")
                        adv_amt = st.number_input("ایڈوانس رقم (Amount)", min_value=1, value=1000)
                        
                        if st.form_submit_button("ایڈوانس ادا کریں"):
                            adv_id = staff_list_df[staff_list_df['name'] == adv_sid_name].iloc[0]['staff_id']
                            curr_adv = safe_int(staff_list_df[staff_list_df['name'] == adv_sid_name].iloc[0].get('advance_salary', 0))
                            v_num = pd.read_sql("SELECT COUNT(*) FROM accounts", conn).iloc[0, 0] + 1001
                            
                            cursor.execute("INSERT INTO salary_records VALUES (?, ?, ?, ?, ?)", (today_date, adv_id, sal_month, adv_amt, "Advance"))
                            cursor.execute("INSERT INTO accounts (date, type, description, amount, head_name, voucher_no) VALUES (?, 'خرچ', ?, ?, 'Staff Salary', ?)", (today_date, f"Advance - {adv_sid_name}", adv_amt, f"V-{v_num}"))
                            cursor.execute(f"UPDATE staff SET advance_salary={curr_adv + adv_amt} WHERE staff_id='{adv_id}'")
                            conn.commit()
                            st.success(f"{adv_amt} روپے ایڈوانس کے طور پر لیجر میں شامل ہو گئے۔")
                            st.rerun()
            else:
                st.warning("ڈیٹا بیس میں کوئی سٹاف موجود نہیں۔")
                
        with tab_stf_ledg:
            st.markdown("### 📖 سٹاف ممبر کا مالیاتی کھاتا (Staff Ledger)")
            if not staff_list_df.empty:
                s_ledg_name = st.selectbox("سٹاف ممبر کا انتخاب کریں", staff_list_df['name'].tolist(), key="ledg_stf")
                s_ledg_id = staff_list_df[staff_list_df['name'] == s_ledg_name].iloc[0]['staff_id']
                s_ledg_adv = safe_int(staff_list_df[staff_list_df['name'] == s_ledg_name].iloc[0].get('advance_salary', 0))
                
                st.metric("موجودہ کٹا ہوا ایڈوانس (Pending Advance Deduction)", f"Rs {s_ledg_adv}")
                
                st.write("---")
                st.markdown("#### 📜 تنخواہ اور ایڈوانس کی ہسٹری")
                stf_history = pd.read_sql(f"SELECT date, month, remarks, amount FROM salary_records WHERE staff_id='{s_ledg_id}' ORDER BY rowid DESC", conn)
                
                if not stf_history.empty:
                    stf_history.columns = ['Date', 'Billing Month', 'Transaction Type', 'Amount (Rs)']
                    st.dataframe(stf_history, use_container_width=True, hide_index=True)
                else:
                    st.info("اس سٹاف ممبر کی کوئی پرانی ہسٹری موجود نہیں۔")

    elif sub_choice == "Salary Slips":
        c_sl1, c_sl2 = st.columns(2)
        slip_month_sel = c_sl1.selectbox(tr("مہینہ", "Month"), months_en, key="slip_month_sel_bulk")
        slip_year_sel = c_sl2.text_input("Year", "2026", key="slip_year")
        
        def get_single_salary_slip_html_local(slip_no, issue_date, emp_name, designation, month_year, amount, advance_deduct, net_payable, status, logo_src):
            status_html = f'<span style="background-color: #fce4e4; color: #c53030; padding: 3px 8px; border-radius: 12px; font-weight: bold; font-size: 10px;">{status}</span>' if status.upper() == 'UNPAID' else f'<span style="background-color: #e6ffed; color: #22863a; padding: 3px 8px; border-radius: 12px; font-weight: bold; font-size: 10px;">{status}</span>'
            adv_deduct_html = ""
            if advance_deduct > 0:
                adv_deduct_html = f"<tr><td style='border: 1px solid #ccc; padding: 8px; color: #155724; font-weight:bold;'>Advance Deduction</td><td style='border: 1px solid #ccc; padding: 8px; text-align: right; font-weight: bold; color: #155724;'>- {advance_deduct} PKR</td></tr>"
            
            logo_html = f'<img src="{logo_src}" style="height: 35px; vertical-align: middle; margin-right: 10px; border-radius: 4px;">' if logo_src else ''
            
            html_row = '<table style="width: 100%; table-layout: fixed; border-collapse: separate; border-spacing: 20px; page-break-after: always;"><tr>'
            for copy_name in ["SCHOOL", "TEACHER"]:
                html_row += f"""<td style="width: 50%; vertical-align: top; border: 1px solid #005b36; padding: 0; font-family: Arial, sans-serif;">
                    <div style="background-color: #005b36; color: white; text-align: center; padding: 10px; font-weight: bold; font-size: 12px; letter-spacing: 1px;">COPY FOR {copy_name}</div>
                    <div style="padding: 20px;">
                        <div style="text-align: center; margin-bottom: 20px;">
                            <h2 style="margin: 0; color: #005b36; font-size: 18px; display:flex; justify-content:center; align-items:center;">{logo_html}{school_name.upper()}</h2>
                            <p style="margin: 4px 0; color: #666; font-size: 11px;">{school_address}</p>
                            <h3 style="margin: 15px 0 5px 0; font-size: 15px; letter-spacing: 1px; color: #000;">SALARY SLIP</h3>
                            <p style="margin: 0; font-size: 12px; color: #555;">{month_year}</p>
                        </div>
                        <table style="width: 100%; border-collapse: collapse; font-size: 11px; margin-bottom: 20px;">
                            <tr><td style="border: 1px solid #ccc; padding: 8px; font-weight: bold; width: 25%; color: #333;">Slip No.</td><td style="border: 1px solid #ccc; padding: 8px; width: 25%; color: #555;">{slip_no}</td>
                            <td style="border: 1px solid #ccc; padding: 8px; font-weight: bold; width: 25%; color: #333;">Date</td><td style="border: 1px solid #ccc; padding: 8px; width: 25%; color: #555;">{issue_date}</td></tr>
                            <tr><td style="border: 1px solid #ccc; padding: 8px; font-weight: bold; color: #333;">Employee Name</td><td style="border: 1px solid #ccc; padding: 8px; color: #000; font-weight: bold;">{emp_name}</td>
                            <td style="border: 1px solid #ccc; padding: 8px; font-weight: bold; color: #333;">Designation</td><td style="border: 1px solid #ccc; padding: 8px; color: #555;">{designation}</td></tr>
                            <tr><td style="border: 1px solid #ccc; padding: 8px; font-weight: bold; color: #333;">Salary Period</td><td style="border: 1px solid #ccc; padding: 8px; color: #555;">{month_year}</td>
                            <td style="border: 1px solid #ccc; padding: 8px; font-weight: bold; color: #333;">Status</td><td style="border: 1px solid #ccc; padding: 8px; text-align: center;">{status_html}</td></tr>
                        </table>
                        <table style="width: 100%; border-collapse: collapse; font-size: 11px; margin-bottom: 20px;">
                            <tr style="background-color: #f8f9fa;"><td style="border: 1px solid #ccc; padding: 8px; font-weight: bold; color: #000;">DESCRIPTION</td><td style="border: 1px solid #ccc; padding: 8px; font-weight: bold; text-align: right; color: #000;">AMOUNT (PKR)</td></tr>
                            <tr><td style="border: 1px solid #ccc; padding: 8px; color: #555;">Monthly Salary - {month_year}</td><td style="border: 1px solid #ccc; padding: 8px; text-align: right; font-weight: bold; color: #000;">{amount} PKR</td></tr>
                            {adv_deduct_html}
                        </table>
                        <div style="border: 2px solid #005b36; padding: 12px; margin-bottom: 40px; background-color: #f2f7f4;">
                            <div style="font-size: 10px; color: #666; margin-bottom: 4px; text-transform: uppercase;">Net Payable</div>
                            <div style="font-size: 20px; font-weight: bold; color: #005b36;">{net_payable} PKR</div>
                        </div>
                        <table style="width: 100%; font-size: 10px; color: #333;">
                            <tr><td style="border-top: 1px solid #000; width: 40%; padding-top: 5px;">Employee Signature</td><td style="width: 20%;"></td><td style="border-top: 1px solid #000; width: 40%; padding-top: 5px; text-align: right;">Authorized Signatory</td></tr>
                        </table>
                    </div></td>"""
            html_row += "</tr></table>"
            return html_row

        if st.button(tr("پوری سٹاف کی سلپس جنریٹ کریں", "Generate All Staff Slips")):
            all_staff = pd.read_sql("SELECT * FROM staff", conn)
            if not all_staff.empty:
                full_html = ""
                for idx, r in all_staff.iterrows():
                    emp_name = get_disp_val(r['name'], r.get('name_en'))
                    emp_fname = get_disp_val(r['fname'], r.get('fname_en'))
                    g_val = str(r.get('gender', 'Male'))
                    rel_type = str(r.get('g_type', 'Father'))
                    rel_label = get_relation_card_label(g_val, rel_type)
                    
                    full_emp_name = f"{emp_name} ({rel_label} {emp_fname})"
                    
                    designation = get_desig_disp(r['designation'])
                    staff_id = r['staff_id']
                    base_salary = safe_int(r['salary'])
                    stf_advance = safe_int(r.get('advance_salary', 0))
                    
                    month_year = f"{slip_month_sel} {slip_year_sel}"
                    slip_no = f"SL-{slip_year_sel}{staff_id}"
                    
                    paid_record = pd.read_sql(f"SELECT * FROM salary_records WHERE staff_id='{staff_id}' AND month='{slip_month_sel}' AND remarks='Salary'", conn)
                    status = "PAID" if not paid_record.empty else "UNPAID"
                    net_payable = max(0, base_salary - stf_advance) if status == "UNPAID" else safe_int(paid_record.iloc[0]['amount'])
                    
                    full_html += get_single_salary_slip_html_local(slip_no, datetime.datetime.strptime(today_date, "%Y-%m-%d").strftime("%d %b %Y"), full_emp_name, designation, month_year, base_salary, stf_advance if status == "UNPAID" else 0, net_payable, status, logo_src_b64)
                
                print_button_js(full_html, tr("تنخواہ سلپس پرنٹ کریں", "Print Salary Slips Now"), landscape=True)
                st.success(f"✅ {len(all_staff)} Salary Slips Generated! Click the Blue Print button above.")
            else:
                st.warning("No staff found.")

        st.write("---")
        st.markdown(f"#### 📄 {tr('مکمل سٹاف سیلری سٹیٹمنٹ', 'Complete Staff Salary Statement')}")
        if st.button(tr("سٹیٹمنٹ پرنٹ کریں (دستخط کے لیے)", "Print Full Salary Statement (For Signatures)"), type="secondary"):
            all_staff = pd.read_sql("SELECT * FROM staff", conn)
            if not all_staff.empty:
                month_year = f"{slip_month_sel} {slip_year_sel}"
                t = {"align": "left", "dir": "ltr"} if st.session_state.ui_lang == "English" else {"align": "right", "dir": "rtl"}
                
                stmt_html = f"""
                <div style="font-family: Arial, sans-serif; padding: 20px; width: 100%; box-sizing: border-box;" dir="{t['dir']}">
                    <div style="text-align: center; margin-bottom: 20px; border-bottom: 3px solid #005b36; padding-bottom: 10px;">
                        {f'<img src="{logo_src_b64}" style="height: 60px; vertical-align: middle; margin-right: 15px;">' if logo_src_b64 else ''}
                        <div style="display: inline-block; vertical-align: middle;">
                            <h1 style="margin: 0; color: #005b36; font-size: 24px;">{school_name.upper()}</h1>
                            <p style="margin: 5px 0; color: #555; font-size: 14px;">{school_address}</p>
                        </div>
                        <h2 style="margin: 15px 0 0 0; color: #d4af37; font-size: 20px; text-transform: uppercase;">STAFF SALARY STATEMENT - {month_year}</h2>
                    </div>
                    <table style="width: 100%; border-collapse: collapse; font-size: 12px; margin-bottom: 30px;">
                        <thead>
                            <tr style="background-color: #005b36; color: white;">
                                <th style="border: 1px solid #ccc; padding: 10px; text-align: center;">Sr.</th>
                                <th style="border: 1px solid #ccc; padding: 10px; text-align: {t['align']};">Staff ID</th>
                                <th style="border: 1px solid #ccc; padding: 10px; text-align: {t['align']};">Employee Name</th>
                                <th style="border: 1px solid #ccc; padding: 10px; text-align: {t['align']};">Designation</th>
                                <th style="border: 1px solid #ccc; padding: 10px; text-align: center;">Base Salary</th>
                                <th style="border: 1px solid #ccc; padding: 10px; text-align: center;">Advance Deduct</th>
                                <th style="border: 1px solid #ccc; padding: 10px; text-align: center;">Net Payable</th>
                                <th style="border: 1px solid #ccc; padding: 10px; text-align: center;">Signature</th>
                            </tr>
                        </thead>
                        <tbody>
                """
                
                total_base, total_adv, total_net = 0, 0, 0
                sr_no = 1
                for idx, r in all_staff.iterrows():
                    emp_name = get_disp_val(r['name'], r.get('name_en'))
                    emp_fname = get_disp_val(r['fname'], r.get('fname_en'))
                    g_val = str(r.get('gender', 'Male'))
                    rel_type = str(r.get('g_type', 'Father'))
                    rel_label = get_relation_card_label(g_val, rel_type)
                    
                    full_emp_name = f"{emp_name} ({rel_label} {emp_fname})"
                    
                    designation = get_desig_disp(r['designation'])
                    staff_id = r['staff_id']
                    base_salary = safe_int(r['salary'])
                    stf_advance = safe_int(r.get('advance_salary', 0))
                    
                    paid_record = pd.read_sql(f"SELECT * FROM salary_records WHERE staff_id='{staff_id}' AND month='{slip_month_sel}' AND remarks='Salary'", conn)
                    status = "PAID" if not paid_record.empty else "UNPAID"
                    net_payable = max(0, base_salary - stf_advance) if status == "UNPAID" else safe_int(paid_record.iloc[0]['amount'])
                    adv_deduct = stf_advance if status == "UNPAID" else 0
                    
                    total_base += base_salary
                    total_adv += adv_deduct
                    total_net += net_payable
                    
                    stmt_html += f"""
                        <tr>
                            <td style="border: 1px solid #ccc; padding: 8px; text-align: center;">{sr_no}</td>
                            <td style="border: 1px solid #ccc; padding: 8px; text-align: {t['align']};">{staff_id}</td>
                            <td style="border: 1px solid #ccc; padding: 8px; text-align: {t['align']}; font-weight: bold;">{full_emp_name}</td>
                            <td style="border: 1px solid #ccc; padding: 8px; text-align: {t['align']};">{designation}</td>
                            <td style="border: 1px solid #ccc; padding: 8px; text-align: center;">{base_salary}</td>
                            <td style="border: 1px solid #ccc; padding: 8px; text-align: center; color: #c53030;">{adv_deduct if adv_deduct > 0 else '-'}</td>
                            <td style="border: 1px solid #ccc; padding: 8px; text-align: center; font-weight: bold; color: #005b36;">{net_payable}</td>
                            <td style="border: 1px solid #ccc; padding: 8px; text-align: center;"></td>
                        </tr>
                    """
                    sr_no += 1
                    
                stmt_html += f"""
                        </tbody>
                        <tfoot>
                            <tr style="background-color: #f2f7f4; font-weight: bold; color: #005b36;">
                                <td colspan="4" style="border: 1px solid #ccc; padding: 10px; text-align: {'right' if t['align']=='left' else 'left'};">GRAND TOTAL:</td>
                                <td style="border: 1px solid #ccc; padding: 10px; text-align: center;">{total_base}</td>
                                <td style="border: 1px solid #ccc; padding: 10px; text-align: center;">{total_adv}</td>
                                <td style="border: 1px solid #ccc; padding: 10px; text-align: center;">{total_net}</td>
                                <td style="border: 1px solid #ccc; padding: 10px;"></td>
                            </tr>
                        </tfoot>
                    </table>
                    <table style="width: 100%; border: none; margin-top: 50px; font-size: 14px;">
                        <tr>
                            <td style="text-align: {t['align']}; width: 50%;">
                                ________________________<br><br><b>Prepared By (Accountant)</b>
                            </td>
                            <td style="text-align: {'right' if t['align'] == 'left' else 'left'}; width: 50%;">
                                ________________________<br><br><b>Approved By (Principal/Admin)</b>
                            </td>
                        </tr>
                    </table>
                </div>
                """
                print_button_js(stmt_html, tr("سٹیٹمنٹ پرنٹ کریں", "Print Statement"), landscape=True)
                st.success("✅ Statement Generated!")
            else:
                st.warning("No staff found.")

# ================= 7. اکاؤنٹس اور رپورٹس =================
elif core_choice in ["اکاؤنٹس اور رپورٹس", "Accounts"]:
    st.markdown(f"<h2 class='no-print'>📈 {tr('اکاؤنٹس اور رپورٹس', 'Accounts & Reports')} - {tr(sub_choice, sub_choice)}</h2>", unsafe_allow_html=True)
    
    # --- ذیلی مینیو 1: روزانہ کی رپورٹ ---
    if sub_choice in ["Daily Report", "روزانہ کی رپورٹ"]:
        st.markdown(f"### 📅 {tr('روزانہ کا حساب کتاب', 'Daily Accounts Report')}")
        
        with st.expander(tr("➕ نیا خرچ یا آمدنی درج کریں (Add Manual Entry)", "➕ Add Manual Entry")):
            with st.form("manual_entry_form", clear_on_submit=True):
                c_me1, c_me2 = st.columns(2)
                me_type = c_me1.selectbox(tr("قسم", "Type"), [tr("آمدنی", "Income"), tr("خرچ", "Expense")])
                me_amount = c_me2.number_input(tr("رقم (Amount)", "Amount"), min_value=1, value=100)
                
                me_head = st.selectbox(tr("مد (Head)", "Head"), ["Utility Bills", "Maintenance", "Stationery", "Entertainment", "Miscellaneous", "Donation/Other Income"])
                me_desc = st.text_input(tr("تفصیل (Description)", "Description"), placeholder="مثلاً: بجلی کا بل یا مہمانوں کی چائے")
                me_date = st.date_input(tr("تاریخ", "Date"), datetime.date.today())
                
                if st.form_submit_button(tr("محفوظ کریں", "Save Entry"), type="primary"):
                    v_num = pd.read_sql("SELECT COUNT(*) FROM accounts", conn).iloc[0, 0] + 1001
                    db_type = 'آمدنی' if "آمدنی" in me_type or "Income" in me_type else 'خرچ'
                    
                    cursor.execute("INSERT INTO accounts (date, type, description, amount, head_name, voucher_no) VALUES (?, ?, ?, ?, ?, ?)", 
                                   (me_date.strftime("%Y-%m-%d"), db_type, me_desc, me_amount, me_head, f"V-{v_num}"))
                    conn.commit()
                    st.success(tr("انٹری کامیابی سے کھاتے میں شامل ہو گئی!", "Entry added to accounts successfully!"))
                    st.rerun()

        st.write("---")
        rep_date = st.date_input(tr("رپورٹ کی تاریخ منتخب کریں", "Select Date for Report"), datetime.date.today())
        rep_date_str = rep_date.strftime("%Y-%m-%d")
        
        acc_df = pd.read_sql(f"SELECT voucher_no, type, head_name, description, amount FROM accounts WHERE date='{rep_date_str}'", conn)
        
        if not acc_df.empty:
            if st.session_state.ui_lang == "اردو":
                acc_df = acc_df.rename(columns={'voucher_no': 'واؤچر نمبر', 'type': 'قسم', 'head_name': 'مد (Head)', 'description': 'تفصیل', 'amount': 'رقم'})
            
            st.dataframe(acc_df, use_container_width=True, hide_index=True)
            
            type_col = 'قسم' if st.session_state.ui_lang == "اردو" else 'type'
            amt_col = 'رقم' if st.session_state.ui_lang == "اردو" else 'amount'
            
            income_mask = acc_df[type_col].isin(['آمدنی', 'Income'])
            expense_mask = acc_df[type_col].isin(['خرچ', 'Expense'])
            
            total_income = acc_df[income_mask][amt_col].sum() if not acc_df[income_mask].empty else 0
            total_expense = acc_df[expense_mask][amt_col].sum() if not acc_df[expense_mask].empty else 0
            net_balance = total_income - total_expense
            
            c1, c2, c3 = st.columns(3)
            c1.metric(tr("کل آمدنی (Total Income)", "Total Income"), f"Rs {total_income}")
            c2.metric(tr("کل خرچ (Total Expense)", "Total Expense"), f"Rs {total_expense}")
            c3.metric(tr("آج کا نیٹ بیلنس (Net Balance)", "Today's Net Balance"), f"Rs {net_balance}")
        else:
            st.info(tr("اس تاریخ کا کھاتے میں کوئی ریکارڈ موجود نہیں۔", "No account records found for this date."))

    # --- ذیلی مینیو 2: ماہانہ رپورٹ ---
    elif sub_choice in ["Monthly Report", "ماہانہ رپورٹ"]:
        st.markdown(f"### 🗓️ {tr('ماہانہ حساب کتاب', 'Monthly Accounts Report')}")
        
        c_m1, c_m2 = st.columns(2)
        m_opts = ["01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11", "12"]
        curr_month = datetime.date.today().strftime("%m")
        rep_month = c_m1.selectbox(tr("مہینہ منتخب کریں", "Select Month"), m_opts, index=m_opts.index(curr_month) if curr_month in m_opts else 0)
        rep_year = c_m2.text_input(tr("سال (Year)", "Year"), value=str(datetime.date.today().year))
        
        search_pattern = f"{rep_year}-{rep_month}-%"
        acc_m_df = pd.read_sql(f"SELECT date, voucher_no, type, head_name, description, amount FROM accounts WHERE date LIKE '{search_pattern}' ORDER BY date", conn)
        
        if not acc_m_df.empty:
            if st.session_state.ui_lang == "اردو":
                acc_m_df = acc_m_df.rename(columns={'date': 'تاریخ', 'voucher_no': 'واؤچر نمبر', 'type': 'قسم', 'head_name': 'مد (Head)', 'description': 'تفصیل', 'amount': 'رقم'})
            
            st.dataframe(acc_m_df, use_container_width=True, hide_index=True)
            
            type_col = 'قسم' if st.session_state.ui_lang == "اردو" else 'type'
            amt_col = 'رقم' if st.session_state.ui_lang == "اردو" else 'amount'
            
            income_mask = acc_m_df[type_col].isin(['آمدنی', 'Income'])
            expense_mask = acc_m_df[type_col].isin(['خرچ', 'Expense'])
            
            total_income = acc_m_df[income_mask][amt_col].sum() if not acc_m_df[income_mask].empty else 0
            total_expense = acc_m_df[expense_mask][amt_col].sum() if not acc_m_df[expense_mask].empty else 0
            net_balance = total_income - total_expense
            
            st.write("---")
            c1, c2, c3 = st.columns(3)
            c1.metric(tr("ماہانہ آمدنی (Monthly Income)", "Monthly Income"), f"Rs {total_income}")
            c2.metric(tr("ماہانہ خرچ (Monthly Expense)", "Monthly Expense"), f"Rs {total_expense}")
            c3.metric(tr("مہینے کا منافع/نقصان (Net PnL)", "Monthly Net PnL"), f"Rs {net_balance}")
        else:
            st.info(tr("اس مہینے کا کھاتے میں کوئی ریکارڈ موجود نہیں۔", "No account records found for this month."))

    # --- ذیلی مینیو 3: لیجر / کھاتہ (میگا لیجر سسٹم) ---
    elif sub_choice in ["Ledger", "لیجر / کھاتہ"]:
        
        tab_stu, tab_stf, tab_gen = st.tabs([
            "🎓 " + tr("طالب علم کا لیجر", "Student Ledger"),
            "💼 " + tr("سٹاف کا لیجر", "Staff Ledger"),
            "🏛️ " + tr("سکول کا جنرل لیجر", "General Ledger")
        ])
        
        with tab_stu:
            st.markdown(f"#### 🎓 {tr('انفرادی سٹوڈنٹ لیجر', 'Individual Student Ledger')}")
            db_cls = pd.read_sql("SELECT class_name FROM sys_classes", conn)['class_name'].tolist()
            if not db_cls: db_cls = classes_list
            c_l1, c_l2 = st.columns(2)
            l_cls = c_l1.selectbox(tr("کلاس", "Class"), db_cls, key="l_cls")
            
            db_sec = pd.read_sql(f"SELECT section_name FROM sys_sections WHERE class_name='{l_cls}'", conn)['section_name'].tolist()
            if not db_sec: db_sec = ["A"]
            l_sec = c_l2.selectbox(tr("سیکشن", "Section"), db_sec, key="l_sec")
            
            students_df = pd.read_sql(f"SELECT reg_id, name, fname, arrears, advance_fee FROM students WHERE class='{l_cls}' AND section='{l_sec}'", conn)
            
            if not students_df.empty:
                stu_opts = students_df.apply(lambda row: f"{row['reg_id']} - {row['name']} (S/O {row['fname']})", axis=1).tolist()
                sel_stu = st.selectbox(tr("طالب علم منتخب کریں", "Select Student"), stu_opts)
                sel_reg_id = sel_stu.split(" - ")[0]
                
                fee_records = pd.read_sql(f"SELECT month as 'Month', total as 'Total', CASE WHEN status='Paid' THEN total ELSE 0 END as 'Paid', CASE WHEN status='Unpaid' THEN total ELSE 0 END as 'Balance', status as 'Status', date as 'Date' FROM fees WHERE reg_id='{sel_reg_id}' ORDER BY rowid DESC", conn)
                
                stu_current_info = students_df[students_df['reg_id'] == sel_reg_id].iloc[0]
                curr_arrears = stu_current_info['arrears']
                curr_advance = stu_current_info.get('advance_fee', 0)
                
                total_billed = pd.read_sql(f"SELECT SUM(total) FROM fees WHERE reg_id='{sel_reg_id}'", conn).iloc[0,0] or 0
                total_paid = pd.read_sql(f"SELECT SUM(total) FROM fees WHERE reg_id='{sel_reg_id}' AND status='Paid'", conn).iloc[0,0] or 0
                
                # 🟢 ایموجی (💰) کو محفوظ HTML کوڈ (&#128176;) سے بدل دیا گیا ہے
                st.markdown(f"""
                <div style='background-color:#f1f8e9; padding:20px; border-radius:10px; border:2px solid #8bc34a; text-align:center; margin-bottom: 20px;'>
                    <h3 style='margin:0; color:#33691e;'>&#128176; {tr('طالب علم کا مالیاتی خلاصہ', 'Student Ledger Summary')}</h3>
                    <hr style='border-top:1px solid #8bc34a;'>
                    <div style='display:flex; justify-content:space-around; flex-wrap:wrap;'>
                        <div style='margin:10px;'>
                            <p style='margin:0; color:#555;'>{tr('کل فیس بنی', 'Total Billed')}</p>
                            <h3 style='margin:0;'>{total_billed} Rs</h3>
                        </div>
                        <div style='margin:10px;'>
                            <p style='margin:0; color:#555;'>{tr('کل فیس جمع ہوئی', 'Total Paid')}</p>
                            <h3 style='margin:0; color:green;'>{total_paid} Rs</h3>
                        </div>
                        <div style='margin:10px;'>
                            <p style='margin:0; color:#555;'>{tr('ایڈوانس فیس', 'Advance')}</p>
                            <h3 style='margin:0; color:blue;'>{curr_advance} Rs</h3>
                        </div>
                        <div style='margin:10px; background-color:#ffebee; padding:10px; border-radius:8px;'>
                            <p style='margin:0; color:#c62828; font-weight:bold;'>{tr('موجودہ بقایا جات', 'Current Arrears')}</p>
                            <h3 style='margin:0; color:#c62828;'>{curr_arrears} Rs</h3>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                if not fee_records.empty:
                    st.markdown(f"#### 📜 {tr('پچھلے تمام چالان کی تفصیل', 'Challan History')}")
                    if st.session_state.ui_lang == "اردو":
                        fee_records = fee_records.rename(columns={'Month': 'مہینہ', 'Total': 'کل فیس', 'Paid': 'ادا شدہ', 'Balance': 'بقایا جات', 'Status': 'سٹیٹس', 'Date': 'تاریخ'})
                    st.dataframe(fee_records, use_container_width=True, hide_index=True)
                else:
                    st.info(tr("اس طالب علم کا کوئی فیس ریکارڈ / چالان موجود نہیں۔", "No fee record found for this student."))
            else:
                st.info(tr("اس کلاس/سیکشن میں کوئی طالب علم نہیں۔", "No students in this class/section."))
                
        with tab_stf:
            st.markdown(f"#### 💼 {tr('سٹاف کا انفرادی لیجر', 'Staff Individual Ledger')}")
            staff_df = pd.read_sql("SELECT staff_id, name, designation, advance_salary FROM staff", conn)
            if not staff_df.empty:
                staff_opts = staff_df.apply(lambda row: f"{row['staff_id']} - {row['name']} ({row['designation']})", axis=1).tolist()
                sel_staff = st.selectbox(tr("سٹاف ممبر منتخب کریں", "Select Staff"), staff_opts)
                sel_staff_id = sel_staff.split(" - ")[0]
                
                curr_stf_adv = staff_df[staff_df['staff_id'] == sel_staff_id].iloc[0].get('advance_salary', 0)
                
                # 🟢 ایموجی (💸) کو محفوظ HTML کوڈ (&#128184;) سے بدل دیا گیا ہے
                st.markdown(f"""
                <div style='background-color:#e3f2fd; padding:20px; border-radius:10px; border:2px solid #2196f3; text-align:center; margin-bottom: 20px;'>
                    <h3 style='margin:0; color:#0d47a1;'>&#128184; {tr('سٹاف کا مالیاتی خلاصہ', 'Staff Ledger Summary')}</h3>
                    <hr style='border-top:1px solid #2196f3;'>
                    <h4 style='margin:5px 0;'>{tr('موجودہ کٹا ہوا ایڈوانس (Pending Advance):', 'Pending Advance:')} <b style='color:red;'>{curr_stf_adv} Rs</b></h4>
                    <p style='color:#555; font-size:12px;'>{tr('(یہ وہ رقم ہے جو سٹاف نے پیشگی لے رکھی ہے اور اگلی تنخواہوں سے کٹے گی)', '(This is the advance amount taken by staff, which will be deducted from upcoming salaries)')}</p>
                </div>
                """, unsafe_allow_html=True)
                
                stf_history = pd.read_sql(f"SELECT date as 'Date', month as 'Month', remarks as 'Type', amount as 'Amount' FROM salary_records WHERE staff_id='{sel_staff_id}' ORDER BY rowid DESC", conn)
                
                if not stf_history.empty:
                    st.markdown(f"#### 📜 {tr('تنخواہ اور ادائیگیوں کی ہسٹری', 'Payment History')}")
                    if st.session_state.ui_lang == "اردو":
                        stf_history = stf_history.rename(columns={'Date': 'تاریخ', 'Month': 'مہینہ', 'Type': 'قسم (تنخواہ/ایڈوانس)', 'Amount': 'رقم'})
                        
                    st.dataframe(stf_history, use_container_width=True, hide_index=True)
                else:
                    st.info(tr("اس سٹاف ممبر کا کوئی سیلری ریکارڈ موجود نہیں۔", "No salary record found for this staff member."))
            else:
                st.info(tr("کوئی سٹاف موجود نہیں۔", "No staff found."))
                
        with tab_gen:
            st.markdown(f"#### 🏛️ {tr('سکول کا جنرل لیجر / مکمل کھاتہ', 'School General Ledger')}")
            st.write(tr("یہاں سے آپ مخصوص تاریخوں کے درمیان سکول کی تمام آمدنی اور اخراجات دیکھ سکتے ہیں۔", "View all income and expenses between specific dates."))
            
            c_gl1, c_gl2 = st.columns(2)
            gl_start = c_gl1.date_input(tr("شروع کی تاریخ (Start Date)", "Start Date"), datetime.date.today().replace(day=1), key="gl_s")
            gl_end = c_gl2.date_input(tr("ختم ہونے کی تاریخ (End Date)", "End Date"), datetime.date.today(), key="gl_e")
            
            if gl_start > gl_end:
                st.error(tr("شروع کی تاریخ ختم ہونے کی تاریخ سے پہلے ہونی چاہیے۔", "Start date must be before end date."))
            else:
                gl_df = pd.read_sql(f"SELECT date, voucher_no, type, head_name, description, amount FROM accounts WHERE date BETWEEN '{gl_start.strftime('%Y-%m-%d')}' AND '{gl_end.strftime('%Y-%m-%d')}' ORDER BY date", conn)
                
                if not gl_df.empty:
                    if st.session_state.ui_lang == "اردو":
                        gl_df_display = gl_df.rename(columns={'date': 'تاریخ', 'voucher_no': 'واؤچر نمبر', 'type': 'قسم', 'head_name': 'مد (Head)', 'description': 'تفصیل', 'amount': 'رقم'})
                    else:
                        gl_df_display = gl_df
                    
                    st.dataframe(gl_df_display, use_container_width=True, hide_index=True)
                    
                    inc_total = gl_df[gl_df['type'].isin(['آمدنی', 'Income'])]['amount'].sum()
                    exp_total = gl_df[gl_df['type'].isin(['خرچ', 'Expense'])]['amount'].sum()
                    net_total = inc_total - exp_total
                    
                    st.write("---")
                    g1, g2, g3 = st.columns(3)
                    g1.metric(tr("مجموعی آمدنی (Total Income)", "Total Income"), f"Rs {inc_total}")
                    g2.metric(tr("مجموعی اخراجات (Total Expenses)", "Total Expenses"), f"Rs {exp_total}")
                    g3.metric(tr("مجموعی بیلنس (Net Balance)", "Net Balance"), f"Rs {net_total}")
                else:
                    st.info(tr("ان تاریخوں کے درمیان کھاتے کا کوئی ریکارڈ نہیں ملا۔", "No account records found between these dates."))

# ================= 8. تعلیمی نظام (Academics & Exams) =================
elif core_choice in ["تعلیمی نظام", "Academics"]:
    st.markdown(f"<h2 class='no-print'>📚 {tr('تعلیمی اور امتحانی نظام', 'Academics & Examination System')} - {tr(sub_choice, sub_choice)}</h2>", unsafe_allow_html=True)
    
    if sub_choice in ["Academic Sessions", "اکیڈمک سیشنز"]:
        st.markdown(f"<h2>📅 Academic Sessions</h2>", unsafe_allow_html=True)
        st.markdown(f"<p style='color:gray;'>Manage academic session years, switch the active session, or edit/delete existing sessions.</p>", unsafe_allow_html=True)
        st.write("---")

        col_reg, col_list = st.columns([1, 1.5])

        with col_reg:
            st.markdown("### ➕ Register Session")
            with st.form("new_session_form"):
                new_sess_name = st.text_input("Session Name", placeholder="e.g. 2027-28")
                if st.form_submit_button("+ Add Session Year", type="primary"):
                    if new_sess_name.strip():
                        new_session = new_sess_name.strip()
                        cursor.execute("SELECT * FROM academic_sessions WHERE session_name=?", (new_session,))
                        if cursor.fetchone():
                            st.error("یہ سیشن پہلے سے موجود ہے!")
                        else:
                            cursor.execute("INSERT INTO academic_sessions VALUES (?, 'INACTIVE')", (new_session,))
                            conn.commit()
                            
                            new_db_file = f'school_system_{new_session}.db'
                            shutil.copy2(DB_FILE, new_db_file)
                            
                            new_conn = sqlite3.connect(new_db_file)
                            new_cursor = new_conn.cursor()
                            tables_to_clear = ['fees', 'accounts', 'attendance', 'salary_records', 'lesson_plan', 'exam_marks', 'timetable', 'notices']
                            for table in tables_to_clear:
                                try: new_cursor.execute(f"DELETE FROM {table}")
                                except: pass
                            new_conn.commit()
                            new_conn.close()
                            
                            st.success(f"سیشن {new_session} کامیابی سے بن گیا!")
                            st.rerun()
                    else:
                        st.warning("Please enter a valid session name.")
            
            st.write("---")
            st.markdown("### ✏️/🗑️ Edit or Delete Session")
            sessions_list = pd.read_sql("SELECT session_name FROM academic_sessions", conn)['session_name'].tolist()
            if sessions_list:
                sel_edit_sess = st.selectbox("Select Session", sessions_list, key="edit_sess_sel")
                new_sess_val = st.text_input("New Name (For Edit)", value=sel_edit_sess, key="new_sess_val")
                
                c_e1, c_e2 = st.columns(2)
                if c_e1.button("✏️ Update Name", use_container_width=True):
                    if new_sess_val.strip() and new_sess_val != sel_edit_sess:
                        cursor.execute("SELECT * FROM academic_sessions WHERE session_name=?", (new_sess_val.strip(),))
                        if cursor.fetchone():
                            st.error("یہ نام پہلے سے کسی سیشن کا ہے!")
                        else:
                            cursor.execute("UPDATE academic_sessions SET session_name=? WHERE session_name=?", (new_sess_val.strip(), sel_edit_sess))
                            conn.commit()
                            
                            old_file = 'school_system.db' if sel_edit_sess == '2026-27' else f'school_system_{sel_edit_sess}.db'
                            new_file = f'school_system_{new_sess_val.strip()}.db'
                            
                            if os.path.exists(old_file):
                                os.rename(old_file, new_file)
                            
                            if active_session == sel_edit_sess:
                                with open(SESSION_TRACKER_FILE, "w") as f:
                                    f.write(new_file)
                                    
                            st.success("سیشن کا نام کامیابی سے تبدیل ہو گیا!")
                            st.rerun()

                if c_e2.button("🗑️ Delete", use_container_width=True):
                    if active_session == sel_edit_sess:
                        st.error("⚠️ آپ ایکٹو (Active) سیشن کو ڈیلیٹ نہیں کر سکتے۔ پہلے کوئی اور سیشن ایکٹو کریں۔")
                    else:
                        cursor.execute("DELETE FROM academic_sessions WHERE session_name=?", (sel_edit_sess,))
                        conn.commit()
                        
                        del_file = 'school_system.db' if sel_edit_sess == '2026-27' else f'school_system_{sel_edit_sess}.db'
                        if os.path.exists(del_file):
                            os.remove(del_file)
                            
                        st.success("سیشن اور اس کا سارا ڈیٹا مکمل طور پر ڈیلیٹ ہو گیا!")
                        st.rerun()

        with col_list:
            st.markdown("### 🟢 Registered Academic Sessions")
            sessions_df = pd.read_sql("SELECT * FROM academic_sessions", conn)
            
            if not sessions_df.empty:
                st.caption(f"Total: {len(sessions_df)}")
                for _, row in sessions_df.iterrows():
                    s_name = row['session_name']
                    s_status = row['status']
                    
                    is_active = (s_status == 'ACTIVE')
                    box_color = "#e8f5e9" if is_active else "#f9f9f9"
                    border_color = "#4caf50" if is_active else "#ccc"
                    
                    c_card1, c_card2 = st.columns([3, 1])
                    with c_card1:
                        # 🟢 کیلنڈر اور ڈاٹ ایموجی کو محفوظ HTML کوڈز سے بدل دیا گیا ہے تاکہ ایرر نہ آئے
                        st.markdown(f"""
                        <div style="background: {box_color}; border: 1px solid {border_color}; padding: 12px; border-radius: 8px; margin-bottom: 10px;">
                            <b>&#128197; Session {s_name}</b> {'<span style="color: green; font-weight: bold; float: right;">&#9679; ACTIVE</span>' if is_active else ''}
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with c_card2:
                        if not is_active:
                            if st.button("Activate", key=f"act_{s_name}"):
                                target_db = 'school_system.db' if s_name == '2026-27' else f'school_system_{s_name}.db'
                                
                                with open(SESSION_TRACKER_FILE, "w") as f:
                                    f.write(target_db)
                                
                                try:
                                    t_conn = sqlite3.connect(target_db)
                                    t_conn.execute("UPDATE academic_sessions SET status='INACTIVE'")
                                    t_conn.execute("UPDATE academic_sessions SET status='ACTIVE' WHERE session_name=?", (s_name,))
                                    t_conn.commit()
                                    t_conn.close()
                                except: pass
                                
                                st.success(f"Session {s_name} is now ACTIVE!")
                                st.rerun()
            else:
                st.info("No sessions found.")

    elif sub_choice in ["Classes", "کلاسز"]:
        st.markdown("<style>.stButton>button { border-radius: 8px; font-weight: bold; }</style>", unsafe_allow_html=True)
        st.markdown(f"<h2 class='no-print'>🏫 {tr('کلاسز، سیکشنز اور مضامین کا نظام', 'Classes, Sections & Subjects Management')}</h2>", unsafe_allow_html=True)
        st.write("---")

        cursor.execute('''CREATE TABLE IF NOT EXISTS sys_classes (class_name TEXT PRIMARY KEY)''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS sys_sections (id INTEGER PRIMARY KEY AUTOINCREMENT, class_name TEXT, section_name TEXT)''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS sys_subjects (id INTEGER PRIMARY KEY AUTOINCREMENT, class_name TEXT, section_name TEXT, subject_name TEXT)''')
        
        for c in classes_list:
            cursor.execute("INSERT OR IGNORE INTO sys_classes (class_name) VALUES (?)", (c,))
            
        cursor.execute("SELECT DISTINCT class FROM students WHERE class IS NOT NULL AND class != ''")
        for cls in cursor.fetchall():
            cursor.execute("INSERT OR IGNORE INTO sys_classes (class_name) VALUES (?)", (cls[0],))
            
        cursor.execute("SELECT DISTINCT class, section FROM students WHERE class IS NOT NULL AND section IS NOT NULL AND section != ''")
        for c_name, s_name in cursor.fetchall():
            cursor.execute("SELECT id FROM sys_sections WHERE class_name=? AND section_name=?", (c_name, s_name))
            if not cursor.fetchone():
                cursor.execute("INSERT INTO sys_sections (class_name, section_name) VALUES (?, ?)", (c_name, s_name))

        cursor.execute("SELECT class_name, section_name FROM sys_sections")
        all_sys_sections = cursor.fetchall()
        
        try:
            cursor.execute("SELECT subject_name FROM subjects")
            old_subjects = [s[0] for s in cursor.fetchall()]
            for c_n, s_n in all_sys_sections:
                cursor.execute("SELECT COUNT(*) FROM sys_subjects WHERE class_name=? AND section_name=?", (c_n, s_n))
                if cursor.fetchone()[0] == 0:
                    for sub in old_subjects:
                        cursor.execute("INSERT INTO sys_subjects (class_name, section_name, subject_name) VALUES (?, ?, ?)", (c_n, s_n, sub))
        except: pass
                    
        conn.commit()

        if 'mgt_sel_class' not in st.session_state: st.session_state.mgt_sel_class = None
        if 'mgt_sel_sec' not in st.session_state: st.session_state.mgt_sel_sec = None

        col_cls, col_sec, col_sub = st.columns([1, 1, 1], gap="large")

        with col_cls:
            st.markdown(f"### 🎓 {tr('کلاسز', 'CLASSES')}")
            classes_df = pd.read_sql("SELECT class_name FROM sys_classes", conn)
            
            if not classes_df.empty:
                for _, row in classes_df.iterrows():
                    c_name = row['class_name']
                    stu_count = pd.read_sql(f"SELECT COUNT(*) FROM students WHERE class='{c_name}' AND status='Active'", conn).iloc[0,0]
                    
                    is_active = (st.session_state.mgt_sel_class == c_name)
                    btn_type = "primary" if is_active else "secondary"
                    
                    cc1, cc2 = st.columns([4, 1])
                    if cc1.button(f"{c_name} 👤 {stu_count}", key=f"btn_c_{c_name}", use_container_width=True, type=btn_type):
                        st.session_state.mgt_sel_class = c_name
                        st.session_state.mgt_sel_sec = None
                        st.rerun()
                    if cc2.button("🗑️", key=f"del_c_{c_name}"):
                        cursor.execute("DELETE FROM sys_classes WHERE class_name=?", (c_name,))
                        cursor.execute("DELETE FROM sys_sections WHERE class_name=?", (c_name,))
                        cursor.execute("DELETE FROM sys_subjects WHERE class_name=?", (c_name,))
                        conn.commit()
                        if st.session_state.mgt_sel_class == c_name:
                            st.session_state.mgt_sel_class = None
                        st.rerun()
            else:
                st.info(tr("کوئی کلاس موجود نہیں۔", "No classes found."))

            st.write("")
            with st.form("add_class_form", clear_on_submit=True):
                new_class = st.text_input(tr("نئی کلاس کا نام", "Add New Class"), placeholder="e.g. Class 10th")
                if st.form_submit_button(tr("➕ شامل کریں", "➕ Add"), use_container_width=True):
                    if new_class.strip():
                        try:
                            cursor.execute("INSERT INTO sys_classes (class_name) VALUES (?)", (new_class.strip(),))
                            conn.commit()
                            st.rerun()
                        except: st.error("Class already exists!")
                        
            with st.expander(tr("✏️ کلاس کا نام تبدیل کریں", "✏️ Rename Class")):
                c_list_db = pd.read_sql("SELECT class_name FROM sys_classes", conn)['class_name'].tolist()
                if c_list_db:
                    with st.form("edit_class_form", clear_on_submit=True):
                        c_to_edit = st.selectbox(tr("کلاس منتخب کریں", "Select Class"), c_list_db)
                        new_c_name = st.text_input(tr("نیا نام لکھیں", "New Name"))
                        if st.form_submit_button(tr("تبدیل کریں", "Update"), use_container_width=True):
                            if new_c_name.strip() and new_c_name.strip() != c_to_edit:
                                n_c = new_c_name.strip()
                                try:
                                    cursor.execute("INSERT INTO sys_classes (class_name) VALUES (?)", (n_c,))
                                    cursor.execute("DELETE FROM sys_classes WHERE class_name=?", (c_to_edit,))
                                    
                                    cursor.execute("UPDATE sys_sections SET class_name=? WHERE class_name=?", (n_c, c_to_edit))
                                    cursor.execute("UPDATE sys_subjects SET class_name=? WHERE class_name=?", (n_c, c_to_edit))
                                    
                                    try: cursor.execute("UPDATE students SET class=? WHERE class=?", (n_c, c_to_edit))
                                    except: pass
                                    try: cursor.execute("UPDATE timetable SET class=? WHERE class=?", (n_c, c_to_edit))
                                    except: pass
                                    try: cursor.execute("UPDATE lesson_plan SET class=? WHERE class=?", (n_c, c_to_edit))
                                    except: pass
                                    
                                    conn.commit()
                                    if st.session_state.mgt_sel_class == c_to_edit:
                                        st.session_state.mgt_sel_class = n_c
                                    st.success(tr("نام کامیابی سے تبدیل ہو گیا!", "Name updated successfully!"))
                                    st.rerun()
                                except: st.error("Name already exists or error occurred.")

        with col_sec:
            if st.session_state.mgt_sel_class:
                sel_c = st.session_state.mgt_sel_class
                st.markdown(f"### 📚 {sel_c.upper()} {tr('کے سیکشنز', 'SECTIONS')}")
                
                sec_df = pd.read_sql(f"SELECT id, section_name FROM sys_sections WHERE class_name='{sel_c}'", conn)
                
                if not sec_df.empty:
                    for _, row in sec_df.iterrows():
                        s_id, s_name = row['id'], row['section_name']
                        stu_count_sec = pd.read_sql(f"SELECT COUNT(*) FROM students WHERE class='{sel_c}' AND section='{s_name}' AND status='Active'", conn).iloc[0,0]
                        
                        is_active_sec = (st.session_state.mgt_sel_sec == s_name)
                        btn_type_sec = "primary" if is_active_sec else "secondary"
                        
                        sc1, sc2 = st.columns([4, 1])
                        if sc1.button(f"Sec {s_name} 👤 {stu_count_sec}", key=f"btn_s_{s_id}", use_container_width=True, type=btn_type_sec):
                            st.session_state.mgt_sel_sec = s_name
                            st.rerun()
                        if sc2.button("🗑️", key=f"del_s_{s_id}"):
                            cursor.execute("DELETE FROM sys_sections WHERE id=?", (s_id,))
                            cursor.execute("DELETE FROM sys_subjects WHERE class_name=? AND section_name=?", (sel_c, s_name))
                            conn.commit()
                            if st.session_state.mgt_sel_sec == s_name:
                                st.session_state.mgt_sel_sec = None
                            st.rerun()
                else:
                    st.info(tr("کوئی سیکشن موجود نہیں۔", "No sections found."))

                st.write("")
                with st.form("add_sec_form", clear_on_submit=True):
                    new_sec = st.text_input(f"Add Section to {sel_c}", placeholder="e.g. A, B, Model")
                    if st.form_submit_button(tr("➕ شامل کریں", "➕ Add"), use_container_width=True):
                        if new_sec.strip():
                            cursor.execute("INSERT INTO sys_sections (class_name, section_name) VALUES (?, ?)", (sel_c, new_sec.strip()))
                            conn.commit()
                            st.rerun()
                            
                with st.expander(tr("✏️ سیکشن کا نام تبدیل کریں", "✏️ Rename Section")):
                    sec_list_db = pd.read_sql(f"SELECT id, section_name FROM sys_sections WHERE class_name='{sel_c}'", conn)
                    if not sec_list_db.empty:
                        with st.form("edit_sec_form", clear_on_submit=True):
                            s_to_edit_id = st.selectbox(tr("سیکشن منتخب کریں", "Select Section"), sec_list_db['id'].tolist(), format_func=lambda x: sec_list_db[sec_list_db['id']==x]['section_name'].values[0])
                            new_s_name = st.text_input(tr("نیا نام لکھیں", "New Name"))
                            if st.form_submit_button(tr("تبدیل کریں", "Update"), use_container_width=True):
                                if new_s_name.strip():
                                    old_s_name = sec_list_db[sec_list_db['id']==s_to_edit_id]['section_name'].values[0]
                                    n_s = new_s_name.strip()
                                    
                                    cursor.execute("UPDATE sys_sections SET section_name=? WHERE id=?", (n_s, s_to_edit_id))
                                    cursor.execute("UPDATE sys_subjects SET section_name=? WHERE class_name=? AND section_name=?", (n_s, sel_c, old_s_name))
                                    
                                    try: cursor.execute("UPDATE students SET section=? WHERE class=? AND section=?", (n_s, sel_c, old_s_name))
                                    except: pass
                                    try: cursor.execute("UPDATE timetable SET section=? WHERE class=? AND section=?", (n_s, sel_c, old_s_name))
                                    except: pass
                                    try: cursor.execute("UPDATE lesson_plan SET section=? WHERE class=? AND section=?", (n_s, sel_c, old_s_name))
                                    except: pass
                                    
                                    conn.commit()
                                    if st.session_state.mgt_sel_sec == old_s_name:
                                        st.session_state.mgt_sel_sec = n_s
                                    st.success(tr("نام کامیابی سے تبدیل ہو گیا!", "Name updated successfully!"))
                                    st.rerun()
            else:
                st.markdown(f"### 📚 {tr('سیکشنز', 'SECTIONS')}")
                st.info(tr("👆 پہلے بائیں طرف سے کوئی کلاس منتخب کریں (اس کے نام پر کلک کریں)۔", "👆 Please click on a class from the left first."))

        with col_sub:
            if st.session_state.mgt_sel_class and st.session_state.mgt_sel_sec:
                sel_c = st.session_state.mgt_sel_class
                sel_s = st.session_state.mgt_sel_sec
                st.markdown(f"### 📖 {tr('مضامین', 'SUBJECTS')} (Sec {sel_s})")
                
                sub_df = pd.read_sql(f"SELECT id, subject_name FROM sys_subjects WHERE class_name='{sel_c}' AND section_name='{sel_s}'", conn)
                
                if not sub_df.empty:
                    for _, row in sub_df.iterrows():
                        sub_id, sub_name = row['id'], row['subject_name']
                        
                        sb1, sb2 = st.columns([4, 1])
                        sb1.markdown(f"<div style='border:1px solid #ccc; padding:7px 10px; border-radius:5px; margin-bottom:5px; background:white;'>{sub_name}</div>", unsafe_allow_html=True)
                        if sb2.button("🗑️", key=f"del_sub_{sub_id}"):
                            cursor.execute("DELETE FROM sys_subjects WHERE id=?", (sub_id,))
                            conn.commit()
                            st.rerun()
                else:
                    st.info(tr("کوئی مضمون موجود نہیں۔", "No subjects found."))

                st.write("")
                with st.form("add_sub_form_new", clear_on_submit=True):
                    new_sub = st.text_input(f"Add Subject to Sec {sel_s}", placeholder="e.g. Biology, English")
                    if st.form_submit_button(tr("➕ شامل کریں", "➕ Add"), use_container_width=True):
                        if new_sub.strip():
                            cursor.execute("INSERT INTO sys_subjects (class_name, section_name, subject_name) VALUES (?, ?, ?)", (sel_c, sel_s, new_sub.strip()))
                            conn.commit()
                            st.rerun()
                            
                with st.expander(tr("✏️ مضمون کا نام تبدیل کریں", "✏️ Rename Subject")):
                    sub_list_db = pd.read_sql(f"SELECT id, subject_name FROM sys_subjects WHERE class_name='{sel_c}' AND section_name='{sel_s}'", conn)
                    if not sub_list_db.empty:
                        with st.form("edit_sub_form", clear_on_submit=True):
                            sub_to_edit_id = st.selectbox(tr("مضمون منتخب کریں", "Select Subject"), sub_list_db['id'].tolist(), format_func=lambda x: sub_list_db[sub_list_db['id']==x]['subject_name'].values[0])
                            new_sub_name = st.text_input(tr("نیا نام لکھیں", "New Name"))
                            if st.form_submit_button(tr("تبدیل کریں", "Update"), use_container_width=True):
                                if new_sub_name.strip():
                                    old_sub_name = sub_list_db[sub_list_db['id']==sub_to_edit_id]['subject_name'].values[0]
                                    n_sub = new_sub_name.strip()
                                    
                                    cursor.execute("UPDATE sys_subjects SET subject_name=? WHERE id=?", (n_sub, sub_to_edit_id))
                                    
                                    try: cursor.execute("UPDATE timetable SET subject=? WHERE class=? AND section=? AND subject=?", (n_sub, sel_c, sel_s, old_sub_name))
                                    except: pass
                                    try: cursor.execute("UPDATE lesson_plan SET subject=? WHERE class=? AND section=? AND subject=?", (n_sub, sel_c, sel_s, old_sub_name))
                                    except: pass
                                    try: cursor.execute("UPDATE exam_marks SET subject=? WHERE subject=? AND reg_id IN (SELECT reg_id FROM students WHERE class=? AND section=?)", (n_sub, old_sub_name, sel_c, sel_s))
                                    except: pass
                                    
                                    conn.commit()
                                    st.success(tr("نام کامیابی سے تبدیل ہو گیا!", "Name updated successfully!"))
                                    st.rerun()
            else:
                st.markdown(f"### 📖 {tr('مضامین', 'SUBJECTS')}")
                st.info(tr("👆 پہلے کلاس اور سیکشن منتخب کریں۔", "👆 Please select class and section first."))

    elif sub_choice == "Time Table":
        st.markdown("<div class='no-print'>", unsafe_allow_html=True)
        
        if 'tt_sel_class' not in st.session_state: st.session_state.tt_sel_class = classes_list[0]
        if 'tt_sel_sec' not in st.session_state: st.session_state.tt_sel_sec = "A"
        
        with st.expander(tr("➕ نیا پیریڈ شامل کریں", "➕ Add New Period"), expanded=True):
            c_a1, c_a2 = st.columns(2)
            
            db_cls = pd.read_sql("SELECT class_name FROM sys_classes", conn)['class_name'].tolist()
            if not db_cls: db_cls = classes_list
            tt_add_class = c_a1.selectbox(
                tr("کلاس", "Class"), 
                db_cls, 
                index=db_cls.index(st.session_state.tt_sel_class) if st.session_state.tt_sel_class in db_cls else 0,
                key="tt_add_cls"
            )
            db_sec = pd.read_sql(f"SELECT section_name FROM sys_sections WHERE class_name='{tt_add_class}'", conn)['section_name'].tolist()
            if not db_sec: db_sec = ["A"]
            tt_add_sec = c_a2.selectbox(
                tr("سیکشن", "Section"), 
                db_sec, 
                index=db_sec.index(st.session_state.tt_sel_sec) if st.session_state.tt_sel_sec in db_sec else 0,
                key="tt_add_sec"
            )
            
            if tt_add_class != st.session_state.tt_sel_class or tt_add_sec != st.session_state.tt_sel_sec:
                st.session_state.tt_sel_class = tt_add_class
                st.session_state.tt_sel_sec = tt_add_sec
                st.rerun()
            
            days = [tr("روزانہ", "Daily"), tr("سوموار", "Monday"), tr("منگل", "Tuesday"), tr("بدھ", "Wednesday"), tr("جمعرات", "Thursday"), tr("جمعہ", "Friday"), tr("ہفتہ", "Saturday")]
            periods = [tr("پہلا پیریڈ", "1st Period"), tr("دوسرا پیریڈ", "2nd Period"), tr("تیسرا پیریڈ", "3rd Period"), tr("چوتھا پیریڈ", "4th Period"), tr("پانچواں پیریڈ", "5th Period"), tr("چھٹا پیریڈ", "6th Period"), tr("ساتواں پیریڈ", "7th Period"), tr("آٹھواں پیریڈ", "8th Period")]
            
            tt_day = st.selectbox(tr("دن", "Day"), days)
            
            existing_tt = pd.read_sql(f"SELECT period, subject FROM timetable WHERE class='{tt_add_class}' AND section='{tt_add_sec}' AND day='{tt_day}'", conn)
            used_periods = existing_tt['period'].tolist() if not existing_tt.empty else []
            used_subs = existing_tt['subject'].tolist() if not existing_tt.empty else []
            
            available_periods = [p for p in periods if p not in used_periods]
            
            all_subs_df = pd.read_sql(f"SELECT subject_name FROM sys_subjects WHERE class_name='{tt_add_class}' AND section_name='{tt_add_sec}'", conn)
            all_subs = all_subs_df['subject_name'].tolist() if not all_subs_df.empty else ["کوئی مضمون نہیں / No Subject"]
            
            available_subs = [s for s in all_subs if s not in used_subs]
            if not available_subs and "No Subject" not in all_subs[0]: 
                 st.info(tr("اس دن کے تمام مضامین شیڈول ہو چکے ہیں۔", "All subjects for this day are already scheduled."))
                 available_subs = ["تمام مضامین شامل ہو چکے ہیں"]
            elif not available_subs:
                 available_subs = all_subs
            
            available_teachers = pd.read_sql("SELECT name FROM staff", conn)['name'].tolist()
            if not available_teachers: available_teachers = ["No Teacher Found"]

            if not available_periods:
                st.warning(tr("اس دن کے تمام پیریڈز مکمل ہو چکے ہیں۔", "All periods for this day are assigned."))
            elif "تمام مضامین" not in available_subs[0] and "No Subject" not in available_subs[0]:
                c_p1, c_p2, c_p3 = st.columns(3)
                tt_period = c_p1.selectbox(tr("پیریڈ", "Period"), available_periods)
                tt_sub = c_p2.selectbox(tr("مضمون", "Subject"), available_subs)
                tt_teacher = c_p3.selectbox(tr("استاد (Teacher)", "Teacher"), available_teachers)
                
                if st.button(tr("ٹائم ٹیبل محفوظ کریں", "Save Timetable")):
                    cursor.execute("INSERT INTO timetable (class, section, day, period, subject, teacher_id) VALUES (?, ?, ?, ?, ?, ?)", (tt_add_class, tt_add_sec, tt_day, tt_period, tt_sub, tt_teacher))
                    conn.commit()
                    st.success(tr("محفوظ ہو گیا!", "Saved!"))
                    st.rerun()
            else:
                if "No Subject" in available_subs[0]:
                    st.error(tr("پہلے اس کلاس کے لیے مضامین شامل کریں!", "Please add subjects for this class first!"))

        st.write("---")
        st.subheader(tr("ٹائم ٹیبل دیکھیں اور پرنٹ کریں", "View & Print Timetable"))
        v_mode = st.radio(tr("طریقہ انتخاب:", "View By:"), [tr("کلاس کے لحاظ سے", "Class-wise"), tr("استاد کے لحاظ سے", "Teacher-wise")], horizontal=True)

        if v_mode in ["کلاس کے لحاظ سے", "Class-wise"]:
            c_v1, c_v2 = st.columns(2)
            db_cls2 = pd.read_sql("SELECT class_name FROM sys_classes", conn)['class_name'].tolist()
            if not db_cls2: db_cls2 = classes_list
            tt_v_class = c_v1.selectbox(tr("کلاس منتخب کریں", "Select Class"), db_cls2, index=db_cls2.index(st.session_state.tt_sel_class) if st.session_state.tt_sel_class in db_cls2 else 0, key="tt_v_cls")
            
            db_sec2 = pd.read_sql(f"SELECT section_name FROM sys_sections WHERE class_name='{tt_v_class}'", conn)['section_name'].tolist()
            if not db_sec2: db_sec2 = ["A"]
            tt_v_sec = c_v2.selectbox(tr("سیکشن", "Section"), db_sec2, index=db_sec2.index(st.session_state.tt_sel_sec) if st.session_state.tt_sel_sec in db_sec2 else 0, key="tt_v_sec")

            if st.button("🗑️ " + tr("اس کلاس کا ٹائم ٹیبل ڈیلیٹ کریں", "Clear Timetable for this Class")):
                 cursor.execute("DELETE FROM timetable WHERE class=? AND section=?", (tt_v_class, tt_v_sec))
                 conn.commit()
                 st.rerun()

            tt_df = pd.read_sql(f"SELECT day, period, subject, teacher_id FROM timetable WHERE class='{tt_v_class}' AND section='{tt_v_sec}'", conn)
            if not tt_df.empty:
                tt_df = tt_df.drop_duplicates(subset=['day', 'period'], keep='last')
                tt_df['Display'] = tt_df['subject'] + "<br><span style='font-size:10px; color:#555;'>(" + tt_df['teacher_id'] + ")</span>"
                pivot_df = tt_df.pivot(index='day', columns='period', values='Display').fillna('-')
                
                days = [tr("روزانہ", "Daily"), tr("سوموار", "Monday"), tr("منگل", "Tuesday"), tr("بدھ", "Wednesday"), tr("جمعرات", "Thursday"), tr("جمعہ", "Friday"), tr("ہفتہ", "Saturday")]
                periods = [tr("پہلا پیریڈ", "1st Period"), tr("دوسرا پیریڈ", "2nd Period"), tr("تیسرا پیریڈ", "3rd Period"), tr("چوتھا پیریڈ", "4th Period"), tr("پانچواں پیریڈ", "5th Period"), tr("چھٹا پیریڈ", "6th Period"), tr("ساتواں پیریڈ", "7th Period"), tr("آٹھواں پیریڈ", "8th Period")]
                
                existing_days = [d for d in days if d in pivot_df.index]
                pivot_df = pivot_df.reindex(existing_days)
                existing_periods = [p for p in periods if p in pivot_df.columns]
                pivot_df = pivot_df[existing_periods]
                pivot_df.index.name = tr('دن / پیریڈ', 'Day / Period')

                t = {"align": "left", "dir": "ltr"} if st.session_state.ui_lang == "English" else {"align": "right", "dir": "rtl"}

                html_table = pivot_df.to_html(escape=False, border=1)
                html_table = html_table.replace('<table border="1" class="dataframe">', '<table style="width:100%; border-collapse: collapse; text-align: center; font-size: 14px; border: 2px solid #000;">')
                html_table = html_table.replace('<th>', f'<th style="background-color:#1a4f8b; color:white; border:1px solid #000; padding:10px; text-align:center;">')
                html_table = html_table.replace('<td>', f'<td style="border:1px solid #000; padding:10px; text-align:center;">')
                html_table = html_table.replace('<th>-', f'<th style="background-color:#1a4f8b; color:white; border:1px solid #000; padding:10px; text-align:center;">-')

                st.markdown(html_table, unsafe_allow_html=True)

                print_html = f"""
                <div style="width: 100%; font-family: Arial, sans-serif;" dir="{t['dir']}">
                <table style="width:100%; border:none; margin-bottom: 15px;">
                <tr>
                <td style="width: 15%; text-align: {t['align']}; vertical-align: middle;">{logo_base64_html}</td>
                <td style="width: 70%; text-align: center; vertical-align: middle;">
                <h2 style="margin: 0; font-size: 24px; color: #1a4f8b; text-transform: uppercase;">{school_name}</h2>
                <p style="margin: 4px 0; font-weight: bold; font-size: 12px;">{school_address}</p>
                <h3 style="margin: 10px 0 0 0; text-decoration: underline; font-weight: bold; font-size: 18px;">{tr('کلاس ٹائم ٹیبل', 'CLASS TIMETABLE')}</h3>
                <p style="margin: 5px 0 0 0; font-weight:bold; font-size: 14px;">{tt_v_class} ( {tt_v_sec} )</p>
                </td>
                <td style="width: 15%; text-align: right;"></td>
                </tr>
                </table>
                <div style="width:100%; display: flex; justify-content: center; margin-top:20px;" dir="{t['dir']}">
                {html_table}
                </div>
                </div>
                """
                if st.button("🖨️ " + tr("کلاس کا ٹائم ٹیبل پرنٹ کریں", "Print Class Timetable")):
                    print_button_js(print_html, tr("پرنٹ کریں", "Print Now"), landscape=True)
            else:
                st.info(tr("اس کلاس کا ٹائم ٹیبل ابھی نہیں بنایا گیا۔", "Timetable for this class is not created yet."))

        else: # Teacher-wise
            t_list_df = pd.read_sql("SELECT DISTINCT teacher_id FROM timetable", conn)
            if not t_list_df.empty:
                t_list = t_list_df['teacher_id'].tolist()
                sel_teacher = st.selectbox(tr("استاد منتخب کریں", "Select Teacher"), t_list)

                tt_df = pd.read_sql(f"SELECT day, period, subject, class, section FROM timetable WHERE teacher_id='{sel_teacher}'", conn)
                if not tt_df.empty:
                    tt_df = tt_df.drop_duplicates(subset=['day', 'period'], keep='last')
                    tt_df['Display'] = tt_df['subject'] + "<br><span style='font-size:10px; color:#555;'>(" + tt_df['class'] + " - " + tt_df['section'] + ")</span>"
                    pivot_df = tt_df.pivot(index='day', columns='period', values='Display').fillna('-')

                    days = [tr("روزانہ", "Daily"), tr("سوموار", "Monday"), tr("منگل", "Tuesday"), tr("بدھ", "Wednesday"), tr("جمعرات", "Thursday"), tr("جمعہ", "Friday"), tr("ہفتہ", "Saturday")]
                    periods = [tr("پہلا پیریڈ", "1st Period"), tr("دوسرا پیریڈ", "2nd Period"), tr("تیسرا پیریڈ", "3rd Period"), tr("چوتھا پیریڈ", "4th Period"), tr("پانچواں پیریڈ", "5th Period"), tr("چھٹا پیریڈ", "6th Period"), tr("ساتواں پیریڈ", "7th Period"), tr("آٹھواں پیریڈ", "8th Period")]

                    existing_days = [d for d in days if d in pivot_df.index]
                    pivot_df = pivot_df.reindex(existing_days)
                    existing_periods = [p for p in periods if p in pivot_df.columns]
                    pivot_df = pivot_df[existing_periods]
                    pivot_df.index.name = tr('دن / پیریڈ', 'Day / Period')

                    t = {"align": "left", "dir": "ltr"} if st.session_state.ui_lang == "English" else {"align": "right", "dir": "rtl"}

                    html_table = pivot_df.to_html(escape=False, border=1)
                    html_table = html_table.replace('<table border="1" class="dataframe">', '<table style="width:100%; border-collapse: collapse; text-align: center; font-size: 14px; border: 2px solid #000;">')
                    html_table = html_table.replace('<th>', f'<th style="background-color:#1a4f8b; color:white; border:1px solid #000; padding:10px; text-align:center;">')
                    html_table = html_table.replace('<td>', f'<td style="border:1px solid #000; padding:10px; text-align:center;">')
                    html_table = html_table.replace('<th>-', f'<th style="background-color:#1a4f8b; color:white; border:1px solid #000; padding:10px; text-align:center;">-')

                    st.markdown(html_table, unsafe_allow_html=True)

                    print_html = f"""
                    <div style="width: 100%; font-family: Arial, sans-serif;" dir="{t['dir']}">
                    <table style="width:100%; border:none; margin-bottom: 15px;">
                    <tr>
                    <td style="width: 15%; text-align: {t['align']}; vertical-align: middle;">{logo_base64_html}</td>
                    <td style="width: 70%; text-align: center; vertical-align: middle;">
                    <h2 style="margin: 0; font-size: 24px; color: #1a4f8b; text-transform: uppercase;">{school_name}</h2>
                    <p style="margin: 4px 0; font-weight: bold; font-size: 12px;">{school_address}</p>
                    <h3 style="margin: 10px 0 0 0; text-decoration: underline; font-weight: bold; font-size: 18px;">{tr('ٹیچر ٹائم ٹیبل', 'TEACHER TIMETABLE')}</h3>
                    <p style="margin: 5px 0 0 0; font-weight:bold; font-size: 14px;">{sel_teacher}</p>
                    </td>
                    <td style="width: 15%; text-align: right;"></td>
                    </tr>
                    </table>
                    <div style="width:100%; display: flex; justify-content: center; margin-top:20px;" dir="{t['dir']}">
                    {html_table}
                    </div>
                    </div>
                    """
                    if st.button("🖨️ " + tr("ٹیچر کا ٹائم ٹیبل پرنٹ کریں", "Print Teacher Timetable")):
                        print_button_js(print_html, tr("پرنٹ کریں", "Print Now"), landscape=True)
                else:
                    st.info(tr("اس ٹیچر کا ٹائم ٹیبل ابھی نہیں ملا۔", "No timetable found for this teacher."))
            else:
                st.info(tr("ابھی تک کوئی ٹیچر ٹائم ٹیبل میں شامل نہیں ہے۔", "No teachers in timetable yet."))

    elif sub_choice == "Lesson Plan":
        st.markdown("<div class='no-print'>", unsafe_allow_html=True)
        
        if 'lp_sel_class' not in st.session_state: st.session_state.lp_sel_class = classes_list[0]
        if 'lp_sel_sec' not in st.session_state: st.session_state.lp_sel_sec = "A"
        
        tab_add, tab_edit, tab_status, tab_del = st.tabs([
            "➕ " + tr("نیا لیسن پلان", "New Lesson Plan"), 
            "✏️ " + tr("ایڈٹ کریں", "Edit"),
            "✅ " + tr("سٹیٹس اپڈیٹ", "Update Status"),
            "🗑️ " + tr("ڈیلیٹ کریں", "Delete")
        ])
        
        available_teachers = pd.read_sql("SELECT name FROM staff", conn)['name'].tolist()
        if not available_teachers: available_teachers = ["No Teacher Found"]
        
        with tab_add:
            c_lp_top1, c_lp_top2, c_lp_type = st.columns(3)
            
            db_cls = pd.read_sql("SELECT class_name FROM sys_classes", conn)['class_name'].tolist()
            if not db_cls: db_cls = classes_list
            lp_class = c_lp_top1.selectbox(
                tr("کلاس", "Class"), 
                db_cls, 
                index=db_cls.index(st.session_state.lp_sel_class) if st.session_state.lp_sel_class in db_cls else 0,
                key="lp_cls"
            )
            db_sec = pd.read_sql(f"SELECT section_name FROM sys_sections WHERE class_name='{lp_class}'", conn)['section_name'].tolist()
            if not db_sec: db_sec = ["A"]
            lp_sec = c_lp_top2.selectbox(
                tr("سیکشن", "Section"), 
                db_sec, 
                index=db_sec.index(st.session_state.lp_sel_sec) if st.session_state.lp_sel_sec in db_sec else 0,
                key="lp_sec"
            )
            
            type_opts_ur = ["روزانہ", "ہفتہ وار", "ماہانہ", "سالانہ"]
            type_opts_en = ["Daily", "Weekly", "Monthly", "Yearly"]
            type_opts = type_opts_ur if st.session_state.ui_lang == "اردو" else type_opts_en
            lp_type = c_lp_type.selectbox(tr("پلان کی قسم", "Plan Type"), type_opts, key="lp_type_sel")
            
            if lp_class != st.session_state.lp_sel_class or lp_sec != st.session_state.lp_sel_sec:
                st.session_state.lp_sel_class = lp_class
                st.session_state.lp_sel_sec = lp_sec
                st.rerun()
            
            c_date1, c_date2 = st.columns(2)
            if lp_type in ["روزانہ", "Daily"]:
                lp_date_val = c_date1.date_input(tr("تاریخ منتخب کریں", "Select Date"), datetime.date.today(), key="lp_d_single")
                final_date_str = lp_date_val.strftime("%Y-%m-%d")
            else:
                lp_start_val = c_date1.date_input(tr("شروع کی تاریخ (Start Date)", "Start Date"), datetime.date.today(), key="lp_d_start")
                lp_end_val = c_date2.date_input(tr("ختم ہونے کی تاریخ (End Date)", "End Date"), datetime.date.today() + datetime.timedelta(days=7), key="lp_d_end")
                final_date_str = f"{lp_start_val.strftime('%Y-%m-%d')} to {lp_end_val.strftime('%Y-%m-%d')}"
            
            existing_lp_df = pd.read_sql(f"SELECT subject FROM lesson_plan WHERE date='{final_date_str}' AND class='{lp_class}' AND section='{lp_sec}'", conn)
            used_lp_subs = existing_lp_df['subject'].tolist() if not existing_lp_df.empty else []
            
            dyn_subs_lp_df = pd.read_sql(f"SELECT subject_name FROM sys_subjects WHERE class_name='{lp_class}' AND section_name='{lp_sec}'", conn)
            all_lp_subs = dyn_subs_lp_df['subject_name'].tolist() if not dyn_subs_lp_df.empty else ["کوئی مضمون نہیں / No Subject"]
            
            available_lp_subs = [s for s in all_lp_subs if used_lp_subs.count(s) < 2]
            
            with st.form("lesson_plan_form", clear_on_submit=True):
                if not available_lp_subs and "No Subject" not in all_lp_subs[0]:
                    st.info(tr("اس تاریخ / رینج کے لیے اس کلاس کے تمام مضامین کا لیسن پلان (2 بار) بن چکا ہے۔", "Lesson plans for all subjects are already created twice for this date/range."))
                    available_lp_subs = ["تمام مضامین شامل ہو چکے ہیں"]
                elif not available_lp_subs:
                    available_lp_subs = all_lp_subs
                
                c_lp4, c_lp5 = st.columns(2)
                lp_sub = c_lp4.selectbox(tr("مضمون", "Subject"), available_lp_subs, key="lp_sub")
                lp_teacher = c_lp5.selectbox(tr("استاد (Teacher)", "Teacher"), available_teachers, key="lp_teacher")
                
                lp_topic = st.text_input(tr("آج کا ٹاپک / سبق کی تفصیل", "Topic / Lesson Details"))
                lp_status = st.radio(tr("سٹیٹس", "Status"), [tr("جاری ہے", "In Progress"), tr("مکمل ہو گیا", "Completed")], index=0, horizontal=True)
                
                if st.form_submit_button(tr("ڈائری محفوظ کریں", "Save Lesson Plan")):
                    if lp_topic and "No Subject" not in lp_sub and "تمام مضامین" not in lp_sub:
                        cursor.execute("INSERT INTO lesson_plan (date, class, section, subject, teacher_id, topic, status, plan_type) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", 
                                       (final_date_str, lp_class, lp_sec, lp_sub, lp_teacher, lp_topic, lp_status, lp_type))
                        conn.commit()
                        st.success(tr("لیسن پلان محفوظ ہو گیا!", "Lesson plan saved!"))
                        st.rerun()
                    elif "No Subject" in lp_sub:
                        st.error(tr("پہلے اس کلاس کے لیے مضامین شامل کریں!", "Please add subjects for this class first!"))
                    elif "تمام مضامین" in lp_sub:
                        st.warning(tr("مزید مضامین باقی نہیں ہیں۔", "No more subjects left."))

        with tab_edit:
            st.markdown(f"### {tr('لیسن پلان میں تبدیلی کریں', 'Edit Lesson Plan')}")
            st.info(tr("تبدیلی کے لیے نیچے دی گئی لسٹ سے لیسن پلان کی ID (پہلا کالم) دیکھ کر یہاں لکھیں۔", "Enter the Lesson Plan ID (from the first column of the list below) to edit it."))
            
            c_e1, c_e2 = st.columns([1, 3])
            edit_lp_id_str = c_e1.text_input(tr("لیسن پلان ID درج کریں", "Enter Lesson Plan ID"), key="edit_lp_id_input")
            
            if edit_lp_id_str.isdigit() and int(edit_lp_id_str) > 0:
                edit_lp_id = int(edit_lp_id_str)
                lp_match = pd.read_sql(f"SELECT * FROM lesson_plan WHERE id={edit_lp_id}", conn)
                
                if not lp_match.empty:
                    lp_data = lp_match.iloc[0]
                    with st.form("edit_lesson_plan_form"):
                        c_e_lp2, c_e_lp3, c_e_lp_type = st.columns(3)
                        
                        db_cls_e = pd.read_sql("SELECT class_name FROM sys_classes", conn)['class_name'].tolist()
                        if not db_cls_e: db_cls_e = classes_list
                        e_lp_class = c_e_lp2.selectbox(tr("کلاس", "Class"), db_cls_e, index=db_cls_e.index(lp_data['class']) if lp_data['class'] in db_cls_e else 0, key="e_lp_cls")
                        
                        db_sec_e = pd.read_sql(f"SELECT section_name FROM sys_sections WHERE class_name='{e_lp_class}'", conn)['section_name'].tolist()
                        if not db_sec_e: db_sec_e = ["A"]
                        e_lp_sec = c_e_lp3.selectbox(tr("سیکشن", "Section"), db_sec_e, index=db_sec_e.index(lp_data['section']) if lp_data['section'] in db_sec_e else 0, key="e_lp_sec")
                        
                        curr_ptype = lp_data.get('plan_type', 'Daily' if st.session_state.ui_lang=="English" else "روزانہ")
                        if curr_ptype in type_opts_ur and st.session_state.ui_lang == "English": curr_ptype = type_opts_en[type_opts_ur.index(curr_ptype)]
                        elif curr_ptype in type_opts_en and st.session_state.ui_lang == "اردو": curr_ptype = type_opts_ur[type_opts_en.index(curr_ptype)]
                        pt_idx = type_opts.index(curr_ptype) if curr_ptype in type_opts else 0
                        e_lp_type = c_e_lp_type.selectbox(tr("پلان کی قسم", "Plan Type"), type_opts, index=pt_idx, key="e_lp_type")
                        
                        curr_date_str = lp_data['date']
                        if " to " in curr_date_str:
                            d_parts = curr_date_str.split(" to ")
                            try:
                                s_date = datetime.datetime.strptime(d_parts[0], "%Y-%m-%d").date()
                                e_date = datetime.datetime.strptime(d_parts[1], "%Y-%m-%d").date()
                            except:
                                s_date = datetime.date.today(); e_date = datetime.date.today()
                        else:
                            try: s_date = datetime.datetime.strptime(curr_date_str, "%Y-%m-%d").date()
                            except: s_date = datetime.date.today()
                            e_date = s_date
                        
                        c_e_d1, c_e_d2 = st.columns(2)
                        e_lp_date_start = c_e_d1.date_input(tr("شروع کی تاریخ / ڈیلی تاریخ", "Start Date / Daily Date"), s_date, key="e_lp_start")
                        e_lp_date_end = c_e_d2.date_input(tr("ختم ہونے کی تاریخ (اگر رینج ہو)", "End Date (if range)"), e_date, key="e_lp_end")
                        
                        c_e_lp4, c_e_lp5 = st.columns(2)
                        edit_dyn_subs_df = pd.read_sql(f"SELECT subject_name FROM sys_subjects WHERE class_name='{lp_data['class']}' AND section_name='{lp_data['section']}'", conn)
                        edit_available_subs = edit_dyn_subs_df['subject_name'].tolist() if not edit_dyn_subs_df.empty else [lp_data['subject']]
                        
                        e_lp_sub = c_e_lp4.selectbox(tr("مضمون", "Subject"), edit_available_subs, index=edit_available_subs.index(lp_data['subject']) if lp_data['subject'] in edit_available_subs else 0, key="e_lp_sub")
                        
                        t_idx = available_teachers.index(lp_data['teacher_id']) if lp_data['teacher_id'] in available_teachers else 0
                        e_lp_teacher = c_e_lp5.selectbox(tr("استاد (Teacher)", "Teacher"), available_teachers, index=t_idx, key="e_lp_teacher")
                        
                        e_lp_topic = st.text_input(tr("آج کا ٹاپک / سبق کی تفصیل", "Topic / Lesson Details"), value=lp_data['topic'], key="e_lp_topic")
                        
                        stat_opts_ur = ["جاری ہے", "مکمل ہو گیا"]
                        stat_opts_en = ["In Progress", "Completed"]
                        stat_opts = stat_opts_ur if st.session_state.ui_lang == "اردو" else stat_opts_en
                        
                        curr_stat = lp_data['status']
                        if curr_stat in stat_opts_ur and st.session_state.ui_lang == "English": curr_stat = stat_opts_en[stat_opts_ur.index(curr_stat)]
                        elif curr_stat in stat_opts_en and st.session_state.ui_lang == "اردو": curr_stat = stat_opts_ur[stat_opts_en.index(curr_stat)]
                            
                        s_idx = stat_opts.index(curr_stat) if curr_stat in stat_opts else 0
                        e_lp_status = st.radio(tr("سٹیٹس", "Status"), stat_opts, index=s_idx, horizontal=True, key="e_lp_status")
                        
                        if st.form_submit_button(tr("تبدیلیاں محفوظ کریں", "Save Changes")):
                            if e_lp_topic:
                                if e_lp_type in ["روزانہ", "Daily"]:
                                    final_e_date = e_lp_date_start.strftime("%Y-%m-%d")
                                else:
                                    final_e_date = f"{e_lp_date_start.strftime('%Y-%m-%d')} to {e_lp_date_end.strftime('%Y-%m-%d')}"
                                
                                cursor.execute("""
                                    UPDATE lesson_plan 
                                    SET date=?, class=?, section=?, subject=?, teacher_id=?, topic=?, status=?, plan_type=? 
                                    WHERE id=?
                                """, (final_e_date, e_lp_class, e_lp_sec, e_lp_sub, e_lp_teacher, e_lp_topic, e_lp_status, e_lp_type, edit_lp_id))
                                conn.commit()
                                st.success(tr("لیسن پلان کامیابی سے تبدیل ہو گیا!", "Lesson plan updated successfully!"))
                                st.rerun()
                else:
                    st.warning(tr("اس ID کا کوئی لیسن پلان موجود نہیں۔", "No lesson plan found with this ID."))

        with tab_status:
            st.markdown(f"### ✅ {tr('نامکمل لیسن پلانز کو مکمل کریں', 'Complete Pending Lesson Plans')}")
            st.info(tr("یہاں آپ ان تمام لیسن پلانز کو ایک ہی کلک میں 'مکمل' کر سکتے ہیں جو ابھی 'جاری ہیں' (In Progress)۔ ٹک لگائیں اور اپڈیٹ کا بٹن دبائیں۔", 
                       "Here you can mark 'In Progress' lesson plans as 'Completed' with a single click. Check the box and click Update."))
            
            pending_lp = pd.read_sql("SELECT id, date as Date, class as Class, section as Section, subject as Subject, teacher_id as Teacher, topic as Topic, status as Status FROM lesson_plan WHERE status IN ('In Progress', 'جاری ہے')", conn)
            
            if not pending_lp.empty:
                pending_lp.insert(0, 'Mark Completed', False)
                if st.session_state.ui_lang == "اردو":
                    pending_lp = pending_lp.rename(columns={'Date': 'تاریخ', 'Class': 'کلاس', 'Section': 'سیکشن', 'Subject': 'مضمون', 'Teacher': 'استاد', 'Topic': 'ٹاپک', 'Status': 'سٹیٹس'})
                
                edited_pending = st.data_editor(
                    pending_lp, 
                    hide_index=True, 
                    column_config={"Mark Completed": st.column_config.CheckboxColumn(tr("مکمل کریں", "Mark Complete"), default=False)}, 
                    disabled=["id", "Date", "تاریخ", "Class", "کلاس", "Section", "سیکشن", "Subject", "مضمون", "Teacher", "استاد", "Topic", "ٹاپک", "Status", "سٹیٹس"], 
                    use_container_width=True, 
                    key="pending_lp_editor"
                )
                
                if st.button(tr("✅ منتخب لیسن پلانز کو مکمل کریں (Update Status)", "✅ Mark Selected as Completed"), type="primary"):
                    selected_ids = edited_pending[edited_pending['Mark Completed'] == True]['id'].tolist()
                    if selected_ids:
                        comp_str = "Completed" if st.session_state.ui_lang == "English" else "مکمل ہو گیا"
                        for pid in selected_ids:
                            cursor.execute("UPDATE lesson_plan SET status=? WHERE id=?", (comp_str, pid))
                        conn.commit()
                        st.success(tr(f"{len(selected_ids)} لیسن پلانز کامیابی سے مکمل کر دیے گئے! پرفارمنس اپڈیٹ ہو گئی۔", f"{len(selected_ids)} lesson plans marked as completed successfully! Performance updated."))
                        st.rerun()
                    else:
                        st.warning(tr("کوئی لیسن پلان منتخب نہیں کیا گیا۔ خانے میں ٹک لگائیں۔", "No lesson plan selected. Please check a box first."))
            else:
                st.success(tr("بہترین! اس وقت کوئی بھی لیسن پلان نامکمل نہیں ہے۔ سب مکمل ہو چکے ہیں۔", "Excellent! There are no pending lesson plans. All are completed."))

        with tab_del:
            st.markdown(f"### 🗑️ {tr('لیسن پلان ڈیلیٹ کریں', 'Delete Lesson Plan')}")
            
            del_mode = st.radio(tr("ڈیلیٹ کرنے کا طریقہ منتخب کریں:", "Select Delete Method:"), 
                                [tr("سنگل لیسن پلان ڈیلیٹ کریں", "Delete Single Lesson Plan"), 
                                 tr("تمام لیسن پلانز ڈیلیٹ کریں (مکمل صفائی)", "Delete All Lesson Plans (Bulk Clear)")])
            
            st.write("---")
            
            if "Single" in del_mode or "سنگل" in del_mode:
                c_d1, c_d2 = st.columns([1, 2])
                del_id_str = c_d1.text_input(tr("ڈیلیٹ کرنے کے لیے لیسن پلان کی ID درج کریں", "Enter Lesson Plan ID to Delete"), key="del_lp_id_input")
                
                if c_d1.button("🗑️ " + tr("ڈیلیٹ کریں", "Delete"), key="btn_del_single"):
                    if del_id_str.isdigit():
                        del_id = int(del_id_str)
                        cursor.execute("SELECT id FROM lesson_plan WHERE id=?", (del_id,))
                        if cursor.fetchone():
                            cursor.execute("DELETE FROM lesson_plan WHERE id=?", (del_id,))
                            conn.commit()
                            st.success(tr("لیسن پلان کامیابی سے ڈیلیٹ ہو گیا!", "Lesson plan deleted successfully!"))
                            st.rerun()
                        else:
                            st.error(tr("اس ID کا کوئی لیسن پلان موجود نہیں۔", "No lesson plan found with this ID."))
                    else:
                        st.warning(tr("براہ کرم درست ID درج کریں۔", "Please enter a valid ID."))
                        
            elif "All" in del_mode or "تمام" in del_mode:
                st.error(tr("⚠️ انتباہ: کیا آپ واقعی تمام لیسن پلانز کا ریکارڈ ڈیلیٹ کرنا چاہتے ہیں؟ یہ عمل واپس نہیں ہو سکتا۔", 
                            "⚠️ WARNING: Are you sure you want to delete ALL lesson plans? This action cannot be undone."))
                confirm_del = st.checkbox(tr("ہاں، میں تمام ریکارڈ ڈیلیٹ کرنا چاہتا ہوں", "Yes, I want to delete all records"))
                
                if st.button("🚨 " + tr("تمام ریکارڈ ڈیلیٹ کریں", "Delete All Records"), key="btn_del_all"):
                    if confirm_del:
                        cursor.execute("DELETE FROM lesson_plan")
                        conn.commit()
                        st.success(tr("تمام لیسن پلانز کامیابی سے ڈیلیٹ ہو گئے!", "All lesson plans deleted successfully!"))
                        st.rerun()
                    else:
                        st.warning(tr("پہلے تصدیقی چیک باکس پر کلک کریں۔", "Please click the confirmation checkbox first."))

        st.write("---")
        st.markdown(f"#### 📖 {tr('محفوظ شدہ لیسن پلانز (آخری 100)', 'Saved Lesson Plans (Last 100)')}")
        
        lp_df = pd.read_sql("SELECT id as ID, date as Date, plan_type as 'Plan Type', class as Class, section as Section, subject as Subject, teacher_id as Teacher, topic as Topic, status as Status FROM lesson_plan ORDER BY id DESC LIMIT 100", conn)
        
        if st.session_state.ui_lang == "اردو":
            lp_df = lp_df.rename(columns={"Date": "تاریخ", "Plan Type": "قسم", "Class": "کلاس", "Section": "سیکشن", "Subject": "مضمون", "Teacher": "استاد", "Topic": "ٹاپک", "Status": "سٹیٹس"})
            
        st.dataframe(lp_df, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
    elif sub_choice in ["Exams & Marks", "امتحانات / مارکس"]:
        st.markdown("<div class='no-print'>", unsafe_allow_html=True)
        
        if 'ex_sel_class' not in st.session_state: st.session_state.ex_sel_class = classes_list[0]
        if 'ex_sel_sec' not in st.session_state: st.session_state.ex_sel_sec = "A"
        if 'ex_sel_exam' not in st.session_state: st.session_state.ex_sel_exam = None
        
        with st.expander(tr("1. نیا امتحان بنائیں (Create Exam)", "1. Create Exam")):
            c_ex1, c_ex2 = st.columns(2)
            exam_name = c_ex1.text_input(tr("امتحان کا نام (مثال: First Term 2026)", "Exam Name (e.g., First Term 2026)"))
            exam_date = c_ex2.date_input(tr("شروع ہونے کی تاریخ", "Start Date"))
            if st.button(tr("امتحان محفوظ کریں", "Save Exam")):
                if exam_name:
                    try: cursor.execute("INSERT INTO exams (exam_name, start_date) VALUES (?, ?)", (exam_name, exam_date.strftime("%Y-%m-%d"))); conn.commit(); st.success("Exam created!"); st.rerun()
                    except: st.error("Exam already exists.")

        with st.expander(tr("2. طلباء کے نمبرز کی انٹری (Enter Marks)", "2. Enter Marks"), expanded=True):
            available_exams = pd.read_sql("SELECT exam_name FROM exams", conn)['exam_name'].tolist()
            if available_exams:
                if not st.session_state.ex_sel_exam or st.session_state.ex_sel_exam not in available_exams:
                    st.session_state.ex_sel_exam = available_exams[0]
                    
                c_em1, c_em2, c_em3 = st.columns(3)
                em_exam = c_em1.selectbox(tr("امتحان", "Exam"), available_exams, index=available_exams.index(st.session_state.ex_sel_exam), key="em_exam")
                
                db_cls = pd.read_sql("SELECT class_name FROM sys_classes", conn)['class_name'].tolist()
                if not db_cls: db_cls = classes_list
                em_class = c_em2.selectbox(tr("کلاس", "Class"), db_cls, index=db_cls.index(st.session_state.ex_sel_class) if st.session_state.ex_sel_class in db_cls else 0, key="em_cls")
                
                db_sec = pd.read_sql(f"SELECT section_name FROM sys_sections WHERE class_name='{em_class}'", conn)['section_name'].tolist()
                if not db_sec: db_sec = ["A"]
                em_sec = c_em3.selectbox(tr("سیکشن", "Section"), db_sec, index=db_sec.index(st.session_state.ex_sel_sec) if st.session_state.ex_sel_sec in db_sec else 0, key="em_sec")
                
                if em_exam != st.session_state.ex_sel_exam or em_class != st.session_state.ex_sel_class or em_sec != st.session_state.ex_sel_sec:
                    st.session_state.ex_sel_exam = em_exam
                    st.session_state.ex_sel_class = em_class
                    st.session_state.ex_sel_sec = em_sec
                    st.rerun()
                
                existing_marks_df = pd.read_sql(f"SELECT DISTINCT subject FROM exam_marks WHERE exam_name='{em_exam}' AND reg_id IN (SELECT reg_id FROM students WHERE class='{em_class}' AND section='{em_sec}')", conn)
                used_ex_subs = existing_marks_df['subject'].tolist() if not existing_marks_df.empty else []
                
                dyn_subs_ex_df = pd.read_sql(f"SELECT subject_name FROM sys_subjects WHERE class_name='{em_class}' AND section_name='{em_sec}'", conn)
                all_ex_subs = dyn_subs_ex_df['subject_name'].tolist() if not dyn_subs_ex_df.empty else ["کوئی مضمون نہیں / No Subject"]
                
                available_ex_subs = [s for s in all_ex_subs if s not in used_ex_subs]
                
                with st.form("marks_entry_form"):
                    if not available_ex_subs and "No Subject" not in all_ex_subs[0]:
                        st.info(tr("اس کلاس کے تمام مضامین کا رزلٹ اس امتحان کے لیے بن چکا ہے۔", "Marks for all subjects have been entered for this class in this exam."))
                        available_ex_subs = ["تمام مضامین شامل ہو چکے ہیں"]
                    elif not available_ex_subs:
                        available_ex_subs = all_ex_subs
                        
                    c_em4, c_em5 = st.columns(2)
                    em_sub = c_em4.selectbox("Subject", available_ex_subs, key="em_sub")
                    tot_marks = c_em5.number_input(tr("اس مضمون کے کل نمبر (Total Marks)", "Total Marks for this subject"), min_value=1.0, value=100.0)
                    
                    exam_students = pd.read_sql(f"SELECT reg_id, name, name_en FROM students WHERE class='{em_class}' AND section='{em_sec}' AND status='Active'", conn)
                    
                    if not exam_students.empty and "No Subject" not in em_sub and "تمام مضامین" not in em_sub:
                        marks_dict = {}
                        for _, es in exam_students.iterrows():
                            def_val = 0.0
                            d_name = get_disp_val(es['name'], es.get('name_en'))
                            c_mark1, c_mark2 = st.columns([2, 1])
                            c_mark1.markdown(f"<div style='padding-top:10px;'>**{d_name}** (Reg: {es['reg_id']})</div>", unsafe_allow_html=True)
                            
                            marks_dict[es['reg_id']] = c_mark2.text_input(tr("حاصل کردہ نمبر", "Obtained Marks"), value="", key=f"mark_{es['reg_id']}", label_visibility="collapsed")
                        
                        if st.form_submit_button(tr("تمام نمبرز محفوظ کریں", "Save All Marks")):
                            for r_id, val_in in marks_dict.items():
                                try: obt_m = float(val_in)
                                except: obt_m = 0.0
                                if obt_m > tot_marks: obt_m = tot_marks
                                if obt_m < 0: obt_m = 0.0
                                cursor.execute("INSERT INTO exam_marks (exam_name, reg_id, subject, total_marks, obtained_marks) VALUES (?, ?, ?, ?, ?)", (em_exam, r_id, em_sub, tot_marks, obt_m))
                            conn.commit()
                            st.success(tr("پوری کلاس کے نمبرز کامیابی سے محفوظ ہو گئے!", "Marks saved successfully for the whole class!"))
                            st.rerun()
                    elif "No Subject" in em_sub:
                        st.warning(tr("اس کلاس کے لیے کوئی مضمون شامل نہیں کیا گیا۔", "No subject added for this class."))
                        st.form_submit_button("Ok", disabled=True)
                    elif "تمام مضامین" in em_sub:
                         st.form_submit_button("Ok", disabled=True)
            else:
                 st.info(tr("پہلے کوئی امتحان بنائیں۔", "Please create an exam first."))

    elif sub_choice in ["Result Card", "رزلٹ کارڈ"]:
        st.markdown("<div class='no-print'>", unsafe_allow_html=True)
        available_exams_res = pd.read_sql("SELECT exam_name FROM exams", conn)['exam_name'].tolist()
        
        if available_exams_res:
            st.markdown(f"### 📄 {tr('رزلٹ کارڈ جنریٹر', 'Result Card Generator')}")
            
            rc_exam = st.selectbox(tr("امتحان منتخب کریں", "Select Exam for Result"), available_exams_res)
            st.write("---")
            
            gen_mode = st.radio(tr("رزلٹ کارڈ کس کا بنانا ہے؟", "Generate result for:"), 
                                [tr("سنگل طالب علم", "Single Student"), 
                                 tr("پوری کلاس", "Whole Class"), 
                                 tr("پورا سکول", "Whole School")], horizontal=True)
            
            students_to_print = pd.DataFrame()
            
            if "Single" in gen_mode or "سنگل" in gen_mode:
                rc_reg = st.text_input(tr("طالب علم کا رول نمبر لکھیں", "Enter Student Reg No"))
                if rc_reg:
                    students_to_print = pd.read_sql(f"SELECT * FROM students WHERE reg_id='{rc_reg}'", conn)
            
            elif "Class" in gen_mode or "کلاس" in gen_mode:
                c_rc1, c_rc2 = st.columns(2)
                db_cls = pd.read_sql("SELECT class_name FROM sys_classes", conn)['class_name'].tolist()
                if not db_cls: db_cls = classes_list
                rc_cls = c_rc1.selectbox(tr("کلاس منتخب کریں", "Select Class"), db_cls)
                db_sec = pd.read_sql(f"SELECT section_name FROM sys_sections WHERE class_name='{rc_cls}'", conn)['section_name'].tolist()
                if not db_sec: db_sec = ["A"]
                rc_sec = c_rc2.selectbox(tr("سیکشن", "Section"), db_sec)
                students_to_print = pd.read_sql(f"SELECT * FROM students WHERE class='{rc_cls}' AND section='{rc_sec}' AND status='Active'", conn)
                
            elif "School" in gen_mode or "سکول" in gen_mode:
                students_to_print = pd.read_sql("SELECT * FROM students WHERE status='Active'", conn)
                st.info(tr("یہ پورے سکول کے تمام طلباء کے رزلٹ کارڈ ایک ساتھ بنائے گا۔ اس میں تھوڑا وقت لگ سکتا ہے۔", "This will generate result cards for ALL students in the school. It may take some time."))
                
            btn_result = st.button(tr("رزلٹ کارڈز جنریٹ کریں", "Generate Result Cards"), type="primary", use_container_width=True)
            
            if btn_result:
                if not students_to_print.empty:
                    t = {"align": "left", "dir": "ltr"} if st.session_state.ui_lang == "English" else {"align": "right", "dir": "rtl"}
                    combined_html = f"<div style='width: 100%;' dir='{t['dir']}'>"
                    
                    cards_generated = 0
                    progress_bar = st.progress(0)
                    total_stu = len(students_to_print)
                    
                    for idx, s_row in students_to_print.iterrows():
                        rc_reg_curr = s_row['reg_id']
                        marks_df = pd.read_sql(f"SELECT subject as 'Subject', total_marks as 'Total', obtained_marks as 'Obtained' FROM exam_marks WHERE exam_name='{rc_exam}' AND reg_id='{rc_reg_curr}'", conn)
                        
                        if not marks_df.empty:
                            grand_total = marks_df['Total'].sum()
                            grand_obtained = marks_df['Obtained'].sum()
                            percentage = (grand_obtained / grand_total) * 100 if grand_total > 0 else 0
                            
                            if percentage >= 80: grade = "A+"
                            elif percentage >= 70: grade = "A"
                            elif percentage >= 60: grade = "B"
                            elif percentage >= 50: grade = "C"
                            elif percentage >= 40: grade = "D"
                            else: grade = "Fail"
                            
                            # 🟢 یہ ہے محفوظ طریقہ (فیصد کو پہلے سٹرنگ میں بدل لیا ہے تاکہ ایرر نہ آئے)
                            perc_str = f"{percentage:.2f}%"
                            
                            marks_rows = ""
                            for _, m_row in marks_df.iterrows():
                                marks_rows += f"<tr><td style='border:1px solid black; padding:6px; font-size:12px;'>{m_row['Subject']}</td><td style='border:1px solid black; padding:6px; text-align:center; font-size:12px;'>{m_row['Total']}</td><td style='border:1px solid black; padding:6px; text-align:center; font-size:12px;'>{m_row['Obtained']}</td></tr>"
                            
                            photo_data = s_row.get('photo', None)
                            student_photo_html = '<div style="width:110px; height:130px; border:2px solid #000; text-align:center; line-height:130px; font-size:12px; background:#f9f9f9; color:#999; margin:0 auto;">Photo</div>'
                            if photo_data:
                                try:
                                    b64_photo = base64.b64encode(photo_data).decode()
                                    student_photo_html = f'<img src="data:image/jpeg;base64,{b64_photo}" style="width:110px; height:130px; object-fit:cover; border:2px solid #000; display:block !important; visibility:visible !important; margin:0 auto;">'
                                except: pass
                            
                            logo_td_content = f'<div style="text-align:{t["align"]}; padding-right: 15px;">{logo_base64_html}</div>'
                            photo_td_content = f'<div style="text-align:{"right" if t["align"]=="left" else "left"}; padding-left: 15px;">{student_photo_html}</div>'
                            
                            raw_g = str(s_row.get('g_type', 'Father'))
                            gender_val = str(s_row.get('gender', 'Boy'))
                            try: rel_str = get_relation_card_label(gender_val, raw_g)
                            except: rel_str = "S/O" if gender_val == "Boy" else "D/O"
                            
                            try: d_name = get_disp_val(s_row['name'], s_row.get('name_en'))
                            except: d_name = s_row['name']
                            try: d_fname = get_disp_val(s_row['fname'], s_row.get('fname_en'))
                            except: d_fname = s_row['fname']
                            
                            res_html = f"""
                            <div style="border: 4px solid black; padding: 15px; width: 100%; max-width: 700px; margin: 0 auto; font-family: 'Arial', sans-serif; background-color: white; color: black; box-sizing: border-box; page-break-inside: avoid;">
                                <table style="width: 100%; border: none; margin-bottom: 10px;">
                                    <tr>
                                        <td style="width: 25%; text-align: center; vertical-align: middle;">{photo_td_content if st.session_state.ui_lang == "اردو" else logo_td_content}</td>
                                        <td style="width: 50%; text-align: center; vertical-align: middle;">
                                            <h1 style="margin: 0; font-size: 26px; color: #1a4f8b; font-weight: bold;">{school_name.upper() if 'school_name' in locals() else 'SCHOOL NAME'}</h1>
                                            <p style="margin: 3px 0; font-size: 13px; font-weight: bold;">{school_address if 'school_address' in locals() else ''}</p>
                                            <h2 style="margin: 10px 0 5px 0; font-size: 18px; color: #1a4f8b; text-decoration: underline;">{tr('نتیجہ (Progress Report)', 'Progress Report')}</h2>
                                            <h3 style="margin: 5px 0 10px 0; font-size: 15px; color: #333;">{rc_exam}</h3>
                                        </td>
                                        <td style="width: 25%; text-align: center; vertical-align: middle;">{logo_td_content if st.session_state.ui_lang == "اردو" else photo_td_content}</td>
                                    </tr>
                                </table>
                                <table style="width: 100%; border-collapse: collapse; margin-bottom: 15px; font-size: 13px; font-weight: bold;">
                                    <tr>
                                        <td style="border: 2px solid black; padding: 6px; width: 20%; background-color: #f2f2f2; text-align:{t['align']};">{tr('داخلہ نمبر:', 'Reg No:')}</td>
                                        <td style="border: 2px solid black; padding: 6px; width: 30%; text-align:{t['align']};">{rc_reg_curr}</td>
                                        <td style="border: 2px solid black; padding: 6px; width: 20%; background-color: #f2f2f2; text-align:{t['align']};">{tr('کلاس/سیکشن:', 'Class/Sec:')}</td>
                                        <td style="border: 2px solid black; padding: 6px; width: 30%; text-align:{t['align']};">{s_row['class']} ( {s_row['section']} )</td>
                                    </tr>
                                    <tr>
                                        <td style="border: 2px solid black; padding: 6px; background-color: #f2f2f2; text-align:{t['align']};">{tr('نام:', 'Name:')}</td>
                                        <td colspan="3" style="border: 2px solid black; padding: 6px; text-align:{t['align']};">{d_name} ({rel_str} {d_fname})</td>
                                    </tr>
                                </table>
                                <table style="width: 100%; border-collapse: collapse; margin-bottom: 15px; font-size: 13px;">
                                    <tr style="background-color: #e6e6e6;">
                                        <th style="border: 2px solid black; padding: 8px; width: 50%; text-align: {t['align']}; font-weight:bold;">{tr('مضمون', 'Subject')}</th>
                                        <th style="border: 2px solid black; padding: 8px; width: 25%; text-align: center; font-weight:bold;">{tr('کل نمبر', 'Total Marks')}</th>
                                        <th style="border: 2px solid black; padding: 8px; width: 25%; text-align: center; font-weight:bold;">{tr('حاصل کردہ نمبر', 'Obtained Marks')}</th>
                                    </tr>
                                    {marks_rows}
                                </table>
                                <table style="width: 100%; border-collapse: collapse; margin-bottom: 30px; font-size: 13px; font-weight: bold; text-align: center;">
                                    <tr>
                                        <td style="border: 3px solid black; padding: 8px; width: 25%;">{tr('کل نمبر (Total Marks)', 'Total Marks')}: {grand_total}</td>
                                        <td style="border: 3px solid black; padding: 8px; width: 25%;">{tr('حاصل کردہ (Obtained)', 'Obtained')}: {grand_obtained}</td>
                                        <td style="border: 3px solid black; padding: 8px; width: 25%;">{tr('فیصد (Percentage)', 'Percentage')}: {perc_str}</td>
                                        <td style="border: 3px solid black; padding: 8px; width: 25%; color: #1a4f8b;">{tr('گریڈ (Grade)', 'Grade')}: {grade}</td>
                                    </tr>
                                </table>
                                <table style="width: 100%; border: none; margin-top: 40px; font-size: 13px;">
                                    <tr>
                                        <td style="text-align: {t['align']}; width: 33%;">___________________<br><br>{tr('پرنسپل کے دستخط', 'Principal Sign')}</td>
                                        <td style="text-align: center; width: 34%;">___________________<br><br>{tr('دستخط والدین', 'Parent Sign')}</td>
                                        <td style="text-align: {'left' if st.session_state.ui_lang == 'اردو' else 'right'}; width: 33%;">___________________<br><br>{tr('دستخط کلاس ٹیچر', 'Class Teacher Sign')}</td>
                                    </tr>
                                </table>
                            </div>
                            <div style="page-break-after: always; height: 1px;"></div>
                            """
                            combined_html += res_html
                            cards_generated += 1
                            
                        progress_bar.progress(min((idx + 1) / total_stu, 1.0))
                            
                    combined_html += "</div>"
                    
                    if cards_generated > 0:
                        try: print_button_js(combined_html, tr(f"{cards_generated} رزلٹ کارڈز پرنٹ کریں", f"Print {cards_generated} Result Cards"), landscape=False)
                        except: st.components.v1.html(combined_html, height=600, scrolling=True)
                    else:
                        st.warning(tr("منتخب شدہ طلباء کے لیے اس امتحان کا کوئی رزلٹ نہیں ملا۔", "No results found for the selected students in this exam."))
                else:
                    st.error(tr("کوئی طالب علم نہیں ملا۔", "No student found."))
        else:
            st.info(tr("پہلے کوئی امتحان بنائیں۔", "Please create an exam first."))

    elif sub_choice in ["Promotion System", "پروموشن سسٹم"]:
        st.markdown("<div class='no-print'>", unsafe_allow_html=True)
        st.info(tr("یہاں سے آپ طلباء کو اگلی کلاس میں پرموٹ (Promote) کر سکتے ہیں، فیل طلباء کو اسی کلاس میں روک سکتے ہیں، یا سکول چھوڑنے والوں کا سٹیٹس تبدیل کر سکتے ہیں۔", "Here you can promote students to the next class, hold failed students, or update the status of those who have left."))
        
        try: cursor.execute("ALTER TABLE students ADD COLUMN status TEXT DEFAULT 'Active'")
        except: pass
        conn.commit()
        
        c_prom1, c_prom2 = st.columns(2)
        db_cls = pd.read_sql("SELECT class_name FROM sys_classes", conn)['class_name'].tolist()
        if not db_cls: db_cls = classes_list
        prom_class = c_prom1.selectbox(tr("موجودہ کلاس منتخب کریں", "Select Current Class"), db_cls)
        
        db_sec = pd.read_sql(f"SELECT section_name FROM sys_sections WHERE class_name='{prom_class}'", conn)['section_name'].tolist()
        if not db_sec: db_sec = ["A"]
        prom_sec = c_prom2.selectbox(tr("موجودہ سیکشن", "Current Section"), db_sec)
        
        stu_to_promote = pd.read_sql(f"SELECT reg_id, name, fname FROM students WHERE class='{prom_class}' AND section='{prom_sec}' AND status='Active'", conn)
        
        if not stu_to_promote.empty:
            stu_to_promote.insert(0, 'Select', True)
            if st.session_state.ui_lang == "اردو":
                stu_to_promote = stu_to_promote.rename(columns={'reg_id': 'رول نمبر', 'name': 'نام', 'fname': 'ولدیت'})
                
            st.markdown(f"#### 📋 {tr('اس کلاس کے طلباء', 'Students of this class')}")
            edited_prom_df = st.data_editor(
                stu_to_promote,
                hide_index=True,
                column_config={"Select": st.column_config.CheckboxColumn(tr("منتخب کریں", "Select"), default=True)},
                disabled=["reg_id", "رول نمبر", "name", "نام", "fname", "ولدیت"],
                use_container_width=True
            )
            
            st.write("---")
            st.markdown(f"#### ⚙️ {tr('ایکشن منتخب کریں', 'Select Action')}")
            
            action_type = st.radio(tr("ان طلباء کے ساتھ کیا کرنا ہے؟", "What to do with selected students?"),
                                   [tr("اگلی کلاس میں پرموٹ کریں (Promote)", "Promote to Next Class"),
                                    tr("فارغ التحصیل / سکول چھوڑ گئے (Mark as Left/Graduated)", "Mark as Left/Graduated")], horizontal=True)
            
            if "Promote" in action_type or "پرموٹ" in action_type:
                c_act1, c_act2 = st.columns(2)
                next_class = c_act1.selectbox(tr("اگلی کلاس (جس میں بھیجنا ہے)", "Next Class (Target)"), db_cls)
                db_sec_next = pd.read_sql(f"SELECT section_name FROM sys_sections WHERE class_name='{next_class}'", conn)['section_name'].tolist()
                if not db_sec_next: db_sec_next = ["A"]
                next_sec = c_act2.selectbox(tr("اگلا سیکشن", "Next Section"), db_sec_next)
                
                if st.button(tr("✅ منتخب طلباء کو پرموٹ کریں", "✅ Promote Selected Students"), type="primary"):
                    sel_col = 'Select'
                    reg_col = 'رول نمبر' if st.session_state.ui_lang == "اردو" else 'reg_id'
                    selected_regs = edited_prom_df[edited_prom_df[sel_col] == True][reg_col].tolist()
                    
                    if selected_regs:
                        for r_id in selected_regs:
                            cursor.execute("UPDATE students SET class=?, section=? WHERE reg_id=?", (next_class, next_sec, r_id))
                        conn.commit()
                        st.success(tr(f"{len(selected_regs)} طلباء کو کامیابی سے {next_class} ({next_sec}) میں پرموٹ کر دیا گیا! (باقی طلباء اسی کلاس میں موجود رہیں گے)", f"Successfully promoted {len(selected_regs)} students to {next_class} ({next_sec})! (Unselected students remain in the current class)"))
                        st.rerun()
                    else:
                        st.warning(tr("کوئی طالب علم منتخب نہیں کیا گیا۔", "No student selected."))
            
            else:
                leave_reason = st.selectbox(tr("سکول چھوڑنے کی وجہ", "Reason for leaving"), [tr("تعلیم مکمل کر لی (Graduated)", "Completed Education (Graduated)"), tr("سکول چھوڑ دیا (Left School)", "Left School"), tr("نکال دیا گیا (Expelled)", "Expelled")])
                
                if st.button(tr("🛑 منتخب طلباء کا سٹیٹس تبدیل کریں", "🛑 Update Status of Selected Students"), type="primary"):
                    sel_col = 'Select'
                    reg_col = 'رول نمبر' if st.session_state.ui_lang == "اردو" else 'reg_id'
                    selected_regs = edited_prom_df[edited_prom_df[sel_col] == True][reg_col].tolist()
                    
                    if selected_regs:
                        leave_val = "Graduated" if "Graduated" in leave_reason or "مکمل" in leave_reason else ("Left" if "Left" in leave_reason or "چھوڑ" in leave_reason else "Expelled")
                        for r_id in selected_regs:
                            cursor.execute("UPDATE students SET status=? WHERE reg_id=?", (leave_val, r_id))
                        conn.commit()
                        st.success(tr(f"{len(selected_regs)} طلباء کا سٹیٹس کامیابی سے '{leave_reason}' کر دیا گیا ہے۔ یہ طلباء اب ایکٹو ریکارڈ سے ہٹا دیے گئے ہیں۔", f"Successfully updated status of {len(selected_regs)} students to '{leave_reason}'. They are now removed from active records."))
                        st.rerun()
                    else:
                        st.warning(tr("کوئی طالب علم منتخب نہیں کیا گیا۔", "No student selected."))
                        
        else:
            st.info(tr("اس کلاس میں کوئی ایکٹو طالب علم موجود نہیں۔", "No active students found in this class."))
        st.markdown("</div>", unsafe_allow_html=True)

# ================= امتحانی جوابی کاپی (Exam Answer Sheet) =================
    elif sub_choice in ["Exam Answer Sheet", "امتحانی جوابی کاپی"]:
        st.markdown(f"### 📝 {tr('امتحانی جوابی کاپی (Answer Sheet)', 'Exam Answer Sheet')}")
        st.write(tr("یہاں سے آپ پنجاب بورڈ کے پیٹرن پر پروفیشنل امتحانی کاپی (لوگو اور واٹر مارک کے ساتھ) جنریٹ اور پرنٹ کر سکتے ہیں۔", "Generate and print professional exam answer sheets based on the Punjab Board pattern."))
        
        is_eng = st.session_state.ui_lang == "English"
        t_dir = "ltr" if is_eng else "rtl"
        t_align = "left" if is_eng else "right"
        t_align_opp = "right" if is_eng else "left"
        
        # 🟢 زبان کے لحاظ سے تمام لیبلز اور فونٹس سیٹ کیے گئے ہیں
        if is_eng:
            font_css = ""
            f_family = "'Arial', sans-serif"
            sheet_lbl = "EXAM ANSWER SHEET"
            inv_sig_lbl = "Sig. of Invigilator"
            st_name_lbl = "Student Name:"
            roll_no_lbl = "Roll No:"
            cls_sec_lbl = "Class & Sec:"
            subject_lbl = "Subject:"
            date_lbl = "Date:"
            tot_pages_lbl = "Total Pages Used:"
            exam_use_lbl = "Examiner's<br>Use Only"
            tot_lbl = "TOTAL"
            obj_sec_lbl = "OBJECTIVE SECTION (MCQs)"
            subj_sec_lbl = "SUBJECTIVE SECTION"
        else:
            font_css = "<style>@import url('https://fonts.googleapis.com/css2?family=Noto+Nastaliq+Urdu:wght@400;700&display=swap');</style>"
            f_family = "'Jameel Noori Nastaliq', 'Noto Nastaliq Urdu', 'Nafees Web Naskh', Arial, sans-serif"
            sheet_lbl = "امتحانی جوابی کاپی"
            inv_sig_lbl = "دستخط نگرانِ امتحان"
            st_name_lbl = "طالب علم کا نام:"
            roll_no_lbl = "رول نمبر:"
            cls_sec_lbl = "کلاس اور سیکشن:"
            subject_lbl = "مضمون:"
            date_lbl = "تاریخ:"
            tot_pages_lbl = "کل صفحات:"
            exam_use_lbl = "صرف ممتحن<br>کے لیے"
            tot_lbl = "کل نمبر"
            obj_sec_lbl = "معروضی حصہ (MCQs)"
            subj_sec_lbl = "انشائیہ حصہ"
        
        c_ex1, c_ex2, c_ex3 = st.columns(3)
        exam_title = c_ex1.text_input(tr("امتحان کا نام (Exam Title)", "Exam Title"), value="First Term Examination 2026" if is_eng else "پہلی ششماہی امتحان 2026")
        mcq_count = c_ex2.number_input(tr("MCQs کی تعداد (0=صرف لائنیں)", "Number of MCQs (0 for only lines)"), min_value=0, max_value=40, value=15)
        subj_count = c_ex3.number_input(tr("انشائیہ سوالات کی تعداد", "Number of Subjective Questions"), min_value=1, max_value=15, value=8)
        
        if st.button(tr("جوابی کاپی جنریٹ کریں", "Generate Answer Sheet"), type="primary"):
            school_n_doc = school_name.upper() if school_name else "DAR UL KHADIJA SCHOOL SYSTEM"
            watermark_html = f"""<div style="position: absolute; top: 0; left: 0; right: 0; bottom: 0; background-image: url('{logo_src_b64}'); background-position: center; background-repeat: no-repeat; background-size: 55%; opacity: 0.07; z-index: 0; pointer-events: none;"></div>""" if logo_src_b64 else ""
            header_logo_html = f'<img src="{logo_src_b64}" style="height: 65px; margin-right: 15px; margin-left: 15px; object-fit: contain;">' if logo_src_b64 else ''
            
            # 🟢 ممتحن کا حصہ (Examiner Marks Block)
            th_cells = ""
            td_cells = ""
            for q in range(1, int(subj_count) + 1):
                th_cells += f"<td style='border: 1px solid #000; padding: 4px; font-size: 11px;'>Q.{q}</td>"
                td_cells += f"<td style='border: 1px solid #000; padding: 10px;'></td>"
                
            examiner_table_html = f"""
            <table style="width: 100%; border-collapse: collapse; margin-bottom: 10px; text-align: center; font-weight: bold; background-color: rgba(240,240,240,0.8);" dir="ltr">
                <tr>
                    <td style="border: 1px solid #000; padding: 4px; background: #ddd; font-size: 11px; font-family: Arial, sans-serif;" rowspan="2">{exam_use_lbl}</td>
                    {th_cells}
                    <td style="border: 1px solid #000; padding: 4px; background: #ddd; font-size: 11px; font-family: Arial, sans-serif;">{tot_lbl}</td>
                </tr>
                <tr>
                    {td_cells}
                    <td style="border: 1px solid #000; padding: 10px; background: #ddd;"></td>
                </tr>
            </table>
            """
            
            # 🟢 MCQs کے ببلز (Bubbles)
            mcq_html = ""
            if mcq_count > 0:
                mcq_html += f"""<div style="margin-top: 10px; border: 1px solid #000; padding: 8px; background: rgba(255,255,255,0.8);"><h4 style="margin: 0 0 5px 0; text-align: center; border-bottom: 1px solid #ccc; padding-bottom: 3px; font-size: 13px; font-family: {f_family};">{obj_sec_lbl}</h4><table style="width: 100%; font-size: 12px; font-family: Arial, sans-serif;" dir="ltr">"""
                rows = (mcq_count + 1) // 2
                for i in range(rows):
                    q1 = i + 1
                    q2 = q1 + rows
                    mcq_html += "<tr>"
                    mcq_html += f"<td style='padding: 3px 0; width: 50%;'><b>Q{q1}.</b> &nbsp; ◯ A &nbsp; ◯ B &nbsp; ◯ C &nbsp; ◯ D</td>"
                    if q2 <= mcq_count:
                        mcq_html += f"<td style='padding: 3px 0; width: 50%;'><b>Q{q2}.</b> &nbsp; ◯ A &nbsp; ◯ B &nbsp; ◯ C &nbsp; ◯ D</td>"
                    else:
                        mcq_html += "<td style='width: 50%;'></td>"
                    mcq_html += "</tr>"
                mcq_html += "</table></div>"

            # 🟢 لکھنے کے لیے لائنیں (Ruled Lines)
            lines_html = ""
            for _ in range(35): 
                lines_html += "<div style='border-bottom: 1px solid #999; height: 32px; width: 100%; box-sizing: border-box;'></div>"

            # 🟢 Flexbox کا استعمال کر کے پورے پیج کو لاک کر دیا گیا ہے
            doc_html = f"""
            {font_css}
            <div style="font-family: {f_family}; padding: 25px 35px; max-width: 800px; height: 1030px; margin: 0 auto; border: 2px solid #000; background: white; position: relative; z-index: 1; box-sizing: border-box; display: flex; flex-direction: column; overflow: hidden; page-break-inside: avoid;" dir="{t_dir}">
                {watermark_html}
                
                <div style="position: relative; z-index: 2; width: 100%;">
                    
                    <!-- 🟢 Header -->
                    <div style="display: flex; align-items: center; justify-content: space-between; border-bottom: 2px solid #000; padding-bottom: 10px; margin-bottom: 15px;">
                        <div style="width: 20%; text-align: {t_align};">{header_logo_html}</div>
                        <div style="width: 60%; text-align: center;">
                            <h1 style="margin: 0; color: #000; font-size: 24px; font-weight: 900; font-family: 'Arial', sans-serif;">{school_n_doc}</h1>
                            <h2 style="margin: 5px 0 0 0; font-size: 15px; background-color: #000; color: #fff; padding: 4px; display: inline-block; letter-spacing: 1px;">{sheet_lbl}</h2>
                            <p style="margin: 5px 0 0 0; font-weight: bold; font-size: 14px;">{exam_title}</p>
                        </div>
                        <div style="width: 20%; text-align: {t_align_opp}; font-size: 11px; font-weight: bold;">
                            <div style="border: 1px solid #000; padding: 12px 5px; text-align: center; font-family: Arial, sans-serif;">
                                {inv_sig_lbl}<br><br><br>________________
                            </div>
                        </div>
                    </div>
                    
                    <!-- 🟢 Student Details -->
                    <table style="width: 100%; border-collapse: collapse; margin-bottom: 15px; font-size: 13px; font-weight: bold;">
                        <tr>
                            <td style="border: 1px solid #000; padding: 8px; width: 50%;">{st_name_lbl} <span style="border-bottom: 1px dashed #000; display: inline-block; width: 65%;"></span></td>
                            <td style="border: 1px solid #000; padding: 8px; width: 50%;">{roll_no_lbl} <span style="border-bottom: 1px dashed #000; display: inline-block; width: 70%;"></span></td>
                        </tr>
                        <tr>
                            <td style="border: 1px solid #000; padding: 8px;">{cls_sec_lbl} <span style="border-bottom: 1px dashed #000; display: inline-block; width: 65%;"></span></td>
                            <td style="border: 1px solid #000; padding: 8px;">{subject_lbl} <span style="border-bottom: 1px dashed #000; display: inline-block; width: 70%;"></span></td>
                        </tr>
                        <tr>
                            <td style="border: 1px solid #000; padding: 8px;">{date_lbl} <span style="border-bottom: 1px dashed #000; display: inline-block; width: 75%;"></span></td>
                            <td style="border: 1px solid #000; padding: 8px;">{tot_pages_lbl} <span style="border-bottom: 1px dashed #000; display: inline-block; width: 55%;"></span></td>
                        </tr>
                    </table>
                    
                    {examiner_table_html}
                    
                    {mcq_html}
                    
                    <div style="text-align: center; margin: 15px 0 5px 0;">
                        <h4 style="margin: 0; border-bottom: 2px solid #000; display: inline-block; font-size: 14px;">{subj_sec_lbl}</h4>
                    </div>
                </div>
                
                <!-- 🟢 یہ حصہ خود بخود باقی بچی ہوئی جگہ پر فکس ہو جائے گا (Overflow Hidden) -->
                <div style="flex-grow: 1; overflow: hidden; position: relative; z-index: 2; width: 100%;">
                    {lines_html}
                </div>
                
            </div>
            """
            
            st.write("---")
            c_btn1, c_btn2 = st.columns([1, 2])
            with c_btn1:
                print_button_js(doc_html, tr("🖨️ پرنٹ جوابی کاپی", "🖨️ Print Answer Sheet"), landscape=False)

# ================= 8.5 ٹرانسپورٹ اور لائیو جی پی ایس (Transport & Live GPS) =================
elif core_choice in ["ٹرانسپورٹ (GPS)", "Transport"]:
    st.markdown(f"<h2 class='no-print'>🚌 {tr('ٹرانسپورٹ اور لائیو ٹریکنگ', 'Transport & Live GPS Tracking')} - {tr(sub_choice, sub_choice)}</h2>", unsafe_allow_html=True)
    
    if sub_choice in ["Vehicles & Routes", "گاڑیاں اور روٹس"]:
        st.markdown(f"### 🚐 {tr('نئی گاڑی یا رکشہ شامل کریں', 'Add New Vehicle / Auto')}")
        with st.form("add_vehicle_form"):
            c1, c2, c3 = st.columns(3)
            v_type = c1.selectbox(tr("گاڑی کی قسم", "Vehicle Type"), ["School Van", "Bus", "Auto Rickshaw", "Car"])
            v_id = c2.text_input(tr("گاڑی کا نمبر (Vehicle No)", "Vehicle No/ID"), placeholder="مثلاً: SGA-1234")
            v_route = c3.text_input(tr("روٹ / علاقہ", "Route / Area"), placeholder="مثلاً: سلانوالی مین سٹی")
            
            c4, c5, c6 = st.columns(3)
            d_name = c4.text_input(tr("ڈرائیور کا نام", "Driver Name"))
            d_phone = c5.text_input(tr("ڈرائیور کا فون", "Driver Phone"))
            v_fare = c6.number_input(tr("ماہانہ کرایہ (Rs)", "Monthly Fare (Rs)"), min_value=0)
            
            if st.form_submit_button(tr("گاڑی محفوظ کریں", "Save Vehicle"), type="primary"):
                if v_id and d_name:
                    try:
                        gps_id = f"GPS_{v_id.replace(' ', '')}"
                        cursor.execute("INSERT INTO transport VALUES (?, ?, ?, ?, ?, ?, ?)", (v_id, v_type, d_name, d_phone, v_route, v_fare, gps_id))
                        # 🟢 سلانوالی کی ابتدائی ڈمی لوکیشن ڈالیں تاکہ میپ چل سکے (Lat: 31.82, Lon: 72.54)
                        cursor.execute("INSERT INTO live_locations VALUES (?, 31.821, 72.542, ?, 0)", (gps_id, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
                        conn.commit()
                        st.success(tr("گاڑی اور GPS سسٹم کامیابی سے شامل ہو گئے!", "Vehicle & GPS initialized successfully!"))
                        st.rerun()
                    except Exception as e: st.error("Error: Vehicle ID might already exist.")
                else: st.warning(tr("گاڑی کا نمبر اور ڈرائیور کا نام لازمی ہے۔", "Vehicle No and Driver name are required."))
        
        st.write("---")
        st.markdown(f"### 📋 {tr('رجسٹرڈ گاڑیاں', 'Registered Vehicles')}")
        v_df = pd.read_sql("SELECT vehicle_id as 'Vehicle No', type as 'Type', driver_name as 'Driver', driver_phone as 'Phone', route_name as 'Route', fare as 'Fare', gps_device_id as 'GPS ID' FROM transport", conn)
        if not v_df.empty: st.dataframe(v_df, use_container_width=True, hide_index=True)
        else: st.info(tr("کوئی گاڑی موجود نہیں۔", "No vehicles registered."))

    elif sub_choice in ["Student Booking", "طلباء کی بکنگ"]:
        st.markdown(f"### 👨‍🎓 {tr('طالب علم کو وین/رکشہ الاٹ کریں', 'Assign Vehicle to Student')}")
        v_df = pd.read_sql("SELECT vehicle_id, route_name, fare FROM transport", conn)
        
        if not v_df.empty:
            v_options = v_df.apply(lambda r: f"{r['vehicle_id']} - {r['route_name']} (Rs {r['fare']})", axis=1).tolist()
            
            c_s1, c_s2 = st.columns(2)
            s_class = c_s1.selectbox(tr("کلاس", "Class"), classes_list, key="ts_cls")
            stu_df = pd.read_sql(f"SELECT reg_id, name FROM students WHERE class='{s_class}'", conn)
            
            if not stu_df.empty:
                stu_options = stu_df.apply(lambda r: f"{r['name']} (Reg: {r['reg_id']})", axis=1).tolist()
                s_name = c_s2.selectbox(tr("طالب علم", "Student"), stu_options)
                
                sel_v = st.selectbox(tr("گاڑی / روٹ منتخب کریں", "Select Vehicle / Route"), v_options)
                
                if st.button(tr("بکنگ محفوظ کریں (Save Booking)", "Save Booking"), type="primary"):
                    r_id = s_name.split("Reg: ")[1].replace(")", "")
                    veh_id = sel_v.split(" - ")[0]
                    
                    cursor.execute("DELETE FROM transport_members WHERE reg_id=?", (r_id,))
                    cursor.execute("INSERT INTO transport_members VALUES (?, ?)", (r_id, veh_id))
                    
                    # 🟢 آٹو فیس میں کرایہ شامل کرنا (اختیاری)
                    extra_fare = v_df[v_df['vehicle_id'] == veh_id].iloc[0]['fare']
                    cursor.execute(f"UPDATE students SET monthly_fee = monthly_fee + {extra_fare} WHERE reg_id='{r_id}'")
                    conn.commit()
                    
                    st.success(tr("طالب علم کو وین الاٹ کر دی گئی اور کرایہ فیس میں شامل کر دیا گیا!", "Assigned successfully and fare added to monthly fee!"))
            else: st.warning(tr("اس کلاس میں طالب علم نہیں۔", "No students in this class."))
            
            st.write("---")
            st.markdown(f"### 🚌 {tr('وین میں سوار طلباء کی لسٹ', 'Students currently using transport')}")
            b_df = pd.read_sql("SELECT t.vehicle_id as 'Vehicle', t.route_name as 'Route', s.reg_id as 'Reg No', s.name as 'Student Name', s.class as 'Class' FROM transport_members tm JOIN students s ON tm.reg_id = s.reg_id JOIN transport t ON tm.vehicle_id = t.vehicle_id", conn)
            if not b_df.empty: st.dataframe(b_df, use_container_width=True, hide_index=True)
            else: st.info("No bookings found.")
        else: st.info(tr("پہلے کوئی گاڑی رجسٹر کریں۔", "Register a vehicle first."))

    elif sub_choice in ["Live GPS Map", "لائیو جی پی ایس (لائیو میپ)"]:
        st.markdown(f"### 🛰️ {tr('لائیو وہیکل ٹریکنگ ڈیش بورڈ', 'Live Vehicle Tracking Dashboard')}")
        st.write(tr("یہاں آپ نقشے پر سکول کی تمام گاڑیوں کی لائیو لوکیشن دیکھ سکتے ہیں۔", "View real-time location of all school vehicles on the map."))
        
        # 🟢 سلانوالی کی لوکیشن کے حساب سے GPS سمولیشن (صرف ڈیمو اور ٹیسٹنگ کے لیے)
        if st.button("📡 سمیلیٹ لائیو موومنٹ (Test Live Movement)", help="گاڑیوں کو نقشے پر حرکت دینے کے لیے اسے دبائیں"):
            locs = pd.read_sql("SELECT device_id, lat, lon FROM live_locations", conn)
            for _, l in locs.iterrows():
                # لوکیشن میں تھوڑی سی تبدیلی (گاڑی کے چلنے کا احساس دلانے کے لیے)
                new_lat = l['lat'] + random.uniform(-0.002, 0.002)
                new_lon = l['lon'] + random.uniform(-0.002, 0.002)
                t_now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                cursor.execute("UPDATE live_locations SET lat=?, lon=?, last_updated=? WHERE device_id=?", (new_lat, new_lon, t_now, l['device_id']))
            conn.commit()
            st.rerun()

        map_df = pd.read_sql("""
            SELECT t.vehicle_id, t.driver_name, l.lat as latitude, l.lon as longitude, l.last_updated
            FROM transport t JOIN live_locations l ON t.gps_device_id = l.device_id
        """, conn)
        
        if not map_df.empty:
            # 🟢 لائیو نقشہ (Streamlit Native Map)
            st.map(map_df, zoom=13, use_container_width=True)
            
            st.markdown("#### 📍 آخری اپڈیٹ (Last Known Locations)")
            st.dataframe(map_df[['vehicle_id', 'driver_name', 'last_updated']], use_container_width=True, hide_index=True)
        else:
            st.warning(tr("نقشے پر دکھانے کے لیے کوئی ایکٹو گاڑی موجود نہیں۔", "No active vehicles found to display on map."))

# ================= 9. WhatsApp Auto Bulk Communication System =================
elif core_choice in ["واٹس ایپ نوٹیفیکیشن", "WhatsApp Alerts"]:
    st.markdown(f"<h2 class='no-print'>&#128241; {tr('واٹس ایپ آٹو کمیونیکیشن سسٹم', 'WhatsApp Auto Bulk Communication System')}</h2>", unsafe_allow_html=True)
    st.markdown(f"<p class='no-print'>{tr('میسجز آٹو جنریٹ کرنے کے لیے کلاس اور کیٹیگری کا انتخاب کریں۔', 'Select class and category to auto-generate messages in professional format with smart subject-based icons.')}</p>", unsafe_allow_html=True)
    
    current_u = st.session_state.current_user
    current_role = st.session_state.current_role
    s_id = st.session_state.ref_id
    if not s_id or s_id == "None" or s_id == "N/A":
        s_id = current_u.replace('staff_', '')
    
    st.write("---")
    
    try:
        cursor.execute("SELECT reg_id, name, name_en, fname, fname_en, class, section, phone FROM students WHERE status='Active' ORDER BY class, name")
        all_students = cursor.fetchall()
    except Exception as e:
        st.error(f"Database Error: {e}")
        all_students = []
        
    t_cls = "All"
    if current_role == "Teacher":
        try:
            cursor.execute(f"SELECT assigned_class FROM staff WHERE staff_id='{s_id}'")
            t_data = cursor.fetchone()
            if t_data and t_data[0] != "None":
                t_cls = t_data[0]
                all_students = [s for s in all_students if str(s[5]) == str(t_cls)]
        except: pass
        
        if t_cls != "All":
            st.info(f"👨‍🏫 {tr(f'ٹیچر موڈ: آپ کو صرف اپنی تفویض کردہ کلاس ({t_cls}) کا ڈیٹا دکھایا جا رہا ہے۔', f'Teacher Mode: Showing data for your assigned class ({t_cls}) only.')}")
        else:
            st.warning(f"⚠️ {tr('آپ کو کوئی کلاس الاٹ نہیں کی گئی۔ براہ کرم پرنسپل/ایڈمن سے رابطہ کریں۔', 'No class assigned to you. Please contact Principal/Admin.')}")
            all_students = []

    if not all_students:
        st.warning(tr("ڈیٹا بیس میں طلباء کا کوئی ریکارڈ نہیں ملا۔", "No student records found."))
    else:
        classes_list_wa = sorted(list(set([str(s[5]) for s in all_students if s[5]])))
        
        cat_options_en = [
            "Daily Homework & Lesson Plan",
            "Daily Attendance Status",
            "Monthly Attendance Summary",
            "Exam Performance & Result Report",
            "General Notice & Circular",
            "Fee Defaulters Reminder"
        ]
        cat_options_ur = [
            "روزانہ ہوم ورک اور لیسن پلان",
            "روزانہ حاضری کی رپورٹ",
            "ماہانہ حاضری کی سمری",
            "امتحان کا رزلٹ اور پرفارمنس",
            "جنرل نوٹس اور سرکلر",
            "فیس ڈیفالٹرز ریمائنڈر"
        ]
        
        display_cats = cat_options_en if st.session_state.ui_lang == "English" else cat_options_ur
        
        message_category = st.selectbox(tr("میسج کیٹیگری", "Message Category"), display_cats, key="wa_stable_category_selector")
        cat_index = display_cats.index(message_category)
        
        st.write("---")
        
        import datetime
        import pandas as pd
        
        extra_details = ""
        attendance_status = "Present"
        selected_exam_wa = None
        target_list = []
        is_staff = False
        
        if cat_index == 4: # General Notice
            st.markdown(f"### &#128226; {tr('نوٹس کی سیٹنگز', 'Notice Settings')}", unsafe_allow_html=True)
            c_d, c_t = st.columns(2)
            msg_date = c_d.date_input(tr("تاریخ منتخب کریں", "Select Date"), value=datetime.date.today(), key="wa_date_notice")
            
            if current_role == "Teacher":
                target_audience = "Students"
                notice_scope = "Specific Class"
                selected_class_wa = classes_list_wa[0] if classes_list_wa else ""
                target_list = [s for s in all_students if str(s[5]) == str(selected_class_wa)]
                c_t.info(tr("ہدف: آپ کے تفویض کردہ طلباء", "Target: Your Assigned Students"))
            else:
                target_audience = c_t.radio(tr("ٹارگٹ آڈینس منتخب کریں", "Select Target Audience"), ["Students", "Staff"], horizontal=True)
                
                if target_audience == "Students":
                    c_s1, c_s2 = st.columns(2)
                    scope_opts = ["Whole School", "Specific Class", "Specific Student"] if st.session_state.ui_lang == "English" else ["پورا سکول", "مخصوص کلاس", "مخصوص طالب علم"]
                    notice_scope = c_s1.selectbox(tr("دائرہ کار منتخب کریں", "Select Scope"), scope_opts)
                    
                    if "Whole" in notice_scope or "پورا" in notice_scope:
                        target_list = all_students
                    elif "Class" in notice_scope or "کلاس" in notice_scope:
                        selected_class_wa = c_s2.selectbox(tr("کلاس منتخب کریں", "Select Class"), classes_list_wa)
                        target_list = [s for s in all_students if str(s[5]) == str(selected_class_wa)]
                    elif "Student" in notice_scope or "طالب علم" in notice_scope:
                        selected_class_wa = c_s2.selectbox(tr("کلاس منتخب کریں", "Select Class"), classes_list_wa)
                        class_st = [s for s in all_students if str(s[5]) == str(selected_class_wa)]
                        if class_st:
                            student_names = [f"{s[2] if s[2] else s[1]} (S/O {s[4] if s[4] else s[3]})" for s in class_st]
                            selected_stu_str = st.selectbox(tr("طالب علم منتخب کریں", "Select Student"), student_names)
                            target_list = [s for s, n in zip(class_st, student_names) if n == selected_stu_str]
                        else:
                            target_list = []
                else: # Staff
                    is_staff = True
                    try:
                        cursor.execute("SELECT staff_id, name, phone FROM staff")
                        target_list = cursor.fetchall()
                    except:
                        st.error(tr("سٹاف کا ڈیٹا بیس میں ریکارڈ نہیں ملا۔", "Staff record not found in database."))
                        target_list = []
            
            try:
                df_notices = pd.read_sql("SELECT title, details FROM notices ORDER BY id DESC", conn)
                notice_options = [tr("نیا نوٹس لکھیں (Custom Notice)", "Custom Notice")] + df_notices['title'].tolist()
            except:
                df_notices = pd.DataFrame()
                notice_options = [tr("نیا نوٹس لکھیں (Custom Notice)", "Custom Notice")]
                
            selected_notice = st.selectbox(tr("نوٹس بورڈ سے نوٹس منتخب کریں", "Select from Notice Board"), notice_options)
            
            default_notice_text = ""
            if "Custom" not in selected_notice and "نیا" not in selected_notice and not df_notices.empty:
                default_notice_text = df_notices[df_notices['title'] == selected_notice]['details'].iloc[0]
                
            extra_details = st.text_area(tr("نوٹس / سرکلر کی تفصیلات:", "Notice / Circular Details:"), value=default_notice_text, height=150, placeholder=tr("یہاں نوٹس ٹائپ کریں...", "Type notice here..."))
            
        else:
            c_w1, c_w2 = st.columns(2)
            
            if current_role == "Teacher" and len(classes_list_wa) > 0:
                selected_class_wa = classes_list_wa[0]
                c_w1.info(tr(f"کلاس خود بخود منتخب ہو گئی: {selected_class_wa}", f"Class Auto-Selected: {selected_class_wa}"))
            else:
                selected_class_wa = c_w1.selectbox(tr("کلاس منتخب کریں", "Select Class"), classes_list_wa, key="wa_stable_class_selector")
                
            msg_date = c_w2.date_input(tr("تاریخ منتخب کریں", "Select Date"), value=datetime.date.today(), key="wa_stable_date_input")
            
            raw_target_list = [s for s in all_students if str(s[5]) == str(selected_class_wa)]
            
            if cat_index == 5:
                target_list = []
                for s in raw_target_list:
                    check_due = pd.read_sql(f"SELECT COUNT(*) FROM fees WHERE reg_id='{s[0]}' AND status='Unpaid'", conn).iloc[0,0]
                    if check_due > 0:
                        target_list.append(s)
            else:
                target_list = raw_target_list
            
            def get_smart_icon(subject_name, topic_text=""):
                sub_lower, topic_lower = str(subject_name).lower(), str(topic_text).lower()
                if "write" in topic_lower or "writing" in topic_lower or "لکھ" in topic_lower or "copy" in topic_lower: return "\u270D\uFE0F"
                if "science" in sub_lower or "سائنس" in sub_lower or "biology" in sub_lower or "physics" in sub_lower or "chemistry" in sub_lower: return "\u2697\uFE0F"
                elif "math" in sub_lower or "ریاضی" in sub_lower or "algebra" in sub_lower or "geometry" in sub_lower or "arithmetic" in sub_lower: return "\uD83D\uDCD0"
                elif "urdu" in sub_lower or "اردو" in sub_lower: return "\uD83D\uDCD8"
                elif "english" in sub_lower or "انگلش" in sub_lower or "eng" in sub_lower or "grammar" in sub_lower: return "\uD83D\uDCD6"
                elif "islam" in sub_lower or "islamiat" in sub_lower or "اسلامیات" in sub_lower or "quran" in sub_lower or "deenyat" in sub_lower or "arabic" in sub_lower: return "\uD83D\uDD4C"
                elif "computer" in sub_lower or "it" in sub_lower or "कंप्यूटर" in sub_lower or "ict" in sub_lower: return "\uD83D\uDCBB"
                elif "social" in sub_lower or "history" in sub_lower or "geography" in sub_lower or "معاشرتی" in sub_lower or "pak studies" in sub_lower or "مطالعہ" in sub_lower: return "\uD83C\uDF0D"
                elif "drawing" in sub_lower or "art" in sub_lower or "پینٹنگ" in sub_lower or "آرٹ" in sub_lower: return "\uD83C\uDFA8"
                elif "general" in sub_lower or "gk" in sub_lower or "معلومات" in sub_lower: return "\uD83E\uDDE0"
                elif "pe" in sub_lower or "sports" in sub_lower or "ورزش" in sub_lower or "کھیل" in sub_lower: return "\u26BD"
                else: return "\uD83D\uDCD8"
            
            if cat_index == 0:
                try:
                    date_str_sql = msg_date.strftime("%Y-%m-%d")
                    query_lp = "SELECT subject, topic FROM lesson_plan WHERE date=? AND class=? AND status IN ('Completed', 'مکمل ہو گیا')"
                    cursor.execute(query_lp, (date_str_sql, selected_class_wa))
                    completed_plans = cursor.fetchall()
                    if completed_plans:
                        plan_lines = ""
                        for p in completed_plans:
                            sub_n, top_n = p[0], p[1]
                            icon = get_smart_icon(sub_n, top_n)
                            icon_space = f"{icon} " if icon else ""
                            plan_lines += f"{icon_space}*{sub_n}*: {top_n}\n"
                        auto_diary_text = plan_lines.strip()
                    else:
                        auto_diary_text = "Please complete the assigned homework."
                except:
                    auto_diary_text = "Please complete the assigned homework."
                extra_details = st.text_area(tr("ہوم ورک کی تفصیلات", "Homework Details"), value=auto_diary_text, height=130, key=f"hw_{msg_date}_{selected_class_wa}")
                
            elif cat_index == 1:
                attendance_status = st.selectbox(tr("حاضری کی حالت", "Attendance Status"), ["Present", "Absent", "Leave"], key=f"att_{msg_date}")
            elif cat_index == 2:
                extra_details = st.text_input(tr("مہینے کا نام", "Month Name"), value="Current Month", key=f"mon_{msg_date}")
            elif cat_index == 3:
                available_exams_wa = pd.read_sql("SELECT exam_name FROM exams", conn)['exam_name'].tolist()
                if available_exams_wa:
                    selected_exam_wa = st.selectbox(tr("امتحان منتخب کریں", "Select Exam"), available_exams_wa, key="wa_exam_sel")
                    extra_details = st.text_input(tr("اضافی ریمارکس (اختیاری)", "Additional Remarks (Optional)"), value="", key=f"rem_{selected_exam_wa}")
                else:
                    st.warning(tr("براہ کرم پہلے امتحان بنائیں اور نمبر درج کریں۔", "Please create an exam and enter marks first."))

        st.write("---")
        
        if not target_list:
            if cat_index == 5:
                st.success(tr("کوئی فیس ڈیفالٹر نہیں ہے! اس کلاس کے تمام طلباء کی فیس جمع ہو چکی ہے۔", "No fee defaulters! All students in this class have paid their fees."))
            else:
                st.info(tr("منتخب کردہ شرائط کے مطابق کوئی وصول کنندہ نہیں ملا۔", "No recipients found for the selected criteria."))
        else:
            total_recipients = len(target_list)
            
            if is_staff:
                st.markdown(f"### &#128203; {tr('ہدف سامعین: سٹاف ممبرز', 'Target Audience: Staff Members')} ({total_recipients} {tr('ریکارڈز', 'Records')})", unsafe_allow_html=True)
            else:
                if cat_index == 4:
                    if current_role == "Teacher":
                        st.markdown(f"### &#128203; {tr('ہدف سامعین: آپ کی تفویض کردہ کلاس', 'Target Audience: Your Assigned Class')} ({total_recipients} {tr('ریکارڈز', 'Records')})", unsafe_allow_html=True)
                    else:
                        st.markdown(f"### &#128203; {tr(f'ہدف سامعین: طلباء ({notice_scope})', f'Target Audience: Students ({notice_scope})')} ({total_recipients} {tr('ریکارڈز', 'Records')})", unsafe_allow_html=True)
                elif cat_index == 5:
                    st.markdown(f"### &#128203; {tr(f'کلاس: {selected_class_wa} - فیس ڈیفالٹرز کی فہرست', f'Class: {selected_class_wa} - Fee Defaulters List')} ({total_recipients} {tr('طلباء', 'Students')})", unsafe_allow_html=True)
                else:
                    st.markdown(f"### &#128203; {tr(f'کلاس: {selected_class_wa} - تمام طلباء کی فہرست', f'Class: {selected_class_wa} - All Students List')} ({total_recipients} {tr('طلباء', 'Students')})", unsafe_allow_html=True)
            
            import urllib.parse
            
            st.markdown(f"""
            <div style='background-color: #e8f5e9; padding: 15px; border-radius: 8px; border: 2px solid #4caf50; margin-bottom: 20px;'>
                <h4 style='color: #2e7d32; margin: 0 0 5px 0;'>&#128994; {tr('آٹو واٹس ایپ بلک سینڈر تیار ہے!', 'Auto WhatsApp Bulk Sender Ready!')}</h4>
                <p style='margin: 0; font-size: 14px;'>{tr('براہ راست واٹس ایپ بٹن نیچے دستیاب ہیں۔ آپ نیچے دیا گیا سنگل کلک آٹو سینڈر بھی استعمال کر سکتے ہیں۔', 'Direct WhatsApp buttons are available below. You can also use the single-click Auto Sender at the bottom.')}</p>
            </div>
            """, unsafe_allow_html=True)
            
            school_name_upper = school_name.upper() if school_name else "SCHOOL"
            
            if current_role == "Teacher":
                footer_sign = f"Regards,\nClass Teacher ({selected_class_wa})\n{school_name_upper}"
            else:
                footer_sign = f"Regards,\n{school_name_upper} ADMINISTRATION"
                
            contact_info = f"\nContact: {school_phone}" if school_phone else ""
            msg_footer = f"\n\n{footer_sign}{contact_info}"
            date_formatted = msg_date.strftime('%d-%m-%Y')
            
            auto_send_data = []
            
            for idx, member in enumerate(target_list, 1):
                if is_staff:
                    s_id = member[0]
                    s_name_msg = str(member[1]).strip()
                    s_phone = member[2]
                    s_fname_msg, s_class, s_sec = "N/A", "Staff", "N/A"
                    
                    phone_raw = str(s_phone).strip() if s_phone and str(s_phone) != "None" else ""
                    if phone_raw.startswith("0"): phone_num = "92" + phone_raw[1:]
                    elif phone_raw.startswith("+92"): phone_num = phone_raw[1:]
                    else: phone_num = phone_raw
                    
                    msg_header = f"*{school_name_upper}*\n{school_address}\n\nDate: {date_formatted}\nAsslam o Aaleikum,\n\nStaff Member: *{s_name_msg}*\n\n"
                    msg_body = f"NOTICE / CIRCULAR:\n{extra_details}"
                    disp_title = f"{idx}. {s_name_msg} (Staff) - [Phone: {phone_num if phone_num else 'Missing'}]"
                    
                else:
                    s_id = member[0]
                    s_name_ur, s_name_en = member[1], member[2]
                    s_fname_ur, s_fname_en = member[3], member[4]
                    s_class, s_sec, s_phone = member[5], member[6], member[7]
                    
                    s_name_msg = str(s_name_en).strip() if s_name_en and str(s_name_en).strip() not in ["", "None"] else str(s_name_ur)
                    s_fname_msg = str(s_fname_en).strip() if s_fname_en and str(s_fname_en).strip() not in ["", "None"] else str(s_fname_ur)
                    
                    phone_raw = str(s_phone).strip() if s_phone and str(s_phone) != "None" else ""
                    if phone_raw.startswith("0"): phone_num = "92" + phone_raw[1:]
                    elif phone_raw.startswith("+92"): phone_num = phone_raw[1:]
                    else: phone_num = phone_raw
                    
                    msg_header = f"*{school_name_upper}*\n{school_address}\n\nDate: {date_formatted}\nAsslam o Aaleikum Dear Parents\n\nStudent: *{s_name_msg}*\nFather: *{s_fname_msg}*\nClass: *{s_class} ({s_sec})*\n\n"
                    
                    if cat_index == 0: 
                        msg_body = f"HOME WORK:\n{extra_details}"
                    elif cat_index == 1: 
                        msg_body = f"Attendance Status: {attendance_status}"
                    elif cat_index == 2: 
                        msg_body = f"Monthly Report ({extra_details}): Satisfactory"
                    elif cat_index == 3:
                        if selected_exam_wa:
                            marks_df = pd.read_sql(f"SELECT subject, total_marks, obtained_marks FROM exam_marks WHERE exam_name='{selected_exam_wa}' AND reg_id='{s_id}'", conn)
                            if not marks_df.empty:
                                grand_tot, grand_obt = marks_df['total_marks'].sum(), marks_df['obtained_marks'].sum()
                                perc = (grand_obt / grand_tot * 100) if grand_tot > 0 else 0
                                marks_str = ""
                                for _, row in marks_df.iterrows():
                                    sub_name, obt_m, tot_m = row['subject'], row['obtained_marks'], row['total_marks']
                                    marks_str += f"*{sub_name}*: {obt_m}/{tot_m}\n"
                                marks_str += f"\n*Total Marks:* {grand_obt}/{grand_tot} ({perc:.1f}%)"
                                msg_body = f"Result Details ({selected_exam_wa}):\n{marks_str}"
                                if extra_details: msg_body += f"\n\n*Remarks:* {extra_details}"
                            else: 
                                msg_body = f"Result Details ({selected_exam_wa}):\nResult not entered yet."
                        else: 
                            msg_body = "Result Details:\nExam not selected or not available."
                    
                    elif cat_index == 4:
                        msg_body = f"NOTICE / CIRCULAR:\n{extra_details}"
                        
                    elif cat_index == 5: 
                        unpaid_fee = pd.read_sql(f"SELECT month, total FROM fees WHERE reg_id='{s_id}' AND status='Unpaid'", conn)
                        if not unpaid_fee.empty:
                            due_amount = unpaid_fee['total'].sum()
                            due_months = ", ".join(unpaid_fee['month'].tolist())
                            msg_body = f"FEE REMINDER:\nDear Parents, this is a gentle reminder that the fee for the month(s) of *{due_months}* amounting to *Rs {due_amount}* is pending. Kindly pay at your earliest convenience to avoid late fines.\n{extra_details}"
                        else:
                            continue
                    
                    disp_phone = phone_num if phone_num else "Missing"
                    disp_title = f"{idx}. {s_name_msg} (Father: {s_fname_msg}) - [Phone: {disp_phone}]"
                    
                msg_text = f"{msg_header}{msg_body}{msg_footer}"
                clean_ph = ''.join(filter(str.isdigit, phone_num)) if phone_num else ""
                
                if clean_ph:
                    auto_send_data.append({"phone": clean_ph, "name": s_name_msg, "message": msg_text})

                encoded_msg = urllib.parse.quote(msg_text)
                wa_link = f"https://api.whatsapp.com/send?phone={clean_ph}&text={encoded_msg}" if clean_ph else "#"
                
                with st.expander(disp_title):
                    c_b1, c_b2 = st.columns([1, 2])
                    if phone_num and len(clean_ph) >= 10:
                        btn_html = f"""<a href="{wa_link}" target="_blank" style='background-color: #25D366; color: white; padding: 10px 18px; text-decoration: none; font-size: 15px; font-weight: bold; border-radius: 5px; display: inline-block; text-align: center; width: 100%;'>&#128172; {tr('واٹس ایپ بھیجیں', 'Send WhatsApp')}</a>"""
                        c_b1.markdown(btn_html, unsafe_allow_html=True)
                    else:
                        c_b1.error(tr("فون نمبر غائب ہے", "Phone missing"))
                    c_b2.text_area(tr("میسج کا پیش نظارہ", "Full Message Preview"), value=msg_text, height=270, key=f"prev_{s_id}_{msg_date}_{cat_index}_{idx}")

        st.write("---")
        st.markdown(f"### &#128640; {tr('سنگل کلک ڈائریکٹ واٹس ایپ سینڈر (Direct Auto Sender)', 'Direct WhatsApp Auto Sender')}", unsafe_allow_html=True)
        st.warning(tr("اہم ہدایت: بٹن دبانے کے بعد اپنے کمپیوٹر کا ماؤس یا کی بورڈ مت چھیڑیں جب تک تمام میسج سینڈ نہ ہو جائیں۔ آپ کا واٹس ایپ ڈیسک ٹاپ ایپ (WhatsApp Desktop) لاگ ان اور اوپن ہونا چاہیے۔", "Important: Do not touch your mouse or keyboard until all messages are sent. WhatsApp Desktop app must be logged in and open."))
        
        if st.button(tr("ایک کلک سے تمام لسٹ کو میسج سینڈ کریں", "Send Messages to All with 1-Click"), type="primary"):
            try:
                import pyautogui
                import time
                import random
                import webbrowser
                
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                total_msgs = len([d for d in auto_send_data if len(d['phone']) >= 10])
                current_msg = 0
                
                if total_msgs == 0:
                    st.error(tr("میسج بھیجنے کے لیے کوئی درست نمبر موجود نہیں ہے۔", "No valid numbers found to send messages."))
                else:
                    for data in auto_send_data:
                        if len(data['phone']) < 10:
                            continue
                            
                        current_msg += 1
                        status_text.info(tr(f"میسج بھیجا جا رہا ہے: {data['name']} ({data['phone']}) ... ({current_msg}/{total_msgs})", f"Sending message to: {data['name']} ({data['phone']}) ... ({current_msg}/{total_msgs})"))
                        
                        encoded_msg = urllib.parse.quote(data['message'])
                        wa_uri = f"whatsapp://send?phone={data['phone']}&text={encoded_msg}"
                        
                        webbrowser.open(wa_uri)
                        time.sleep(8) 
                        pyautogui.press('enter') 
                        
                        if current_msg < total_msgs: 
                            safe_delay = random.randint(30, 45)
                            status_text.warning(tr(f"واٹس ایپ اینٹی بلاک سسٹم: اگلے میسج سے پہلے {safe_delay} سیکنڈ کا محفوظ وقفہ لیا جا رہا ہے...", f"WhatsApp Anti-Block System: Taking a safe pause of {safe_delay} seconds before next message..."))
                            time.sleep(safe_delay)
                        
                        progress_bar.progress(current_msg / total_msgs)
                        
                    status_text.success(tr("الحمدللہ! تمام منتخب ممبرز کو میسج محفوظ طریقے سے بھیجے جا چکے ہیں۔", "Alhamdulillah! Messages have been securely sent to all selected members."))
            except ImportError:
                st.error(tr("اس فیچر کو چلانے کے لیے اپنے کمپیوٹر کے CMD میں یہ کمانڈ چلائیں: pip install pyautogui", "To use this feature, run this command in your computer's CMD: pip install pyautogui"))

        st.write("---")
        with st.expander(tr("یا بلک سینڈر کے لیے ایکسل ڈاؤن لوڈ کریں (Optional Backup)", "Or Download Excel for Bulk Sender (Optional Backup)")):
            export_df = pd.DataFrame(auto_send_data)
            import io
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                export_df.to_excel(writer, index=False, sheet_name='WhatsApp_Data')
            processed_data = output.getvalue()
            st.download_button(
                label=tr("ایکسل فائل ڈاؤن لوڈ کریں", "Download Excel File"),
                data=processed_data,
                file_name=f"WhatsApp_List_{msg_date.strftime('%Y-%m-%d')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

# ================= 10. پرفارمنس ڈیش بورڈ (Performance Dashboard) =================
elif core_choice in ["پرفارمنس", "Performance"]:
    st.markdown(f"<h2 class='no-print'>📈 {tr('کارکردگی کا جائزہ', 'Performance Dashboard')} - {tr(sub_choice, sub_choice)}</h2>", unsafe_allow_html=True)
    
    if sub_choice == "Student Performance":
        c_p1, c_p2 = st.columns(2)
        p_cls = c_p1.selectbox(tr("کلاس منتخب کریں", "Select Class"), classes_list, key="perf_s_cls")
        stu_list = pd.read_sql(f"SELECT reg_id, name, name_en FROM students WHERE class='{p_cls}'", conn)
        if not stu_list.empty:
            stu_dict = {f"{get_disp_val(r['name'], r.get('name_en'))} (Reg: {r['reg_id']})": r['reg_id'] for _, r in stu_list.iterrows()}
            p_stu_name = c_p2.selectbox(tr("طالب علم منتخب کریں", "Select Student"), list(stu_dict.keys()))
            s_reg = stu_dict[p_stu_name]
            st.write("---")
            att_tot = pd.read_sql(f"SELECT COUNT(*) FROM attendance WHERE type='طالب علم' AND person_id='{s_reg}'", conn).iloc[0,0]
            att_pres = pd.read_sql(f"SELECT COUNT(*) FROM attendance WHERE type='طالب علم' AND person_id='{s_reg}' AND status IN ('Present', '🟢 Present', '🟢 حاضر')", conn).iloc[0,0]
            att_perc = (att_pres / att_tot * 100) if att_tot > 0 else 0
            
            marks = pd.read_sql(f"SELECT SUM(obtained_marks) as obt, SUM(total_marks) as tot FROM exam_marks WHERE reg_id='{s_reg}'", conn)
            acad_tot = marks.iloc[0]['tot']
            acad_obt = marks.iloc[0]['obt']
            acad_perc = (acad_obt / acad_tot * 100) if pd.notna(acad_tot) and acad_tot > 0 else 0
            
            col1, col2 = st.columns(2)
            col1.markdown(f"<div class='metric-card'><div class='metric-lbl'>{tr('حاضری کی شرح', 'Attendance Rate')}</div><div class='metric-val'>{att_perc:.1f}%</div><div style='font-size:12px; color:#888;'>({att_pres} / {att_tot} {tr('دن', 'Days')})</div></div>", unsafe_allow_html=True)
            col1.progress(int(att_perc) / 100)
            col2.markdown(f"<div class='metric-card'><div class='metric-lbl'>{tr('تعلیمی کارکردگی (اوسط)', 'Academic Performance (Avg)')}</div><div class='metric-val'>{acad_perc:.1f}%</div><div style='font-size:12px; color:#888;'>({tr('مجموعی امتحانی نتیجہ', 'Overall Exam Results')})</div></div>", unsafe_allow_html=True)
            col2.progress(int(acad_perc) / 100)
            
            st.write("")
            st.markdown(f"**{tr('تفصیلی امتحانی ریکارڈ:', 'Detailed Exam Records:')}**")
            d_marks = pd.read_sql(f"SELECT exam_name as 'Exam', subject as 'Subject', obtained_marks as 'Obtained', total_marks as 'Total' FROM exam_marks WHERE reg_id='{s_reg}'", conn)
            if not d_marks.empty: st.dataframe(d_marks, use_container_width=True)
            else: st.info(tr("امتحانات کا کوئی ریکارڈ نہیں ملا۔", "No exam records found."))
        else: st.warning(tr("اس کلاس میں کوئی طالب علم موجود نہیں۔", "No student found in this class."))

    elif sub_choice == "Staff Performance":
        try: 
            cursor.execute("ALTER TABLE staff ADD COLUMN assigned_class TEXT")
            cursor.execute("ALTER TABLE staff ADD COLUMN assigned_sec TEXT")
            conn.commit()
        except: pass

        stf_list = pd.read_sql("SELECT staff_id, name, name_en, designation, assigned_class, assigned_sec FROM staff", conn)
        if not stf_list.empty:
            stf_dict = {f"{get_disp_val(r['name'], r.get('name_en'))} ({get_desig_disp(r['designation'])})": r['staff_id'] for _, r in stf_list.iterrows()}
            p_stf_name = st.selectbox(tr("سٹاف ممبر منتخب کریں", "Select Staff Member"), list(stf_dict.keys()))
            t_id = stf_dict[p_stf_name]
            actual_name = p_stf_name.split(" (")[0]
            
            t_row = stf_list[stf_list['staff_id'] == t_id].iloc[0]
            t_cls = str(t_row.get('assigned_class', 'None')).strip()
            t_sec = str(t_row.get('assigned_sec', 'None')).strip()
            
            st.write("---")
            
            # 1. حاضری کا سکور (سب سے اہم)
            s_att_tot = pd.read_sql(f"SELECT COUNT(*) FROM attendance WHERE type='سٹاف' AND person_id='{t_id}'", conn).iloc[0,0]
            s_att_pres = pd.read_sql(f"SELECT COUNT(*) FROM attendance WHERE type='سٹاف' AND person_id='{t_id}' AND status IN ('Present', '🟢 Present', '🟢 حاضر')", conn).iloc[0,0]
            s_att_perc = (s_att_pres / s_att_tot * 100) if s_att_tot > 0 else 0
            
            # 2. لیسن پلان کا سکور
            lp_tot = pd.read_sql(f"SELECT COUNT(*) FROM lesson_plan WHERE teacher_id='{actual_name}'", conn).iloc[0,0]
            lp_comp = pd.read_sql(f"SELECT COUNT(*) FROM lesson_plan WHERE teacher_id='{actual_name}' AND status IN ('Completed', 'مکمل ہو گیا')", conn).iloc[0,0]
            lp_perc = (lp_comp / lp_tot * 100) if lp_tot > 0 else 0
            
            # 3. 🟢 ہیلپ ڈیسک پینلٹی (Penalty) - ہر پینڈنگ شکایت پر 1% کٹوتی
            tot_comps, res_comps, pending_comps = 0, 0, 0
            comp_perc = 100.0
            penalty_score = 0.0
            
            if t_cls != "None" and t_cls != "" and t_cls != "nan":
                comp_q = f"SELECT c.status FROM complaints c JOIN students s ON c.reg_id = s.reg_id WHERE s.class='{t_cls}'"
                if t_sec != "None" and t_sec != "" and t_sec != "nan" and t_sec != "All":
                    comp_q += f" AND s.section='{t_sec}'"
                    
                try: 
                    t_comps = pd.read_sql(comp_q, conn)
                    tot_comps = len(t_comps)
                    res_comps = len(t_comps[t_comps['status'] == 'Resolved'])
                    pending_comps = tot_comps - res_comps
                except: 
                    pass
                
                if tot_comps > 0:
                    comp_perc = (res_comps / tot_comps) * 100
                    # 🔴 1 شکایت پینڈنگ = 1% کٹوتی
                    penalty_score = pending_comps * 1.0 
                    
            # 🌟 4. نیا متوازن مجموعی پرفارمنس سکور
            is_teacher = ("Teacher" in str(t_row['designation']) or "استاد" in str(t_row['designation']))
            if is_teacher:
                # 50% حاضری، 50% لیسن پلان کا ویٹج - اور پھر شکایت کی 1% کٹوتی
                base_score = (s_att_perc * 0.5) + (lp_perc * 0.5)
                overall_score = max(0, base_score - penalty_score) # سکور مائنس میں نہ جائے
            else:
                overall_score = s_att_perc # نان ٹیچنگ سٹاف کے لیے صرف حاضری
                
            score_color = "#2e7d32" if overall_score >= 80 else ("#f57f17" if overall_score >= 50 else "#c62828")
            score_bg = "#e8f5e9" if overall_score >= 80 else ("#fff3e0" if overall_score >= 50 else "#ffebee")
            
            penalty_text = f"<p style='margin:5px 0 0 0; color:#c62828; font-weight:bold;'>⚠️ کٹوتی: {pending_comps} پینڈنگ شکایات کی وجہ سے {penalty_score}% نمبر کاٹے گئے۔</p>" if penalty_score > 0 else ""
            
            st.markdown(f"""
            <div style='background-color:{score_bg}; padding:20px; border-radius:10px; border:2px solid {score_color}; text-align:center; margin-bottom:25px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);'>
                <h3 style='margin:0; color:{score_color}; font-weight: bold;'>🏆 {tr('مجموعی پرفارمنس سکور', 'Overall Performance Score')}</h3>
                <h1 style='margin:10px 0; color:{score_color}; font-size: 50px; font-weight: 900;'>{overall_score:.1f}%</h1>
                <p style='margin:0; color:#555; font-size: 14px;'>{tr('اسکور کی تقسیم: حاضری (50%)، لیسن پلان (50%)، اور ہر زیرِ التواء شکایت پر -1% کٹوتی۔', 'Score breakdown: Attendance (50%), Lesson Plan (50%), with -1% penalty per pending complaint.')}</p>
                {penalty_text}
            </div>
            """, unsafe_allow_html=True)
            
            c1, c2, c3 = st.columns(3)
            c1.markdown(f"<div class='metric-card'><div class='metric-lbl'>{tr('حاضری کی شرح', 'Attendance Rate')}</div><div class='metric-val'>{s_att_perc:.1f}%</div><div style='font-size:12px; color:#888;'>({s_att_pres} / {s_att_tot} {tr('دن', 'Days')})</div></div>", unsafe_allow_html=True)
            c1.progress(int(s_att_perc) / 100)
            
            c2.markdown(f"<div class='metric-card'><div class='metric-lbl'>{tr('لیسن پلان تکمیل', 'Lesson Plan')}</div><div class='metric-val'>{lp_perc:.1f}%</div><div style='font-size:12px; color:#888;'>({lp_comp} / {lp_tot} {tr('اسباق', 'Lessons')})</div></div>", unsafe_allow_html=True)
            c2.progress(int(lp_perc) / 100)
            
            if is_teacher:
                comp_color = '#c62828' if pending_comps > 0 else '#2e7d32'
                c3.markdown(f"<div class='metric-card' style='border-color: {comp_color};'><div class='metric-lbl'>{tr('زیر التواء شکایات', 'Pending Complaints')}</div><div class='metric-val' style='color: {comp_color};'>{pending_comps} {tr('شکایات', 'Comps')}</div><div style='font-size:12px; color:#888;'>({res_comps} / {tot_comps} {tr('حل شدہ', 'Resolved')})</div></div>", unsafe_allow_html=True)
            else:
                c3.info(tr("یہ نان ٹیچنگ سٹاف ہے۔", "This is non-teaching staff."))
            
            st.write("")
            st.markdown(f"**{tr('تفویض کردہ کلاسز (ٹائم ٹیبل):', 'Assigned Classes (Timetable):')}**")
            t_tt = pd.read_sql(f"SELECT class as 'Class', section as 'Section', subject as 'Subject', COUNT(period) as 'Periods/Week' FROM timetable WHERE teacher_id='{actual_name}' GROUP BY class, section, subject", conn)
            if not t_tt.empty: st.dataframe(t_tt, use_container_width=True)
            else: st.info(tr("ٹائم ٹیبل میں کوئی کلاس الاٹ نہیں کی گئی۔", "No classes allotted in timetable."))
        else: st.warning(tr("سٹاف کا کوئی ریکارڈ موجود نہیں۔", "No staff records found."))

    elif sub_choice == "Overall School Performance":
        o_stu = pd.read_sql("SELECT COUNT(*) FROM students", conn).iloc[0,0]
        o_stf = pd.read_sql("SELECT COUNT(*) FROM staff", conn).iloc[0,0]
        
        today_str = datetime.date.today().strftime('%Y-%m-%d')
        o_stu_pres = pd.read_sql(f"SELECT COUNT(*) FROM attendance WHERE type='طالب علم' AND date='{today_str}' AND status IN ('Present', '🟢 Present', '🟢 حاضر')", conn).iloc[0,0]
        o_stu_tot_att = pd.read_sql(f"SELECT COUNT(*) FROM attendance WHERE type='طالب علم' AND date='{today_str}'", conn).iloc[0,0]
        o_stu_att_perc = (o_stu_pres / o_stu_tot_att * 100) if o_stu_tot_att > 0 else 0
        
        o_stf_pres = pd.read_sql(f"SELECT COUNT(*) FROM attendance WHERE type='سٹاف' AND date='{today_str}' AND status IN ('Present', '🟢 Present', '🟢 حاضر')", conn).iloc[0,0]
        o_stf_tot_att = pd.read_sql(f"SELECT COUNT(*) FROM attendance WHERE type='سٹاف' AND date='{today_str}'", conn).iloc[0,0]
        o_stf_att_perc = (o_stf_pres / o_stf_tot_att * 100) if o_stf_tot_att > 0 else 0
        
        acc_inc = pd.read_sql("SELECT SUM(amount) FROM accounts WHERE type='آمدنی' OR type='Income'", conn).iloc[0,0] or 0
        acc_exp = pd.read_sql("SELECT SUM(amount) FROM accounts WHERE type='خرچ' OR type='Expense'", conn).iloc[0,0] or 0
        acc_bal = acc_inc - acc_exp
        
        col_o1, col_o2, col_o3 = st.columns(3)
        col_o1.markdown(f"<div class='metric-card'><div class='metric-lbl'>{tr('کل طلباء', 'Total Students')}</div><div class='metric-val'>{o_stu}</div></div>", unsafe_allow_html=True)
        col_o2.markdown(f"<div class='metric-card'><div class='metric-lbl'>{tr('کل سٹاف', 'Total Staff')}</div><div class='metric-val'>{o_stf}</div></div>", unsafe_allow_html=True)
        col_o3.markdown(f"<div class='metric-card'><div class='metric-lbl'>{tr('موجودہ بیلنس', 'Current Balance')}</div><div class='metric-val'>Rs {acc_bal}</div></div>", unsafe_allow_html=True)
        
        st.write("---")
        c_oa1, c_oa2 = st.columns(2)
        c_oa1.markdown(f"#### {tr('آج کی طلباء کی حاضری', 'Today Student Attendance')}")
        c_oa1.progress(int(o_stu_att_perc) / 100)
        c_oa1.caption(f"{o_stu_att_perc:.1f}% ({o_stu_pres} Present)")
        
        c_oa2.markdown(f"#### {tr('آج کی سٹاف کی حاضری', 'Today Staff Attendance')}")
        c_oa2.progress(int(o_stf_att_perc) / 100)
        c_oa2.caption(f"{o_stf_att_perc:.1f}% ({o_stf_pres} Present)")

# ================= 10.5. ڈسپلن اور میرٹ سسٹم (Discipline & Merit) =================
elif core_choice in ["ڈسپلن اور میرٹ", "Discipline & Merit"]:
    st.markdown(f"<h2 class='no-print'>⭐ {tr('سٹوڈنٹ ڈسپلن اور میرٹ سسٹم', 'Student Discipline & Merit System')}</h2>", unsafe_allow_html=True)
    st.write(tr("طلباء کی کارکردگی، اخلاقیات، اور نظم و ضبط کا ریکارڈ رکھیں۔", "Track student performance, behavior, and disciplinary records."))
    
    # 🟢 آٹو ڈیٹا بیس ٹیبل بنانا (اگر پہلے سے موجود نہ ہو)
    cursor.execute('''CREATE TABLE IF NOT EXISTS discipline (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT,
        reg_id TEXT,
        record_type TEXT,
        category TEXT,
        points INTEGER,
        remarks TEXT,
        reported_by TEXT
    )''')
    conn.commit()

    tab_add, tab_report, tab_leaderboard, tab_certs = st.tabs(["✨ " + tr("نیا ریکارڈ درج کریں", "Add New Record"), "📜 " + tr("بیہیویئر رپورٹ اور پرنٹ", "Behavior Report & Print"), "🏆 " + tr("سٹار طلباء لیڈر بورڈ", "Star Students Leaderboard"), "🏅 " + tr("سرٹیفکیٹس", "Certificates")])

    # 🟢 ڈیٹا بیس سے تمام کالمز (بشمول gender) نکالنا
    try: 
        st_df = pd.read_sql("SELECT * FROM students WHERE status='Active'", conn)
    except: 
        st_df = pd.DataFrame()

    # ================= 1. نیا ریکارڈ درج کریں =================
    with tab_add:
        st.markdown(f"#### 📝 {tr('طالب علم کی کارکردگی یا شکایت درج کریں', 'Log Student Performance or Complaint')}")
        
        if not st_df.empty:
            c_da1, c_da2 = st.columns(2)
            classes_avail = sorted(st_df['class'].unique().tolist())
            sel_cls = c_da1.selectbox(tr("کلاس منتخب کریں", "Select Class"), classes_avail, key="d_cls")
            
            cls_students = st_df[st_df['class'] == sel_cls]
            st_opts = [f"{r['name']} (S/O {r['fname']}) - ID:{r['reg_id']}" for _, r in cls_students.iterrows()]
            sel_st = c_da2.selectbox(tr("طالب علم منتخب کریں", "Select Student"), st_opts, key="d_stu")
            stu_reg = sel_st.split("ID:")[1]
            
            st.write("---")
            
            col_type, col_cat, col_pts = st.columns(3)
            
            rec_type = col_type.radio(tr("ریکارڈ کی قسم (Record Type)", "Record Type"), ["🌟 Merit (اچھائی/انعام)", "⚠️ Demerit (غلطی/شکایت)"])
            
            if "⚠️" in rec_type or "Demerit" in rec_type:
                cat_opts_en = ["Homework Missing", "Bad Behavior", "Late Arrival", "Improper Uniform", "Fighting / Bullying", "Using Bad Language", "Damaging Property", "Other"]
                cat_opts_ur = ["ہوم ورک نہیں کیا", "خراب رویہ / بدتمیزی", "دیر سے آنا", "نامکمل یونیفارم", "لڑائی جھگڑا / تنگ کرنا", "گالی گلوچ", "سکول کی پراپرٹی کا نقصان", "دیگر (Other)"]
                default_pts = -5
            else:
                cat_opts_en = ["Excellent Homework", "Good Behavior", "Helping Others", "Punctuality", "Neat Uniform", "Sports Achievement", "Class Participation", "Other"]
                cat_opts_ur = ["بہترین ہوم ورک", "اچھا رویہ / اخلاق", "دوسروں کی مدد کرنا", "وقت کی پابندی", "صاف ستھرا یونیفارم", "کھیلوں میں شاندار کارکردگی", "کلاس میں بہترین حصہ لینا", "دیگر (Other)"]
                default_pts = 5
                
            display_opts = cat_opts_en if st.session_state.ui_lang == "English" else cat_opts_ur
            category = col_cat.selectbox(tr("کیٹیگری (Category)", "Category"), display_opts)
            points = col_pts.number_input(tr("پوائنٹس (Points)", "Points"), value=default_pts, help=tr("میرٹ کے لیے پلس (+)، ڈی میرٹ کے لیے مائنس (-) استعمال کریں", "Use + for Merit, - for Demerit"))
            
            c_d_rem1, c_d_rem2 = st.columns([3, 1])
            remarks = c_d_rem1.text_input(tr("تفصیلات / ریمارکس لکھیں (Remarks)", "Enter Details / Remarks"), placeholder=tr("مثلاً: آج اس نے پوری کلاس کی مدد کی...", "e.g., Helped a classmate today..."))
            reported_by = c_d_rem2.text_input(tr("رپورٹ کرنے والا", "Reported By"), value=st.session_state.current_user)
            d_date = st.date_input(tr("تاریخ", "Date"), datetime.date.today())
            
            if st.button(tr("ریکارڈ محفوظ کریں", "Save Record"), type="primary", use_container_width=True):
                cat_index = display_opts.index(category)
                db_category = cat_opts_en[cat_index]
                
                cursor.execute("INSERT INTO discipline (date, reg_id, record_type, category, points, remarks, reported_by) VALUES (?, ?, ?, ?, ?, ?, ?)", (d_date.strftime("%Y-%m-%d"), stu_reg, rec_type.split(" ")[1], db_category, points, remarks, reported_by))
                conn.commit()
                st.success(tr("ریکارڈ کامیابی سے محفوظ ہو گیا!", "Record saved successfully!"))
                import time
                time.sleep(1)
                st.rerun()
        else:
            st.warning(tr("کوئی ایکٹو طالب علم موجود نہیں۔", "No active students found."))

    # ================= 2. بیہیویئر رپورٹ اور پرنٹ =================
    with tab_report:
        st.markdown(f"#### 📜 {tr('طالب علم کی مکمل ڈسپلن رپورٹ', 'Student Detailed Discipline Report')}")
        if not st_df.empty:
            c_r1, c_r2 = st.columns([1, 2])
            r_cls = c_r1.selectbox(tr("کلاس", "Class"), sorted(st_df['class'].unique().tolist()), key="r_cls")
            r_students = st_df[st_df['class'] == r_cls]
            r_opts = [f"{r['name']} (S/O {r['fname']}) - ID:{r['reg_id']}" for _, r in r_students.iterrows()]
            r_sel_st = c_r2.selectbox(tr("طالب علم", "Student"), r_opts, key="r_stu")
            r_reg = r_sel_st.split("ID:")[1]
            
            stu_info = st_df[st_df['reg_id'] == r_reg].iloc[0]
            
            d_df = pd.read_sql(f"SELECT date as 'Date', record_type as 'Type', category as 'Category', points as 'Points', remarks as 'Remarks', reported_by as 'Reported By' FROM discipline WHERE reg_id='{r_reg}' ORDER BY id DESC", conn)
            
            total_merit = d_df[d_df['Type'] == 'Merit']['Points'].sum() if not d_df.empty else 0
            total_demerit = d_df[d_df['Type'] == 'Demerit']['Points'].sum() if not d_df.empty else 0
            net_score = total_merit + total_demerit
            
            if net_score >= 50: grade, g_color, icon = "Outstanding ⭐⭐⭐", "#155724", "🌟"
            elif net_score >= 20: grade, g_color, icon = "Very Good ⭐⭐", "#005b36", "👍"
            elif net_score >= 0: grade, g_color, icon = "Satisfactory ⭐", "#0c5460", "🙂"
            elif net_score >= -20: grade, g_color, icon = "Needs Improvement ⚠️", "#856404", "⚠️"
            else: grade, g_color, icon = "Critical Warning 🚨", "#721c24", "🚨"
            
            c_m1, c_m2, c_m3, c_m4 = st.columns(4)
            c_m1.metric(tr("میرٹ پوائنٹس (+)", "Merit Points (+)"), f"+{total_merit}")
            c_m2.metric(tr("ڈی-میرٹ پوائنٹس (-)", "Demerit Points (-)"), f"{total_demerit}")
            c_m3.metric(tr("کل سکور (Net Score)", "Net Score"), net_score)
            c_m4.markdown(f"<div style='text-align:center; padding:10px; border-radius:10px; background-color:{g_color}22; color:{g_color}; font-weight:bold;'>{icon} {grade}</div>", unsafe_allow_html=True)
            
            st.write("---")
            if not d_df.empty:
                st.dataframe(d_df, use_container_width=True, hide_index=True)
                
                school_n = school_name.upper() if school_name else "SCHOOL SYSTEM"
                t = {"align": "left", "dir": "ltr"} if st.session_state.ui_lang == "English" else {"align": "right", "dir": "rtl"}
                
                table_html = d_df.to_html(index=False, classes="report-table", border=0)
                table_html = table_html.replace('<th>', f'<th style="background-color:#f0f2f5; color:#333; border-bottom:2px solid #ccc; padding:10px; text-align:{t["align"]};">')
                table_html = table_html.replace('<td>', f'<td style="border-bottom:1px solid #eee; padding:10px; text-align:{t["align"]};">')
                
                print_html = f"""
                <div style="font-family: Arial, sans-serif; padding: 30px; background: white;" dir="{t['dir']}">
                    <div style="text-align: center; border-bottom: 3px solid #1a4f8b; padding-bottom: 15px; margin-bottom: 25px;">
                        {f'<img src="{logo_src_b64}" style="height: 70px; margin-bottom:10px;">' if logo_src_b64 else ''}
                        <h1 style="margin: 0; color: #1a4f8b; font-size: 26px;">{school_n}</h1>
                        <p style="margin: 5px 0; color: #555; font-size: 14px;">{school_address}</p>
                        <h2 style="margin: 15px 0 0 0; background-color: #1a4f8b; color: white; display: inline-block; padding: 5px 20px; border-radius: 20px; font-size: 16px; letter-spacing: 1px;">STUDENT BEHAVIOR & DISCIPLINE REPORT</h2>
                    </div>
                    
                    <table style="width: 100%; margin-bottom: 25px; border-collapse: collapse; font-size: 14px;">
                        <tr>
                            <td style="padding: 8px; border: 1px solid #ddd;"><b>Student Name:</b> {stu_info['name']}</td>
                            <td style="padding: 8px; border: 1px solid #ddd;"><b>Reg No:</b> {r_reg}</td>
                        </tr>
                        <tr>
                            <td style="padding: 8px; border: 1px solid #ddd;"><b>Father Name:</b> {stu_info['fname']}</td>
                            <td style="padding: 8px; border: 1px solid #ddd;"><b>Class/Section:</b> {stu_info['class']} ({stu_info['section']})</td>
                        </tr>
                    </table>
                    
                    <div style="display: flex; justify-content: space-between; margin-bottom: 30px; text-align: center;">
                        <div style="width: 23%; border: 2px solid #28a745; border-radius: 10px; padding: 15px; background: #f8fff9;">
                            <div style="font-size: 12px; color: #28a745; font-weight: bold; text-transform: uppercase;">Merit Points</div>
                            <div style="font-size: 24px; font-weight: bold; color: #155724;">+{total_merit}</div>
                        </div>
                        <div style="width: 23%; border: 2px solid #dc3545; border-radius: 10px; padding: 15px; background: #fff8f8;">
                            <div style="font-size: 12px; color: #dc3545; font-weight: bold; text-transform: uppercase;">Demerit Points</div>
                            <div style="font-size: 24px; font-weight: bold; color: #721c24;">{total_demerit}</div>
                        </div>
                        <div style="width: 23%; border: 2px solid #005b36; border-radius: 10px; padding: 15px; background: #f0f7f4;">
                            <div style="font-size: 12px; color: #005b36; font-weight: bold; text-transform: uppercase;">Net Score</div>
                            <div style="font-size: 24px; font-weight: bold; color: #000;">{net_score}</div>
                        </div>
                        <div style="width: 23%; border: 2px solid {g_color}; border-radius: 10px; padding: 15px; background: {g_color}11;">
                            <div style="font-size: 12px; color: {g_color}; font-weight: bold; text-transform: uppercase;">Current Status</div>
                            <div style="font-size: 16px; font-weight: bold; color: {g_color}; margin-top: 5px;">{icon} {grade.split(' ')[0]}</div>
                        </div>
                    </div>
                    
                    <h3 style="color: #333; font-size: 16px; border-bottom: 2px solid #ccc; padding-bottom: 5px; margin-bottom: 15px;">Detailed Disciplinary Log</h3>
                    <div style="width: 100%; border: 1px solid #ddd; border-radius: 8px; overflow: hidden;">
                        <table style="width:100%; border-collapse: collapse; font-size:12px;">
                            {table_html.replace('<table border="0" class="dataframe report-table">', '').replace('</table>', '')}
                        </table>
                    </div>
                    
                    <table style="width: 100%; border: none; margin-top: 60px; font-size: 13px;">
                        <tr>
                            <td style="text-align: left; width: 33%;">________________________<br><br><b>Class Teacher Sign</b></td>
                            <td style="text-align: center; width: 33%;">________________________<br><br><b>Parents Sign</b></td>
                            <td style="text-align: right; width: 33%;">________________________<br><br><b>Principal Sign</b></td>
                        </tr>
                    </table>
                </div>
                """
                st.write("")
                print_button_js(print_html, tr("🖨️ یہ رپورٹ پرنٹ کریں", "🖨️ Print Behavior Report"), landscape=False)
            else:
                st.info(tr("اس طالب علم کا کوئی ڈسپلن یا میرٹ ریکارڈ موجود نہیں۔", "No discipline or merit records found for this student."))

    # ================= 3. لیڈر بورڈ اور الرٹس =================
    with tab_leaderboard:
        st.markdown(f"#### 🏆 {tr('سکول کے سٹار طلباء اور ڈیفالٹرز', 'School Star Students & Defaulters')}")
        st.write(tr("یہ سسٹم تمام طلباء کے پوائنٹس جمع کر کے آٹو میٹک لیڈر بورڈ بناتا ہے۔", "This system aggregates all points and creates an automatic leaderboard."))
        
        lb_query = """
        SELECT d.reg_id, s.name, s.class, s.section, SUM(d.points) as net_score 
        FROM discipline d JOIN students s ON d.reg_id = s.reg_id 
        GROUP BY d.reg_id 
        ORDER BY net_score DESC
        """
        try: lb_df = pd.read_sql(lb_query, conn)
        except: lb_df = pd.DataFrame()
        
        if not lb_df.empty:
            c_lb1, c_lb2 = st.columns(2)
            
            with c_lb1:
                st.markdown(f"<h3 style='color:#155724; background-color:#d4edda; padding:10px; border-radius:5px; text-align:center;'>🌟 {tr('ٹاپ 5 سٹار طلباء', 'Top 5 Star Students')}</h3>", unsafe_allow_html=True)
                top_stars = lb_df[lb_df['net_score'] > 0].head(5)
                if not top_stars.empty:
                    for i, r in top_stars.iterrows():
                        st.success(f"**{r['name']}** (Class: {r['class']} {r['section']}) — Score: **+{r['net_score']}** 🏆")
                else: st.write("کوئی سٹار طالب علم نہیں۔")
                
            with c_lb2:
                st.markdown(f"<h3 style='color:#721c24; background-color:#f8d7da; padding:10px; border-radius:5px; text-align:center;'>🚨 {tr('توجہ طلب طلباء (Warnings)', 'Students Needing Attention')}</h3>", unsafe_allow_html=True)
                bottom_students = lb_df[lb_df['net_score'] < 0].sort_values('net_score').head(5)
                if not bottom_students.empty:
                    for i, r in bottom_students.iterrows():
                        st.error(f"**{r['name']}** (Class: {r['class']} {r['section']}) — Score: **{r['net_score']}** ⚠️")
                else: st.write("کوئی ڈیفالٹر طالب علم نہیں۔")
        else:
            st.info(tr("ڈیٹا بیس میں کوئی ریکارڈ موجود نہیں۔", "No records exist in the database."))

    # ================= 4. سرٹیفکیٹس (Certificates) =================
    with tab_certs:
        st.markdown(f"#### 🏅 {tr('پروفیشنل سٹار سرٹیفکیٹس', 'Professional Star Certificates')}")
        st.write(tr("اپنے بہترین طلباء کے لیے شاندار سرٹیفکیٹس جنریٹ کریں۔", "Generate stunning certificates for your outstanding students."))
        
        is_eng = st.session_state.ui_lang == "English"
        t_dir = "ltr" if is_eng else "rtl"
        
        # 🟢 نستعلیق فونٹ کا ویب لنک
        if is_eng:
            font_css = ""
            f_family = "'Arial', sans-serif"
            cert_of_exc = "CERTIFICATE OF EXCELLENCE"
            proudly_presented = "This is proudly presented to"
            class_lbl = "Class:"
            date_lbl = "Date:"
            prin_lbl = "Principal"
            sign_lbl = "Signature"
        else:
            font_css = "<style>@import url('https://fonts.googleapis.com/css2?family=Noto+Nastaliq+Urdu:wght@400;700&display=swap');</style>"
            f_family = "'Jameel Noori Nastaliq', 'Noto Nastaliq Urdu', 'Nafees Web Naskh', Arial, sans-serif"
            cert_of_exc = "اعزازی سند (Certificate of Excellence)"
            proudly_presented = "یہ سند فخر کے ساتھ پیش کی جاتی ہے بطرف:"
            class_lbl = "کلاس:"
            date_lbl = "تاریخ:"
            prin_lbl = "پرنسپل"
            sign_lbl = "دستخط"
            
        if not st_df.empty:
            c_c1, c_c2 = st.columns(2)
            c_cls = c_c1.selectbox(tr("کلاس", "Class"), sorted(st_df['class'].unique().tolist()), key="c_cls")
            c_students = st_df[st_df['class'] == c_cls]
            c_opts = [f"{r['name']} (S/O {r['fname']}) - ID:{r['reg_id']}" for _, r in c_students.iterrows()]
            c_sel_st = c_c2.selectbox(tr("طالب علم", "Student"), c_opts, key="c_stu")
            c_reg = c_sel_st.split("ID:")[1]
            
            stu_info_cert = st_df[st_df['reg_id'] == c_reg].iloc[0]
            
            stu_gender = str(stu_info_cert.get('gender', 'Male')).strip().lower()
            if stu_gender in ['female', 'girl', 'f', 'عورت', 'لڑکی', 'بچی']:
                rel_label = "D/O" if is_eng else "بنتِ"
            else:
                rel_label = "S/O" if is_eng else "ولد"
            
            c_t1, c_t2 = st.columns(2)
            
            doc_opts_en = ["Star of the Month", "Star of the Week", "Student of the Year", "Outstanding Behavior"]
            doc_opts_ur = ["مہینے کا بہترین طالب علم (Star of the Month)", "ہفتے کا بہترین طالب علم (Star of the Week)", "سال کا بہترین طالب علم (Student of the Year)", "بہترین اخلاق و کردار (Outstanding Behavior)"]
            doc_opts = doc_opts_en if is_eng else doc_opts_ur
            
            cert_type_sel = c_t1.selectbox(tr("سرٹیفکیٹ کی قسم", "Certificate Type"), doc_opts)
            cert_type = doc_opts_en[doc_opts.index(cert_type_sel)]
            cert_date = c_t2.date_input(tr("جاری کرنے کی تاریخ", "Issue Date"), datetime.date.today(), key="c_date")
            
            if "Month" in cert_type:
                bg_color = "linear-gradient(135deg, #f6d365 0%, #fda085 100%)"
                ribbon_color = "#d9534f"
                title = "STAR OF THE MONTH" if is_eng else "مہینے کا بہترین طالب علم"
                cert_desc = "In recognition of outstanding performance, excellent behavior, and dedication during this month. We are incredibly proud of your continuous efforts and achievements!" if is_eng else "اس ماہ کے دوران شاندار کارکردگی، بہترین اخلاق اور لگن کے اعتراف میں۔ ہمیں آپ کی مسلسل محنت اور کامیابیوں پر بے حد فخر ہے!"
            elif "Week" in cert_type:
                bg_color = "linear-gradient(135deg, #84fab0 0%, #8fd3f4 100%)"
                ribbon_color = "#17a2b8"
                title = "STAR OF THE WEEK" if is_eng else "ہفتے کا بہترین طالب علم"
                cert_desc = "Awarded for demonstrating consistent hard work, great discipline, and positive attitude throughout the week. Keep shining brightly!" if is_eng else "پورا ہفتہ مسلسل محنت، بہترین ڈسپلن اور مثبت رویہ ظاہر کرنے پر یہ سند دی جاتی ہے۔ اسی طرح چمکتے رہیں!"
            elif "Year" in cert_type:
                bg_color = "linear-gradient(135deg, #FFD700 0%, #B8860B 100%)"
                ribbon_color = "#2E8B57"
                title = "STUDENT OF THE YEAR" if is_eng else "سال کا بہترین طالب علم"
                cert_desc = "Awarded for exceptional academic excellence, exemplary character, and outstanding overall performance throughout the academic year. A truly remarkable and proud achievement!" if is_eng else "تعلیمی سال کے دوران شاندار تعلیمی کارکردگی، مثالی کردار اور مجموعی طور پر بہترین کارکردگی پر یہ سند دی جاتی ہے۔ یہ واقعی ایک قابلِ فخر اور شاندار کامیابی ہے!"
            else:
                bg_color = "linear-gradient(135deg, #a1c4fd 0%, #c2e9fb 100%)"
                ribbon_color = "#005b36"
                title = "OUTSTANDING BEHAVIOR" if is_eng else "بہترین اخلاق و کردار"
                cert_desc = "In recognition of exemplary conduct, excellent manners, and serving as a highly positive role model for peers. Thank you for your outstanding behavior!" if is_eng else "مثالی رویے، بہترین آداب اور دوسرے طلباء کے لیے ایک مثبت رول ماڈل بننے کے اعتراف میں۔ آپ کے شاندار اخلاق کا بہت شکریہ!"

            school_n_cert = school_name.upper() if school_name else "SCHOOL SYSTEM"
            watermark_html = f"""<div style="position: absolute; top: 0; left: 0; right: 0; bottom: 0; background-image: url('{logo_src_b64}'); background-position: center; background-repeat: no-repeat; background-size: 55%; opacity: 0.08; z-index: 0; pointer-events: none;"></div>""" if logo_src_b64 else ""
            
            # 🟢 Flexbox کا استعمال کر کے لے آؤٹ کو فکس کر دیا گیا ہے
            cert_html = f"""
            {font_css}
            <div style="padding: 15px; background: {bg_color}; font-family: {f_family}; border-radius: 15px; box-shadow: 0 10px 30px rgba(0,0,0,0.2); position: relative; overflow: hidden; width: 100%; max-width: 1050px; height: 660px; margin: 0 auto; box-sizing: border-box; text-align: center; page-break-inside: avoid;" dir="{t_dir}">
                <div style="border: 4px double white; padding: 25px; border-radius: 10px; background: rgba(255, 255, 255, 0.95); position: relative; height: 100%; box-sizing: border-box; z-index: 1; display: flex; flex-direction: column; justify-content: space-between;">
                    
                    <!-- Watermark Layer -->
                    {watermark_html}
                    
                    <div style="position: absolute; top: -10px; left: -10px; width: 50px; height: 50px; border-top: 5px solid {ribbon_color}; border-left: 5px solid {ribbon_color}; z-index: 2;"></div>
                    <div style="position: absolute; top: -10px; right: -10px; width: 50px; height: 50px; border-top: 5px solid {ribbon_color}; border-right: 5px solid {ribbon_color}; z-index: 2;"></div>
                    <div style="position: absolute; bottom: -10px; left: -10px; width: 50px; height: 50px; border-bottom: 5px solid {ribbon_color}; border-left: 5px solid {ribbon_color}; z-index: 2;"></div>
                    <div style="position: absolute; bottom: -10px; right: -10px; width: 50px; height: 50px; border-bottom: 5px solid {ribbon_color}; border-right: 5px solid {ribbon_color}; z-index: 2;"></div>
                    
                    <div style="position: relative; z-index: 2; flex-grow: 1;">
                        {f'<img src="{logo_src_b64}" style="height: 70px; margin-bottom: 5px;">' if logo_src_b64 else '<div style="font-size: 40px;">🏫</div>'}
                        <h1 style="margin: 0; color: #333; font-size: 28px; letter-spacing: 2px; font-family: 'Arial', sans-serif;">{school_n_cert}</h1>
                        <p style="color: #666; font-size: 13px; margin-top: 2px; font-family: 'Arial', sans-serif;">{cert_of_exc}</p>
                        
                        <div style="margin: 15px auto; background-color: {ribbon_color}; color: white; padding: 8px 40px; display: inline-block; font-size: 24px; font-weight: bold; letter-spacing: 2px; border-radius: 5px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                            {title}
                        </div>
                        
                        <p style="font-size: 15px; color: #555; margin-top: 10px;">{proudly_presented}</p>
                        
                        <h2 style="font-size: 46px; color: #000; margin: 0 0 5px 0; border-bottom: 2px solid #ccc; display: inline-block; padding-bottom: 5px; line-height: 1.4;">{stu_info_cert['name']}</h2>
                        
                        <div style="font-size: 17px; color: #333; margin-top: 5px; margin-bottom: 15px;">
                            <b>{class_lbl}</b> {stu_info_cert['class']} ({stu_info_cert['section']}) &nbsp;&nbsp;|&nbsp;&nbsp; <b>{rel_label}</b> <span style="font-size: 20px;">{stu_info_cert['fname']}</span>
                        </div>
                        
                        <p style="font-size: 15px; color: #555; line-height: 1.6; max-width: 700px; margin: 0 auto; text-align: center;">
                            {cert_desc}
                        </p>
                    </div>
                    
                    <table style="width: 100%; font-family: 'Arial', sans-serif; position: relative; z-index: 2; margin-top: auto;">
                        <tr>
                            <td style="width: 33%; text-align: center; vertical-align: bottom;">
                                <div style="border-top: 2px solid #000; display: inline-block; width: 140px; padding-top: 5px; font-weight: bold; font-size: 13px;">{date_lbl}</div>
                                <div style="font-size: 12px; color: #555; margin-top: 5px;">{cert_date.strftime("%d %B, %Y")}</div>
                            </td>
                            <td style="width: 33%; text-align: center;">
                                <div style="font-size: 45px; line-height: 1;">🏅</div>
                            </td>
                            <td style="width: 33%; text-align: center; vertical-align: bottom;">
                                <div style="border-top: 2px solid #000; display: inline-block; width: 140px; padding-top: 5px; font-weight: bold; font-size: 13px;">{prin_lbl}</div>
                                <div style="font-size: 12px; color: #555; margin-top: 5px;">{sign_lbl}</div>
                            </td>
                        </tr>
                    </table>
                </div>
            </div>
            """
            
            st.write("---")
            st.markdown(cert_html, unsafe_allow_html=True)
            st.write("---")
            
            c_p1, c_p2 = st.columns([1, 2])
            with c_p1:
                print_button_js(cert_html, tr("🖨️ پرنٹ سرٹیفکیٹ (Print)", "🖨️ Print Certificate"), landscape=True)
        else:
            st.warning(tr("کوئی طالب علم موجود نہیں۔", "No students found."))

# ================= 11. نوٹس بورڈ (Notice Board) =================
elif core_choice in ["نوٹس بورڈ", "Notice Board"]:
    st.markdown(f"<h2 class='no-print'>📢 {tr('نوٹس بورڈ', 'Notice Board')} - {tr(sub_choice, sub_choice)}</h2>", unsafe_allow_html=True)
    
    # 🟢 اگر یوزر "والدین" (Guardian) ہے تو اسے صرف نوٹس دیکھنے کا اختیار دیں (بنانے یا پرنٹ کا نہیں)
    if st.session_state.current_role == "Guardian":
        st.markdown(f"#### 📌 {tr('سکول کے تازہ ترین نوٹسز اور سرکولرز', 'Latest School Notices & Circulars')}")
        df_notices = pd.read_sql("SELECT id, date as Date, audience as Audience, title as Title, details as Details FROM notices WHERE audience IN ('All', 'Students') ORDER BY id DESC", conn)
        
        if not df_notices.empty:
            for _, r in df_notices.iterrows():
                with st.expander(f"📌 {r['Date']} | {r['Title']}"):
                    st.write(r['Details'])
        else:
            st.info(tr("کوئی نوٹس موجود نہیں۔", "No notices found."))
            
    else:
        # 🟢 ایڈمن اور ٹیچر کے لیے پرانا مکمل نظام (نیا نوٹس بنانا، پرنٹ اور ڈیلیٹ کرنا)
        if sub_choice == "New Notice":
            with st.form("notice_form"):
                n_title = st.text_input(tr("نوٹس کا عنوان *", "Notice Title *"))
                n_aud = st.selectbox(tr("کس کے لیے ہے؟ (Audience)", "Audience"), ["All", "Students", "Staff"])
                n_det = st.text_area(tr("نوٹس کی تفصیل *", "Notice Details *"))
                
                if st.form_submit_button(tr("نوٹس شائع کریں", "Publish Notice")):
                    if n_title and n_det:
                        cursor.execute("INSERT INTO notices (date, audience, title, details) VALUES (?, ?, ?, ?)", (today_date, n_aud, n_title, n_det))
                        conn.commit()
                        st.success(tr("نوٹس کامیابی سے شائع ہو گیا!", "Notice Published Successfully!"))
                    else:
                        st.error(tr("عنوان اور تفصیل لکھنا لازمی ہے۔", "Title and Details are required."))
                        
        elif sub_choice == "All Notices":
            df_notices = pd.read_sql("SELECT id, date as Date, audience as Audience, title as Title, details as Details FROM notices ORDER BY id DESC", conn)
            if not df_notices.empty:
                logo_base64_html = f'<img src="{logo_src_b64}" style="max-width: 80px; max-height: 80px; object-fit: contain;">' if logo_src_b64 else '<div style="font-size:35px;">🏫</div>'
                
                for _, r in df_notices.iterrows():
                    with st.expander(f"📌 {r['Date']} | {r['Title']} ({tr('For:', 'For:')} {r['Audience']})"):
                        st.write(r['Details'])
                        
                        t = {"align": "left", "dir": "ltr"} if st.session_state.ui_lang == "English" else {"align": "right", "dir": "rtl"}
                        notice_html = f"""
                        <div style="border: 4px double #005b36; padding: 20px; width: 100%; max-width: 800px; min-height: 270mm; height: auto; margin: 0 auto; background-color: white; color: black; box-sizing: border-box; overflow: visible;" dir="{t['dir']}">
                            <table style="width: 100%; border: none; margin-bottom: 15px; border-bottom: 2px solid #d4af37; padding-bottom: 10px;">
                                <tr>
                                    <td style="width: 20%; text-align: {t['align']}; vertical-align: middle;">{logo_base64_html}</td>
                                    <td style="width: 60%; text-align: center; vertical-align: middle;">
                                        <h1 style="margin: 0; font-size: 28px; color: #005b36; font-weight: bold; font-family: 'Arial', sans-serif;">{school_name.upper()}</h1>
                                        <p style="margin: 5px 0; font-size: 14px; font-weight: bold; font-family: 'Arial', sans-serif;">{school_address}</p>
                                    </td>
                                    <td style="width: 20%; text-align: right; vertical-align: middle;"></td>
                                </tr>
                            </table>
                            <h2 style="text-align: center; font-size: 22px; color: #005b36; text-decoration: underline; margin-bottom: 20px; font-family: 'Arial', sans-serif;">{tr('نوٹس بورڈ', 'NOTICE BOARD')}</h2>
                            
                            <table style="width: 100%; border: none; margin-bottom: 20px; font-size: 14px; font-weight: bold; font-family: 'Arial', sans-serif;">
                                <tr>
                                    <td style="text-align: {t['align']}; width: 50%;">{tr('تاریخ:', 'Date:')} {r['Date']}</td>
                                    <td style="text-align: {'right' if t['align']=='left' else 'left'}; width: 50%;">{tr('برائے:', 'To:')} {r['Audience']}</td>
                                </tr>
                            </table>
                            
                            <div style="direction: rtl; text-align: right;">
                                <h3 style="font-size: 18px; color: #005b36; margin-bottom: 10px; font-family: 'Arial', sans-serif;">{tr('عنوان:', 'Subject:')} {r['Title']}</h3>
                                <div style="font-size: 16px; line-height: 1.8; margin-bottom: 20px; min-height: 150px; white-space: pre-wrap; font-family: 'Jameel Noori Nastaleeq', 'Urdu Typesetting', Arial, sans-serif;">
                                    {r['Details']}
                                </div>
                            </div>
                            
                            <table style="width: 100%; border: none; margin-top: 30px; font-size: 14px; font-family: 'Arial', sans-serif;">
                                <tr>
                                    <td style="text-align: {t['align']}; width: 50%;"></td>
                                    <td style="text-align: {'right' if t['align']=='left' else 'left'}; width: 50%;">
                                        ___________________<br><br><b>{tr('پرنسپل / ایڈمن', 'Principal / Admin')}</b><br>{school_name}
                                    </td>
                                </tr>
                            </table>
                        </div>
                        """
                        
                        st.write("")
                        col_b1, col_b2 = st.columns([1, 4])
                        if col_b1.button("🗑️ " + tr("ڈیلیٹ کریں", "Delete Notice"), key=f"del_not_{r['id']}"):
                            cursor.execute(f"DELETE FROM notices WHERE id={r['id']}")
                            conn.commit()
                            st.rerun()
                        
                        with col_b2:
                            print_button_js(notice_html, tr("نوٹس پرنٹ کریں", "Print Notice"), landscape=False)
            else:
                st.info(tr("کوئی نوٹس موجود نہیں۔", "No notices found."))

# ================= 12. آئی ڈی کارڈ میکر =================
elif core_choice == "ID Card Maker":
    st.markdown(f"<h2 class='no-print'>🪪 {tr('آئی ڈی کارڈ میکر (QR Code کے ساتھ)', 'ID Card Maker (with QR)')}</h2>", unsafe_allow_html=True)
    st.markdown("<div class='no-print'>", unsafe_allow_html=True)
    
    c_mode, c_filt = st.columns(2)
    card_type = c_mode.radio(tr("کارڈ کی قسم منتخب کریں:", "Select Card Type:"), [tr("طلباء (Students)", "Students"), tr("سٹاف (Staff)", "Staff")], horizontal=True)
    
    if card_type in ["طلباء (Students)", "Students"]:
        id_class = c_filt.selectbox(tr("کلاس منتخب کریں", "Select Class"), ["All"] + classes_list)
        query = "SELECT * FROM students" if id_class == "All" else f"SELECT * FROM students WHERE class='{id_class}' AND status='Active'"
    else:
        distinct_desigs = pd.read_sql("SELECT DISTINCT designation FROM staff", conn)['designation'].dropna().tolist()
        disp_desigs = ["All"] + [get_desig_disp(d) for d in distinct_desigs]
        id_desig_disp = c_filt.selectbox(tr("عہدہ منتخب کریں", "Select Designation"), disp_desigs)
        
        if id_desig_disp == "All":
             query = "SELECT * FROM staff"
        else:
             actual_val = distinct_desigs[disp_desigs.index(id_desig_disp) - 1]
             query = f"SELECT * FROM staff WHERE designation='{actual_val}'"
        
    if st.button(tr("کارڈز جنریٹ کریں", "Generate Cards"), type="primary"):
        df_cards = pd.read_sql(query, conn)
        if not df_cards.empty:
            t = {"align": "left", "dir": "ltr"} if st.session_state.ui_lang == "English" else {"align": "right", "dir": "rtl"}
            
            cards_html = f'<div style="display: flex; flex-wrap: wrap; justify-content: center; gap: 20px; padding: 10px;" dir="{t["dir"]}">'
            
            for _, r in df_cards.iterrows():
                photo_data = r.get("photo")
                if photo_data:
                    b64_photo = base64.b64encode(photo_data).decode()
                    photo_src = f"data:image/jpeg;base64,{b64_photo}"
                else:
                    photo_src = "https://cdn-icons-png.flaticon.com/512/149/149071.png"
                
                d_name = get_disp_val(r['name'], r.get('name_en'))
                d_fname = get_disp_val(r['fname'], r.get('fname_en'))
                d_phone = r.get('phone', '-')
                try: 
                    d_dob_raw = r.get('dob', '-')
                    if d_dob_raw != '-':
                        d_dob = datetime.datetime.strptime(d_dob_raw, "%Y-%m-%d").strftime("%d-%m-%Y")
                    else: d_dob = '-'
                except: d_dob = r.get('dob', '-')
                
                cnic_bform_val = r.get('bform', '-') if card_type in ["طلباء (Students)", "Students"] else r.get('cnic', '-')
                d_address = get_disp_val(r.get('address', '-'), r.get('address_en', '-'))
                
                if card_type in ["طلباء (Students)", "Students"]:
                    r_id = r['reg_id']
                    id_label = tr("رول نمبر", "Reg No")
                    cnic_bform_label = tr("ب فارم", "B-Form")
                    g_val = str(r.get('gender', 'Boy'))
                    d_gender = tr("لڑکی", "Female") if "Girl" in g_val or "لڑکی" in g_val else (tr("دیگر", "Other") if "Other" in g_val or "دیگر" in g_val else tr("لڑکا", "Male"))
                    rel_label = get_relation_card_label(g_val, r.get('g_type', 'Father'))
                    
                    subtitle = f"{rel_label} {d_fname}"
                    extra_label = tr('کلاس', 'Class')
                    extra_val = f"{r['class']} ({r.get('section', 'A')})"
                    qr_data = f"Student Reg: {r_id}"
                else:
                    r_id = r['staff_id']
                    desig_val = get_desig_disp(r['designation'])
                    id_label = tr("سٹاف آئی ڈی", "Staff ID")
                    cnic_bform_label = tr("شناختی کارڈ", "CNIC")
                    g_val = str(r.get('gender', 'Male'))
                    d_gender = tr("عورت", "Female") if "Female" in g_val or "عورت" in g_val else (tr("دیگر", "Other") if "Other" in g_val or "دیگر" in g_val else tr("مرد", "Male"))
                    rel_label = get_relation_card_label(g_val, r.get('g_type', 'Father'))
                    
                    subtitle = f"{rel_label} {d_fname}"
                    extra_label = tr('عہدہ', 'Designation')
                    extra_val = desig_val
                    qr_data = f"Staff ID: {r_id}"
                
                # 🟢 کیو-آر کوڈ جنریٹ کرنے کا لائیو لنک
                qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=50x50&data={urllib.parse.quote(qr_data)}"
                
                prop_text = tr(f"یہ کارڈ {school_name} کی ملکیت ہے۔ ملنے پر سکول آفس میں جمع کروائیں۔", f"Property of {school_name}. If found, return to school office.")
                card_logo_html = f'<img src="{logo_src_b64}" style="width: 25px; height: 25px; object-fit: contain; background: white; border-radius: 50%; padding: 2px;">' if logo_src_b64 else ''
                watermark_html = f'<div style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; display: flex; align-items: center; justify-content: center; z-index: 0; opacity: 0.1;"><img src="{logo_src_b64}" style="width: 80%; object-fit: contain;"></div>' if logo_src_b64 else ''
                
                cards_html += f"""
                <div style="width: 2.125in; height: 3.375in; border: 1px solid #005b36; border-radius: 8px; box-shadow: 0 4px 8px rgba(0,0,0,0.2); background-color: #ebf5ee; position: relative; overflow: hidden; page-break-inside: avoid; display: flex; flex-direction: column; font-family: Arial, sans-serif;">
                    {watermark_html}
                    <div style="background-color: #005b36; color: white; padding: 6px; border-bottom: 3px solid #d4af37; display: flex; align-items: center; justify-content: center; gap: 5px; position: relative; z-index: 1;">
                        {card_logo_html}
                        <div style="text-align: center;">
                            <h4 style="margin: 0; font-size: 10px; text-transform: uppercase; line-height: 1.2;">{school_name}</h4>
                            <p style="margin: 2px 0 0 0; font-size: 6.5px; line-height: 1.1;">{school_address}</p>
                        </div>
                    </div>
                    <div style="text-align: center; margin-top: 5px; position: relative; z-index: 1; display: flex; justify-content: space-between; padding: 0 10px;">
                        <div style="width: 35px;"></div> <!-- Spacer -->
                        <div>
                            <img src="{photo_src}" style="width: 55px; height: 55px; border-radius: 50%; border: 2px solid #005b36; object-fit: cover; background: white;">
                        </div>
                        <div>
                            <img src="{qr_url}" style="width: 35px; height: 35px; border: 1px solid #ccc; background: white; padding: 1px; margin-top: 10px;">
                        </div>
                    </div>
                    <div style="text-align: center; position: relative; z-index: 1;">
                        <h3 style="margin: 3px 0 1px 0; font-size: 13px; color: #005b36; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; padding: 0 5px;">{d_name}</h3>
                        <p style="margin: 0; font-size: 10px; color: #d4af37; font-weight: bold; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; padding: 0 5px;">{subtitle}</p>
                    </div>
                    <div style="padding: 2px 10px; flex-grow: 1; display: flex; flex-direction: column; justify-content: center; position: relative; z-index: 1;">
                        <table style="width: 100%; font-size: 10px; font-weight: bold; line-height: 1.4; color: #000; text-align: {t['align']}; border: none;">
                            <tr><td style="border:none; padding:1px; width:35%; color: #005b36;">{id_label}:</td><td style="border:none; padding:1px;">{r_id}</td></tr>
                            <tr><td style="border:none; padding:1px; color: #005b36;">{extra_label}:</td><td style="border:none; padding:1px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">{extra_val}</td></tr>
                            <tr><td style="border:none; padding:1px; color: #005b36;">{cnic_bform_label}:</td><td style="border:none; padding:1px;">{cnic_bform_val}</td></tr>
                            <tr><td style="border:none; padding:1px; color: #005b36;">{tr('فون', 'Phone')}:</td><td style="border:none; padding:1px;">{d_phone}</td></tr>
                        </table>
                    </div>
                    <div style="padding: 3px 5px; text-align: center; font-size: 5.5px; color: #444; background-color: rgba(244, 244, 244, 0.85); border-top: 1px solid #ccc; line-height: 1.2; position: relative; z-index: 1;">
                        {prop_text}
                    </div>
                    <div style="background-color: #005b36; color: white; text-align: center; padding: 4px; font-size: 8px; position: relative; z-index: 1;">
                        <b>{tr('پرنسپل کے دستخط', 'Principal Signature')}</b>
                    </div>
                </div>
                """
            cards_html += "</div>"
            
            st.markdown("</div>", unsafe_allow_html=True)
            print_button_js(cards_html, tr("آئی ڈی کارڈز پرنٹ کریں", "Print ID Cards"), landscape=False)
            st.success(tr("✅ آئی ڈی کارڈز تیار ہیں! پرنٹ کا بٹن دبائیں۔", "✅ ID Cards Ready! Click the Print button."))
        else:
            st.warning(tr("کوئی ریکارڈ نہیں ملا۔", "No record found."))

# ================= 13. رپورٹس اور پرنٹنگ (Official & Comprehensive) =================
elif core_choice in ["رپورٹس", "Reports"]:
    st.markdown(f"<h2 class='no-print'>📊 {tr('دفتری اور جامع رپورٹس (Official Reports)', 'Official & Comprehensive Reports')}</h2>", unsafe_allow_html=True)
    st.markdown(f"<p class='no-print'>{tr('یہاں سے آپ سکول کے ریکارڈ کے لیے باقاعدہ دستخط شدہ اور آفیشل فارمیٹ میں رپورٹس پرنٹ کر سکتے ہیں۔', 'Generate official, signature-ready reports for school records.')}</p>", unsafe_allow_html=True)
    
    months_ur = ["جنوری", "فروری", "مارچ", "اپریل", "مئی", "جون", "جولائی", "اگست", "ستمبر", "اکتوبر", "نومبر", "دسمبر"]
    months_en = ["JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"]

    st.markdown("<div class='no-print'>", unsafe_allow_html=True)
    rep_opts_ur = ["طلباء کی رپورٹ", "سٹاف کی رپورٹ", "فیس کی رپورٹ", "تنخواہوں کی رپورٹ", "حاضری کی رپورٹ", "اکاؤنٹس روزنامچہ"]
    rep_opts_en = ["Students Report", "Staff Report", "Fees Report", "Salaries Report", "Attendance Report", "Accounts Ledger"]
    rep_opts_disp = rep_opts_ur if st.session_state.ui_lang == "اردو" else rep_opts_en
    
    rep_sel = st.selectbox(tr("رپورٹ کی قسم منتخب کریں", "Select Report Type"), rep_opts_disp)
    report_type = rep_opts_en[rep_opts_disp.index(rep_sel)]
    st.write("---")

    def get_official_header_footer(title, html_table, summary_html=""):
        t = get_translations(st.session_state.ui_lang)
        current_datetime = datetime.datetime.now().strftime("%d-%b-%Y %I:%M %p")
        logo_img = logo_base64_html.replace("max-height:80px", "max-height:60px").replace("max-width:80px", "max-width:60px")
        
        sign_titles = [tr("تیار کنندہ (Prepared By)", "Prepared By"), tr("چیک کنندہ (Checked By)", "Checked By"), tr("پرنسپل (Principal)", "Principal")]
        
        return f"""
        <div style="padding: 0; margin: 0 auto; width: 100%; box-sizing: border-box; background: white; height: auto; overflow: visible;">
            <div style="border: 2px solid #000; padding: 10px 15px; margin: 5px; width: calc(100% - 10px); box-sizing: border-box; background: white; font-family: 'Arial', sans-serif; {t['font']}; min-height: 100%; overflow: visible;" dir="{t['dir']}">
                
                <table style="width:100%; box-sizing: border-box; border-bottom: 2px solid #1a4f8b; padding-bottom: 10px; margin-bottom: 15px; page-break-inside: avoid;">
                    <tr>
                        <td style="width: 15%; text-align: {t['logo_align']}; vertical-align: middle;">{logo_img}</td>
                        <td style="width: 70%; text-align: center; vertical-align: middle;">
                            <h1 style="margin: 0; font-size: 22px; color: #1a4f8b;">{school_name.upper()}</h1>
                            <p style="margin: 3px 0; font-size: 13px; font-weight: bold;">{school_address}</p>
                            <p style="margin: 3px 0; font-size: 12px;">{tr('فون: ', 'Phone: ')} {school_phone} | {tr('رجسٹریشن: ', 'Reg: ')} {school_reg}</p>
                        </td>
                        <td style="width: 15%; text-align: {t['text_align_rev']}; vertical-align: middle;"></td>
                    </tr>
                </table>
                
                <div style="display: flex; justify-content: space-between; margin-bottom: 15px; box-sizing: border-box; page-break-inside: avoid;">
                    <h2 style="margin: 0; text-decoration: underline; font-size: 16px;">{title}</h2>
                    <span style="font-size: 12px; font-weight: bold;">{tr('پرنٹ کی تاریخ: ', 'Printed On: ')} {current_datetime}</span>
                </div>
                
                <div style="width:100%; box-sizing: border-box; font-size: 12px; overflow: visible; height: auto;">
                    {html_table}
                </div>
                
                <div style="width:100%; box-sizing: border-box; page-break-inside: avoid;">
                    {summary_html}
                </div>
                
                <table style="width:100%; box-sizing: border-box; margin-top: 50px; font-weight:bold; font-size: 13px; page-break-inside: avoid;" dir="{t['dir']}">
                    <tr>
                        <td style="text-align: center; width: 33%;"><hr style="width: 70%; border: 1px solid black; margin-bottom: 5px;">{sign_titles[0]}</td>
                        <td style="text-align: center; width: 33%;"><hr style="width: 70%; border: 1px solid black; margin-bottom: 5px;">{sign_titles[1]}</td>
                        <td style="text-align: center; width: 33%;"><hr style="width: 70%; border: 1px solid black; margin-bottom: 5px;">{sign_titles[2]}</td>
                    </tr>
                </table>
                
            </div>
        </div>
        """

    if report_type == "Students Report":
        c1, c2, c3, c4 = st.columns(4)
        filter_class = c1.selectbox(tr("کلاس", "Class"), [tr("سب", "All")] + classes_list)
        filter_section = c2.selectbox(tr("سیکشن", "Section"), [tr("سب", "All"), "A", "B", "C", "D"])
    if st.button(tr("رپورٹ تیار کریں", "Generate Report"), type="primary"):
            q_cond = []
            if filter_class != tr("سب", "All"): q_cond.append(f"class='{filter_class}'")
            if filter_section != tr("سب", "All"): q_cond.append(f"section='{filter_section}'")
            if filter_gender == tr("لڑکا", "Boy"): q_cond.append("gender='Boy'")
            elif filter_gender == tr("لڑکی", "Girl"): q_cond.append("gender='Girl'")
            if search_query: q_cond.append(f"(name LIKE '%{search_query}%' OR name_en LIKE '%{search_query}%' OR reg_id LIKE '%{search_query}%')")
            
            where_clause = " WHERE " + " AND ".join(q_cond) if q_cond else ""
            query = f"SELECT reg_id, name, name_en, gender, dob, bform, fname, fname_en, phone, address, class, section, adm_date FROM students{where_clause} ORDER BY CAST(reg_id AS INTEGER) ASC"
            df = pd.read_sql(query, conn)
            
            if not df.empty:
                t = get_translations(st.session_state.ui_lang)
                df['class_sec'] = df['class'].astype(str) + ' (' + df['section'].fillna('').astype(str) + ')'
                df['final_name'] = df.apply(lambda row: get_disp_val(row['name'], row.get('name_en')), axis=1)
                df['final_fname'] = df.apply(lambda row: get_disp_val(row['fname'], row.get('fname_en')), axis=1)
                
                if st.session_state.ui_lang == "اردو":
                    df['gender'] = df['gender'].replace({'Boy': 'لڑکا', 'Girl': 'لڑکی', 'Other': 'دیگر'})
                    df = df[['reg_id', 'final_name', 'final_fname', 'gender', 'dob', 'bform', 'phone', 'class_sec', 'adm_date']]
                    df.columns = ['رول نمبر', 'نام', 'والد/سرپرست', 'جنس', 'تاریخ پیدائش', 'ب فارم', 'فون نمبر', 'کلاس', 'تاریخ داخلہ']
                else:
                    df = df[['reg_id', 'final_name', 'final_fname', 'gender', 'dob', 'bform', 'phone', 'class_sec', 'adm_date']]
                    df.columns = ['Reg No', 'Student Name', 'Father/Guardian', 'Gender', 'DOB', 'B-Form', 'Phone', 'Class', 'Admission Date']
                
                html_table = df.to_html(classes="data-table", index=False, border=1, justify='center', na_rep='-')
                html_table = html_table.replace('class="dataframe data-table"', f'class="data-table" dir="{t["dir"]}" style="width:100%; box-sizing: border-box; border-collapse: collapse;"')
                
                disp_c = filter_class if filter_class != tr("سب", "All") else tr("تمام", "All")
                disp_s = filter_section if filter_section != tr("سب", "All") else tr("تمام", "All")
                heading_text = f"Official Students Record - Class: {disp_c} (Sec: {disp_s})" if st.session_state.ui_lang == "English" else f"طلباء کا دفتری ریکارڈ - کلاس: {disp_c} (سیکشن: {disp_s})"
                
                summary_html = f"<h4 style='text-align:{t['text_align_rev']}; margin-top:15px; color:#1a4f8b;'>{tr('کل طلباء: ', 'Total Students: ')} {len(df)}</h4>"
                
                print_html = get_official_header_footer(heading_text, html_table, summary_html)
                st.success(tr("رپورٹ تیار ہے! نیچے دیے گئے بٹن سے فوری پرنٹ کریں۔", "Report Ready! Use the button below to print."))
                print_button_js(print_html, tr("🖨️ فوری پرنٹ کریں (Print Report)", "🖨️ Print Report"), landscape=True)

                csv = df.to_csv(index=False).encode('utf-8')
                st.download_button(label=tr("📥 ایکسل (CSV) ڈاؤن لوڈ کریں", "📥 Download Excel (CSV)"), data=csv, file_name=f"Official_Students_Record_{today_date}.csv", mime="text/csv")
                
                st.write("---")
                st.dataframe(df, use_container_width=True)
            else: st.info(tr("کوئی ریکارڈ نہیں ملا۔", "No record found."))

    elif report_type == "Staff Report":
        if st.button(tr("سٹاف کی رپورٹ تیار کریں", "Generate Staff Report"), type="primary"):
            df = pd.read_sql("SELECT staff_id, name, name_en, cnic, phone, designation, joining_date, salary FROM staff ORDER BY CAST(staff_id AS INTEGER) ASC", conn)
            
            if not df.empty:
                t = get_translations(st.session_state.ui_lang)
                df['final_name'] = df.apply(lambda row: get_disp_val(row['name'], row.get('name_en')), axis=1)
                
                if st.session_state.ui_lang == "اردو":
                    df['designation'] = df['designation'].replace({"Teacher": "استاد / ٹیچر", "Principal": "پرنسپل", "Clerk": "کلرک", "Maid/Peon": "آیا / چپڑاسی", "Security Guard": "سیکیورٹی گارڈ"})
                    df = df[['staff_id', 'final_name', 'cnic', 'phone', 'designation', 'joining_date', 'salary']]
                    df.columns = ['سٹاف آئی ڈی', 'نام', 'شناختی کارڈ', 'فون نمبر', 'عہدہ', 'تاریخ شمولیت', 'تنخواہ']
                else:
                    df = df[['staff_id', 'final_name', 'cnic', 'phone', 'designation', 'joining_date', 'salary']]
                    df.columns = ['Staff ID', 'Name', 'CNIC', 'Phone', 'Designation', 'Join Date', 'Salary']
                
                html_table = df.to_html(classes="data-table", index=False, border=1, justify='center', na_rep='-')
                html_table = html_table.replace('class="dataframe data-table"', f'class="data-table" dir="{t["dir"]}" style="width:100%; box-sizing: border-box; border-collapse: collapse;"')
                
                heading_text = "Official Staff Details Record" if st.session_state.ui_lang == "English" else "سٹاف کا دفتری اور تفصیلی ریکارڈ"
                summary_html = f"<h4 style='text-align:{t['text_align_rev']}; margin-top:15px; color:#1a4f8b;'>{tr('کل سٹاف: ', 'Total Staff: ')} {len(df)} &nbsp; | &nbsp; {tr('کل ماہانہ تنخواہ: ', 'Total Monthly Salary: ')} Rs {df['Salary' if st.session_state.ui_lang == 'English' else 'تنخواہ'].sum():,}</h4>"
                
                print_html = get_official_header_footer(heading_text, html_table, summary_html)
                st.success(tr("رپورٹ تیار ہے! نیچے دیے گئے بٹن سے فوری پرنٹ کریں۔", "Report Ready! Use the button below to print."))
                print_button_js(print_html, tr("🖨️ فوری پرنٹ کریں (Print Report)", "🖨️ Print Report"), landscape=True)
                
                csv = df.to_csv(index=False).encode('utf-8')
                st.download_button(label=tr("📥 ایکسل (CSV) ڈاؤن لوڈ کریں", "📥 Download Excel (CSV)"), data=csv, file_name=f"Official_Staff_Report_{today_date}.csv", mime="text/csv")
                
                st.write("---")
                st.dataframe(df, use_container_width=True)
            else: st.info(tr("کوئی ریکارڈ نہیں ملا۔", "No record found."))

    elif report_type == "Fees Report":
        c_dt1, c_dt2 = st.columns(2)
        start_date = c_dt1.date_input(tr("شروع کی تاریخ (Start Date)", "Start Date"), datetime.date.today().replace(day=1))
        end_date = c_dt2.date_input(tr("ختم ہونے کی تاریخ (End Date)", "End Date"), datetime.date.today())
        
        c1, c2, c3 = st.columns(3)
        f_reg = c1.text_input(tr("رجسٹریشن نمبر", "Reg No"))
        f_class = c2.selectbox(tr("کلاس", "Class"), [tr("سب", "All")] + classes_list)
        f_status = c3.selectbox(tr("فیس سٹیٹس", "Fee Status"), [tr("سب", "All"), "Paid", "Unpaid"])
        
        if st.button(tr("فیس وصولی کی آفیشل رپورٹ تیار کریں", "Generate Official Fee Report"), type="primary"):
            q_cond = [f"f.date BETWEEN '{start_date.strftime('%Y-%m-%d')}' AND '{end_date.strftime('%Y-%m-%d')}'"]
            if f_reg: q_cond.append(f"f.reg_id LIKE '%{f_reg}%'")
            if f_class != tr("سب", "All"): q_cond.append(f"s.class='{f_class}'")
            if f_status != tr("سب", "All"): q_cond.append(f"f.status='{f_status}'")
            
            where_clause = " WHERE " + " AND ".join(q_cond)
            query = f"""
                SELECT f.date as 'Date', f.invoice_no as 'Invoice', f.reg_id as 'Reg No', s.name as 'Name', s.name_en as 'Name_EN', s.class as 'Class', 
                f.month as 'Month', f.tuition as 'Tuition', f.arrears_col as 'Arrears Collected', f.total as 'Total', f.status as 'Status'
                FROM fees f JOIN students s ON f.reg_id = s.reg_id {where_clause} ORDER BY f.date ASC
            """
            df = pd.read_sql(query, conn)
            
            if not df.empty:
                t = get_translations(st.session_state.ui_lang)
                df['Final Name'] = df.apply(lambda row: get_disp_val(row['Name'], row.get('Name_EN')), axis=1)
                total_collected = df[df['Status'].isin(['Paid', 'Paid (Auto)']) | df['Status'].isna()]['Total'].sum()
                
                if st.session_state.ui_lang == "اردو":
                    df = df[['Date', 'Invoice', 'Reg No', 'Final Name', 'Class', 'Month', 'Total', 'Status']]
                    df = df.rename(columns={'Date':'تاریخ', 'Invoice':'چالان نمبر', 'Reg No':'رول نمبر', 'Final Name':'نام', 'Class':'کلاس', 'Month':'مہینہ', 'Total':'کل رقم', 'Status':'سٹیٹس'})
                else:
                    df = df[['Date', 'Invoice', 'Reg No', 'Final Name', 'Class', 'Month', 'Total', 'Status']]
                    df = df.rename(columns={'Final Name':'Name'})
                
                html_table = df.to_html(classes="data-table", index=False, border=1, justify='center', na_rep='-')
                html_table = html_table.replace('class="dataframe data-table"', f'class="data-table" dir="{t["dir"]}" style="width:100%; box-sizing: border-box; border-collapse: collapse;"')
                
                heading_text = f"Official Fee Collection Report ({start_date.strftime('%d-%b-%Y')} to {end_date.strftime('%d-%b-%Y')})" if st.session_state.ui_lang == "English" else f"فیس وصولی کی آفیشل رپورٹ ({start_date.strftime('%d-%m-%Y')} سے {end_date.strftime('%d-%m-%Y')})"
                summary_html = f"""
                <div style="border: 2px solid green; padding: 10px; margin-top: 15px; background: #e6ffe6; text-align: center; box-sizing: border-box;">
                    <h3 style="margin: 0; color: green;">{tr('اس عرصے کی کل وصول شدہ فیس: ', 'Grand Total Collected Fees: ')} Rs {total_collected:,}</h3>
                </div>
                """
                
                print_html = get_official_header_footer(heading_text, html_table, summary_html)
                st.success(tr("رپورٹ تیار ہے! نیچے دیے گئے بٹن سے فوری پرنٹ کریں۔", "Report Ready! Use the button below to print."))
                print_button_js(print_html, tr("🖨️ فوری پرنٹ کریں (Print Report)", "🖨️ Print Report"), landscape=False)
                
                csv = df.to_csv(index=False).encode('utf-8')
                st.download_button(label=tr("📥 ایکسل (CSV) ڈاؤن لوڈ کریں", "📥 Download Excel (CSV)"), data=csv, file_name=f"Official_Fee_Report_{today_date}.csv", mime="text/csv")
                
                st.write("---")
                st.dataframe(df, use_container_width=True)
            else: st.info(tr("اس عرصے کا کوئی فیس ریکارڈ نہیں ملا۔", "No fee record found for this period."))

    elif report_type == "Salaries Report":
        c1, c2, c3 = st.columns(3)
        s_sid = c1.text_input(tr("سٹاف آئی ڈی / نام", "Staff ID / Name"))
        months_disp_sel = [tr("سب", "All")] + [tr(m_ur, m_en) for m_ur, m_en in zip(months_ur, months_en)]
        s_month_disp = c2.selectbox(tr("مہینہ", "Month"), months_disp_sel)
        s_year = c3.selectbox(tr("سال", "Year"), [tr("سب", "All"), "2024", "2025", "2026", "2027", "2028"])
        
        if st.button(tr("تنخواہوں کی رپورٹ تیار کریں", "Generate Salaries Report"), type="primary"):
            q_cond = []
            if s_sid: q_cond.append(f"(sr.staff_id LIKE '%{s_sid}%' OR st.name LIKE '%{s_sid}%' OR st.name_en LIKE '%{s_sid}%')")
            
            if s_month_disp != tr("سب", "All"):
                s_m_ur = months_ur[months_disp_sel.index(s_month_disp) - 1]
                s_m_en = months_en[months_disp_sel.index(s_month_disp) - 1]
                q_cond.append(f"(sr.month='{s_m_ur}' OR sr.month='{s_m_en}')")
                
            if s_year != tr("سب", "All") and s_year != "All": 
                q_cond.append(f"sr.date LIKE '{s_year}-%'")
            
            where_clause = " WHERE " + " AND ".join(q_cond) if q_cond else ""
            query = f"""
                SELECT sr.date as 'Date', sr.staff_id as 'Staff ID', st.name as 'Name', st.name_en as 'Name_EN',
                sr.month as 'Month', sr.amount as 'Amount', sr.remarks as 'Remarks' 
                FROM salary_records sr JOIN staff st ON sr.staff_id = st.staff_id {where_clause} ORDER BY sr.date ASC
            """
            df = pd.read_sql(query, conn)
            
            if not df.empty:
                t = get_translations(st.session_state.ui_lang)
                df['Final Name'] = df.apply(lambda row: get_disp_val(row['Name'], row.get('Name_EN')), axis=1)
                total_paid = df['Amount'].sum()
                
                if st.session_state.ui_lang == "اردو":
                    df['Remarks'] = df['Remarks'].replace({'Salary': 'تنخواہ'})
                    df = df[['Date', 'Staff ID', 'Final Name', 'Month', 'Amount', 'Remarks']]
                    df = df.rename(columns={'Date':'تاریخ', 'Staff ID':'آئی ڈی', 'Final Name':'نام', 'Month':'مہینہ', 'Amount':'رقم', 'Remarks':'تفصیل'})
                else:
                    df = df[['Date', 'Staff ID', 'Final Name', 'Month', 'Amount', 'Remarks']]
                    df = df.rename(columns={'Final Name':'Name'})
                
                html_table = df.to_html(classes="data-table", index=False, border=1, justify='center', na_rep='-')
                html_table = html_table.replace('class="dataframe data-table"', f'class="data-table" dir="{t["dir"]}" style="width:100%; box-sizing: border-box; border-collapse: collapse;"')
                
                heading_text = f"Official Staff Salaries Report ({s_month_disp}-{s_year})" if st.session_state.ui_lang == "English" else f"سٹاف کی تنخواہوں کی رپورٹ ({s_month_disp}-{s_year})"
                summary_html = f"""
                <div style="border: 2px solid green; padding: 10px; margin-top: 15px; background: #e6ffe6; text-align: center; box-sizing: border-box;">
                    <h3 style="margin: 0; color: green;">{tr('اس عرصے کی کل ادا شدہ تنخواہیں: ', 'Grand Total Paid Salaries: ')} Rs {total_paid:,}</h3>
                </div>
                """
                
                print_html = get_official_header_footer(heading_text, html_table, summary_html)
                st.success(tr("رپورٹ تیار ہے! نیچے دیے گئے بٹن سے فوری پرنٹ کریں۔", "Report Ready! Use the button below to print."))
                print_button_js(print_html, tr("🖨️ فوری پرنٹ کریں (Print Report)", "🖨️ Print Report"), landscape=False)
                
                csv = df.to_csv(index=False).encode('utf-8')
                st.download_button(label=tr("📥 ایکسل (CSV) ڈاؤن لوڈ کریں", "📥 Download Excel (CSV)"), data=csv, file_name=f"Official_Salaries_Report_{today_date}.csv", mime="text/csv")
                
                st.write("---")
                st.dataframe(df, use_container_width=True)
            else: st.info(tr("کوئی ریکارڈ نہیں ملا۔", "No record found."))

    elif report_type == "Attendance Report":
        c1, c2, c3 = st.columns(3)
        start_date = c1.date_input(tr("شروع کی تاریخ", "Start Date"), datetime.date.today().replace(day=1))
        end_date = c2.date_input(tr("ختم ہونے کی تاریخ", "End Date"), datetime.date.today())
        a_type_disp = c3.radio(tr("قسم", "Type"), [tr("طالب علم", "Student"), tr("سٹاف", "Staff")])
        a_type = "طالب علم" if a_type_disp in ["طالب علم", "Student"] else "سٹاف"
        
        a_class = tr("سب", "All")
        a_sec = tr("سب", "All")
        
        if a_type == "طالب علم":
            ca1, ca2 = st.columns(2)
            a_class = ca1.selectbox(tr("کلاس", "Class"), [tr("سب", "All")] + classes_list)
            a_sec = ca2.selectbox(tr("سیکشن", "Section"), [tr("سب", "All"), "A", "B", "C", "D"])
        
        if st.button(tr("حاضری کی رپورٹ تیار کریں", "Generate Attendance Report"), type="primary"):
            date_start_str = start_date.strftime("%Y-%m-%d")
            date_end_str = end_date.strftime("%Y-%m-%d")
            
            if a_type == "طالب علم":
                q_cond = [f"a.date BETWEEN '{date_start_str}' AND '{date_end_str}'", "a.type='طالب علم'"]
                if a_class != tr("سب", "All"): q_cond.append(f"s.class='{a_class}'")
                if a_sec != tr("سب", "All"): q_cond.append(f"s.section='{a_sec}'")
                where_clause = " WHERE " + " AND ".join(q_cond)
                query = f"SELECT a.date as 'Date', s.reg_id as 'ID', s.name as 'Name', s.name_en as 'Name_EN', s.class as 'Class', a.status as 'Status' FROM attendance a JOIN students s ON a.person_id = s.reg_id {where_clause} ORDER BY a.date ASC, CAST(s.reg_id AS INTEGER) ASC"
            else:
                query = f"SELECT a.date as 'Date', st.staff_id as 'ID', st.name as 'Name', st.name_en as 'Name_EN', st.designation as 'Desig', a.status as 'Status' FROM attendance a JOIN staff st ON a.person_id = st.staff_id WHERE a.date BETWEEN '{date_start_str}' AND '{date_end_str}' AND a.type='سٹاف' ORDER BY a.date ASC, CAST(st.staff_id AS INTEGER) ASC"
                
            df = pd.read_sql(query, conn)
            
            if not df.empty:
                t = get_translations(st.session_state.ui_lang)
                df['Final Name'] = df.apply(lambda row: get_disp_val(row['Name'], row.get('Name_EN')), axis=1)
                
                tot_p = len(df[df['Status'] == 'Present'])
                tot_a = len(df[df['Status'] == 'Absent'])
                tot_l = len(df[df['Status'] == 'Leave'])
                
                if start_date != end_date:
                    group_cols = ['ID', 'Final Name', 'Desig'] if a_type == "سٹاف" else ['ID', 'Final Name', 'Class']
                    df['Count'] = 1
                    df_agg = pd.pivot_table(df, values='Count', index=group_cols, columns='Status', aggfunc='sum', fill_value=0).reset_index()
                    df_agg.columns.name = None
                    
                    for s in ['Present', 'Absent', 'Leave']:
                        if s not in df_agg.columns: df_agg[s] = 0
                            
                    df_agg['Total Days'] = df_agg['Present'] + df_agg['Absent'] + df_agg['Leave']
                    df = df_agg[group_cols + ['Present', 'Absent', 'Leave', 'Total Days']]
                    
                    if st.session_state.ui_lang == "اردو":
                        if a_type == "سٹاف":
                            df['Desig'] = df['Desig'].replace({"Teacher": "استاد / ٹیچر", "Principal": "پرنسپل", "Clerk": "کلرک", "Maid/Peon": "آیا / چپڑاسی", "Security Guard": "سیکیورٹی گارڈ"})
                            df = df.rename(columns={'ID':'آئی ڈی', 'Final Name':'نام', 'Desig':'عہدہ', 'Present':'کل حاضر', 'Absent':'کل غیر حاضر', 'Leave':'کل چھٹی', 'Total Days':'کل دن'})
                        else:
                            df = df.rename(columns={'ID':'رول نمبر', 'Final Name':'نام', 'Class':'کلاس', 'Present':'کل حاضر', 'Absent':'کل غیر حاضر', 'Leave':'کل چھٹی', 'Total Days':'کل دن'})
                    else:
                        if a_type == "سٹاف":
                            df = df.rename(columns={'ID':'Staff ID', 'Final Name':'Name', 'Desig':'Designation', 'Present':'Total Present', 'Absent':'Total Absent', 'Leave':'Total Leaves', 'Total Days':'Total Days'})
                        else:
                            df = df.rename(columns={'ID':'Reg No', 'Final Name':'Name', 'Present':'Total Present', 'Absent':'Total Absent', 'Leave':'Total Leaves', 'Total Days':'Total Days'})
                    
                    disp_c_att = a_class if a_class != tr("سب", "All") else tr("تمام", "All")
                    heading_title = f"Attendance Summary ({date_start_str} to {date_end_str}) - Class: {disp_c_att}" if st.session_state.ui_lang == "English" and a_type == "طالب علم" else f"حاضری کا خلاصہ ({date_start_str} تا {date_end_str}) - کلاس: {disp_c_att}" if st.session_state.ui_lang == "اردو" and a_type == "طالب علم" else f"Staff Attendance Summary ({date_start_str} to {date_end_str})" if st.session_state.ui_lang == "English" else f"سٹاف کی حاضری کا خلاصہ ({date_start_str} تا {date_end_str})"
                    
                else:
                    if st.session_state.ui_lang == "اردو":
                        df['Status'] = df['Status'].replace({'Present':'حاضر', 'Absent':'غیر حاضر', 'Leave':'چھٹی'})
                        if a_type == "سٹاف":
                            df['Desig'] = df['Desig'].replace({"Teacher": "استاد / ٹیچر", "Principal": "پرنسپل", "Clerk": "کلرک", "Maid/Peon": "آیا / چپڑاسی", "Security Guard": "سیکیورٹی گارڈ"})
                            df = df[['Date', 'ID', 'Final Name', 'Desig', 'Status']]
                            df = df.rename(columns={'Date':'تاریخ', 'ID':'آئی ڈی', 'Final Name':'نام', 'Desig':'عہدہ', 'Status':'حاضری'})
                        else:
                            df = df[['Date', 'ID', 'Final Name', 'Class', 'Status']]
                            df = df.rename(columns={'Date':'تاریخ', 'ID':'رول نمبر', 'Final Name':'نام', 'Class':'کلاس', 'Status':'حاضری'})
                    else:
                        if a_type == "سٹاف":
                            df = df[['Date', 'ID', 'Final Name', 'Desig', 'Status']]
                            df = df.rename(columns={'ID':'Staff ID', 'Final Name':'Name', 'Desig':'Designation'})
                        else:
                            df = df[['Date', 'ID', 'Final Name', 'Class', 'Status']]
                            df = df.rename(columns={'ID':'Reg No', 'Final Name':'Name'})
                    
                    disp_c_att = a_class if a_class != tr("سب", "All") else tr("تمام", "All")
                    heading_title = f"Attendance Report - {date_start_str} (Class: {disp_c_att})" if st.session_state.ui_lang == "English" and a_type == "طالب علم" else f"حاضری کی رپورٹ - {date_start_str} (کلاس: {disp_c_att})" if st.session_state.ui_lang == "اردو" and a_type == "طالب علم" else f"Staff Attendance Report - {date_start_str}" if st.session_state.ui_lang == "English" else f"سٹاف کی حاضری کی رپورٹ - {date_start_str}"
                
                html_table = df.to_html(classes="data-table", index=False, border=1, justify='center', na_rep='-')
                html_table = html_table.replace('class="dataframe data-table"', f'class="data-table" dir="{t["dir"]}" style="width:100%; box-sizing: border-box; border-collapse: collapse;"')
                
                summary_html = f"""
                <table style="width:100%; margin-top:15px; font-weight:bold; border-collapse:collapse; font-size:14px; box-sizing: border-box;" dir="{t['dir']}">
                    <tr>
                        <td style="border:2px solid green; padding:8px; text-align:center; color:green; background:#e6ffe6;">{tr('اس عرصے میں کل حاضریاں: ', 'Total Presents in this period: ')} {tot_p}</td>
                        <td style="border:2px solid red; padding:8px; text-align:center; color:red; background:#ffe6e6;">{tr('کل غیر حاضریاں: ', 'Total Absents: ')} {tot_a}</td>
                        <td style="border:2px solid #ff9900; padding:8px; text-align:center; color:#cc7a00; background:#fff5e6;">{tr('کل چھٹیاں: ', 'Total Leaves: ')} {tot_l}</td>
                    </tr>
                </table>
                """
                
                print_html = get_official_header_footer(heading_title, html_table, summary_html)
                st.success(tr("رپورٹ تیار ہے! نیچے دیے گئے بٹن سے فوری پرنٹ کریں۔", "Report Ready! Use the button below to print."))
                print_button_js(print_html, tr("🖨️ فوری پرنٹ کریں (Print Report)", "🖨️ Print Report"), landscape=False)
                
                csv = df.to_csv(index=False).encode('utf-8')
                st.download_button(label=tr("📥 ایکسل (CSV) ڈاؤن لوڈ کریں", "📥 Download Excel (CSV)"), data=csv, file_name=f"Official_Attendance_Report_{today_date}.csv", mime="text/csv")
                
                st.write("---")
                st.dataframe(df, use_container_width=True)
            else: st.info(tr("اس تاریخ پر کوئی حاضری نہیں ملی۔", "No attendance found for this date."))

    elif report_type == "Accounts Ledger":
        c_dt1, c_dt2, c_dt3 = st.columns(3)
        start_date = c_dt1.date_input(tr("شروع کی تاریخ", "Start Date"), datetime.date.today().replace(day=1), key="acc_start")
        end_date = c_dt2.date_input(tr("ختم ہونے کی تاریخ", "End Date"), datetime.date.today(), key="acc_end")
        
        available_heads = pd.read_sql("SELECT head_name FROM account_heads", conn)['head_name'].tolist()
        acc_head_disp = c_dt3.selectbox(tr("اکاؤنٹ ہیڈ (مخصوص کھاتہ)", "Account Head"), [tr("تمام کھاتے (All)", "All")] + available_heads)
        
        if st.button(tr("آفیشل اکاؤنٹس لیجر (روزنامچہ) تیار کریں", "Generate Official Ledger"), type="primary"):
            q_cond = [f"date BETWEEN '{start_date.strftime('%Y-%m-%d')}' AND '{end_date.strftime('%Y-%m-%d')}'"]
            if acc_head_disp != tr("تمام کھاتے (All)", "All"):
                q_cond.append(f"head_name='{acc_head_disp}'")
                
            where_clause = " WHERE " + " AND ".join(q_cond)
            
            df = pd.read_sql(f"SELECT date as 'Date', voucher_no as 'Voucher No', type as 'Type', head_name as 'Head', description as 'Details', amount as 'Amount' FROM accounts {where_clause} ORDER BY date ASC, rowid ASC", conn)
            
            if not df.empty:
                t = get_translations(st.session_state.ui_lang)
                income_col, expense_col, bal_col = [], [], []
                r_bal, tot_income, tot_expense = 0, 0, 0
                
                for _, row in df.iterrows():
                    amt = float(row['Amount'])
                    if row['Type'] in ['آمدنی', 'Income']:
                        income_col.append(amt)
                        expense_col.append(0)
                        tot_income += amt
                        r_bal += amt
                    else:
                        income_col.append(0)
                        expense_col.append(amt)
                        tot_expense += amt
                        r_bal -= amt
                    bal_col.append(r_bal)
                
                df['Income'] = income_col
                df['Expense'] = expense_col
                df['Balance'] = bal_col
                df = df[['Date', 'Voucher No', 'Head', 'Details', 'Income', 'Expense', 'Balance']]
                
                if st.session_state.ui_lang == "اردو":
                    df.columns = ['تاریخ', 'واؤچر نمبر', 'اکاؤنٹ ہیڈ', 'تفصیلات', 'آمدنی (+)', 'خرچ (-)', 'بیلنس']
                
                html_table = df.to_html(classes="data-table", index=False, border=1, justify='center', na_rep='-')
                html_table = html_table.replace('class="dataframe data-table"', f'class="data-table" dir="{t["dir"]}" style="width:100%; box-sizing: border-box; border-collapse: collapse;"')
                
                head_txt_disp = acc_head_disp if acc_head_disp != tr("تمام کھاتے (All)", "All") else tr("تمام کھاتے", "All Accounts")
                heading_text = f"Official Account Ledger ({head_txt_disp}) - {start_date.strftime('%d-%m-%Y')} to {end_date.strftime('%d-%m-%Y')}" if st.session_state.ui_lang == "English" else f"آفیشل اکاؤنٹس روزنامچہ ({head_txt_disp}) - {start_date.strftime('%d-%m-%Y')} سے {end_date.strftime('%d-%m-%Y')}"
                
                summary_html = f"""
                <table style="width:100%; margin-top:15px; font-weight:bold; border-collapse:collapse; font-size:14px; box-sizing: border-box;" dir="{t['dir']}">
                    <tr>
                        <td style="border:2px solid green; padding:10px; text-align:center; color:green; background:#e6ffe6;">{tr('کل آمدنی: ', 'Total Income: ')} Rs {tot_income:,}</td>
                        <td style="border:2px solid red; padding:10px; text-align:center; color:red; background:#ffe6e6;">{tr('کل اخراجات: ', 'Total Expense: ')} Rs {tot_expense:,}</td>
                        <td style="border:2px solid #1a4f8b; padding:10px; text-align:center; background:#e6f2ff; color:#1a4f8b;">{tr('اختتامی بیلنس: ', 'Closing Balance: ')} Rs {r_bal:,}</td>
                    </tr>
                </table>
                """
                
                print_html = get_official_header_footer(heading_text, html_table, summary_html)
                st.success(tr("آفیشل آڈٹ رپورٹ تیار ہے! نیچے دیے گئے بٹن سے فوری پرنٹ کریں۔", "Official Audit Report Ready! Use the button below to print."))
                print_button_js(print_html, tr("🖨️ فوری پرنٹ کریں (Print Report)", "🖨️ Print Report"), landscape=True)
                
                csv = df.to_csv(index=False).encode('utf-8')
                st.download_button(label=tr("📥 ایکسل (CSV) ڈاؤن لوڈ کریں", "📥 Download Ledger (CSV)"), data=csv, file_name=f"Official_Accounts_Ledger_{today_date}.csv", mime="text/csv")
                
                st.write("---")
                st.dataframe(df, use_container_width=True)
            else: st.info(tr("اس عرصے میں کوئی ٹرانزیکشن نہیں ہوئی۔", "No transaction found in this period."))
            
    st.markdown("</div>", unsafe_allow_html=True)

# ================= 14. ڈیٹا بیک اپ اور ریسٹور =================
elif core_choice in ["ڈیٹا بیک اپ", "Data Backup"]:
    st.markdown(f"<h2 class='no-print'>💾 {tr('ڈیٹا بیک اپ اور ریسٹور', 'Data Backup & Restore')}</h2>", unsafe_allow_html=True)
    st.markdown(f"<p class='no-print'>{tr('یہاں سے آپ سکول کے ڈیٹا کا بیک اپ لے سکتے ہیں اور کسی بھی سائز کی بیک اپ فائل یہاں سے ریسٹور کر سکتے ہیں۔', 'Here you can backup and restore school data with unlimited file size support.')}</p>", unsafe_allow_html=True)
    
    st.write("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader(tr("📥 بیک اپ ڈاؤن لوڈ کریں", "📥 Download Backup"))
        st.write(tr("اپنے موجودہ ڈیٹا کی ایک کاپی محفوظ کرنے کے لیے نیچے دیے گئے بٹن پر کلک کریں۔", "Click the button below to save a copy of your current data."))
        
        try:
            with open(DB_FILE, "rb") as file:
                btn = st.download_button(
                    label=tr("ڈیٹا بیس ڈاؤن لوڈ کریں", "Download Database"),
                    data=file,
                    file_name=f"school_backup_{active_session}_{datetime.date.today().strftime('%d-%m-%Y')}.db",
                    mime="application/octet-stream"
                )
        except FileNotFoundError:
            st.error(tr("ڈیٹا بیس کی فائل نہیں ملی۔", "Database file not found."))
            
    with col2:
        st.subheader(tr("📤 ڈیٹا ریسٹور کریں (ان لمیٹڈ سائز)", "📤 Restore Backup (Unlimited Size)"))
        st.write(tr("اپنی بیک اپ (.db) فائل یہاں اپلوڈ کریں۔ اب سائز کی کوئی حد نہیں ہے۔", "Upload your backup (.db) file here. There is no size limit now."))
        
        uploaded_backup = st.file_uploader(tr("بیک اپ فائل (.db) منتخب کریں", "Select Backup File (.db)"), type=['db'], max_upload_size=2000)
        
        if uploaded_backup is not None:
            if st.button(tr("سسٹم میں ڈیٹا واپس لائیں (Restore Now)", "Restore Data Now"), type="primary"):
                try:
                    conn.close()
                    with open(DB_FILE, "wb") as f:
                        f.write(uploaded_backup.getbuffer())
                        
                    st.success(tr("ڈیٹا کامیابی سے ریسٹور ہو گیا! براہ کرم سافٹ ویئر کو ری سٹارٹ کریں یا پیج ریفریش (F5) کریں۔", "Data restored successfully! Please restart the software or refresh the page (F5)."))
                    
                    conn = sqlite3.connect(DB_FILE, check_same_thread=False)
                    cursor = conn.cursor()
                    
                except Exception as e:
                    st.error(f"{tr('فائل ریسٹور کرنے میں مسئلہ آیا:', 'Error restoring file:')} {e}")

# ================= 15. پیرنٹ پورٹل (Parent Portal) =================
elif core_choice in ["پیرنٹ پورٹل", "Parent Portal"]:
    st.markdown(f"<h2 class='no-print'>👨‍👩‍👦 {tr('والدین کا پورٹل (Parent Dashboard)', 'Parent Portal')}</h2>", unsafe_allow_html=True)
    
    curr_u = st.session_state.current_user
    stu_df = pd.read_sql(f"SELECT * FROM students WHERE phone='{curr_u}' OR reg_id=REPLACE('{curr_u}', 'parent_', '')", conn)
    
    if not stu_df.empty:
        stu = stu_df.iloc[0]
        s_reg = stu['reg_id']
        s_class = stu['class']
        s_sec = stu['section']
        s_name = get_disp_val(stu['name'], stu.get('name_en'))
        
        welcome_msg = tr(f"خوش آمدید! آپ <b>{s_name}</b> (کلاس: {s_class}) کا ڈیش بورڈ دیکھ رہے ہیں۔", f"Welcome! You are viewing the dashboard of <b>{s_name}</b> (Class: {s_class}).")
        
        st.markdown(f"""
        <div style="background-color:#e8f5e9; padding:15px; border-left:5px solid #4caf50; border-radius:5px; margin-bottom: 20px;">
            <h3 style="margin:0; color:#2e7d32;">{welcome_msg}</h3>
        </div>
        """, unsafe_allow_html=True)
        
        tab_diary = "📚 " + tr("آج کی ڈائری", "Today's Diary")
        tab_att = "📊 " + tr("حاضری ریکارڈ", "Attendance Record")
        tab_fee = "💵 " + tr("فیس کی تفصیل", "Fee Details")
        tab_leave = "📝 " + tr("چھٹی کی درخواست", "Leave Application")
        tab_van = "🚌 " + tr("لائیو سکول وین", "Live School Van")
        tab_comp = "🎧 " + tr("شکایت / تجویز", "Complaint & Helpdesk")
        
        p_tab1, p_tab2, p_tab3, p_tab4, p_tab5, p_tab6 = st.tabs([tab_diary, tab_att, tab_fee, tab_leave, tab_van, tab_comp])
        
        with p_tab1:
            st.markdown(f"#### 📖 {tr('طالب علم کی ڈائری اور ہوم ورک', 'Student Diary & Homework')}")
            
            q_cols_diary = "date as 'تاریخ', subject as 'مضمون', topic as 'ہوم ورک تفصیل', status as 'سٹیٹس'" if st.session_state.ui_lang == "اردو" else "date as 'Date', subject as 'Subject', topic as 'Homework Details', status as 'Status'"
            lp = pd.read_sql(f"SELECT {q_cols_diary} FROM lesson_plan WHERE class='{s_class}' AND section='{s_sec}' ORDER BY id DESC LIMIT 10", conn)
            
            if not lp.empty:
                def get_smart_icon(subject_name):
                    sub_lower = str(subject_name).lower()
                    if "science" in sub_lower or "سائنس" in sub_lower or "biology" in sub_lower or "physics" in sub_lower or "chemistry" in sub_lower: return "⚗️"
                    elif "math" in sub_lower or "ریاضی" in sub_lower or "algebra" in sub_lower: return "📐"
                    elif "urdu" in sub_lower or "اردو" in sub_lower: return "📘"
                    elif "english" in sub_lower or "انگلش" in sub_lower or "eng" in sub_lower: return "📖"
                    elif "islam" in sub_lower or "islamiat" in sub_lower or "اسلامیات" in sub_lower or "quran" in sub_lower or "arabic" in sub_lower: return "🕌"
                    elif "computer" in sub_lower or "it" in sub_lower or "ict" in sub_lower: return "💻"
                    elif "social" in sub_lower or "history" in sub_lower or "geography" in sub_lower or "معاشرتی" in sub_lower or "pak studies" in sub_lower: return "🌍"
                    elif "drawing" in sub_lower or "art" in sub_lower or "پینٹنگ" in sub_lower or "آرٹ" in sub_lower: return "🎨"
                    elif "pe" in sub_lower or "sports" in sub_lower or "ورزش" in sub_lower or "کھیل" in sub_lower: return "⚽"
                    else: return "📝"

                date_col = 'تاریخ' if st.session_state.ui_lang == "اردو" else 'Date'
                sub_col = 'مضمون' if st.session_state.ui_lang == "اردو" else 'Subject'
                top_col = 'ہوم ورک تفصیل' if st.session_state.ui_lang == "اردو" else 'Homework Details'
                stat_col = 'سٹیٹس' if st.session_state.ui_lang == "اردو" else 'Status'
                
                for _, row in lp.iterrows():
                    icon = get_smart_icon(row[sub_col])
                    raw_stat = str(row[stat_col])
                    if "Complete" in raw_stat or "مکمل" in raw_stat:
                        stat_disp = "مکمل ہو گیا ✅" if st.session_state.ui_lang == "اردو" else "Completed ✅"
                        stat_color, stat_bg = "#2e7d32", "#e8f5e9"
                    else:
                        stat_disp = "جاری ہے ⏳" if st.session_state.ui_lang == "اردو" else "In Progress ⏳"
                        stat_color, stat_bg = "#e65100", "#fff3e0"
                    
                    dir_tag = 'rtl' if st.session_state.ui_lang == "اردو" else 'ltr'
                    align_tag = 'right' if st.session_state.ui_lang == "اردو" else 'left'
                    
                    st.markdown(f"""
                    <div style='background-color: white; border-left: 5px solid #1a4f8b; padding: 15px; margin-bottom: 12px; border-radius: 8px; box-shadow: 0 2px 5px rgba(0,0,0,0.05); border-right: 1px solid #eee; border-top: 1px solid #eee; border-bottom: 1px solid #eee;' dir="{dir_tag}">
                        <div style='display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;'>
                            <strong style='font-size: 17px; color: #1a4f8b;'>{icon} {row[sub_col]}</strong>
                            <span style='font-size: 12px; color: #666; background-color: #f1f3f4; padding: 4px 8px; border-radius: 12px;'>📅 {row[date_col]}</span>
                        </div>
                        <div style='font-size: 15px; color: #333; margin-bottom: 12px; line-height: 1.6; text-align: {align_tag};'>
                            {row[top_col]}
                        </div>
                        <div style='font-size: 12px; font-weight: bold; color: {stat_color}; background-color: {stat_bg}; display: inline-block; padding: 5px 12px; border-radius: 4px;'>
                            {stat_disp}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info(tr("آج کی ڈائری ابھی اپلوڈ نہیں ہوئی۔", "Today's diary has not been uploaded yet."))
                
        with p_tab2:
            st.markdown(f"#### 📅 {tr('پچھلے 30 دن کی حاضری کا ریکارڈ', 'Attendance Record (Last 30 Days)')}")
            q_cols_att = "date as 'تاریخ', status as 'حاضری'" if st.session_state.ui_lang == "اردو" else "date as 'Date', status as 'Attendance'"
            att = pd.read_sql(f"SELECT {q_cols_att} FROM attendance WHERE person_id='{s_reg}' AND type='طالب علم' ORDER BY date DESC LIMIT 30", conn)
            if not att.empty:
                att_col_name = 'حاضری' if st.session_state.ui_lang == "اردو" else 'Attendance'
                if st.session_state.ui_lang == "اردو":
                    att[att_col_name] = att[att_col_name].replace({'Present': 'حاضر ✅', 'Absent': 'غیر حاضر ❌', 'Leave': 'چھٹی 🟡'})
                else:
                    att[att_col_name] = att[att_col_name].replace({'Present': 'Present ✅', 'Absent': 'Absent ❌', 'Leave': 'Leave 🟡'})
                st.dataframe(att, use_container_width=True, hide_index=True)
            else:
                st.info(tr("حاضری کا کوئی ریکارڈ موجود نہیں۔", "No attendance record found."))
                
        with p_tab3:
            st.markdown(f"#### 🧾 {tr('فیس کے چالان اور ادائیگی کی تفصیل', 'Fee Challans & Payment Details')}")
            q_cols_fee = "month as 'مہینہ', total as 'رقم', status as 'سٹیٹس', date as 'تاریخ'" if st.session_state.ui_lang == "اردو" else "month as 'Month', total as 'Amount', status as 'Status', date as 'Date'"
            fees = pd.read_sql(f"SELECT {q_cols_fee} FROM fees WHERE reg_id='{s_reg}' ORDER BY rowid DESC", conn)
            if not fees.empty:
                st.dataframe(fees, use_container_width=True, hide_index=True)
            else:
                st.info(tr("فیس کا کوئی ریکارڈ موجود نہیں۔", "No fee record found."))
                
        with p_tab4:
            st.markdown(f"#### ✉️ {tr('سکول انتظامیہ کو چھٹی کی درخواست بھیجیں', 'Send Leave Application to School Admin')}")
            try:
                cursor.execute("CREATE TABLE IF NOT EXISTS leave_requests (id INTEGER PRIMARY KEY AUTOINCREMENT, reg_id TEXT, date TEXT, reason TEXT, status TEXT DEFAULT 'Pending')")
                try: cursor.execute("ALTER TABLE leave_requests ADD COLUMN admin_remarks TEXT")
                except: pass
                conn.commit()
            except: pass
            
            with st.form("leave_req_form", clear_on_submit=True):
                l_date = st.date_input(tr("کس تاریخ کی چھٹی چاہیے؟", "Date for leave?"), datetime.date.today())
                l_reason = st.text_area(tr("چھٹی کی وجہ بیان کریں (بیماری، ضروری کام وغیرہ) *", "Reason for leave (Illness, urgent work etc) *"))
                if st.form_submit_button(tr("درخواست بھیجیں (Submit Application)", "Submit Application"), type="primary"):
                    if l_reason.strip():
                        def_remark = "انتظار فرمائیں..." if st.session_state.ui_lang == "اردو" else "Please wait..."
                        cursor.execute("INSERT INTO leave_requests (reg_id, date, reason, admin_remarks) VALUES (?, ?, ?, ?)", (s_reg, l_date.strftime("%Y-%m-%d"), l_reason, def_remark))
                        conn.commit()
                        st.success(tr("✅ آپ کی چھٹی کی درخواست پرنسپل آفس کو کامیابی سے بھیج دی گئی ہے!", "✅ Your leave request has been successfully sent to the Principal's office!"))
                    else:
                        st.error(tr("براہ کرم چھٹی کی وجہ لازمی لکھیں۔", "Please provide a reason for the leave."))
                        
            st.write("---")
            st.markdown(f"**{tr('آپ کی پچھلی درخواستوں کا ریکارڈ:', 'Your Past Leave Requests Record:')}**")
            q_cols_req = "date as 'تاریخ', reason as 'وجہ', status as 'سٹیٹس', admin_remarks as 'سکول کا جواب'" if st.session_state.ui_lang == "اردو" else "date as 'Date', reason as 'Reason', status as 'Status', admin_remarks as 'School Reply'"
            past_req = pd.read_sql(f"SELECT {q_cols_req} FROM leave_requests WHERE reg_id='{s_reg}' ORDER BY id DESC", conn)
            if not past_req.empty:
                def style_status(val):
                    if st.session_state.ui_lang == "اردو":
                        if val == 'Approved': return 'منظور ہو گئی ✅'
                        elif val == 'Rejected': return 'مسترد ہو گئی ❌'
                        return 'انتظار فرمائیں ⏳'
                    else:
                        if val == 'Approved': return 'Approved ✅'
                        elif val == 'Rejected': return 'Rejected ❌'
                        return 'Pending ⏳'
                        
                stat_col = 'سٹیٹس' if st.session_state.ui_lang == "اردو" else 'Status'
                past_req[stat_col] = past_req[stat_col].apply(style_status)
                st.dataframe(past_req, use_container_width=True, hide_index=True)
            else:
                st.info(tr("کوئی پرانی درخواست موجود نہیں۔", "No past requests found."))
                
        with p_tab5:
            st.markdown(f"#### 🛰️ {tr('بچے کی سکول وین (لائیو ٹریکنگ)', 'Student School Van (Live Tracking)')}")
            try:
                veh_check = pd.read_sql(f"SELECT vehicle_id FROM transport_members WHERE reg_id='{s_reg}'", conn)
                if not veh_check.empty:
                    v_id = veh_check.iloc[0]['vehicle_id']
                    v_details = pd.read_sql(f"SELECT driver_name, driver_phone, gps_device_id FROM transport WHERE vehicle_id='{v_id}'", conn).iloc[0]
                    veh_info = tr(f"🚐 **گاڑی:** {v_id} | 👤 **ڈرائیور:** {v_details['driver_name']} | 📞 **رابطہ:** {v_details['driver_phone']}", f"🚐 **Vehicle:** {v_id} | 👤 **Driver:** {v_details['driver_name']} | 📞 **Contact:** {v_details['driver_phone']}")
                    st.info(veh_info)
                    
                    if st.button("🔄 " + tr("ریفریش لائیو لوکیشن (Refresh Location)", "Refresh Live Location")):
                        st.rerun()
                        
                    map_df = pd.read_sql(f"SELECT lat as latitude, lon as longitude, last_updated FROM live_locations WHERE device_id='{v_details['gps_device_id']}'", conn)
                    if not map_df.empty:
                        st.map(map_df, zoom=14, use_container_width=True)
                        st.caption(tr(f"آخری اپڈیٹ: {map_df.iloc[0]['last_updated']}", f"Last Updated: {map_df.iloc[0]['last_updated']}"))
                    else:
                        st.warning(tr("گاڑی کا جی پی ایس سگنل موصول نہیں ہو رہا۔", "Vehicle GPS signal not received."))
                else:
                    st.warning(tr("⚠️ آپ کا بچہ سکول کی ٹرانسپورٹ سروس میں رجسٹرڈ نہیں ہے۔ بکنگ کے لیے انتظامیہ سے رابطہ کریں۔", "⚠️ Your child is not registered in the school transport service. Please contact administration for booking."))
            except Exception as e:
                st.error(tr("ٹرانسپورٹ سسٹم فی الحال اپڈیٹ ہو رہا ہے۔", "Transport system is currently being updated."))

        # 🟢 ہیلپ ڈیسک اور شکایات (والدین کے لیے)
        with p_tab6:
            st.markdown(f"#### 🎧 {tr('سکول انتظامیہ کو شکایت یا تجویز بھیجیں', 'Send Complaint/Feedback to School Admin')}")
            
            with st.form("comp_form", clear_on_submit=True):
                c_sub = st.text_input(tr("موضوع / عنوان (Subject) *", "Subject / Title *"))
                c_det = st.text_area(tr("تفصیل (Details) *", "Details *"))
                
                if st.form_submit_button(tr("ارسال کریں (Submit)", "Submit"), type="primary"):
                    if c_sub.strip() and c_det.strip():
                        cursor.execute("INSERT INTO complaints (date, sender_name, sender_type, reg_id, subject, details, admin_reply) VALUES (?, ?, ?, ?, ?, ?, ?)", (datetime.date.today().strftime("%Y-%m-%d"), s_name, "Parent", s_reg, c_sub, c_det, tr('انتظار فرمائیں...', 'Please wait...')))
                        conn.commit()
                        st.success(tr("آپ کی بات پرنسپل تک پہنچا دی گئی ہے۔ شکریہ!", "Your message has been sent to the Principal. Thank you!"))
                    else:
                        st.error(tr("موضوع اور تفصیل لکھنا لازمی ہے۔", "Subject and Details are required."))
            
            st.write("---")
            st.markdown(f"**{tr('آپ کی پچھلی شکایات / تجاویز:', 'Your Past Complaints / Feedback:')}**")
            p_comp = pd.read_sql(f"SELECT date, subject, details, status, admin_reply FROM complaints WHERE reg_id='{s_reg}' ORDER BY id DESC", conn)
            
            if not p_comp.empty:
                for _, r in p_comp.iterrows():
                    stat_icon = "🟢" if r['status'] == "Resolved" else "🔴"
                    with st.expander(f"{stat_icon} {r['date']} | {r['subject']}"):
                        st.write(r['details'])
                        st.markdown(f"**{tr('سکول کا جواب:', 'School Reply:')}**\n\n> {r['admin_reply']}")
            else:
                st.info(tr("کوئی پرانی ہسٹری نہیں۔", "No history found."))
                
    else:
        st.error(tr("⚠️ آپ کے اکاؤنٹ کے ساتھ کوئی طالب علم منسلک نہیں ہے۔ براہ کرم سکول انتظامیہ سے اپنا رجسٹرڈ فون نمبر درست کروائیں۔", "⚠️ No student is linked to your account. Please get your registered phone number corrected by the school administration."))

# ================= 15.1 لائبریری مینجمنٹ (Library System) =================
elif core_choice in ["لائبریری", "Library"]:
    if not sub_choice:
        sub_choice = "کتابوں کا ریکارڈ" if st.session_state.ui_lang == "اردو" else "Manage Books"
        
    st.markdown(f"<h2 class='no-print'>&#128214; {tr('لائبریری مینجمنٹ', 'Library Management')} - {tr(sub_choice, sub_choice)}</h2>", unsafe_allow_html=True)
    
    if sub_choice in ["Manage Books", "کتابوں کا ریکارڈ"]:
        with st.expander(tr("➕ نئی کتاب شامل کریں (Add New Book)", "➕ Add New Book"), expanded=True):
            with st.form("add_book_form", clear_on_submit=True):
                c1, c2, c3 = st.columns(3)
                b_id = c1.text_input(tr("کتاب کا نمبر / ISBN", "Book ID / ISBN"), placeholder="مثلاً: BK-1001")
                b_title = c2.text_input(tr("کتاب کا نام", "Book Title"), placeholder="مثلاً: بانگِ درا")
                b_author = c3.text_input(tr("مصنف کا نام", "Author Name"))
                
                c4, c5 = st.columns(2)
                b_cat = c4.selectbox(tr("کیٹیگری (Category)", "Category"), ["Literature", "Science", "History", "Islamic", "General Knowledge", "Fiction", "Course Book"])
                b_qty = c5.number_input(tr("کل تعداد (Total Quantity)", "Total Quantity"), min_value=1, value=1)
                
                if st.form_submit_button(tr("کتاب محفوظ کریں", "Save Book"), type="primary"):
                    if b_id and b_title:
                        try:
                            cursor.execute("INSERT INTO books VALUES (?, ?, ?, ?, ?, ?)", (b_id, b_title, b_author, b_cat, b_qty, b_qty))
                            conn.commit()
                            st.success(tr("کتاب کامیابی سے شامل ہو گئی!", "Book added successfully!"))
                            import time
                            time.sleep(1)
                            st.rerun()
                        except:
                            st.error(tr("یہ بک آئی ڈی پہلے سے موجود ہے۔", "Book ID already exists."))
                    else:
                        st.warning(tr("آئی ڈی اور نام لازمی ہے۔", "ID and Title are required."))
                    
        st.write("---")
        st.markdown(f"#### &#128218; {tr('موجودہ کتابوں کا ریکارڈ', 'Books Inventory')}", unsafe_allow_html=True)
        books_df = pd.read_sql("SELECT book_id as 'ID', title as 'Title', author as 'Author', category as 'Category', total_qty as 'Total Qty', available_qty as 'Available Qty' FROM books", conn)
        if not books_df.empty:
            st.dataframe(books_df, use_container_width=True, hide_index=True)
        else:
            st.info(tr("لائبریری میں کوئی کتاب موجود نہیں۔", "No books in library."))

    elif sub_choice in ["Issue / Return Books", "کتاب جاری / واپس کریں"]:
        # 🟢 ٹیبز کی بجائے ریڈیو بٹن کا استعمال کیا گیا ہے تاکہ فارم چھپے نہیں
        action_type = st.radio(tr("آپ کیا کرنا چاہتے ہیں؟", "What do you want to do?"), [tr("کتاب جاری کریں (Issue Book)", "Issue Book"), tr("کتاب واپس لیں (Return Book)", "Return Book")], horizontal=True)
        st.write("---")
        
        if "Issue" in action_type or "جاری" in action_type:
            st.markdown(f"### &#128228; {tr('نئی کتاب جاری کریں', 'Issue New Book')}", unsafe_allow_html=True)
            books_df = pd.read_sql("SELECT book_id, title, available_qty FROM books WHERE available_qty > 0", conn)
            
            if not books_df.empty:
                b_opts = [f"{r['title']} (ID: {r['book_id']}) - Available: {r['available_qty']}" for _, r in books_df.iterrows()]
                
                c_is1, c_is2 = st.columns(2)
                iss_book = c_is1.selectbox(tr("کتاب منتخب کریں", "Select Book"), b_opts, key="iss_book_sel")
                iss_type = c_is2.radio(tr("کس کو جاری کرنی ہے؟", "Issue to?"), ["Student", "Staff"], horizontal=True, key="iss_type_rad")
                
                c_is3, c_is4 = st.columns(2)
                iss_reg = ""
                
                if iss_type == "Student":
                    stu_df = pd.read_sql("SELECT reg_id, name, class, section FROM students WHERE status='Active'", conn)
                    if not stu_df.empty:
                        stu_opts = [f"{r['name']} (Class: {r['class']} {r['section']}) - ID: {r['reg_id']}" for _, r in stu_df.iterrows()]
                        sel_person = c_is3.selectbox(tr("طالب علم منتخب کریں", "Select Student"), stu_opts, key="iss_stu_sel")
                        iss_reg = sel_person.split(" - ID: ")[1]
                    else:
                        c_is3.warning(tr("کوئی طالب علم موجود نہیں۔", "No active students found."))
                else:
                    stf_df = pd.read_sql("SELECT staff_id, name, designation FROM staff", conn)
                    if not stf_df.empty:
                        stf_opts = [f"{r['name']} ({r['designation']}) - ID: {r['staff_id']}" for _, r in stf_df.iterrows()]
                        sel_person = c_is3.selectbox(tr("سٹاف ممبر منتخب کریں", "Select Staff"), stf_opts, key="iss_stf_sel")
                        iss_reg = sel_person.split(" - ID: ")[1]
                    else:
                        c_is3.warning(tr("کوئی سٹاف موجود نہیں۔", "No staff found."))
                
                due_d = c_is4.date_input(tr("واپسی کی تاریخ", "Due Date"), datetime.date.today() + datetime.timedelta(days=7), key="iss_date_inp")
                
                if st.button(tr("کتاب جاری کریں (Issue Now)", "Issue Now"), type="primary", key="iss_btn_now"):
                    if iss_reg.strip():
                        b_id_sel = iss_book.split(" (ID: ")[1].split(")")[0]
                        issue_dt = datetime.date.today().strftime("%Y-%m-%d")
                        cursor.execute("INSERT INTO book_issue (book_id, issued_to_type, reg_id, issue_date, due_date) VALUES (?, ?, ?, ?, ?)", (b_id_sel, iss_type, iss_reg, issue_dt, due_d.strftime("%Y-%m-%d")))
                        cursor.execute(f"UPDATE books SET available_qty = available_qty - 1 WHERE book_id='{b_id_sel}'")
                        conn.commit()
                        st.success(tr("کتاب کامیابی سے جاری کر دی گئی!", "Book issued successfully!"))
                        import time
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error(tr("آئی ڈی منتخب کرنا لازمی ہے۔", "ID selection is required."))
            else:
                st.warning(tr("اس وقت لائبریری میں جاری کرنے کے لیے کوئی کتاب دستیاب نہیں ہے۔", "No books available in library to issue."))
                
        elif "Return" in action_type or "واپس" in action_type:
            st.markdown(f"### &#128229; {tr('کتاب واپس لیں', 'Return Book')}", unsafe_allow_html=True)
            issued_df = pd.read_sql("SELECT bi.id, bi.book_id, b.title, bi.issued_to_type, bi.reg_id, bi.due_date FROM book_issue bi JOIN books b ON bi.book_id = b.book_id WHERE bi.status='Issued'", conn)
            
            if not issued_df.empty:
                ret_opts = [f"Issue ID: {r['id']} | {r['title']} -> {r['issued_to_type']} ({r['reg_id']}) | Due: {r['due_date']}" for _, r in issued_df.iterrows()]
                ret_sel = st.selectbox(tr("واپس آنے والی کتاب کا انتخاب کریں", "Select Book to Return"), ret_opts, key="ret_book_sel")
                
                ret_id = ret_sel.split("Issue ID: ")[1].split(" |")[0]
                b_id_ret = issued_df[issued_df['id'] == int(ret_id)].iloc[0]['book_id']
                due_date_str = issued_df[issued_df['id'] == int(ret_id)].iloc[0]['due_date']
                
                due_date_obj = datetime.datetime.strptime(due_date_str, "%Y-%m-%d").date()
                today_obj = datetime.date.today()
                late_days = (today_obj - due_date_obj).days if today_obj > due_date_obj else 0
                fine_amt = late_days * 20 # 20 روپے فی دن جرمانہ
                
                if late_days > 0:
                    st.error(f"&#9888;&#65039; {tr('یہ کتاب لیٹ ہے! تاخیر:', 'This book is late! Delayed by:')} {late_days} Days. | {tr('جرمانہ:', 'Fine:')} Rs {fine_amt}")
                else:
                    st.success(tr("یہ کتاب وقت پر واپس آ رہی ہے۔ کوئی جرمانہ نہیں۔", "Book is returned on time. No fine."))
                
                if st.button(tr("کتاب واپس لیں (Mark as Returned)", "Mark as Returned"), type="primary", key="ret_btn_now"):
                    cursor.execute(f"UPDATE book_issue SET status='Returned', return_date='{today_obj.strftime('%Y-%m-%d')}', fine={fine_amt} WHERE id={ret_id}")
                    cursor.execute(f"UPDATE books SET available_qty = available_qty + 1 WHERE book_id='{b_id_ret}'")
                    if fine_amt > 0:
                        v_num = pd.read_sql("SELECT COUNT(*) FROM accounts", conn).iloc[0, 0] + 1001
                        cursor.execute("INSERT INTO accounts (date, type, description, amount, head_name, voucher_no) VALUES (?, 'آمدنی', ?, ?, 'Library Fine', ?)", (today_obj.strftime("%Y-%m-%d"), f"Late Fine Book ID: {b_id_ret}", fine_amt, f"V-{v_num}"))
                    conn.commit()
                    st.success(tr("کتاب کی واپسی درج ہو گئی اور سٹاک اپڈیٹ ہو گیا!", "Book returned successfully and stock updated!"))
                    import time
                    time.sleep(1)
                    st.rerun()
            else: 
                st.success(tr("کوئی کتاب جاری نہیں کی گئی۔ تمام کتابیں لائبریری میں موجود ہیں۔", "No issued books pending. All books are in library."))

    elif sub_choice in ["Library Reports", "لائبریری رپورٹس"]:
        st.markdown(f"### &#128202; {tr('لائبریری کی رپورٹ', 'Library Report')}", unsafe_allow_html=True)
        rep_df = pd.read_sql("SELECT bi.id, b.title as 'Book Title', bi.issued_to_type as 'Type', bi.reg_id as 'User ID', bi.issue_date as 'Issue Date', bi.due_date as 'Due Date', bi.status as 'Status', bi.fine as 'Fine' FROM book_issue bi JOIN books b ON bi.book_id = b.book_id ORDER BY bi.id DESC", conn)
        if not rep_df.empty:
            st.dataframe(rep_df, use_container_width=True, hide_index=True)
        else:
            st.info(tr("کوئی ریکارڈ موجود نہیں۔", "No records."))

# ================= 15.2 گیٹ سیکیورٹی اور ڈیجیٹل وزیٹر بک (Gate Security) =================
elif core_choice in ["گیٹ سیکیورٹی", "Gate Security"]:
    if not sub_choice:
        sub_choice = "نیا وزیٹر (انٹری)" if st.session_state.ui_lang == "اردو" else "New Visitor (Entry)"
        
    st.markdown(f"<h2 class='no-print'>&#128110; {tr('ڈیجیٹل وزیٹر بک اور سیکیورٹی', 'Visitor Book & Gate Security')} - {tr(sub_choice, sub_choice)}</h2>", unsafe_allow_html=True)
    
    if sub_choice in ["New Visitor (Entry)", "نیا وزیٹر (انٹری)"]:
        st.markdown(f"#### &#9997; {tr('نئے مہمان کی انٹری درج کریں', 'Register New Visitor')}", unsafe_allow_html=True)
        with st.form("visitor_entry_form", clear_on_submit=True):
            c1, c2, c3 = st.columns(3)
            v_name = c1.text_input(tr("مہمان کا نام (Visitor Name) *", "Visitor Name *"))
            v_phone = c2.text_input(tr("موبائل نمبر / شناختی کارڈ", "Phone / CNIC"))
            v_meet = c3.selectbox(tr("کس سے ملنا ہے؟", "Whom to meet?"), ["Principal", "Admin / Operator", "Teacher", "Student", "Accounts", "Other"])
            
            v_purp = st.text_input(tr("آنے کا مقصد (Purpose of Visit)", "Purpose of Visit"))
            
            if st.form_submit_button(tr("گیٹ پاس بنائیں (Generate Gate Pass)", "Generate Gate Pass"), type="primary"):
                if v_name.strip():
                    time_in = datetime.datetime.now().strftime("%I:%M %p")
                    date_today = datetime.date.today().strftime("%Y-%m-%d")
                    cursor.execute("INSERT INTO visitors (date, time_in, time_out, name, phone, purpose, to_meet, status) VALUES (?, ?, '-', ?, ?, ?, ?, 'Inside')", (date_today, time_in, v_name, v_phone, v_purp, v_meet))
                    conn.commit()
                    
                    # پرنٹ ایبل گیٹ پاس
                    pass_id = pd.read_sql("SELECT MAX(id) FROM visitors", conn).iloc[0, 0]
                    t = {"align": "left", "dir": "ltr"} if st.session_state.ui_lang == "English" else {"align": "right", "dir": "rtl"}
                    pass_html = f"""
                    <div style="border: 3px solid #333; width: 3.5in; padding: 15px; margin: 0 auto; font-family: Arial, sans-serif; text-align: center; border-radius: 10px; background-color: white; color: black;" dir="{t['dir']}">
                        <h2 style="margin:0; color:#1a4f8b; font-size:18px;">{school_name.upper()}</h2>
                        <div style="background-color: #333; color: white; margin: 10px 0; padding: 5px; font-weight: bold; font-size: 14px;">VISITOR GATE PASS</div>
                        <table style="width: 100%; text-align: {t['align']}; font-size: 12px; line-height: 1.8;">
                            <tr><td><b>Pass No:</b></td><td>GP-{pass_id}</td></tr>
                            <tr><td><b>Date & Time:</b></td><td>{date_today} ({time_in})</td></tr>
                            <tr><td><b>Name:</b></td><td>{v_name}</td></tr>
                            <tr><td><b>To Meet:</b></td><td>{v_meet}</td></tr>
                            <tr><td><b>Purpose:</b></td><td>{v_purp}</td></tr>
                        </table>
                        <div style="margin-top: 25px; border-top: 1px dashed #999; padding-top: 5px; font-size: 9px; color: #555;">
                            Valid for today only. Please return this pass to security at the exit gate.
                        </div>
                    </div>
                    """
                    st.success(tr("انٹری ہو گئی! گیٹ پاس پرنٹ کریں۔", "Entry saved! Print the gate pass."))
                    print_button_js(pass_html, tr("گیٹ پاس پرنٹ کریں", "Print Gate Pass"), landscape=False)
                else: 
                    st.error(tr("مہمان کا نام لازمی ہے۔", "Visitor name is required."))

    elif sub_choice in ["Active Visitors (Out)", "موجودہ وزیٹرز (آؤٹ)"]:
        st.markdown(f"### &#128694; {tr('سکول کے اندر موجود مہمان', 'Visitors currently inside')}", unsafe_allow_html=True)
        v_in_df = pd.read_sql("SELECT id, time_in as 'Time In', name as 'Name', phone as 'Phone', to_meet as 'To Meet', purpose as 'Purpose' FROM visitors WHERE status='Inside' AND date=DATE('now', 'localtime')", conn)
        
        if not v_in_df.empty:
            for _, r in v_in_df.iterrows():
                cc1, cc2 = st.columns([4, 1])
                cc1.info(f"&#128100; **{r['Name']}** | To Meet: {r['To Meet']} | In: {r['Time In']}")
                if cc2.button("Check Out", key=f"cout_{r['id']}", type="primary", use_container_width=True):
                    time_out = datetime.datetime.now().strftime("%I:%M %p")
                    cursor.execute(f"UPDATE visitors SET status='Left', time_out='{time_out}' WHERE id={r['id']}")
                    conn.commit()
                    st.rerun()
        else:
            st.success(tr("اس وقت سکول کے اندر کوئی مہمان موجود نہیں۔", "No active visitors inside the premises."))

    elif sub_choice in ["Visitor History", "وزیٹر ہسٹری"]:
        st.markdown(f"### &#128220; {tr('وزیٹر ہسٹری (مکمل ریکارڈ)', 'Visitor History (Full Record)')}", unsafe_allow_html=True)
        st.write(tr("یہاں سے آپ پرانے مہمانوں کا ریکارڈ تاریخ، نام یا شناختی کارڈ/فون نمبر کے ذریعے تلاش کر سکتے ہیں۔", "Search visitor history by date, name, or CNIC/Phone."))
        
        with st.expander(tr("تلاش اور فلٹرز (Search & Filters)", "Search & Filters"), expanded=True):
            c_sh1, c_sh2, c_sh3 = st.columns(3)
            
            # 🟢 ڈبل ڈیٹ (Date Range) کا فلٹر
            f_date = c_sh1.date_input(tr("تاریخ کی حد (Date Range)", "Date Range"), value=[], help=tr("دو تاریخوں کے درمیان ریکارڈ دیکھنے کے لیے", "To view records between two dates"))
            f_name = c_sh2.text_input(tr("نام سے تلاش کریں", "Search by Name"), placeholder="مثلاً: Ali")
            f_phone = c_sh3.text_input(tr("فون نمبر / CNIC", "Phone / CNIC"), placeholder="مثلاً: 0300... یا 38403...")
            
            if st.button(tr("فلٹرز صاف کریں (Clear Filters)", "Clear Filters")):
                st.rerun()

        base_query = "SELECT date as 'Date', name as 'Name', phone as 'Phone/CNIC', to_meet as 'Whom to Meet', time_in as 'Time In', time_out as 'Time Out', status as 'Status' FROM visitors WHERE 1=1"
        
        # 🟢 تاریخ کے حساب سے کیوری جنریٹ کرنا
        if f_date:
            if len(f_date) == 2:
                # اگر دو تاریخیں سلیکٹ کی گئی ہیں (شروع اور ختم)
                base_query += f" AND date >= '{f_date[0].strftime('%Y-%m-%d')}' AND date <= '{f_date[1].strftime('%Y-%m-%d')}'"
            elif len(f_date) == 1:
                # اگر صرف ایک تاریخ سلیکٹ کی گئی ہے
                base_query += f" AND date = '{f_date[0].strftime('%Y-%m-%d')}'"
                
        if f_name.strip():
            base_query += f" AND name LIKE '%{f_name.strip()}%'"
        if f_phone.strip():
            base_query += f" AND phone LIKE '%{f_phone.strip()}%'"
            
        base_query += " ORDER BY id DESC LIMIT 500" 
        
        try:
            v_hist = pd.read_sql(base_query, conn)
        except Exception as e:
            v_hist = pd.DataFrame()
            st.error(f"Error fetching records: {e}")

        if not v_hist.empty:
            st.success(f"✅ {tr('کل', 'Total')} **{len(v_hist)}** {tr('ریکارڈز ملے', 'records found')}")
            
            # پرنٹنگ کے لیے ڈیٹا فریم کو الگ متغیر میں محفوظ کر رہے ہیں
            print_df = v_hist.copy()
            
            if st.session_state.ui_lang == "اردو":
                v_hist.columns = ['تاریخ', 'نام', 'فون/شناختی کارڈ', 'کس سے ملنا تھا', 'ٹائم اِن', 'ٹائم آؤٹ', 'سٹیٹس']
                v_hist['سٹیٹس'] = v_hist['سٹیٹس'].replace({'Inside': 'اندر موجود', 'Left': 'واپس چلے گئے'})
                
            st.dataframe(v_hist, use_container_width=True, hide_index=True)
            
            # 🟢 وزیٹر ہسٹری کا پرنٹ بٹن
            st.write("")
            if st.button("🖨️ " + tr("یہ ہسٹری پرنٹ کریں (Print History)", "Print this History"), type="primary", use_container_width=True):
                t = {"align": "left", "dir": "ltr"} if st.session_state.ui_lang == "English" else {"align": "right", "dir": "rtl"}
                html_table = v_hist.to_html(index=False, border=1, justify='center')
                html_table = html_table.replace('<table border="1" class="dataframe">', f'<table style="width:100%; border-collapse: collapse; text-align: center; font-size: 14px; border: 2px solid #000;" dir="{t["dir"]}">')
                html_table = html_table.replace('<th>', f'<th style="background-color:#1a4f8b; color:white; border:1px solid #000; padding:10px; text-align:center;">')
                html_table = html_table.replace('<td>', f'<td style="border:1px solid #000; padding:8px; text-align:center;">')
                
                logo_html = f'<img src="{logo_src_b64}" style="height: 60px; object-fit: contain;">' if 'logo_src_b64' in globals() and logo_src_b64 else ''
                
                print_html = f'''
                <div style="width: 100%; font-family: Arial, sans-serif;" dir="{t['dir']}">
                    <table style="width:100%; border:none; margin-bottom: 15px;">
                        <tr>
                            <td style="width: 20%; text-align: {t['align']}; vertical-align: middle;">{logo_html}</td>
                            <td style="width: 60%; text-align: center; vertical-align: middle;">
                                <h2 style="margin: 0; font-size: 24px; color: #1a4f8b;">{school_name.upper()}</h2>
                                <p style="margin: 4px 0; font-weight: bold; font-size: 12px;">{school_address}</p>
                                <h3 style="margin: 10px 0 0 0; text-decoration: underline; font-weight: bold; font-size: 18px;">{tr('وزیٹر ہسٹری رپورٹ', 'Visitor History Report')}</h3>
                            </td>
                            <td style="width: 20%;"></td>
                        </tr>
                    </table>
                    <div style="margin-bottom: 15px; font-size: 15px;"><b>{tr('کل مہمان:', 'Total Visitors:')}</b> {len(v_hist)}</div>
                    {html_table}
                </div>
                '''
                print_button_js(print_html, tr("پرنٹ کریں", "Print Now"), landscape=False)
        else: 
            st.info(tr("منتخب کردہ شرائط کے مطابق کوئی ریکارڈ نہیں ملا۔", "No records found matching the selected criteria."))

# ================= 15.3 انوینٹری اور سٹاک (Inventory) =================
elif core_choice in ["انوینٹری (سٹاک)", "Inventory"]:
    st.markdown(f"<h2 class='no-print'>📦 {tr('سکول انوینٹری اور سٹاک', 'School Inventory & Stock')} - {tr(sub_choice, sub_choice)}</h2>", unsafe_allow_html=True)
    
    if sub_choice in ["Add New Stock", "نیا سٹاک شامل کریں"]:
        with st.form("add_stock_form", clear_on_submit=True):
            c1, c2, c3 = st.columns(3)
            i_name = c1.text_input(tr("آئٹم کا نام (Item Name)", "Item Name"), placeholder="مثال: ڈیسک، کمپیوٹر، وائٹ بورڈ مارکر")
            i_cat = c2.selectbox(tr("کیٹیگری (Category)", "Category"), ["Furniture", "Electronics & IT", "Stationery", "Sports", "Lab Equipment", "Cleaning & Janitorial", "Other"])
            i_qty = c3.number_input(tr("مقدار (Quantity)", "Quantity"), min_value=1, value=1)
            
            if st.form_submit_button(tr("سٹاک میں شامل کریں", "Add to Stock"), type="primary"):
                if i_name.strip():
                    cursor.execute("INSERT INTO inventory (item_name, category, total_qty, used_qty) VALUES (?, ?, ?, 0)", (i_name, i_cat, i_qty))
                    conn.commit()
                    st.success(tr(f"{i_name} کی {i_qty} مقدار سٹاک میں شامل ہو گئی ہے۔", f"{i_qty} quantity of {i_name} added to stock."))
                    st.rerun()
                else:
                    st.error(tr("آئٹم کا نام لکھنا لازمی ہے۔", "Item name is required."))

    elif sub_choice in ["Stock Record", "سٹاک کا ریکارڈ"]:
        st.markdown(f"#### 📋 {tr('موجودہ سٹاک اور استعمال کی تفصیل', 'Current Stock & Usage Record')}")
        inv_df = pd.read_sql("SELECT id, item_name as 'Item Name', category as 'Category', total_qty as 'Total Qty', used_qty as 'Used Qty', (total_qty - used_qty) as 'Available' FROM inventory", conn)
        
        if not inv_df.empty:
            if st.session_state.ui_lang == "اردو":
                inv_df.columns = ['ID', 'آئٹم کا نام', 'کیٹیگری', 'کل مقدار', 'استعمال شدہ', 'دستیاب باقی']
            
            st.dataframe(inv_df, use_container_width=True, hide_index=True)
            
            st.write("---")
            st.markdown(f"#### 📉 {tr('سامان کا استعمال (Consume Stock)', 'Consume/Use Stock')}")
            c_use1, c_use2 = st.columns([2, 1])
            
            inv_opts = [f"{r['Item Name']} (Available: {r['Available']})" if st.session_state.ui_lang=="English" else f"{r['آئٹم کا نام']} (دستیاب: {r['دستیاب باقی']})" for _, r in inv_df.iterrows()]
            sel_item = c_use1.selectbox(tr("وہ آئٹم منتخب کریں جو استعمال ہوئی ہو", "Select Item to Consume"), inv_opts)
            use_qty = c_use2.number_input(tr("کتنی مقدار استعمال ہوئی؟", "How much quantity used?"), min_value=1, value=1)
            
            if st.button(tr("استعمال شدہ ظاہر کریں", "Mark as Used"), type="primary"):
                sel_id = inv_df.iloc[inv_opts.index(sel_item)]['ID']
                avail = inv_df.iloc[inv_opts.index(sel_item)]['Available' if st.session_state.ui_lang=="English" else 'دستیاب باقی']
                
                if use_qty <= avail:
                    cursor.execute(f"UPDATE inventory SET used_qty = used_qty + {use_qty} WHERE id={sel_id}")
                    conn.commit()
                    st.success(tr("سٹاک اپڈیٹ ہو گیا!", "Stock updated!"))
                    st.rerun()
                else:
                    st.error(tr("استعمال شدہ مقدار دستیاب سٹاک سے زیادہ نہیں ہو سکتی!", "Used quantity cannot be more than available stock!"))
        else:
            st.info(tr("سٹاک میں کوئی آئٹم موجود نہیں۔", "No items in stock."))

# ================= 15.4 ہیلپ ڈیسک (Helpdesk) =================
elif core_choice in ["ہیلپ ڈیسک (شکایات)", "Helpdesk"]:
    st.markdown(f"<h2 class='no-print'>&#127911; {tr('سپورٹ اور ہیلپ ڈیسک', 'Support & Helpdesk')}</h2>", unsafe_allow_html=True)
    
    current_u = st.session_state.current_user
    current_role = st.session_state.current_role
    
    s_id = st.session_state.ref_id
    if not s_id or s_id == "None" or s_id == "N/A":
        s_id = current_u.replace('staff_', '')
    
    # 🟢 سمارٹ فلٹر: ٹیچر کو صرف اس کی کلاس کی شکایات دکھائیں
    if current_role == "Teacher":
        st.info(tr("یہاں آپ کو صرف آپ کی تفویض کردہ (Assigned) کلاس کے طلباء کی شکایات اور تجاویز نظر آئیں گی۔", "Here you will only see complaints and suggestions from students in your assigned class."))
        try:
            cursor.execute(f"SELECT assigned_class, assigned_sec FROM staff WHERE staff_id='{s_id}'")
            t_data = cursor.fetchone()
        except:
            t_data = None
            
        if t_data and t_data[0] != "None":
            t_cls, t_sec = t_data[0], t_data[1]
            query = f"SELECT c.* FROM complaints c LEFT JOIN students s ON c.reg_id = s.reg_id WHERE s.class='{t_cls}' AND s.section='{t_sec}' ORDER BY c.id DESC"
        else:
            query = "SELECT * FROM complaints WHERE 1=0"
    else:
        st.info(tr("یہاں والدین اور سٹاف کی طرف سے بھیجی گئی تمام شکایات اور فیڈبیک کا ریکارڈ موجود ہے۔ پرنسپل انہیں پڑھ کر جواب دے سکتے ہیں۔", "Here you can manage all complaints and feedback. Principal can review and reply."))
        query = "SELECT * FROM complaints ORDER BY id DESC"
    
    try: comp_df = pd.read_sql(query, conn)
    except: comp_df = pd.DataFrame()
    
    if not comp_df.empty:
        pending_comps = comp_df[comp_df['status'] == 'Pending']
        resolved_comps = comp_df[comp_df['status'] != 'Pending']
        
        # 🟢 رول بیسڈ ٹیبز (ایڈمن کے لیے تیسرا اینالیٹکس ٹیب شامل کیا گیا ہے)
        if current_role in ["Admin", "Operator"]:
            tab_new, tab_old, tab_analytics = st.tabs([
                f"&#128308; {tr('نئی شکایات', 'Pending Complaints')} ({len(pending_comps)})", 
                f"&#128994; {tr('حل شدہ', 'Resolved')} ({len(resolved_comps)})",
                f"&#128202; {tr('تجزیہ اور رپورٹس (صرف ایڈمن)', 'Analytics & Filters (Admin)')}"
            ])
        else:
            tab_new, tab_old = st.tabs([
                f"&#128308; {tr('نئی شکایات', 'Pending Complaints')} ({len(pending_comps)})", 
                f"&#128994; {tr('حل شدہ', 'Resolved')} ({len(resolved_comps)})"
            ])
            tab_analytics = None # ٹیچر کے لیے یہ غائب رہے گا
        
        with tab_new:
            if not pending_comps.empty:
                for _, r in pending_comps.iterrows():
                    with st.expander(f"⚠️ {r['date']} | {r['subject']} - By: {r['sender_name']} ({r['sender_type']})"):
                        st.markdown(f"<div style='background-color:#fff3cd; padding:15px; border-left:4px solid #ffc107; border-radius:5px;'>{r['details']}</div>", unsafe_allow_html=True)
                        st.write("")
                        admin_rep = st.text_input(tr("اپنا جواب لکھیں:", "Write your reply:"), key=f"rep_{r['id']}")
                        if st.button("✅ " + tr("جواب بھیجیں اور حل شدہ کریں (Mark Resolved)", "Reply & Mark Resolved"), key=f"res_{r['id']}", type="primary"):
                            cursor.execute("UPDATE complaints SET status='Resolved', admin_reply=? WHERE id=?", (admin_rep, r['id']))
                            conn.commit()
                            st.success(tr("جواب بھیج دیا گیا!", "Reply Sent!"))
                            import time
                            time.sleep(1)
                            st.rerun()
            else:
                st.success(tr("اس وقت کوئی نئی شکایت موجود نہیں۔", "No pending complaints at the moment."))
                
        with tab_old:
            if not resolved_comps.empty:
                for _, r in resolved_comps.iterrows():
                    with st.expander(f"✅ {r['date']} | {r['subject']} - By: {r['sender_name']} ({r['sender_type']})"):
                        st.markdown(f"**{tr('شکایت/تجویز:', 'Complaint/Suggestion:')}**\n<div style='background-color:#f5f5f5; padding:10px; margin-bottom:10px;'>{r['details']}</div>", unsafe_allow_html=True)
                        st.markdown(f"**{tr('سکول کا جواب:', 'School Reply:')}**\n<div style='background-color:#e8f5e9; padding:10px; border-left:3px solid #4caf50;'>{r['admin_reply']}</div>", unsafe_allow_html=True)
            else:
                st.info(tr("کوئی پرانی شکایت موجود نہیں۔", "No resolved complaints found."))
                
        # 🟢 ایڈمن اینالیٹکس اور فلٹرز والا ٹیب
        if tab_analytics:
            with tab_analytics:
                st.markdown("### &#128202; " + tr("شکایات کا تجزیہ اور اسیسمنٹ (Filters)", "Complaints Analytics & Assessment"), unsafe_allow_html=True)
                st.write(tr("یہاں سے آپ ڈیلی، ویکلی، اور منتھلی بنیادوں پر کلاس اور ٹیچر کے لحاظ سے شکایات کا جائزہ لے کر پرفارمنس کا اندازہ لگا سکتے ہیں۔", "Filter complaints daily, weekly, or monthly by class and teacher to assess performance."))
                
                c_f1, c_f2, c_f3 = st.columns(3)
                
                time_opts = ["All Time (ہمیشہ)", "Today (ڈیلی)", "This Week (ویکلی)", "This Month (منتھلی)"]
                time_flt = c_f1.selectbox(tr("وقت کا انتخاب (Time)", "Time Period"), time_opts)
                
                db_cls = pd.read_sql("SELECT class_name FROM sys_classes", conn)['class_name'].tolist()
                if not db_cls: db_cls = classes_list
                cls_flt = c_f2.selectbox(tr("کلاس (Class-wise)", "Class-wise"), ["All"] + db_cls)
                
                t_df = pd.read_sql("SELECT name, assigned_class FROM staff WHERE designation='Teacher' OR designation='استاد / ٹیچر'", conn)
                t_opts = ["All"] + t_df['name'].tolist() if not t_df.empty else ["All"]
                tch_flt = c_f3.selectbox(tr("ٹیچر کے لحاظ سے (Teacher-wise)", "Teacher-wise"), t_opts)
                
                q = "SELECT c.id, c.date, c.sender_name, c.subject, c.details, c.status, s.class as cls, s.section as sec FROM complaints c LEFT JOIN students s ON c.reg_id = s.reg_id WHERE 1=1"
                
                today_dt = datetime.date.today()
                if "Today" in time_flt:
                    q += f" AND c.date = '{today_dt.strftime('%Y-%m-%d')}'"
                elif "Week" in time_flt:
                    week_ago_dt = today_dt - datetime.timedelta(days=7)
                    q += f" AND c.date >= '{week_ago_dt.strftime('%Y-%m-%d')}'"
                elif "Month" in time_flt:
                    month_start_dt = today_dt.replace(day=1)
                    q += f" AND c.date >= '{month_start_dt.strftime('%Y-%m-%d')}'"
                    
                if cls_flt != "All":
                    q += f" AND s.class = '{cls_flt}'"
                    
                if tch_flt != "All":
                    try:
                        t_cls = t_df[t_df['name'] == tch_flt].iloc[0]['assigned_class']
                        q += f" AND s.class = '{t_cls}'"
                    except: pass
                    
                q += " ORDER BY c.id DESC"
                
                try: ana_df = pd.read_sql(q, conn)
                except: ana_df = pd.DataFrame()
                
                if not ana_df.empty:
                    tot_c = len(ana_df)
                    res_c = len(ana_df[ana_df['status'] == 'Resolved'])
                    pen_c = len(ana_df[ana_df['status'] == 'Pending'])
                    
                    st.write("---")
                    m1, m2, m3 = st.columns(3)
                    m1.markdown(f"<div style='background-color:#e3f2fd; padding:15px; border-radius:10px; border:2px solid #2196f3; text-align:center;'><h4 style='margin:0; color:#0d47a1;'>{tot_c}</h4><p style='margin:0; color:#555;'>{tr('اس فلٹر کی کل شکایات', 'Total in this filter')}</p></div>", unsafe_allow_html=True)
                    m2.markdown(f"<div style='background-color:#e8f5e9; padding:15px; border-radius:10px; border:2px solid #4caf50; text-align:center;'><h4 style='margin:0; color:#1b5e20;'>{res_c}</h4><p style='margin:0; color:#555;'>{tr('حل شدہ (Resolved)', 'Resolved')}</p></div>", unsafe_allow_html=True)
                    m3.markdown(f"<div style='background-color:#ffebee; padding:15px; border-radius:10px; border:2px solid #f44336; text-align:center;'><h4 style='margin:0; color:#b71c1c;'>{pen_c}</h4><p style='margin:0; color:#555;'>{tr('زیر التواء (Pending)', 'Pending')}</p></div>", unsafe_allow_html=True)
                    
                    st.write("")
                    disp_df = ana_df[['date', 'sender_name', 'cls', 'subject', 'status']].copy()
                    
                    if st.session_state.ui_lang == "اردو":
                        disp_df.columns = ['تاریخ', 'بھیجنے والا', 'متعلقہ کلاس', 'عنوان', 'سٹیٹس']
                        disp_df['سٹیٹس'] = disp_df['سٹیٹس'].replace({'Pending': 'زیر التواء', 'Resolved': 'حل شدہ'})
                    else:
                        disp_df.columns = ['Date', 'Sender', 'Class', 'Subject', 'Status']
                        
                    st.dataframe(disp_df, use_container_width=True, hide_index=True)
# 🟢 پرنٹ رپورٹ بٹن (صرف ایڈمن کے لیے)
                    st.write("")
                    if st.button("🖨️ " + tr("یہ تجزیاتی رپورٹ پرنٹ کریں", "Print this Analytics Report"), type="primary", use_container_width=True):
                        t = {"align": "left", "dir": "ltr"} if st.session_state.ui_lang == "English" else {"align": "right", "dir": "rtl"}
                        html_table = disp_df.to_html(index=False, border=1, justify='center')
                        html_table = html_table.replace('<table border="1" class="dataframe">', f'<table style="width:100%; border-collapse: collapse; text-align: center; font-size: 14px; border: 2px solid #000;" dir="{t["dir"]}">')
                        html_table = html_table.replace('<th>', f'<th style="background-color:#1a4f8b; color:white; border:1px solid #000; padding:10px; text-align:center;">')
                        html_table = html_table.replace('<td>', f'<td style="border:1px solid #000; padding:10px; text-align:center;">')
                        
                        logo_html = f'<img src="{logo_src_b64}" style="height: 60px; object-fit: contain;">' if logo_src_b64 else ''
                        
                        print_html = f'''
                        <div style="width: 100%; font-family: Arial, sans-serif;" dir="{t['dir']}">
                            <table style="width:100%; border:none; margin-bottom: 15px;">
                                <tr>
                                    <td style="width: 20%; text-align: {t['align']}; vertical-align: middle;">{logo_html}</td>
                                    <td style="width: 60%; text-align: center; vertical-align: middle;">
                                        <h2 style="margin: 0; font-size: 24px; color: #1a4f8b;">{school_name.upper()}</h2>
                                        <p style="margin: 4px 0; font-weight: bold; font-size: 12px;">{school_address}</p>
                                        <h3 style="margin: 10px 0 0 0; text-decoration: underline; font-weight: bold; font-size: 18px;">{tr('شکایات کا تجزیہ اور اسیسمنٹ رپورٹ', 'Complaints Analytics & Assessment Report')}</h3>
                                    </td>
                                    <td style="width: 20%;"></td>
                                </tr>
                            </table>
                            <div style="display:flex; justify-content: space-between; border: 2px solid #333; padding: 10px; margin-bottom: 20px; background-color: #f9f9f9; font-size:15px;">
                                <div><b>{tr('کل شکایات:', 'Total Complaints:')}</b> {tot_c}</div>
                                <div style="color: green;"><b>{tr('حل شدہ:', 'Resolved:')}</b> {res_c}</div>
                                <div style="color: red;"><b>{tr('زیر التواء:', 'Pending:')}</b> {pen_c}</div>
                            </div>
                            {html_table}
                        </div>
                        '''
                        print_button_js(print_html, tr("پرنٹ کریں", "Print Now"), landscape=False)
                else:
                    st.info(tr("منتخب کردہ فلٹرز کے مطابق کوئی شکایت نہیں ملی۔", "No complaints found for the selected filters."))
                    
    else:
        st.info(tr("سسٹم میں تاحال کوئی متعلقہ شکایت یا تجویز درج نہیں کی گئی۔", "No relevant complaints or suggestions registered in the system yet."))


# ================= 16. اے آئی مواد جنریٹر =================
elif core_choice in ["اے آئی جنریٹر", "AI Generator"]:
    st.markdown(f"<h2 class='no-print'>🤖 {tr('اے آئی مواد جنریٹر (AI Content Generator)', 'AI Content Generator')}</h2>", unsafe_allow_html=True)
    st.markdown(f"<p class='no-print'>{tr('یہاں سے آپ سکول کے لیے تفصیلی نظمیں، کہانیاں، مضامین، اور تقاریر خود بخود تیار کروا سکتے ہیں۔', 'Generate detailed poems, stories, essays, and speeches automatically for school use.')}</p>", unsafe_allow_html=True)
    
    st.write("---")
    
    c1, c2 = st.columns(2)
    content_type = c1.selectbox(tr("مضمون یا مواد کی قسم", "Select Content Type"), [
        tr("مضمون (Detailed Essay)", "Detailed Essay"), 
        tr("تقریر (Detailed Speech)", "Detailed Speech"), 
        tr("نظم / ملی نغمہ (Long Poem / Anthem)", "Long Poem / Anthem"), 
        tr("کہانی (Long Story)", "Long Story"), 
        tr("خصوصی پیغام / نوٹس (Detailed Notice / Message)", "Detailed Notice / Message")
    ])
    
    lang_choice = c2.selectbox(tr("زبان کا انتخاب", "Language Selection"), ["اردو (Urdu)", "English"])
    
    topic_prompt = st.text_area(tr("عنوان یا تفصیل درج کریں (مثلاً: یومِ آزادی، علم کی اہمیت، محنت کا پھل، استاد کا احترام)", "Enter Topic or Details (e.g., Independence Day, Importance of Education)"))
    
    if st.button(tr("✨ تفصیلی مواد تیار کروائیں (Generate Detailed Content)", "✨ Generate Detailed Content"), type="primary"):
        if not topic_prompt.strip():
            st.error(tr("براہ کرم پہلے عنوان یا تفصیل درج کریں۔", "Please enter a topic or prompt first."))
        else:
            with st.spinner(tr("تفصیلی اور معیاری مواد تیار کیا جا رہا ہے، براہ کرم انتظار کریں...", "Generating detailed and professional content, please wait...")):
                try:
                    if "اردو" in lang_choice:
                        if "مضمون" in content_type or "Essay" in content_type:
                            generated_text = f"""### عنوان: {topic_prompt}\n\n**1. تمہید اور تعارف:**\nزندگی کے ہر شعبے میں {topic_prompt} کی اہمیت ایک مسلمہ حقیقت ہے۔ یہ ایک ایسا موضوع ہے جس نے نہ صرف انفرادی بلکہ اجتماعی سطح پر انسانی معاشرے کو متاثر کیا ہے۔ تاریخ گواہ ہے کہ جن قوموں نے اس اصول کو اپنایا، انھوں نے دنیا بھر میں سرخروئی حاصل کی۔\n\n**2. موضوع کی اہمیت و افادیت:**\nجب ہم اس کا گہرائی سے مطالعہ کرتے ہیں تو یہ بات واضح ہوتی ہے کہ {topic_prompt} کے بغیر کامیابی کا حصول ناممکن ہے۔ یہ انسان کے اندر نظم و ضبط، عزم صمیم اور آگے بڑھنے کی لگن پیدا کرتا ہے۔ طالب علموں کے لیے بالخصوص یہ وہ زینہ ہے جس پر چڑھ کر وہ بلند ترین منازل طے کر سکتے ہیں۔\n\n**3. معاشرتی اور اخلاقی پہلو:**\nمعاشرے کی تشکیل میں ایسی اقدار کا بڑا ہاتھ ہوتا ہے۔ ہمیں چاہیے کہ ہم اپنے گھروں اور سکولوں میں بچوں کی تربیت اسی نہج پر کریں تاکہ وہ بڑے ہو کر ایک ذمہ دار شہری بن سکیں۔ دارالخدیجہ سکول سسٹم جیسے ادارے اسی مقصد کے تحت طلباء میں یہ روح بیدار کر رہے ہیں۔\n\n**4. چیلنجز اور ان کا حل:**\nبلاشبہ اس راہ میں کچھ مشکلات بھی حائل ہوتی ہیں، لیکن پختہ ارادہ اور مسلسل محنت تمام رکاوٹوں کو دور کر دیتی ہے۔ ہمیں سستی اور کاہلی کو چھوڑ کر عملی میدان میں اترنا ہوگا۔\n\n**5. نتیجہ اور سفارشات:**\nآخر میں اس عزم کا اعادہ کرنا ضروری ہے کہ ہم {topic_prompt} کو اپنی زندگی کا شعار بنائیں گے۔ یہی وہ واحد راستہ ہے جو ہمیں ایک روشن، خوشحال اور ترقی یافتہ مستقبل کی طرف لے جاتا ہے۔"""
                        elif "تقریر" in content_type or "Speech" in content_type:
                            generated_text = f"""### عنوان: {topic_prompt}\n\nحضراتِ صدر، محترم اساتذہ کرام اور میرے عزیز ساتھیو!\nالسلام علیکم ورحمۃ اللہ وبرکاتہ!\n\nآج اس پروقار اسٹیج پر کھڑے ہو کر مجھے جس موضوع پر بات کرنے کا موقع ملا ہے، وہ ہے: **{topic_prompt}**۔\n\nسب سے پہلے میں اپنے اساتذہ کا تہِ دل سے شکریہ ادا کرتا ہوں جن کی تربیت کی بدولت آج ہم اس قابل ہوئے ہیں کہ اس اہم اسٹیج سے اپنے خیالات کا اظہار کر سکیں۔ \n\nساتھیو! دنیا کی کوئی بھی قوم اس وقت تک ترقی نہیں کر سکتی جب تک وہ اپنے اصل مقاصد سے جڑی نہ ہو۔ آج کا یہ دن ہمیں یاد دلاتا ہے کہ {topic_prompt} ہماری زندگی کا کتنا اہم حصہ ہے۔ اگر ہم نے آج اس پر غور نہ کیا اور عملی اقدامات نہ اٹھائے، تو آنے والا وقت ہمیں معاف نہیں کرے گا۔\n\nآئیے آج اس مقدس مٹی کو گواہ بنا کر یہ عہد کریں کہ ہم اپنی تمام صلاحیتیں اسکول کی بہتری اور ملک کی ترقی کے لیے وقف کر دیں گے۔ محنت ہمارا شعار ہو گی اور صداقت ہمارا طرۂ امتیاز!\n\nآپ سب کا بہت شکریہ!\nپاکستان زندہ باد! پائندہ باد!"""
                        elif "نظم" in content_type or "Poem" in content_type:
                            generated_text = f"""### عنوان: {topic_prompt}\n\nنکلتا ہے سورج سدا نور لے کر،\nنیا اک اجالا ہے ہر طور لے کر۔\nبڑھو آگے بچوں یہی ہے نشانی،\nسنو تم ہمیشہ یہ پیاری کہانی۔\n\n{topic_prompt} کی راہوں پہ چل کر دکھاؤ،\nوطن کا پرچم ہمیشہ اٹھاؤ!\n\nمحنت ہی سے ملتی ہے ہر اک خوشی یہاں،\nبنے گا میرا دیس سارا جہاں!\n\nقلم کی طاقت سے دنیا بدل دو،\nہر اک غم کو دل سے اپنے نکال دو۔\nچلو اب یہ مل کر ارادہ کریں ہم،\nوطن کے لیے جینا مرنا قسم!\n\nبلندی کے ہر بام کو چھو لیں گے ہم،\nنیا اک نیا آسمان ہو گا قدم!\nستارے بھی جس کی گواہی دیں گے،\nوہ سندر زمانہ ہمارا بنے گا!"""
                        else:
                            generated_text = f"""### تفصیلی نوٹ / سرکولر: {topic_prompt}\n\n**مقام:** دارالخدیجہ سکول سسٹم، سلانوالی\n\n**تعارف:**\nتمام والدین، اساتذہ اور طلباء کی توجہ کے لیے یہ اہم نوٹ جاری کیا جا رہا ہے جس کا بنیادی مقصد **{topic_prompt}** کے حوالے سے بہترین انتظامات کرنا اور شعور اجاگر کرنا ہے۔\n\n**تفصیلی ہدایات:**\n1. اسکول میں اس سلسلے میں خصوصی سیشنز اور مقابلے منعقد کیے جائیں گے۔\n2. تمام طلباء سے گزارش ہے کہ وہ اس میں بھرپور حصہ لیں اور اپنی صلاحیتوں کا لوہا منوائیں۔\n3. اساتذہ کرام اس بات کو یقینی بنائیں گے کہ ہر طالبعلم اس عمل میں شامل ہو اور اس کے مثبت نتائج سامنے آئیں۔\n\n**اختتامی کلمات:**\nآپ کا تعاون ہمارے لیے ہمیشہ باعثِ فخر رہا ہے۔ امید ہے کہ ہم سب مل کر اسکول کا نام مزید روشن کریں گے۔"""
                    else:
                        generated_text = f"""### Title: {topic_prompt}\n\n**1. Introduction:**\nIn the contemporary era, the significance of {topic_prompt} holds profound importance. It serves as a foundational pillar upon which successful academic and personal milestones are achieved. History consistently demonstrates that societies prioritizing this core value thrive exceptionally.\n\n**2. Key Significance and Impact:**\nA deeper analysis reveals that {topic_prompt} fosters discipline, critical thinking, and unwavering dedication. For students, mastering this concept opens doors to limitless opportunities and prepares them to tackle future challenges with confidence and resilience.\n\n**3. Role of Educational Institutions:**\nSchools play an indispensable role in shaping character. Institutions like Dar-ul-Khadija School System continuously strive to instill these noble qualities through structured activities, moral mentoring, and academic excellence.\n\n**4. Conclusion:**\nIn conclusion, embracing {topic_prompt} is not merely an option but a necessity. By committing to these principles today, we pave the way for a brighter, more prosperous, and successful tomorrow for our students and our beloved nation."""

                    st.success(tr("تفصیلی مواد کامیابی سے تیار ہو گیا!", "Detailed Content Generated Successfully!"))
                    st.write("---")
                    st.markdown(generated_text)
                    st.write("---")
                    st.download_button(
                        label=tr("📥 تفصیلی ٹیکسٹ فائل ڈاؤن لوڈ کریں", "📥 Download Detailed Text File"),
                        data=generated_text,
                        file_name=f"Detailed_School_Content.txt",
                        mime="text/plain"
                    )
                        
                except Exception as e:
                    st.error(f"{tr('مواد تیار کرنے میں خرابی آئی:', 'Error generating content:')} {e}")

# ================= 17. پاسورڈ تبدیل (Change Password) =================
elif core_choice in ["پاسورڈ تبدیل", "Change Password"]:
    st.markdown(f"<h2 class='no-print'>🔑 {tr('سسٹم کا پاسورڈ تبدیل کریں', 'Change System Password')}</h2>", unsafe_allow_html=True)
    st.markdown("<div class='no-print'>", unsafe_allow_html=True)
    with st.form("change_pass_form"):
        old_pass = st.text_input(tr("پرانا پاسورڈ", "Old Password"), type="password")
        new_pass = st.text_input(tr("نیا پاسورڈ", "New Password"), type="password")
        confirm_pass = st.text_input(tr("نئے پاسورڈ کی تصدیق", "Confirm Password"), type="password")
        if st.form_submit_button(tr("پاسورڈ تبدیل کریں", "Change Password")):
            cursor.execute("SELECT value FROM settings WHERE key='password'")
            row = cursor.fetchone()
            current_saved_pass = row[0] if row else "1234"
            if old_pass == current_saved_pass:
                if new_pass == confirm_pass and new_pass != "":
                    cursor.execute(f"UPDATE settings SET value='{new_pass}' WHERE key='password'")
                    conn.commit()
                    st.success(tr("پاسورڈ کامیابی سے تبدیل ہو گیا!", "Password changed successfully!"))
                else: st.error(tr("نئے پاسورڈ آپس میں نہیں ملتے یا خانے خالی ہیں۔", "New passwords do not match or are empty."))
            else: st.error(tr("پرانا پاسورڈ غلط ہے۔", "Incorrect old password."))
    st.markdown("</div>", unsafe_allow_html=True)
