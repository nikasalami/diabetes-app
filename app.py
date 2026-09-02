import streamlit as st
import pandas as pd
from datetime import datetime
import requests

# ================= تنظیمات صفحه =================
st.set_page_config(
    page_title="DiaCare AI | سامانه خودمراقبتی هوشمند دیابت",
    page_icon="🩺",
    layout="wide"
)

# ================= آدرس وب‌هوک پیش‌فرض =================
DEFAULT_SHEET_URL = "https://script.google.com/macros/s/AKfycbzCLMcPY7EkaoI9JPn4zLyN7az4fzMPZGL4tZJwTQ7Pa54z61BUX1BJXSaFbdE-GUXn/exec"

if "google_sheet_url" not in st.session_state:
    st.session_state.google_sheet_url = DEFAULT_SHEET_URL

if "click_count" not in st.session_state:
    st.session_state.click_count = 0

if "form_submitted" not in st.session_state:
    st.session_state.form_submitted = False

if "user_info_summary" not in st.session_state:
    st.session_state.user_info_summary = ""

if "user_gender" not in st.session_state:
    st.session_state.user_gender = ""

def send_to_google_sheet(payload):
    """ارسال داده‌ها به وب‌هوک گوگل شیت"""
    url = st.session_state.google_sheet_url.strip()
    try:
        headers = {"Content-Type": "application/json"}
        response = requests.post(
            url,
            json=payload,
            headers=headers,
            allow_redirects=True,
            timeout=15
        )
        if response.status_code in [200, 302]:
            return True, "اطلاعات با موفقیت در گوگل‌شیت ثبت شد."
        else:
            return False, f"کد خطای سرور: {response.status_code}"
    except Exception as e:
        return False, f"خطا در ارتباط: {str(e)}"

# ================= استایل =================
st.markdown("""
<style>
    .main-title {text-align: right; color: #0D47A1; font-weight: bold; margin-bottom: 5px;}
    .sub-title {text-align: right; color: #546E7A; margin-bottom: 25px;}
    .section-header {background-color: #E3F2FD; padding: 8px 15px; border-radius: 8px; color: #0D47A1; font-weight: bold; margin-top: 15px; margin-bottom: 15px; text-align: right;}
    .feedback-box {background-color: #F1F8E9; border: 1px solid #AED581; padding: 20px; border-radius: 12px; margin-top: 30px;}
</style>
""", unsafe_allow_html=True)

# منوی کناری
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2854/2854341.png", width=90)
    st.title("DiaCare AI")
    st.markdown("**سامانه توصیه‌گر خودمراقبتی دیابت**")
    st.caption("مبتنی بر پرسشنامه استاندارد موج صفر")
    st.markdown("---")
    menu = st.radio("بخش‌های سامانه:", [
        "📝 تکمیل پرسشنامه و دریافت توصیه",
        "ℹ️ درباره طرح پژوهشی",
        "🔐 پنل مدیریت و تست اتصال"
    ])

