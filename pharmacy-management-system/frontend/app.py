import streamlit as st
from components.sidebar import render_sidebar

# استيراد المكونات ودوال المصادقة
from services.auth import is_authenticated, login_user

# ==================================================
# PAGE CONFIGURATION
# ==================================================
st.set_page_config(
    page_title="Pharmacy ERP",
    page_icon="💊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================================================
# LOGIN PAGE
# ==================================================
def login_page():
    # إخفاء القائمة الجانبية تماماً في صفحة تسجيل الدخول
    st.markdown(
        """
        <style>
            [data-testid="collapsedControl"] {
                display: none;
            }
            [data-testid="stSidebar"] {
                display: none;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )

    _col1, col2, _col3 = st.columns([1, 2, 1])

    with col2:
        st.title("💊 Pharmacy ERP")
        st.subheader("System Login")

        with st.form(key="login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            
            submit_btn = st.form_submit_button(
                "Login",
                use_container_width=True,
                type="primary"
            )

            if submit_btn:
                if not username or not password:
                    st.warning("Please enter both username and password.")
                else:
                    with st.spinner("Authenticating..."):
                        success, message = login_user(username, password)
                        
                        if success:
                            # ضمان توحيد تخزين التوكن بالمفتاحين لتجنب أي ضياع للجلسة
                            token_val = st.session_state.get("token") or st.session_state.get("access_token")
                            if token_val:
                                st.session_state["token"] = token_val
                                st.session_state["access_token"] = token_val

                            st.success("Login successful! Redirecting...")
                            st.rerun()
                        else:
                            st.error(message)


# ==================================================
# DASHBOARD PAGE
# ==================================================
def dashboard_page():
    # إخفاء قائمة التنقل التلقائية لملفات الصفحات في الشريط الجانبي وإبقاء القائمة المخصصة
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

    st.title("💊 Pharmacy ERP Dashboard")
    st.write("Welcome to the Pharmacy Management System. Please select a module below or from the sidebar.")

    st.divider()

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("💊 Medicines", use_container_width=True):
            st.switch_page("pages/medicines.py")

    with col2:
        if st.button("🏢 Suppliers", use_container_width=True):
            st.switch_page("pages/suppliers.py")

    with col3:
        if st.button("📦 Inventory", use_container_width=True):
            st.switch_page("pages/inventory.py")

    col4, col5, col6 = st.columns(3)

    with col4:
        if st.button("🧾 Purchases", use_container_width=True):
            st.switch_page("pages/purchases.py")

    with col5:
        if st.button("🛒 Sales", use_container_width=True):
            st.switch_page("pages/sales_invoices.py")

    with col6:
        if st.button("📊 Reports", use_container_width=True):
            st.switch_page("pages/reports.py")

    st.divider()

    st.subheader("System Modules Status")

    st.info(
        """
        ✅ Medicines Management  
        ✅ Suppliers Management  
        ✅ Inventory Management  
        ✅ Purchases Management  
        ✅ Sales Management  
        ✅ Reports & Analytics  
        ✅ System Audit Logs
        """
    )


# ==================================================
# MAIN APP ROUTING
# ==================================================
if is_authenticated():
    dashboard_page()
else:
    login_page()

    