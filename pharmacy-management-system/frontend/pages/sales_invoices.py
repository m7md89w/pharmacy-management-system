import streamlit as st

from services.api_client import (
    get,
    post,
    put,
    delete
)

st.set_page_config(
    page_title="Sales Invoices",
    page_icon="💰",
    layout="wide"
)

st.title("💰 Sales Invoices")


# ==================================================
# AUTH
# ==================================================
if "token" not in st.session_state:
    st.warning("Please login first.")
    st.stop()

if "selected_invoice" not in st.session_state:
    st.session_state.selected_invoice = None


# ==================================================
# LOAD CUSTOMERS
# ==================================================
response = get(
    "/customers/",
    st.session_state.token
)

customers = []
customer_map = {}

if response.status_code == 200:

    customers = response.json()

    customer_map = {
        customer["customer_id"]:
        customer["full_name"]
        for customer in customers
    }


# ==================================================
# CREATE INVOICE
# ==================================================
with st.expander(
    "➕ Create Sales Invoice"
):

    customer_names = [
        "Walk-in Customer"
    ]

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

    if st.button(
        "Create Invoice",
        type="primary"
    ):

        data = {
            "payment_method":
                payment_method
        }

        if (
            customer_name
            != "Walk-in Customer"
        ):

            customer = next(
                c
                for c in customers
                if c["full_name"]
                == customer_name
            )

            data["customer_id"] = (
                customer[
                    "customer_id"
                ]
            )

        response = post(
            "/sales-invoices/",
            data,
            st.session_state.token
        )

        if response.status_code == 201:

            st.success(
                "Invoice created successfully."
            )

            st.rerun()

        else:

            try:
                error = (
                    response.json()["error"]
                )
            except:
                error = response.text

            st.error(error)


# ==================================================
# SEARCH
# ==================================================
st.divider()

search = st.text_input(
    "🔍 Search Invoice"
)


# ==================================================
# LOAD INVOICES
# ==================================================
response = get(
    "/sales-invoices/",
    st.session_state.token
)

if response.status_code != 200:
    st.error(
        "Failed to load invoices."
    )
    st.stop()

invoices = response.json()


# ==================================================
# FILTER
# ==================================================
if search:

    query = search.lower()

    invoices = [
        invoice
        for invoice in invoices
        if (
            query
            in str(
                invoice["invoice_id"]
            )
            or
            query
            in invoice[
                "invoice_number"
            ].lower()
            or
            query
            in invoice[
                "status"
            ].lower()
        )
    ]


# ==================================================
# HEADER
# ==================================================
st.subheader(
    f"Invoices ({len(invoices)})"
)

if not invoices:
    st.info(
        "No invoices found."
    )
    st.stop()


# ==================================================
# INVOICES
# ==================================================
for invoice in invoices:

    col1, col2, col3, col4, col5, col6, col7 = (
        st.columns(
            [2, 3, 2, 2, 1, 1, 1]
        )
    )

    with col1:

        st.write(
            invoice[
                "invoice_number"
            ]
        )

        if invoice.get(
            "sale_date"
        ):
            st.caption(
                invoice[
                    "sale_date"
                ]
            )

    with col2:

        customer_name = (
            customer_map.get(
                invoice[
                    "customer_id"
                ],
                "Walk-in Customer"
            )
        )

        st.write(
            customer_name
        )

    with col3:

        status = invoice[
            "status"
        ]

        if status == "DRAFT":
            st.warning(status)

        elif status == "COMPLETED":
            st.success(status)

        elif status == "CANCELLED":
            st.error(status)

        elif status == "REFUNDED":
            st.info(status)

    with col4:

        st.write(
            f"{invoice['total_amount']} JOD"
        )

    # ==========================================
    # DETAILS
    # ==========================================
    with col5:

        if st.button(
            "👁",
            key=f"view_{invoice['invoice_id']}"
        ):

            st.session_state.selected_invoice = (
                invoice["invoice_id"]
            )

            st.switch_page(
                "pages/sale_details.py"
            )

    # ==========================================
    # COMPLETE
    # ==========================================
    with col6:

        if invoice["status"] == "DRAFT":

            if st.button(
                "✅",
                key=f"complete_{invoice['invoice_id']}"
            ):

                response = put(
                    f"/sales-invoices/{invoice['invoice_id']}",
                    {
                        "status": "COMPLETED"
                    },
                    st.session_state.token
                )

                if response.status_code == 200:

                    st.success(
                        "Invoice completed."
                    )

                    st.rerun()

                else:

                    try:
                        error = (
                            response.json()["error"]
                        )
                    except:
                        error = response.text

                    st.error(error)

    # ==========================================
    # DELETE
    # ==========================================
    with col7:

        if invoice["status"] == "DRAFT":

            if st.button(
                "🗑️",
                key=f"delete_{invoice['invoice_id']}"
            ):

                response = delete(
                    f"/sales-invoices/{invoice['invoice_id']}",
                    st.session_state.token
                )

                if response.status_code == 200:

                    st.success(
                        "Invoice deleted."
                    )

                    st.rerun()

                else:

                    try:
                        error = (
                            response.json()["error"]
                        )
                    except:
                        error = response.text

                    st.error(error)

    st.divider()