# ================= ۱. فرم ارزیابی و دریافت توصیه‌ها =================
if menu == "📝 تکمیل پرسشنامه و دریافت توصیه":
    st.markdown("<h2 class='main-title'>🩺 سامانه توصیه‌گر هوشمند خودمراقبتی بیماران دیابتی</h2>", unsafe_allow_html=True)
    st.markdown("<p class='sub-title'>لطفاً پرسشنامه را تکمیل فرمایید تا سیستم توصیه‌های بالینی و خودمراقبتی اختصاصی شما را ارائه دهد.</p>", unsafe_allow_html=True)

    with st.form("diabetes_survey_form"):
        # بخش ۱: مشخصات فردی
        st.markdown("<div class='section-header'>👤 بخش ۱: مشخصات فردی و دموگرافیک</div>", unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            q1_name = st.text_input("۱. نام و نام خانوادگی یا نام مستعار (جهت خطاب):", value="کاربر گرامی")
            q3_gender = st.radio("۳. جنسیت:", ["زن", "مرد"], horizontal=True)
            q5_height = st.number_input("۵. قد (سانتی‌متر):", min_value=100, max_value=230, value=168)
        with c2:
            q2_phone = st.text_input("۲. شماره تلفن همراه (اختیاری):", value="")
            q4_age = st.number_input("۴. سن (سال):", min_value=10, max_value=100, value=48)
            q6_weight = st.number_input("۶. وزن فعلی (کیلوگرم):", min_value=30.0, max_value=200.0, value=74.0, step=0.5)

        bmi = round(q6_weight / ((q5_height / 100) ** 2), 1)

        # بخش ۲: وضعیت درمانی
        st.markdown("<div class='section-header'>💊 بخش ۲: سابقه و روش درمانی دیابت</div>", unsafe_allow_html=True)
        c3, c4 = st.columns(2)
        with c3:
            q7_type = st.selectbox("۷. نوع دیابت شما چیست؟", [
                "دیابت نوع ۲",
                "دیابت نوع ۱",
                "دیابت بارداری",
                "مطمئن نیستم / نمی‌دانم"
            ])
            q9_treatment = st.selectbox("۹. روش درمانی فعلی شما چیست؟", [
                "قرص‌های خوراکی (متفورمین، گلی‌بن‌کلامید، امپاگلیفلوزین و...)",
                "تزریق انسولین",
                "هم قرص خوراکی و هم انسولین",
                "فقط رژیم غذایی و ورزش (بدون دارو)"
            ])
        with c4:
            q8_duration = st.selectbox("۸. چند سال از تشخیص دیابت شما می‌گذرد؟", [
                "کمتر از ۱ سال",
                "۱ تا ۵ سال",
                "۵ تا ۱۰ سال",
                "بیش از ۱۰ سال"
            ])
            q10_comorbidities = st.multiselect("۱۰. بیماری‌های همراه:", [
                "فشار خون بالا",
                "چربی خون بالا",
                "سابقه بیماری قلبی - عروقی",
                "مشکلات کلیوی",
                "زخم پای دیابتی یا گزگز و بی‌حسی پا",
                "هیچ‌کدام"
            ], default=["هیچ‌کدام"])

        # بخش ۳: آزمایش‌ها
        st.markdown("<div class='section-header'>🧪 بخش ۳: وضعیت قند خون و آزمایش‌ها</div>", unsafe_allow_html=True)
        c5, c6 = st.columns(2)
        with c5:
            q11_fbs = st.selectbox("۱۱. میانگین قند خون ناشتای شما در دو هفته اخیر:", [
                "۷۰ تا ۱۳۰ (محدوده مطلوب)",
                "۱۳۰ تا ۱۸۰ (کمی بالاتر از حد هدف)",
                "بیشتر از ۱۸۰ (خیلی بالا)",
                "کمتر از ۷۰ (افت مکرر قند خون)",
                "قند ناشتا را نمی‌سنجم / اطلاعی ندارم"
            ])
            q13_hba1c = st.selectbox("۱۳. آخرین آزمایش هموگلوبین ای‌وان‌سی (HbA1c):", [
                "کمتر از ۷ درصد (کنترل مناسب)",
                "۷ تا ۸ درصد (کنترل متوسط)",
                "بیشتر از ۸ درصد (کنترل ضعیف)",
                "انجام نداده‌ام / نمی‌دانم"
            ])
        with c6:
            q12_ppg = st.selectbox("۱۲. میانگین قند خون ۲ ساعت بعد از غذا:", [
                "کمتر از ۱۸۰ (محدوده مطلوب)",
                "۱۸۰ تا ۲۵۰ (بالا)",
                "بیشتر از ۲۵۰ (خیلی بالا)",
                "نمی‌سنجم / اطلاعی ندارم"
            ])
            q14_hypo = st.selectbox("۱۴. آیا در یک ماه گذشته دچار افت قند شدید شده‌اید؟", [
                "خیر",
                "بله، یک یا دو بار",
                "بله، مکرراً (بیش از ۲ بار)"
            ])

        # بخش ۴: خودمراقبتی
        st.markdown("<div class='section-header'>🏃‍♂️ بخش ۴: خودمراقبتی و سبک زندگی</div>", unsafe_allow_html=True)
        c7, c8 = st.columns(2)
        with c7:
            q15_glucometer = st.selectbox("۱۵. چقدر از دستگاه قند سنج (گلوکومتر) استفاده می‌کنید؟", [
                "روزانه یک‌بار یا بیشتر",
                "چند بار در هفته",
                "فقط زمانی که حالم بد است",
                "اصلاً دستگاه ندارم / استفاده نمی‌کنم"
            ])
            q17_exercise = st.selectbox("۱۷. در طول هفته چند روز فعالیت بدنی (حداقل ۳۰ دقیقه) دارید؟", [
                "اصلاً یا کمتر از ۱ روز",
                "۱ تا ۲ روز در هفته",
                "۳ تا ۴ روز در هفته",
                "۵ روز یا بیشتر در هفته"
            ])
        with c8:
            q16_adherence = st.selectbox("۱۶. نحوه مصرف داروهای دیابت یا تزریق انسولین:", [
                "کاملاً منظم و دقیقاً طبق دستور",
                "گاهی فراموش می‌کنم (یک یا دو بار در هفته)",
                "اغلب فراموش می‌کنم یا نامنظم است"
            ])
            q18_diet = st.selectbox("۱۸. مصرف قندهای ساده، شیرینی‌جات و نوشیدنی‌های شیرین:", [
                "به‌ندرت یا اصلاً مصرف نمی‌کنم",
                "گاهی در طول هفته",
                "تقریباً هر روز"
            ])

        st.markdown("---")
        submit_btn = st.form_submit_button("🔍 ثبت اطلاعات و دریافت برنامه خودمراقبتی", use_container_width=True, type="primary")

    if submit_btn:
        st.session_state.click_count += 1
        st.session_state.form_submitted = True
        st.session_state.user_gender = q3_gender
        
        # ذخیره خلاصه پرونده
        summary = f"نوع: {q7_type} | درمان: {q9_treatment} | ناشتا: {q11_fbs} | HbA1c: {q13_hba1c} | BMI: {bmi}"
        st.session_state.user_info_summary = summary
        
        # ارسال به گوگل شیت
        payload = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "gender": q3_gender,
            "received_advice": "بله (توصیه دریافت شد)",
            "click_count": st.session_state.click_count,
            "diabetes_info": summary
        }
        send_to_google_sheet(payload)

    # نمایش توصیه‌ها پس از ثبت
    if st.session_state.form_submitted:
        st.success(f"✅ پرونده شما با موفقیت تحلیل شد و توصیه‌های خودمراقبتی آماده است.")
        
        # شاخص BMI
        c_bmi1, c_bmi2 = st.columns(2)
        with c_bmi1:
            st.metric("شاخص توده بدنی (BMI)", f"{bmi} kg/m²")
        with c_bmi2:
            if bmi < 18.5:
                st.warning("⚠️ کمبود وزن: نیاز به تقویت کالری دریافتی")
            elif 18.5 <= bmi <= 24.9:
                st.success("🟢 وزن نرمال و ایده‌آل")
            elif 25.0 <= bmi <= 29.9:
                st.warning("🟡 دارای اضافه‌وزن: رژیم متعادل توصیه می‌شود")
            else:
                st.error("🔴 چاقی: کاهش تدریجی وزن ضروری است")

        st.markdown("### 📋 بسته‌های توصیه‌گر بالینی شخصی‌سازی‌شده:")
        t1, t2, t3, t4 = st.tabs(["🥗 رژیم و تغذیه", "🏃‍♂️ فعالیت بدنی", "💊 داروها و پایش", "⚠️ هشدارها و پیگیری"])
        
        with t1:
            if "هر روز" in q18_diet:
                st.error("• مصرف قندهای ساده و نوشیدنی‌های شیرین را متوقف کرده و کربوهیدرات‌های پیچیده جایگزین کنید.")
            st.write("• بشقاب غذایی استاندارد: ۵۰٪ سبزیجات غیرنشاسته‌ای، ۲۵٪ پروتئین کم‌چرب و ۲۵٪ غلات کامل.")
            st.write("• مصرف نمک و چربی‌های اشباع را جهت محافظت از عروق و کلیه‌ها کاهش دهید.")

        with t2:
            if "اصلاً" in q17_exercise:
                st.warning("• فعالیت بدنی ناکافی است. روزانه با ۱۵ دقیقه پیاده‌روی شروع کنید و به ۳۰ دقیقه برسانید.")
            else:
                st.info("• هدف استاندارد: حداقل ۱۵۰ دقیقه پیاده‌روی سریع در هفته در جلسات ۳۰ دقیقه‌ای.")

        with t3:
            if "فراموش" in q16_adherence:
                st.error("• مصرف منظم دارو کلید پیشگیری از عوارض دیابت است. یادآور منظم تنظیم کنید.")
            if "اصلاً" in q15_glucometer or "فقط زمانی" in q15_glucometer:
                st.warning("• پایش دوره‌ای قند خون ناشتا و بعد از غذا را در برنامه هفتگی قرار دهید.")

        with t4:
            if "بله، مکرراً" in q14_hypo or "<۷۰" in q11_fbs:
                st.error("🚨 خطر افت قند خون: حتماً با پزشک معالج برای تنظیم دوز داروها مشورت کنید.")
            if "زخم پای دیابتی" in q10_comorbidities:
                st.error("🚨 مراقبت ویژه از پا: روزانه پاها را از نظر هرگونه خراش یا تغییر رنگ معاینه فرمایید.")
            st.info("• انجام منظم آزمایش HbA1c هر ۳ تا ۶ ماه یک‌بار الزامی است.")

        # ================= فرم جدید: سنجش رضایت و بازخورد =================
        st.markdown("---")
        st.markdown("### 🌟 نظرسنجی و ارزیابی سامانه هوشمند")
        st.write("پاسخ‌های شما به بهبود کیفیت سیستم و پژوهش کمک شایانی خواهد کرد:")

        with st.form("feedback_form"):
            fb_satisfaction = st.select_slider(
                "۱. چقدر از توصیه‌های ارائه‌شده توسط سامانه رضایت دارید؟",
                options=["خیلی کم / ناراضی", "کم", "متوسط", "زیاد", "بسیار عالی و کاربردی"],
                value="بسیار عالی و کاربردی"
            )
            
            fb_reuse = st.radio(
                "۲. آیا مایل هستید در آینده نیز از این سامانه جهت پایش خودمراقبتی استفاده کنید؟",
                ["بله، حتماً", "احتمالاً بله", "خیر"],
                horizontal=True
            )
            
            fb_comment = st.text_area(
                "۳. پیشنهادات، انتقادات یا نکاتی که برای بهبود سامانه به نظرتان می‌رسد را بنویسید:",
                placeholder="مثلاً: اضافه شدن یادآور پیامکی، توضیحات بیشتر درباره رژیم غذایی و..."
            )
            
            submit_feedback = st.form_submit_button("💌 ثبت نظر و ارسال بازخورد", use_container_width=True, type="primary")

        if submit_feedback:
            feedback_summary = f"رضایت: {fb_satisfaction} | استفاده مجدد: {fb_reuse} | پیشنهاد: {fb_comment.strip() if fb_comment.strip() else 'بدون متن'}"
            feedback_payload = {
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "gender": st.session_state.user_gender,
                "received_advice": "ثبت بازخورد و رضایت‌سنجی",
                "click_count": st.session_state.click_count,
                "diabetes_info": f"[بازخورد] {feedback_summary}"
            }
            fb_ok, fb_msg = send_to_google_sheet(feedback_payload)
            if fb_ok:
                st.balloons()
                st.success("🎉 با تشکر فراوان! بازخورد ارزشمند شما با موفقیت در پایگاه داده پژوهش ثبت گردید.")
            else:
                st.error(f"خطا در ثبت بازخورد: {fb_msg}")

