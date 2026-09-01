import streamlit as st
from datetime import datetime

# تنظیمات اولیه صفحه
st.set_page_config(
    page_title="سامانه هوشمند توصیه‌گر دیابت (DiaCare AI)",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded"
)

# استایل اختصاصی راست‌چین (RTL) و فونت فارسی
st.markdown("""
<style>
    @import url('https://v1.fontapi.ir/css/Vazir');
    * {
        font-family: 'Vazir', sans-serif !important;
        direction: rtl;
        text-align: right;
    }
    .main-header {
        background: linear-gradient(135deg, #0f766e, #0d9488);
        padding: 20px;
        border-radius: 12px;
        color: white;
        text-align: center;
        margin-bottom: 25px;
    }
    .card {
        background-color: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        padding: 18px;
        margin-bottom: 15px;
    }
    .alert-card {
        background-color: #fee2e2;
        border-right: 6px solid #ef4444;
        padding: 15px;
        border-radius: 8px;
        margin-bottom: 15px;
    }
    .safe-card {
        background-color: #dcfce7;
        border-right: 6px solid #22c55e;
        padding: 15px;
        border-radius: 8px;
        margin-bottom: 15px;
    }
    .warning-card {
        background-color: #fef3c7;
        border-right: 6px solid #f59e0b;
        padding: 15px;
        border-radius: 8px;
        margin-bottom: 15px;
    }
</style>
""", unsafe_allow_html=True)

# هدر اصلی سامانه
st.markdown("""
<div class="main-header">
    <h2 style="color:white; margin:0;">سامانه توصیه‌گر هوشمند خودمراقبتی بیماران دیابتی</h2>
    <p style="margin:5px 0 0 0; opacity:0.9;">موتور استنتاج بالینی مبتنی بر قواعد اولویت‌دار (قواعد A تا G)</p>
</div>
""", unsafe_allow_html=True)

# ==================== سایدبار: فرم اطلاعات بیمار (موج صفر) ====================
with st.sidebar:
    st.header("📋 اطلاعات پایه و بالینی بیمار")
    st.caption("برگرفته از پرسشنامه موج صفر")
    
    patient_name = st.text_input("نام بیمار / شناسه ناشناس", value="بیمار آزمایشی P-01")
    col_demo1, col_demo2 = st.columns(2)
    with col_demo1:
        age = st.number_input("سن (سال)", min_value=10, max_value=100, value=52)
        gender = st.selectbox("جنسیت", ["مرد", "زن"])
    with col_demo2:
        height = st.number_input("قد (سانتی‌متر)", min_value=120, max_value=220, value=170)
        weight = st.number_input("وزن (کیلوگرم)", min_value=30.0, max_value=180.0, value=82.0)
    
    # محاسبه شاخص توده بدنی (BMI)
    bmi = round(weight / ((height / 100) ** 2), 1)
    st.info(f"شاخص توده بدنی (BMI): **{bmi}**")

    st.markdown("---")
    st.subheader("🩸 شاخص‌های قند خون")
    fbs = st.number_input("قند خون ناشتا - FBS (mg/dL)", min_value=40, max_value=500, value=145)
    ppbg = st.number_input("قند ۲ ساعت پس از غذا (mg/dL)", min_value=40, max_value=600, value=195)
    
    hypo_symptoms = st.checkbox("آیا علائم افت قند (لرزش، تعریق سرد، تپش قلب، سرگیجه) دارید؟")

    st.markdown("---")
    st.subheader("🩺 سوابق درمانی و بالینی")
    diabetes_type = st.selectbox("نوع دیابت", ["دیابت نوع ۲", "دیابت نوع ۱", "پره‌دیابت"])
    treatment = st.selectbox("شیوه درمان اصلی", ["داروی خوراکی (متفورمین/سولفونیل‌اوره)", "انسولین", "ترکیب دارو و انسولین", "فقط رژیم غذایی"])
    
    comorbidities = st.multiselect(
        "بیماری‌های همراه و عوارض",
        ["فشار خون بالا", "چربی خون بالا (دیس‌لیپیدمی)", "مشکلات کلیوی (نفروپاتی)", "عوارض قلبی عروقی", "زخم پا یا نوروپاتی محیطی"],
        default=["فشار خون بالا"]
    )
    
    physical_activity = st.selectbox("میزان فعالیت فیزیکی در هفته", ["بی‌تحرک (کمتر از ۳۰ دقیقه)", "متوسط (۱ تا ۲ روز)", "منظم (بیش از ۱۵۰ دقیقه)"])

