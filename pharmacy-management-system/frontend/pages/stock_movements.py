from datetime import date
from components.sidebar import render_sidebar
import pandas as pd
from services.api_client import get
import streamlit as st

# ==========================================
# PAGE CONFIGURATION
# ==========================================
st.set_page_config(
    page_title="Stock Movements History",
    page_icon="📦",
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

st.title("📦 Stock Movements & Audit History")
st.markdown(
    "Track the complete audit trail, timestamps, operator details, and linked"
    " commercial transactions."
)

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
# DATA FETCHING & FILTERS SECTION
# ==========================================
st.divider()

col_header, col_refresh = st.columns([4, 1])
with col_header:
  st.subheader("🔍 Advanced Filters & Search")
with col_refresh:
  if st.button("🔄 Refresh Data", use_container_width=True):
    st.rerun()

response = get("/stock-movements/", token)

if response.status_code == 200:
  movements = response.json()
  if movements:
    df = pd.DataFrame(movements)

    date_column_name = None
    for col in ["created_at", "movement_date", "date"]:
      if col in df.columns:
        date_column_name = col
        break

    if date_column_name:
      df["parsed_date"] = pd.to_datetime(
          df[date_column_name], errors="coerce"
      ).dt.date
    else:
      df["parsed_date"] = date.today()

    col_f1, col_f2, col_f3, col_f4 = st.columns(4)

    with col_f1:
      search_id = st.text_input(
          "Exact Movement ID", placeholder="e.g., 1 (press Enter)"
      )

    with col_f2:
      available_types = (
          ["All"] + df["movement_type"].dropna().unique().tolist()
          if "movement_type" in df.columns
          else ["All"]
      )
      selected_type = st.selectbox(
          "Filter by Movement Type", options=available_types
      )

    with col_f3:
      min_date = (
          df["parsed_date"].min()
          if not df["parsed_date"].isnull().all()
          else date.today()
      )
      start_date = st.date_input("Start Date", value=min_date)

    with col_f4:
      max_date = (
          df["parsed_date"].max()
          if not df["parsed_date"].isnull().all()
          else date.today()
      )
      end_date = st.date_input("End Date", value=max_date)

    filtered_df = df.copy()

    if search_id.strip():
      if "movement_id" in filtered_df.columns:
        try:
          target_id = int(search_id.strip())
          filtered_df = filtered_df[filtered_df["movement_id"] == target_id]
        except ValueError:
          filtered_df = filtered_df.iloc[0:0]

    if selected_type != "All":
      filtered_df = filtered_df[
          filtered_df["movement_type"] == selected_type
      ]

    if start_date and end_date and date_column_name:
      filtered_df = filtered_df[
          (filtered_df["parsed_date"] >= start_date)
          & (filtered_df["parsed_date"] <= end_date)
      ]

    st.markdown("---")

    col_stat1, col_stat2, col_stat3 = st.columns(3)
    with col_stat1:
      st.metric(label="Total Operations Logged", value=len(filtered_df))
    with col_stat2:
      total_qty_change = (
          filtered_df["quantity_change"].sum()
          if "quantity_change" in filtered_df.columns
          else 0
      )
      st.metric(
          label="Net Quantity Impact",
          value=int(total_qty_change),
          delta=int(total_qty_change),
      )
    with col_stat3:
      st.metric(
          label="Unique Batches",
          value=filtered_df["batch_id"].nunique()
          if "batch_id" in filtered_df.columns
          else 0,
      )

    st.subheader("📋 Audit Trail Table")
    if not filtered_df.empty:
      if date_column_name and date_column_name in filtered_df.columns:
        filtered_df = filtered_df.sort_values(
            by=date_column_name, ascending=False
        )

      display_df = filtered_df.drop(columns=["parsed_date"], errors="ignore")
      st.dataframe(display_df, use_container_width=True)

      if search_id.strip() and len(filtered_df) == 1:
        st.markdown("---")
        st.subheader("🔍 Detailed Movement & Transaction Insight")

        row = filtered_df.iloc[0]
        m_id = row.get("movement_id")

        detail_res = get(f"/stock-movements/{m_id}", token)
        if detail_res.status_code == 200:
          d_data = detail_res.json()

          col_d1, col_d2, col_d3 = st.columns(3)

          with col_d1:
            st.markdown("##### 📦 Movement Attributes")
            st.write(f"🆔 **Movement ID:** {d_data.get('movement_id')}")
            st.write(
                f"🏷️ **Batch ID / Number:** {d_data.get('batch_id')} (Batch"
                f" No: {d_data.get('batch_number', 'N/A')})"
            )
            st.write(f"🔄 **Type:** {d_data.get('movement_type')}")
            st.write(f"📊 **Qty Change:** {d_data.get('quantity_change')}")

          with col_d2:
            st.markdown("##### 👤 Operator & Time")
            st.write(f"👤 **User ID:** {d_data.get('created_by', 'N/A')}")
            st.write(f"📅 **Timestamp:** {d_data.get('created_at', 'N/A')}")
            st.write(f"📝 **Notes:** {d_data.get('notes', 'None')}")

          with col_d3:
            st.markdown("##### 🔗 Linked Transaction")
            ref_type = d_data.get("reference_type", "N/A")
            ref_id = d_data.get("reference_id", "N/A")
            st.write(f"📌 **Reference Type:** {ref_type}")
            st.write(f"🔑 **Reference ID:** {ref_id}")

            ref_details = d_data.get("reference_details", {})
            if ref_details:
              st.info(
                  f"📋 **Linked {ref_details.get('type')}:**\n\n- ID:"
                  f" `{ref_details.get('invoice_id') or ref_details.get('purchase_id')}`\n- Status:"
                  f" `{ref_details.get('status')}`"
              )
            else:
              st.caption("No extended transaction metadata linked.")
        else:
          st.error("Failed to load extended movement details.")
    else:
      st.warning(
          "⚠️ No stock movements match your search criteria. Try clearing or"
          " broadening your filters."
      )

  else:
    st.info(
        "No stock movements recorded yet. Movements are automatically logged"
        " with timestamps and operators."
    )
else:
  st.error("Failed to load stock movements from backend.")