# ================= ۲. درباره سامانه =================
elif menu == "ℹ️ درباره طرح پژوهشی":
    st.markdown("### 📘 درباره سامانه توصیه‌گر هوشمند DiaCare AI")
    st.write("""
    این پژوهش با هدف طراحی و ارزیابی سامانه تصمیم‌یار بالینی هوشمند (CDSS) جهت ارتقای رفتارهای خودمراقبتی و مدیریت بیماری در افراد مبتلا به دیابت انجام شده است.
    """)

# ================= ۳. پنل مدیریت پژوهشگر =================
elif menu == "🔐 پنل مدیریت و تست اتصال":
    st.markdown("<h2 class='main-title'>🔐 پنل مدیریت و تنظیمات اتصال</h2>", unsafe_allow_html=True)
    admin_pass = st.text_input("رمز عبور مدیر:", type="password")
    
    if admin_pass == "admin123":
        st.success("🔓 ورود موفقیت‌آمیز بود.")
        current_url = st.text_input("Google Webhook URL:", value=st.session_state.google_sheet_url)
        
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            if st.button("💾 ذخیره آدرس جدید", use_container_width=True):
                st.session_state.google_sheet_url = current_url.strip()
                st.success("✅ آدرس با موفقیت ذخیره شد.")
                
        with col_btn2:
            if st.button("🧪 ارسال داده تستی و بررسی اتصال", use_container_width=True, type="primary"):
                test_data = {
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "gender": "تست سیستم",
                    "received_advice": "بله",
                    "click_count": 999,
                    "diabetes_info": "تست ثبت داده و بازخورد"
                }
                ok, response_msg = send_to_google_sheet(test_data)
                if ok:
                    st.success(f"🎉 ارتباط با گوگل شیت برقرار است! ({response_msg})")
                else:
                    st.error(f"❌ خطا: {response_msg}")
    elif admin_pass != "":
        st.error("❌ رمز عبور نادرست است.")