# ==================== موتور استنتاج بالینی (قواعد A تا G) ====================
def run_clinical_recommender(patient):
    recommendations = []
    alerts = []
    
    # قاعده سطح ۱ (حیاتی): پیشگیری و مدیریت هیپوگلیسمی (گروه A)
    if patient["fbs"] < 70 or patient["ppbg"] < 70 or patient["hypo_symptoms"]:
        alerts.append({
            "level": "CRITICAL",
            "title": "🚨 هشدار قرمز: احتمال افت شدید قند خون (هیپوگلیسمی)",
            "action": (
                "**اجرای فوری قانون ۱۵-۱۵:**\n"
                "- سریعاً ۱۵ گرم کربوهیدرات ساده مصرف کنید (نصف لیوان آبمیوه طبیعی، یا ۳ حبه قند، یا یک قاشق شکر حل‌شده در آب).\n"
                "- به مدت ۱۵ دقیقه استراحت کنید و مجدداً قند خون را اندازه بگیرید.\n"
                "- در صورت باقی ماندن قند زیر ۷۰ mg/dL، همین مراحل را تکرار کنید و در صورت بیهوشی یا عدم بهبود فوراً با اورژانس (۱۱۵) تماس بگیرید."
            )
        })
    
    # قاعده سطح ۲: پایش و وضعیت قند خون (گروه B)
    if patient["fbs"] >= 180 or patient["ppbg"] >= 250:
        recommendations.append({
            "category": "پایش قند خون (Hyperglycemia)",
            "icon": "⚠️",
            "text": f"سطح قند خون شما (ناشتا: {patient['fbs']}، بعد غذا: {patient['ppbg']}) بالاتر از بازه هدف است. هیدراتاسیون مناسب (نوشیدن آب کافی) را رعایت نموده و در صورت تداوم، دوز درمانی با پزشک معالج بازبینی شود."
        })
    elif 70 <= patient["fbs"] <= 130 and patient["ppbg"] < 180:
        recommendations.append({
            "category": "پایش قند خون",
            "icon": "✅",
            "text": "شاخص‌های قند ناشتا و بعد از غذای شما در محدوده مطلوب انجمن دیابت (ADA) قرار دارند. برنامه پایش هفتگی فعلی را ادامه دهید."
        })
    else:
        recommendations.append({
            "category": "پایش قند خون",
            "icon": "ℹ️",
            "text": "قند خون در وضعیت نیازمند پایش تکمیلی است. توصیه می‌شود حداقل ۳ بار در هفته قند ناشتا و پس از غذا ثبت شود."
        })

    # قاعده سطح ۳: توصیه‌های تغذیه و کنترل وزن (گروه C)
    diet_text = "رعایت بشقاب سالم دیابتی: نصف بشقاب سبزیجات غنی از فیبر، یک‌چهارم پروتئین کم‌چرب و یک‌چهارم غلات کامل."
    if patient["bmi"] >= 25.0:
        diet_text += f" با توجه به شاخص توده بدنی ({patient['bmi']} - اضافه وزن/چاقی)، کاهش ۵ تا ۷ درصدی وزن از طریق کاهش مصرف قندهای ساده و کربوهیدرات‌های تصفیه‌شده، حساسیت به انسولین را به طور معناداری ارتقا می‌دهد."
    if "فشار خون بالا" in patient["comorbidities"]:
        diet_text += " با توجه به فشار خون همراه، محدودسازی سدیم دریافتی (کمتر از ۲۳۰۰ میلی‌گرم در روز یا نمک کمتر از ۱ قاشق چای‌خوری) اکیداً پیشنهاد می‌شود."
    
    recommendations.append({
        "category": "رژیم غذایی و تغذیه",
        "icon": "🥗",
        "text": diet_text
    })

    # قاعده سطح ۴: فعالیت بدنی متناسب با عوارض (گروه D)
    if "زخم پا یا نوروپاتی محیطی" in patient["comorbidities"]:
        activity_advice = "به علت وجود نوروپاتی یا عارضه پا، از ورزش‌های ضربه‌ای (دویدن شدید) پرهیز کنید. ورزش‌های با فشار کم مانند شنا، دوچرخه ثابت یا ورزش‌های کششی نشسته همراه با بازرسی روزانه پوست پا الزامی است."
    elif "عوارض قلبی عروقی" in patient["comorbidities"]:
        activity_advice = "ورزش‌های ملایم هوازی نظیر پیاده‌روی با گام آرام تا متوسط (روزانه ۲۰ تا ۳۰ دقیقه)، بدون وارد کردن فشار ناگهانی به سیستم قلبی انجام شود."
    else:
        activity_advice = "هدف‌گذاری استاندارد: ۱۵۰ دقیقه فعالیت هوازی با شدت متوسط در هفته (نظیر پیاده‌روی تند در ۵ روز ۳۰ دقیقه‌ای) به همراه تمرینات مقاومتی سبک."
    
    recommendations.append({
        "category": "برنامه فعالیت فیزیکی",
        "icon": "🚶‍♂️",
        "text": activity_advice
    })

    # قاعده سطح ۵: مراقبت دارویی و پایبندی (گروه E)
    med_text = f"داروهای شما ({patient['treatment']}) باید راس ساعات مشخص و مطابق با زمان وعده‌های غذایی مصرف شوند. هرگز دوز دارو یا انسولین را بدون دستور پزشک دستکاری نکنید."
    recommendations.append({
        "category": "مدیریت دارو و انسولین",
        "icon": "💊",
        "text": med_text
    })

    # قاعده سطح ۶: مراقبت تخصصی از پا و ارگان‌ها (گروه F و G)
    recommendations.append({
        "category": "مراقبت روزانه از پا و چکاپ",
        "icon": "🦶",
        "text": "هر شب پاهای خود را از نظر قرمزی، تاول، ترک‌خوردگی یا تغییر رنگ بررسی کنید. کفش استاندارد و جوراب نخی بدون درز بپوشید. آزمایش فصلی HbA1c و معاینه چشم سالانه در برنامه قرار گیرد."
    })

    return alerts, recommendations

