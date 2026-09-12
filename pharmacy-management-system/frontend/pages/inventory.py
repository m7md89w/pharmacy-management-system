from datetime import datetime

import streamlit as st
from components.sidebar import render_sidebar
from services.api_client import get

st.set_page_config(
    page_title="Inventory Overview",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ==================================================
# إخفاء القائمة الجانبية الافتراضية لملفات الصفحات في Streamlit
# ==================================================
st.markdown(
    """
    <style>
        /* إخفاء قائمة التنقل التلقائية لأسماء الملفات في الشريط الجانبي */
        [data-testid="stSidebarNav"] {
            display: none !important;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# عرض القائمة الجانبية المخصصة للمشروع
render_sidebar()

st.title("📦 Inventory Overview")

# ==================================================
# AUTHENTICATION CHECK
# ==================================================
token = st.session_state.get("token") or st.session_state.get("access_token")

if not token:
  st.warning("⚠️ Please log in first to continue.")
  if st.button("Go to Login / Main Page"):
    st.switch_page("app.py")
  st.stop()

# ==================================================
# 1. FETCH DATA FROM BACKEND (Source of Truth)
# ==================================================
with st.spinner("Fetching inventory data..."):
  response = get("/inventory/", token=token)

if response.status_code == 200:
  inventory_items = response.json()

  if not inventory_items:
    st.info("No inventory records currently found in the system.")
    st.stop()

  # ==================================================
  # 2. METRICS CALCULATION
  # ==================================================
  total_medicines = len(inventory_items)
  total_remaining_quantity = sum(
      item.get("total_quantity", 0) for item in inventory_items
  )
  low_stock_items = [
      item
      for item in inventory_items
      if item.get("total_quantity", 0) <= item.get("min_stock_level", 0)
  ]
  low_stock_count = len(low_stock_items)

  total_batches = sum(len(item.get("batches", [])) for item in inventory_items)

  m1, m2, m3, m4 = st.columns(4)
  m1.metric("Registered Medicines", f"{total_medicines} Items")
  m2.metric("Total Remaining Units", f"{total_remaining_quantity} Units")
  m3.metric("Low Stock Alerts", f"{low_stock_count} Items", delta_color="inverse")
  m4.metric("Registered Batches", f"{total_batches} Batches")

  st.markdown("---")

  # ==================================================
  # 3. FILTERS & SEARCH
  # ==================================================
  filter_col1, filter_col2 = st.columns([3, 1])

  with filter_col1:
    search_query = (
        st.text_input("🔍 Search Medicine by Name, Code, or Barcode", "")
        .strip()
        .lower()
    )

  with filter_col2:
    stock_filter = st.selectbox(
        "Availability Status:",
        ["All", "In Stock", "Low / Needs Reorder", "Out of Stock"],
    )

  # Apply Filters
  filtered_items = []
  today_str = datetime.now().strftime("%Y-%m-%d")  # noqa: DTZ005

  for item in inventory_items:
    med_name = str(item.get("medicine_name", "")).lower()
    barcode = str(item.get("barcode") or "").lower()
    total_qty = item.get("total_quantity", 0)
    min_lvl = item.get("min_stock_level", 0)

    if search_query:  # noqa: SIM102
      if search_query not in med_name and search_query not in barcode:
        continue

    if (
        (stock_filter == "In Stock" and total_qty <= 0)
        or (stock_filter == "Low / Needs Reorder" and total_qty > min_lvl)
        or (stock_filter == "Out of Stock" and total_qty > 0)
    ):
      continue

    filtered_items.append(item)

  st.write(f"Showing medicines: **{len(filtered_items)}** Items")
  st.divider()

  # ==================================================
  # 4. PRESENTATION LAYER (Quantities Breakdown: Total, Available, Expired)
  # ==================================================
  if not filtered_items:
    st.warning("No medicines match the specified search and filter criteria.")
  else:
    for item in filtered_items:
      med_id = item.get("medicine_id")
      med_name = item.get("medicine_name", "Not Specified")
      total_qty = item.get("total_quantity", 0)
      min_lvl = item.get("min_stock_level", 0)
      loc = item.get("location") or "Not Specified"
      raw_barcode = item.get("barcode")
      batches = item.get("batches", [])

      # حساب الكميات بدقة من تفصيلات الدفعات (Batches) دون تضارب
      available_qty = 0
      expired_qty = 0

      for b in batches:
        qty = b.get("remaining_quantity", b.get("quantity", 0))
        exp_date = b.get("expiry_date") or ""

        # التحقق مما إذا كان تاريخ الصلاحية منتهياً مقارنة بتاريخ اليوم
        is_expired = (
            exp_date != "" and exp_date != "—" and exp_date < today_str
        )

        if is_expired:
          expired_qty += qty
        else:
          available_qty += qty

      # في حال لم يتم توزيع الباتشات تاريخياً، نعتبر المتاح هو ما تبقى بعد استبعاد المنتهي أو الإجمالي
      if available_qty == 0 and expired_qty == 0 and total_qty > 0:
        available_qty = total_qty
      elif available_qty + expired_qty != total_qty:  # noqa: SIM102
        # ضمان اتساق الأرقام مع الإجمالي الكلي
        if total_qty > expired_qty:
          available_qty = total_qty - expired_qty

      if not raw_barcode or str(raw_barcode).strip().lower() in (
          "none",
          "null",
          "",
      ):
        barcode_display = "Not Registered"
      else:
        barcode_display = str(raw_barcode)

      if total_qty == 0:
        status_icon = "🔴"
        status_badge = "Out of Stock"
      elif total_qty <= min_lvl:
        status_icon = "🟠"
        status_badge = "Low Stock"
      else:
        status_icon = "🟢"
        status_badge = "Available"

      col1, col2, col3, col4 = st.columns([3, 2, 2, 2])

      with col1:
        st.write(f"### {status_icon} {med_name}")
        st.caption(f"Barcode: {barcode_display} | Location: `{loc}`")

      with col2:
        st.metric(label="Total Quantity", value=f"{total_qty} Units")
        # عرض الكمية المتاحة (خضراء) والكمية التالفة/المنتهية (حمراء) بشكل صحيح
        st.caption(f"🟢 {available_qty} available | 🔴 {expired_qty} expired/damaged")

      with col3:
        st.write(f"**Status:** {status_badge}")
        st.write(f"**Batches Count:** {len(batches)}")

      with col4:
        st.write("")
        if st.button("🔍 View Batches & Details", key=f"btn_med_{med_id}"):
          st.session_state.selected_inventory_medicine = med_id
          st.switch_page("pages/inventory_details.py")

      st.divider()

else:
  try:
    error_payload = response.json()
    error_msg = error_payload.get("error", response.text)
  except Exception:  # noqa: BLE001
    error_msg = response.text
  st.error(f"Failed to retrieve inventory data from the server: {error_msg}")