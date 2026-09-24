from components.sidebar import render_sidebar
import pandas as pd
from services.api_client import delete, get, post, put
import streamlit as st

# ==========================================
# PAGE CONFIGURATION
# ==========================================
st.set_page_config(
    page_title="Prescription Details",
    page_icon="📜",
    layout="wide",
    initial_sidebar_state="expanded",
)

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

# ==========================================
# AUTHENTICATION CHECK
# ==========================================
token = st.session_state.get("token") or st.session_state.get("access_token")

if not token:
    st.warning("⚠️ Please log in first.")
    if st.button("Go to Login"):
        st.switch_page("app.py")
    st.stop()

prescription_id = st.session_state.get("selected_prescription_id")

if not prescription_id:
    st.warning("⚠️ No prescription selected.")
    if st.button("Back to Prescriptions"):
        st.switch_page("pages/prescriptions.py")
    st.stop()

st.title(f"📜 Prescription Details #{prescription_id}")

if st.button("⬅️ Back to Prescriptions"):
    st.switch_page("pages/prescriptions.py")

st.divider()

# جلب الأدوية لتعبئة القائمة
medicines_res = get("/medicines/", token)
medicines_map = {}
id_to_med_name = {}
if medicines_res.status_code == 200:
    for m in medicines_res.json():
        c_name = m.get('commercial_name')
        s_name = m.get('scientific_name')
        mid = m.get("id")
        display_name = f"{c_name} ({s_name})"
        medicines_map[display_name] = mid
        id_to_med_name[mid] = c_name  # الاسم للفحص

