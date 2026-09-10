from components.sidebar import render_sidebar
import pandas as pd
from services.api_client import delete, get, post, put
import streamlit as st

# ==========================================
# PAGE CONFIGURATION
# ==========================================
st.set_page_config(
    page_title="Notifications Management",
    page_icon="🔔",
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

st.title("🔔 System Notifications")

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
# 1. CREATE NOTIFICATION EXPANDER
# ==========================================
with st.expander("➕ Create New Notification"):
  col1, col2 = st.columns(2)
  with col1:
    notif_type = st.selectbox(
        "Type", options=["LOW_STOCK", "EXPIRY", "SYSTEM", "OTHER"]
    )
    severity = st.selectbox(
        "Severity", options=["LOW", "MEDIUM", "HIGH"], index=1
    )
  with col2:
    medicine_id = st.number_input(
        "Medicine ID (Optional)", min_value=0, value=0, step=1
    )
    batch_id = st.number_input(
        "Batch ID (Optional)", min_value=0, value=0, step=1
    )

  message = st.text_area("Notification Message")

  if st.button("Send Notification", type="primary"):
    if not message.strip():
      st.error("❌ Message is required.")
    else:
      payload = {
          "type": notif_type,
          "severity": severity,
          "message": message.strip(),
      }
      if medicine_id > 0:
        payload["medicine_id"] = int(medicine_id)
      if batch_id > 0:
        payload["batch_id"] = int(batch_id)

      res = post("/notifications/", payload, token)
      if res.status_code == 201:
        st.success("✅ Notification created successfully.")
        st.rerun()
      else:
        try:
          err = res.json().get("error", "Failed to create notification.")
        except Exception:
          err = res.text
        st.error(err)


# ==========================================
# 2. VIEW NOTIFICATIONS (Tabs: All & Unread)
# ==========================================
st.divider()

if st.button("🔄 Refresh Data"):
  st.rerun()

tab1, tab2 = st.tabs(["📋 All Notifications", "📬 Unread Only"])

with tab1:
  st.subheader("All Notifications History")
  response = get("/notifications/", token)
  if response.status_code == 200:
    notifs = response.json()
    if notifs:
      for n in notifs:
        col1, col2, col3, col4 = st.columns([3, 2, 2, 2])
        with col1:
          status_icon = "🟢" if n.get("is_read") else "🔴"
          st.write(
              f"{status_icon} **[{n.get('type')}]** — Severity:"
              f" `{n.get('severity')}`"
          )
          st.caption(n.get("message"))
        with col2:
          st.write(f"Med ID: {n.get('medicine_id') or 'N/A'}")
          st.write(f"Batch ID: {n.get('batch_id') or 'N/A'}")
        with col3:
          st.caption(f"🕒 {n.get('created_at', 'N/A')}")
        with col4:
          if not n.get("is_read"):
            if st.button("✅ Mark Read", key=f"read_{n['notification_id']}"):
              r = put(f"/notifications/{n['notification_id']}/read", {}, token)
              if r.status_code == 200:
                st.success("Marked as read!")
                st.rerun()
              else:
                st.error("Failed to mark as read.")
          if st.button("🗑️ Delete", key=f"del_notif_{n['notification_id']}"):
            d = delete(f"/notifications/{n['notification_id']}", token)
            if d.status_code == 200:
              st.success("Deleted successfully.")
              st.rerun()
            else:
              try:
                err = d.json().get("error", "Failed to delete.")
              except Exception:
                err = d.text
              st.error(err)
        st.divider()
    else:
      st.info("No notifications found.")
  else:
    st.error("Failed to load notifications from backend.")

with tab2:
  st.subheader("Unread Notifications")
  unread_res = get("/notifications/unread", token)
  if unread_res.status_code == 200:
    unread_notifs = unread_res.json()
    if unread_notifs:
      for n in unread_notifs:
        col1, col2, col3 = st.columns([4, 2, 2])
        with col1:
          st.write(
              f"🔴 **[{n.get('type')}]** — Severity: `{n.get('severity')}`"
          )
          st.write(n.get("message"))
        with col2:
          st.caption(f"ID: {n.get('notification_id')}")
        with col3:
          if st.button(
              "✅ Mark Read", key=f"unread_read_{n['notification_id']}"
          ):
            r = put(f"/notifications/{n['notification_id']}/read", {}, token)
            if r.status_code == 200:
              st.success("Marked as read!")
              st.rerun()
            else:
              st.error("Failed to mark as read.")
        st.divider()
    else:
      st.info("No unread notifications.")
  else:
    st.error("Failed to load unread notifications.")