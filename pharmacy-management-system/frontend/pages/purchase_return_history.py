import streamlit as st

from services.api_client import (
    get
)
from components.sidebar import render_sidebar

st.set_page_config(
    page_title="Purchase Return History",
    page_icon="📜",
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

st.title("📜 Purchase Return History")

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

if (
    "selected_return_purchase"
    not in st.session_state
):

    st.warning(
        "No Purchase Order selected."
    )

    st.stop()

purchase_id = (
    st.session_state.selected_return_purchase
)


# ==================================================
# LOAD RETURNS
# ==================================================
response = get(
    f"/purchase-returns/purchase/{purchase_id}",
    token=token
)

if response.status_code != 200:

    st.error(
        "Failed to load purchase returns."
    )

    st.stop()

returns = response.json()


st.subheader(
    f"Purchase Order #{purchase_id}"
)

st.caption(
    f"Returns: {len(returns)}"
)

# ==================================================
# RETURNS TABLE
# ==================================================
st.divider()

if not returns:

    st.info(
        "No purchase returns found."
    )

else:

    for purchase_return in returns:

        col1, col2, col3, col4, col5 = (
            st.columns(
                [1, 2, 2, 2, 1]
            )
        )

        with col1:

            st.write(
                f"#{purchase_return['return_id']}"
            )

        with col2:

            if purchase_return["status"] == "COMPLETED":

                st.success(
                    purchase_return["status"]
                )

            else:

                st.warning(
                    purchase_return["status"]
                )

        with col3:

            st.write(
                purchase_return["return_date"]
            )

        with col4:

            st.write(
                f"{purchase_return['total_amount']:.2f} JOD"
            )

        with col5:

            if st.button(
                "📂 Open",
                key=f"return_{purchase_return['return_id']}"
            ):

                st.session_state.selected_purchase_return = (
                    purchase_return["return_id"]
                )

                st.switch_page(
                    "pages/purchase_return_details.py"
                )

        st.divider()

# ==================================================
# BACK
# ==================================================
if st.button(
    "⬅ Back",
    use_container_width=True
):

    st.switch_page(
        "pages/purchase_returns.py"
    )