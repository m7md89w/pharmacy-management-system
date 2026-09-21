import streamlit as st
from components.sidebar import render_sidebar
from services.api_client import post

# ==========================================
# PAGE CONFIGURATION
# ==========================================
st.set_page_config(
    page_title="Drug Interactions",
    page_icon="💊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ==========================================
# إخفاء القائمة الجانبية الافتراضية
# ==========================================
st.markdown(
    """
    <style>
        [data-testid="stSidebarNav"] {
            display: none !important;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

render_sidebar()

st.title("💊 Drug Interactions")
st.markdown(
    "فحص التداخلات الدوائية بالاعتماد على نص \"Drug Interactions\" الرسمي من نشرات "
    "الأدوية المعتمدة من FDA (openFDA)، مع توحيد أسماء الأدوية عبر RxNorm."
)
st.caption(
    "⚠️ هذا فحص مساعد (اجتهادي) مبني على نص حر من نشرات الدواء، وليس بديلاً عن "
    "مصدر سريري مرخّص أو عن تقييم الصيدلي/الطبيب."
)

# ==========================================
# AUTHENTICATION CHECK
# ==========================================
token = st.session_state.get("token") or st.session_state.get("access_token")

if not token:
    st.warning("⚠️ Please log in first.")
    if st.button("Go to Login"):
        st.switch_page("app.py")
    st.stop()

# ==========================================
# DRUG INPUT SECTION
# ==========================================
with st.expander("🔍 Enter Medications for Checking", expanded=True):
    col1, col2 = st.columns(2)

    with col1:
        current_drugs_input = st.text_input(
            "أدوية المريض الحالية (Current Medications):",
            placeholder="مثال: Warfarin, Aspirin",
            help="الأدوية المزمنة أو المستمرة التي يتناولها المريض حالياً. افصل بينها بفاصلة (,)"
        )

    with col2:
        new_drugs_input = st.text_input(
            "الأدوية الجديدة (New Prescription):",
            placeholder="مثال: Ibuprofen",
            help="الأدوية الجديدة المراد إضافتها للمريض. افصل بينها بفاصلة (,)"
        )

    st.divider()
    check_btn = st.button("فحص التعارضات (Check Interactions)", type="primary", use_container_width=True)

# ==========================================
# RESULTS DISPLAY
# ==========================================
if check_btn:
    current_drugs = [d.strip() for d in current_drugs_input.split(",") if d.strip()]
    new_drugs = [d.strip() for d in new_drugs_input.split(",") if d.strip()]
    total_count = len(current_drugs) + len(new_drugs)

    if not new_drugs:
        st.warning("⚠️ الرجاء إدخال دواء جديد واحد على الأقل في خانة الأدوية الجديدة.")
    elif total_count < 2:
        st.warning("⚠️ يلزم إدخال دواءين على الأقل لإجراء فحص التداخلات.")
    else:
        payload = {
            "current_drugs": current_drugs,
            "new_drugs": new_drugs
        }

        with st.spinner("جاري الاستعلام عن التداخلات..."):
            # استدعاء الـ Backend عبر الـ API Client المعتمد في المشروع
            res = post("/drug-interactions/check", payload, token)

            if res.status_code == 200:
                data = res.json()
                interactions = data.get("interactions", [])
                unchecked_drugs = data.get("unchecked_drugs", [])

                # لازم نعرض هاد التحذير *قبل* أي رسالة نجاح/أمان، لأنه لو في
                # أدوية ما قدرنا نتحقق منها فعلياً (فشل اتصال بـ openFDA/RxNorm)،
                # رسالة "✅ آمن" بتكون مضلِّلة — الفحص ناقص مش نتيجته "لا تعارض".
                if unchecked_drugs:
                    st.warning(
                        "⚠️ تعذّر التحقق الكامل من التعارضات — فشل الاتصال بمصدر "
                        f"البيانات (openFDA/RxNorm) للأدوية التالية: **{', '.join(unchecked_drugs)}**. "
                        "النتيجة أدناه غير مكتملة ولا يجب الاعتماد عليها وحدها كفحص آمن. "
                        "تأكد من اتصال الإنترنت بالسيرفر ثم أعد المحاولة."
                    )

                if not interactions:
                    if unchecked_drugs:
                        st.info("لم يتم العثور على تعارض ضمن الأدوية التي *تم* التحقق منها فقط.")
                    else:
                        st.success("✅ لم يتم العثور على أي ذكر صريح لتعارض بين هذه الأدوية في نشرات FDA.")
                else:
                    st.error(f"⚠️ تحذير: تم اكتشاف {len(interactions)} تفاعل دوائي محتمل!")

                    for item in interactions:
                        with st.expander(f"⚠️ تعارض: {item['drug1']} ↔️ {item['drug2']}", expanded=True):
                            st.markdown(f"**التفاصيل:** {item['description']}")
                            st.caption(f"📄 المصدر: {item.get('source', 'openFDA')}")
                            st.caption(f"🏷️ الخطورة: {item.get('severity', 'غير مصنّف')}")

                            if item.get("relation_type") == "CURRENT_VS_NEW":
                                st.info(f"💡 **نوع التعارض:** {item.get('relation_label')}")
                            elif item.get("relation_type") == "NEW_VS_NEW":
                                st.warning(f"🚨 **نوع التعارض:** {item.get('relation_label')}")
                            else:
                                st.caption(f"ℹ️ **نوع التعارض:** {item.get('relation_label')}")
            else:
                try:
                    error_msg = res.json().get("error", "Failed to check interactions.")
                except Exception:
                    error_msg = res.text
                st.error(f"❌ Server Error: {error_msg}")