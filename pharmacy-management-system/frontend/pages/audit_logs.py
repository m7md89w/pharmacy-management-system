from datetime import date
from components.sidebar import render_sidebar
import pandas as pd
from services.api_client import get
import streamlit as st

# ==========================================
# PAGE CONFIGURATION
# ==========================================
st.set_page_config(
    page_title="Audit Logs & Activity History",
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

st.title("📜 System Audit Logs & Activity History")
st.markdown(
    "Track all system activities, timestamps, operator names, and detailed"
    " audit trails with linked transactions."
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
  st.subheader("🔍 Advanced Filters & Log Search")
with col_refresh:
  if st.button("🔄 Refresh Logs", use_container_width=True):
    st.rerun()

response = get("/audit-logs/", token)

if response.status_code == 200:
  logs = response.json()
  if logs:
    df = pd.DataFrame(logs)

    date_column_name = None
    for col in ["timestamp", "created_at", "date", "action_date"]:
      if col in df.columns:
        date_column_name = col
        break

    if date_column_name:
      df["parsed_date"] = pd.to_datetime(
          df[date_column_name], errors="coerce"
      ).dt.date
    else:
      df["parsed_date"] = date.today()

    id_col_name = None
    for col in ["audit_id", "log_id", "id"]:
      if col in df.columns:
        id_col_name = col
        break

    col_f1, col_f2, col_f3 = st.columns(3)

    with col_f1:
      search_id = st.text_input(
          "Exact Log ID Search", placeholder="e.g., 5 (press Enter)"
      )

    with col_f2:
      min_date = (
          df["parsed_date"].min()
          if not df["parsed_date"].isnull().all()
          else date.today()
      )
      start_date = st.date_input("Start Date", value=min_date)

    with col_f3:
      max_date = (
          df["parsed_date"].max()
          if not df["parsed_date"].isnull().all()
          else date.today()
      )
      end_date = st.date_input("End Date", value=max_date)

    filtered_df = df.copy()

    if search_id.strip() and id_col_name:
      try:
        target_id = int(search_id.strip())
        filtered_df = filtered_df[filtered_df[id_col_name] == target_id]
      except ValueError:
        filtered_df = filtered_df.iloc[0:0]

    if start_date and end_date and date_column_name:
      filtered_df = filtered_df[
          (filtered_df["parsed_date"] >= start_date)
          & (filtered_df["parsed_date"] <= end_date)
      ]

    st.markdown("---")

    col_stat1, col_stat2 = st.columns(2)
    with col_stat1:
      st.metric(label="Total Logs Found", value=len(filtered_df))
    with col_stat2:
      unique_operators = (
          filtered_df["operator"].nunique()
          if "operator" in filtered_df.columns
          else 0
      )
      st.metric(label="Active Operators Involved", value=unique_operators)

    st.subheader("📋 Audit Logs Table")
    if not filtered_df.empty:
      if date_column_name and date_column_name in filtered_df.columns:
        filtered_df = filtered_df.sort_values(
            by=date_column_name, ascending=False
        )

      display_df = filtered_df.drop(columns=["parsed_date"], errors="ignore")
      st.dataframe(display_df, use_container_width=True)

      if search_id.strip() and len(filtered_df) == 1 and id_col_name:
        st.markdown("---")
        st.subheader("🔍 Detailed Audit Log & Transaction Insight")

        row = filtered_df.iloc[0]
        l_id = row.get(id_col_name)

        detail_res = get(f"/audit-logs/{l_id}", token)
        if detail_res.status_code == 200:
          d_data = detail_res.json()

          col_d1, col_d2, col_d3 = st.columns(3)

          with col_d1:
            st.markdown("##### 🆔 Log Attributes")
            st.write(
                f"🏷️ **Log ID:** {d_data.get('audit_id') or d_data.get('id')}"
            )
            st.write(f"👤 **Operator:** {d_data.get('operator', 'N/A')}")
            st.write(f"⚡ **Action / Event:** {d_data.get('action', 'N/A')}")

          with col_d2:
            st.markdown("##### 📅 Time & Details")
            st.write(
                f"📅 **Timestamp:** {d_data.get('timestamp', 'No Timestamp')}"
            )
            st.info(
                "📝 **Description:**\n\n"
                f"{d_data.get('details', 'No details recorded.')}"
            )

          with col_d3:
            st.markdown("##### 🔗 Linked Transaction")
            linked_trans = d_data.get("linked_transaction", {})
            if linked_trans:
              t_type = linked_trans.get("type", "Transaction")
              t_id = (
                  linked_trans.get("purchase_id")
                  or linked_trans.get("invoice_id")
                  or linked_trans.get("return_id")
                  or "N/A"
              )
              t_status = linked_trans.get("status", "N/A")
              st.info(
                  f"📋 **Linked {t_type}:**\n\n- ID: `{t_id}`\n- Status:"
                  f" `{t_status}`"
              )
            else:
              st.caption("No extended transaction metadata linked.")
        else:
          st.error("Failed to load extended audit log details.")
    else:
      st.warning(
          "⚠️ No audit logs match your search criteria. Try clearing or"
          " broadening your filters."
      )

  else:
    st.info("No audit logs recorded in the system yet.")
else:
  st.error("Failed to load audit logs from backend.")