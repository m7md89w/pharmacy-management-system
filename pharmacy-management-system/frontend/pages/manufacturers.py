from components.sidebar import render_sidebar
import pandas as pd
from services.api_client import delete, get, post, put
import streamlit as st

# ==========================================
# PAGE CONFIGURATION
# ==========================================
st.set_page_config(
    page_title="Manufacturers Management",
    page_icon="🏢",
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

st.title("🏢 Manufacturers Management")

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
# 1. CREATE MANUFACTURER EXPANDER
# ==========================================
with st.expander("➕ Add New Manufacturer"):
  col1, col2 = st.columns(2)
  with col1:
    name = st.text_input("Manufacturer Name *", key="man_name_input")
    contact_email = st.text_input("Contact Email", key="man_email_input")
  with col2:
    contact_phone = st.text_input("Contact Phone", key="man_phone_input")
    address = st.text_input("Address", key="man_address_input")

  if st.button("Save Manufacturer", type="primary"):
    if not name.strip():
      st.error("❌ Manufacturer name is required.")
    else:
      payload = {
          "name": name.strip(),
          "contact_email": contact_email.strip() if contact_email else "",
          "contact_phone": contact_phone.strip() if contact_phone else "",
          "address": address.strip() if address else "",
      }
      res = post("/manufacturers/", payload, token)
      if res.status_code == 201:
        st.success("✅ Manufacturer created successfully.")
        st.rerun()
      else:
        try:
          err = res.json().get("error", "Failed to create manufacturer.")
        except Exception:
          err = res.text
        st.error(err)


# ==========================================
# 2. VIEW & MANAGE MANUFACTURERS
# ==========================================
st.divider()
st.subheader("📋 Manufacturers List")

if st.button("🔄 Refresh Data"):
  st.rerun()

response = get("/manufacturers/", token)

if response.status_code == 200:
  manufacturers = response.json()
  if manufacturers:
    for m in manufacturers:
      with st.expander(
          f"🏢 {m.get('name')} (ID: {m.get('manufacturer_id')})"
      ):
        col1, col2, col3 = st.columns(3)
        with col1:
          st.write(f"📧 **Email:** {m.get('contact_email', 'N/A')}")
        with col2:
          st.write(f"📞 **Phone:** {m.get('contact_phone', 'N/A')}")
        with col3:
          st.write(f"📍 **Address:** {m.get('address', 'N/A')}")

        st.markdown("---")

        # Update Form inside Expander
        with st.form(key=f"update_man_form_{m['manufacturer_id']}"):
          st.write("✏️ **Update Manufacturer Details**")
          up_name = st.text_input("Name", value=m.get("name", ""))
          up_email = st.text_input(
              "Email", value=m.get("contact_email", "")
          )
          up_phone = st.text_input(
              "Phone", value=m.get("contact_phone", "")
          )
          up_address = st.text_input(
              "Address", value=m.get("address", "")
          )

          submitted = st.form_submit_button("Update Manufacturer")
          if submitted:
            update_payload = {
                "name": up_name.strip(),
                "contact_email": up_email.strip(),
                "contact_phone": up_phone.strip(),
                "address": up_address.strip(),
            }
            put_res = put(
                f"/manufacturers/{m['manufacturer_id']}", update_payload, token
            )
            if put_res.status_code == 200:
              st.success("✅ Manufacturer updated successfully.")
              st.rerun()
            else:
              try:
                err_msg = put_res.json().get(
                    "error", "Failed to update manufacturer."
                )
              except Exception:
                err_msg = put_res.text
              st.error(err_msg)

        if st.button("🗑️ Delete", key=f"del_man_{m['manufacturer_id']}"):
          del_res = delete(f"/manufacturers/{m['manufacturer_id']}", token)
          if del_res.status_code == 200:
            st.success("✅ Manufacturer deleted successfully.")
            st.rerun()
          else:
            try:
              err_msg = del_res.json().get(
                  "error", "Failed to delete manufacturer."
              )
            except Exception:
              err_msg = del_res.text
            st.error(err_msg)
  else:
    st.info("No manufacturers found in the system.")
else:
  st.error("Failed to load manufacturers from backend.")