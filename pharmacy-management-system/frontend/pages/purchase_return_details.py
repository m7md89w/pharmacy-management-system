import streamlit as st

from services.api_client import (
    get,
    post,
    delete
)
from components.sidebar import render_sidebar

st.set_page_config(
    page_title="Purchase Return Details",
    page_icon="📦",
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

st.title("📦 Purchase Return Details")


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
    "selected_purchase_return"
    not in st.session_state
):

    st.warning(
        "No Purchase Return selected."
    )

    st.stop()

return_id = (
    st.session_state.selected_purchase_return
)


# ==================================================
# LOAD RETURN
# ==================================================
response = get(
    f"/purchase-returns/{return_id}",
    token=token
)

if response.status_code != 200:

    st.error(
        "Purchase Return not found."
    )

    st.stop()

purchase_return = response.json()

is_completed = (
    purchase_return["status"]
    ==
    "COMPLETED"
)


# ==================================================
# LOAD PURCHASE
# ==================================================
response = get(
    f"/purchase-orders/{purchase_return['purchase_id']}",
    token=token
)

if response.status_code != 200:

    st.error(
        "Purchase Order not found."
    )

    st.stop()

purchase = response.json()

st.subheader(
    f"Purchase Order #{purchase['purchase_id']}"
)

st.caption(
    f"Status: {purchase_return['status']}"
)
# ==================================================
# LOAD PURCHASE ITEMS
# ==================================================
response = get(
    f"/purchase-items/purchase/{purchase['purchase_id']}",
    token=token
)

if response.status_code != 200:

    st.error(
        "Failed to load purchase items."
    )

    st.stop()

purchase_items = response.json()

# ==================================================
# LOAD RETURN ITEMS
# ==================================================
response = get(
    f"/purchase-return-items/return/{return_id}",
    token=token
)

if response.status_code == 200:

    return_items = response.json()

else:

    return_items = []


# ==================================================
# LOAD COMPLETED RETURN ITEMS
# ==================================================
response = get(
    f"/purchase-return-items/purchase/{purchase['purchase_id']}",
    token=token
)

if response.status_code == 200:

    completed_return_items = response.json()

else:

    completed_return_items = []



# ==================================================
# BUILD RETURNED MAP
# ==================================================
returned_map = {}

for item in completed_return_items:

    returned_map[
        item["purchase_item_id"]
    ] = (

        returned_map.get(
            item["purchase_item_id"],
            0
        )

        +

        item["quantity"]

    )

# ==================================================
# BUILD AVAILABLE ITEMS
# ==================================================
available_items = []

for item in purchase_items:

    purchased = item["quantity"]

    returned = returned_map.get(
        item["purchase_item_id"],
        0
    )

    sold = item.get(
        "sold",
        0
    )

    remaining = (
        purchased
        - sold
        - returned
    )

    if remaining <= 0:
        continue

    available_items.append({

        **item,

        # الكمية المسموح بإرجاعها
        "quantity":
            remaining,

        "purchased":
            purchased,

        "sold":
            sold,

        "returned":
            returned,

        "remaining":
            remaining

    })


# ==================================================
# ADD ITEM
# ==================================================
if not is_completed:

    st.divider()

    st.subheader(
        "➕ Add Item"
    )

    if not available_items:

        st.info(
            "All purchase items have already been returned."
        )

    else:

        item_options = {

            (
                f"{item['medicine_name']}\n"
                f"Purchased: {item['purchased']} | "
                f"Returned: {item['returned']} | "
                f"Remaining: {item['remaining']}"
            ): item

            for item in available_items

        }

        selected = st.selectbox(

            "Purchase Item",

            list(item_options.keys())

        )

        selected_item = item_options[
            selected
        ]

        st.info(

            f"Purchased: {selected_item['purchased']} | "

            f"Returned: {selected_item['returned']} | "

            f"Remaining: {selected_item['remaining']}"

        )

        quantity = st.number_input(

            "Quantity",

            min_value=1,

            max_value=int(
                selected_item["remaining"]
            ),

            value=1,

            step=1

        )

        reason = st.text_input(
            "Reason"
        )

        if st.button(

            "Add Item",

            type="primary",

            use_container_width=True

        ):

            response = post(

                "/purchase-return-items/",

                {

                    "return_id":
                        return_id,

                    "purchase_item_id":
                        selected_item[
                            "purchase_item_id"
                        ],

                    "quantity":
                        quantity,

                    "reason":
                        reason

                },

                token=token

            )

            if response.status_code == 201:

                st.success(
                    "Item added successfully."
                )

                st.rerun()

            else:

                try:

                    error = response.json()[
                        "error"
                    ]

                except Exception:

                    error = response.text

                st.error(
                    error
                )
