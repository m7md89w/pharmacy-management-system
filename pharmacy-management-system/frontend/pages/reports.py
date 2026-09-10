from components.sidebar import render_sidebar
import pandas as pd
from services.api_client import get
import streamlit as st

# ==================================================
# PAGE CONFIGURATION
# ==================================================
st.set_page_config(
    page_title="Pharmacy Reports",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ==================================================
# إخفاء القائمة الجانبية الافتراضية لملفات الصفحات
# ==================================================
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

st.title("📈 Pharmacy Analytics & Reports")

# ==================================================
# AUTHENTICATION CHECK
# ==================================================
token = st.session_state.get("token") or st.session_state.get("access_token")

if not token:
  st.warning("⚠️ Please log in first to access this page.")
  if st.button("Go to Login / Main Page"):
    st.switch_page("app.py")
  st.stop()

# ==================================================
# TABS FOR DIFFERENT REPORTS (استهلاك بيانات الـ Backend)
# ==================================================
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📊 Financial & Dashboard",
    "🛒 Sales Report",
    "📦 Purchases Report",
    "💊 Inventory Summary",
    "⚠️ Low Stock Alert",
    "⏳ Expiry Tracking",
])

# --- TAB 1: Financial & Dashboard Summary ---
with tab1:
  st.subheader("General Financial & System Overview")
  try:
    res = get("/reports/dashboard", token=token)
    if res.status_code == 200:
      data = res.json()
      col1, col2, col3 = st.columns(3)
      with col1:
        st.metric(
            "💰 Total Sales", f"${data.get('total_sales', 0.0):,.2f}"
        )
      with col2:
        st.metric(
            "🛍️ Total Purchases",
            f"${data.get('total_purchases', 0.0):,.2f}",
        )
      with col3:
        st.metric("📈 Net Profit", f"${data.get('profit', 0.0):,.2f}")

      st.divider()

      c1, c2, c3 = st.columns(3)
      with c1:
        st.metric("💊 Medicines Count", data.get("medicines_count", 0))
      with c2:
        st.metric("⚠️ Low Stock Items", data.get("low_stock_count", 0))
      with c3:
        st.metric("⏳ Expired Batches", data.get("expired_batches", 0))
    else:
      st.error("Failed to fetch dashboard summary from backend.")
  except Exception as e:
    st.error(f"Connection error: {e}")

# --- TAB 2: Sales Report ---
with tab2:
  st.subheader("Sales Analytics")
  try:
    res = get("/reports/sales", token=token)
    if res.status_code == 200:
      s_data = res.json()
      col_s1, col_s2, col_s3 = st.columns(3)
      with col_s1:
        st.metric("Invoices Count", s_data.get("invoices_count", 0))
      with col_s2:
        st.metric(
            "Total Sales Amount", f"${s_data.get('total_sales', 0.0):,.2f}"
        )
      with col_s3:
        st.metric("Total Items Sold", s_data.get("total_items_sold", 0))
    else:
      st.error("Failed to fetch sales report.")
  except Exception as e:
    st.error(f"Error: {e}")

# --- TAB 3: Purchases Report ---
with tab3:
  st.subheader("Purchases Analytics")
  try:
    res = get("/reports/purchases", token=token)
    if res.status_code == 200:
      p_data = res.json()
      col_p1, col_p2, col_p3 = st.columns(3)
      with col_p1:
        st.metric("Purchase Orders", p_data.get("purchase_orders", 0))
      with col_p2:
        st.metric(
            "Total Purchases Amount",
            f"${p_data.get('total_purchases', 0.0):,.2f}",
        )
      with col_p3:
        st.metric("Total Items Purchased", p_data.get("total_items_purchased", 0))
    else:
      st.error("Failed to fetch purchase report.")
  except Exception as e:
    st.error(f"Error: {e}")

# --- TAB 4: Inventory Summary ---
with tab4:
  st.subheader("Inventory Stock Summary")
  try:
    res = get("/reports/inventory", token=token)
    if res.status_code == 200:
      inv_data = res.json()
      c1, c2 = st.columns(2)
      with c1:
        st.metric("Unique Medicines", inv_data.get("medicines_count", 0))
      with c2:
        st.metric("Total Physical Quantity", inv_data.get("total_quantity", 0))
    else:
      st.error("Failed to fetch inventory summary.")
  except Exception as e:
    st.error(f"Error: {e}")

# --- TAB 5: Low Stock Alert ---
with tab5:
  st.subheader("Low Stock Warning Report")
  try:
    res = get("/reports/low-stock", token=token)
    if res.status_code == 200:
      low_items = res.json()
      if low_items:
        st.warning(
            f"Found {len(low_items)} items at or below minimum stock level!"
        )
        df_low = pd.DataFrame(low_items)
        st.dataframe(df_low, use_container_width=True, hide_index=True)
      else:
        st.success("All inventory levels are optimal!")
    else:
      st.error("Failed to fetch low stock report.")
  except Exception as e:
    st.error(f"Error: {e}")

# --- TAB 6: Expiry Tracking ---
with tab6:
  st.subheader("Expired Batches Report")
  try:
    res = get("/reports/expiry", token=token)
    if res.status_code == 200:
      expired_items = res.json()
      if expired_items:
        st.error(f"Found {len(expired_items)} expired batches!")
        df_exp = pd.DataFrame(expired_items)
        
        # عرض البيانات التفصيلية للدواء والدفعة بوضوح
        display_cols = [col for col in ["barcode", "medicine_name", "batch_number", "expiry_date", "quantity", "selling_price"] if col in df_exp.columns]
        display_df = df_exp[display_cols].rename(columns={
            "barcode": "Barcode",
            "medicine_name": "Medicine Name",
            "batch_number": "Batch #",
            "expiry_date": "Expiry Date",
            "quantity": "Quantity",
            "selling_price": "Selling Price ($)"
        })
        
        st.dataframe(display_df, use_container_width=True, hide_index=True)
      else:
        st.success("No expired batches found in the system.")
    else:
      st.error("Failed to fetch expiry report.")
  except Exception as e:
    st.error(f"Error: {e}")