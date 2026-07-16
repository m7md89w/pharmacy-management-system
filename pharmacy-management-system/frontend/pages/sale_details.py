import streamlit as st

from services.api_client import (
    get,
    post,
    put,
    delete
)

st.set_page_config(
    page_title="Sale Details",
    page_icon="💰",
    layout="wide"
)

st.title("💰 Sale Details")

# ==================================================
# AUTH
# ==================================================
if "token" not in st.session_state:
    st.warning("Please login first.")
    st.stop()

if (
    "selected_invoice" not in st.session_state
    or st.session_state.selected_invoice is None
):
    st.error("No invoice selected.")
    st.stop()

invoice_id = st.session_state.selected_invoice

# ==================================================
# LOAD INVOICE
# ==================================================
response = get(
    f"/sales-invoices/{invoice_id}",
    st.session_state.token
)

if response.status_code != 200:
    st.error("Invoice not found.")
    st.stop()

invoice = response.json()

# ==================================================
# LOAD CUSTOMERS
# ==================================================
response = get(
    "/customers/",
    st.session_state.token
)

customer_map = {}

if response.status_code == 200:

    customers = response.json()

    customer_map = {
        c["customer_id"]: c["full_name"]
        for c in customers
    }

# ==================================================
# LOAD MEDICINES
# ==================================================
response = get(
    "/medicines/",
    st.session_state.token
)

if response.status_code != 200:
    st.error("Failed to load medicines.")
    st.stop()

medicines = response.json()

medicine_map = {
    medicine["id"]: medicine["commercial_name"]
    for medicine in medicines
}

medicine_options = {
    medicine["commercial_name"]: medicine["id"]
    for medicine in medicines
}

# ==================================================
# LOAD SALE ITEMS
# ==================================================
response = get(
    f"/sale-items/invoice/{invoice_id}",
    st.session_state.token
)

if response.status_code != 200:

    st.error(
        "Failed to load sale items."
    )

    st.stop()

items = response.json()


# ==================================================
# LOAD RETURNS
# ==================================================
response = get(
    f"/sales-returns/invoice/{invoice_id}",
    st.session_state.token
)

sales_returns = []

if response.status_code == 200:
    sales_returns = response.json()


# ==================================================
# LOAD RETURN ITEMS
# ==================================================
response = get(
    f"/sales-return-items/invoice/{invoice_id}",
    st.session_state.token
)

returned_items = []

if response.status_code == 200:
    returned_items = response.json()


# ==================================================
# CALCULATE RETURNED QTY
# ==================================================
returned_map = {}

for item in returned_items:

    returned_map[item["sale_item_id"]] = (

        returned_map.get(
            item["sale_item_id"],
            0
        )

        + item["quantity"]

    )


# ==================================================
# HEADER
# ==================================================
col1, col2 = st.columns(2)

with col1:

    st.subheader(
        f"Invoice #{invoice['invoice_number']}"
    )

    customer_name = customer_map.get(
        invoice["customer_id"],
        "Walk-in Customer"
    )

    st.write(
        f"Customer: {customer_name}"
    )

    st.write(
        f"Status: {invoice['status']}"
    )

with col2:

    st.write(
        f"Total Amount: {invoice['total_amount']} JOD"
    )

    st.write(
        f"Payment Method: {invoice['payment_method']}"
    )

    if invoice.get("sale_date"):

        st.write(
            f"Date: {invoice['sale_date']}"
        )


# ==================================================
# BACK
# ==================================================
if st.button(
    "⬅️ Back to Sales"
):

    st.session_state.selected_invoice = None

    st.switch_page(
        "pages/sales_invoices.py"
    )


# ==================================================
# COMPLETE SALE
# ==================================================
if invoice["status"] == "DRAFT":

    st.divider()

    if st.button(
        "✅ Complete Sale",
        type="primary",
        use_container_width=True
    ):

        if len(items) == 0:

            st.error(
                "Cannot complete an empty invoice."
            )

        else:

            response = post(
                f"/sales-invoices/{invoice_id}/complete",
                {},
                st.session_state.token
            )

            if response.status_code == 200:

                st.success(
                    "Sale completed successfully."
                )

                st.rerun()

            else:

                try:
                    error = response.json()["error"]
                except:
                    error = response.text

                st.error(error)


