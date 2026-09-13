from components.sidebar import render_sidebar
from datetime import date
from services.api_client import delete, get, post, put
import streamlit as st

st.set_page_config(
    page_title="Sale Details",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded",
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

st.title("💰 Sale Details")

# ==================================================
# AUTH
# ==================================================
token = st.session_state.get("token") or st.session_state.get("access_token")

if not token:
  st.warning("Please login first.")
  if st.button("Go to Login / Main Page"):
    st.switch_page("app.py")
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
response = get(f"/sales-invoices/{invoice_id}", token=token)

if response.status_code != 200:
  st.error("Invoice not found.")
  st.stop()

invoice = response.json()

# ==================================================
# LOAD CUSTOMERS
# ==================================================
response = get("/customers/", token=token)

customers = []
customer_map = {}
customer_options = {"Walk-in Customer (None)": None}

if response.status_code == 200:
  customers = response.json()
  for c in customers:
    customer_map[c["customer_id"]] = c["full_name"]
    customer_options[f"{c['full_name']} ({c.get('phone', 'No Phone')})"] = c[
        "customer_id"
    ]

# ==================================================
# LOAD MEDICINES
# ==================================================
response = get("/medicines/", token=token)

if response.status_code != 200:
  st.error("Failed to load medicines.")
  st.stop()

medicines = response.json()

medicine_map = {}
medicine_options = {}

for medicine in medicines:
  med_id = medicine["id"]
  com_name = medicine["commercial_name"]
  strength_val = medicine.get("strength")
  display_name = (
      f"{com_name} ({strength_val})" if strength_val else com_name
  )
  medicine_map[med_id] = display_name
  medicine_options[display_name] = med_id

# ==================================================
# LOAD SALE ITEMS
# ==================================================
response = get(f"/sale-items/invoice/{invoice_id}", token=token)

if response.status_code != 200:
  st.error("Failed to load sale items.")
  st.stop()

items = response.json()

# ==================================================
# LOAD RETURNS
# ==================================================
response = get(f"/sales-returns/invoice/{invoice_id}", token=token)
sales_returns = response.json() if response.status_code == 200 else []

# ==================================================
# LOAD RETURN ITEMS
# ==================================================
response = get(f"/sales-return-items/invoice/{invoice_id}", token=token)
returned_items = response.json() if response.status_code == 200 else []

# ==================================================
# CALCULATE RETURNED QTY
# ==================================================
returned_map = {}
for item in returned_items:
  returned_map[item["sale_item_id"]] = (
      returned_map.get(item["sale_item_id"], 0) + item["quantity"]
  )

# ==================================================
# HEADER & CUSTOMER / PAYMENT METHOD SELECTION (IF DRAFT)
# ==================================================
col1, col2 = st.columns(2)

with col1:
  st.subheader(f"Invoice #{invoice['invoice_number']}")

  current_customer_id = invoice.get("customer_id")
  current_payment_method = invoice.get("payment_method", "CASH")

  if invoice["status"] == "DRAFT":
    # 1. Customer Selection (مباشرة وبدون زر حفظ)
    inv_customer_keys = list(customer_options.keys())
    current_selection_index = 0
    for idx, (name, cid) in enumerate(customer_options.items()):
      if cid == current_customer_id:
        current_selection_index = idx
        break

    selected_customer_label = st.selectbox(
        "Assign / Change Customer",
        inv_customer_keys,
        index=current_selection_index,
    )
    selected_customer_id = customer_options[selected_customer_label]

    if selected_customer_id != current_customer_id:
      update_res = put(
          f"/sales-invoices/{invoice_id}",
          {"customer_id": selected_customer_id},
          token=token,
      )
      if update_res.status_code == 200 or update_res.status_code == 201:
        st.success("Customer updated successfully.")
        st.rerun()
      else:
        try:
          err = update_res.json().get("error", update_res.text)
        except Exception:
          err = update_res.text
        st.error(err)

    # 2. Payment Method Selection (مباشرة وبدون زر حفظ)
    payment_methods = ["CASH", "CARD", "INSURANCE", "OTHER"]
    current_pay_index = (
        payment_methods.index(current_payment_method)
        if current_payment_method in payment_methods
        else 0
    )
    selected_payment_method = st.selectbox(
        "Payment Method", payment_methods, index=current_pay_index
    )

    if selected_payment_method != current_payment_method:
      update_res = put(
          f"/sales-invoices/{invoice_id}",
          {"payment_method": selected_payment_method},
          token=token,
      )
      if update_res.status_code == 200 or update_res.status_code == 201:
        st.success("Payment method updated successfully.")
        st.rerun()
      else:
        try:
          err = update_res.json().get("error", update_res.text)
        except Exception:
          err = update_res.text
        st.error(err)
  else:
    customer_name = customer_map.get(current_customer_id, "Walk-in Customer")
    st.write(f"Customer: {customer_name}")
    st.write(f"Payment Method: {current_payment_method}")

  st.write(f"Status: {invoice['status']}")

with col2:
  st.write(f"Total Amount: {invoice['total_amount']} JOD")
  if invoice.get("sale_date"):
    st.write(f"Date: {invoice['sale_date']}")

# ==================================================
# PRESCRIPTIONS INTEGRATION (IF CUSTOMER SELECTED & DRAFT)
# ==================================================
if invoice["status"] == "DRAFT" and invoice.get("customer_id"):
  st.divider()
  st.subheader("📋 Customer Prescriptions")

  pres_res = get(
      f"/prescriptions/customer/{invoice['customer_id']}", token=token
  )
  if pres_res.status_code == 200:
    prescriptions = pres_res.json()
    if not prescriptions:
      st.info("No prescriptions found for this customer.")
    else:
      for pres in prescriptions:
        with st.expander(
            f"Prescription #{pres.get('prescription_id')} | Dr."
            f" {pres.get('doctor_name', 'Unknown')} | Date:"
            f" {pres.get('issue_date', 'N/A')}"
        ):
          st.write(f"**Notes:** {pres.get('notes', 'None')}")

          items_res = get(
              f"/prescription-items/prescription/{pres.get('prescription_id')}",
              token=token,
          )
          pres_items = items_res.json() if items_res.status_code == 200 else []

          if pres_items:
            st.write("Prescription Medicines:")
            for pi in pres_items:
              med_name = medicine_map.get(
                  pi.get("medicine_id"), "Unknown Medicine"
              )
              st.caption(f"- {med_name}")

          if st.button(
              f"📥 Add Prescription #{pres.get('prescription_id')} to Invoice",
              key=f"import_pres_{pres.get('prescription_id')}",
          ):
            imported_count = 0
            failed_count = 0

            for p_item in pres_items:
              med_id = p_item.get("medicine_id")
              item_res = post(
                  "/sale-items/",
                  {
                      "invoice_id": invoice_id,
                      "medicine_id": med_id,
                      "quantity": 1,
                  },
                  token=token,
              )
              if item_res.status_code == 201 or item_res.status_code == 200:
                imported_count += 1
              else:
                failed_count += 1

            if imported_count > 0:
              st.success(
                  f"Successfully added {imported_count} prescription items to"
                  " draft invoice!"
              )
              if failed_count > 0:
                st.warning(
                    f"Could not add {failed_count} items due to lack of stock or"
                    " expiry."
                )
              st.rerun()
            else:
              st.error(
                  "Failed to add prescription items. Check available valid"
                  " inventory stock."
              )
  else:
    st.caption("Could not load customer prescriptions.")

# ==================================================
# BACK
# ==================================================
st.divider()
if st.button("⬅️ Back to Sales"):
  st.session_state.selected_invoice = None
  st.switch_page("pages/sales_invoices.py")

# ==================================================
# COMPLETE SALE
# ==================================================
if invoice["status"] == "DRAFT":
  st.divider()
  if st.button(
      "✅ Complete Sale (Deduct Stock)",
      type="primary",
      use_container_width=True,
  ):
    if len(items) == 0:
      st.error("Cannot complete an empty invoice.")
    else:
      response = post(f"/sales-invoices/{invoice_id}/complete", {}, token=token)
      if response.status_code == 200 or response.status_code == 201:
        st.success(
            "Sale completed successfully and inventory stock updated."
        )
        st.rerun()
      else:
        try:
          error = response.json()["error"]
        except Exception:
          error = response.text
        st.error(error)

# ==================================================
# ADD ITEM MANUALLY (FILTERING EXPIRED BATCHES)
# ==================================================
if invoice["status"] == "DRAFT":
  st.divider()
  st.subheader("➕ Add Sale Item Manually")

  medicine_name = st.selectbox(
      "Medicine", list(medicine_options.keys()), key="manual_med_select"
  )
  selected_medicine_id = medicine_options[medicine_name]

  # جلب الدفعات وتصفية المنتهية منها
  response = get(f"/batches/medicine/{selected_medicine_id}", token=token)
  valid_batches = []
  today = date.today()

  if response.status_code == 200:
    for batch in response.json():
      if batch["quantity"] > 0 and batch.get("expiry_date"):
        try:
          exp_date = date.fromisoformat(batch["expiry_date"])
          if exp_date >= today:
            valid_batches.append(batch)
        except Exception:
          continue

  total_stock = sum(batch["quantity"] for batch in valid_batches)

  if total_stock == 0:
    st.warning(
        "No valid (non-expired) stock available for this medicine."
    )
  else:
    st.success(f"Available Valid Stock : {total_stock}")

    with st.expander("📦 Valid Batches & Expiry Dates"):
      for b in valid_batches:
        st.write(
            f"- **Batch Number:** {b.get('batch_number')} | **Valid Qty:**"
            f" {b.get('quantity')} | **Expiry Date:**"
            f" {b.get('expiry_date')} | **Price:** {b.get('selling_price')} JOD"
        )

    quantity = st.number_input(
        "Quantity", min_value=1, max_value=total_stock, value=1, step=1
    )

    if st.button("➕ Add Item to Invoice", type="primary"):
      response = post(
          "/sale-items/",
          {
              "invoice_id": invoice_id,
              "medicine_id": selected_medicine_id,
              "quantity": int(quantity),
          },
          token=token,
      )

      if response.status_code == 201 or response.status_code == 200:
        st.success("Sale item added to invoice successfully.")
        st.rerun()
      else:
        try:
          st.error(response.json()["error"])
        except Exception:
          st.error(response.text)

# ==================================================
# SALE ITEMS LIST
# ==================================================
st.divider()
st.subheader(f"Invoice Items ({len(items)})")

if len(items) == 0:
  st.info("No items in this invoice yet.")
else:
  for item in items:
    returned_qty = returned_map.get(item["sale_item_id"], 0)
    remaining_qty = item["quantity"] - returned_qty

    col1, col2, col3, col4, col5, col6 = st.columns([3, 2, 2, 2, 2, 1])

    with col1:
      st.write(
          medicine_map.get(item["medicine_id"], "Unknown")
      )
      st.caption(f"Batch ID : {item['batch_id']}")

    with col2:
      st.write(f"Qty : {item['quantity']}")
      if returned_qty > 0:
        st.caption(f"Returned : {returned_qty}")
        st.caption(f"Remaining : {remaining_qty}")

    with col3:
      st.write(f"{item['unit_price']} JOD")

    with col4:
      st.write(f"{item['subtotal']} JOD")

    with col5:
      if remaining_qty == 0:
        st.success("Returned")
      elif returned_qty > 0:
        st.warning("Partially Returned")
      else:
        st.info("In Draft / Sold")

    with col6:
      if invoice["status"] == "DRAFT":
        if st.button("🗑️", key=f"delete_{item['sale_item_id']}"):
          response = delete(f"/sale-items/{item['sale_item_id']}", token=token)
          if response.status_code == 200 or response.status_code == 201:
            st.success("Item removed from invoice.")
            st.rerun()
          else:
            try:
              st.error(response.json()["error"])
            except Exception:
              st.error(response.text)
    st.divider()