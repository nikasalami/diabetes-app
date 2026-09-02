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

# ================= آدرس وب‌هوک گوگل شیت (آدرس نهایی و فعال شما) =================
DEFAULT_SHEET_URL = "https://script.google.com/macros/s/AKfycbzuNbLV7kaM8PmZO1Dogssna7l9j0z5s9Z7_iOwmBSxY0ADuqPR4ACaZEcU7qwFeNrP/exec"

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
    """ارسال داده‌ها به وب‌هوک گوگل شیت با مدیریت تغییر مسیر"""
    url = st.session_state.google_sheet_url.strip()
    try:
        headers = {"Content-Type": "text/plain;charset=utf-8"}
        # استفاده از متد POST و پشتیبانی کامل از ریدایرکت گوگل
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
            return False, f"کد وضعیت سرور: {response.status_code}"
    except Exception as e:
        return False, f"خطا در ارتباط: {str(e)}"

# ================= استایل‌های بصری =================
st.markdown("""
<style>
    .main-title {text-align: right; color: #0D47A1; font-weight: bold; margin-bottom: 5px;}
    .sub-title {text-align: right; color: #546E7A; margin-bottom: 25px;}
    .section-header {background-color: #E3F2FD; padding: 8px 15px; border-radius: 8px; color: #0D47A1; font-weight: bold; margin-top: 15px; margin-bottom: 15px; text-align: right;}
</style>
""", unsafe_allow_html=True)

# منوی کناری (Sidebar)
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2854/2854341.png", width=80)
    st.title("DiaCare AI")
    st.markdown("**سامانه هوشمند خودمراقبتی دیابت**")
    st.caption("مبتنی بر پروتکل استاندارد موج صفر")
    st.markdown("---")
    menu = st.radio("بخش‌های سامانه:", [
        "📝 تکمیل پرسشنامه و دریافت برنامه",
        "ℹ️ درباره طرح پژوهشی",
        "🔐 پنل مدیریت و بررسی اتصال"
    ])

