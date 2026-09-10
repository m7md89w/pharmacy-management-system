import streamlit as st
import pandas as pd
from datetime import datetime
from services.api_client import get
from components.sidebar import render_sidebar

st.set_page_config(
    page_title="Inventory & Batches",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded"
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

st.title("📦 Inventory & Batches Management")

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
    total_remaining_quantity = sum(item.get("total_quantity", 0) for item in inventory_items)
    low_stock_items = [
        item for item in inventory_items 
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
    # 3. FILTERS & CONTROLS
    # ==================================================
    filter_col1, filter_col2, filter_col3 = st.columns([2, 1, 1])

    with filter_col1:
        search_query = st.text_input("🔍 Search by Medicine Name, Code, or Barcode", "").strip().lower()

    with filter_col2:
        stock_filter = st.selectbox(
            "Availability Status:",
            ["All", "In Stock", "Low / Needs Reorder", "No Batches"]
        )

    with filter_col3:
        view_mode = st.radio(
            "View Mode:",
            ["Per Medicine Details", "Comprehensive Table"],
            horizontal=True
        )

    # Apply Filters
    filtered_items = []
    for item in inventory_items:
        med_name = str(item.get("medicine_name", "")).lower()
        barcode = str(item.get("barcode") or "").lower()
        total_qty = item.get("total_quantity", 0)
        min_lvl = item.get("min_stock_level", 0)
        batches = item.get("batches", [])

        if search_query:
            if search_query not in med_name and search_query not in barcode:
                continue

        if stock_filter == "In Stock" and total_qty <= 0:
            continue
        elif stock_filter == "Low / Needs Reorder" and total_qty > min_lvl:
            continue
        elif stock_filter == "No Batches" and len(batches) > 0:
            continue

        filtered_items.append(item)

    st.write(f"Showing results: **{len(filtered_items)}** Items")

    # ==================================================
    # 4. PRESENTATION LAYER
    # ==================================================
    if not filtered_items:
        st.warning("No items match the specified search and filter criteria.")

    elif view_mode == "Per Medicine Details":
        for item in filtered_items:
            med_name = item.get("medicine_name", "Not Specified")
            total_qty = item.get("total_quantity", 0)
            min_lvl = item.get("min_stock_level", 0)
            loc = item.get("location") or "Not Specified"
            raw_barcode = item.get("barcode")

            if not raw_barcode or str(raw_barcode).strip().lower() in ("none", "null", ""):
                barcode_display = "Not Registered"
            else:
                barcode_display = str(raw_barcode)

            batches = item.get("batches", [])

            if total_qty == 0:
                status_icon = "🔴"
                status_badge = "Out of Stock"
            elif total_qty <= min_lvl:
                status_icon = "🟠"
                status_badge = "Low Stock"
            else:
                status_icon = "🟢"
                status_badge = "Available"

            expander_title = (
                f"{status_icon} {med_name} | Remaining Balance: {total_qty} units | Barcode: {barcode_display}"
            )

            with st.expander(expander_title):
                info_c1, info_c2, info_c3, info_c4 = st.columns(4)
                info_c1.write(f"**Stock Status:** {status_badge}")
                info_c2.write(f"**Storage Location:** `{loc}`")
                info_c3.write(f"**Reorder Level:** {min_lvl}")
                info_c4.write(f"**Number of Batches:** {len(batches)}")

                if batches:
                    batches_rows = []
                    today_str = datetime.now().strftime("%Y-%m-%d")

                    for b in batches:
                        exp_date = b.get("expiry_date") or "—"
                        is_expired = exp_date != "—" and exp_date < today_str
                        orig_qty = b.get("original_quantity", 0)
                        rem_qty = b.get("remaining_quantity", b.get("quantity", 0))

                        batches_rows.append({
                            "Batch Number": b.get("batch_number") or "—",
                            "Original Qty": orig_qty,
                            "Remaining Qty": rem_qty,
                            "Unit Cost": f"{b.get('unit_cost', 0.0):.2f} JOD",
                            "Selling Price": f"{b.get('selling_price', 0.0):.2f} JOD",
                            "Manufacture Date": b.get("manufacture_date") or "—",
                            "Expiry Date": exp_date,
                            "Expiry Status": "Expired ⚠️" if is_expired else "Valid ✅"
                        })

                    df_batches = pd.DataFrame(batches_rows)
                    st.dataframe(df_batches, use_container_width=True, hide_index=True)
                else:
                    st.info("ℹ️ No supply batches received for this item currently.")

    else:
        # Comprehensive Flat Table for all batches
        flat_records = []
        today_str = datetime.now().strftime("%Y-%m-%d")

        for item in filtered_items:
            med_name = item.get("medicine_name", "Not Specified")
            raw_barcode = item.get("barcode")
            barcode_clean = "Not Registered" if not raw_barcode or str(raw_barcode).strip().lower() in ("none", "null") else str(raw_barcode)
            total_qty = item.get("total_quantity", 0)
            loc = item.get("location") or "Not Specified"
            batches = item.get("batches", [])

            if batches:
                for b in batches:
                    exp_date = b.get("expiry_date") or "—"
                    is_expired = exp_date != "—" and exp_date < today_str
                    orig_qty = b.get("original_quantity", 0)
                    rem_qty = b.get("remaining_quantity", b.get("quantity", 0))

                    flat_records.append({
                        "Medicine Name": med_name,
                        "Barcode": barcode_clean,
                        "Batch Number": b.get("batch_number") or "—",
                        "Original Qty": orig_qty,
                        "Remaining Qty": rem_qty,
                        "Total Item Stock": total_qty,
                        "Unit Cost": f"{b.get('unit_cost', 0.0):.2f} JOD",
                        "Selling Price": f"{b.get('selling_price', 0.0):.2f} JOD",
                        "Expiry Date": exp_date,
                        "Expiry Status": "Expired ⚠️" if is_expired else "Valid ✅",
                        "Location": loc
                    })
            else:
                flat_records.append({
                    "Medicine Name": med_name,
                    "Barcode": barcode_clean,
                    "Batch Number": "—",
                    "Original Qty": 0,
                    "Remaining Qty": 0,
                    "Total Item Stock": total_qty,
                    "Unit Cost": "0.00 JOD",
                    "Selling Price": "0.00 JOD",
                    "Expiry Date": "—",
                    "Expiry Status": "No Batches",
                    "Location": loc
                })

        df_flat = pd.DataFrame(flat_records)
        st.dataframe(df_flat, use_container_width=True, hide_index=True)

else:
    try:
        error_payload = response.json()
        error_msg = error_payload.get("error", response.text)
    except Exception:
        error_msg = response.text
    st.error(f"Failed to retrieve inventory data from the server: {error_msg}")