# ==================================================
# ADD ITEM
# ==================================================
if invoice["status"] == "DRAFT":

    st.divider()

    st.subheader(
        "➕ Add Sale Item"
    )

    medicine_name = st.selectbox(
        "Medicine",
        list(medicine_options.keys())
    )

    selected_medicine_id = medicine_options[
        medicine_name
    ]

    # ==========================================
    # LOAD AVAILABLE BATCHES
    # ==========================================
    response = get(
        f"/batches/medicine/{selected_medicine_id}",
        st.session_state.token
    )

    available_batches = []

    if response.status_code == 200:

        available_batches = [

            batch

            for batch in response.json()

            if batch["quantity"] > 0

        ]

    total_stock = sum(
        batch["quantity"]
        for batch in available_batches
    )

    if total_stock == 0:

        st.warning(
            "No stock available for this medicine."
        )

    else:

        st.success(
            f"Available Stock : {total_stock}"
        )

        with st.expander(
            "Available Batches"
        ):

            for batch in available_batches:

                st.write(
                    f"Batch : {batch['batch_number']}"
                )

                st.caption(
                    f"Qty : {batch['quantity']} | "
                    f"Expiry : {batch['expiry_date']} | "
                    f"Price : {batch['selling_price']}"
                )

                st.divider()

        quantity = st.number_input(
            "Quantity",
            min_value=1,
            max_value=total_stock,
            value=1,
            step=1
        )

        if st.button(
            "➕ Add Item",
            type="primary"
        ):

            response = post(
                "/sale-items/",
                {
                    "invoice_id": invoice_id,
                    "medicine_id": selected_medicine_id,
                    "quantity": int(quantity)
                },
                st.session_state.token
            )

            if response.status_code == 201:

                st.success(
                    "Sale item added successfully."
                )

                st.rerun()

            else:

                try:
                    st.error(
                        response.json()["error"]
                    )
                except:

                    st.error(
                        response.text
                    )


# ==================================================
# SALE ITEMS
# ==================================================
st.divider()

st.subheader(
    f"Sale Items ({len(items)})"
)

if len(items) == 0:

    st.info(
        "No sale items."
    )

else:

    for item in items:

        returned_qty = returned_map.get(
            item["sale_item_id"],
            0
        )

        remaining_qty = (
            item["quantity"]
            - returned_qty
        )

        col1, col2, col3, col4, col5, col6 = st.columns(
            [3, 2, 2, 2, 2, 1]
        )

        # ======================================
        # MEDICINE
        # ======================================
        with col1:

            st.write(

                medicine_map.get(
                    item["medicine_id"],
                    "Unknown"
                )

            )

            st.caption(
                f"Batch ID : {item['batch_id']}"
            )

        # ======================================
        # QUANTITY
        # ======================================
        with col2:

            st.write(
                f"Sold : {item['quantity']}"
            )

            if returned_qty > 0:

                st.caption(
                    f"Returned : {returned_qty}"
                )

                st.caption(
                    f"Remaining : {remaining_qty}"
                )

        # ======================================
        # UNIT PRICE
        # ======================================
        with col3:

            st.write(
                f"{item['unit_price']} JOD"
            )

        # ======================================
        # SUBTOTAL
        # ======================================
        with col4:

            st.write(
                f"{item['subtotal']} JOD"
            )

        # ======================================
        # STATUS
        # ======================================
        with col5:

            if remaining_qty == 0:

                st.success(
                    "Returned"
                )

            elif returned_qty > 0:

                st.warning(
                    "Partially Returned"
                )

            else:

                st.info(
                    "Sold"
                )

        # ======================================
        # DELETE
        # ======================================
        with col6:

            if invoice["status"] == "DRAFT":

                if st.button(
                    "🗑️",
                    key=f"delete_{item['sale_item_id']}"
                ):

                    response = delete(
                        f"/sale-items/{item['sale_item_id']}",
                        st.session_state.token
                    )

                    if response.status_code == 200:

                        st.success(
                            "Item deleted."
                        )

                        st.rerun()

                    else:

                        try:

                            st.error(
                                response.json()["error"]
                            )

                        except:

                            st.error(
                                response.text
                            )

        st.divider()



# ==================================================
# SALES RETURNS
# ==================================================
st.divider()

st.subheader("↩️ Sales Returns")