# ==================================================
# RETURN ITEMS
# ==================================================
st.divider()

st.subheader(
    "Returned Items"
)

if not return_items:

    st.info(
        "No items added."
    )

else:

    total = 0

    for item in return_items:

        total += item["subtotal"]

        purchased = 0
        sold = 0

        for purchase_item in purchase_items:

            if (
                purchase_item["purchase_item_id"]
                ==
                item["purchase_item_id"]
            ):

                purchased = purchase_item["quantity"]

                sold = purchase_item.get(
                    "sold",
                    0
                )

                break

        completed_returned = 0

        for completed in completed_return_items:

            if (
                completed["purchase_item_id"]
                ==
                item["purchase_item_id"]
            ):

                completed_returned += (
                    completed["quantity"]
                )

        if is_completed:

            returned = completed_returned

        else:

            returned = (
                completed_returned
                +
                item["quantity"]
            )

        remaining = (
            purchased
            -
            sold
            -
            returned
        )

        col1, col2, col3, col4, col5, col6 = (
            st.columns(
                [3, 1, 1, 1, 2, 1]
            )
        )

        with col1:

            st.write(
                item["medicine_name"]
            )

        with col2:

            st.write(
                purchased
            )

        with col3:

            st.write(
                returned
            )

        with col4:

            st.write(
                remaining
            )

        with col5:

            st.write(
                f"{item['subtotal']:.2f} JOD"
            )

        with col6:

            if not is_completed:

                if st.button(
                    "🗑️",
                    key=f"delete_{item['return_item_id']}"
                ):

                    response = delete(
                        f"/purchase-return-items/{item['return_item_id']}",
                        token=token
                    )

                    if response.status_code == 200:

                        st.success(
                            "Item deleted."
                        )

                        st.rerun()

                    else:

                        try:

                            error = response.json()[
                                "error"
                            ]

                        except Exception:

                            error = response.text

                        st.error(
                            error
                        )

    st.divider()

    st.metric(

        "Total Return Amount",

        f"{total:.2f} JOD"

    )
# ==================================================
# ACTIONS
# ==================================================
st.divider()

col1, col2, col3 = st.columns(3)

# ==========================================
# COMPLETE
# ==========================================
with col1:

    if not is_completed:

        if st.button(
            "✅ Complete Return",
            type="primary",
            use_container_width=True
        ):

            response = post(
                f"/purchase-returns/{return_id}/complete",
                {},
                token=token
            )

            if response.status_code == 200:

                st.success(
                    "Purchase Return completed successfully."
                )

                st.rerun()

            else:

                try:

                    error = response.json()[
                        "error"
                    ]

                except Exception:

                    error = response.text

                st.error(
                    error
                )

    else:

        st.success(
            "Purchase Return Completed"
        )


# ==========================================
# DELETE
# ==========================================
with col2:

    if not is_completed:

        if st.button(
            "🗑️ Delete Draft",
            use_container_width=True
        ):

            response = delete(
                f"/purchase-returns/{return_id}",
                token=token
            )

            if response.status_code == 200:

                st.success(
                    "Purchase Return deleted."
                )

                st.session_state.selected_purchase_return = None

                st.switch_page(
                    "pages/purchase_returns.py"
                )

            else:

                try:

                    error = response.json()[
                        "error"
                    ]

                except Exception:

                    error = response.text

                st.error(
                    error
                )

    else:

        st.info(
            "Completed returns cannot be deleted."
        )


# ==========================================
# BACK
# ==========================================
with col3:

    if st.button(
        "⬅ Back",
        use_container_width=True
    ):

        st.session_state.selected_purchase_return = None

        st.switch_page(
            "pages/purchase_returns.py"
        )