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

# ================= آدرس وب‌هوک گوگل شیت =================
# اگر لینک جدیدی از دیپلوی گرفتید، می‌توانید آن را اینجا یا از بخش پنل مدیریت وارد کنید
DEFAULT_SHEET_URL = "https://script.google.com/macros/s/AKfycbzCLMcPY7EkaoI9JPn4zLyN7az4fzMPZGL4tZJwTQ7Pa54z61BUX1BJXSaFbdE-GUXn/exec"

if "google_sheet_url" not in st.session_state:
    st.session_state.google_sheet_url = DEFAULT_SHEET_URL

if "click_count" not in st.session_state:
    st.session_state.click_count = 0

def send_to_google_sheet(payload):
    """ارسال داده‌ها به وب‌هوک گوگل شیت با دریافت وضعیت پاسخ"""
    try:
        response = requests.post(st.session_state.google_sheet_url, json=payload, timeout=8)
        if response.status_code == 200:
            return True, "اطلاعات با موفقیت در سرور ثبت شد."
        else:
            return False, f"خطای سرور گوگل: {response.status_code}"
    except Exception as e:
        return False, f"خطا در برقراری ارتباط: {str(e)}"

# ================= استایل و سربرگ =================
st.markdown("""
<style>
    .main-title {text-align: right; color: #0D47A1; font-weight: bold; margin-bottom: 5px;}
    .sub-title {text-align: right; color: #546E7A; margin-bottom: 25px;}
    .section-header {background-color: #E3F2FD; padding: 8px 15px; border-radius: 8px; color: #0D47A1; font-weight: bold; margin-top: 15px; margin-bottom: 15px; text-align: right;}
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
        "🔐 پنل مدیریت و آمار پژوهشگر"
    ])

# ================= ۱. فرم ارزیابی =================
if menu == "📝 تکمیل پرسشنامه و دریافت توصیه":
    st.markdown("<h2 class='main-title'>🩺 سامانه توصیه‌گر هوشمند خودمراقبتی بیماران دیابتی</h2>", unsafe_allow_html=True)
    st.markdown("<p class='sub-title'>لطفاً به تمامی سؤالات زیر با دقت پاسخ دهید تا توصیه‌های متناسب با وضعیت بالینی خود را دریافت نمایید.</p>", unsafe_allow_html=True)

    with st.form("diabetes_survey_form"):
        # بخش ۱: اطلاعات فردی
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

        # محاسبه BMI
        bmi = round(q6_weight / ((q5_height / 100) ** 2), 1)

        # بخش ۲: وضعیت بالینی و درمان
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
            q10_comorbidities = st.multiselect("۱۰. بیماری‌های همراه (می‌توانید چند مورد را انتخاب کنید):", [
                "فشار خون بالا",
                "چربی خون بالا",
                "سابقه بیماری قلبی - عروقی",
                "مشکلات کلیوی",
                "زخم پای دیابتی یا گزگز و بی‌حسی پا",
                "هیچ‌کدام"
            ], default=["هیچ‌کدام"])

        # بخش ۳: آزمایش‌ها و کنترل قند خون
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

        # بخش ۴: رفتارهای خودمراقبتی و سبک زندگی
        st.markdown("<div class='section-header'>🏃‍♂️ بخش ۴: خودمراقبتی و سبک زندگی</div>", unsafe_allow_html=True)
        c7, c8 = st.columns(2)
        with c7:
            q15_glucometer = st.selectbox("۱۵. چقدر از دستگاه قند سنج (گلوکومتر) استفاده می‌کنید؟", [
                "روزانه یک‌بار یا بیشتر",
                "چند بار در هفته",
                "فقط زمانی که حالم بد است",
                "اصلاً دستگاه ندارم / استفاده نمی‌کنم"
            ])
            q17_exercise = st.selectbox("۱۷. در طول هفته چند روز فعالیت بدنی (حداقل ۳۰ دقیقه پیاده‌روی) دارید؟", [
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
        
        # خلاصه اطلاعات جهت ثبت در ستون ۵
        summary_info = f"نوع: {q7_type} | درمان: {q9_treatment} | ناشتا: {q11_fbs} | HbA1c: {q13_hba1c} | BMI: {bmi}"
        
        # ارسال اطلاعات به گوگل شیت
        payload = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "gender": q3_gender,
            "received_advice": "بله",
            "click_count": st.session_state.click_count,
            "diabetes_info": summary_info
        }
        success, msg = send_to_google_sheet(payload)

        # نمایش پیام وضعیت
        st.success(f"✅ با تشکر از شما {q1_name}، پرونده خودمراقبتی شما با موفقیت ثبت و تحلیل شد.")
        
        # شاخص توده بدنی
        c_bmi1, c_bmi2 = st.columns(2)
        with c_bmi1:
            st.metric("شاخص توده بدنی (BMI)", f"{bmi} kg/m²")
        with c_bmi2:
            if bmi < 18.5:
                st.warning("⚠️ کمبود وزن: نیاز به دریافت کالری مغذی")
            elif 18.5 <= bmi <= 24.9:
                st.success("🟢 وزن نرمال و ایده‌آل")
            elif 25.0 <= bmi <= 29.9:
                st.warning("🟡 دارای اضافه‌وزن: اصلاح سبک زندگی توصیه می‌شود")
            else:
                st.error("🔴 چاقی: مدیریت وزن تأثیر چشمگیری در کاهش مقاومت به انسولین دارد")

        st.markdown("### 📋 بسته‌های توصیه‌گر بالینی شخصی‌سازی‌شده:")
        
        t1, t2, t3, t4 = st.tabs(["🥗 رژیم و تغذیه", "🏃‍♂️ فعالیت بدنی", "💊 داروها و پایش", "⚠️ هشدارها و پیگیری"])
        
        with t1:
            if "هر روز" in q18_diet:
                st.error("• مصرف قندهای ساده را سریعاً متوقف کنید و به‌جای آن از میوه‌های با فیبر بالا استفاده نمایید.")
            st.write("• بشقاب غذایی خود را به ۳ قسمت تقسیم کنید: نصف بشقاب سبزیجات، یک‌چهارم پروتئین سالم و یک‌چهارم کربوهیدرات پیچیده.")
            st.write("• مصرف نمک و چربی‌های اشباع را به‌ویژه به علت محافظت از کلیه‌ها و قلب کاهش دهید.")

        with t2:
            if "اصلاً" in q17_exercise:
                st.warning("• فعالیت بدنی ناکافی است. روزانه با ۱۵ دقیقه پیاده‌روی سبک شروع کنید و تدریجاً به ۳۰ دقیقه برسانید.")
            else:
                st.info("• هدف ایده‌آل: حداقل ۱۵۰ دقیقه پیاده‌روی سریع در هفته در جلسات ۳۰ دقیقه‌ای بدون فاصله بیش از ۲ روز متوالی.")

        with t3:
            if "فراموش" in q16_adherence:
                st.error("• نظم دارویی پایه اصلی کنترل دیابت است. برای مصرف داروها یادآور گوشی یا جعبه تقسیم دارو تنظیم کنید.")
            if "اصلاً" in q15_glucometer or "فقط زمانی" in q15_glucometer:
                st.warning("• پایش منظم قند خون به شما و پزشکتان کمک می‌کند تصمیمات درمانی دقیق‌تری بگیرید.")

        with t4:
            if "بله، مکرراً" in q14_hypo or "<۷۰" in q11_fbs:
                st.error("🚨 خطر افت قند (هیپوگلیسمی): در صورت تکرار افت قند، سریعاً به پزشک معالج مراجعه فرمایید و همواره چند حبه قند به همراه داشته باشید.")
            if "زخم پای دیابتی" in q10_comorbidities:
                st.error("🚨 مراقبت پا: پاهای خود را روزانه معاینه کنید و از پوشیدن کفش‌های تنگ خودداری فرمایید.")
            else:
                st.info("• حداقل سالی یک‌بار جهت معاینه چشم‌پزشکی و آزمایش ادرار (میکروآلبومین) مراجعه فرمایید.")

# ================= ۲. درباره سامانه =================
elif menu == "ℹ️ درباره طرح پژوهشی":
    st.markdown("### 📘 درباره سامانه توصیه‌گر هوشمند DiaCare AI")
    st.write("""
    این پژوهش در قالب یک سیستم تصمیم‌یار بالینی (CDSS) جهت بررسی اثربخشی آموزش و توصیه‌های هوشمند در ارتقای شاخص‌های خودمراقبتی و سواد سلامت بیماران دیابتی طراحی شده است.
    """)

# ================= ۳. پنل مدیریت پژوهشگر =================
elif menu == "🔐 پنل مدیریت و آمار پژوهشگر":
    st.markdown("<h2 class='main-title'>🔐 پنل مدیریت و تنظیمات اتصال</h2>", unsafe_allow_html=True)
    st.markdown("<p class='sub-title'>جهت مشاهده وضعیت و ویرایش لینک اتصال گوگل‌شیت وارد شوید.</p>", unsafe_allow_html=True)

    admin_pass = st.text_input("رمز عبور مدیر:", type="password")
    
    # رمز پیش‌فرض: admin123
    if admin_pass == "admin123":
        st.success("🔓 احراز هویت با موفقیت انجام شد.")
        
        st.markdown("### ⚙️ تنظیمات لینک وب‌هوک گوگل شیت")
        new_url = st.text_input("آدرس Webhook Google Apps Script:", value=st.session_state.google_sheet_url)
        if st.button("💾 ذخیره لینک جدید"):
            st.session_state.google_sheet_url = new_url
            st.success("✅ لینک وب‌هوک با موفقیت به‌روزرسانی شد.")
            
        st.markdown("---")
        st.markdown("### 🧪 تست فوری ارسال داده به گوگل‌شیت")
        if st.button("🚀 ارسال داده تستی به گوگل‌شیت"):
            test_payload = {
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "gender": "تست سیستم",
                "received_advice": "بله",
                "click_count": 99,
                "diabetes_info": "تست سلامت اتصال گوگل‌شیت از پنل ادمین"
            }
            ok, msg = send_to_google_sheet(test_payload)
            if ok:
                st.success("✅ ارسال تست موفق بود! لطفاً گوگل شیت خود را چک کنید، یک ردیف تستی اضافه شده است.")
            else:
                st.error(f"❌ خطا در اتصال به گوگل‌شیت: {msg}")
    elif admin_pass != "":
        st.error("❌ رمز عبور اشتباه است.")

