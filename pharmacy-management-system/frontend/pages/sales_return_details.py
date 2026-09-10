import streamlit as st

from services.api_client import (
    get,
    post,
    delete
)
from components.sidebar import render_sidebar

st.set_page_config(
    page_title="Sales Return Details",
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

st.title("↩️ Sales Return Details")


# ==================================================
# AUTH & SESSION CHECK
# ==================================================
token = st.session_state.get("token") or st.session_state.get("access_token")

if not token:
    st.warning("Please login first.")
    if st.button("Go to Login / Main Page"):
        st.switch_page("app.py")
    st.stop()

if (
    "selected_sales_return" not in st.session_state
    or not st.session_state.selected_sales_return
):
    st.warning("No sales return selected.")
    if st.button("⬅️ Back to Returns"):
        st.switch_page("pages/sales_return.py")
    st.stop()

return_id = st.session_state.selected_sales_return


# ==================================================
# LOAD RETURN
# ==================================================
response = get(
    f"/sales-returns/{return_id}",
    token=token
)

if response.status_code != 200:
    st.error("Failed to load sales return.")
    if st.button("⬅️ Back to Returns"):
        st.switch_page("pages/sales_return.py")
    st.stop()

sales_return = response.json()

is_completed = (
    sales_return["status"]
    == "COMPLETED"
)

is_cancelled = (
    sales_return["status"]
    == "CANCELLED"
)


# ==================================================
# LOAD INVOICE
# ==================================================
response = get(
    f"/sales-invoices/{sales_return['invoice_id']}",
    token=token
)

if response.status_code != 200:
    st.error("Failed to load invoice.")
    st.stop()

invoice = response.json()


# ==================================================
# LOAD COMPLETED RETURN ITEMS FOR THIS INVOICE
# ==================================================
response = get(
    f"/sales-return-items/invoice/{invoice['invoice_id']}",
    token=token
)

if response.status_code != 200:
    st.error("Failed to load completed return items.")
    st.stop()

completed_return_items = response.json()

# ==================================================
# LOAD RETURN ITEMS
# ==================================================
response = get(
    f"/sales-return-items/return/{return_id}",
    token=token
)

if response.status_code != 200:
    st.error("Failed to load return items.")
    st.stop()

return_items = response.json()


# ==================================================
# LOAD SALE ITEMS
# ==================================================
response = get(
    f"/sale-items/invoice/{invoice['invoice_id']}",
    token=token
)

if response.status_code != 200:
    st.error("Failed to load sale items.")
    st.stop()

sale_items = response.json()


# ==================================================
# LOAD MEDICINES
# ==================================================
response = get(
    "/medicines/",
    token=token
)

if response.status_code != 200:
    st.error("Failed to load medicines.")
    st.stop()

medicines = response.json()

medicine_map = {
    medicine["id"]: medicine
    for medicine in medicines
}


# ==================================================
# CALCULATE RETURNED QUANTITIES
# ==================================================
returned_map = {}

for item in completed_return_items:
    returned_map[
        item["sale_item_id"]
    ] = (
        returned_map.get(
            item["sale_item_id"],
            0
        )
        + item["quantity"]
    )

# أضف عناصر الطلب الحالي (Draft)
if not is_completed and not is_cancelled:
    for item in return_items:
        returned_map[
            item["sale_item_id"]
        ] = (
            returned_map.get(
                item["sale_item_id"],
                0
            )
            + item["quantity"]
        )


# ==================================================
# RETURN INFO
# ==================================================
st.info(
    f"""
Return ID: #{sales_return['return_id']}

Invoice: {invoice['invoice_number']}

Status: {sales_return['status']}

Total Return: {float(sales_return['total_amount']):.2f} JOD
"""
)


# ==================================================
# ADD RETURN ITEM
# ==================================================
st.divider()

if is_completed:
    st.success("This Sales Return has been completed.")
elif is_cancelled:
    st.warning("This Sales Return has been cancelled.")
else:
    st.subheader("➕ Add Return Item")

    available_items = []

    for item in sale_items:
        sold = item["quantity"]
        returned = returned_map.get(
            item["sale_item_id"],
            0
        )
        remaining = sold - returned

        if remaining <= 0:
            continue

        medicine = medicine_map.get(
            item["medicine_id"],
            {}
        )

        available_items.append({
            "sale_item_id": item["sale_item_id"],
            "medicine_name": medicine.get("commercial_name", "Unknown"),
            "sold": sold,
            "returned": returned,
            "remaining": remaining
        })

    if not available_items:
        st.info("Everything in this invoice has already been returned.")
    else:
        labels = [
            f"{item['medicine_name']} | Sold: {item['sold']} | Returned: {item['returned']} | Remaining: {item['remaining']}"
            for item in available_items
        ]

        selected_index = st.selectbox(
            "Sale Item",
            range(len(labels)),
            format_func=lambda i: labels[i]
        )

        selected_item = available_items[selected_index]

        quantity = st.number_input(
            "Return Quantity",
            min_value=1,
            max_value=int(selected_item["remaining"]),
            value=1,
            step=1
        )

        st.caption(f"Remaining Quantity: {selected_item['remaining']}")

        if st.button("Add Return Item", type="primary"):
            response = post(
                "/sales-return-items/",
                {
                    "return_id": return_id,
                    "sale_item_id": selected_item["sale_item_id"],
                    "quantity": quantity
                },
                token=token
            )

            if response.status_code == 201:
                st.success("Return item added successfully.")
                st.rerun()
            else:
                try:
                    error = response.json()["error"]
                except Exception:
                    error = response.text
                st.error(error)


# ==================================================
# RETURN ITEMS LIST
# ==================================================
st.divider()
st.subheader(f"Returned Items ({len(return_items)})")

if not return_items:
    st.info("No returned items yet.")
else:
    for item in return_items:
        medicine = medicine_map.get(
            item["medicine_id"],
            {}
        )

        col1, col2, col3, col4, col5, col6 = st.columns([3, 1, 1, 1, 1, 1])

        with col1:
            st.write(medicine.get("commercial_name", "Unknown Medicine"))
            st.caption(medicine.get("scientific_name", ""))

        with col2:
            st.write(f"{item['quantity']}")

        with col3:
            st.write(f"{float(item['unit_price']):.2f} JOD")

        with col4:
            st.write(f"{float(item['subtotal']):.2f} JOD")

        with col5:
            st.write(f"Batch #{item['batch_id']}")

        with col6:
            if not is_completed and not is_cancelled:
                if st.button("🗑️", key=f"delete_{item['return_item_id']}"):
                    response = delete(
                        f"/sales-return-items/{item['return_item_id']}",
                        token=token
                    )
                    if response.status_code == 200:
                        st.success("Return item deleted successfully.")
                        st.rerun()
                    else:
                        try:
                            error = response.json()["error"]
                        except Exception:
                            error = response.text
                        st.error(error)

        st.divider()


# ==================================================
# COMPLETE OR CANCEL RETURN ACTIONS
# ==================================================
if not is_completed and not is_cancelled:
    st.divider()
    if len(return_items) == 0:
        st.warning("Add at least one return item before completing the return.")
    else:
        if st.button("✅ Complete Return", type="primary", use_container_width=True):
            response = post(
                f"/sales-returns/{return_id}/complete",
                {},
                token=token
            )
            if response.status_code == 200:
                st.success("Sales Return completed successfully.")
                st.rerun()
            else:
                try:
                    error = response.json()["error"]
                except Exception:
                    error = response.text
                st.error(error)

elif is_completed:
    st.divider()
    st.success("✅ This Sales Return has already been completed.")

    # زر إلغاء المرتجع المكتمل مع عكس المخزون
    if st.button("❌ Cancel Sales Return", type="secondary", use_container_width=True):
        response = post(
            f"/sales-returns/{return_id}/cancel",
            {},
            token=token
        )
        if response.status_code == 200:
            st.success("Sales Return cancelled successfully and stock reversed.")
            st.rerun()
        else:
            try:
                error = response.json()["error"]
            except Exception:
                error = response.text
            st.error(error)

else:
    st.divider()
    st.warning("⚠️ This Sales Return is cancelled.")
    

# ==================================================
# BACK
# ==================================================
if st.button("⬅ Back to Returns", use_container_width=True):
    st.switch_page("pages/sales_return.py")