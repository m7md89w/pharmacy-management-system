import streamlit as st

from services.api_client import (
    get,
    post
)

st.set_page_config(
    page_title="Sales Returns",
    page_icon="↩️",
    layout="wide"
)

st.title("↩️ Sales Returns")


# ==================================================
# AUTH
# ==================================================
if "token" not in st.session_state:
    st.warning("Please login first.")
    st.stop()

if "selected_sales_return" not in st.session_state:
    st.session_state.selected_sales_return = None

if "selected_return_invoice" not in st.session_state:
    st.session_state.selected_return_invoice = None


# ==================================================
# LOAD COMPLETED INVOICES
# ==================================================
response = get(
    "/sales-invoices/status/COMPLETED",
    st.session_state.token
)

if response.status_code != 200:

    st.error(
        "Failed to load invoices."
    )

    st.stop()

invoices = response.json()

invoice_map = {

    invoice["invoice_id"]: invoice

    for invoice in invoices

}


# ==================================================
# CREATE / OPEN RETURN
# ==================================================
with st.expander(
    "➕ Create / Open Sales Return",
    expanded=False
):

    invoice_options = {

        f"{invoice['invoice_number']} (#{invoice['invoice_id']})":
        invoice["invoice_id"]

        for invoice in invoices

    }

    if invoice_options:

        selected_invoice = st.selectbox(
            "Invoice",
            list(invoice_options.keys())
        )

        if st.button(
            "Create / Open Return",
            type="primary",
            use_container_width=True
        ):

            invoice_id = invoice_options[
                selected_invoice
            ]

            # ==========================================
            # CHECK FOR DRAFT
            # ==========================================
            response = get(
                f"/sales-returns/invoice/{invoice_id}/draft",
                st.session_state.token
            )

            if response.status_code == 200:

                data = response.json()

                st.session_state.selected_sales_return = (
                    data["return_id"]
                )

                st.switch_page(
                    "pages/sales_return_details.py"
                )

            else:

                response = post(
                    "/sales-returns/",
                    {
                        "invoice_id": invoice_id
                    },
                    st.session_state.token
                )

                if response.status_code in (
                    200,
                    201
                ):

                    data = response.json()

                    st.session_state.selected_sales_return = (
                        data["return_id"]
                    )

                    st.switch_page(
                        "pages/sales_return_details.py"
                    )

                else:

                    try:
                        error = response.json()["error"]
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
# LOAD RETURNED INVOICES
# ==================================================
response = get(
    "/sales-returns/invoices",
    st.session_state.token
)

if response.status_code != 200:

    st.error(
        "Failed to load returned invoices."
    )

    st.stop()

returned_invoices = response.json()


# ==================================================
# FILTER
# ==================================================
if search:

    query = search.lower()

    returned_invoices = [

        invoice

        for invoice in returned_invoices

        if (

            query in str(
                invoice["invoice_id"]
            )

            or

            query in invoice[
                "invoice_number"
            ].lower()

        )

    ]


# ==================================================
# TABLE HEADER
# ==================================================
st.divider()

st.subheader(
    f"Returned Invoices ({len(returned_invoices)})"
)

if not returned_invoices:

    st.info(
        "No returned invoices found."
    )

    st.stop()


for invoice in returned_invoices:

    col1, col2, col3, col4, col5 = (
        st.columns(
            [2, 3, 2, 2, 1]
        )
    )

    # ==========================================
    # INVOICE
    # ==========================================
    with col1:

        st.write(
            invoice["invoice_number"]
        )

        st.caption(
            f"Invoice #{invoice['invoice_id']}"
        )

    # ==========================================
    # RETURNS
    # ==========================================
    with col2:

        st.write(
            f"Returns: {invoice['returns_count']}"
        )

        st.caption(
            f"Returned Amount: "
            f"{invoice['total_returned']:.2f} JOD"
        )

    # ==========================================
    # STATUS
    # ==========================================
    with col3:

        if invoice["returns_count"] == 0:

            st.info(
                "No Returns"
            )

        elif invoice["returns_count"] == 1:

            st.success(
                "1 Return"
            )

        else:

            st.warning(
                f"{invoice['returns_count']} Returns"
            )

    # ==========================================
    # VIEW HISTORY
    # ==========================================
    with col4:

        if st.button(
            "📜 View History",
            key=f"history_{invoice['invoice_id']}"
        ):

            st.session_state.selected_return_invoice = (
                invoice["invoice_id"]
            )

            st.switch_page(
                "pages/sales_return_history.py"
            )

    # ==========================================
    # NEW RETURN
    # ==========================================
    with col5:

        if st.button(
            "➕ New Return",
            key=f"new_return_{invoice['invoice_id']}"
        ):

            # --------------------------------------
            # يوجد Draft؟
            # --------------------------------------
            response = get(
                f"/sales-returns/invoice/{invoice['invoice_id']}/draft",
                st.session_state.token
            )

            if response.status_code == 200:

                data = response.json()

                st.session_state.selected_sales_return = (
                    data["return_id"]
                )

                st.switch_page(
                    "pages/sales_return_details.py"
                )

            else:

                response = post(
                    "/sales-returns/",
                    {
                        "invoice_id":
                            invoice["invoice_id"]
                    },
                    st.session_state.token
                )

                if response.status_code in (
                    200,
                    201
                ):

                    data = response.json()

                    st.session_state.selected_sales_return = (
                        data["return_id"]
                    )

                    st.switch_page(
                        "pages/sales_return_details.py"
                    )

                else:

                    try:
                        error = response.json()["error"]
                    except:
                        error = response.text

                    st.error(error)

    st.divider()