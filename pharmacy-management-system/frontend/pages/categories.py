from components.sidebar import render_sidebar
import pandas as pd
from services.api_client import delete, get, post, put
import streamlit as st

# ==========================================
# PAGE CONFIGURATION
# ==========================================
st.set_page_config(
    page_title="Medicine Categories",
    page_icon="🏷️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ==========================================
# إخفاء القائمة الجانبية الافتراضية
# ==========================================
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

st.title("🏷️ Medicine Categories Management")

# ==========================================
# AUTHENTICATION CHECK
# ==========================================
token = st.session_state.get("token") or st.session_state.get("access_token")

if not token:
  st.warning("⚠️ Please log in first.")
  if st.button("Go to Login"):
    st.switch_page("app.py")
  st.stop()

if "edit_category" not in st.session_state:
  st.session_state.edit_category = None


# ==========================================
# CREATE CATEGORY EXPANDER
# ==========================================
with st.expander("➕ Add New Category"):
  cat_name = st.text_input("Category Name", key="c_name")
  cat_desc = st.text_area("Description", key="c_desc")

  if st.button("Create Category", type="primary"):
    if not cat_name.strip():
      st.error("❌ Category name is required.")
    else:
      data = {
          "category_name": cat_name.strip(),
          "description": cat_desc.strip() if cat_desc else "",
      }
      res = post("/categories/", data, token)
      if res.status_code == 201:
        st.success("✅ Category created successfully.")
        st.rerun()
      else:
        try:
          error_msg = res.json().get("error", "Failed to create category.")
        except Exception:
          error_msg = res.text
        st.error(error_msg)


# ==========================================
# EDIT CATEGORY SECTION
# ==========================================
if st.session_state.edit_category:
  c = st.session_state.edit_category
  st.divider()
  st.subheader(f"✏️ Edit Category: {c['category_name']}")

  e_name = st.text_input(
      "Category Name", value=c["category_name"], key="edit_c_name"
  )
  e_desc = st.text_area(
      "Description", value=c.get("description", ""), key="edit_c_desc"
  )

  col1, col2 = st.columns(2)
  with col1:
    if st.button("💾 Save Changes"):
      if not e_name.strip():
        st.error("❌ Category name is required.")
      else:
        payload = {
            "category_name": e_name.strip(),
            "description": e_desc.strip() if e_desc else "",
        }
        res = put(f"/categories/{c['category_id']}", payload, token)
        if res.status_code == 200:
          st.success("✅ Category updated successfully.")
          st.session_state.edit_category = None
          st.rerun()
        else:
          try:
            error_msg = res.json().get("error", "Failed to update category.")
          except Exception:
            error_msg = res.text
          st.error(error_msg)

  with col2:
    if st.button("❌ Cancel"):
      st.session_state.edit_category = None
      st.rerun()


# ==========================================
# SEARCH & CATEGORIES LIST
# ==========================================
st.divider()

# حقل البحث الجديد عن طريق اسم التصنيف
search_query = st.text_input(
    "🔍 Search by Category Name", placeholder="Type category name..."
)

col_refresh, _ = st.columns([1, 5])
with col_refresh:
  if st.button("🔄 Refresh"):
    st.rerun()

response = get("/categories/", token)

if response.status_code == 200:
  categories = response.json()

  # تصفية التصنيفات بناءً على مدخلات البحث
  if search_query:
    query = search_query.strip().lower()
    categories = [
        cat for cat in categories if query in cat["category_name"].lower()
    ]

  st.subheader(f"📋 Categories List ({len(categories)})")

  if categories:
    for cat in categories:
      col1, col2, col3, col4 = st.columns([3, 4, 1, 1])
      with col1:
        st.write(f"🏷️ **{cat['category_name']}**")
      with col2:
        st.caption(cat.get("description", "No description"))
      with col3:
        if st.button("✏️ Edit", key=f"edit_cat_{cat['category_id']}"):
          st.session_state.edit_category = cat
          st.rerun()
      with col4:
        if st.button("🗑️ Delete", key=f"del_cat_{cat['category_id']}"):
          res = delete(f"/categories/{cat['category_id']}", token)
          if res.status_code == 200:
            st.success("✅ Category deleted successfully.")
            st.rerun()
          else:
            try:
              error_msg = res.json().get("error", "Failed to delete category.")
            except Exception:
              error_msg = res.text
            st.error(error_msg)
      st.divider()
  else:
    st.info("No categories found matching your search.")
else:
  st.error("Failed to load categories from backend.")