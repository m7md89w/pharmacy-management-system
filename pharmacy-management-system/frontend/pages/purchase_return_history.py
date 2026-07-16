import streamlit as st

from services.api_client import (
    get
)

st.set_page_config(
    page_title="Purchase Return History",
    page_icon="📜",
    layout="wide"
)

st.title("📜 Purchase Return History")

# ==================================================
# AUTH
# ==================================================
if "token" not in st.session_state:

    st.warning(
        "Please login first."
    )

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
    st.session_state.token
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


