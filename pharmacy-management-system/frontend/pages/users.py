from components.sidebar import render_sidebar
import pandas as pd
from services.api_client import delete, get, post, put
import streamlit as st

# ==================================================
# PAGE CONFIGURATION
# ==================================================
st.set_page_config(
    page_title="Users Management",
    page_icon="👥",
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

st.title("👥 Pharmacy Users & Pharmacists Management")

# ==================================================
# AUTHENTICATION & ROLE CHECK
# ==================================================
token = st.session_state.get("token") or st.session_state.get("access_token")

if not token:
  st.warning("⚠️ Please log in first to access this page.")
  if st.button("Go to Login / Main Page"):
    st.switch_page("app.py")
  st.stop()

if "edit_user" not in st.session_state:
  st.session_state.edit_user = None


# ==================================================
# FETCH ROLES FROM BACKEND (SINGLE SOURCE OF TRUTH)
# ==================================================
roles_res = get("/roles/", token)
roles_map = {}  # role_name -> role_id
id_to_role_name = {}  # role_id -> role_name
roles_list = []

if roles_res.status_code == 200:
  roles_data = roles_res.json()
  for r in roles_data:
    r_id = r.get("role_id")
    r_name = r.get("role_name")
    if r_id is not None and r_name:
      roles_map[r_name] = r_id
      id_to_role_name[r_id] = r_name
      roles_list.append(r_name)


# ==================================================
# CREATE USER EXPANDER
# ==================================================
with st.expander("➕ Add New User / Pharmacist"):
  col1, col2 = st.columns(2)

  with col1:
    full_name = st.text_input("Full Name", key="create_fname")
    username = st.text_input("Username", key="create_uname")
    email = st.text_input("Email", key="create_email")

  with col2:
    phone = st.text_input("Phone", key="create_phone")
    password = st.text_input("Password", type="password", key="create_pass")
    confirm_password = st.text_input(
        "Confirm Password", type="password", key="create_cpass"
    )

    selected_role_name = st.selectbox(
        "Role",
        options=roles_list if roles_list else ["Admin", "Pharmacist"],
        key="create_role",
    )
    role_id = roles_map.get(
        selected_role_name, 1
    )  # Fallback to 1 if not mapped

  if st.button("Create User", type="primary"):
    if not full_name.strip() or not username.strip() or not password:
      st.error(
          "❌ Please fill in all required fields (Full Name, Username, and"
          " Password)."
      )
    elif password != confirm_password:
      st.error("❌ Passwords do not match.")
    else:
      data = {
          "full_name": full_name.strip(),
          "username": username.strip(),
          "email": email.strip() if email else None,
          "phone": phone.strip() if phone else None,
          "password": password.strip(),
          "role_id": int(role_id),
      }

      response = post("/users/", data, token)

      if response.status_code == 201:
        st.success("✅ User created successfully.")
        st.rerun()
      else:
        try:
          error = response.json().get("error", "Failed to create user.")
        except Exception:
          error = response.text
        st.error(error)


# ==================================================
# EDIT USER SECTION
# ==================================================
if st.session_state.edit_user:
  u = st.session_state.edit_user
  st.divider()
  st.subheader(f"✏️ Edit User: {u['username']}")

  edit_full_name = st.text_input(
      "Full Name", value=u.get("full_name", ""), key="e_fname"
  )
  edit_email = st.text_input("Email", value=u.get("email", ""), key="e_email")
  edit_phone = st.text_input("Phone", value=u.get("phone", ""), key="e_phone")

  current_role_id = u.get("role_id", 1)
  current_role_name = id_to_role_name.get(current_role_id, "Admin")
  default_role_index = (
      roles_list.index(current_role_name)
      if current_role_name in roles_list
      else 0
  )

  edit_role_name = st.selectbox(
      "Role",
      options=roles_list if roles_list else ["Admin", "Pharmacist"],
      index=default_role_index,
      key="e_role",
  )
  edit_role_id = roles_map.get(edit_role_name, current_role_id)

  edit_password = st.text_input(
      "New Password (leave blank to keep current)",
      type="password",
      key="e_pass",
  )
  edit_confirm_password = st.text_input(
      "Confirm New Password", type="password", key="e_cpass"
  )

  col1, col2 = st.columns(2)
  with col1:
    if st.button("💾 Save Changes"):
      if edit_password and edit_password != edit_confirm_password:
        st.error("❌ New passwords do not match.")
      else:
        payload = {
            "full_name": edit_full_name.strip(),
            "email": edit_email.strip() if edit_email else None,
            "phone": edit_phone.strip() if edit_phone else None,
            "role_id": int(edit_role_id),
        }
        if edit_password:
          payload["password"] = edit_password.strip()

        res = put(f"/users/{u['user_id']}", payload, token)
        if res.status_code == 200:
          st.success("✅ User updated successfully.")
          st.session_state.edit_user = None
          st.rerun()
        else:
          try:
            st.error(res.json().get("error", "Failed to update user."))
          except:
            st.error(res.text)

  with col2:
    if st.button("❌ Cancel"):
      st.session_state.edit_user = None
      st.rerun()


# ==================================================
# USERS LIST
# ==================================================
st.divider()
st.subheader("📋 System Users List")

if st.button("🔄 Refresh List"):
  st.rerun()

response = get("/users/", token)

if response.status_code == 200:
  users = response.json()

  if users:
    for u in users:
      col1, col2, col3, col4 = st.columns([3, 2, 2, 2])

      with col1:
        r_id = u.get("role_id")
        role_label = id_to_role_name.get(r_id, f"Role ID: {r_id}")
        st.write(f"👤 **{u['full_name']}** ({u['username']})")
        st.caption(
            f"Role: 🛡️ {role_label} | Email: {u.get('email', 'N/A')}"
        )

      with col2:
        status_text = (
            "🟢 Active" if u.get("is_active", True) else "❄️ Deactivated"
        )
        st.write(f"Status: {status_text}")

      with col3:
        if st.button("✏️ Edit", key=f"edit_u_{u['user_id']}"):
          st.session_state.edit_user = u
          st.rerun()

      with col4:
        is_active = u.get("is_active", True)
        btn_label = "❄️ Deactivate" if is_active else "🟢 Activate"
        if st.button(btn_label, key=f"deactivate_{u['user_id']}"):
          res = delete(f"/users/{u['user_id']}", token)
          if res.status_code == 200:
            st.success("✅ User status updated successfully.")
            st.rerun()
          else:
            try:
              st.error(res.json().get("error", "Failed to update status."))
            except:
              st.error(res.text)

      st.divider()
  else:
    st.info("No users found in the system.")
else:
  st.error(
      "Failed to load users from backend. Make sure you are logged in as Admin."
  )