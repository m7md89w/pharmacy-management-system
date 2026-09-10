import streamlit as st

from services.api_client import (
    get,
    post
)
from components.sidebar import render_sidebar

st.set_page_config(
    page_title="Purchase Returns",
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

st.title("↩️ Purchase Returns")

# ==================================================
# AUTH
# ==================================================
token = st.session_state.get("token") or st.session_state.get("access_token")

if not token:

    st.warning(
        "Please login first."
    )
    if st.button("Go to Login / Main Page"):
        st.switch_page("app.py")
    st.stop()

if "selected_purchase_return" not in st.session_state:
    st.session_state.selected_purchase_return = None

if "selected_return_purchase" not in st.session_state:
    st.session_state.selected_return_purchase = None

# ==================================================
# LOAD RECEIVED PURCHASES
# ==================================================
response = get(
    "/purchase-orders/status/RECEIVED",
    token=token
)

if response.status_code != 200:

    st.error(
        "Failed to load purchase orders."
    )

    st.stop()

purchases = response.json()

purchase_map = {

    purchase["purchase_id"]: purchase

    for purchase in purchases

}

# ==================================================
# CREATE / OPEN RETURN
# ==================================================
with st.expander(
    "➕ Create / Open Purchase Return",
    expanded=False
):

    purchase_options = {

        f"PO #{purchase['purchase_id']}":
        purchase["purchase_id"]

        for purchase in purchases

    }

    if purchase_options:

        selected_purchase = st.selectbox(
            "Purchase Order",
            list(
                purchase_options.keys()
            )
        )

        if st.button(
            "Create / Open Return",
            type="primary",
            use_container_width=True
        ):

            purchase_id = purchase_options[
                selected_purchase
            ]

            response = get(
                f"/purchase-returns/purchase/{purchase_id}/draft",
                token=token
            )

            if response.status_code == 200:

                data = response.json()

                if data:

                    st.session_state.selected_purchase_return = (
                        data["return_id"]
                    )

                else:

                    response = post(

                        "/purchase-returns/",

                        {
                            "purchase_id": purchase_id
                        },

                        token=token

                    )

                    if response.status_code not in (
                        200,
                        201
                    ):

                        try:
                            st.error(
                                response.json()["error"]
                            )
                        except Exception:
                            st.error(
                                response.text
                            )

                        st.stop()

                    data = response.json()

                    st.session_state.selected_purchase_return = (
                        data["return_id"]
                    )

                st.switch_page(
                    "pages/purchase_return_details.py"
                )

            else:

                st.error(
                    "Failed to open purchase return."
                )


# ==================================================
# SEARCH
# ==================================================
st.divider()

search = st.text_input(
    "🔍 Search Purchase Order"
)

# ==================================================
# LOAD RETURNED PURCHASES
# ==================================================
response = get(
    "/purchase-returns/purchases",
    token=token
)

if response.status_code != 200:

    st.error(
        "Failed to load returned purchase orders."
    )

    st.stop()

returned_purchases = response.json()

# ==================================================
# FILTER
# ==================================================
if search:

    query = search.lower()

    returned_purchases = [

        purchase

        for purchase in returned_purchases

        if query in str(
            purchase["purchase_id"]
        )

    ]

# ==================================================
# TABLE
# ==================================================
st.divider()

st.subheader(
    f"Returned Purchase Orders ({len(returned_purchases)})"
)

if not returned_purchases:

    st.info(
        "No returned purchase orders found."
    )

    st.stop()

for purchase in returned_purchases:

    col1, col2, col3, col4 = st.columns(
        [3, 3, 2, 2]
    )

    with col1:

        st.write(
            f"Purchase #{purchase['purchase_id']}"
        )

    with col2:

        st.write(
            f"Returns: {purchase['returns_count']}"
        )

        st.caption(
            f"Returned Amount: "
            f"{purchase['total_returned']:.2f} JOD"
        )

    with col3:

        if st.button(
            "📜 History",
            key=f"history_{purchase['purchase_id']}"
        ):

            st.session_state.selected_return_purchase = (
                purchase["purchase_id"]
            )

            st.switch_page(
                "pages/purchase_return_history.py"
            )

    with col4:

        if st.button(
            "➕ New Return",
            key=f"new_return_{purchase['purchase_id']}"
        ):

            response = get(
                f"/purchase-returns/purchase/{purchase['purchase_id']}/draft",
                token=token
            )

            if response.status_code == 200:

                data = response.json()

                if data:

                    st.session_state.selected_purchase_return = (
                        data["return_id"]
                    )

                else:

                    response = post(
                        "/purchase-returns/",
                        {
                            "purchase_id":
                                purchase["purchase_id"]
                        },
                        token=token
                    )

                    if response.status_code not in (
                        200,
                        201
                    ):

                        try:
                            st.error(
                                response.json()["error"]
                            )
                        except Exception:
                            st.error(
                                response.text
                            )

                        st.stop()

                    data = response.json()

                    st.session_state.selected_purchase_return = (
                        data["return_id"]
                    )

            else:

                st.error(
                    "Failed to open purchase return."
                )

                st.stop()

            st.switch_page(
                "pages/purchase_return_details.py"
            )

    st.divider()