if invoice["status"] == "COMPLETED":

    completed_items = [

        item

        for item in items

        if item["quantity"]
        >
        returned_map.get(
            item["sale_item_id"],
            0
        )

    ]

    if len(completed_items) == 0:

        st.success(
            "All items have already been returned."
        )

    else:

        sale_item = st.selectbox(

            "Sale Item",

            completed_items,

            format_func=lambda x:
            f"{medicine_map.get(x['medicine_id'],'Unknown')} "
            f"(Qty {x['quantity'] - returned_map.get(x['sale_item_id'],0)})"

        )

        max_qty = (

            sale_item["quantity"]

            -

            returned_map.get(
                sale_item["sale_item_id"],
                0
            )

        )

        return_qty = st.number_input(

            "Return Quantity",

            min_value=1,

            max_value=max_qty,

            value=1

        )

        reason = st.text_input(
            "Reason"
        )

        if st.button(
            "↩️ Return Item",
            type="primary"
        ):

            response = post(

                "/sales-return-items/",

                {

                    "sale_item_id":
                        sale_item["sale_item_id"],

                    "quantity":
                        int(return_qty),

                    "reason":
                        reason

                },

                st.session_state.token

            )

            if response.status_code == 201:

                st.success(
                    "Return completed successfully."
                )

                st.rerun()

            else:

                try:

                    st.error(
                        response.json()["error"]
                    )

                except:

                    st.error(
                        response.text
                    )


# ==================================================
# RETURNS HISTORY
# ==================================================
st.divider()

st.subheader("📋 Returns History")

if len(sales_returns) == 0:

    st.info(
        "No returns found."
    )

else:

    for sale_return in sales_returns:

        with st.expander(

            f"Return #{sale_return['return_number']}"

        ):

            st.write(
                f"Status : {sale_return['status']}"
            )

            st.write(
                f"Total : {sale_return['total_amount']} JOD"
            )

            if sale_return.get(
                "return_date"
            ):

                st.write(
                    f"Date : {sale_return['return_date']}"
                )

            response = get(
                f"/sales-return-items/return/{sale_return['return_id']}",
                st.session_state.token
            )

            if response.status_code == 200:

                return_items = response.json()

                for item in return_items:

                    medicine_name = medicine_map.get(
                        item["medicine_id"],
                        "Unknown"
                    )

                    st.markdown(
                        f"""
**{medicine_name}**

- Quantity : {item['quantity']}
- Unit Price : {item['unit_price']} JOD
- Subtotal : {item['subtotal']} JOD
- Reason : {item.get('reason','-')}
"""
                    )

                    st.divider()


# ==================================================
# INVOICE SUMMARY
# ==================================================
st.divider()

st.subheader("🧾 Invoice Summary")

total_items = sum(
    item["quantity"]
    for item in items
)

returned_total = sum(
    returned_map.values()
)

active_items = total_items - returned_total

col1, col2, col3 = st.columns(3)

with col1:

    st.metric(
        "Items Sold",
        total_items
    )

with col2:

    st.metric(
        "Items Returned",
        returned_total
    )

with col3:

    st.metric(
        "Active Items",
        active_items
    )

st.divider()

col1, col2 = st.columns(2)

with col1:

    st.metric(
        "Invoice Total",
        f"{invoice['total_amount']} JOD"
    )

with col2:

    st.metric(
        "Status",
        invoice["status"]
    )


# ==================================================
# REFRESH
# ==================================================
if st.button(
    "🔄 Refresh",
    use_container_width=True
):

    st.rerun()


# ==================================================
# DELETE INVOICE
# ==================================================
if invoice["status"] == "DRAFT":

    if st.button(
        "🗑️ Delete Invoice",
        use_container_width=True
    ):

        response = delete(
            f"/sales-invoices/{invoice_id}",
            st.session_state.token
        )

        if response.status_code == 200:

            st.success(
                "Invoice deleted successfully."
            )

            st.session_state.selected_invoice = None

            st.switch_page(
                "pages/sales_invoices.py"
            )

        else:

            try:
                st.error(
                    response.json()["error"]
                )

            except:

                st.error(
                    response.text
                )


# ==================================================
# DEBUG (اختياري)
# ==================================================
with st.expander("🔍 Debug Information"):

    st.write("Invoice")

    st.json(invoice)

    st.write("Sale Items")

    st.json(items)

    st.write("Returned Quantities")

    st.json(returned_map)


# ==================================================
# FOOTER
# ==================================================
st.divider()

st.caption(
    "Pharmacy ERP • Sales Module"
)