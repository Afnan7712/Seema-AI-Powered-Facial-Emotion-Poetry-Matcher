import streamlit as st
import cv2
import numpy as np
from deepface import DeepFace
import random
import os
import urllib.parse

# =========================================================
# 1. إعدادات الصفحة (يجب أن تكون أول أمر Streamlit)
# =========================================================
st.set_page_config(
    page_title="سِيماء - ملامح وأبيات",
    page_icon="📜",
    layout="centered"
)

# =========================================================
# 2. خلفية الـ SVG
# =========================================================
svg_pattern = '''<svg xmlns="http://www.w3.org/2000/svg" width="300" height="300" viewBox="0 0 300 300"><g fill="none" stroke-width="1.8"><path stroke="#F472B6" d="M20 30h30a5 5 0 0 1 5 5v35a5 5 0 0 0-5-5H20z"/><path stroke="#F472B6" d="M20 30a5 5 0 0 0-5 5v35a5 5 0 0 1 5-5h30"/><path stroke="#0284C7" d="M150 50c10-8 25-8 35 0v30c-10-8-25-8-35 0z"/><path stroke="#0284C7" d="M150 50c-10-8-25-8-35 0v30c10-8 25-8 35 0z"/><path stroke="#C084FC" d="M250 120h25a4 4 0 0 1 4 4v25a4 4 0 0 0-4-4h-25z"/><path stroke="#FBBF24" d="M40 180h30M40 186h30M40 192h30"/><path stroke="#34D399" d="M160 220c8-6 20-6 28 0v24c-8-6-20-6-28 0z"/><path stroke="#34D399" d="M160 220c-8-6-20-6-28 0v24c8-6 20-6 28 0z"/><path stroke="#F472B6" d="M260 250h20a3 3 0 0 1 3 3v20a3 3 0 0 0-3-3h-20z"/><circle cx="90" cy="100" r="3" fill="#38BDF8"/><circle cx="220" cy="40" r="3.5" fill="#F472B6"/><circle cx="80" cy="260" r="2.5" fill="#FBBF24"/><circle cx="210" cy="180" r="3" fill="#C084FC"/></g></svg>'''

encoded_svg = urllib.parse.quote(svg_pattern)

# =========================================================
# 3. تنسيقات الـ CSS
# =========================================================
st.markdown(f"""
    <style>
    .stApp {{
        background-color: #F8FAFC !important;
        background-image: url("data:image/svg+xml,{encoded_svg}") !important;
        background-repeat: repeat !important;
        background-size: 260px 260px !important;
        direction: rtl;
    }}

    .header-card, .poem-card, .emotion-badge {{
        background-color: #FFFFFF !important;
        border-radius: 20px;
        border: 1px solid #E2E8F0;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.05);
        margin-bottom: 20px;
        text-align: center;
        width: 100%;
    }}

    .header-card {{
        padding: 25px 20px;
    }}

    .main-title {{
        color: #1E293B;
        font-family: 'Tajawal', sans-serif;
        font-size: 2.8rem;
        font-weight: 800;
        margin-bottom: 8px;
    }}

    .sub-title {{
        color: #475569;
        font-size: 1.15rem;
        font-weight: 600;
        margin: 0;
    }}

    .emotion-badge {{
        color: #0F172A !important;
        padding: 12px 25px;
        font-size: 1.25rem;
        font-weight: 700;
        display: inline-block;
    }}

    .poem-card {{
        color: #1E293B !important;
        padding: 30px;
        font-size: 1.35rem;
        font-weight: bold;
        line-height: 1.9;
    }}
    </style>
""", unsafe_allow_html=True)

# =========================================================
# 4. الواجهة الرئيسية
# =========================================================
st.markdown('''
    <div class="header-card">
        <div class="main-title"> سِيــماء</div>
        <div class="sub-title">تَقْرَأ المَلامِح.. فَتَنْطِقُ الأَبْيَات ✨</div>
    </div>
''', unsafe_allow_html=True)

