import streamlit as st
from datetime import datetime
from services.api_client import (
    get,
    post,
    put,
    delete
)
from components.sidebar import render_sidebar

st.set_page_config(
    page_title="Purchase Details",
    page_icon="📄",
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

st.title("📄 Purchase Details")

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
    "selected_purchase"
    not in st.session_state
    or
    st.session_state.selected_purchase is None
):

    st.error(
        "No Purchase selected."
    )

    st.stop()

purchase_id = st.session_state.selected_purchase

# ==================================================
# LOAD PURCHASE
# ==================================================
response = get(
    f"/purchase-orders/{purchase_id}",
    token=token
)

if response.status_code != 200:

    st.error(
        "Purchase not found."
    )

    st.stop()

purchase = response.json()

# ==================================================
# LOAD SUPPLIERS
# ==================================================
response = get(
    "/suppliers/",
    token=token
)

supplier_name = "Unknown Supplier"

if response.status_code == 200:

    suppliers = response.json()

    for supplier in suppliers:

        if supplier["id"] == purchase["supplier_id"]:

            supplier_name = supplier["name"]

            break

# ==================================================
# LOAD PURCHASE ITEMS
# ==================================================
response = get(
    f"/purchase-items/purchase/{purchase_id}",
    token=token
)

purchase_items = []

if response.status_code == 200:

    purchase_items = response.json()

# ==================================================
# LOAD PURCHASE RETURNS
# ==================================================
response = get(
    f"/purchase-returns/purchase/{purchase_id}",
    token=token
)

purchase_returns = []

if response.status_code == 200:

    purchase_returns = response.json()

# ==================================================
# LOAD RETURN ITEMS
# ==================================================
response = get(
    f"/purchase-return-items/purchase/{purchase_id}",
    token=token
)

completed_return_items = []

if response.status_code == 200:

    completed_return_items = response.json()

returned_map = {}

for item in completed_return_items:

    returned_map[item["purchase_item_id"]] = (
        returned_map.get(
            item["purchase_item_id"],
            0
        )
        + item["quantity"]
    )

# ==================================================
# HEADER
# ==================================================
st.subheader(
    f"Purchase #{purchase['purchase_id']}"
)

c1, c2, c3 = st.columns(3)

with c1:

    st.write(
        f"Supplier: {supplier_name}"
    )

with c2:

    if purchase["status"] == "PENDING":

        st.warning("PENDING")

    elif purchase["status"] == "RECEIVED":

        st.success("RECEIVED")

    else:

        st.info(
            purchase["status"]
        )

with c3:

    st.metric(
        "Total Amount",
        f"{float(purchase['total_amount']):.2f} JOD"
    )

st.divider()


# ==================================================
# ADD PURCHASE ITEM
# ==================================================
if purchase["status"] == "PENDING":

    st.subheader("➕ Add Purchase Item")

    response = get(
        "/medicines/",
        token=token
    )

    medicines = []

    if response.status_code == 200:

        medicines = response.json()

    if not medicines:

        st.info(
            "No medicines found."
        )

    else:

        medicine_options = {

            medicine["commercial_name"]: medicine

            for medicine in medicines

        }

        selected_name = st.selectbox(
            "Medicine",
            list(medicine_options.keys())
        )

        selected_medicine = medicine_options[
            selected_name
        ]

        col1, col2 = st.columns(2)

        with col1:

            quantity = st.number_input(
                "Quantity",
                value=1
            )

            unit_cost = st.number_input(
                "Unit Cost",
                value=0.0,
                step=0.1
            )

            selling_price = st.number_input(
                "Selling Price",
                value=0.0,
                step=0.1
            )

        with col2:

            batch_number = st.text_input(
                "Batch Number"
            )

            manufacture_date = st.date_input(
                "Manufacture Date"
            )

            expiry_date = st.date_input(
                "Expiry Date"
            )

        if st.button(
            "➕ Add Item",
            type="primary",
            use_container_width=True
        ):

            response = post(

                "/purchase-items/",

                {

                    "purchase_id":
                        purchase_id,

                    "medicine_id":
                        selected_medicine["id"],

                    "quantity":
                        int(quantity),

                    "unit_cost":
                        float(unit_cost),

                    "selling_price":
                        float(selling_price),

                    "batch_number":
                        batch_number,

                    "manufacture_date":
                        str(manufacture_date),

                    "expiry_date":
                        str(expiry_date)

                },

                token=token

            )

            if response.status_code == 201:

                st.success(
                    "Purchase Item added successfully."
                )

                st.rerun()

            else:

                try:

                    st.error(
                        response.json()["error"]
                    )

                except Exception:

                    st.error(
                        response.text
                    )

