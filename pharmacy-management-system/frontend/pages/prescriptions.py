from components.sidebar import render_sidebar
import pandas as pd
from services.api_client import delete, get, post, put
import streamlit as st

# ==========================================
# PAGE CONFIGURATION
# ==========================================
st.set_page_config(
    page_title="Prescriptions Management",
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

st.title("📜 Prescriptions Management")

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
# FETCH CUSTOMERS FOR MAPPINGS
# ==========================================
customers_res = get("/customers/", token)
customers_map = {}
if customers_res.status_code == 200:
  customers_map = {
      f"{c.get('full_name')} (ID: {c.get('customer_id')})": c.get("customer_id")
      for c in customers_res.json()
  }


# ==========================================
# 1. CREATE PRESCRIPTION EXPANDER
# ==========================================
with st.expander("➕ Add New Prescription"):
  col1, col2 = st.columns(2)
  with col1:
    cust_options = (
        list(customers_map.keys()) if customers_map else ["No Customers Found"]
    )
    selected_customer = st.selectbox("Customer *", options=cust_options)
    doctor_name = st.text_input("Doctor Name *", key="pres_doctor_input")
  with col2:
    issue_date = st.date_input("Issue Date", key="pres_date_input")
    prescription_image = st.text_input(
        "Prescription Image URL / Path", key="pres_image_input"
    )

  notes = st.text_area("Notes", key="pres_notes_input")

  if st.button("Save Prescription", type="primary"):
    if not customers_map or selected_customer == "No Customers Found":
      st.error(
          "❌ Please select a valid customer (or add one in Customers page)."
      )
    elif not doctor_name.strip():
      st.error("❌ Doctor name is required.")
    else:
      payload = {
          "customer_id": int(customers_map[selected_customer]),
          "doctor_name": doctor_name.strip(),
          "prescription_image": prescription_image.strip()
          if prescription_image
          else "",
          "issue_date": str(issue_date),
          "notes": notes.strip() if notes else "",
      }
      res = post("/prescriptions/", payload, token)
      if res.status_code == 201:
        st.success("✅ Prescription created successfully.")
        st.rerun()
      else:
        try:
          err = res.json().get("error", "Failed to create prescription.")
        except Exception:
          err = res.text
        st.error(err)


# ==========================================
# 2. VIEW PRESCRIPTIONS LIST (Clean View)
# ==========================================
st.divider()
st.subheader("📋 Prescriptions List")

if st.button("🔄 Refresh Data"):
  st.rerun()

response = get("/prescriptions/", token)

if response.status_code == 200:
  prescriptions = response.json()
  if prescriptions:
    for p in prescriptions:
      cust_name_display = f"Customer ID: {p.get('customer_id')}"
      for name, cid in customers_map.items():
        if cid == p.get("customer_id"):
          cust_name_display = name
          break

      col_info1, col_info2, col_action = st.columns([3, 3, 1])
      with col_info1:
        st.write(
            f"📜 **Prescription #{p.get('prescription_id')}** — Dr."
            f" {p.get('doctor_name')}"
        )
        st.caption(f"Patient: {cust_name_display}")
      with col_info2:
        st.write(f"📅 **Date:** {p.get('issue_date', 'N/A')}")
        st.caption(f"Notes: {p.get('notes', 'No notes')}")
      with col_action:
        # التصحيح هنا: استخدام المسار الصحيح مع امتداد .py
        if st.button("🔍 Details", key=f"view_detail_{p['prescription_id']}"):
          st.session_state.selected_prescription_id = p["prescription_id"]
          st.switch_page("pages/prescription_detail.py")
      st.divider()
  else:
    st.info("No prescriptions found in the system.")
else:
  st.error("Failed to load prescriptions from backend.")