# داده‌های ورودی آماده تحلیل
patient_data = {
    "name": patient_name,
    "age": age,
    "gender": gender,
    "bmi": bmi,
    "fbs": fbs,
    "ppbg": ppbg,
    "hypo_symptoms": hypo_symptoms,
    "diabetes_type": diabetes_type,
    "treatment": treatment,
    "comorbidities": comorbidities,
    "physical_activity": physical_activity
}

# دکمه اجرای تحلیل موتور توصیه‌گر
col_act1, col_act2 = st.columns([1, 4])
with col_act1:
    btn_generate = st.button("🔍 اجرای موتور استنتاج", type="primary", use_container_width=True)

st.markdown("---")

# اجرای موتور توصیه‌گر و نمایش خروجی‌ها
alerts, recs = run_clinical_recommender(patient_data)

st.subheader(f"📊 پنل نتایج و توصیه‌های شخصی‌سازی‌شده برای: {patient_name}")

# نمایش هشدارهای اولویت ۱
if alerts:
    for a in alerts:
        st.markdown(f"""
        <div class="alert-card">
            <h3 style="color:#b91c1c; margin-top:0;">{a['title']}</h3>
            <p>{a['action']}</p>
        </div>
        """, unsafe_allow_html=True)

# خلاصه وضعیت بیمار در قالب کارت‌های متریک
m1, m2, m3, m4 = st.columns(4)
m1.metric(label="شاخص BMI", value=f"{bmi}", delta="نرمال: ۱۸.۵-۲۴.۹")
m2.metric(label="قند ناشتا (FBS)", value=f"{fbs} mg/dL", delta="هدف: ۷۰-۱۳۰")
m3.metric(label="قند ۲ ساعته", value=f"{ppbg} mg/dL", delta="هدف: کمتر از ۱۸۰")
m4.metric(label="تعداد عوارض همراه", value=f"{len(comorbidities)} مورد")

st.markdown("### 💡 سبد توصیه‌های بالینی صادر شده")

# نمایش توصیه‌های گروه‌های مختلف به صورت کارت‌های مجزا
for r in recs:
    with st.container():
        st.markdown(f"""
        <div class="card">
            <h4 style="color:#0f766e; margin-top:0;">{r['icon']} محور: {r['category']}</h4>
            <p style="font-size:15px; line-height:1.8; color:#334155;">{r['text']}</p>
        </div>
        """, unsafe_allow_html=True)

st.caption(f"زمان پردازش استنتاج: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | موتور توصیه‌گر نسخه ۱.۰ پایان‌نامه")
