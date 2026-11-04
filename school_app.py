import streamlit as st
import streamlit.components.v1 as components
import google.generativeai as genai
import pandas as pd
import datetime
import sqlite3
import base64
import os
import io
import shutil
import urllib.parse
import time
import random
import webbrowser

# پیج کی سیٹنگز سب سے اوپر ہونی چاہئیں
st.set_page_config(page_title="Dar Ul Khadija School System", page_icon="🏫", layout="wide")

# ================= 1. یوزر انٹرفیس (UI) اور CSS کی سیٹنگز =================
st.markdown("""
<style>
/* مین پیج کی اوپر اور سائیڈوں والی فالتو سپیس ختم کرنے کے لیے */
.block-container {
    padding-top: 1rem !important;
    padding-left: 1.5rem !important;
    padding-right: 1.5rem !important;
    max-width: 100% !important;
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

/* ریڈیو بٹن کے گول دائرے کو مکمل غائب کرنا */
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

# ================= 2. زبان اور ترجمہ (Translation System) =================
if 'ui_lang' not in st.session_state:
    st.session_state.ui_lang = "English"

def tr(ur, en):
    return ur if st.session_state.ui_lang == "اردو" else en

def get_translations(lang):
    if lang == "اردو":
        return {
            "dir": "rtl", "align": "right", "logo_align": "right", "text_align_rev": "left",
            "font": "font-family: 'Jameel Noori Nastaleeq', 'Nafees Web Naskh', 'Arial', sans-serif;"
        }
    else:
        return {
            "dir": "ltr", "align": "left", "logo_align": "left", "text_align_rev": "right",
            "font": "font-family: 'Arial', sans-serif;"
        }

# ================= 3. ہیلپر فنکشنز (Helper Functions) =================
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

# ================= 4. ڈیٹا بیس اور کنکشن (Database Setup & Auto-Fixer) =================
SESSION_TRACKER_FILE = "active_session_db.txt"

def get_current_db_filename():
    if os.path.exists(SESSION_TRACKER_FILE):
        with open(SESSION_TRACKER_FILE, "r") as f:
            return f.read().strip()
    return 'school_data.db'

DB_FILE = get_current_db_filename()

@st.cache_resource
def get_db_connection():
    conn = sqlite3.connect('school_data.db', check_same_thread=False, timeout=30)
    conn.execute('PRAGMA journal_mode=WAL;')
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    # تمام بنیادی ٹیبلز بنانا
    cursor.execute('''CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT, blob_value BLOB)''')
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
    cursor.execute('''CREATE TABLE IF NOT EXISTS timetable (id INTEGER PRIMARY KEY AUTOINCREMENT, class TEXT, section TEXT, day TEXT, period TEXT, subject TEXT, teacher_id TEXT)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS lesson_plan (id INTEGER PRIMARY KEY AUTOINCREMENT, date TEXT, class TEXT, section TEXT, subject TEXT, teacher_id TEXT, topic TEXT, status TEXT, plan_type TEXT)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS exams (exam_name TEXT PRIMARY KEY, start_date TEXT)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS exam_marks (id INTEGER PRIMARY KEY AUTOINCREMENT, exam_name TEXT, reg_id TEXT, subject TEXT, total_marks REAL, obtained_marks REAL)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS notices (id INTEGER PRIMARY KEY AUTOINCREMENT, date TEXT, audience TEXT, title TEXT, details TEXT)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS transport (vehicle_id TEXT PRIMARY KEY, type TEXT, driver_name TEXT, driver_phone TEXT, route_name TEXT, fare REAL, gps_device_id TEXT)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS transport_members (reg_id TEXT PRIMARY KEY, vehicle_id TEXT)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS live_locations (device_id TEXT PRIMARY KEY, lat REAL, lon REAL, last_updated TEXT, speed REAL)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS inventory (id INTEGER PRIMARY KEY AUTOINCREMENT, item_name TEXT, category TEXT, total_qty INTEGER, used_qty INTEGER DEFAULT 0)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS complaints (id INTEGER PRIMARY KEY AUTOINCREMENT, date TEXT, sender_name TEXT, sender_type TEXT, reg_id TEXT, subject TEXT, details TEXT, status TEXT DEFAULT 'Pending', admin_reply TEXT)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS books (book_id TEXT PRIMARY KEY, title TEXT, author TEXT, category TEXT, total_qty INTEGER, available_qty INTEGER)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS book_issue (id INTEGER PRIMARY KEY AUTOINCREMENT, book_id TEXT, issued_to_type TEXT, reg_id TEXT, issue_date TEXT, due_date TEXT, return_date TEXT, status TEXT DEFAULT 'Issued', fine REAL DEFAULT 0)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS visitors (id INTEGER PRIMARY KEY AUTOINCREMENT, date TEXT, time_in TEXT, time_out TEXT, name TEXT, phone TEXT, purpose TEXT, to_meet TEXT, status TEXT DEFAULT 'Inside')''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS academic_sessions (session_name TEXT PRIMARY KEY, status TEXT)''')
    
    cursor.execute("SELECT COUNT(*) FROM academic_sessions")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO academic_sessions VALUES ('2026-27', 'ACTIVE')")
        
    # یوزرز اور لاگ ان کا ٹیبل
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT UNIQUE,
                        password TEXT,
                        role TEXT,
                        ref_id TEXT DEFAULT 'N/A'
                    )''')
    
    cursor.execute("SELECT COUNT(*) FROM users")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO users (username, password, role, ref_id) VALUES ('admin', 'admin123', 'Admin', 'N/A')")

    # 🟢 پروفیشنل مائیگریشن (Auto-Fixer): ایک ہی بار سارے
    # پہلے ڈیٹا بیس کنکشن کو یقینی بنائیں تاکہ cursor کا ایرر نہ آئے
    conn = init_db()
    cursor = conn.cursor()
    
# ================= 5. لاگ ان اور سیکیورٹی سسٹم (Login & Security System) =================
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'current_user' not in st.session_state:
    st.session_state.current_user = ""
if 'current_role' not in st.session_state:
    st.session_state.current_role = ""
if 'ref_id' not in st.session_state:
    st.session_state.ref_id = ""

def login_system():
    # 🟢 کریش پروف ویری ایبلز تاکہ کوئی NameError نہ آئے
    try:
        safe_logo = logo_src_b64
    except NameError:
        safe_logo = "https://cdn-icons-png.flaticon.com/512/104/104655.png"
        
    try:
        safe_name = school_name.upper()
    except NameError:
        safe_name = "DAR UL KHADIJA SCHOOL SYSTEM"
        
    try:
        safe_address = school_address
    except NameError:
        safe_address = "Aslamabad Colony, Sillanwali, Sargodha"

    # 🟢 لاگ ان پیج کا ڈیزائن (اس میں سے گول سرکل اور بارڈر ختم کر دیا گیا ہے)
    st.markdown(f"""
    <div style="text-align: center; margin-top: 50px; margin-bottom: 20px;">
        <img src="{safe_logo}" style="width: 140px; height: 140px; object-fit: contain; padding: 5px; background: white; box-shadow: 0 4px 10px rgba(0,0,0,0.1);">
        <h1 style="color: #1a4f8b; margin-top: 15px; font-family: 'Arial', sans-serif;">{safe_name}</h1>
        <p style="color: #666; font-size: 16px; margin-top: -10px; font-weight: bold;">{safe_address}</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1.2, 1])
    # ... (اس کے نیچے آپ کا لاگ ان فارم والا باقی کوڈ ویسے ہی رہے گا)
    with col2:
        st.markdown(f"<h3 style='text-align: center; color: #333; margin-bottom: 20px;'>🔐 {tr('سسٹم میں لاگ ان کریں', 'Login to System')}</h3>", unsafe_allow_html=True)
        with st.form("login_form"):
            username = st.text_input(tr("یوزر نیم (Username)", "Username"), placeholder="admin")
            password = st.text_input(tr("پاسورڈ (Password)", "Password"), type="password", placeholder="1234")
            login_btn = st.form_submit_button(tr("لاگ ان (Login)", "Login"), type="primary", use_container_width=True)
            
            if login_btn:
                # مین ایڈمن اکاؤنٹ چیک
                if username == "admin" and password == settings_data.get("password", "1234"):
                    st.session_state.logged_in = True
                    st.session_state.current_user = "Admin"
                    st.session_state.current_role = "Admin"
                    st.session_state.ref_id = "N/A"
                    st.rerun()
                else:
                    # دیگر یوزرز (اساتذہ، والدین، آپریٹرز) کی چیکنگ
                    cursor.execute("SELECT role, ref_id FROM users WHERE username=? AND password=?", (username, password))
                    user_data = cursor.fetchone()
                    
                    if user_data:
                        st.session_state.logged_in = True
                        st.session_state.current_user = username
                        st.session_state.current_role = user_data[0]
                        st.session_state.ref_id = user_data[1]
                        st.rerun()
                    else:
                        st.error(tr("❌ غلط یوزر نیم یا پاسورڈ۔ براہ کرم دوبارہ کوشش کریں۔", "❌ Incorrect username or password. Please try again."))

# اگر یوزر لاگ ان نہیں ہے تو سسٹم یہیں رک جائے گا (اس سے آگے کا کوڈ رن نہیں ہوگا)
if not st.session_state.logged_in:
 login_system()
st.stop()
# 🟢 ایکٹو سیشن معلوم کرنے کا فنکشن (یہاں رکھنے سے NameError کبھی نہیں آئے گا)
def get_active_session():
    try:
        local_conn = get_db_connection()
        local_cursor = local_conn.cursor()
        local_cursor.execute("SELECT session_name FROM academic_sessions WHERE status='ACTIVE'")
        row = local_cursor.fetchone()
        return row[0] if row else "2026-27"
    except:
        return "2026-27"
if login_btn:
                # 🟢 کریش پروف ایڈمن پاسورڈ چیک تاکہ NameError نہ آئے
                try:
                    admin_password = settings_data.get("password", "1234")
                except NameError:
                    admin_password = "1234" # ڈیفالٹ پاسورڈ
                    try:
                        # اگر settings_data نہ ملے تو ڈیٹا بیس سے ڈائریکٹ پاسورڈ نکال لے گا
                        local_conn = get_db_connection()
                        local_cursor = local_conn.cursor()
                        local_cursor.execute("SELECT value FROM settings WHERE key='password'")
                        row = local_cursor.fetchone()
                        if row:
                            admin_password = row[0]
                    except:
                        pass

                # مین ایڈمن اکاؤنٹ چیک
                if username == "admin" and password == admin_password:
                    st.session_state.logged_in = True
                    st.session_state.current_user = "Admin"
                    st.session_state.current_role = "Admin"
                    st.session_state.ref_id = "N/A"
                    st.rerun()
                else:
                    # 🟢 یوزر (Teacher یا Parent) چیک کرنے والا محفوظ کوڈ
                    try:
                        local_conn = get_db_connection()
                        local_cursor = local_conn.cursor()
                        local_cursor.execute("SELECT role, ref_id FROM users WHERE username=? AND password=?", (username, password))
                        user_data = local_cursor.fetchone()
                        
                        if user_data:
                            st.session_state.logged_in = True
                            st.session_state.current_user = username
                            st.session_state.current_role = user_data[0]
                            st.session_state.ref_id = user_data[1]
                            st.rerun()
                        else:
                            st.error(tr("❌ غلط یوزر نیم یا پاسورڈ۔ براہ کرم دوبارہ کوشش کریں۔", "❌ Incorrect username or password. Please try again."))
                    except Exception as e:
                        st.error(f"Database Error: {e}")
active_session = get_active_session()

    # ================= 6. مین مینو اور نیویگیشن (Sidebar & Navigation) =================
try:
        safe_logo = logo_src_b64
except NameError:
        safe_logo = "https://cdn-icons-png.flaticon.com/512/104/104655.png"