# ================= بخش ۱: پرسشنامه و دریافت توصیه‌ها =================
if menu == "📝 تکمیل پرسشنامه و دریافت برنامه":
    st.markdown("<h2 class='main-title'>🩺 سامانه توصیه‌گر خودمراقبتی بیماران دیابتی</h2>", unsafe_allow_html=True)
    st.markdown("<p class='sub-title'>لطفاً مشخصات بالینی خود را وارد فرمایید تا توصیه‌های اختصاصی به شما ارائه شود.</p>", unsafe_allow_html=True)

    with st.form("diabetes_survey_form"):
        # بخش ۱: اطلاعات فردی
        st.markdown("<div class='section-header'>👤 بخش ۱: مشخصات فردی و آنتروپومتریک</div>", unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            q1_name = st.text_input("۱. نام و نام خانوادگی یا نام مستعار:", value="کاربر گرامی")
            q3_gender = st.radio("۳. جنسیت:", ["زن", "مرد"], horizontal=True)
            q5_height = st.number_input("۵. قد (سانتی‌متر):", min_value=100, max_value=230, value=168)
        with c2:
            q2_phone = st.text_input("۲. شماره تماس (اختیاری):", value="")
            q4_age = st.number_input("۴. سن (سال):", min_value=10, max_value=100, value=48)
            q6_weight = st.number_input("۶. وزن فعلی (کیلوگرم):", min_value=30.0, max_value=200.0, value=74.0, step=0.5)

        bmi = round(q6_weight / ((q5_height / 100) ** 2), 1)

        # بخش ۲: وضعیت درمانی
        st.markdown("<div class='section-header'>💊 بخش ۲: سابقه و روش درمانی</div>", unsafe_allow_html=True)
        c3, c4 = st.columns(2)
        with c3:
            q7_type = st.selectbox("۷. نوع دیابت:", [
                "دیابت نوع ۲",
                "دیابت نوع ۱",
                "پره‌دیابت (پیش‌دیابت)",
                "دیابت بارداری",
                "نمی‌دانم / مطمئن نیستم"
            ])
            q9_treatment = st.selectbox("۹. روش اصلی کنترل و درمان دیابت شما:", [
                "فقط قرص‌های خوراکی (مانند متفورمین)",
                "تزریق انسولین (با یا بدون قرص)",
                "فقط اصلاح سبک زندگی (رژیم غذایی و ورزش)",
                "دارو مصرف نمی‌کنم"
            ])
        with c4:
            q8_duration = st.selectbox("۸. مدت‌زمان ابتلا به دیابت:", [
                "کمتر از ۱ سال (به‌تازگی تشخیص داده شده)",
                "۱ تا ۵ سال",
                "۵ تا ۱۰ سال",
                "بیش از ۱۰ سال"
            ])
            q10_comorbidities = st.multiselect("۱۰. بیماری‌های زمینه‌ای یا عوارض همزمان (در صورت وجود):", [
                "فشار خون بالا",
                "چربی خون بالا",
                "مشکلات قلبی-عروقی",
                "نارسایی یا اختلال کلیوی",
                "مشکلات بینایی / شبکیه چشم",
                "زخم پای دیابتی / گزگز پاها",
                "هیچ‌کدام"
            ], default=["هیچ‌کدام"])

        # بخش ۳: شاخص‌های خونی
        st.markdown("<div class='section-header'>🩸 بخش ۳: کنترل قند خون و وضعیت بالینی</div>", unsafe_allow_html=True)
        c5, c6 = st.columns(2)
        with c5:
            q11_fbs = st.selectbox("۱۱. میانگین قند خون ناشتا در دو هفته اخیر:", [
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
            q14_hypo = st.selectbox("۱۴. افت قند خون شدید (هیپوگلیسمی) در یک ماه گذشته:", [
                "خیر",
                "بله، یک یا دو بار",
                "بله، مکرراً (بیش از ۲ بار)"
            ])

        # بخش ۴: رفتارهای خودمراقبتی
        st.markdown("<div class='section-header'>🏃‍♂️ بخش ۴: خودمراقبتی و سبک زندگی</div>", unsafe_allow_html=True)
        c7, c8 = st.columns(2)
        with c7:
            q15_glucometer = st.selectbox("۱۵. پایش قند با دستگاه گلوکومتر خانگی:", [
                "روزانه یک‌بار یا بیشتر",
                "چند بار در هفته",
                "فقط در صورت بروز علائم بدحالی",
                "دستگاه ندارم / استفاده نمی‌کنم"
            ])
            q17_exercise = st.selectbox("۱۷. فعالیت بدنی (حداقل ۳۰ دقیقه) در طول هفته:", [
                "اصلاً یا کمتر از ۱ روز",
                "۱ تا ۲ روز در هفته",
                "۳ تا ۴ روز در هفته",
                "۵ روز یا بیشتر در هفته"
            ])
        with c8:
            q16_adherence = st.selectbox("۱۶. نظم در مصرف داروهای تجویز شده یا تزریق انسولین:", [
                "کاملاً منظم و طبق دستور پزشک",
                "گاهی فراموش می‌کنم (۱ یا ۲ بار در هفته)",
                "اغلب فراموش می‌کنم یا نامنظم است"
            ])
            q18_diet = st.selectbox("۱۸. مصرف قندهای ساده، نوشابه و شیرینی‌جات:", [
                "به‌ندرت یا اصلاً مصرف نمی‌کنم",
                "گاهی در طول هفته",
                "تقریباً هر روز"
            ])

        st.markdown("---")
        submit_btn = st.form_submit_button("🔍 ثبت مشخصات و صدور توصیه‌ها", use_container_width=True, type="primary")

    if submit_btn:
        st.session_state.click_count += 1
        st.session_state.form_submitted = True
        st.session_state.user_gender = q3_gender
        
        summary = f"نوع: {q7_type} | درمان: {q9_treatment} | ناشتا: {q11_fbs} | HbA1c: {q13_hba1c} | BMI: {bmi}"
        st.session_state.user_info_summary = summary
        
        # ثبت ورود کاربر در گوگل‌شیت
        payload = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "gender": q3_gender,
            "received_advice": "بله (توصیه دریافت شد)",
            "click_count": st.session_state.click_count,
            "diabetes_info": summary,
            "satisfaction": "در انتظار ثبت نظر",
            "reuse": "-",
            "comment": "-"
        }
        send_to_google_sheet(payload)

    # نمایش نتایج و توصیه‌ها
    if st.session_state.form_submitted:
        st.success("✅ اطلاعات با موفقیت ثبت شد. توصیه‌های بالینی شما به شرح زیر است:")
        
        m1, m2 = st.columns(2)
        with m1:
            st.metric("شاخص توده بدنی (BMI)", f"{bmi} kg/m²")
        with m2:
            if bmi < 18.5:
                st.warning("⚠️ کمبود وزن: نیاز به ارتقای دریافت کالری با پروتئین باکیفیت")
            elif 18.5 <= bmi <= 24.9:
                st.success("🟢 وزن نرمال و در محدوده سلامت")
            elif 25.0 <= bmi <= 29.9:
                st.warning("🟡 اضافه وزن: کاهش ۵ تا ۷ درصدی وزن به بهبود قند خون کمک می‌کند")
            else:
                st.error("🔴 چاقی: تنظیم برنامه غذایی کم‌کالری و مشاوره تغذیه ضروری است")

        st.markdown("### 📋 بسته‌های توصیه‌گر شخصی‌سازی‌شده:")
        tab1, tab2, tab3, tab4 = st.tabs(["🥗 رژیم غذایی", "🏃‍♂️ فعالیت بدنی", "💊 دارودرمانی و پایش", "⚠️ هشدارها و عوارض"])
        
        with tab1:
            if "هر روز" in q18_diet:
                st.error("• مصرف قندهای ساده و نوشیدنی‌های قندی را متوقف و فیبرهای محلول را جایگزین فرمایید.")
            st.write("• طبق الگوی بشقاب سالم: نیمی از بشقاب سبزیجات، یک‌چهارم غلات کامل و یک‌چهارم پروتئین سالم باشد.")
            st.write("• مصرف نمک و چربی‌های اشباع را برای حفظ سلامت قلب و عروق محدود کنید.")

        with tab2:
            if "اصلاً" in q17_exercise:
                st.warning("• فعالیت بدنی ناکافی است. روزانه حداقل با ۱۵ دقیقه پیاده‌روی شروع کنید.")
            else:
                st.info("• هدف استاندارد: ۱۵۰ دقیقه پیاده‌روی سریع در هفته (۵ روز در هفته، هر بار ۳۰ دقیقه).")

        with tab3:
            if "فراموش" in q16_adherence:
                st.error("• پایبندی به برنامه دارویی کلید اصلی پیشگیری از نارسایی کلیه و عروق است.")
            if "ندارم" in q15_glucometer or "فقط در صورت" in q15_glucometer:
                st.warning("• پایش منظم قند خون با گلوکومتر برای جلوگیری از نوسانات شدید لازم است.")

        with tab4:
            if "بله، مکرراً" in q14_hypo or "کمتر از ۷۰" in q11_fbs:
                st.error("🚨 خطر هیپوگلیسمی: همیشه حبه قند یا آبمیوه همراه داشته باشید و فوراً با پزشک مشورت فرمایید.")
            if "زخم پای دیابتی" in q10_comorbidities:
                st.error("🚨 مراقبت از پا: روزانه پاها را با آب ولرم شسته، خشک کرده و از نظر زخم یا قرمزی بررسی فرمایید.")
            st.info("• آزمایش هموگلوبین گلیکوزیله (HbA1c) را هر ۳ تا ۶ ماه تکرار کنید.")

        # ================= بخش نظرسنجی و رضایت‌سنجی =================
        st.markdown("---")
        st.markdown("### 🌟 فرم ارزیابی و میزان رضایت از توصیه‌گر هوشمند")
        st.caption("پاسخ‌های شما جهت ارزیابی در رساله پژوهشی در گوگل‌شیت ثبت می‌گردد:")

        with st.form("feedback_form"):
            fb_satisfaction = st.select_slider(
                "۱. میزان رضایت شما از کارایی و توصیه‌های سامانه هوشمند:",
                options=["خیلی کم / ناراضی", "کم", "متوسط", "زیاد", "بسیار زیاد و کاملاً کاربردی"],
                value="بسیار زیاد و کاملاً کاربردی"
            )
            
            fb_reuse = st.radio(
                "۲. تمایل به استفاده مجدد یا معرفی به دیگران:",
                ["بله، حتماً", "احتمالاً بله", "خیر"],
                horizontal=True
            )
            
            fb_comment = st.text_area(
                "۳. پیشنهادات یا انتقادات تکمیلی شما:",
                placeholder="نظر ارزشمند خود را در اینجا بنویسید..."
            )
            
            submit_feedback = st.form_submit_button("💌 ثبت میزان رضایت و نظر", use_container_width=True, type="primary")

        if submit_feedback:
            feedback_payload = {
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "gender": st.session_state.user_gender,
                "received_advice": "ثبت بازخورد",
                "click_count": st.session_state.click_count,
                "diabetes_info": st.session_state.user_info_summary,
                "satisfaction": fb_satisfaction,
                "reuse": fb_reuse,
                "comment": fb_comment.strip() if fb_comment.strip() else "بدون نظر متنی"
            }
            fb_ok, fb_msg = send_to_google_sheet(feedback_payload)
            if fb_ok:
                st.balloons()
                st.success("🎉 با تشکر! میزان رضایت شما با موفقیت در گوگل‌شیت ذخیره شد.")
            else:
                st.error(f"خطا در ثبت: {fb_msg}")

# ================= بخش ۲: درباره سامانه =================
elif menu == "ℹ️ درباره طرح پژوهشی":
    st.markdown("### 📘 درباره سامانه خودمراقبتی هوشمند DiaCare AI")
    st.write("""
    این سامانه با بهره‌گیری از هوش مصنوعی و پروتکل‌های خودمراقبتی استاندارد طراحی شده است تا تصمیم‌یاری مناسب برای ارتقای سلامت بیماران دیابتی فراهم آورد.
    """)

# ================= بخش ۳: پنل مدیریت =================
elif menu == "🔐 پنل مدیریت و بررسی اتصال":
    st.markdown("<h2 class='main-title'>🔐 پنل مدیریت و تست ارتباط</h2>", unsafe_allow_html=True)
    admin_pass = st.text_input("رمز عبور مدیر:", type="password")
    
    if admin_pass == "admin123":
        st.success("🔓 احراز هویت موفقیت‌آمیز بود.")
        current_url = st.text_input("آدرس وب‌هوک گوگل شیت:", value=st.session_state.google_sheet_url)
        
        c_btn1, c_btn2 = st.columns(2)
        with c_btn1:
            if st.button("💾 ذخیره آدرس در این نشست", use_container_width=True):
                st.session_state.google_sheet_url = current_url.strip()
                st.success("✅ آدرس ذخیره شد.")
                
        with c_btn2:
            if st.button("🧪 ارسال داده تستی به گوگل‌شیت", use_container_width=True, type="primary"):
                test_payload = {
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "gender": "تست سیستم",
                    "received_advice": "بله",
                    "click_count": 999,
                    "diabetes_info": "تست ستون‌های شیت",
                    "satisfaction": "بسیار زیاد (تست)",
                    "reuse": "بله، حتماً",
                    "comment": "اتصال تستی بدون خطا برقرار است."
                }
                ok, res = send_to_google_sheet(test_payload)
                if ok:
                    st.success(f"🎉 ارتباط با موفقیت برقرار است! ({res})")
                else:
                    st.error(f"❌ خطا: {res}")
    elif admin_pass != "":
        st.error("❌ رمز عبور اشتباه است.")
