from components.sidebar import render_sidebar
import pandas as pd
from services.api_client import delete, get, post, put
import streamlit as st

# ==========================================
# PAGE CONFIGURATION
# ==========================================
st.set_page_config(
    page_title="Expired Medicines Management",
    page_icon="⚠️",
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

st.title("⚠️ Expired & Damaged Medicines Management")

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
# FETCH MASTER DATA (Medicines & Batches)
# ==========================================
medicines_res = get("/medicines/", token)
medicines_map = {}
if medicines_res.status_code == 200:
  medicines_map = {
      m["commercial_name"] + f" ({m.get('scientific_name', '')})": m["id"]
      for m in medicines_res.json()
  }

batches_res = get("/batches/", token)
batches_data = batches_res.json() if batches_res.status_code == 200 else []


# ==========================================
# 1. CREATE EXPIRED RECORD HEADER
# ==========================================
with st.expander("➕ Create New Expired Record (Header)"):
  notes = st.text_input(
      "General Notes / Reason (e.g., Routine check, damaged batch)",
      key="exp_notes_input",
  )

  if st.button("Create Record Header", type="primary"):
    data = {"notes": notes.strip() if notes else ""}
    res = post("/expired-medicines/", data, token)
    if res.status_code == 201:
      st.success("✅ Expired record header created successfully.")
      st.rerun()
    else:
      try:
        err = res.json().get("error", "Failed to create record.")
      except Exception:
        err = res.text
      st.error(err)


# ==========================================
# 2. ADD EXPIRED ITEMS TO A RECORD
# ==========================================
st.divider()
st.subheader("📦 Add Expired/Damaged Item & Deduct Stock")

expired_records_res = get("/expired-medicines/", token)
expired_records = (
    expired_records_res.json()
    if expired_records_res.status_code == 200
    else []
)

if expired_records:
  record_options = {
      f"Record ID: {r['expired_id']} | Notes: {r.get('notes', 'N/A')}": r[
          "expired_id"
      ]
      for r in expired_records
  }
  selected_record_label = st.selectbox(
      "Select Expired Record", options=list(record_options.keys())
  )
  selected_expired_id = record_options[selected_record_label]

  col1, col2, col3 = st.columns(3)
  with col1:
    sel_med_label = st.selectbox(
        "Select Medicine",
        options=list(medicines_map.keys())
        if medicines_map
        else ["No Medicines"],
    )
  with col2:
    selected_med_id = (
        medicines_map.get(sel_med_label) if medicines_map else None
    )
    filtered_batches = (
        [b for b in batches_data if b.get("medicine_id") == selected_med_id]
        if selected_med_id
        else batches_data
    )

    batch_options = {
        f"Batch #{b.get('batch_id')} (Code: {b.get('batch_number')} | Available: {b.get('quantity')})": b[
            "batch_id"
        ]
        for b in filtered_batches
    }
    sel_batch_label = st.selectbox(
        "Select Batch",
        options=list(batch_options.keys()) if batch_options else ["No Batches"],
    )
    selected_batch_id = (
        batch_options.get(sel_batch_label) if batch_options else None
    )

  with col3:
    quantity = st.number_input(
        "Quantity to Waste", min_value=1, value=1, step=1
    )

  item_reason = st.text_input(
      "Item Reason / Notes (e.g., Expired, Damaged shelf item)",
      key="item_reason_input",
  )

  if st.button("Submit Item & Update Stock", type="primary"):
    if not selected_med_id or not selected_batch_id:
      st.error("❌ Please select a valid medicine and batch.")
    else:
      item_payload = {
          "expired_id": int(selected_expired_id),
          "medicine_id": int(selected_med_id),
          "batch_id": int(selected_batch_id),
          "quantity": int(quantity),
          "reason": item_reason.strip() if item_reason else "",
      }
      item_res = post("/expired-medicine-items/", item_payload, token)
      if item_res.status_code == 201:
        st.success(
            "✅ Expired item logged successfully, batch and inventory updated"
            " securely!"
        )
        st.rerun()
      else:
        try:
          err_msg = item_res.json().get("error", "Failed to add item.")
        except Exception:
          err_msg = item_res.text
        st.error(err_msg)
else:
  st.info("ℹ️ Please create an expired record header first above.")


# ==========================================
# 3. VIEW RECORDS AND THEIR ITEMS HISTORY
# ==========================================
st.divider()
st.subheader("📋 Expired Records & Items History")

if st.button("🔄 Refresh Data"):
  st.rerun()

if expired_records:
  for rec in expired_records:
    with st.expander(
        f"📁 Record ID: {rec.get('expired_id')} | User ID:"
        f" {rec.get('user_id')}"
    ):
      st.write(f"**General Notes:** {rec.get('notes', 'No notes')}")

      # جلب العناصر التابعة لهذا السجل عبر الـ Endpoint المرتبط بالكنترولر
      items_res = get(
          f"/expired-medicine-items/expired/{rec.get('expired_id')}", token
      )
      if items_res.status_code == 200:
        items = items_res.json()
        if items:
          st.markdown("---")
          st.markdown("**Logged Items in this Record:**")
          df_items = pd.DataFrame(items)
          st.dataframe(df_items, use_container_width=True)
        else:
          st.info("No items logged under this record yet.")
      else:
        st.caption("Could not load items for this record.")
else:
  st.info("No expired records found in the system.")