import streamlit as st

from services.api_client import (
    get,
    post,
    delete
)
from components.sidebar import render_sidebar

st.set_page_config(
    page_title="Sales Returns",
    page_icon="↩️",
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

st.title("↩️ Sales Returns")


# ==================================================
# AUTH
# ==================================================
token = st.session_state.get("token") or st.session_state.get("access_token")

if not token:
    st.warning("Please login first.")
    if st.button("Go to Login / Main Page"):
        st.switch_page("app.py")
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
    token=token
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
                token=token
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
                    token=token
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
                    except Exception:
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
    token=token
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

    col1, col2, col3, col4, col5, col6 = (
        st.columns(
            [2, 2, 2, 2, 1, 1]
        )
    )

    # التحقق مما إذا كان هناك مسودة (Draft) فارغة لهذه الفاتورة
    draft_response = get(
        f"/sales-returns/invoice/{invoice['invoice_id']}/draft",
        token=token
    )
    has_empty_draft = False
    draft_return_id = None
    if draft_response.status_code == 200:
        draft_data = draft_response.json()
        draft_return_id = draft_data.get("return_id")
        if draft_return_id:
            items_response = get(
                f"/sales-return-items/return/{draft_return_id}",
                token=token
            )
            if items_response.status_code == 200:
                draft_items = items_response.json()
                if len(draft_items) == 0:
                    has_empty_draft = True

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
            if has_empty_draft:
                st.warning("Draft (Empty)")
            else:
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
    # DELETE DRAFT (IF EMPTY)
    # ==========================================
    with col5:
        if has_empty_draft and draft_return_id:
            if st.button(
                "🗑️",
                key=f"delete_draft_{invoice['invoice_id']}"
            ):
                del_response = delete(
                    f"/sales-returns/{draft_return_id}",
                    token=token
                )
                if del_response.status_code == 200:
                    st.success("Draft return deleted successfully.")
                    st.rerun()
                else:
                    try:
                        error = del_response.json()["error"]
                    except Exception:
                        error = del_response.text
                    st.error(error)

    # ==========================================
    # NEW RETURN / OPEN
    # ==========================================
    with col6:

        if st.button(
            "➕ New Return",
            key=f"new_return_{invoice['invoice_id']}"
        ):

            # --------------------------------------
            # يوجد Draft؟
            # --------------------------------------
            response = get(
                f"/sales-returns/invoice/{invoice['invoice_id']}/draft",
                token=token
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
                    token=token
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
                    except Exception:
                        error = response.text

                    st.error(error)

    st.divider()