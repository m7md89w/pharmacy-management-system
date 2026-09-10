import streamlit as st


def render_sidebar():
  """Renders the common sidebar navigation for the Pharmacy Management System.

  Must be called on every page to ensure consistent navigation.
  """
  with st.sidebar:
    st.title("💊 Pharmacy ERP")
    st.markdown("---")

    # Check authentication status
    if "token" in st.session_state:
      st.subheader("Main Menu")
      st.page_link("pages/dashboard.py", label="Dashboard", icon="📊")
      st.page_link("pages/reports.py", label="Reports & Analytics", icon="📈")
      st.page_link("pages/inventory.py", label="Inventory & Batches", icon="📦")
      st.page_link(
          "pages/expired_medicines.py", label="Expired Medicines", icon="⚠️"
      )

      st.subheader("Sales Management")
      st.page_link("pages/sales_invoices.py", label="Sales Invoices", icon="💰")
      st.page_link("pages/sales_return.py", label="Sales Returns", icon="🔙")
      st.page_link(
          "pages/prescriptions.py", label="Prescriptions", icon="📜"
      )

      st.subheader("Purchase Management")
      st.page_link("pages/purchases.py", label="Purchase Orders", icon="🛒")
      st.page_link(
          "pages/purchase_returns.py", label="Purchase Returns", icon="📤"
      )

      st.subheader("Master Data")
      st.page_link("pages/medicines.py", label="Medicines", icon="💊")
      st.page_link("pages/categories.py", label="Categories", icon="🏷️")
      st.page_link(
          "pages/manufacturers.py", label="Manufacturers", icon="🏢"
      )
      st.page_link("pages/customers.py", label="Customers", icon="📇")
      st.page_link("pages/suppliers.py", label="Suppliers", icon="🏢")

      st.subheader("System & Security")
      st.page_link("pages/audit_logs.py", label="Audit Logs", icon="📜")
      # إضافة رابط صفحة حركات المخزون هنا
      st.page_link(
          "pages/stock_movements.py", label="Stock Movements", icon="📊"
      )
      st.page_link("pages/users.py", label="Users Management", icon="👥")
      st.page_link(
          "pages/notifications.py", label="Notifications", icon="🔔"
      )

      st.markdown("---")

      # Logout Logic
      if st.button("🚪 Logout", use_container_width=True):
        st.session_state.clear()
        st.rerun()

    else:
      st.info("Please login to access system features.")
      st.page_link("pages/login.py", label="Login", icon="🔑")