st.divider()


# ==================================================
# PURCHASE ITEMS
# ==================================================
st.subheader(
    f"Purchase Items ({len(purchase_items)})"
)

if not purchase_items:

    st.info(
        "No purchase items."
    )

else:

    for item in purchase_items:

        returned = returned_map.get(
            item["purchase_item_id"],
            0
        )

        remaining = (
            item["quantity"]
            - returned
        )

        with st.expander(

            f"{item['medicine_name']} | "
            f"Batch: {item['batch_number']} | "
            f"Qty: {item['quantity']}"

        ):

            c1, c2, c3 = st.columns(3)

            with c1:

                st.write(
                    f"Purchased : {item['quantity']}"
                )

                st.write(
                    f"Returned : {returned}"
                )

                st.write(
                    f"Remaining : {remaining}"
                )

            with c2:

                st.write(
                    f"Unit Cost : {float(item['unit_cost']):.2f}"
                )

                st.write(
                    f"Selling : {float(item['selling_price']):.2f}"
                )

                st.write(
                    f"Subtotal : {float(item['subtotal']):.2f}"
                )

            with c3:

                if returned == 0:

                    st.success(
                        "Not Returned"
                    )

                elif remaining == 0:

                    st.error(
                        "Fully Returned"
                    )

                else:

                    st.warning(
                        "Partially Returned"
                    )

            # ======================================
            # EDIT
            # ======================================
            if purchase["status"] == "PENDING":

                st.divider()

                st.markdown(
                    "### ✏ Edit Item"
                )

                qty = st.number_input(

                    "Quantity",

                    value=item["quantity"],

                    key=f"qty_{item['purchase_item_id']}"

                )

                cost = st.number_input(

                    "Unit Cost",

                    value=float(item["unit_cost"]),

                    key=f"cost_{item['purchase_item_id']}"

                )

                sell = st.number_input(

                    "Selling Price",

                    value=float(item["selling_price"]),

                    key=f"sell_{item['purchase_item_id']}"

                )

                batch = st.text_input(

                    "Batch Number",

                    value=item["batch_number"],

                    key=f"batch_{item['purchase_item_id']}"

                )

                mfg = st.date_input(

                    "Manufacture Date",

                    value=datetime.strptime(item["manufacture_date"], "%Y-%m-%d").date() if isinstance(item["manufacture_date"], str) else item["manufacture_date"],

                    key=f"mfg_{item['purchase_item_id']}"

                )

                exp = st.date_input(

                    "Expiry Date",

                    value=datetime.strptime(item["expiry_date"], "%Y-%m-%d").date() if isinstance(item["expiry_date"], str) else item["expiry_date"],

                    key=f"exp_{item['purchase_item_id']}"

                )

                b1, b2 = st.columns(2)

                with b1:

                    if st.button(

                        "💾 Save",

                        key=f"save_{item['purchase_item_id']}",

                        use_container_width=True

                    ):

                        response = put(

                            f"/purchase-items/{item['purchase_item_id']}",

                            {

                                "quantity": qty,

                                "unit_cost": cost,

                                "selling_price": sell,

                                "batch_number": batch,

                                "manufacture_date": str(mfg),

                                "expiry_date": str(exp)

                            },

                            token=token

                        )

                        if response.status_code == 200:

                            st.success(
                                "Updated successfully."
                            )

                            st.rerun()

                        else:

                            try:

                                st.error(
                                    response.json()["error"]
                                )

                            except Exception:

                                st.error(
                                    response.text
                                )

                with b2:

                    if st.button(

                        "🗑 Delete",

                        key=f"delete_{item['purchase_item_id']}",

                        use_container_width=True

                    ):

                        response = delete(

                            f"/purchase-items/{item['purchase_item_id']}",

                            token=token

                        )

                        if response.status_code == 200:

                            st.success(
                                "Deleted successfully."
                            )

                            st.rerun()

                        else:

                            try:

                                st.error(
                                    response.json()["error"]
                                )

                            except Exception:

                                st.error(
                                    response.text
                                )

