import streamlit as st
import pandas as pd
from datetime import datetime
import requests
import uuid

# ================= تنظیمات صفحه =================
st.set_page_config(
    page_title="DiaCare AI | سامانه خود‌مراقبتی دیابت",
    page_icon="🩺",
    layout="wide"
)

# ================= لینک گوگل‌شیت اختصاصی شما =================
GOOGLE_SHEET_URL = "https://script.google.com/macros/s/AKfycbzCLMcPY7EkaoI9JPn4zLyN7az4fzMPZGL4tZJwTQ7Pa54z61BUX1BJXSaFbdE-GUXn/exec"

# ================= مدیریت شناسه کاربر و ثبت آمار =================
if "user_id" not in st.session_state:
    st.session_state.user_id = str(uuid.uuid4())[:8]

def send_to_google_sheet(action_name, detail=""):
    """ارسال امن آمار به گوگل‌شیت"""
    try:
        data = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "user_id": st.session_state.user_id,
            "action": action_name,
            "detail": detail
        }
        requests.post(GOOGLE_SHEET_URL, json=data, timeout=5)
    except Exception:
        pass  # جلوگیری از نمایش خطا به کاربر در صورت کندی اینترنت

# ثبت ورود در ابتدای باز شدن صفحه
if "has_logged_visit" not in st.session_state:
    st.session_state.has_logged_visit = True
    send_to_google_sheet("بازدید", "ورود کاربر به سامانه")

# ================= منوی کناری (سایدبار) =================
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2854/2854341.png", width=100)
    st.title("DiaCare AI")
    st.markdown("**سامانه هوشمند پایش و خودمراقبتی دیابت**")
    st.markdown("---")
    
    menu = st.radio(
        "بخش‌های سامانه:",
        ["صفحه اصلی و ارزیابی", "پنل مدیریت آمار", "درباره سامانه"]
    )
    st.markdown("---")
    st.caption("طراحی شده بر اساس راهنماهای بالینی خودمراقبتی")