# =========================================================
# 5. الأبيات
# =========================================================
POEMS = {
    "happy": [
        "وَتَبْتَسِمُ الحَيَاةُ إِذَا ابْتَسَمْتَ\nوَيَزْهُو فِي كَفَّيْكَ الرَّبِيعُ",
        "لا السيفُ يفعلُ بي ما أنتِ فاعلةٌ\nولا لقاءُ عدوّى مثلَ لُقياك\nلوباتَ سهمٌ من الأعداءِ في كَبدي\nما نالَ مِنّىَ ما نالتْهُ عيناك\nالمتنبي",
        "أتُقالُ فِيك قَصيدَةٌ مَرْمُوقَةٌ\nأنت القَصائِدُ، مَطْلَعًا، وختامًا.",
        "أنيري مَكانَ البَدرِ إن أفَلَ البَدرُ \nوَقومي مَقامَ الشمس ما استَأْخَرَ الفَجرُ \n قيس ابن الملوح",
        "إنّي لأنظر في الوجودِ بأسرهِ\nلأرى الوجوة، فلا أرى إلاّك\nقالوا ويخلقُ أربعينَ مُشابها \nمن أربعينك لا أريدُ سِواك \n جميل بن معمر"
    ],
    "sad": [
        "مَنْ عَزَّ بِالأَقْوَامِ ذَلَّ بِذُلِّهِمْ\nوَمَنْ عَزَّ بِالرَّحْمَنِ ظَلَّ عَزِيزًا",
        "لأهلِ الصَّبْرِ نهاياتٌ جَميلَة.",
        "وَلَا تَبْتَئِسْ مِنْ مِحْنَةِ سَاقهَا القضا إليْك\n فكمْ بؤس تلاه نعيمُ\n - محمود سامي البارودي",
        "سيأتي الحُلم في مِشكَاة فجر \nوعند الصّبح تبتسم الأمـانيِ",
        "لَيسَ بي داءٌ وَلَكِنِّي اِمرُؤْ\n لَستُ في أرضي وَلَا بَينَ صَحابي\n- إيليا أبو ماضي",
        "لن يدومَ الهمُّ يا حلوَ المُحيّا \nلن يظلّ الحزنُ في عينيكَ يحيا.",
        "ولعل ما تَخشاه ليس بِكائنٍ، \nولعلّ ما ترجوهُ سوف يكونُ\nولعل ما هونت ليس بهينِ،\nولعل ما شددت سوف يهون"
    ],
    "surprise": [
        "سُبْحَانَ مَنْ أَلْهَمَ الخَاطِرَ المَذْهُولَ فِكْرَة!",
        "تََبَارَكَ مَنْ صَوَّرَ هَذَا الجَمَالَ وَأَبْدَعَه!"
    ],
    "angry": [
        "عَلَى قَدْرِ أَهْلِ العَزْمِ تأْتِي العَزَائِمُ\nوَتَأْتِي عَلَى قَدْرِ الكِرَامِ المَكَارِمُ",
        "وَإذا بُليتَ بِظالم كن ظالم \nوإذا لقيت ذوي الجَهالة فاجهَل\n- عنترة بن شداد",
        "قومّ إذا جَالسْتهم صَدِئت بقرْبهمُ العقول\n لا يُفهموني قولهُم ويدق عَنهُم ما أقول\n- دعبل الخزاعي",
        "وَيَجهَدُ الناسُ في الدُنيا مُنافَسَةً\n وَلَيسَ لِلناسِ شَيءٌ غيرَ ما رُزِقوا\n• أبو العتاهية .",
        "شَكَوْتُ وما الشَّكوَى لِمِثْلِي عَادَةً\nوِلَكِنْ تَفِيْضُ النَّفْسُ عِنْدَ امتِلائِهَا\n- أبو تمام",
        "لا يَحمِلُ الحِقدَ مَن تَعلو بِهِ الرُتَبُ\n وَلا يَنالَ العُلا مَن طبعُهُ الغضبُ\n- عنترة بن شداد"
        
    ],
    "neutral": [
        "هَل تَعَلَمينَ وَراءَ الحُبِّ مَنزلَةً \n تُدني إِلَيكِ فَإنَّ الحُبَّ أقصاني\nبشار بن برد",
        "وَقَدْ تَنْطِقُ الأَشْيَاءُ وَهِيَ صَوَامِتٌ\nوَمَا كُلُّ نُطْقِ المُنْبِرِينَ كَلامُ",
        "تلك العُيون قَصائد لَو تُرجمت\n لم يبق عند القائلين كلام.",
        "رماكَ الحاسدون بكل عيبِ..\nوعيبك أن حسنك لا يعابُ."
    ]
}
EMOTION_TRANSLATE = {
    "happy": "سعيد / مبتسم 😃",
    "sad": "متأثر / حزين 💔",
    "surprise": "مندهش 😲",
    "angry": "متجهم / غاضب 😠",
    "neutral": "هادئ / متزن 😐",
    "fear": "متأثر / حزين 💔",
    "disgust": "متجهم / غاضب 😠"
}

# =========================================================
# 6. التفاعل والصورة
# =========================================================
img_file_buffer = st.camera_input("التقط صورة لتفعيل التفاعل:")

st.markdown(
    """
    <div style="text-align: center; margin-top: 10px;">
        <span style="
            color: #d9534f; 
            background-color: rgba(217, 83, 79, 0.1); 
            border: 1px solid rgba(217, 83, 79, 0.3);
            padding: 6px 14px; 
            border-radius: 20px; 
            font-size: 0.88rem; 
            font-weight: bold; 
            display: inline-block;">
            🔒 تنويه الخصوصية: الصور تُحلل لحظياً داخل الذاكرة ولا يتم حفظها أو تخزينها مطلقاً.
        </span>
    </div>
    """, 
    unsafe_allow_html=True
)
if img_file_buffer is not None:
    bytes_data = img_file_buffer.getvalue()
    cv2_img = cv2.imdecode(np.frombuffer(bytes_data, np.uint8), cv2.IMREAD_COLOR)

    with st.spinner("جاري قراءة الملامح... ✨"):
        try:
            rgb_img = cv2.cvtColor(cv2_img, cv2.COLOR_BGR2RGB)
            results = DeepFace.analyze(
                img_path=rgb_img, 
                actions=['emotion'], 
                enforce_detection=False,
                detector_backend='skip'
            )

            raw_emotion = results[0]['dominant_emotion']
            
            # إعادة توجيه الحالات الفردية لترسيتها على الفئات الأساسية
            if raw_emotion == 'fear':
                detected_emotion = 'surprise'
            elif raw_emotion == 'disgust':
                detected_emotion = 'angry'
            else:
                detected_emotion = raw_emotion

            poem_list = POEMS.get(detected_emotion, POEMS["neutral"])
            selected_poem = random.choice(poem_list)
            translated_emotion = EMOTION_TRANSLATE.get(raw_emotion, "هادئ / متزن 😐")

            st.markdown(f'<div class="emotion-badge">التعبير المكتشف: {translated_emotion}</div>', unsafe_allow_html=True)

            formatted_poem = selected_poem.replace('\n', '<br>')
            st.markdown(f'''
                <div class="poem-card">
                    📜 البيت الشعري المناسب:<br><br>
                    "{formatted_poem}"
                </div>
            ''', unsafe_allow_html=True)

        except Exception as e:
            st.warning(f"حدث خطأ أثناء التحليل: {e}")
