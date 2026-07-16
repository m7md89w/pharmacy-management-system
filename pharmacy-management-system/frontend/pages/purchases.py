import streamlit as st

from services.api_client import (
    get,
    post,
    put,
    delete
)

st.set_page_config(
    page_title="Purchase Orders",
    page_icon="🧾",
    layout="wide"
)

st.title("🧾 Purchase Orders")


# ==================================================
# AUTH
# ==================================================
if "token" not in st.session_state:
    st.warning("Please login first.")
    st.stop()

if "selected_purchase" not in st.session_state:
    st.session_state.selected_purchase = None


# ==================================================
# LOAD SUPPLIERS
# ==================================================
response = get(
    "/suppliers/",
    st.session_state.token
)

if response.status_code != 200:
    st.error("Failed to load suppliers.")
    st.stop()

suppliers = response.json()

supplier_map = {
    supplier["id"]: supplier["name"]
    for supplier in suppliers
}


# ==================================================
# CREATE PURCHASE ORDER
# ==================================================
with st.expander("➕ Create Purchase Order"):

    if suppliers:

        supplier_name = st.selectbox(
            "Supplier",
            [s["name"] for s in suppliers]
        )

        if st.button(
            "Create Purchase Order",
            type="primary"
        ):

            supplier_id = next(
                    supplier["id"]
                    for supplier in suppliers
                    if supplier["name"] == supplier_name
                )
            response = post(
                "/purchase-orders/",
                {
                    "supplier_id": supplier_id
                },
                st.session_state.token
            )

            if response.status_code == 201:

                st.success(
                    "Purchase order created successfully."
                )

                st.rerun()

            else:

                try:
                    error = response.json()["error"]
                except:
                    error = response.text

                st.error(error)

    else:

        st.info(
            "No suppliers found."
        )


# ==================================================
# SEARCH
# ==================================================
st.divider()

search = st.text_input(
    "🔍 Search Purchase Order"
)


# ==================================================
# LOAD ORDERS
# ==================================================
response = get(
    "/purchase-orders/",
    st.session_state.token
)

if response.status_code != 200:
    st.error(
        "Failed to load purchase orders."
    )
    st.stop()

orders = response.json()

# ==================================================
# FILTER
# ==================================================
if search:

    query = search.lower()

    orders = [
        order
        for order in orders
        if (
            query in str(
                order["purchase_id"]
            )
            or
            query in supplier_map.get(
                order["supplier_id"],
                ""
            ).lower()
            or
            query in order["status"].lower()
        )
    ]


# ==================================================
# TABLE HEADER
# ==================================================
st.subheader(
    f"Purchase Orders ({len(orders)})"
)

if not orders:

    st.info(
        "No purchase orders found."
    )

    st.stop()


# ==================================================
# PURCHASE ORDERS
# ==================================================
for order in orders:

    col1, col2, col3, col4, col5, col6, col7 = (
        st.columns([1, 3, 2, 2, 1, 1, 1])
    )

    with col1:

        st.write(
            f"#{order['purchase_id']}"
        )

    with col2:

        st.write(
            supplier_map.get(
                order["supplier_id"],
                "Unknown Supplier"
            )
        )

        if order.get("order_date"):

            st.caption(
                order["order_date"]
            )

    with col3:

        status = order["status"]

        if status == "PENDING":
            st.warning(status)

        elif status == "RECEIVED":
            st.success(status)

        elif status == "CANCELLED":
            st.error(status)

        else:
            st.info(status)

    with col4:

        st.write(
            f"{float(order['total_amount']):.2f} JOD"
        )

    # ==========================================
    # VIEW DETAILS
    # ==========================================
    with col5:

        if st.button(
            "👁",
            key=f"view_{order['purchase_id']}"
        ):

            st.session_state.selected_purchase = (
                order["purchase_id"]
            )

            st.switch_page(
                "pages/purchase_details.py"
            )

    # ==========================================
    # RECEIVE ORDER
    # ==========================================
    with col6:

        if order["status"] == "PENDING":

            if st.button(
                "📦",
                key=f"receive_{order['purchase_id']}"
            ):

                response = put(
                    f"/purchase-orders/{order['purchase_id']}",
                    {
                        "status": "RECEIVED"
                    },
                    st.session_state.token
                )

                if response.status_code == 200:

                    st.success(
                        "Purchase order received successfully."
                    )

                    st.rerun()

                else:

                    try:
                        error = response.json()["error"]
                    except:
                        error = response.text

                    st.error(error)

    # ==========================================
    # DELETE
    # ==========================================
    with col7:

        if order["status"] == "PENDING":

            if st.button(
                "🗑️",
                key=f"delete_{order['purchase_id']}"
            ):

                response = delete(
                    f"/purchase-orders/{order['purchase_id']}",
                    st.session_state.token
                )

                if response.status_code == 200:

                    st.success(
                        "Purchase order deleted successfully."
                    )

                    st.rerun()

                else:

                    try:
                        error = response.json()["error"]
                    except:
                        error = response.text

                    st.error(error)

    st.divider()