# ================= ۱. صفحه اصلی و ارزیابی =================
if menu == "صفحه اصلی و ارزیابی":
    st.markdown("<h2 style='text-align: right; color: #1E88E5;'>🩺 سامانه توصیه‌گر هوشمند خودمراقبتی دیابت</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: right; color: #555;'>لطفاً اطلاعات بالینی و فردی خود را وارد نمایید تا توصیه‌های متناسب شخصی‌سازی‌شده را دریافت کنید.</p>", unsafe_allow_html=True)
    st.write("")

    col1, col2 = st.columns(2)
    
    with col1:
        age = st.number_input("سن (سال):", min_value=10, max_value=100, value=45)
        diabetes_type = st.selectbox("نوع دیابت:", ["دیابت نوع ۲", "دیابت نوع ۱", "پره‌دیابت (پیش‌دیابت)"])
        fbs = st.number_input("قند خون ناشتا (mg/dL):", min_value=50, max_value=400, value=130)
        hba1c = st.number_input("هموگلوبین A1c (درصد):", min_value=4.0, max_value=15.0, value=7.2, step=0.1)

    with col2:
        activity_level = st.selectbox("سطح فعالیت بدنی هفتگی:", ["کمتر از ۳۰ دقیقه (بی‌تحرک)", "۳۰ تا ۱۵۰ دقیقه (متوسط)", "بیش از ۱۵۰ دقیقه (فعال)"])
        foot_check = st.radio("آیا روزانه پاهای خود را بررسی می‌کنید؟", ["بله، مرتب بررسی می‌کنم", "خیر، یا گاهی اوقات"])
        medication_adherence = st.selectbox("مصرف منظم داروها/انسولین:", ["کاملاً منظم و سر وقت", "گاهی فراموش می‌کنم", "نامنظم"])

    st.markdown("---")
    
    if st.button("🔍 دریافت توصیه‌های شخصی‌سازی‌شده", type="primary", use_container_width=True):
        # ثبت رویداد دریافت توصیه در گوگل شیت
        send_to_google_sheet(
            "دریافت توصیه", 
            f"نوع: {diabetes_type} | FBS: {fbs} | HbA1c: {hba1c}"
        )
        
        st.success("✅ ارزیابی بالینی با موفقیت انجام شد. توصیه‌های زیر را با دقت مطالعه فرمایید:")
        
        # تحلیل قند خون
        st.subheader("📊 تحلیل وضعیت کنترل قند:")
        if hba1c < 7.0 and fbs < 130:
            st.info("🟢 **وضعیت مطلوب:** قند خون و HbA1c شما در محدوده هدف قرار دارد. این روند عالی را حفظ کنید.")
        elif hba1c >= 7.0 and hba1c < 8.5:
            st.warning("🟡 **نیاز به بهبود:** قند خون شما بالاتر از حد ایده‌آل است. اصلاح رژیم غذایی و پایبندی دارویی توصیه می‌شود.")
        else:
            st.error("🔴 **هشدار کنترل ضعیف:** سطح قند شما بالاست. حتماً در اسرع وقت جهت بازبینی دوز داروها به پزشک معالج مراجعه نمایید.")

        # توصیه‌های ۳ گانه خودمراقبتی
        c_rec1, c_rec2, c_rec3 = st.columns(3)
        
        with c_rec1:
            st.markdown("### 🥗 تغذیه و رژیم")
            st.write("• مصرف کربوهیدرات‌های ساده (شیرینی، قند، نان سفید) را محدود کنید.")
            st.write("• مصرف فیبر (سبزیجات تازه، حبوبات) را در هر وعده افزایش دهید.")
            st.write("• حجم وعده‌ها را کوچک و تعداد آن‌ها را بیشتر کنید.")

        with c_rec2:
            st.markdown("### 🏃‍♂️ فعالیت بدنی")
            if "بی‌تحرک" in activity_level:
                st.write("• روزانه با **۱۵ دقیقه پیاده‌روی سبک** شروع کنید و تدریجاً به ۳۰ دقیقه برسانید.")
            else:
                st.write("• حداقل **۱۵۰ دقیقه در هفته** ورزش هوازی با شدت متوسط (مانند پیاده‌روی تند) داشته باشید.")
            st.write("• از نشستن مداوم بیش از ۳۰ دقیقه خودداری کنید.")

        with c_rec3:
            st.markdown("### 🦶 مراقبت از پا و داروها")
            if "خیر" in foot_check:
                st.write("⚠️ **مهم:** هر شب پاهای خود را از نظر زخم، قرمزی یا ترک‌خوردگی بررسی کنید.")
            else:
                st.write("• پایش روزانه پاها را ادامه دهید و همیشه از جوراب‌های نخی و کفش مناسب استفاده کنید.")
            if medication_adherence != "کاملاً منظم و سر وقت":
                st.write("⚠️ داروها را رأس ساعت معین میل کنید؛ از آلارم گوشی برای یادآوری استفاده کنید.")

# ================= ۲. پنل مدیریت آمار =================
elif menu == "پنل مدیریت آمار":
    st.markdown("<h2 style='text-align: right;'>🔒 پنل مدیریت سامانه</h2>", unsafe_allow_html=True)
    admin_password = st.text_input("رمز عبور مدیر:", type="password")
    
    if admin_password == "admin123":
        st.success("ورود موفقیت‌آمیز به عنوان مدیر.")
        st.markdown("### 📈 پایگاه داده ابری (Google Sheets)")
        st.info("تمامی اطلاعات بازدیدها و درخواست‌های توصیه به صورت لحظه‌ای و پایدار در گوگل‌شیت ثبت می‌شوند.")
        
        st.markdown(f"🔗 **[برای مشاهده و دانلود کامل جدول داده‌ها اینجا کلیک کنید]({GOOGLE_SHEET_URL.replace('/exec', '')})**")
    elif admin_password:
        st.error("رمز عبور اشتباه است.")

# ================= ۳. درباره سامانه =================
elif menu == "درباره سامانه":
    st.markdown("### 📖 درباره DiaCare AI")
    st.write("""
    این سامانه یک دستیار هوشمند خود‌مراقبتی جهت توانمندسازی بیماران مبتلا به دیابت و پیش‌دیابت است.
    هدف این ابزار، ارتقای سواد سلامت، پایش مداوم شاخص‌ها و ارائه توصیه‌های مبتنی بر شواهد بالینی جهت پیشگیری از عوارض ثانویه دیابت می‌باشد.
    """)
