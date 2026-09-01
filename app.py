import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# ==================== تنظیمات صفحه ====================
st.set_page_config(
    page_title="DiaCare AI | سامانه خودمراقبتی دیابت",
    page_icon="🩺",
    layout="wide"
)

# ==================== راه‌اندازی دیتابیس آمار ====================
def init_db():
    conn = sqlite3.connect('analytics.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS visits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            action_type TEXT,
            diabetes_type TEXT,
            blood_sugar INTEGER
        )
    ''')
    conn.commit()
    conn.close()

def log_event(action_type, diabetes_type="-", blood_sugar=0):
    try:
        conn = sqlite3.connect('analytics.db')
        c = conn.cursor()
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        c.execute('''
            INSERT INTO visits (timestamp, action_type, diabetes_type, blood_sugar)
            VALUES (?, ?, ?, ?)
        ''', (now, action_type, diabetes_type, blood_sugar))
        conn.commit()
        conn.close()
    except Exception as e:
        pass

def get_stats():
    conn = sqlite3.connect('analytics.db')
    df = pd.read_sql_query("SELECT * FROM visits ORDER BY id DESC", conn)
    conn.close()
    return df

# اجرای اولیه دیتابیس
init_db()

# ثبت ورود به صفحه در هر نشست (Session)
if 'visited' not in st.session_state:
    st.session_state['visited'] = True
    log_event("ورود به سایت")

# ==================== منوی کناری و بخش مدیریت ====================
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2966/2966327.png", width=70)
    st.title("پنل دسترسی")
    menu = st.radio("انتخاب بخش:", ["صفحه اصلی (سامانه دیابت)", "پنل مدیریت و آمار"])

# ==================== ۱. صفحه اصلی سامانه دیابت ====================
if menu == "صفحه اصلی (سامانه دیابت)":
    st.title("🩺 سامانه هوشمند خودمراقبتی بیماران دیابتی (DiaCare AI)")
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        age = st.number_input("سن:", min_value=1, max_value=120, value=45)
        diabetes_type = st.selectbox("نوع دیابت:", ["دیابت نوع ۱", "دیابت نوع ۲", "دیابت بارداری", "پیش‌دیابت"])
        blood_sugar = st.number_input("میزان قند خون ناشتا (mg/dL):", min_value=40, max_value=500, value=110)
        
    with col2:
        activity_level = st.selectbox("سطح فعالیت بدنی:", ["کم (بی‌تحرک)", "متوسط (۱ تا ۳ روز در هفته)", "زیاد (بیش از ۳ روز در هفته)"])
        symptoms = st.multiselect("علائم تجربه شده اخیر:", ["تشنگی مفرط", "تکرر ادرار", "خستگی مداوم", "تاری دید", "سرگیجه", "کاهش وزن ناگهانی"])

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button(" دریافت توصیه‌های خودمراقبتی", type="primary"):
        # ثبت رویداد دریافت توصیه در دیتابیس
        log_event("دریافت توصیه خودمراقبتی", diabetes_type, blood_sugar)
        
        st.success(" اطلاعات با موفقیت تحلیل شد. توصیه‌های اختصاصی شما:")
        
        # منطق توصیه‌ها
        t1, t2, t3 = st.tabs([" تغذیه و رژیم", " فعالیت بدنی", " هشدارهای مراقبتی"])
        
        with t1:
            if blood_sugar > 130:
                st.warning("⚠️ قند خون شما بالاتر از حد نرمال است. مصرف کربوهیدرات‌های ساده (قند، شکر، نان سفید) را محدود کرده و مصرف فیبر و سبزیجات را افزایش دهید.")
            else:
                st.info(" وضعیت قند خون شما در محدوده مناسب است. رژیم غذایی متعادل با شاخص گلیسمی پایین را حفظ کنید.")
                
        with t2:
            if activity_level == "کم (بی‌تحرک)":
                st.info("🏃‍♂️ شروع پیاده‌روی روزانه به مدت ۲۰ تا ۳۰ دقیقه می‌تواند حساسیت به انسولین را به میزان چشمگیری بهبود دهد.")
            else:
                st.success(" ادامه فعالیت بدنی منظم به کنترل قند خون و سلامت قلب شما کمک شایانی می‌کند.")
                
        with t3:
            if "تاری دید" in symptoms or "سرگیجه" in symptoms:
                st.error("🚨 با توجه به علائم گزارش شده، توصیه اکید می‌شود در اولین فرصت به پزشک معالج خود مراجعه نمایید.")
            else:
                st.info(" رعایت نظم در مصرف داروها و چکاپ دوره‌ای هر ۳ ماه یک‌بار (آزمایش HbA1c) الزامی است.")

# ==================== ۲. پنل مدیریت و آمار بازدید ====================
elif menu == "پنل مدیریت و آمار":
    st.title("📊 پنل مدیریت و آمار استفاده از سامانه")
    st.markdown("---")
    
    password = st.text_input("رمز عبور مدیریت را وارد کنید:", type="password")
    
    # رمز عبور پیش‌فرض: admin123 (می‌توانید تغییر دهید)
    if password == "admin123":
        st.success("ورود موفقیت‌آمیز بود.")
        
        df_stats = get_stats()
        
        total_visits = len(df_stats)
        total_recommendations = len(df_stats[df_stats['action_type'] == "دریافت توصیه خودمراقبتی"])
        
        # نمایش کارت‌های آماری
        m1, m2 = st.columns(2)
        m1.metric(label="👥 کل بازدیدها / تعاملات", value=total_visits)
        m2.metric(label="📝 دفعات استفاده از فرم و دریافت توصیه", value=total_recommendations)
        
        st.markdown("### 📋 جدول لاگ و تاریخچه استفاده")
        st.dataframe(df_stats, use_container_width=True)
        
        # دکمه خروجی CSV / اکسل
        csv = df_stats.to_csv(index=False).encode('utf-8-sig')
        st.download_button(
            label="📥 دانلود فایل خروجی (CSV / اکسل)",
            data=csv,
            file_name=f"diacare_usage_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
            type="primary"
        )
    elif password != "":
        st.error("❌ رمز عبور نادرست است!")
