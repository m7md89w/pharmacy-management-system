from datetime import datetime

import pandas as pd
import streamlit as st
from components.sidebar import render_sidebar
from services.api_client import get

st.set_page_config(
    page_title="Inventory Details & Batches",
    page_icon="🔍",
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

st.title("🔍 Medicine Batches & Inventory Details")

token = st.session_state.get("token") or st.session_state.get("access_token")

if not token:
  st.warning("⚠️ Please log in first to continue.")
  if st.button("Go to Login / Main Page"):
    st.switch_page("app.py")
  st.stop()

med_id = st.session_state.get("selected_inventory_medicine")

if not med_id:
  st.warning("⚠️ No medicine selected. Please select a medicine from the inventory overview.")
  if st.button("⬅️ Back to Inventory Overview"):
    st.switch_page("pages/inventory.py")
  st.stop()

with st.spinner("Fetching medicine and batches details..."):
  med_response = get(f"/medicines/{med_id}", token=token)
  batches_response = get(f"/batches/medicine/{med_id}", token=token)

if med_response.status_code != 200:
  st.error("Failed to load medicine details from the server.")
  if st.button("⬅️ Back to Inventory Overview"):
    st.switch_page("pages/inventory.py")
  st.stop()

medicine = med_response.json()
batches = batches_response.json() if batches_response.status_code == 200 else []

commercial_name = medicine.get("commercial_name", "Unknown")
scientific_name = medicine.get("scientific_name", "Unknown")
barcode = medicine.get("barcode") or "Not Registered"
category = medicine.get("category_name", "General")

st.info(
    f"📦 **Commercial Name:** {commercial_name}  \n"
    f"🧪 **Scientific Name:** {scientific_name}  \n"
    f"🏷️ **Barcode:** `{barcode}` | 📁 **Category:** {category}"
)

st.divider()

col_f1, col_f2, col_f3 = st.columns([2, 1, 1])

with col_f1:
  batch_search = st.text_input("🔍 Search by Batch Number", "").strip().lower()

with col_f2:
  status_filter = st.selectbox(
      "Filter by Status:",
      ["All Batches", "Valid", "Expired / Damaged"]
  )

with col_f3:
  st.write("")
  st.write("")
  st.write(f"**Total Batches:** {len(batches)}")

today_str = datetime.now().strftime("%Y-%m-%d")  # noqa: DTZ005
filtered_batches = []

for b in batches:
  b_num = str(b.get("batch_number", "")).lower()
  exp_date = b.get("expiry_date") or ""

  is_expired = exp_date != "" and exp_date != "—" and exp_date < today_str

  if batch_search and batch_search not in b_num:
    continue

  if status_filter == "Valid" and is_expired or status_filter == "Expired / Damaged" and not is_expired:
    continue

  filtered_batches.append(b)

st.subheader(f"📋 Batches Records ({len(filtered_batches)})")

if not filtered_batches:
  st.warning("No batches found matching your search and filter criteria.")
else:
  batch_rows = []
  for b in filtered_batches:
    exp_date = b.get("expiry_date") or "—"
    mfg_date = b.get("manufacture_date") or "—"
    is_expired = exp_date != "—" and exp_date < today_str
    qty = b.get("quantity", 0)

    purchase_price = b.get("purchase_price")
    selling_price = b.get("selling_price")

    batch_rows.append({
        "Batch ID": b.get("batch_id"),
        "Batch Number": b.get("batch_number") or "—",
        "Quantity": qty,
        "Purchase Price": f"{float(purchase_price):.2f} JOD" if purchase_price is not None else "—",
        "Selling Price": f"{float(selling_price):.2f} JOD" if selling_price is not None else "—",
        "Manufacture Date": mfg_date,
        "Expiry Date": exp_date,
        "Status": "Expired ⚠️" if is_expired else "Valid ✅",
    })

  df_batches = pd.DataFrame(batch_rows)
  st.dataframe(df_batches, use_container_width=True, hide_index=True)

st.divider()

if st.button("⬅️ Back to Inventory Overview", use_container_width=True):
  st.switch_page("pages/inventory.py")