# ==================================================
# RECEIVE PURCHASE
# ==================================================
st.divider()

if purchase["status"] == "PENDING":

    if st.button(

        "📦 Receive Purchase",

        type="primary",

        use_container_width=True

    ):

        response = put(

            f"/purchase-orders/{purchase_id}",

            {

                "status": "RECEIVED"

            },

            token=token

        )

        if response.status_code == 200:

            st.success(
                "Purchase received successfully."
            )

            st.rerun()

        else:

            try:

                st.error(
                    response.json()["error"]
                )

            except Exception:

                st.error(
                    response.text
                )


# ==================================================
# PURCHASE RETURNS
# ==================================================
st.divider()

st.subheader(
    "Purchase Returns"
)

completed_returns = [

    purchase_return

    for purchase_return in purchase_returns

    if purchase_return["status"] == "COMPLETED"

]

if not completed_returns:

    st.info(
        "No completed purchase returns."
    )

else:

    for purchase_return in completed_returns:

        with st.expander(

            f"Return #{purchase_return['return_id']}"

        ):

            st.write(

                f"Amount : "

                f"{float(purchase_return['total_amount']):.2f} JOD"

            )

            if purchase_return.get(
                "return_date"
            ):

                st.write(

                    purchase_return[
                        "return_date"
                    ]

                )

            if st.button(

                "Open Return",

                key=f"return_{purchase_return['return_id']}"

            ):

                st.session_state.selected_purchase_return = (

                    purchase_return["return_id"]

                )

                st.switch_page(

                    "pages/purchase_return_details.py"

                )


# ==================================================
# SUMMARY
# ==================================================
st.divider()

purchased = sum(

    item["quantity"]

    for item in purchase_items

)

returned = sum(

    returned_map.values()

)

remaining = purchased - returned

c1, c2, c3 = st.columns(3)

with c1:

    st.metric(
        "Purchased",
        purchased
    )

with c2:

    st.metric(
        "Returned",
        returned
    )

with c3:

    st.metric(
        "Remaining",
        remaining
    )


# ==================================================
# CREATE PURCHASE RETURN
# ==================================================
st.divider()

if (

    purchase["status"] == "RECEIVED"

    and

    remaining > 0

):

    if st.button(

        "↩ Create Purchase Return",

        type="primary",

        use_container_width=True

    ):

        response = post(

            "/purchase-returns/",

            {

                "purchase_id":
                    purchase_id

            },

            token=token

        )

        if response.status_code in [200, 201]:

            data = response.json()

            st.session_state.selected_purchase_return = (

                data["return_id"]

            )

            st.switch_page(

                "pages/purchase_return_details.py"

            )

        else:

            try:

                st.error(
                    response.json()["error"]
                )

            except Exception:

                st.error(
                    response.text
                )


elif purchase["status"] == "RECEIVED":

    st.success(
        "All quantities have already been returned."
    )


# ==================================================
# REFRESH
# ==================================================
if st.button(

    "🔄 Refresh",

    use_container_width=True

):

    st.rerun()