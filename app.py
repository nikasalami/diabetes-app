import streamlit as st
import pandas as pd
from datetime import datetime
import requests

# ================= تنظیمات صفحه =================
st.set_page_config(
    page_title="DiaCare AI | سامانه خود‌مراقبتی دیابت",
    page_icon="🩺",
    layout="wide"
)

# ================= لینک وب‌هوک گوگل‌شیت =================
GOOGLE_SHEET_URL = "https://script.google.com/macros/s/AKfycbzCLMcPY7EkaoI9JPn4zLyN7az4fzMPZGL4tZJwTQ7Pa54z61BUX1BJXSaFbdE-GUXn/exec"

# ================= شمارنده کلیک و نشست کاربر =================
if "click_count" not in st.session_state:
    st.session_state.click_count = 0

def send_to_google_sheet(gender, received_advice, click_count, diabetes_info):
    """ارسال داده‌ها متناسب با ستون‌های گوگل‌شیت"""
    try:
        data = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "gender": gender,
            "received_advice": received_advice,
            "click_count": click_count,
            "diabetes_info": diabetes_info
        }
        requests.post(GOOGLE_SHEET_URL, json=data, timeout=5)
    except Exception:
        pass

# ================= منوی کناری =================
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2854/2854341.png", width=100)
    st.title("DiaCare AI")
    st.markdown("**سامانه هوشمند پایش و خودمراقبتی دیابت**")
    st.markdown("---")
    menu = st.radio("بخش‌های سامانه:", ["صفحه اصلی و ارزیابی", "درباره سامانه"])
    st.markdown("---")
    st.caption("بر اساس راهنماهای بالینی خودمراقبتی")

# ================= ۱. صفحه اصلی و ارزیابی =================
if menu == "صفحه اصلی و ارزیابی":
    st.markdown("<h2 style='text-align: right; color: #1E88E5;'>🩺 سامانه توصیه‌گر هوشمند خودمراقبتی دیابت</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: right; color: #555;'>لطفاً اطلاعات بالینی و فردی خود را وارد نمایید تا توصیه‌های متناسب شخصی‌سازی‌شده را دریافت کنید.</p>", unsafe_allow_html=True)
    st.write("")

    col1, col2 = st.columns(2)
    
    with col1:
        gender = st.radio("جنسیت:", ["زن", "مرد"], horizontal=True)
        age = st.number_input("سن (سال):", min_value=10, max_value=100, value=45)
        diabetes_type = st.selectbox("نوع دیابت:", ["دیابت نوع ۲", "دیابت نوع ۱", "پره‌دیابت (پیش‌دیابت)"])
        fbs = st.number_input("قند خون ناشتا (mg/dL):", min_value=50, max_value=400, value=130)

    with col2:
        hba1c = st.number_input("هموگلوبین A1c (درصد):", min_value=4.0, max_value=15.0, value=7.2, step=0.1)
        activity_level = st.selectbox("سطح فعالیت بدنی هفتگی:", ["کمتر از ۳۰ دقیقه (بی‌تحرک)", "۳۰ تا ۱۵۰ دقیقه (متوسط)", "بیش از ۱۵۰ دقیقه (فعال)"])
        foot_check = st.radio("آیا روزانه پاهای خود را بررسی می‌کنید؟", ["بله، مرتب بررسی می‌کنم", "خیر، یا گاهی اوقات"])
        medication_adherence = st.selectbox("مصرف منظم داروها/انسولین:", ["کاملاً منظم و سر وقت", "گاهی فراموش می‌کنم", "نامنظم"])

    st.markdown("---")
    
    if st.button("🔍 دریافت توصیه‌های شخصی‌سازی‌شده", type="primary", use_container_width=True):
        st.session_state.click_count += 1
        
        # اطلاعات تجمیعی جهت ثبت در ستون ۵
        diabetes_info_str = f"{diabetes_type} | قند ناشتا: {fbs} | هموگلوبین: {hba1c} | سن: {age}"
        
        # ارسال داده به گوگل شیت
        send_to_google_sheet(
            gender=gender,
            received_advice="بله",
            click_count=st.session_state.click_count,
            diabetes_info=diabetes_info_str
        )
        
        st.success("✅ ارزیابی بالینی با موفقیت انجام شد. توصیه‌های شخصی‌سازی‌شده زیر را مطالعه فرمایید:")
        
        # تحلیل وضعیت قند خون
        st.subheader("📊 تحلیل وضعیت کنترل قند:")
        if hba1c < 7.0 and fbs < 130:
            st.info("🟢 **وضعیت مطلوب:** شاخص‌های قند شما در محدوده هدف قرار دارد.")
        elif hba1c >= 7.0 and hba1c < 8.5:
            st.warning("🟡 **نیاز به بهبود:** قند خون شما بالاتر از حد ایده‌آل است.")
        else:
            st.error("🔴 **هشدار کنترل ضعیف:** سطح قند شما بالاست؛ نیاز به بازبینی دوز دارو توسط پزشک معالج دارید.")

        # توصیه‌های ۳ گانه
        c_rec1, c_rec2, c_rec3 = st.columns(3)
        with c_rec1:
            st.markdown("### 🥗 تغذیه و رژیم")
            st.write("• مصرف کربوهیدرات‌های ساده (قند و شیرینی) را محدود کنید.")
            st.write("• مصرف فیبر و سبزیجات تازه را در هر وعده افزایش دهید.")
        with c_rec2:
            st.markdown("### 🏃‍♂️ فعالیت بدنی")
            st.write("• حداقل ۱۵۰ دقیقه در هفته فعالیت بدنی با شدت متوسط داشته باشید.")
        with c_rec3:
            st.markdown("### 🦶 مراقبت از پا و داروها")
            st.write("• هر شب پاها را از لحاظ زخم یا قرمزی بازبینی کنید.")
            st.write("• داروها را رأس ساعت معین و منظم مصرف فرمایید.")

# ================= ۲. درباره سامانه =================
elif menu == "درباره سامانه":
    st.markdown("### 📖 درباره DiaCare AI")
    st.write("""
    این سامانه یک دستیار هوشمند خود‌مراقبتی جهت توانمندسازی بیماران مبتلا به دیابت و پیش‌دیابت است.
    هدف این ابزار ارتقای سواد سلامت و ارائه توصیه‌های مبتنی بر شواهد بالینی می‌باشد.
    """)