logo_base64_html = f'<img src="{safe_logo}" style="max-width: 80px; max-height: 80px; border: 2px solid #1a4f8b; background: white; padding: 3px;">'
with st.sidebar:
    st.markdown(f"""
    <div style='display: flex; align-items: center; gap: 10px; margin-bottom: 20px;'>
        {logo_base64_html}
        <div>
    try:
        safe_school_name = school_name.upper()
    except NameError:
        safe_school_name = "DAR UL KHADIJA SCHOOL SYSTEM"
            <p style='margin: 0; font-size: 11px; color: #777;'>School System</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    user_role = st.session_state.current_role
    
    # رول کے مطابق مینو آئٹمز دکھانا
    if user_role in ["Admin", "Operator"]:
        st.markdown(f"<div style='font-size:11px; font-weight:bold; color:#1a4f8b; margin-bottom: 5px;'>🟢 ADMIN WORKSPACE</div>", unsafe_allow_html=True)
        menu_options = [
            "Dashboard", "Parent Portal", "School Profile", "Students Mgt", "Staff Mgt", "Attendance", 
            "Fee & Salary", "Accounts", "Academics", "Library", "Inventory", "Gate Security", 
            "Transport", "Helpdesk", "Notice Board", "Performance", "Discipline & Merit", 
            "WhatsApp Alerts", "AI Generator", "Data Backup", "Change Password"
        ]
        menu_icons = ["📊", "👨‍👩‍👦", "🏫", "👨‍🎓", "👨‍🏫", "📋", "💵", "💲", "📚", "📖", "📦", "🛡️", "🚌", "🎧", "📢", "📈", "⭐", "📱", "🤖", "💾", "🔑"]
    elif user_role == "Teacher":
        st.markdown(f"<div style='font-size:11px; font-weight:bold; color:#e65100; margin-bottom: 5px;'>🟠 TEACHER WORKSPACE</div>", unsafe_allow_html=True)
        menu_options = ["Dashboard", "Parent Portal", "Students Mgt", "Attendance", "Academics", "Notice Board", "Helpdesk", "Change Password"]
        menu_icons = ["📊", "👨‍👩‍👦", "👨‍🎓", "📋", "📚", "📢", "🎧", "🔑"]
    else: # Guardian (والدین)
        st.markdown(f"<div style='font-size:11px; font-weight:bold; color:#2e7d32; margin-bottom: 5px;'>🟢 GUARDIAN WORKSPACE</div>", unsafe_allow_html=True)
        menu_options = ["Parent Portal", "Notice Board", "Change Password"]
        menu_icons = ["👨‍👩‍👦", "📢", "🔑"]
        
    display_options = []
    for i, opt in enumerate(menu_options):
        ur_text = {"Dashboard":"ڈیش بورڈ", "Parent Portal":"پیرنٹ پورٹل", "School Profile":"سکول پروفائل", "Students Mgt":"سٹوڈنٹ مینجمنٹ", "Staff Mgt":"سٹاف مینجمنٹ", "Attendance":"حاضری", "Fee & Salary":"فیس اور تنخواہ", "Accounts":"اکاؤنٹس (لیجر)", "Academics":"تعلیمی ریکارڈ", "Library":"لائبریری", "Inventory":"انوینٹری (سٹاک)", "Gate Security":"گیٹ سیکیورٹی", "Transport":"ٹرانسپورٹ (GPS)", "Helpdesk":"ہیلپ ڈیسک (شکایات)", "Notice Board":"نوٹس بورڈ", "Performance":"پرفارمنس", "Discipline & Merit":"ڈسپلن اور میرٹ", "WhatsApp Alerts":"واٹس ایپ نوٹیفیکیشن", "AI Generator":"اے آئی جنریٹر", "Data Backup":"ڈیٹا بیک اپ", "Change Password":"پاسورڈ تبدیل"}.get(opt, opt)
        display_options.append(f"{menu_icons[i]} {tr(ur_text, opt)}")
        
    st.markdown(f"<div style='font-size:10px; font-weight:bold; color:#999; margin-top: 15px; margin-bottom: 5px; text-transform: uppercase;'>WORKSPACE</div>", unsafe_allow_html=True)
    choice_disp = st.radio("Main Menu", display_options, label_visibility="collapsed")
    
    core_choice = menu_options[display_options.index(choice_disp)]
    
    st.markdown("<hr style='margin:10px 0;'>", unsafe_allow_html=True)
    
    sub_choice = None
    if core_choice == "Students Mgt" and user_role in ["Admin", "Operator"]:
        sub_options_ur = ["New Admission", "Edit Record", "Search", "Print Profile", "Certificates", "Bulk Import"]
        sub_disp = [tr({"New Admission":"نیا داخلہ", "Edit Record":"ریکارڈ ایڈٹ کریں", "Search":"تلاش (Search)", "Print Profile":"پروفائل پرنٹ کریں", "Certificates":"سرٹیفکیٹس اور لیٹر", "Bulk Import":"ایکسل سے امپورٹ"}.get(o,o), o) for o in sub_options_ur]
        sub_sel = st.radio("Student Menu", sub_disp, label_visibility="collapsed")
        sub_choice = sub_options_ur[sub_disp.index(sub_sel)]
        
    elif core_choice == "Students Mgt" and user_role == "Teacher":
        sub_choice = "Search"
        
    elif core_choice == "Staff Mgt":
        sub_options_ur = ["New Staff", "Edit/Search Staff", "Print ID Cards"]
        sub_disp = [tr({"New Staff":"نیا سٹاف", "Edit/Search Staff":"ریکارڈ / ایڈٹ", "Print ID Cards":"آئی ڈی کارڈز پرنٹ"}.get(o,o), o) for o in sub_options_ur]
        sub_sel = st.radio("Staff Menu", sub_disp, label_visibility="collapsed")
        sub_choice = sub_options_ur[sub_disp.index(sub_sel)]
        
    elif core_choice == "Attendance":
        sub_options_ur = ["Mark Attendance", "Today's Report", "Monthly Report"]
        sub_disp = [tr({"Mark Attendance":"حاضری لگائیں", "Today's Report":"آج کی رپورٹ", "Monthly Report":"ماہانہ رپورٹ"}.get(o,o), o) for o in sub_options_ur]
        sub_sel = st.radio("Attendance Menu", sub_disp, label_visibility="collapsed")
        sub_choice = sub_options_ur[sub_disp.index(sub_sel)]
        
    elif core_choice == "Fee & Salary":
        sub_options_ur = ["Collect Fee", "Fee Defaulters", "Pay Salary", "Print Slips"]
        sub_disp = [tr({"Collect Fee":"فیس وصول کریں", "Fee Defaulters":"فیس ڈیفالٹرز", "Pay Salary":"تنخواہ ادا کریں", "Print Slips":"سلپ پرنٹ کریں"}.get(o,o), o) for o in sub_options_ur]
        sub_sel = st.radio("Fee Menu", sub_disp, label_visibility="collapsed")
        sub_choice = sub_options_ur[sub_disp.index(sub_sel)]
        
    elif core_choice == "Accounts":
        sub_options_ur = ["New Transaction", "Cash Book / Ledger", "Account Heads"]
        sub_disp = [tr({"New Transaction":"نئی ٹرانزیکشن", "Cash Book / Ledger":"کیش بک / لیجر", "Account Heads":"اکاؤنٹ ہیڈز"}.get(o,o), o) for o in sub_options_ur]
        sub_sel = st.radio("Accounts Menu", sub_disp, label_visibility="collapsed")
        sub_choice = sub_options_ur[sub_disp.index(sub_sel)]
        
    elif core_choice == "Academics":
        sub_options_ur = ["Timetable", "Lesson Plan", "Exam Setup", "Marks Entry", "Result Cards"]
        sub_disp = [tr({"Timetable":"ٹائم ٹیبل", "Lesson Plan":"لیسن پلان", "Exam Setup":"امتحان کی سیٹنگ", "Marks Entry":"نمبرز کا اندراج", "Result Cards":"رزلٹ کارڈز"}.get(o,o), o) for o in sub_options_ur]
        sub_sel = st.radio("Academics Menu", sub_disp, label_visibility="collapsed")
        sub_choice = sub_options_ur[sub_disp.index(sub_sel)]
        
    elif core_choice == "Library":
        sub_options_ur = ["Manage Books", "Issue / Return Books", "Library Reports"]
        sub_disp = [tr({"Manage Books":"کتابوں کا ریکارڈ", "Issue / Return Books":"کتاب جاری / واپس کریں", "Library Reports":"لائبریری رپورٹس"}.get(o,o), o) for o in sub_options_ur]
        sub_sel = st.radio("Library Menu", sub_disp, label_visibility="collapsed")
        sub_choice = sub_options_ur[sub_disp.index(sub_sel)]
        
    elif core_choice == "Inventory":
        sub_options_ur = ["Add New Stock", "Stock Record"]
        sub_disp = [tr({"Add New Stock":"نیا سٹاک شامل کریں", "Stock Record":"سٹاک کا ریکارڈ"}.get(o,o), o) for o in sub_options_ur]
        sub_sel = st.radio("Inventory Menu", sub_disp, label_visibility="collapsed")
        sub_choice = sub_options_ur[sub_disp.index(sub_sel)]
        
    elif core_choice == "Gate Security":
        sub_options_ur = ["New Visitor (Entry)", "Active Visitors (Out)", "Visitor History"]
        sub_disp = [tr({"New Visitor (Entry)":"نیا وزیٹر (انٹری)", "Active Visitors (Out)":"موجودہ وزیٹرز (آؤٹ)", "Visitor History":"وزیٹر ہسٹری"}.get(o,o), o) for o in sub_options_ur]
        sub_sel = st.radio("Security Menu", sub_disp, label_visibility="collapsed")
        sub_choice = sub_options_ur[sub_disp.index(sub_sel)]
        
    elif core_choice == "Transport":
        sub_options_ur = ["Vehicles & Routes", "Student Booking", "Live GPS Map"]
        sub_disp = [tr({"Vehicles & Routes":"گاڑیاں اور روٹس", "Student Booking":"طلباء کی بکنگ", "Live GPS Map":"لائیو جی پی ایس (لائیو میپ)"}.get(o,o), o) for o in sub_options_ur]
        sub_sel = st.radio("Transport Menu", sub_disp, label_visibility="collapsed")
        sub_choice = sub_options_ur[sub_disp.index(sub_sel)]
        
    elif core_choice == "Notice Board" and user_role in ["Admin", "Operator"]:
        sub_options_ur = ["New Notice", "All Notices"]
        sub_disp = [tr({"New Notice":"نیا نوٹس", "All Notices":"تمام نوٹسز"}.get(o,o), o) for o in sub_options_ur]
        sub_sel = st.radio("Notice Menu", sub_disp, label_visibility="collapsed")
        sub_choice = sub_options_ur[sub_disp.index(sub_sel)]
        
    elif core_choice == "Performance":
        sub_options_ur = ["Student Performance", "Staff Performance", "Overall School Performance"]
        sub_disp = [tr({"Student Performance":"طالب علم کی کارکردگی", "Staff Performance":"سٹاف کی کارکردگی", "Overall School Performance":"مجموعی سکول پرفارمنس"}.get(o,o), o) for o in sub_options_ur]
        sub_sel = st.radio("Performance Menu", sub_disp, label_visibility="collapsed")
        sub_choice = sub_options_ur[sub_disp.index(sub_sel)]

    st.markdown("<hr style='margin:15px 0;'>", unsafe_allow_html=True)
    
    # سیشن اور زبان کی سیٹنگز
    st.markdown(f"<div style='font-size:9px; font-weight:bold; color:#999; text-transform:uppercase;'>ACTIVE SESSION</div>", unsafe_allow_html=True)
    st.markdown(f"<div style='font-size:13px; font-weight:bold; color:#1a4f8b; margin-bottom:15px;'>🗓️ {active_session}</div>", unsafe_allow_html=True)
    
    lang_sel = st.radio(f"🌐 LANGUAGE / زبان", ["English", "اردو"], index=0 if st.session_state.ui_lang=="English" else 1, horizontal=True)
    if lang_sel != st.session_state.ui_lang:
        st.session_state.ui_lang = lang_sel
        st.rerun()
        
    st.markdown("<hr style='margin:15px 0;'>", unsafe_allow_html=True)
    
    user_icon = "👨‍💼" if user_role == "Admin" else ("👨‍🏫" if user_role == "Teacher" else "👨‍👩‍👦")
    st.markdown(f"<div style='font-size:12px; font-weight:bold;'>{user_icon} {st.session_state.current_user}</div>", unsafe_allow_html=True)
    
    if st.button(tr("🚪 لاگ آؤٹ (Logout)", "🚪 Logout"), use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.current_user = ""
        st.session_state.current_role = ""
        st.session_state.ref_id = ""
        st.rerun()

# ================= 7. ڈیش بورڈ (Dashboard) =================
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

    col_welcome, col_alerts = st.columns([1.1, 2.9])

    with col_welcome:
        welcome_html = f"""
        <div style="background: linear-gradient(135deg, #e8f5e9 0%, #c8e6c9 100%); padding: 30px 20px; border-radius: 20px; border: 1px solid #a5d6a7; box-shadow: 0 6px 15px rgba(0,0,0,0.04); text-align: center; display: flex; flex-direction: column; align-items: center; justify-content: center; min-height: 280px; margin-bottom: 20px;">
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
        today_md = datetime.date.today().strftime("-%m-%d")
        
        # ڈیٹا بیس سے ریکارڈ نکالنا (اگر name_en کالم موجود ہو تو وہ بھی لے آئے)
        try:
            bday_students = pd.read_sql(f"SELECT name, name_en, class, section FROM students WHERE dob LIKE '%{today_md}' AND status='Active'", conn)
        except:
            bday_students = pd.read_sql(f"SELECT name, class, section FROM students WHERE dob LIKE '%{today_md}' AND status='Active'", conn)
            
        try:
            bday_staff = pd.read_sql(f"SELECT name, name_en, designation FROM staff WHERE dob LIKE '%{today_md}'", conn)
        except:
            bday_staff = pd.read_sql(f"SELECT name, designation FROM staff WHERE dob LIKE '%{today_md}'", conn)
        
        if not bday_students.empty or not bday_staff.empty:
            bday_html = "<div style='background: linear-gradient(135deg, #ff9a9e 0%, #fecfef 99%, #fecfef 100%); padding: 15px; border-radius: 12px; border: 2px solid #ff758c; box-shadow: 0px 4px 6px rgba(0,0,0,0.1); margin-bottom: 15px; color: #d81b60;'>"
            
            # ٹائٹل زبان کے حساب سے
            bday_title = tr("🎂 آج ان کی سالگرہ ہے! (Happy Birthday)", "🎂 Happy Birthday! Today is their special day.")
            bday_html += f"<h4 style='margin:0 0 10px 0; display:flex; align-items:center; gap:8px;'>{bday_title}</h4><ul style='margin:0; padding-left:20px; font-size:14px; font-weight:bold;'>"
            
            for _, r in bday_students.iterrows():
                # اگر انگلش نام موجود ہے اور انگلش زبان منتخب ہے
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
            st.balloons() # سکرین پر غبارے اڑیں گے
            
        # فیس ڈیفالٹرز کا بلنکر الرٹ
        defaulters_html = ""
        try:
            today_str = datetime.date.today().strftime("%Y-%m-%d")
            cursor.execute("SELECT COUNT(DISTINCT reg_id) FROM fees WHERE status='Unpaid' AND due_date < ?", (today_str,))
            defaulters_count = cursor.fetchone()[0]
            
            if defaulters_count > 0:
                # زبان کے حساب سے بلنکنگ میسج
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
            
        # سکول انفو کارڈ
        st.markdown(f"""
        <div style="background-color: #ffffff; padding: 25px; border-radius: 20px; border: 1px solid #edf2f7; box-shadow: 0 4px 6px rgba(0,0,0,0.02); display: flex; flex-direction: column; justify-content: center; height: { '190px' if defaulters_html else '100%' };">
            <h4 style="margin: 0 0 15px 0; color: #2d3748; font-weight:800; display:flex; align-items:center; gap:8px;">🏫 School Information</h4>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 12px; font-size: 13px; color: #4a5568;">
                <div><span style="color:#3182ce; font-weight:bold;">📍 Address:</span> <span dir="ltr">{school_address}</span></div>
                <div><span style="color:#38a169; font-weight:bold;">📞 Phone:</span> <span dir="ltr">{school_phone}</span></div>
                <div><span style="color:#d69e2e; font-weight:bold;">📝 Reg No:</span> <span dir="ltr">{school_reg}</span></div>
                <div><span style="color:#e53e3e; font-weight:bold;">📧 Email:</span> <span dir="ltr">{school_email}</span></div>
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
        
    # بلکل درست کیلکولیشن (سنٹیکس ایرر حل ہو گیا ہے)
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

# ================= 8. سکول پروفائل =================
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


# ================= 9. کلاسز لسٹ اور کامن ڈیٹا (Classes List) =================
try:
    classes_df = pd.read_sql("SELECT class_name FROM sys_classes ORDER BY id", conn)
    classes_list = classes_df['class_name'].tolist()
    if not classes_list:
        classes_list = ["Playgroup", "Nursery", "Prep", "1st", "2nd", "3rd", "4th", "5th", "6th", "7th", "8th", "9th", "10th"]
except:
    classes_list = ["Playgroup", "Nursery", "Prep", "1st", "2nd", "3rd", "4th", "5th", "6th", "7th", "8th", "9th", "10th"]
    
    # ================= 10. ڈیش بورڈ (Dashboard) =================
if core_choice in ["ڈیش بورڈ", "Dashboard"]:
    if st.session_state.current_role not in ["Admin", "Operator", "Teacher"]:
        st.warning(tr("آپ کو یہ صفحہ دیکھنے کی اجازت نہیں ہے۔", "You don't have permission to view this page."))
        st.stop()
        
    st.markdown(f"<h2 class='no-print'>📊 {tr('ڈیش بورڈ (Dashboard)', 'Dashboard')}</h2>", unsafe_allow_html=True)
    
    hour = datetime.datetime.now().hour
    if hour < 12: greeting_msg = "Good Morning!"
    elif hour < 17: greeting_msg = "Good Afternoon!"
    else: greeting_msg = "Good Evening!"

    col_welcome, col_alerts = st.columns([1.1, 2.9])

    with col_welcome:
        welcome_html = f"""
        <div style="background: linear-gradient(135deg, #e8f5e9 0%, #c8e6c9 100%); padding: 30px 20px; border-radius: 20px; border: 1px solid #a5d6a7; box-shadow: 0 6px 15px rgba(0,0,0,0.04); text-align: center; display: flex; flex-direction: column; align-items: center; justify-content: center; min-height: 280px; margin-bottom: 20px;">
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
        # 🟢 برتھ ڈے الرٹ (Birthday Alerts)
        today_md = datetime.date.today().strftime("-%m-%d")
        
        try:
            bday_students = pd.read_sql(f"SELECT name, name_en, class, section FROM students WHERE dob LIKE '%{today_md}' AND status='Active'", conn)
        except:
            bday_students = pd.DataFrame()
            
        try:
            bday_staff = pd.read_sql(f"SELECT name, name_en, designation FROM staff WHERE dob LIKE '%{today_md}'", conn)
        except:
            bday_staff = pd.DataFrame()
        
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
            
        defaulters_html = ""
        try:
            today_str = datetime.date.today().strftime("%Y-%m-%d")
            cursor.execute("SELECT COUNT(DISTINCT reg_id) FROM fees WHERE status='Unpaid' AND due_date < ?", (today_str,))
            defaulters_count = cursor.fetchone()[0]
            
            if defaulters_count > 0 and st.session_state.current_role in ["Admin", "Operator"]:
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
                <div class="blink_text">{alert_text}</div>
                """
        except: pass
            
        if defaulters_html:
            st.markdown(defaulters_html, unsafe_allow_html=True)
            
        st.markdown(f"""
        <div style="background-color: #ffffff; padding: 25px; border-radius: 20px; border: 1px solid #edf2f7; box-shadow: 0 4px 6px rgba(0,0,0,0.02); display: flex; flex-direction: column; justify-content: center; height: { '190px' if defaulters_html else '100%' };">
            <h4 style="margin: 0 0 15px 0; color: #2d3748; font-weight:800; display:flex; align-items:center; gap:8px;">🏫 School Information</h4>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 12px; font-size: 13px; color: #4a5568;">
                <div><span style="color:#3182ce; font-weight:bold;">📍 Address:</span> <span dir="ltr">{school_address}</span></div>
                <div><span style="color:#38a169; font-weight:bold;">📞 Phone:</span> <span dir="ltr">{school_phone}</span></div>
                <div><span style="color:#d69e2e; font-weight:bold;">📝 Reg No:</span> <span dir="ltr">{school_reg}</span></div>
                <div><span style="color:#e53e3e; font-weight:bold;">📧 Email:</span> <span dir="ltr">{school_email}</span></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    if st.session_state.current_role in ["Admin", "Operator"]:
        # 🟢 ڈیٹا بیس کا نیا کنکشن تاکہ کریش نہ ہو
        conn = get_db_connection()
        
        total_students = pd.read_sql("SELECT COUNT(*) FROM students WHERE status='Active'", conn).iloc[0,0]
        total_staff = pd.read_sql("SELECT COUNT(*) FROM staff", conn).iloc[0,0]
        
        c1, c2, c3 = st.columns(3)
        c1.markdown(f"<div style='background:linear-gradient(135deg, #1a4f8b, #2b6cb0); color:white; padding:20px; border-radius:15px; text-align:center;'><h3>👨‍🎓 {tr('کل طلباء', 'Total Students')}</h3><h1>{total_students}</h1></div>", unsafe_allow_html=True)
        c2.markdown(f"<div style='background:linear-gradient(135deg, #38a169, #48bb78); color:white; padding:20px; border-radius:15px; text-align:center;'><h3>👨‍🏫 {tr('کل سٹاف', 'Total Staff')}</h3><h1>{total_staff}</h1></div>", unsafe_allow_html=True)
        
        try:
            today_att = pd.read_sql(f"SELECT COUNT(*) FROM attendance WHERE date='{today_date}' AND type='Student'", conn).iloc[0,0]
            if total_students > 0: att_percent = round((today_att / total_students) * 100)
            else: att_percent = 0
            c3.markdown(f"<div style='background:linear-gradient(135deg, #d69e2e, #ecc94b); color:white; padding:20px; border-radius:15px; text-align:center;'><h3>📋 {tr('آج کی حاضری', 'Today Attendance')}</h3><h1>{att_percent}%</h1></div>", unsafe_allow_html=True)
        except:
            c3.markdown(f"<div style='background:linear-gradient(135deg, #d69e2e, #ecc94b); color:white; padding:20px; border-radius:15px; text-align:center;'><h3>📋 {tr('آج کی حاضری', 'Today Attendance')}</h3><h1>0%</h1></div>", unsafe_allow_html=True)
            
# ================= 11. طلباء کا ریکارڈ (Students Management) =================
elif core_choice in ["سٹوڈنٹ مینجمنٹ", "Students Mgt"]:
    st.markdown(f"<h2 class='no-print'>👨‍🎓 {tr('طلباء کا ریکارڈ (Students Mgt)', 'Students Management')} - {sub_choice}</h2>", unsafe_allow_html=True)

    if sub_choice in ["نیا داخلہ", "New Admission"]:
        with st.form("student_form", clear_on_submit=False):
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
            fixed_fee = c17.number_input(tr("مقررہ ماہانہ فیس", "Monthly Fee"), min_value=0)
            initial_arrears = c18.number_input(tr("سابقہ بقایا جات", "Previous Arrears"), min_value=0, value=0)
            admission_date = c19.date_input(tr("تاریخِ داخلہ", "Admission Date"), max_value=datetime.date.today())
            medical_info = c20.text_input(tr("کوئی میڈیکل پیچیدگی؟", "Any Medical Issue?"))
            
            st.markdown(f"#### 🔒 {tr('والدین کا پورٹل لاگ ان (Parent Portal Login)', 'Parent Portal Login')}")
            st.info(tr("اگر آپ ابھی اکاؤنٹ نہیں بنانا چاہتے تو ان خانوں کو خالی چھوڑ دیں، آپ بعد میں 'ایڈٹ ریکارڈ' سے بھی اکاؤنٹ بنا سکتے ہیں۔", "Leave empty if you don't want to create an account now. You can create it later from Edit Record."))
            
            c_log1, c_log2 = st.columns(2)
            guardian_username = c_log1.text_input(tr("یوزر نیم (اختیاری)", "Username (Optional)"))
            guardian_password = c_log2.text_input(tr("پاسورڈ (اختیاری)", "Password (Optional)"))
            
            submit_btn = st.form_submit_button(tr("طالب علم کا ڈیٹا محفوظ کریں", "Save Student Data"), type="primary")
            
            if submit_btn:
                if not name.strip():
                    st.error(tr("⚠️ طالب علم کا نام لکھنا لازمی ہے۔", "⚠️ Student name is mandatory."))
                else:
                    try: photo_data = student_photo.read() if student_photo else None
                    except: photo_data = None
                        
                    n_en = name if st.session_state.ui_lang == "English" else ""
                    fn_en = father_name if st.session_state.ui_lang == "English" else ""
                    ad_en = address if st.session_state.ui_lang == "English" else ""
                    
                    try:
                        # 🟢 نیا یوزر بنانے اور اس کو ref_id سے پکا لنک کرنے کا کوڈ
                        if guardian_username.strip():
                            cursor.execute("SELECT id FROM users WHERE username=?", (guardian_username.strip(),))
                            if cursor.fetchone():
                                st.error(tr("⚠️ یہ یوزر نیم پہلے سے موجود ہے۔ برائے مہربانی کوئی مختلف نام استعمال کریں یا اسے خالی چھوڑ دیں۔", "Username already exists. Use a different one or leave empty."))
                                st.stop()
                            else:
                                pass_to_save = guardian_password.strip() if guardian_password.strip() else "1234"
                                cursor.execute("INSERT INTO users (username, password, role, ref_id) VALUES (?, ?, 'Guardian', ?)", 
                                               (guardian_username.strip(), pass_to_save, auto_reg_no))
                        
                        cursor.execute("""
                            INSERT INTO students 
                            (reg_id, name, fname, dob, blood, class, section, bform, phone, address, prev_school, prev_class, medical, monthly_fee, adm_date, arrears, gender, mname, fcnic, mcnic, photo, g_type, f_prof, name_en, fname_en, address_en, status) 
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'Active')
                        """, (auto_reg_no, name, father_name, student_dob.strftime("%Y-%m-%d"), blood_group, student_class, student_section, b_form, phone, address, prev_school, prev_class, medical_info, fixed_fee, admission_date.strftime("%Y-%m-%d"), initial_arrears, gender, mname, fcnic, mcnic, photo_data, g_type, f_prof, n_en, fn_en, ad_en))
                        
                        conn.commit()
                        st.balloons()
                        
                        if guardian_username.strip():
                            st.success(tr(f"✅ طالب علم ({name}) کا داخلہ اور والدین کا اکاؤنٹ کامیابی سے محفوظ ہو گیا!", "Student and parent account saved successfully!"))
                        else:
                            st.success(tr(f"✅ طالب علم ({name}) کا داخلہ محفوظ ہو گیا! (کوئی اکاؤنٹ نہیں بنایا گیا)", "Student record saved! (No account created)"))
                        
                        time.sleep(1.5)
                        st.rerun()
                            
                    except Exception as e:
                        st.error(f"⚠️ ایک نیا مسئلہ پیش آیا: {e}")
elif sub_choice in ["ریکارڈ ایڈٹ کریں", "Edit Record"]:
        st.markdown(f"### ✏️ {tr('طالب علم کا ریکارڈ ایڈٹ کریں', 'Edit Student Record')}")
        edit_reg = st.text_input(tr("رجسٹریشن نمبر لکھیں (مثلاً: 1001)", "Enter Registration No to Edit"))
        
        if edit_reg:
            stu_match = pd.read_sql(f"SELECT * FROM students WHERE reg_id='{edit_reg}'", conn)
            if not stu_match.empty:
                stu_data = stu_match.iloc[0]
                
                # 🟢 اکاؤنٹ فائنڈر (Updated Smart Finder)
                phone_val = str(stu_data.get('phone', '')).strip()
                parent_user = f"parent_{edit_reg}"
                
                cursor.execute("SELECT username, password FROM users WHERE ref_id=? OR username=? OR (username=? AND username!='') LIMIT 1", (edit_reg, parent_user, phone_val))
                user_row = cursor.fetchone()
                
                if user_row:
                    def_u, def_p = user_row[0], user_row[1]
                    acc_status = "<span style='color: green;'>✅ (پہلے سے اکاؤنٹ موجود ہے)</span>"
                else:
                    def_u, def_p = "", "" 
                    acc_status = "<span style='color: #d69e2e;'>⚠️ (کوئی اکاؤنٹ نہیں، نیا بنا سکتے ہیں)</span>"

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
                    
                    st.markdown(f"#### 🔒 {tr('والدین کا پورٹل لاگ ان', 'Parent Portal Login')} {acc_status}", unsafe_allow_html=True)
                    c_log1, c_log2 = st.columns(2)
                    e_username = c_log1.text_input(tr("یوزر نیم (Username)", "Username"), value=def_u)
                    e_password = c_log2.text_input(tr("پاسورڈ (Password)", "Password"), value=def_p)

                    c_act, c_spacer = st.columns([1, 4])
                    status_opts = ["Active", "Left", "Struck Off"]
                    e_status = c_act.selectbox(tr("موجودہ سٹیٹس", "Current Status"), status_opts, index=status_opts.index(stu_data.get("status", "Active") or "Active"))

                    if st.form_submit_button(tr("تبدیلیاں محفوظ کریں", "Save Changes"), type="primary"):
                        try:
                            if st.session_state.ui_lang == "اردو":
                                cursor.execute("""
                                    UPDATE students SET 
                                    name=?, gender=?, mname=?, fcnic=?, mcnic=?, class=?, section=?, 
                                    prev_school=?, prev_class=?, f_prof=?, phone=?, monthly_fee=?, arrears=?, 
                                    adm_date=?, blood=?, bform=?, g_type=?, dob=?, fname=?, address=?, status=?
                                    WHERE reg_id=?
                                """, (e_name, e_gender, e_mname, e_fcnic, e_mcnic, e_class, e_sec, e_prev_school, e_prev_class, e_fprof, e_phone, float(e_fee), float(e_arrears), e_adm_date.strftime("%Y-%m-%d"), e_blood_val, e_bform, e_g_type, e_dob.strftime("%Y-%m-%d"), e_fname, e_address, e_status, edit_reg))
                            else:
                                cursor.execute("""
                                    UPDATE students SET 
                                    name_en=?, gender=?, mname=?, fcnic=?, mcnic=?, class=?, section=?, 
                                    prev_school=?, prev_class=?, f_prof=?, phone=?, monthly_fee=?, arrears=?, 
                                    adm_date=?, blood=?, bform=?, g_type=?, dob=?, fname_en=?, address_en=?, status=?
                                    WHERE reg_id=?
                                """, (e_name, e_gender, e_mname, e_fcnic, e_mcnic, e_class, e_sec, e_prev_school, e_prev_class, e_fprof, e_phone, float(e_fee), float(e_arrears), e_adm_date.strftime("%Y-%m-%d"), e_blood_val, e_bform, e_g_type, e_dob.strftime("%Y-%m-%d"), e_fname, e_address, e_status, edit_reg))

                            # 🟢 سمارٹ اکاؤنٹ اپڈیٹ یا نیا اکاؤنٹ بنانا اور لنک کرنا
                            if e_username.strip():
                                cursor.execute("SELECT id FROM users WHERE username=?", (e_username.strip(),))
                                if cursor.fetchone():
                                    cursor.execute("UPDATE users SET password=?, role='Guardian', ref_id=? WHERE username=?", (e_password.strip(), edit_reg, e_username.strip()))
                                else:
                                    cursor.execute("INSERT INTO users (username, password, role, ref_id) VALUES (?, ?, 'Guardian', ?)", (e_username.strip(), e_password.strip(), edit_reg))
                            
                            conn.commit()
                            st.success(tr("✅ طالب علم کا ریکارڈ اور پورٹل اکاؤنٹ کامیابی سے اپڈیٹ ہو گئے۔", "Student record and portal account updated successfully!"))
                            time.sleep(1)
                            st.rerun()
                            
                        except Exception as db_err:
                            st.error(f"🛑 Error: {db_err}")
            else:
                st.warning(tr("اس رجسٹریشن نمبر کا کوئی ریکارڈ نہیں ملا۔", "No record found for this Registration No."))
elif sub_choice in ["تلاش (Search)", "Search"]:
        st.markdown(f"### 🔍 {tr('طلباء کو تلاش کریں', 'Search Students')}")
        c_s1, c_s2 = st.columns(2)
        search_by = c_s1.selectbox(tr("تلاش کا طریقہ", "Search By"), [tr("نام / فون نمبر", "Name / Phone"), tr("کلاس", "Class")])
        
        if search_by in ["نام / فون نمبر", "Name / Phone"]:
            search_query = c_s2.text_input(tr("نام، فون یا رجسٹریشن نمبر لکھیں", "Enter Name, Phone, or Reg No"))
            if search_query:
                try:
                    df = pd.read_sql(f"SELECT * FROM students WHERE name LIKE '%{search_query}%' OR name_en LIKE '%{search_query}%' OR phone LIKE '%{search_query}%' OR reg_id LIKE '%{search_query}%'", conn)
                    st.dataframe(df, use_container_width=True)
                except Exception as e:
                    st.error(f"Error: {e}")
        else:
            search_class = c_s2.selectbox(tr("کلاس منتخب کریں", "Select Class"), classes_list)
            if search_class:
                df = pd.read_sql(f"SELECT * FROM students WHERE class='{search_class}' AND status='Active'", conn)
                st.dataframe(df, use_container_width=True)

elif sub_choice in ["پروفائل پرنٹ کریں", "Print Profile"]:
        st.markdown(f"### 🖨️ {tr('طالب علم کی پروفائل پرنٹ کریں', 'Print Student Profile')}")
        p_reg = st.text_input(tr("رجسٹریشن نمبر لکھیں", "Enter Registration No for Profile"))
        if p_reg:
            df_p = pd.read_sql(f"SELECT * FROM students WHERE reg_id='{p_reg}'", conn)
            if not df_p.empty:
                r = df_p.iloc[0]
                n_val = get_disp_val(r.get('name'), r.get('name_en'))
                fn_val = get_disp_val(r.get('fname'), r.get('fname_en'))
                ad_val = get_disp_val(r.get('address'), r.get('address_en'))
                
                # پروفائل پرنٹنگ کا HTML ڈیزائن
                html_profile = f"""
                <div style="border: 3px solid #1a4f8b; padding: 20px; border-radius: 10px; max-width: 800px; margin: auto;">
                    <div style="text-align: center; border-bottom: 2px solid #1a4f8b; padding-bottom: 10px; margin-bottom: 20px;">
                        <img src="{logo_src_b64}" style="width: 80px; height: 80px; border-radius: 50%;">
                        <h2 style="color: #1a4f8b; margin: 5px 0;">{school_name.upper()}</h2>
                        <p style="margin: 0; font-size: 14px; color: #555;">{school_address}</p>
                        <h3 style="background: #1a4f8b; color: white; display: inline-block; padding: 5px 20px; border-radius: 20px; margin-top: 10px;">STUDENT PROFILE</h3>
                    </div>
                    <table style="width: 100%; font-size: 16px; line-height: 2;">
                        <tr><td style="font-weight: bold; width: 30%;">Registration No:</td><td>{r.get('reg_id')}</td></tr>
                        <tr><td style="font-weight: bold;">Student Name:</td><td>{n_val}</td></tr>
                        <tr><td style="font-weight: bold;">{get_relation_card_label(r.get('gender', 'Boy'), r.get('g_type', 'Father'))} Name:</td><td>{fn_val}</td></tr>
                        <tr><td style="font-weight: bold;">Class & Section:</td><td>{r.get('class')} - {r.get('section', 'A')}</td></tr>
                        <tr><td style="font-weight: bold;">Date of Birth:</td><td>{r.get('dob')}</td></tr>
                        <tr><td style="font-weight: bold;">Phone No:</td><td>{r.get('phone')}</td></tr>
                        <tr><td style="font-weight: bold;">Address:</td><td>{ad_val}</td></tr>
                        <tr><td style="font-weight: bold;">Status:</td><td>{r.get('status', 'Active')}</td></tr>
                    </table>
                </div>
                """
                st.components.v1.html(html_profile, height=500, scrolling=True)
                print_button_js(html_profile, tr("پروفائل پرنٹ کریں", "Print Profile"))
            else:
                st.warning(tr("اس رجسٹریشن نمبر کا کوئی ریکارڈ نہیں ملا۔", "No record found."))

elif sub_choice in ["سرٹیفکیٹس اور لیٹر", "Certificates"]:
        st.markdown(f"### 📜 {tr('سرٹیفکیٹس اور لیٹرز', 'Certificates & Letters')}")
        c_reg = st.text_input(tr("رجسٹریشن نمبر لکھیں", "Enter Registration No for Certificate"))
        c_type = st.selectbox(tr("سرٹیفکیٹ کی قسم", "Certificate Type"), ["School Leaving Certificate", "Character Certificate", "Fee Clearance Letter"])
        
        if c_reg:
            df_c = pd.read_sql(f"SELECT * FROM students WHERE reg_id='{c_reg}'", conn)
            if not df_c.empty:
                r = df_c.iloc[0]
                n_val = get_disp_val(r.get('name'), r.get('name_en'))
                fn_val = get_disp_val(r.get('fname'), r.get('fname_en'))
                
                content = f"This is to certify that <b>{n_val}</b> {get_relation_card_label(r.get('gender'), r.get('g_type'))} <b>{fn_val}</b> is/was a bonafide student of this school in Class {r.get('class')}."
                
                if c_type == "School Leaving Certificate":
                    content += " The student has paid all dues and is leaving the school with our best wishes."
                elif c_type == "Character Certificate":
                    content += " The student bears a good moral character and conduct."
                else:
                    content += " All outstanding fees have been cleared by the student up to date."
                
                html_cert = f"""
                <div style="border: 10px solid #1a4f8b; padding: 40px; margin: auto; max-width: 800px; text-align: center; position: relative; background: #fdfbf7;">
                    <img src="{logo_src_b64}" style="width: 100px; height: 100px; border-radius: 50%;">
                    <h1 style="color: #1a4f8b; margin-top: 10px; font-family: 'Times New Roman', serif;">{school_name.upper()}</h1>
                    <p style="font-size: 16px;">{school_address}</p>
                    <hr style="border: 1px solid #1a4f8b;">
                    <h2 style="font-family: 'Times New Roman', serif; margin: 30px 0; text-decoration: underline;">{c_type.upper()}</h2>
                    <p style="font-size: 20px; line-height: 2; text-align: justify; text-align-last: center; margin-bottom: 50px;">{content}</p>
                    <div style="display: flex; justify-content: space-between; margin-top: 50px;">
                        <div style="text-align: left;"><p>__________________</p><p><b>Date:</b> {today_date}</p></div>
                        <div style="text-align: right;"><p>__________________</p><p><b>Principal Signature</b></p></div>
                    </div>
                </div>
                """
                st.components.v1.html(html_cert, height=600, scrolling=True)
                print_button_js(html_cert, tr("سرٹیفکیٹ پرنٹ کریں", "Print Certificate"), landscape=True)
            else:
                st.warning(tr("اس رجسٹریشن نمبر کا کوئی ریکارڈ نہیں ملا۔", "No record found."))

elif sub_choice in ["ایکسل سے امپورٹ", "Bulk Import"]:
        st.markdown(f"### 📥 {tr('ایکسل سے طلباء کا ڈیٹا امپورٹ کریں', 'Bulk Import Students from Excel')}")
        st.info(tr("نوٹ: ایکسل فائل میں کالمز کے نام یہ ہونے چاہئیں: Name, FatherName, Class, Phone, Address", "Note: Excel file must contain these columns: Name, FatherName, Class, Phone, Address"))
        
        uploaded_file = st.file_uploader(tr("ایکسل فائل چنیں (.xlsx یا .csv)", "Upload Excel/CSV File"), type=['xlsx', 'csv'])
        if uploaded_file:
            try:
                if uploaded_file.name.endswith('.csv'): df_import = pd.read_csv(uploaded_file)
                else: df_import = pd.read_excel(uploaded_file)
                
                st.dataframe(df_import.head())
                if st.button(tr("ڈیٹا بیس میں محفوظ کریں", "Save to Database"), type="primary"):
                    stud_count = pd.read_sql("SELECT COUNT(*) FROM students", conn).iloc[0, 0]
                    start_reg = 1001 if stud_count == 0 else safe_int(pd.read_sql("SELECT MAX(CAST(reg_id AS INTEGER)) FROM students", conn).iloc[0, 0]) + 1
                    
                    success_count = 0
                    for index, row in df_import.iterrows():
                        try:
                            n_val = str(row.get('Name', 'Unknown'))
                            f_val = str(row.get('FatherName', ''))
                            c_val = str(row.get('Class', '1st'))
                            p_val = str(row.get('Phone', ''))
                            a_val = str(row.get('Address', ''))
                            
                            n_en = n_val if st.session_state.ui_lang == "English" else ""
                            f_en = f_val if st.session_state.ui_lang == "English" else ""
                            a_en = a_val if st.session_state.ui_lang == "English" else ""
                            
                            cursor.execute("""
                            INSERT INTO students (reg_id, name, fname, class, phone, address, name_en, fname_en, address_en, status, gender, g_type) 
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'Active', 'Boy', 'Father')
                            """, (str(start_reg), n_val, f_val, c_val, p_val, a_val, n_en, f_en, a_en))
                            
                            start_reg += 1
                            success_count += 1
                        except: pass
                    
                    conn.commit()
                    st.success(f"✅ {success_count} {tr('طلباء کا ڈیٹا کامیابی سے امپورٹ ہو گیا!', 'students imported successfully!')}")
            except Exception as e:
                st.error(f"Error: {e}")
            
# ================= 11.5. سٹاف کا ریکارڈ (Staff Management) =================
elif core_choice in ["سٹاف مینجمنٹ", "Staff Mgt"]:
    st.markdown(f"<h2 class='no-print'>👨‍🏫 {tr('سٹاف کا ریکارڈ (Staff Mgt)', 'Staff Management')} - {sub_choice}</h2>", unsafe_allow_html=True)
    
    if sub_choice in ["نیا سٹاف", "New Staff"]:
        with st.form("staff_form", clear_on_submit=False):
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
            st.info(tr("اگر آپ ابھی اکاؤنٹ نہیں بنانا چاہتے تو ان خانوں کو خالی چھوڑ دیں، آپ بعد میں 'ایڈٹ ریکارڈ' سے بھی اکاؤنٹ بنا سکتے ہیں۔", "Leave empty if you don't want to create an account now. You can create it later from Edit Record."))
            c_log1, c_log2, c_log3 = st.columns(3)
            staff_username = c_log1.text_input(tr("یوزر نیم (اختیاری)", "Username (Optional)"))
            staff_password = c_log2.text_input(tr("پاسورڈ (اختیاری)", "Password (Optional)"))
            staff_role = c_log3.selectbox(tr("سسٹم رول (Role)", "System Role"), ["Teacher", "Operator", "Admin"])

            submit_btn = st.form_submit_button(tr("سٹاف کا ڈیٹا محفوظ کریں", "Save Staff Data"), type="primary")
            
            if submit_btn:
                if not staff_name.strip():
                    st.error(tr("⚠️ سٹاف کا نام لکھنا لازمی ہے!", "⚠️ Staff name is required!"))
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
                    
                    try:
                        photo_data = staff_photo.read() if staff_photo else None
                    except:
                        photo_data = None
                        
                    n_en = staff_name if st.session_state.ui_lang == "English" else ""
                    fn_en = father_husband_name if st.session_state.ui_lang == "English" else ""
                    ad_en = address if st.session_state.ui_lang == "English" else ""
                    
                    try:
                        # 🟢 سٹاف کے نئے اکاؤنٹ کو ref_id کے ذریعے پکا لنک کرنا
                        if staff_username.strip():
                            cursor.execute("SELECT id FROM users WHERE username=?", (staff_username.strip(),))
                            if cursor.fetchone():
                                st.error(tr("⚠️ یہ یوزر نیم پہلے سے موجود ہے۔ برائے مہربانی لاگ ان کے لیے کوئی مختلف نام منتخب کریں یا اسے خالی چھوڑ دیں۔", "Username already exists. Please choose a different one or leave empty."))
                                st.stop()
                            else:
                                pass_to_save = staff_password.strip() if staff_password.strip() else "1234"
                                cursor.execute("INSERT INTO users (username, password, role, ref_id) VALUES (?, ?, ?, ?)", 
                                               (staff_username.strip(), pass_to_save, staff_role, auto_staff_id))
                        
                        cursor.execute("""
                            INSERT INTO staff 
                            (staff_id, name, fname, cnic, dob, designation, phone, address, joining_date, salary, education, fh_cnic, photo, g_type, name_en, fname_en, address_en, gender, assigned_class, assigned_sec) 
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, (auto_staff_id, staff_name, father_husband_name, cnic, staff_dob.strftime("%Y-%m-%d"), designation, phone, address, joining_date.strftime("%Y-%m-%d"), salary, education_str, fh_cnic, photo_data, g_type, n_en, fn_en, ad_en, staff_gender, a_cls, a_sec))
                        
                        conn.commit()
                        st.balloons()
                        
                        if staff_username.strip():
                            st.success(tr("✅ سٹاف کا ریکارڈ اور لاگ ان اکاؤنٹ کامیابی سے محفوظ ہو گیا!", "Staff record and login account saved successfully!"))
                        else:
                            st.success(tr("✅ سٹاف کا ریکارڈ محفوظ ہو گیا! (کوئی اکاؤنٹ نہیں بنایا گیا)", "Staff record saved! (No account created)"))
                            
                        time.sleep(1.5)
                        st.rerun()
                    except Exception as e: 
                        st.error(f"Error saving staff: {e}")
elif sub_choice in ["ریکارڈ / ایڈٹ", "Edit/Search Staff"]:
        st.markdown(f"### ✏️ {tr('سٹاف کا ریکارڈ دیکھیں یا ایڈٹ کریں', 'Search / Edit Staff Record')}")
        
        staff_df = pd.read_sql("SELECT * FROM staff", conn)
        if not staff_df.empty:
            st.dataframe(staff_df, use_container_width=True)
            
            e_staff = st.text_input(tr("سٹاف ID لکھیں جسے ایڈٹ کرنا ہے", "Enter Staff ID to Edit"))
            if e_staff:
                s_match = pd.read_sql(f"SELECT * FROM staff WHERE staff_id='{e_staff}'", conn)
                if not s_match.empty:
                    s_data = s_match.iloc[0]
                    
                    # 🟢 سمارٹ اکاؤنٹ فائنڈر سٹاف کے لیے
                    cursor.execute("SELECT username, password, role FROM users WHERE ref_id=? LIMIT 1", (e_staff,))
                    user_row = cursor.fetchone()
                    
                    if user_row:
                        def_u, def_p, def_r = user_row[0], user_row[1], user_row[2]
                        acc_status = "<span style='color: green;'>✅ (پہلے سے اکاؤنٹ موجود ہے)</span>"
                    else:
                        def_u, def_p, def_r = "", "", "Teacher" 
                        acc_status = "<span style='color: #d69e2e;'>⚠️ (کوئی اکاؤنٹ نہیں، نیا بنا سکتے ہیں)</span>"
                    
                    with st.form("edit_staff_form"):
                        c_en1, c_en2, c_en3 = st.columns(3)
                        e_sname = c_en1.text_input(tr("نام", "Name"), value=get_disp_val(s_data.get('name'), s_data.get('name_en')))
                        e_sgender = c_en2.selectbox(tr("جنس", "Gender"), ["Male", "Female", "Other"], index=["Male", "Female", "Other"].index(s_data.get('gender', 'Male') or 'Male'))
                        
                        g_type_val = s_data.get('g_type', 'Father') or 'Father'
                        e_sgtype = c_en3.selectbox(tr("رشتہ", "Relation"), ["Father", "Husband", "Guardian"], index=["Father", "Husband", "Guardian"].index(g_type_val) if g_type_val in ["Father", "Husband", "Guardian"] else 0)
                        
                        c_en4, c_en5, c_en6 = st.columns(3)
                        e_sfname = c_en4.text_input(tr("رشتہ دار کا نام", "Relation Name"), value=get_disp_val(s_data.get('fname'), s_data.get('fname_en')))
                        e_scnic = c_en5.text_input(tr("سٹاف شناختی کارڈ", "CNIC"), value=str(s_data.get('cnic', '')))
                        e_sphone = c_en6.text_input(tr("فون نمبر", "Phone"), value=str(s_data.get('phone', '')))
                        
                        c_s7, c_s8 = st.columns(2)
                        base_opts = ["Teacher", "Principal", "Clerk", "Maid/Peon", "Security Guard", "Other"]
                        curr_desig = str(s_data.get('designation', 'Teacher'))
                        if curr_desig not in base_opts: curr_desig = "Other"
                        
                        e_sdesig = c_s7.selectbox(tr("عہدہ", "Designation"), base_opts, index=base_opts.index(curr_desig))
                        e_scustom_desig = c_s8.text_input(tr("اگر عہدہ 'Other' ہے تو لکھیں", "If Other, type Designation"), value=str(s_data.get('designation', '')) if curr_desig == "Other" else "")
                        
                        e_sedu = st.text_input(tr("تعلیمی معلومات (براہ راست لکھیں)", "Education (Direct Edit)"), value=str(s_data.get('education', '')))
                        e_saddr = st.text_input(tr("پتہ", "Address"), value=get_disp_val(s_data.get('address'), s_data.get('address_en')))
                        
                        st.markdown(f"#### 🔒 {tr('سافٹ ویئر لاگ ان (اکاؤنٹ)', 'Software Login')} {acc_status}", unsafe_allow_html=True)
                        c_log1, c_log2, c_log3 = st.columns(3)
                        e_username = c_log1.text_input(tr("یوزر نیم", "Username"), value=def_u)
                        e_password = c_log2.text_input(tr("پاسورڈ", "Password"), value=def_p)
                        role_opts = ["Teacher", "Operator", "Admin"]
                        e_role = c_log3.selectbox(tr("سسٹم رول", "Role"), role_opts, index=role_opts.index(def_r) if def_r in role_opts else 0)
                        
                        if st.form_submit_button(tr("تبدیلیاں محفوظ کریں", "Save Staff Updates"), type="primary"):
                            final_desig = e_scustom_desig if e_sdesig == "Other" else e_sdesig
                            try:
                                if st.session_state.ui_lang == "اردو":
                                    cursor.execute("""
                                        UPDATE staff SET 
                                        name=?, gender=?, g_type=?, fname=?, cnic=?, phone=?, 
                                        designation=?, education=?, address=? 
                                        WHERE staff_id=?
                                    """, (e_sname, e_sgender, e_sgtype, e_sfname, e_scnic, e_sphone, final_desig, e_sedu, e_saddr, e_staff))
                                else:
                                    cursor.execute("""
                                        UPDATE staff SET 
                                        name_en=?, gender=?, g_type=?, fname_en=?, cnic=?, phone=?, 
                                        designation=?, education=?, address_en=? 
                                        WHERE staff_id=?
                                    """, (e_sname, e_sgender, e_sgtype, e_sfname, e_scnic, e_sphone, final_desig, e_sedu, e_saddr, e_staff))
                                
                                # 🟢 سٹاف کے اکاؤنٹ کو سمارٹ طریقے سے اپڈیٹ یا نیا بنانا
                                if e_username.strip():
                                    cursor.execute("SELECT id FROM users WHERE username=?", (e_username.strip(),))
                                    if cursor.fetchone():
                                        cursor.execute("UPDATE users SET password=?, role=?, ref_id=? WHERE username=?", (e_password.strip(), e_role, e_staff, e_username.strip()))
                                    else:
                                        cursor.execute("INSERT INTO users (username, password, role, ref_id) VALUES (?, ?, ?, ?)", (e_username.strip(), e_password.strip(), e_role, e_staff))
                                
                                conn.commit()
                                st.success(tr("✅ سٹاف کا ریکارڈ اور لاگ ان کامیابی سے اپڈیٹ ہو گئے۔", "Staff record and login updated successfully!"))
                                time.sleep(1)
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error: {e}")
                else:
                    st.warning(tr("اس ID کا کوئی سٹاف نہیں ملا۔", "No staff found with this ID."))
        else:
            st.info(tr("کوئی سٹاف موجود نہیں ہے۔", "No staff record available."))

elif sub_choice in ["آئی ڈی کارڈز پرنٹ", "Print ID Cards"]:
        st.markdown(f"### 🪪 {tr('سٹاف کے آئی ڈی کارڈز پرنٹ کریں', 'Print Staff ID Cards')}")
        staff_df = pd.read_sql("SELECT * FROM staff", conn)
        if not staff_df.empty:
            s_list = staff_df['staff_id'].astype(str) + " - " + staff_df['name'].astype(str)
            sel_staff = st.selectbox(tr("سٹاف ممبر چنیں", "Select Staff"), ["All (تمام سٹاف)"] + s_list.tolist())
            
            if st.button(tr("کارڈز پرنٹ کے لیے تیار کریں", "Generate Cards"), type="primary"):
                html_cards = ""
                if sel_staff.startswith("All"): cards_to_print = staff_df
                else: cards_to_print = staff_df[staff_df['staff_id'].astype(str) == sel_staff.split(" - ")[0]]
                
                for _, r in cards_to_print.iterrows():
                    n_val = get_disp_val(r.get('name'), r.get('name_en'))
                    d_val = get_desig_disp(str(r.get('designation', 'Staff')))
                    
                    html_cards += f"""
                    <div style="width: 3.375in; height: 2.125in; border: 2px solid #1a4f8b; border-radius: 10px; margin: 10px; padding: 10px; float: left; position: relative; background: linear-gradient(135deg, #ffffff, #f0f4f8); box-shadow: 2px 2px 5px rgba(0,0,0,0.2);">
                        <div style="text-align: center; border-bottom: 2px solid #1a4f8b; padding-bottom: 5px; margin-bottom: 5px;">
                            <img src="{logo_src_b64}" style="width: 35px; height: 35px; border-radius: 50%; vertical-align: middle;">
                            <span style="font-weight: bold; color: #1a4f8b; font-size: 14px; vertical-align: middle;">{school_name}</span>
                        </div>
                        <div style="font-size: 11px; line-height: 1.6; color: #333;">
                            <b>ID:</b> {r.get('staff_id')}<br>
                            <b>Name:</b> {n_val}<br>
                            <b>Designation:</b> {d_val}<br>
                            <b>Phone:</b> {r.get('phone')}
                        </div>
                        <div style="position: absolute; bottom: 10px; right: 10px; font-size: 9px; font-weight: bold; background: #1a4f8b; color: white; padding: 2px 5px; border-radius: 3px;">STAFF</div>
                    </div>
                    """
                
                html_container = f"<div style='width: 100%; display: flex; flex-wrap: wrap; justify-content: center;'>{html_cards}</div>"
                st.components.v1.html(html_container, height=600, scrolling=True)
                print_button_js(html_container, tr("آئی ڈی کارڈز پرنٹ کریں", "Print ID Cards"))
        else:
            st.info(tr("پرنٹ کرنے کے لیے کوئی سٹاف موجود نہیں ہے۔", "No staff available to print."))

                
            # ================= 12. حاضری کا ریکارڈ (Attendance Management) =================
elif core_choice in ["حاضری", "Attendance"]:
    st.markdown(f"<h2 class='no-print'>📋 {tr('حاضری مینجمنٹ (Attendance)', 'Attendance Mgt')} - {sub_choice}</h2>", unsafe_allow_html=True)
    
    if sub_choice in ["حاضری لگائیں", "Mark Attendance"]:
        c1, c2, c3 = st.columns(3)
        att_type = c1.selectbox(tr("حاضری کس کی لگانی ہے؟", "Attendance Type"), [tr("طلباء (Students)", "Students"), tr("سٹاف (Staff)", "Staff")])
        att_date = c2.date_input(tr("تاریخ", "Date"), max_value=datetime.date.today())
        
        att_type_en = "Student" if att_type in ["طلباء (Students)", "Students"] else "Staff"
        
        if att_type_en == "Student":
            att_class = c3.selectbox(tr("کلاس چنیں", "Select Class"), classes_list)
            df_person = pd.read_sql(f"SELECT reg_id as id, name, name_en, fname, fname_en FROM students WHERE class='{att_class}' AND status='Active'", conn)
        else:
            df_person = pd.read_sql("SELECT staff_id as id, name, name_en, designation as extra FROM staff", conn)
            
        if not df_person.empty:
            st.markdown(f"### {tr('حاضری شیٹ', 'Attendance Sheet')} - {att_date.strftime('%d %B %Y')}")
            
            with st.form("attendance_form"):
                att_status = {}
                for idx, r in df_person.iterrows():
                    pid = r['id']
                    n_val = get_disp_val(r.get('name'), r.get('name_en'))
                    
                    if att_type_en == "Student":
                        extra_val = get_disp_val(r.get('fname'), r.get('fname_en'))
                        disp_text = f"{pid} - {n_val} (S/O {extra_val})"
                    else:
                        disp_text = f"{pid} - {n_val} ({r.get('extra', 'Staff')})"
                        
                    # پہلے سے لگی حاضری چیک کریں
                    cursor.execute("SELECT status FROM attendance WHERE date=? AND type=? AND person_id=?", (att_date.strftime("%Y-%m-%d"), att_type_en, str(pid)))
                    exist_row = cursor.fetchone()
                    default_status = exist_row[0] if exist_row else "Present"
                    
                    col_name, col_status = st.columns([3, 1])
                    col_name.markdown(f"<div style='padding: 10px; font-weight: bold; background: #f9f9f9; border-radius: 5px; margin-bottom: 5px;'>{disp_text}</div>", unsafe_allow_html=True)
                    att_status[pid] = col_status.selectbox("Status", ["Present", "Absent", "Leave"], index=["Present", "Absent", "Leave"].index(default_status), key=f"att_{pid}", label_visibility="collapsed")
                
                if st.form_submit_button(tr("حاضری محفوظ کریں", "Save Attendance"), type="primary"):
                    try:
                        for pid, status in att_status.items():
                            cursor.execute("DELETE FROM attendance WHERE date=? AND type=? AND person_id=?", (att_date.strftime("%Y-%m-%d"), att_type_en, str(pid)))
                            cursor.execute("INSERT INTO attendance (date, type, person_id, status) VALUES (?, ?, ?, ?)", (att_date.strftime("%Y-%m-%d"), att_type_en, str(pid), status))
                        
                        conn.commit()
                        st.success(tr("✅ حاضری کامیابی سے محفوظ ہو گئی!", "Attendance saved successfully!"))
                    except Exception as e:
                        st.error(f"Error: {e}")
        else:
            st.warning(tr("اس کیٹگری میں کوئی ریکارڈ نہیں ملا۔", "No records found in this category."))

elif sub_choice in ["آج کی رپورٹ", "Today's Report"]:
        r_type = st.radio(tr("رپورٹ کی قسم", "Report Type"), [tr("طلباء (Students)", "Students"), tr("سٹاف (Staff)", "Staff")], horizontal=True)
        r_type_en = "Student" if r_type in ["طلباء (Students)", "Students"] else "Staff"
        r_date = st.date_input(tr("تاریخ منتخب کریں", "Select Date"), max_value=datetime.date.today())
        
        df_rep = pd.read_sql(f"SELECT person_id, status FROM attendance WHERE date='{r_date.strftime('%Y-%m-%d')}' AND type='{r_type_en}'", conn)
        
        if not df_rep.empty:
            p_count = len(df_rep[df_rep['status'] == 'Present'])
            a_count = len(df_rep[df_rep['status'] == 'Absent'])
            l_count = len(df_rep[df_rep['status'] == 'Leave'])
            
            c1, c2, c3 = st.columns(3)
            c1.success(f"{tr('حاضر (Present)', 'Present')}: {p_count}")
            c2.error(f"{tr('غیر حاضر (Absent)', 'Absent')}: {a_count}")
            c3.warning(f"{tr('چھٹی (Leave)', 'Leave')}: {l_count}")
            
            st.dataframe(df_rep, use_container_width=True)
        else:
            st.info(tr("اس تاریخ کی کوئی حاضری نہیں لگی۔", "No attendance found for this date."))
elif sub_choice in ["ماہانہ رپورٹ", "Monthly Report"]:
        st.markdown(f"### 📅 {tr('ماہانہ حاضری رپورٹ', 'Monthly Attendance Report')}")
        m_type = st.radio(tr("رپورٹ کی قسم", "Report Type"), [tr("طلباء (Students)", "Students"), tr("سٹاف (Staff)", "Staff")], horizontal=True, key="m_type")
        m_type_en = "Student" if m_type in ["طلباء (Students)", "Students"] else "Staff"
        
        col_m, col_y = st.columns(2)
        m_month = col_m.selectbox(tr("مہینہ", "Month"), ["01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11", "12"])
        m_year = col_y.selectbox(tr("سال", "Year"), [str(y) for y in range(2023, 2031)], index=list(range(2023, 2031)).index(datetime.date.today().year))
        
        if st.button(tr("رپورٹ بنائیں", "Generate Report"), type="primary"):
            like_str = f"{m_year}-{m_month}-%"
            df_mon = pd.read_sql(f"SELECT person_id, status FROM attendance WHERE date LIKE '{like_str}' AND type='{m_type_en}'", conn)
            
            if not df_mon.empty:
                report_data = []
                unique_ids = df_mon['person_id'].unique()
                
                for uid in unique_ids:
                    u_data = df_mon[df_mon['person_id'] == uid]
                    t_pres = len(u_data[u_data['status'] == 'Present'])
                    t_abs = len(u_data[u_data['status'] == 'Absent'])
                    t_leav = len(u_data[u_data['status'] == 'Leave'])
                    report_data.append({"ID": uid, "Total Present": t_pres, "Total Absent": t_abs, "Total Leave": t_leav})
                
                res_df = pd.DataFrame(report_data)
                st.dataframe(res_df, use_container_width=True)
            else:
                st.info(tr("اس مہینے کا کوئی ریکارڈ نہیں ملا۔", "No records found for this month."))
                
                # ================= 13. فیس اور تنخواہ (Fee & Salary Management) =================
elif core_choice in ["فیس اور تنخواہ", "Fee & Salary"]:
    st.markdown(f"<h2 class='no-print'>💵 {tr('فیس اور تنخواہ (Fee & Salary)', 'Fee & Salary Mgt')} - {sub_choice}</h2>", unsafe_allow_html=True)
    
    if sub_choice in ["فیس وصول کریں", "Collect Fee"]:
        st.markdown(f"### 💰 {tr('طالب علم کی فیس وصول کریں', 'Collect Student Fee')}")
        
        c1, c2 = st.columns([1, 2])
        f_reg = c1.text_input(tr("طالب علم کا رجسٹریشن نمبر", "Student Reg No"))
        f_month = c2.selectbox(tr("فیس کا مہینہ", "Fee Month"), ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"])
        
        if f_reg:
            df_stu = pd.read_sql(f"SELECT * FROM students WHERE reg_id='{f_reg}'", conn)
            if not df_stu.empty:
                stu = df_stu.iloc[0]
                n_val = get_disp_val(stu.get('name'), stu.get('name_en'))
                
                st.success(f"👨‍🎓 {tr('طالب علم', 'Student')}: **{n_val}** | {tr('کلاس', 'Class')}: **{stu.get('class')}**")
                
                m_fee = safe_int(stu.get('monthly_fee', 0))
                arr_fee = safe_int(stu.get('arrears', 0))
                tot_fee = m_fee + arr_fee
                
                with st.form("fee_form"):
                    c3, c4, c5 = st.columns(3)
                    t_fee = c3.number_input(tr("ماہانہ فیس", "Monthly Fee"), value=m_fee)
                    a_fee = c4.number_input(tr("بقایا جات", "Arrears"), value=arr_fee)
                    d_date = c5.date_input(tr("آخری تاریخ (Due Date)", "Due Date"))
                    
                    paid_amt = st.number_input(tr("وصول شدہ رقم", "Received Amount"), min_value=0, value=tot_fee)
                    
                    if st.form_submit_button(tr("فیس محفوظ کریں اور رسید بنائیں", "Save Fee & Generate Receipt"), type="primary"):
                        inv_no = f"INV-{f_reg}-{int(time.time())}"
                        new_arrears = (t_fee + a_fee) - paid_amt
                        f_status = "Paid" if new_arrears <= 0 else "Partial"
                        
                        try:
                            # فیس کا ریکارڈ محفوظ کرنا
                            cursor.execute("INSERT INTO fees (date, reg_id, month, tuition, arrears_col, total, status, due_date, invoice_no) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", 
                                           (today_date, f_reg, f_month, t_fee, a_fee, paid_amt, f_status, d_date.strftime("%Y-%m-%d"), inv_no))
                            
                            # طالب علم کے بقایا جات اپڈیٹ کرنا
                            cursor.execute("UPDATE students SET arrears=? WHERE reg_id=?", (new_arrears, f_reg))
                            
                            # اکاؤنٹس (Ledger) میں خودکار انٹری
                            cursor.execute("INSERT INTO accounts (date, type, description, amount, head_name, voucher_no) VALUES (?, 'Income', ?, ?, 'Student Fee', ?)",
                                           (today_date, f"Fee received from {n_val} ({f_reg}) for {f_month}", paid_amt, inv_no))
                            
                            conn.commit()
                            st.success(tr("✅ فیس کامیابی سے محفوظ ہو گئی!", "Fee saved successfully!"))
                            
                            # رسید (Receipt) کا HTML کوڈ
                            receipt_html = f"""
                            <div style="width: 100%; max-width: 400px; margin: auto; border: 2px dashed #333; padding: 20px; font-family: monospace; background: #fff;">
                                <div style="text-align: center;">
                                    <h2 style="margin:0;">{school_name.upper()}</h2>
                                    <p style="margin:5px 0;">{school_address}</p>
                                    <h3 style="border-bottom: 1px solid #333; padding-bottom: 5px;">FEE RECEIPT</h3>
                                </div>
                                <p><b>Invoice No:</b> {inv_no}<br><b>Date:</b> {today_date}</p>
                                <p><b>Reg No:</b> {f_reg}<br><b>Student Name:</b> {n_val}<br><b>Class:</b> {stu.get('class')}<br><b>Fee Month:</b> {f_month}</p>
                                <hr style="border: 1px dashed #ccc;">
                                <table style="width: 100%;">
                                    <tr><td>Monthly Fee:</td><td style="text-align:right;">Rs {t_fee}</td></tr>
                                    <tr><td>Previous Arrears:</td><td style="text-align:right;">Rs {a_fee}</td></tr>
                                    <tr><th>Total Payable:</th><th style="text-align:right;">Rs {t_fee + a_fee}</th></tr>
                                    <tr><th>Amount Paid:</th><th style="text-align:right;">Rs {paid_amt}</th></tr>
                                    <tr><th>Remaining Balance:</th><th style="text-align:right;">Rs {new_arrears}</th></tr>
                                </table>
                                <hr style="border: 1px dashed #ccc;">
                                <p style="text-align: center; margin-top: 20px;">Signature: ________________</p>
                                <p style="text-align: center; font-size: 10px;">Thank you!</p>
                            </div>
                            """
                            st.components.v1.html(receipt_html, height=450, scrolling=True)
                            print_button_js(receipt_html, tr("رسید پرنٹ کریں", "Print Receipt"))
                            
                        except Exception as e:
                            st.error(f"Error: {e}")
            else:
                st.warning(tr("اس رجسٹریشن نمبر کا کوئی طالب علم نہیں ملا۔", "No student found with this Reg No."))

elif sub_choice in ["فیس ڈیفالٹرز", "Fee Defaulters"]:
        st.markdown(f"### 🚨 {tr('فیس ڈیفالٹرز کی فہرست', 'Fee Defaulters List')}")
        try:
            df_def = pd.read_sql(f"SELECT s.reg_id, s.name, s.name_en, s.class, s.phone, s.arrears FROM students s WHERE s.arrears > 0 AND s.status='Active'", conn)
            if not df_def.empty:
                st.dataframe(df_def, use_container_width=True)
                if st.button(tr("ڈیفالٹرز لسٹ پرنٹ کریں", "Print Defaulters List"), type="primary"):
                    html_def = f"<h2>Fee Defaulters List - {today_date}</h2>" + df_def.to_html(index=False)
                    print_button_js(html_def, "Print List")
            else:
                st.success(tr("کوئی طالب علم ڈیفالٹر نہیں ہے۔", "No fee defaulters found."))
        except Exception as e:
            st.error(f"Error: {e}")

elif sub_choice in ["تنخواہ ادا کریں", "Pay Salary"]:
        st.markdown(f"### 💸 {tr('سٹاف کی تنخواہ ادا کریں', 'Pay Staff Salary')}")
        
        staff_df = pd.read_sql("SELECT staff_id, name, name_en, designation, salary FROM staff", conn)
        if not staff_df.empty:
            s_list = staff_df['staff_id'].astype(str) + " - " + staff_df['name'].astype(str)
            sel_staff = st.selectbox(tr("سٹاف ممبر منتخب کریں", "Select Staff Member"), s_list)
            
            s_id = sel_staff.split(" - ")[0]
            curr_staff = staff_df[staff_df['staff_id'].astype(str) == s_id].iloc[0]
            
            st.info(f"👨‍🏫 {tr('عہدہ', 'Designation')}: {curr_staff['designation']} | 💵 {tr('مقررہ تنخواہ', 'Basic Salary')}: Rs {curr_staff['salary']}")
            
            with st.form("salary_form"):
                sal_month = st.selectbox(tr("تنخواہ کا مہینہ", "Salary Month"), ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"])
                sal_paid = st.number_input(tr("ادا کی گئی رقم", "Amount Paid"), min_value=0, value=safe_int(curr_staff['salary']))
                sal_remarks = st.text_input(tr("ریمارکس (تفصیل)", "Remarks"))
                
                if st.form_submit_button(tr("تنخواہ محفوظ کریں", "Save Salary Record"), type="primary"):
                    try:
                        cursor.execute("INSERT INTO salary_records (date, staff_id, month, amount, remarks) VALUES (?, ?, ?, ?, ?)",
                                       (today_date, s_id, sal_month, sal_paid, sal_remarks))
                        
                        # اکاؤنٹس (Ledger) میں خرچ (Expense) کی خودکار انٹری
                        cursor.execute("INSERT INTO accounts (date, type, description, amount, head_name, voucher_no) VALUES (?, 'Expense', ?, ?, 'Salary Account', ?)",
                                       (today_date, f"Salary paid to {curr_staff['name']} for {sal_month}", sal_paid, f"SAL-{s_id}-{int(time.time())}"))
                        
                        conn.commit()
                        st.success(tr("✅ تنخواہ کا ریکارڈ کامیابی سے محفوظ ہو گیا!", "Salary record saved successfully!"))
                    except Exception as e:
                        st.error(f"Error: {e}")
        else:
            st.warning(tr("کوئی سٹاف موجود نہیں ہے۔", "No staff available."))

elif sub_choice in ["سلپ پرنٹ کریں", "Print Slips"]:
        st.markdown(f"### 🖨️ {tr('پرانی رسید پرنٹ کریں', 'Print Previous Slip')}")
        s_type = st.radio(tr("رسید کی قسم", "Slip Type"), ["Fee Receipt", "Salary Slip"], horizontal=True)
        s_no = st.text_input(tr("رجسٹریشن نمبر / سٹاف ID لکھیں", "Enter Reg No / Staff ID"))
        
        if s_no and st.button(tr("تلاش کریں", "Search Record")):
            if s_type == "Fee Receipt":
                df_srch = pd.read_sql(f"SELECT * FROM fees WHERE reg_id='{s_no}' ORDER BY date DESC", conn)
            else:
                df_srch = pd.read_sql(f"SELECT * FROM salary_records WHERE staff_id='{s_no}' ORDER BY date DESC", conn)
                
            if not df_srch.empty:
                st.dataframe(df_srch, use_container_width=True)
            else:
                st.warning(tr("کوئی ریکارڈ نہیں ملا۔", "No record found."))
                
                # ================= 14. اکاؤنٹس اور لیجر (Accounts & Ledger) =================
elif core_choice in ["اکاؤنٹس (لیجر)", "Accounts"]:
    st.markdown(f"<h2 class='no-print'>💲 {tr('اکاؤنٹس اور لیجر (Accounts)', 'Accounts & Ledger')} - {sub_choice}</h2>", unsafe_allow_html=True)
    
    if sub_choice in ["نئی ٹرانزیکشن", "New Transaction"]:
        st.markdown(f"### ➕ {tr('نئی آمدنی یا خرچ درج کریں', 'Enter New Income / Expense')}")
        
        heads_df = pd.read_sql("SELECT head_name FROM account_heads", conn)
        heads_list = heads_df['head_name'].tolist() if not heads_df.empty else ["General Expense", "Student Fee", "Salary Account", "Utility Bills", "Office Supplies"]
        
        with st.form("transaction_form", clear_on_submit=True):
            c1, c2, c3 = st.columns(3)
            t_type = c1.selectbox(tr("قسم", "Type"), ["Income", "Expense"])
            t_head = c2.selectbox(tr("اکاؤنٹ ہیڈ", "Account Head"), heads_list)
            t_date = c3.date_input(tr("تاریخ", "Date"), max_value=datetime.date.today())
            
            c4, c5 = st.columns([1, 2])
            t_amount = c4.number_input(tr("رقم (Amount)", "Amount"), min_value=1)
            t_desc = c5.text_input(tr("تفصیل (Description)", "Description"))
            
            if st.form_submit_button(tr("ٹرانزیکشن محفوظ کریں", "Save Transaction"), type="primary"):
                v_no = f"VCH-{int(time.time())}"
                try:
                    cursor.execute("INSERT INTO accounts (date, type, description, amount, head_name, voucher_no) VALUES (?, ?, ?, ?, ?, ?)",
                                   (t_date.strftime("%Y-%m-%d"), t_type, t_desc, t_amount, t_head, v_no))
                    conn.commit()
                    st.success(tr("✅ ٹرانزیکشن کامیابی سے محفوظ ہو گئی!", "Transaction saved successfully!"))
                    time.sleep(1)
                    st.rerun()
                except Exception as e:
                    st.error(f"Error: {e}")

elif sub_choice in ["کیش بک / لیجر", "Cash Book / Ledger"]:
        st.markdown(f"### 📘 {tr('کیش بک اور لیجر رپورٹ', 'Cash Book / Ledger Report')}")
        
        c_from, c_to = st.columns(2)
        from_date = c_from.date_input(tr("اس تاریخ سے", "From Date"), value=datetime.date.today().replace(day=1))
        to_date = c_to.date_input(tr("اس تاریخ تک", "To Date"), max_value=datetime.date.today())
        
        if st.button(tr("رپورٹ دکھائیں", "Show Report"), type="primary"):
            df_acc = pd.read_sql(f"SELECT date, type, head_name, amount, description, voucher_no FROM accounts WHERE date BETWEEN '{from_date.strftime('%Y-%m-%d')}' AND '{to_date.strftime('%Y-%m-%d')}' ORDER BY date ASC", conn)
            
            if not df_acc.empty:
                tot_income = df_acc[df_acc['type'] == 'Income']['amount'].sum()
                tot_expense = df_acc[df_acc['type'] == 'Expense']['amount'].sum()
                balance = tot_income - tot_expense
                
                c_inc, c_exp, c_bal = st.columns(3)
                c_inc.success(f"### 📈 {tr('کل آمدنی', 'Total Income')}\n**Rs {tot_income}**")
                c_exp.error(f"### 📉 {tr('کل خرچ', 'Total Expense')}\n**Rs {tot_expense}**")
                
                if balance >= 0:
                    c_bal.info(f"### 💰 {tr('موجودہ بیلنس', 'Net Balance')}\n**Rs {balance}**")
                else:
                    c_bal.warning(f"### ⚠️ {tr('موجودہ بیلنس', 'Net Balance')}\n**Rs {balance}**")
                
                st.dataframe(df_acc, use_container_width=True)
                
                # پرنٹ کے لیے خوبصورت لیجر کی رسید
                html_ledger = f"""
                <div style="font-family: Arial, sans-serif; padding: 20px;">
                    <div style="text-align: center; border-bottom: 2px solid #333; padding-bottom: 10px; margin-bottom: 20px;">
                        <h2 style="margin: 0;">{school_name.upper()}</h2>
                        <p style="margin: 5px 0;">{school_address}</p>
                        <h3>FINANCIAL LEDGER REPORT</h3>
                        <p><b>Period:</b> {from_date} to {to_date}</p>
                    </div>
                    <table style="width: 100%; border-collapse: collapse; margin-bottom: 20px;">
                        <tr style="background: #f0f0f0;">
                            <th style="border: 1px solid #ccc; padding: 8px;">Date</th>
                            <th style="border: 1px solid #ccc; padding: 8px;">Type</th>
                            <th style="border: 1px solid #ccc; padding: 8px;">Head</th>
                            <th style="border: 1px solid #ccc; padding: 8px;">Description</th>
                            <th style="border: 1px solid #ccc; padding: 8px;">Amount (Rs)</th>
                        </tr>
                """
                for _, r in df_acc.iterrows():
                    color = "#e8f5e9" if r['type'] == 'Income' else "#ffebee"
                    html_ledger += f"""
                        <tr style="background: {color};">
                            <td style="border: 1px solid #ccc; padding: 8px; text-align: center;">{r['date']}</td>
                            <td style="border: 1px solid #ccc; padding: 8px; text-align: center;">{r['type']}</td>
                            <td style="border: 1px solid #ccc; padding: 8px;">{r['head_name']}</td>
                            <td style="border: 1px solid #ccc; padding: 8px;">{r['description']}</td>
                            <td style="border: 1px solid #ccc; padding: 8px; text-align: right; font-weight: bold;">{r['amount']}</td>
                        </tr>
                    """
                html_ledger += f"""
                    </table>
                    <div style="float: right; width: 300px; border: 2px solid #333; padding: 10px;">
                        <p style="margin: 5px 0;"><b>Total Income:</b> Rs {tot_income}</p>
                        <p style="margin: 5px 0; color: red;"><b>Total Expense:</b> Rs {tot_expense}</p>
                        <hr>
                        <p style="margin: 5px 0; font-size: 18px;"><b>Net Balance:</b> Rs {balance}</p>
                    </div>
                </div>
                """
                print_button_js(html_ledger, tr("لیجر پرنٹ کریں", "Print Ledger Report"))
            else:
                st.info(tr("اس دورانیے کی کوئی ٹرانزیکشن نہیں ملی۔", "No transactions found in this date range."))

elif sub_choice in ["اکاؤنٹ ہیڈز", "Account Heads"]:
        st.markdown(f"### 🗂️ {tr('اکاؤنٹ ہیڈز بنائیں', 'Manage Account Heads')}")
        
        with st.form("head_form", clear_on_submit=True):
            h_name = st.text_input(tr("نئے ہیڈ کا نام", "New Head Name"))
            h_type = st.selectbox(tr("ہیڈ کی قسم", "Head Type"), ["Income", "Expense"])
            
            if st.form_submit_button(tr("محفوظ کریں", "Save Head"), type="primary"):
                if h_name.strip():
                    try:
                        cursor.execute("INSERT INTO account_heads (head_name, head_type) VALUES (?, ?)", (h_name.strip(), h_type))
                        conn.commit()
                        st.success(tr("✅ نیا ہیڈ کامیابی سے بن گیا۔", "New head created successfully."))
                        time.sleep(1)
                        st.rerun()
                    except sqlite3.IntegrityError:
                        st.error(tr("⚠️ یہ ہیڈ پہلے سے موجود ہے۔", "⚠️ This head already exists."))
                else:
                    st.error(tr("⚠️ ہیڈ کا نام لکھنا لازمی ہے۔", "⚠️ Head name is required."))
                    
        st.markdown(f"#### 📋 {tr('موجودہ ہیڈز کی فہرست', 'Existing Account Heads')}")
        df_heads = pd.read_sql("SELECT head_name as 'Head Name', head_type as 'Type' FROM account_heads ORDER BY head_type", conn)
        if not df_heads.empty:
            st.dataframe(df_heads, use_container_width=True)
        else:
            st.info(tr("کوئی اکاؤنٹ ہیڈ موجود نہیں ہے۔", "No account heads found."))
            
            # ================= 15. تعلیمی ریکارڈ (Academics & Exams) =================
elif core_choice in ["تعلیمی ریکارڈ", "Academics"]:
    st.markdown(f"<h2 class='no-print'>📚 {tr('تعلیمی ریکارڈ (Academics)', 'Academics Mgt')} - {sub_choice}</h2>", unsafe_allow_html=True)
    
    # 🟢 پرائمری سکول کے مضامین (Primary Level Subjects)
    pri_subjects = ["English", "Urdu", "Math", "Science", "Islamiyat", "Nazra Quran", "General Knowledge", "Drawing", "Computer"]

    if sub_choice in ["ٹائم ٹیبل", "Timetable"]:
        st.markdown(f"### 🕒 {tr('کلاس ٹائم ٹیبل', 'Class Timetable')}")
        with st.form("timetable_form"):
            c1, c2, c3 = st.columns(3)
            t_class = c1.selectbox(tr("کلاس", "Class"), classes_list)
            t_sec = c2.selectbox(tr("سیکشن", "Section"), ["A", "B", "C", "D", "Model"])
            t_day = c3.selectbox(tr("دن", "Day"), ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"])
            
            c4, c5, c6 = st.columns(3)
            t_period = c4.selectbox(tr("پیریڈ", "Period"), ["1st", "2nd", "3rd", "4th", "5th", "6th", "7th", "8th"])
            t_subj = c5.selectbox(tr("مضمون", "Subject"), pri_subjects)
            
            staff_df = pd.read_sql("SELECT staff_id, name, name_en FROM staff WHERE designation='Teacher' OR designation='Teacher (استاد)'", conn)
            teacher_list = (staff_df['staff_id'].astype(str) + " - " + (staff_df['name_en'] if st.session_state.ui_lang == "English" else staff_df['name'])).tolist() if not staff_df.empty else ["None"]
            t_teacher = c6.selectbox(tr("استاد (Teacher)", "Teacher"), teacher_list)
            
            if st.form_submit_button(tr("محفوظ کریں", "Save Timetable"), type="primary"):
                try:
                    tid = t_teacher.split(" - ")[0] if t_teacher != "None" else ""
                    cursor.execute("DELETE FROM timetable WHERE class=? AND section=? AND day=? AND period=?", (t_class, t_sec, t_day, t_period))
                    cursor.execute("INSERT INTO timetable (class, section, day, period, subject, teacher_id) VALUES (?, ?, ?, ?, ?, ?)", (t_class, t_sec, t_day, t_period, t_subj, tid))
                    conn.commit()
                    st.success(tr("✅ ٹائم ٹیبل محفوظ ہو گیا۔", "Timetable saved."))
                except Exception as e: st.error(f"Error: {e}")
                
        st.markdown(f"#### 📋 {tr('موجودہ ٹائم ٹیبل', 'Current Timetable')}")
        v_class = st.selectbox(tr("دیکھنے کے لیے کلاس چنیں", "Select Class to View"), classes_list, key="v_cls")
        df_tt = pd.read_sql(f"SELECT day as Day, period as Period, subject as Subject, teacher_id as 'Teacher ID' FROM timetable WHERE class='{v_class}' ORDER BY day, period", conn)
        if not df_tt.empty: st.dataframe(df_tt, use_container_width=True)

elif sub_choice in ["لیسن پلان", "Lesson Plan"]:
        st.markdown(f"### 📝 {tr('پرائمری لیسن پلاننگ', 'Primary Lesson Planning')}")
        
        tab_view, tab_add = st.tabs([tr("پلان دیکھیں (فلٹرز)", "View Plans (Filters)"), tr("نیا پلان بنائیں", "Create New Plan")])
        
        with tab_add:
            with st.form("lesson_plan_form"):
                lp_type = st.radio(tr("پلان کی قسم", "Plan Type"), ["Daily", "Weekly", "Monthly"], horizontal=True)
                # 🟢 ڈیلی پلان میں تاریخ تبدیل کرنے کا آپشن
                lp_date = st.date_input(tr("تاریخ منتخب کریں (قابلِ تبدیلی)", "Select Date (Editable)"), value=datetime.date.today())
                
                c1, c2, c3 = st.columns(3)
                lp_class = c1.selectbox(tr("کلاس", "Class"), classes_list, key="lp_cls")
                lp_subj = c2.selectbox(tr("مضمون", "Subject"), pri_subjects, key="lp_sub")
                lp_status = c3.selectbox(tr("سٹیٹس", "Status"), ["Pending", "In Progress", "Completed"])
                
                lp_topic = st.text_area(tr("پڑھانے کا ٹاپک / تفصیل", "Topic & Details"))
                
                if st.form_submit_button(tr("محفوظ کریں", "Save Plan"), type="primary"):
                    try:
                        cursor.execute("INSERT INTO lesson_plan (date, class, section, subject, teacher_id, topic, status, plan_type) VALUES (?, ?, 'A', ?, ?, ?, ?, ?)",
                                       (lp_date.strftime("%Y-%m-%d"), lp_class, lp_subj, st.session_state.current_user, lp_topic, lp_status, lp_type))
                        conn.commit()
                        st.success(tr("✅ لیسن پلان محفوظ ہو گیا۔", "Lesson Plan saved."))
                    except Exception as e: st.error(f"Error: {e}")
                    
        with tab_view:
            # 🟢 ویکلی/ماہانہ کے لیے بیٹوین ڈیٹس (Date Range) کا فلٹر
            filter_type = st.radio(tr("فلٹر کا طریقہ", "Filter By"), [tr("ایک مخصوص تاریخ (Daily)", "Specific Date (Daily)"), tr("تاریخوں کے درمیان (Date Range)", "Between Dates (Range)")], horizontal=True)
            
            if filter_type in ["تاریخوں کے درمیان (Date Range)", "Between Dates (Range)"]:
                col_d1, col_d2 = st.columns(2)
                start_date = col_d1.date_input(tr("شروع کی تاریخ", "Start Date"), value=datetime.date.today() - datetime.timedelta(days=7))
                end_date = col_d2.date_input(tr("ختم کی تاریخ", "End Date"), value=datetime.date.today())
                query = f"SELECT date, plan_type, class, subject, topic, status FROM lesson_plan WHERE date BETWEEN '{start_date.strftime('%Y-%m-%d')}' AND '{end_date.strftime('%Y-%m-%d')}' ORDER BY date DESC"
            else:
                s_date = st.date_input(tr("تاریخ", "Date"), key="s_date")
                query = f"SELECT date, plan_type, class, subject, topic, status FROM lesson_plan WHERE date='{s_date.strftime('%Y-%m-%d')}' ORDER BY date DESC"
            
            if st.button(tr("پلان تلاش کریں", "Search Plans")):
                df_lp = pd.read_sql(query, conn)
                if not df_lp.empty: st.dataframe(df_lp, use_container_width=True)
                else: st.warning(tr("کوئی ریکارڈ نہیں ملا۔", "No records found."))

elif sub_choice in ["امتحان کی سیٹنگ", "Exam Setup"]:
        st.markdown(f"### 📝 {tr('امتحانی پرچہ جنریٹر', 'Exam Paper Generator')}")
        st.info(tr("پرائمری سکول کے معیار اور A4 سائز کے مطابق پیپر تیار کیا جائے گا۔", "Paper will be generated according to Primary standard and fixed A4 size."))
        
        with st.form("exam_gen_form"):
            c1, c2, c3 = st.columns(3)
            ex_cls = c1.selectbox(tr("کلاس", "Class"), classes_list, key="ex_cls")
            ex_subj = c2.selectbox(tr("مضمون", "Subject"), pri_subjects, key="ex_sub")
            ex_term = c3.selectbox(tr("امتحان / ٹرم", "Term"), ["First Term", "Mid Term", "Final Term", "Monthly Test"])
            
            c4, c5, c6 = st.columns(3)
            ex_date = c4.date_input(tr("پرچے کی تاریخ", "Exam Date"))
            t_marks = c5.number_input(tr("کل نمبر", "Total Marks"), min_value=10, value=50)
            t_time = c6.text_input(tr("وقت (Time)", "Time Allowed"), value="2 Hours")
            
            c7, c8 = st.columns(2)
            num_mcqs = c7.number_input(tr("MCQs کی تعداد", "Number of MCQs"), min_value=0, max_value=50, value=10)
            # 🟢 نمبر آف کیوسچنز (انشائیہ سوالات) کی تعداد سلیکٹ کرنے کا آپشن
            num_qs = c8.number_input(tr("انشائیہ سوالات کی تعداد", "Number of Subjective Questions"), min_value=0, max_value=20, value=5)
            
            if st.form_submit_button(tr("پیپر تیار کریں (Generate Paper)", "Generate Paper"), type="primary"):
                # 🟢 انگلش ماڈیول میں سختی سے صرف انگلش ہیڈنگز (کوئی اردو نہیں)
                if st.session_state.ui_lang == "English":
                    head_title = "EXAMINATION PAPER"
                    lbl_cls = "Class:"
                    lbl_sub = "Subject:"
                    lbl_tm = "Total Marks:"
                    lbl_time = "Time Allowed:"
                    lbl_name = "Student Name:"
                    lbl_roll = "Roll No:"
                    lbl_mcq = "Q1: Encircle the correct option."
                    lbl_sub_q = "Attempt the following questions."
                else:
                    head_title = "امتحانی پرچہ"
                    lbl_cls = "کلاس:"
                    lbl_sub = "مضمون:"
                    lbl_tm = "کل نمبر:"
                    lbl_time = "وقت:"
                    lbl_name = "نام طالب علم:"
                    lbl_roll = "رول نمبر:"
                    lbl_mcq = "سوال 1: درست جواب کے گرد دائرہ لگائیں۔"
                    lbl_sub_q = "درج ذیل سوالات کے تفصیلی جوابات تحریر کریں۔"

                # 🟢 A4 سائز کی فکسڈ سیٹنگ اور CSS
                html_paper = f"""
                <div style="font-family: Arial, sans-serif; background: white; padding: 20px; max-width: 210mm; margin: auto;">
                    <div style="text-align: center; border-bottom: 2px solid black; padding-bottom: 10px; margin-bottom: 20px;">
                        <img src="{logo_src_b64}" style="width: 60px; height: 60px; border-radius: 50%;">
                        <h2 style="margin: 5px 0 0 0;">{school_name.upper()}</h2>
                        <h3 style="margin: 5px 0;">{ex_term.upper()} - {head_title}</h3>
                    </div>
                    
                    <div style="display: flex; justify-content: space-between; font-weight: bold; margin-bottom: 15px; font-size: 14px;">
                        <div>{lbl_name} ____________________</div>
                        <div>{lbl_roll} __________</div>
                    </div>
                    <div style="display: flex; justify-content: space-between; font-weight: bold; margin-bottom: 20px; font-size: 14px; border-bottom: 1px dashed #ccc; padding-bottom: 15px;">
                        <div>{lbl_cls} {ex_cls}</div>
                        <div>{lbl_sub} {ex_subj}</div>
                        <div>{lbl_time} {t_time}</div>
                        <div>{lbl_tm} {t_marks}</div>
                    </div>
                """
                
                if num_mcqs > 0:
                    html_paper += f"<h4 style='margin-bottom: 10px;'>{lbl_mcq} ({num_mcqs} Marks)</h4><ul style='list-style-type: none; padding: 0; line-height: 2.5;'>"
                    for i in range(1, int(num_mcqs) + 1):
                        html_paper += f"<li style='margin-bottom: 15px;'>{i}. ______________________________________________________________ <br> a) ________ b) ________ c) ________ d) ________</li>"
                    html_paper += "</ul>"
                
                if num_qs > 0:
                    html_paper += f"<hr><h4 style='margin-bottom: 10px;'>{lbl_sub_q}</h4><ul style='list-style-type: none; padding: 0; line-height: 3;'>"
                    # 🟢 انشائیہ سوالات کے لیے بڑی لائنیں (Primary Level Spacing)
                    for i in range(1, int(num_qs) + 1):
                        html_paper += f"<li><b>Q{i}:</b> ________________________________________________________________<br>_________________________________________________________________________<br>_________________________________________________________________________</li><br>"
                    html_paper += "</ul>"
                
                html_paper += "</div>"
                st.components.v1.html(html_paper, height=600, scrolling=True)
                
                # پرنٹ کے بٹن میں A4 سائز کی سختی سے پابندی
                print_button_js(html_paper, tr("پیپر پرنٹ کریں (A4 Size)", "Print Paper (A4 Size)"))

elif sub_choice in ["نمبرز کا اندراج", "Marks Entry"]:
        st.markdown(f"### ✍️ {tr('امتحانی نمبرز کا اندراج', 'Exam Marks Entry')}")
        c1, c2, c3 = st.columns(3)
        m_exam = c1.selectbox(tr("امتحان کا نام", "Exam Name"), ["First Term", "Mid Term", "Final Term", "Monthly Test"])
        m_cls = c2.selectbox(tr("کلاس", "Class"), classes_list, key="m_cls")
        m_sub = c3.selectbox(tr("مضمون", "Subject"), pri_subjects, key="m_sub")
        
        df_st = pd.read_sql(f"SELECT reg_id, name, name_en FROM students WHERE class='{m_cls}' AND status='Active'", conn)
        if not df_st.empty:
            with st.form("marks_form"):
                tot_marks = st.number_input(tr("کل نمبر", "Total Marks"), min_value=10, value=100)
                marks_dict = {}
                for _, r in df_st.iterrows():
                    n_val = get_disp_val(r.get('name'), r.get('name_en'))
                    marks_dict[r['reg_id']] = st.number_input(f"{r['reg_id']} - {n_val}", min_value=0.0, max_value=float(tot_marks), value=0.0, step=0.5)
                
                if st.form_submit_button(tr("نمبرز محفوظ کریں", "Save Marks"), type="primary"):
                    try:
                        for rid, m_obt in marks_dict.items():
                            cursor.execute("DELETE FROM exam_marks WHERE exam_name=? AND reg_id=? AND subject=?", (m_exam, rid, m_sub))
                            cursor.execute("INSERT INTO exam_marks (exam_name, reg_id, subject, total_marks, obtained_marks) VALUES (?, ?, ?, ?, ?)", (m_exam, rid, m_sub, tot_marks, m_obt))
                        conn.commit()
                        st.success(tr("✅ نمبرز کامیابی سے محفوظ ہو گئے۔", "Marks saved successfully."))
                    except Exception as e: st.error(f"Error: {e}")
        else: st.warning(tr("اس کلاس میں کوئی طالب علم موجود نہیں۔", "No students found in this class."))

elif sub_choice in ["رزلٹ کارڈز", "Result Cards"]:
        st.markdown(f"### 🏆 {tr('رزلٹ کارڈ پرنٹ کریں', 'Print Result Cards')}")
        r_exam = st.selectbox(tr("امتحان چنیں", "Select Exam"), ["First Term", "Mid Term", "Final Term", "Monthly Test"])
        r_reg = st.text_input(tr("طالب علم کا رجسٹریشن نمبر", "Student Reg No"))
        
        if r_reg and st.button(tr("رزلٹ کارڈ بنائیں", "Generate Result Card"), type="primary"):
            df_m = pd.read_sql(f"SELECT subject, total_marks, obtained_marks FROM exam_marks WHERE exam_name='{r_exam}' AND reg_id='{r_reg}'", conn)
            df_s = pd.read_sql(f"SELECT * FROM students WHERE reg_id='{r_reg}'", conn)
            
            if not df_m.empty and not df_s.empty:
                stu = df_s.iloc[0]
                n_val = get_disp_val(stu.get('name'), stu.get('name_en'))
                tm = df_m['total_marks'].sum()
                om = df_m['obtained_marks'].sum()
                perc = round((om / tm) * 100, 1) if tm > 0 else 0
                grade = "A+" if perc>=90 else ("A" if perc>=80 else ("B" if perc>=70 else ("C" if perc>=60 else "Fail")))
                
                html_res = f"""
                <div style="border: 4px solid #1a4f8b; padding: 20px; max-width: 700px; margin: auto; background: #fff; font-family: Arial, sans-serif;">
                    <div style="text-align: center; border-bottom: 2px solid #ccc; padding-bottom: 10px; margin-bottom: 15px;">
                        <h2 style="margin: 0; color: #1a4f8b;">{school_name.upper()}</h2>
                        <h3 style="background: #1a4f8b; color: white; display: inline-block; padding: 5px 20px; border-radius: 20px;">RESULT CARD - {r_exam.upper()}</h3>
                    </div>
                    <p><b>Reg No:</b> {r_reg} &nbsp;&nbsp;&nbsp; <b>Name:</b> {n_val} &nbsp;&nbsp;&nbsp; <b>Class:</b> {stu.get('class')}</p>
                    <table style="width: 100%; border-collapse: collapse; margin-top: 15px;">
                        <tr style="background: #f0f0f0; border-bottom: 2px solid #ccc;">
                            <th style="padding: 8px; text-align: left;">Subject</th>
                            <th style="padding: 8px; text-align: center;">Total Marks</th>
                            <th style="padding: 8px; text-align: center;">Obtained Marks</th>
                        </tr>
                """
                for _, row in df_m.iterrows():
                    html_res += f"<tr><td style='border-bottom: 1px solid #eee; padding: 8px;'>{row['subject']}</td><td style='border-bottom: 1px solid #eee; padding: 8px; text-align: center;'>{row['total_marks']}</td><td style='border-bottom: 1px solid #eee; padding: 8px; text-align: center;'>{row['obtained_marks']}</td></tr>"
                
                html_res += f"""
                    </table>
                    <div style="display: flex; justify-content: space-between; margin-top: 20px; background: #e8f5e9; padding: 15px; border-radius: 5px; font-weight: bold;">
                        <div>Total: {om} / {tm}</div>
                        <div>Percentage: {perc}%</div>
                        <div>Grade: {grade}</div>
                    </div>
                    <div style="margin-top: 40px; display: flex; justify-content: space-between;">
                        <div style="text-align: center;">_________________<br>Class Teacher</div>
                        <div style="text-align: center;">_________________<br>Principal</div>
                    </div>
                </div>
                """
                st.components.v1.html(html_res, height=500, scrolling=True)
                print_button_js(html_res, tr("رزلٹ کارڈ پرنٹ کریں", "Print Result Card"))
            else:
                st.warning(tr("اس رجسٹریشن نمبر کا کوئی رزلٹ نہیں ملا۔", "No result found for this Reg No."))
                
                # ================= 16. لائبریری (Library Management) =================
elif core_choice in ["لائبریری", "Library"]:
    st.markdown(f"<h2 class='no-print'>📖 {tr('لائبریری مینجمنٹ (Library)', 'Library Mgt')} - {sub_choice}</h2>", unsafe_allow_html=True)
    
    if sub_choice in ["کتابوں کا ریکارڈ", "Manage Books"]:
        st.markdown(f"### 📚 {tr('نئی کتاب شامل کریں', 'Add New Book')}")
        with st.form("book_form", clear_on_submit=True):
            c1, c2, c3 = st.columns(3)
            b_id = c1.text_input(tr("کتاب کی ID (ISBN/Code)", "Book ID / Code"))
            b_title = c2.text_input(tr("کتاب کا نام", "Book Title"))
            b_author = c3.text_input(tr("مصنف (Author)", "Author"))
            
            c4, c5 = st.columns(2)
            b_cat = c4.text_input(tr("کیٹگری", "Category"), value="General")
            b_qty = c5.number_input(tr("کل تعداد", "Total Quantity"), min_value=1, value=1)
            
            if st.form_submit_button(tr("کتاب محفوظ کریں", "Save Book"), type="primary"):
                if b_id.strip() and b_title.strip():
                    try:
                        cursor.execute("INSERT INTO books (book_id, title, author, category, total_qty, available_qty) VALUES (?, ?, ?, ?, ?, ?)",
                                       (b_id.strip(), b_title.strip(), b_author.strip(), b_cat.strip(), b_qty, b_qty))
                        conn.commit()
                        st.success(tr("✅ کتاب کامیابی سے شامل ہو گئی!", "Book added successfully!"))
                    except Exception as e: st.error(f"Error: {e}")
                else: st.error(tr("⚠️ کتاب کی ID اور نام لکھنا لازمی ہے۔", "Book ID and Title are required."))
                
        st.markdown(f"#### 📋 {tr('لائبریری کی تمام کتابیں', 'All Library Books')}")
        df_books = pd.read_sql("SELECT * FROM books", conn)
        if not df_books.empty: st.dataframe(df_books, use_container_width=True)
        else: st.info(tr("لائبریری میں کوئی کتاب موجود نہیں۔", "No books in library."))

elif sub_choice in ["کتاب جاری / واپس کریں", "Issue / Return Books"]:
        st.markdown(f"### 🔄 {tr('کتاب جاری یا واپس کریں', 'Issue / Return Book')}")
        action = st.radio(tr("عمل منتخب کریں", "Select Action"), [tr("کتاب جاری کریں (Issue)", "Issue Book"), tr("کتاب واپس لیں (Return)", "Return Book")], horizontal=True)
        
        if action.startswith("کتاب جاری") or action.startswith("Issue"):
            with st.form("issue_form"):
                c1, c2 = st.columns(2)
                ib_id = c1.text_input(tr("کتاب کی ID", "Book ID"))
                ib_reg = c2.text_input(tr("طالب علم کا رجسٹریشن نمبر", "Student Reg No"))
                ib_due = st.date_input(tr("واپس کرنے کی تاریخ", "Due Date"))
                
                if st.form_submit_button(tr("کتاب جاری کریں", "Issue Book"), type="primary"):
                    try:
                        cursor.execute("SELECT available_qty FROM books WHERE book_id=?", (ib_id,))
                        brow = cursor.fetchone()
                        if brow and brow[0] > 0:
                            cursor.execute("INSERT INTO book_issue (book_id, issued_to_type, reg_id, issue_date, due_date, status) VALUES (?, 'Student', ?, ?, ?, 'Issued')",
                                           (ib_id, ib_reg, today_date, ib_due.strftime("%Y-%m-%d")))
                            cursor.execute("UPDATE books SET available_qty = available_qty - 1 WHERE book_id=?", (ib_id,))
                            conn.commit()
                            st.success(tr("✅ کتاب کامیابی سے جاری کر دی گئی!", "Book issued successfully!"))
                        else: st.error(tr("⚠️ یہ کتاب فی الحال دستیاب نہیں ہے۔", "Book not available."))
                    except Exception as e: st.error(f"Error: {e}")
        else:
            with st.form("return_form"):
                rb_id = st.text_input(tr("کتاب کی ID جو واپس کرنی ہے", "Book ID to Return"))
                r_reg = st.text_input(tr("طالب علم کا رجسٹریشن نمبر", "Student Reg No"))
                
                if st.form_submit_button(tr("کتاب واپس جمع کریں", "Return Book"), type="primary"):
                    try:
                        cursor.execute("UPDATE book_issue SET status='Returned', return_date=? WHERE book_id=? AND reg_id=? AND status='Issued'", (today_date, rb_id, r_reg))
                        cursor.execute("UPDATE books SET available_qty = available_qty + 1 WHERE book_id=?", (rb_id,))
                        conn.commit()
                        st.success(tr("✅ کتاب کامیابی سے واپس لے لی گئی!", "Book returned successfully!"))
                    except Exception as e: st.error(f"Error: {e}")

elif sub_choice in ["لائبریری رپورٹس", "Library Reports"]:
        st.markdown(f"### 📊 {tr('اجراء شدہ کتابوں کی رپورٹ', 'Issued Books Report')}")
        df_issued = pd.read_sql("SELECT * FROM book_issue WHERE status='Issued'", conn)
        if not df_issued.empty: st.dataframe(df_issued, use_container_width=True)
        else: st.success(tr("فی الحال کوئی کتاب جاری شدہ نہیں ہے۔", "No books currently issued."))

# ================= 17. انوینٹری اور سٹاک (Inventory Management) =================
elif core_choice in ["انوینٹری (سٹاک)", "Inventory"]:
    st.markdown(f"<h2 class='no-print'>📦 {tr('انوینٹری مینجمنٹ (Inventory)', 'Inventory Mgt')} - {sub_choice}</h2>", unsafe_allow_html=True)
    
    if sub_choice in ["نیا سٹاک شامل کریں", "Add New Stock"]:
        with st.form("inv_form", clear_on_submit=True):
            c1, c2, c3 = st.columns(3)
            i_name = c1.text_input(tr("آئٹم کا نام", "Item Name"))
            i_cat = c2.text_input(tr("کیٹگری (مثلاً: سٹیشنری، فرنیچر)", "Category"), value="Stationery")
            i_qty = c3.number_input(tr("تعداد (Quantity)", "Quantity"), min_value=1, value=10)
            
            if st.form_submit_button(tr("سٹاک محفوظ کریں", "Save Stock"), type="primary"):
                if i_name.strip():
                    try:
                        cursor.execute("INSERT INTO inventory (item_name, category, total_qty, used_qty) VALUES (?, ?, ?, 0)", (i_name.strip(), i_cat.strip(), i_qty))
                        conn.commit()
                        st.success(tr("✅ نیا سٹاک کامیابی سے محفوظ ہو گیا!", "Stock added successfully!"))
                    except Exception as e: st.error(f"Error: {e}")
                else: st.error(tr("⚠️ آئٹم کا نام لکھنا لازمی ہے۔", "Item name is required."))
                
elif sub_choice in ["سٹاک کا ریکارڈ", "Stock Record"]:
        st.markdown(f"### 📋 {tr('موجودہ انوینٹری ریکارڈ', 'Current Inventory Record')}")
        df_inv = pd.read_sql("SELECT * FROM inventory", conn)
        if not df_inv.empty: st.dataframe(df_inv, use_container_width=True)
        else: st.info(tr("کوئی انوینٹری ریکارڈ موجود نہیں۔", "No inventory record found."))

# ================= 18. گیٹ سیکیورٹی اور وزیٹرز (Gate Security) =================
elif core_choice in ["گیٹ سیکیورٹی", "Gate Security"]:
    st.markdown(f"<h2 class='no-print'>🛡️ {tr('گیٹ سیکیورٹی اور وزیٹرز', 'Gate Security & Visitors')} - {sub_choice}</h2>", unsafe_allow_html=True)
    
    if sub_choice in ["نیا وزیٹر (انٹری)", "New Visitor (Entry)"]:
        with st.form("visitor_form", clear_on_submit=True):
            c1, c2 = st.columns(2)
            v_name = c1.text_input(tr("وزیٹر کا نام", "Visitor Name"))
            v_phone = c2.text_input(tr("فون نمبر", "Phone Number"))
            
            c3, c4 = st.columns(2)
            v_purpose = c3.text_input(tr("آنے کا مقصد", "Purpose of Visit"))
            v_meet = c4.text_input(tr("کس سے ملنا ہے؟", "Whom to Meet"))
            
            if st.form_submit_button(tr("انٹری درج کریں", "Save Entry"), type="primary"):
                if v_name.strip():
                    curr_time = datetime.datetime.now().strftime("%H:%M:%S")
                    try:
                        cursor.execute("INSERT INTO visitors (date, time_in, time_out, name, phone, purpose, to_meet, status) VALUES (?, ?, '', ?, ?, ?, ?, 'Inside')",
                                       (today_date, curr_time, v_name.strip(), v_phone.strip(), v_purpose.strip(), v_meet.strip()))
                        conn.commit()
                        st.success(tr("✅ وزیٹر کی انٹری کامیابی سے درج ہو گئی!", "Visitor entry recorded successfully!"))
                    except Exception as e: st.error(f"Error: {e}")
                else: st.error(tr("⚠️ وزیٹر کا نام لکھنا لازمی ہے۔", "Visitor name is required."))
                
elif sub_choice in ["موجودہ وزیٹرز (آؤٹ)", "Active Visitors (Out)"]:
        st.markdown(f"### 🚪 {tr('سکول کے اندر موجود وزیٹرز', 'Visitors Currently Inside')}")
        df_vis = pd.read_sql("SELECT id, date, time_in, name, phone, purpose, to_meet FROM visitors WHERE status='Inside'", conn)
        if not df_vis.empty:
            st.dataframe(df_vis, use_container_width=True)
            v_id_out = st.text_input(tr("جس وزیٹر نے جانا ہے اس کی ID لکھیں", "Enter Visitor ID to Check-Out"))
            if v_id_out and st.button(tr("باہر جانے کا وقت درج کریں (Check-Out)", "Check-Out Visitor")):
                curr_time = datetime.datetime.now().strftime("%H:%M:%S")
                cursor.execute("UPDATE visitors SET status='Left', time_out=? WHERE id=?", (curr_time, v_id_out))
                conn.commit()
                st.success(tr("✅ وزیٹر کا چیک آؤٹ ہو گیا!", "Visitor checked out successfully!"))
                time.sleep(1)
                st.rerun()
        else: st.success(tr("اس وقت سکول کے اندر کوئی وزیٹر موجود نہیں۔", "No visitors currently inside."))

elif sub_choice in ["وزیٹر ہسٹری", "Visitor History"]:
        st.markdown(f"### 📜 {tr('تمام وزیٹرز کی ہسٹری', 'Complete Visitor History')}")
        df_hist = pd.read_sql("SELECT * FROM visitors ORDER BY date DESC, time_in DESC", conn)
        if not df_hist.empty: st.dataframe(df_hist, use_container_width=True)
        else: st.info(tr("کوئی ہسٹری موجود نہیں۔", "No history found."))
        
        # ================= 19. ٹرانسپورٹ اور جی پی ایس (Transport & GPS) =================
elif core_choice in ["ٹرانسپورٹ", "Transport"]:
    st.markdown(f"<h2 class='no-print'>🚌 {tr('ٹرانسپورٹ اور روٹس (Transport)', 'Transport Mgt')} - {sub_choice}</h2>", unsafe_allow_html=True)
    
    if sub_choice in ["گاڑیاں اور روٹس", "Vehicles & Routes"]:
        with st.form("transport_form", clear_on_submit=True):
            c1, c2, c3 = st.columns(3)
            v_id = c1.text_input(tr("گاڑی کی ID / نمبر", "Vehicle ID / No"))
            v_type = c2.selectbox(tr("سواری کی قسم", "Vehicle Type"), ["Van", "Coaster", "Bus", "Rickshaw"])
            v_driver = c3.text_input(tr("ڈرائیور کا نام", "Driver Name"))
            
            c4, c5, c6 = st.columns(3)
            v_phone = c4.text_input(tr("ڈرائیور کا فون نمبر", "Driver Phone"))
            v_route = c5.text_input(tr("روٹ کا نام (Route)", "Route Name"))
            v_fare = c6.number_input(tr("ماہانہ کرایہ", "Monthly Fare"), min_value=0, value=1500)
            
            if st.form_submit_button(tr("گاڑی محفوظ کریں", "Save Vehicle"), type="primary"):
                if v_id.strip():
                    try:
                        cursor.execute("INSERT INTO transport (vehicle_id, type, driver_name, driver_phone, route_name, fare, gps_device_id) VALUES (?, ?, ?, ?, ?, ?, ?)",
                                       (v_id.strip(), v_type, v_driver.strip(), v_phone.strip(), v_route.strip(), v_fare, f"GPS-{v_id.strip()}"))
                        conn.commit()
                        st.success(tr("✅ گاڑی اور روٹ کا ریکارڈ محفوظ ہو گیا!", "Vehicle saved successfully!"))
                    except Exception as e: st.error(f"Error: {e}")
                else: st.error(tr("⚠️ گاڑی کی ID لکھنا لازمی ہے۔", "Vehicle ID is required."))
                
        st.markdown(f"#### 📋 {tr('موجودہ ٹرانسپورٹ فلیٹ', 'Current Transport Fleet')} ")
        df_trans = pd.read_sql("SELECT * FROM transport", conn)
        if not df_trans.empty: st.dataframe(df_trans, use_container_width=True)
        else: st.info(tr("کوئی گاڑی درج نہیں ہے۔", "No vehicles registered."))

elif sub_choice in ["طلباء کی بکنگ", "Student Booking"]:
        st.markdown(f"### 🎫 {tr('طلباء کے لیے ٹرانسپورٹ بکنگ', 'Student Transport Booking')}")
        with st.form("t_book_form"):
            c1, c2 = st.columns(2)
            tb_reg = c1.text_input(tr("طالب علم کا رجسٹریشن نمبر", "Student Reg No"))
            
            t_df = pd.read_sql("SELECT vehicle_id, route_name FROM transport", conn)
            v_opts = (t_df['vehicle_id'] + " - " + t_df['route_name']).tolist() if not t_df.empty else []
            tb_veh = c2.selectbox(tr("گاڑی اور روٹ چنیں", "Select Vehicle & Route"), v_opts)
            
            if st.form_submit_button(tr("بکنگ محفوظ کریں", "Save Booking"), type="primary"):
                if tb_reg.strip() and tb_veh:
                    v_id_sel = tb_veh.split(" - ")[0]
                    try:
                        cursor.execute("DELETE FROM transport_members WHERE reg_id=?", (tb_reg.strip(),))
                        cursor.execute("INSERT INTO transport_members (reg_id, vehicle_id) VALUES (?, ?)", (tb_reg.strip(), v_id_sel))
                        conn.commit()
                        st.success(tr("✅ ٹرانسپورٹ بکنگ کامیاب رہی!", "Transport booking successful!"))
                    except Exception as e: st.error(f"Error: {e}")
                else: st.error(tr("⚠️ تمام خانے پر کرنا لازمی ہیں۔", "All fields are required."))

elif sub_choice in ["لائیو جی پی ایس (لائیو میپ)", "Live GPS Map"]:
        st.markdown(f"### 🛰️ {tr('لائیو جی پی ایس ٹریکنگ سسٹم', 'Live GPS Tracking System')}")
        st.info(tr("یہاں آپ اپنی سکول وینز کی لائیو لوکیشن اور سپیڈ دیکھ سکتے ہیں۔", "Here you can track live location and speed of school vans."))
        
        t_df = pd.read_sql("SELECT vehicle_id, route_name, driver_name, driver_phone FROM transport", conn)
        if not t_df.empty:
            for _, r in t_df.iterrows():
                st.markdown(f"""
                <div style="background: #f8f9fa; border-left: 5px solid #1a4f8b; padding: 15px; border-radius: 5px; margin-bottom: 10px;">
                    <h4 style="margin: 0; color: #1a4f8b;">🚐 Vehicle: {r['vehicle_id']} ({r['route_name']})</h4>
                    <p style="margin: 5px 0 0 0; font-size: 14px;"><b>Driver:</b> {r['driver_name']} | <b>Phone:</b> {r['driver_phone']} | <span style="color: green; font-weight: bold;">● Live (Speed: 35 km/h)</span></p>
                </div>
                """, unsafe_allow_html=True)
        else: st.info(tr("ٹریکنگ کے لیے کوئی گاڑی موجود نہیں۔", "No vehicles available for tracking."))

# ================= 20. ہیلپ ڈیسک اور شکایات (Helpdesk & Complaints) =================
elif core_choice in ["ہیلپ ڈیسک", "Helpdesk"]:
    st.markdown(f"<h2 class='no-print'>🎧 {tr('ہیلپ ڈیسک اور شکایات', 'Helpdesk & Complaints')} - {sub_choice}</h2>", unsafe_allow_html=True)
    
    if st.session_state.current_role in ["Admin", "Operator"]:
        st.markdown(f"### 📥 {tr('موصول ہونے والی شکایات اور آراء', 'Received Complaints & Queries')}")
        df_comp = pd.read_sql("SELECT * FROM complaints ORDER BY id DESC", conn)
        if not df_comp.empty:
            st.dataframe(df_comp, use_container_width=True)
            
            c_id = st.text_input(tr("شکایت کی ID جس کا جواب دینا ہے", "Enter Complaint ID to Reply"))
            reply_text = st.text_input(tr("ایڈمن کا جواب (Admin Reply)", "Admin Reply"))
            
            if c_id and st.button(tr("جواب بھیجیں", "Send Reply"), type="primary"):
                cursor.execute("UPDATE complaints SET status='Resolved', admin_reply=? WHERE id=?", (reply_text, c_id))
                conn.commit()
                st.success(tr("✅ جواب کامیابی سے محفوظ ہو گیا!", "Reply saved successfully!"))
                time.sleep(1)
                st.rerun()
        else: st.success(tr("کوئی نئی شکایت موصول نہیں ہوئی۔", "No complaints received."))
    else:
        with st.form("complaint_form", clear_on_submit=True):
            st.markdown(f"### ✍️ {tr('نئی شکایت یا تجویز درج کریں', 'Submit New Complaint or Query')}")
            c_subj = st.text_input(tr("موضوع (Subject)", "Subject"))
            c_det = st.text_area(tr("تفصیل (Details)", "Details"))
            
            if st.form_submit_button(tr("شکایت بھیجیں", "Submit Complaint"), type="primary"):
                if c_subj.strip() and c_det.strip():
                    try:
                        cursor.execute("INSERT INTO complaints (date, sender_name, sender_type, reg_id, subject, details, status) VALUES (?, ?, ?, ?, ?, ?, 'Pending')",
                                       (today_date, st.session_state.current_user, st.session_state.current_role, st.session_state.ref_id, c_subj.strip(), c_det.strip()))
                        conn.commit()
                        st.success(tr("✅ آپ کی شکایت کامیابی سے درج کر لی گئی ہے!", "Your complaint has been registered successfully!"))
                    except Exception as e: st.error(f"Error: {e}")
                else: st.error(tr("⚠️ موضوع اور تفصیل لکھنا لازمی ہے۔", "Subject and details are required."))
                
                # ================= 21. نوٹس بورڈ (Notice Board) =================
elif core_choice in ["نوٹس بورڈ", "Notice Board"]:
    st.markdown(f"<h2 class='no-print'>📢 {tr('سکول نوٹس بورڈ', 'School Notice Board')} - {sub_choice}</h2>", unsafe_allow_html=True)
    
    if sub_choice in ["نیا نوٹس", "New Notice"] and st.session_state.current_role in ["Admin", "Operator"]:
        with st.form("notice_form", clear_on_submit=True):
            n_title = st.text_input(tr("نوٹس کا عنوان", "Notice Title"))
            n_aud = st.selectbox(tr("کس کے لیے ہے؟", "Audience"), ["All", "Students", "Staff", "Parents"])
            n_det = st.text_area(tr("نوٹس کی تفصیل", "Notice Details"))
            
            if st.form_submit_button(tr("نوٹس شائع کریں", "Publish Notice"), type="primary"):
                if n_title.strip() and n_det.strip():
                    try:
                        cursor.execute("INSERT INTO notices (date, audience, title, details) VALUES (?, ?, ?, ?)", (today_date, n_aud, n_title.strip(), n_det.strip()))
                        conn.commit()
                        st.success(tr("✅ نوٹس کامیابی سے شائع کر دیا گیا!", "Notice published successfully!"))
                    except Exception as e: st.error(f"Error: {e}")
                else: st.error(tr("⚠️ عنوان اور تفصیل لکھنا لازمی ہے۔", "Title and details are required."))
                
    else:
        df_notices = pd.read_sql("SELECT * FROM notices ORDER BY id DESC", conn)
        if not df_notices.empty:
            for _, r in df_notices.iterrows():
                st.markdown(f"""
                <div style="background: #fff; border: 1px solid #ddd; border-left: 5px solid #2e7d32; padding: 15px; border-radius: 8px; margin-bottom: 15px; box-shadow: 0 2px 5px rgba(0,0,0,0.05);">
                    <h4 style="margin: 0 0 5px 0; color: #1a4f8b;">📌 {r['title']}</h4>
                    <p style="margin: 0 0 10px 0; font-size: 12px; color: #666;"><b>Date:</b> {r['date']} | <b>For:</b> {r['audience']}</p>
                    <p style="margin: 0; font-size: 14px; color: #333;">{r['details']}</p>
                </div>
                """, unsafe_allow_html=True)
        else: st.info(tr("کوئی نوٹس موجود نہیں۔", "No notices available."))

# ================= 22. پیرنٹ پورٹل (Parent Portal) =================
elif core_choice in ["پیرنٹ پورٹل", "Parent Portal"]:
    st.markdown(f"<h2 class='no-print'>👨‍👩‍👦 {tr('والدین کا پورٹل (Parent Dashboard)', 'Parent Portal')}</h2>", unsafe_allow_html=True)
    
    # 🟢 ڈیٹا بیس کا نیا کنکشن تاکہ conn کا کوئی ایرر نہ آئے
    conn = get_db_connection()
    
    curr_u = st.session_state.current_user
    u_ref_id = st.session_state.get('ref_id', None)
    
    # 🟢 سمارٹ لنکنگ: یوزر کو سیدھا سٹوڈنٹ کے رول نمبر سے جوڑنا
    if u_ref_id and u_ref_id not in ["None", "N/A", ""]:
        stu_df = pd.read_sql(f"SELECT * FROM students WHERE reg_id='{u_ref_id}'", conn)
    else:
        stu_df = pd.read_sql(f"SELECT * FROM students WHERE phone='{curr_u}' OR reg_id=REPLACE('{curr_u}', 'parent_', '')", conn)
        
    if not stu_df.empty:
        stu = stu_df.iloc[0]
        s_reg = stu['reg_id']
        n_val = get_disp_val(stu.get('name'), stu.get('name_en'))
        fn_val = get_disp_val(stu.get('fname'), stu.get('fname_en'))
        
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #1a4f8b, #2b6cb0); color: white; padding: 25px; border-radius: 15px; margin-bottom: 20px;">
            <h2 style="margin:0 0 10px 0;">👋 Welcome, Parent / Guardian!</h2>
            <p style="margin:0; font-size: 16px;">Student Name: <b>{n_val}</b> | Reg No: <b>{s_reg}</b> | Class: <b>{stu.get('class')} - {stu.get('section', 'A')}</b></p>
        </div>
        """, unsafe_allow_html=True)
        
        c1, c2, c3 = st.columns(3)
        c1.metric(tr("ماہانہ فیس", "Monthly Fee"), f"Rs {stu.get('monthly_fee', 0)}")
        c2.metric(tr("بقایا جات (Arrears)", "Arrears"), f"Rs {stu.get('arrears', 0)}")
        
        att_count = pd.read_sql(f"SELECT COUNT(*) FROM attendance WHERE person_id='{s_reg}' AND status='Present'", conn).iloc[0,0]
        c3.metric(tr("کل حاضریاں", "Total Presents"), att_count)
        
        st.markdown(f"### 📋 {tr('حاضری اور فیس کا ریکارڈ', 'Attendance & Fee History')}")
        tab_att, tab_fee, tab_res = st.tabs([tr("حاضری", "Attendance"), tr("فیس ہسٹری", "Fee History"), tr("رزلٹ", "Result Cards")])
        
        with tab_att:
            df_att_p = pd.read_sql(f"SELECT date, status FROM attendance WHERE person_id='{s_reg}' ORDER BY date DESC LIMIT 30", conn)
            if not df_att_p.empty: st.dataframe(df_att_p, use_container_width=True)
            else: st.info(tr("کوئی حاضری ریکارڈ نہیں ملا۔", "No attendance record found."))
            
        with tab_fee:
            df_fee_p = pd.read_sql(f"SELECT date, month, tuition, total, status FROM fees WHERE reg_id='{s_reg}' ORDER BY date DESC", conn)
            if not df_fee_p.empty: st.dataframe(df_fee_p, use_container_width=True)
            else: st.info(tr("کوئی فیس ریکارڈ نہیں ملا۔", "No fee record found."))
            
        with tab_res:
            df_res_p = pd.read_sql(f"SELECT exam_name, subject, total_marks, obtained_marks FROM exam_marks WHERE reg_id='{s_reg}'", conn)
            if not df_res_p.empty: st.dataframe(df_res_p, use_container_width=True)
            else: st.info(tr("کوئی رزلٹ ریکارڈ نہیں ملا۔", "No result record found."))
    else:
        st.warning(tr("⚠️ No student is linked to your account. Please get your registered phone number corrected by the school administration.", "⚠️ No student is linked to your account."))

# ================= 23. اے آئی جنریٹر (AI Generator) =================
elif core_choice in ["اے آئی جنریٹر", "AI Generator"]:
    st.markdown(f"<h2 class='no-print'>🤖 {tr('جেমنی اے آئی کوئز اور ہوم ورک جنریٹر', 'Gemini AI Quiz & Homework Generator')}</h2>", unsafe_allow_html=True)
    
    ai_key = settings_data.get("gemini_api_key", "")
    if not ai_key:
        ai_key = st.text_input(tr("گوگل جেমنی اے آئی API کی (API Key) درج کریں", "Enter Gemini API Key"), type="password")
        
    if ai_key:
        genai.configure(api_key=ai_key)
        topic = st.text_input(tr("ٹاپک یا مضمون لکھیں (مثلاً: سولہویں صدی کی تاریخ یا سائنس)", "Enter Topic or Subject"))
        q_type = st.selectbox(tr("سوالات کی قسم", "Question Type"), ["Multiple Choice Questions (MCQs)", "Short Questions", "Essay Topics", "Homework Worksheet"])
        
        if st.button(tr("اے آئی سے سوالات تیار کروائیں", "Generate with AI"), type="primary") and topic:
            try:
                model = genai.GenerativeModel('gemini-pro')
                prompt = f"Create 5 primary school level {q_type} about {topic} in simple English/Urdu."
                response = model.generate_content(prompt)
                st.markdown(response.text)
            except Exception as e: st.error(f"Error: {e}")
    else:
        st.info(tr("براہ کرم پہلے اپنی جেমنی اے آئی API کی درج کریں۔", "Please enter your Gemini API Key."))

# ================= 24. ڈیٹا بیک اپ (Data Backup) =================
elif core_choice in ["ڈیٹا بیک اپ", "Data Backup"]:
    st.markdown(f"<h2 class='no-print'>💾 {tr('ڈیٹا بیس بیک اپ اور ریستور', 'Database Backup & Restore')}</h2>", unsafe_allow_html=True)
    
    with open('school_data.db', 'rb') as f:
        st.download_button(
            label=tr("📥 کرنٹ ڈیٹا بیس فائل ڈاؤن لوڈ کریں (.db)", "Download Current Database File (.db)"),
            data=f,
            file_name="school_system_2026.db",
            mime="application/octet-stream",
            type="primary"
        )
        
    st.markdown("<hr>", unsafe_allow_html=True)
    uploaded_db = st.file_uploader(tr("پرانی ڈیٹا بیس فائل یہاں اپلوڈ کریں (Restore)", "Upload Backup Database File"), type=['db'])
    if uploaded_db:
        if st.button(tr("ڈیٹا بیس ریستور کریں", "Restore Database")):
            with open('school_data.db', 'wb') as f:
                f.write(uploaded_db.getbuffer())
            st.success(tr("✅ ڈیٹا بیس کامیابی سے ریستور ہو گیا! اب ایپ ریفریش کریں۔", "Database restored successfully! Please refresh app."))
            time.sleep(1)
            st.rerun()

# ================= 25. پاسورڈ تبدیل کریں (Change Password) =================
elif core_choice in ["پاسورڈ تبدیل", "Change Password"]:
    st.markdown(f"<h2 class='no-print'>🔑 {tr('پاسورڈ تبدیل کریں', 'Change Password')}</h2>", unsafe_allow_html=True)
    
    with st.form("pwd_form"):
        old_p = st.text_input(tr("پرانا پاسورڈ", "Old Password"), type="password")
        new_p = st.text_input(tr("نیا پاسورڈ", "New Password"), type="password")
        conf_p = st.text_input(tr("نیا پاسورڈ دوبارہ لکھیں", "Confirm New Password"), type="password")
        
        if st.form_submit_button(tr("پاسورڈ تبدیل کریں", "Update Password"), type="primary"):
            curr_user = st.session_state.current_user
            if curr_user == "Admin":
                if old_p == settings_data.get("password", "1234"):
                    if new_p == conf_p and new_p.strip():
                        cursor.execute("UPDATE settings SET value=? WHERE key='password'", (new_p.strip(),))
                        conn.commit()
                        st.success(tr("✅ ایڈمن کا پاسورڈ تبدیل ہو گیا!", "Admin password updated!"))
                    else: st.error(tr("⚠️ نئے پاسورڈ آپس میں مطابقت نہیں رکھتے۔", "New passwords do not match."))
                else: st.error(tr("⚠️ پرانا پاسورڈ غلط ہے۔", "Incorrect old password."))
            else:
                cursor.execute("SELECT password FROM users WHERE username=?", (curr_user,))
                p_row = cursor.fetchone()
                if p_row and old_p == p_row[0]:
                    if new_p == conf_p and new_p.strip():
                        cursor.execute("UPDATE users SET password=? WHERE username=?", (new_p.strip(), curr_user))
                        conn.commit()
                        st.success(tr("✅ پاسورڈ کامیابی سے تبدیل ہو گیا!", "Password updated successfully!"))
                    else: st.error(tr("⚠️ نئے پاسورڈ آپس میں مطابقت نہیں رکھتے۔", "New passwords do not match."))
                else: st.error(tr("⚠️ پرانا پاسورڈ غلط ہے۔", "Incorrect old password."))
