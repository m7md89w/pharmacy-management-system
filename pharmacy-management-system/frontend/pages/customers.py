from components.sidebar import render_sidebar
import pandas as pd
from services.api_client import delete, get, post, put
import streamlit as st

# ==========================================
# PAGE CONFIGURATION
# ==========================================
st.set_page_config(
    page_title="Customers Management",
    page_icon="📇",
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

st.title("📇 Customers Management")

# ==========================================
# AUTHENTICATION CHECK
# ==========================================
token = st.session_state.get("token") or st.session_state.get("access_token")

if not token:
  st.warning("⚠️ Please log in first.")
  if st.button("Go to Login"):
    st.switch_page("app.py")
  st.stop()

if "edit_customer" not in st.session_state:
  st.session_state.edit_customer = None


# ==========================================
# CREATE CUSTOMER EXPANDER
# ==========================================
with st.expander("➕ Add New Customer"):
  col1, col2 = st.columns(2)
  with col1:
    full_name = st.text_input("Full Name", key="cust_fname")
    phone = st.text_input("Phone", key="cust_phone")
  with col2:
    email = st.text_input("Email", key="cust_email")
    loyalty_points = st.number_input(
        "Loyalty Points", min_value=0, value=0, step=1, key="cust_points"
    )

  if st.button("Create Customer", type="primary"):
    if not full_name.strip():
      st.error("❌ Full Name is required.")
    else:
      data = {
          "full_name": full_name.strip(),
          "phone": phone.strip() if phone else "",
          "email": email.strip() if email else "",
          "loyalty_points": int(loyalty_points),
      }
      res = post("/customers/", data, token)
      if res.status_code == 201:
        st.success("✅ Customer created successfully.")
        st.rerun()
      else:
        try:
          error_msg = res.json().get("error", "Failed to create customer.")
        except Exception:
          error_msg = res.text
        st.error(error_msg)


# ==========================================
# EDIT CUSTOMER SECTION
# ==========================================
if st.session_state.edit_customer:
  c = st.session_state.edit_customer
  st.divider()
  st.subheader(f"✏️ Edit Customer: {c.get('full_name', '')}")

  e_fname = st.text_input(
      "Full Name", value=c.get("full_name", ""), key="edit_cust_fname"
  )
  e_phone = st.text_input(
      "Phone", value=c.get("phone", ""), key="edit_cust_phone"
  )
  e_email = st.text_input(
      "Email", value=c.get("email", ""), key="edit_cust_email"
  )
  e_points = st.number_input(
      "Loyalty Points",
      value=int(c.get("loyalty_points", 0)),
      min_value=0,
      step=1,
      key="edit_cust_points",
  )

  col1, col2 = st.columns(2)
  with col1:
    if st.button("💾 Save Changes"):
      if not e_fname.strip():
        st.error("❌ Full Name is required.")
      else:
        payload = {
            "full_name": e_fname.strip(),
            "phone": e_phone.strip() if e_phone else "",
            "email": e_email.strip() if e_email else "",
            "loyalty_points": int(e_points),
        }
        res = put(f"/customers/{c['customer_id']}", payload, token)
        if res.status_code == 200:
          st.success("✅ Customer updated successfully.")
          st.session_state.edit_customer = None
          st.rerun()
        else:
          try:
            error_msg = res.json().get("error", "Failed to update customer.")
          except Exception:
            error_msg = res.text
          st.error(error_msg)

  with col2:
    if st.button("❌ Cancel"):
      st.session_state.edit_customer = None
      st.rerun()


# ==========================================
# SEARCH & CUSTOMERS LIST
# ==========================================
st.divider()
search_query = st.text_input(
    "🔍 Search by Name or Phone", placeholder="Type name or phone..."
)

if st.button("🔄 Refresh"):
  st.rerun()

response = get("/customers/", token)

if response.status_code == 200:
  customers = response.json()

  if search_query:
    query = search_query.strip().lower()
    customers = [
        cust
        for cust in customers
        if query in str(cust.get("full_name", "")).lower()
        or query in str(cust.get("phone", "")).lower()
    ]

  st.subheader(f"📋 Customers List ({len(customers)})")

  if customers:
    for cust in customers:
      # استخدام expander لعرض تفاصيل العميل والروشتات الخاصة به
      with st.expander(
          f"👤 {cust.get('full_name', 'N/A')} — Phone: {cust.get('phone', 'N/A')}"
      ):
        col_a, col_b = st.columns(2)
        with col_a:
          st.write(f"📧 **Email:** {cust.get('email', 'N/A')}")
        with col_b:
          st.write(f"⭐ **Loyalty Points:** {cust.get('loyalty_points', 0)}")

        st.markdown("---")
        st.subheader("📜 Customer Prescriptions")

        # جلب الـ Prescriptions الخاصة بهذا العميل من الـ Backend
        pres_res = get(
            f"/prescriptions/customer/{cust.get('customer_id')}", token
        )
        if pres_res.status_code == 200:
          cust_prescriptions = pres_res.json()
          if cust_prescriptions:
            for cp in cust_prescriptions:
              col_cp1, col_cp2 = st.columns([4, 1])
              with col_cp1:
                st.markdown(
                    f"- **Prescription #{cp.get('prescription_id')}** | Dr."
                    f" {cp.get('doctor_name')} | Date:"
                    f" {cp.get('issue_date', 'N/A')}"
                )
              with col_cp2:
                if st.button(
                    "🔍 View", key=f"cust_pres_btn_{cp.get('prescription_id')}"
                ):
                  st.session_state.selected_prescription_id = cp.get(
                      "prescription_id"
                  )
                  st.switch_page("pages/prescription_detail.py")
          else:
            st.info("No prescriptions found for this customer.")
        else:
          st.error("Failed to load customer prescriptions.")

        st.markdown("---")

        # أزرار التعديل والحذف للعميل داخل الـ Expander
        col1, col2 = st.columns(2)
        with col1:
          if st.button("✏️ Edit Customer", key=f"edit_cust_{cust['customer_id']}"):
            st.session_state.edit_customer = cust
            st.rerun()
        with col2:
          if st.button("🗑️ Delete Customer", key=f"del_cust_{cust['customer_id']}"):
            res = delete(f"/customers/{cust['customer_id']}", token)
            if res.status_code == 200:
              st.success("✅ Customer deleted successfully.")
              st.rerun()
            else:
              try:
                error_msg = res.json().get(
                    "error", "Failed to delete customer."
                )
              except Exception:
                error_msg = res.text
              st.error(error_msg)

      st.divider()
  else:
    st.info("No customers found matching your search.")
else:
  st.error("Failed to load customers from backend.")