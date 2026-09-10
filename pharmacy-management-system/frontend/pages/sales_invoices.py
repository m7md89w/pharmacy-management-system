import streamlit as st

from services.api_client import (
    get,
    post,
    put,
    delete
)
from components.sidebar import render_sidebar

st.set_page_config(
    page_title="Sales Invoices",
    page_icon="💰",
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

st.title("💰 Sales Invoices")


# ==================================================
# AUTHENTICATION GUARD
# ==================================================
token = st.session_state.get("token") or st.session_state.get("access_token")

if not token:
    st.warning("Please log in first.")
    if st.button("Go to Login / Main Page"):
        st.switch_page("app.py")
    st.stop()

if "selected_invoice" not in st.session_state:
    st.session_state.selected_invoice = None


# ==================================================
# LOAD CUSTOMERS
# ==================================================
response = get(
    "/customers/",
    token=token
)

customers = []
customer_map = {}

if response.status_code == 200:
    customers = response.json()
    customer_map = {
        customer["customer_id"]: customer["full_name"]
        for customer in customers
    }
else:
    # معالجة الخطأ في حال تعذر جلب العملاء
    try:
        error_msg = response.json().get("error", "Failed to load customers.")
    except Exception:
        error_msg = response.text
    st.error(error_msg)


# ==================================================
# CREATE INVOICE
# ==================================================
with st.expander("➕ Create Sales Invoice"):

    customer_names = ["Walk-in Customer"]
    customer_names.extend([
        customer["full_name"]
        for customer in customers
    ])

    customer_name = st.selectbox(
        "Customer",
        customer_names
    )

    payment_method = st.selectbox(
        "Payment Method",
        [
            "CASH",
            "CARD",
            "INSURANCE",
            "OTHER"
        ]
    )

    if st.button("Create Invoice", type="primary"):

        data = {
            "payment_method": payment_method
        }

        if customer_name != "Walk-in Customer":
            customer = next(
                c for c in customers
                if c["full_name"] == customer_name
            )
            data["customer_id"] = customer["customer_id"]

        response = post(
            "/sales-invoices/",
            data,
            token=token
        )

        if response.status_code == 201:
            st.success("Invoice created successfully.")
            st.rerun()
        else:
            try:
                error = response.json().get("error", response.text)
            except Exception:
                error = response.text
            st.error(error)


# ==================================================
# SEARCH
# ==================================================
st.divider()

search = st.text_input("🔍 Search Invoice")


# ==================================================
# LOAD INVOICES
# ==================================================
response = get(
    "/sales-invoices/",
    token=token
)

if response.status_code != 200:
    try:
        error_msg = response.json().get("error", "Failed to load invoices.")
    except Exception:
        error_msg = response.text
    st.error(error_msg)
    st.stop()

invoices = response.json()


# ==================================================
# FILTER
# ==================================================
if search:
    query = search.lower()
    invoices = [
        invoice for invoice in invoices
        if (
            query in str(invoice.get("invoice_id", ""))
            or query in invoice.get("invoice_number", "").lower()
            or query in invoice.get("status", "").lower()
        )
    ]


# ==================================================
# HEADER
# ==================================================
st.subheader(f"Invoices ({len(invoices)})")

if not invoices:
    st.info("No invoices found.")
    st.stop()


# ==================================================
# INVOICES LIST & ACTIONS
# ==================================================
for invoice in invoices:

    col1, col2, col3, col4, col5, col6, col7 = st.columns(
        [2, 3, 2, 2, 1, 1, 1]
    )

    with col1:
        st.write(invoice.get("invoice_number", ""))
        if invoice.get("sale_date"):
            st.caption(invoice["sale_date"])

    with col2:
        customer_name = customer_map.get(
            invoice.get("customer_id"),
            "Walk-in Customer"
        )
        st.write(customer_name)

    with col3:
        status = invoice.get("status", "")
        if status == "DRAFT":
            st.warning(status)
        elif status == "COMPLETED":
            st.success(status)
        elif status == "CANCELLED":
            st.error(status)
        elif status == "REFUNDED":
            st.info(status)
        else:
            st.write(status)

    with col4:
        total = invoice.get("total_amount", 0.0)
        st.write(f"{total} JOD")

    # ==========================================
    # DETAILS
    # ==========================================
    with col5:
        if st.button("👁", key=f"view_{invoice['invoice_id']}"):
            st.session_state.selected_invoice = invoice["invoice_id"]
            st.switch_page("pages/sale_details.py")

    # ==========================================
    # COMPLETE
    # ==========================================
    with col6:
        if invoice.get("status") == "DRAFT":
            if st.button("✅", key=f"complete_{invoice['invoice_id']}"):
                response = put(
                    f"/sales-invoices/{invoice['invoice_id']}",
                    {"status": "COMPLETED"},
                    token=token
                )

                if response.status_code == 200:
                    st.success("Invoice completed.")
                    st.rerun()
                else:
                    try:
                        error = response.json().get("error", response.text)
                    except Exception:
                        error = response.text
                    st.error(error)

    # ==========================================
    # DELETE
    # ==========================================
    with col7:
        if invoice.get("status") == "DRAFT":
            if st.button("🗑️", key=f"delete_{invoice['invoice_id']}"):
                response = delete(
                    f"/sales-invoices/{invoice['invoice_id']}",
                    token=token
                )

                if response.status_code == 200:
                    st.success("Invoice deleted.")
                    st.rerun()
                else:
                    try:
                        error = response.json().get("error", response.text)
                    except Exception:
                        error = response.text
                    st.error(error)

    st.divider()