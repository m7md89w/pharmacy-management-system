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

# تهيئة القائمة وحقل النص المؤقت في session_state
if "current_meds_list" not in st.session_state:
    st.session_state["current_meds_list"] = []

if "temp_drug_input_val" not in st.session_state:
    st.session_state["temp_drug_input_val"] = ""

# دالة لإضافة الدواء وتفريغ حقل الإدخال
def add_drug_callback():
    drug_clean = st.session_state.get("temp_drug_input_field", "").strip()
    if drug_clean:
        if drug_clean not in st.session_state["current_meds_list"]:
            st.session_state["current_meds_list"].append(drug_clean)
            # تفريغ مفتاح الحقل ليمسح التيكست بوكس
            st.session_state["temp_drug_input_field"] = ""
        else:
            st.warning("هذا الدواء موجود مسبقاً في القائمة.")

# ==========================================
# DRUG INPUT SECTION
# ==========================================
with st.expander("🔍 Enter Medications for Checking", expanded=True):
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**أدوية المريض الحالية (Current Medications):**")
        
        # حقل إدخال مع ربطه بـ key وإضافة دواء عبر زر (+) أو Enter
        col_input, col_add_btn = st.columns([4, 1])
        with col_input:
            st.text_input(
                "أضف دواء حالي:",
                placeholder="مثال: Warfarin",
                label_visibility="collapsed",
                key="temp_drug_input_field"
            )
        with col_add_btn:
            # استخدام on_click أو زر عادي يستدعي الدالة لتفريغ الحقل
            if st.button("➕ إضافة", use_container_width=True, on_click=add_drug_callback):
                pass

        # عرض الأدوية الحالية المضافة مع زر حذف (-) بجانب كل دواء
        if st.session_state["current_meds_list"]:
            st.markdown("---")
            st.caption("الأدوية الحالية المسجلة:")
            for idx, med in enumerate(st.session_state["current_meds_list"]):
                c_name, c_del = st.columns([5, 1])
                with c_name:
                    st.markdown(f"• {med}")
                with c_del:
                    if st.button("➖", key=f"del_med_{idx}", use_container_width=True):
                        st.session_state["current_meds_list"].pop(idx)
                        st.rerun()
        else:
            st.info("لم يتم إضافة أي أدوية حالية بعد.")

    with col2:
        st.markdown("**الدواء الجديد (New Medication):**")
        new_drug_input = st.text_input(
            "الدواء الجديد المراد فحصه:",
            placeholder="مثال: Ibuprofen",
            help="أدخل دواءً جديداً واحداً فقط لفحصه ضد أدوية المريض الحالية",
            key="single_new_drug_input"
        )

    st.divider()
    check_btn = st.button("فحص التعارضات (Check Interactions)", type="primary", use_container_width=True)

# ==========================================
# RESULTS DISPLAY
# ==========================================
if check_btn:
    current_drugs = st.session_state["current_meds_list"]
    new_drugs = [new_drug_input.strip()] if new_drug_input.strip() else []
    total_count = len(current_drugs) + len(new_drugs)

    if not current_drugs:
        st.warning("⚠️ الرجاء إضافة دواء واحد على الأقل لأدوية المريض الحالية.")
    elif not new_drugs:
        st.warning("⚠️ الرجاء إدخال الدواء الجديد المراد فحصه.")
    elif total_count < 2:
        st.warning("⚠️ يلزم إدخال دواءين إجمالياً على الأقل لإجراء الفحص (أدوية حالية ودواء جديد).")
    else:
        payload = {
            "current_drugs": current_drugs,
            "new_drugs": new_drugs
        }

        with st.spinner("جاري الاستعلام عن التداخلات بين الأدوية..."):
            res = post("/drug-interactions/check", payload, token)

            if res.status_code == 200:
                data = res.json()
                interactions = data.get("interactions", [])
                unchecked_drugs = data.get("unchecked_drugs", [])

                if unchecked_drugs:
                    st.warning(
                        "⚠️ تعذّر التحقق الكامل من التعارضات — فشل الاتصال بمصدر "
                        f"البيانات (openFDA/RxNorm) للأدوية التالية: **{', '.join(unchecked_drugs)}**. "
                        "النتيجة أدناه غير مكتملة ولا يجب الاعتماد عليها وحدها كفحص آمن."
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