# جلب بيانات الوصفة الأساسية من الـ Backend (المصدر الوحيد للحقيقة)
res = get(f"/prescriptions/{prescription_id}", token)
if res.status_code == 200:
    p = res.json()

    col1, col2, col3 = st.columns(3)
    with col1:
        st.write(f"🩺 **Doctor Name:** {p.get('doctor_name', 'N/A')}")
        st.write(f"🆔 **Customer ID:** {p.get('customer_id', 'N/A')}")
    with col2:
        st.write(f"📅 **Issue Date:** {p.get('issue_date', 'N/A')}")
    with col3:
        st.write(f"🖼️ **Image:** {p.get('prescription_image', 'None Provided')}")

    if p.get("notes"):
        st.info(f"📝 **Notes:** {p.get('notes')}")

    st.divider()
    
    # رأس القسم مع زر الفحص اليدوي (On-Demand Check Button)
    col_head_title, col_head_btn = st.columns([3, 1])
    with col_head_title:
        st.subheader("💊 Prescription Items")
    with col_head_btn:
        check_interactions_clicked = st.button("🔄 Check Interactions", type="secondary", use_container_width=True)

    # جلب عناصر الوصفة (الأدوية)
    items_res = get(f"/prescription-items/prescription/{prescription_id}", token)
    if items_res.status_code == 200:
        items = items_res.json()
        
        # تنفيذ الفحص حصرياً عند الضغط على زر التحقق
        if check_interactions_clicked:
            if not items or len(items) < 2:
                st.warning("⚠️ يلزم وجود دواءين على الأقل في الروشتة لفحص التعارضات.")
            else:
                prescription_drug_names = [
                    id_to_med_name.get(item.get("medicine_id"))
                    for item in items
                    if id_to_med_name.get(item.get("medicine_id"))
                ]

                if len(prescription_drug_names) >= 2:
                    with st.spinner("جاري فحص التداخلات الدوائية عبر السيرفر..."):
                        interaction_payload = {
                            "current_drugs": prescription_drug_names,
                            "new_drugs": []
                        }
                        int_res = post("/drug-interactions/check", interaction_payload, token)

                        if int_res.status_code == 200:
                            int_data = int_res.json()
                            interactions = int_data.get("interactions", [])
                            unchecked_drugs = int_data.get("unchecked_drugs", [])

                            if unchecked_drugs:
                                st.warning(
                                    f"⚠️ تعذّر التحقق الكامل من التعارضات لبعض الأدوية: {', '.join(unchecked_drugs)}"
                                )

                            if interactions:
                                st.error(f"🚨 تحذير خطير: تم اكتشاف {len(interactions)} تداخل دوائي محتمل بين أدوية هذه الروشتة!")
                                for inter in interactions:
                                    with st.expander(f"⚠️ تعارض: {inter['drug1']} ↔️ {inter['drug2']}", expanded=True):
                                        st.markdown(f"**التفاصيل:** {inter['description']}")
                                        st.caption(f"📄 المصدر: {inter.get('source', 'openFDA')}")
                                        st.warning(f"💡 **نوع التعارض:** {inter.get('relation_label')}")
                            else:
                                st.success("✅ لم يتم العثور على أي تداخل دوائي صريح بين أدوية هذه الروشتة.")
                        else:
                            st.error("❌ فشل الاتصال بخدمة فحص التداخلات.")

        if items:
            for item in items:
                med_name_display = f"Medicine ID: {item.get('medicine_id')}"
                for mname, mid in medicines_map.items():
                    if mid == item.get("medicine_id"):
                        med_name_display = mname
                        break

                # تقسيم الصف لعرض تفاصيل الدواء مع زر الحذف الخاص به
                col_item_info, col_item_del = st.columns([5, 1])
                with col_item_info:
                    st.markdown(
                        f"- **Medicine:** {med_name_display} | **Dosage:**"
                        f" {item.get('dosage')} | **Frequency:**"
                        f" {item.get('frequency')} | **Duration:**"
                        f" {item.get('duration')} | **Notes:**"
                        f" {item.get('notes', 'N/A')}"
                    )
                with col_item_del:
                    if st.button("🗑️ Delete", key=f"del_item_{item['prescription_item_id']}"):
                        del_item_res = delete(
                            f"/prescription-items/{item['prescription_item_id']}", token
                        )
                        if del_item_res.status_code == 200:
                            st.success("✅ Item deleted successfully.")
                            st.rerun()
                        else:
                            try:
                                err_msg = del_item_res.json().get(
                                    "error", "Failed to delete item."
                                )
                            except Exception:
                                err_msg = del_item_res.text
                            st.error(err_msg)
        else:
            st.info("No items added to this prescription yet.")
    else:
        st.error("Failed to load prescription items.")

    st.divider()

    # نموذج إضافة دواء جديد للروشتة
    with st.form(key=f"detail_add_item_form_{prescription_id}"):
        st.write("➕ **Add Medicine Item to Prescription**")
        item_med_name = st.selectbox(
            "Select Medicine",
            options=list(medicines_map.keys())
            if medicines_map
            else ["No Medicines Available"],
        )
        item_dosage = st.text_input("Dosage (e.g., 500mg)")
        item_frequency = st.text_input("Frequency (e.g., Twice daily)")
        item_duration = st.text_input("Duration (e.g., 5 days)")
        item_notes = st.text_input("Item Notes")

        if st.form_submit_button("Add Item"):
            if not medicines_map or item_med_name == "No Medicines Available":
                st.error("❌ Please select a valid medicine.")
            else:
                item_payload = {
                    "prescription_id": int(prescription_id),
                    "medicine_id": int(medicines_map[item_med_name]),
                    "dosage": item_dosage.strip() if item_dosage else "",
                    "frequency": item_frequency.strip() if item_frequency else "",
                    "duration": item_duration.strip() if item_duration else "",
                    "notes": item_notes.strip() if item_notes else "",
                }
                item_res = post("/prescription-items/", item_payload, token)
                if item_res.status_code == 201:
                    st.success("✅ Item added successfully.")
                    st.rerun()
                else:
                    try:
                        err_msg = item_res.json().get("error", "Failed to add item.")
                    except Exception:
                        err_msg = item_res.text
                    st.error(err_msg)

    st.divider()

    # نموذج تحديث بيانات الروشتة الأساسية
    with st.form(key=f"detail_update_form_{prescription_id}"):
        st.write("✏️ **Update Prescription Details**")
        up_doctor = st.text_input("Doctor Name", value=p.get("doctor_name", ""))
        up_image = st.text_input(
            "Prescription Image", value=p.get("prescription_image", "")
        )
        up_notes = st.text_input("Notes", value=p.get("notes", ""))

        if st.form_submit_button("Update Prescription"):
            update_payload = {
                "doctor_name": up_doctor.strip(),
                "prescription_image": up_image.strip(),
                "notes": up_notes.strip(),
            }
            put_res = put(f"/prescriptions/{prescription_id}", update_payload, token)
            if put_res.status_code == 200:
                st.success("✅ Prescription updated successfully.")
                st.rerun()
            else:
                try:
                    err_msg = put_res.json().get(
                        "error", "Failed to update prescription."
                    )
                except Exception:
                    err_msg = put_res.text
                st.error(err_msg)

    if st.button("🗑️ Delete Prescription"):
        del_res = delete(f"/prescriptions/{prescription_id}", token)
        if del_res.status_code == 200:
            st.success("✅ Prescription deleted successfully.")
            st.session_state.selected_prescription_id = None
            st.switch_page("pages/prescriptions.py")
        else:
            try:
                err_msg = del_res.json().get("error", "Failed to delete prescription.")
            except Exception:
                err_msg = del_res.text
            st.error(err_msg)
else:
    st.error("Failed to load prescription details.")