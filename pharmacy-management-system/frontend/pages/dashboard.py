from components.sidebar import render_sidebar
from services.api_client import get
import pandas as pd
import streamlit as st

# ==================================================
# PAGE CONFIGURATION
# ==================================================
st.set_page_config(
    page_title="Pharmacy Dashboard",
    page_icon="📊",
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

st.title("📊 Pharmacy Dashboard")

# ==================================================
# AUTHENTICATION CHECK
# ==================================================
token = st.session_state.get("token") or st.session_state.get("access_token")

if not token:
  st.warning("Please login first.")
  if st.button("Go to Login / Main Page"):
    st.switch_page("app.py")
  st.stop()


col1, col2, col3 = st.columns(3)

# Medicines
medicines = []
try:
  res = get("/medicines/", token=token)
  if res.status_code == 200:
    medicines = res.json()
except Exception as e:
  st.error(f"Failed to fetch medicines: {e}")

# Suppliers
suppliers = []
try:
  res = get("/suppliers/", token=token)
  if res.status_code == 200:
    suppliers = res.json()
except Exception as e:
  st.error(f"Failed to fetch suppliers: {e}")

# Inventory
inventory = []
try:
  res = get("/inventory/", token=token)
  if res.status_code == 200:
    inventory = res.json()
except Exception as e:
  st.error(f"Failed to fetch inventory: {e}")


with col1:
  st.metric("💊 Medicines", len(medicines))

with col2:
  st.metric("🏢 Suppliers", len(suppliers))

with col3:
  st.metric("📦 Inventory Records", len(inventory))


st.divider()

st.subheader("📦 Inventory Overview")

if inventory:
  # تجهيز البيانات وتنسيق حقل batches لمنع ظهور [object Object]
  processed_inventory = []
  for item in inventory:
    item_copy = item.copy()

    # معالجة حقل batches إذا كان يحتوي على قائمة قواميس
    batches_data = item_copy.get("batches")
    if isinstance(batches_data, list) and batches_data:
      formatted_batches = []
      for b in batches_data:
        if isinstance(b, dict):
          b_num = b.get("batch_number", "N/A")
          b_qty = b.get("quantity", 0)
          formatted_batches.append(f"#{b_num} (Qty: {b_qty})")
        else:
          formatted_batches.append(str(b))
      item_copy["batches_summary"] = ", ".join(formatted_batches)
    else:
      item_copy["batches_summary"] = "No Batches"

    processed_inventory.append(item_copy)

  df = pd.DataFrame(processed_inventory)

  # إسقاط الحقل القديم غير المعالج إذا وجد
  if "batches" in df.columns:
    df = df.drop(columns=["batches"])

  # إعادة تسمية الأعمدة لتصبح أكثر وضوحاً واحترافية
  rename_mapping = {
      "barcode": "Barcode",
      "inventory_id": "Inventory ID",
      "location": "Location",
      "medicine_id": "Medicine ID",
      "medicine_name": "Medicine Name",
      "min_stock_level": "Min Stock Level",
      "total_quantity": "Total Quantity",
      "batches_summary": "Batches Details",
  }
  df = df.rename(columns=rename_mapping)

  # تحديد ترتيب الأعمدة المنطقي
  desired_order = [
      "Inventory ID",
      "Barcode",
      "Medicine Name",
      "Total Quantity",
      "Min Stock Level",
      "Location",
      "Batches Details",
  ]
  columns_order = [col for col in desired_order if col in df.columns]
  # إضافة أي عمود إضافي إن وجد
  remaining_cols = [col for col in df.columns if col not in columns_order]
  df = df[columns_order + remaining_cols]

  st.dataframe(df, use_container_width=True, hide_index=True)
else:
  st.info("No inventory records found or unable to connect to backend.")