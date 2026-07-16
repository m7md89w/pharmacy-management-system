import streamlit as st

from services.api_client import (
    get
)

st.set_page_config(
    page_title="Return History",
    page_icon="📜",
    layout="wide"
)

st.title("📜 Return History")


# ==================================================
# AUTH
# ==================================================
if "token" not in st.session_state:

    st.warning(
        "Please login first."
    )

    st.stop()


if (
    "selected_return_invoice"
    not in st.session_state
):

    st.warning(
        "No invoice selected."
    )

    st.stop()


invoice_id = (
    st.session_state.selected_return_invoice
)


# ==================================================
# LOAD INVOICE
# ==================================================
response = get(
    f"/sales-invoices/{invoice_id}",
    st.session_state.token
)

if response.status_code != 200:

    st.error(
        "Invoice not found."
    )

    st.stop()

invoice = response.json()


# ==================================================
# LOAD RETURNS
# ==================================================
response = get(
    f"/sales-returns/invoice/{invoice_id}",
    st.session_state.token
)

if response.status_code != 200:

    st.error(
        "Failed to load return history."
    )

    st.stop()

returns = response.json()


# ==================================================
# HEADER
# ==================================================
st.subheader(
    f"Invoice {invoice['invoice_number']}"
)

st.caption(
    f"Invoice ID: {invoice_id}"
)

st.write(
    f"Total Returns: {len(returns)}"
)

st.divider()

# ==================================================
# NO RETURNS
# ==================================================
if not returns:

    st.info(
        "No returns found for this invoice."
    )

    if st.button(
        "⬅ Back"
    ):

        st.switch_page(
            "pages/sales_return.py"
        )

    st.stop()


# ==================================================
# RETURN HISTORY
# ==================================================
for sales_return in returns:

    col1, col2, col3, col4 = (
        st.columns(
            [2, 2, 2, 1]
        )
    )

    with col1:

        st.write(
            f"Return #{sales_return['return_id']}"
        )

        if sales_return.get(
            "return_date"
        ):

            st.caption(
                sales_return["return_date"]
            )

    with col2:

        if (
            sales_return["status"]
            == "COMPLETED"
        ):

            st.success(
                "COMPLETED"
            )

        elif (
            sales_return["status"]
            == "DRAFT"
        ):

            st.warning(
                "DRAFT"
            )

        else:

            st.write(
                sales_return["status"]
            )

    with col3:

        st.write(
            f"{float(sales_return['total_amount']):.2f} JOD"
        )

    with col4:

        if st.button(
            "👁 View",
            key=f"view_{sales_return['return_id']}"
        ):

            st.session_state.selected_sales_return = (
                sales_return["return_id"]
            )

            st.switch_page(
                "pages/sales_return_details.py"
            )

    st.divider()


# ==================================================
# BACK
# ==================================================
if st.button(
    "⬅ Back to Returns",
    use_container_width=True
):

    st.switch_page(
        "pages/sales_return.py"
    )