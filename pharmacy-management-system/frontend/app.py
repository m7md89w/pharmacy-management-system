import streamlit as st
from services.api_client import post

st.set_page_config(
    page_title="Pharmacy ERP",
    page_icon="💊",
    layout="wide"
)

# ==================================================
# SESSION
# ==================================================
if "token" not in st.session_state:
    st.session_state.token = None

if "user" not in st.session_state:
    st.session_state.user = None


# ==================================================
# LOGIN PAGE
# ==================================================
def login_page():

    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:

        st.title("💊 Pharmacy ERP")
        st.subheader("Login")

        username = st.text_input(
            "Username"
        )

        password = st.text_input(
            "Password",
            type="password"
        )

        if st.button(
            "Login",
            use_container_width=True,
            type="primary"
        ):

            response = post(
                "/auth/login",
                {
                    "username": username,
                    "password": password
                }
            )

            if response.status_code == 200:

                data = response.json()

                st.session_state.token = (
                    data["access_token"]
                )

                st.session_state.user = data

                st.rerun()

            else:
                st.error(
                    "Invalid username or password."
                )


# ==================================================
# DASHBOARD
# ==================================================
def dashboard_page():

    user = st.session_state.user

    st.sidebar.title("💊 Pharmacy ERP")

    st.sidebar.success(
        f"👋 {user['username']}"
    )

    st.sidebar.divider()

    if st.sidebar.button(
        "🚪 Logout",
        use_container_width=True
    ):
        st.session_state.token = None
        st.session_state.user = None
        st.rerun()

    st.title(
        "💊 Pharmacy ERP Dashboard"
    )

    st.write(
        "Welcome to the Pharmacy Management System"
    )

    st.divider()

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button(
            "💊 Medicines",
            use_container_width=True
        ):
            st.switch_page(
                "pages/medicines.py"
            )

    with col2:
        if st.button(
            "🏢 Suppliers",
            use_container_width=True
        ):
            st.switch_page(
                "pages/suppliers.py"
            )

    with col3:
        if st.button(
            "📦 Inventory",
            use_container_width=True
        ):
            st.switch_page(
                "pages/inventory.py"
            )

    col4, col5, col6 = st.columns(3)

    with col4:
        if st.button(
            "🧾 Purchases",
            use_container_width=True
        ):
            st.switch_page(
                "pages/purchases.py"
            )

    with col5:
        if st.button(
            "🛒 Sales",
            use_container_width=True
        ):
            st.switch_page(
                "pages/sales_invoices.py"
            )

    with col6:
        if st.button(
            "📊 Reports",
            use_container_width=True
        ):
            st.switch_page(
                "pages/reports.py"
            )

    st.divider()

    st.subheader("System Modules")

    st.info(
        """
        ✅ Medicines Management  
        ✅ Suppliers Management  
        ✅ Inventory Management  
        ✅ Purchases Management  
        ✅ Sales Management  
        ✅ Reports & Analytics
        """
    )


# ==================================================
# APP
# ==================================================
if st.session_state.token:
    dashboard_page()
else:
    login_page()