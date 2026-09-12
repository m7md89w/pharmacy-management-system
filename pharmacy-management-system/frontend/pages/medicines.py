from components.sidebar import render_sidebar
import pandas as pd
from services.api_client import delete, get, post, put
import streamlit as st

# ==================================================
# PAGE CONFIGURATION
# ==================================================
st.set_page_config(
    page_title="Medicines",
    page_icon="💊",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
        [data-testid="stSidebarNav"] {
            display: none !important;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

render_sidebar()

st.title("💊 Medicines Management")

# ==================================================
# AUTHENTICATION CHECK
# ==================================================
token = st.session_state.get("token") or st.session_state.get("access_token")

if not token:
  st.warning("Please login first.")
  if st.button("Go to Login / Main Page"):
    st.switch_page("app.py")
  st.stop()

if "restore_barcode" not in st.session_state:
  st.session_state.restore_barcode = None

if "edit_medicine" not in st.session_state:
  st.session_state.edit_medicine = None


# ==================================================
# FETCH CATEGORIES & MANUFACTURERS FOR DROPDOWNS
# ==================================================
categories_res = get("/categories/", token)
categories_map = {}
category_options = []

if categories_res.status_code == 200:
  categories_data = categories_res.json()
  categories_map = {
      cat["category_name"]: cat["category_id"] for cat in categories_data
  }
  category_options = list(categories_map.keys())

manufacturers_res = get("/manufacturers/", token)
manufacturers_map = {}
manufacturer_options = []

if manufacturers_res.status_code == 200:
  manufacturers_data = manufacturers_res.json()
  manufacturers_map = {
      man["name"]: man["manufacturer_id"] for man in manufacturers_data
  }
  manufacturer_options = list(manufacturers_map.keys())


# ==================================================
# CREATE MEDICINE
# ==================================================
with st.expander("➕ Add New Medicine"):
  col1, col2 = st.columns(2)

  with col1:
    scientific_name = st.text_input("Scientific Name", key="create_sci")
    commercial_name = st.text_input("Commercial Name", key="create_com")
    strength = st.text_input(
        "Strength / Dosage (e.g., 50mg, 10)", key="create_strength"
    )
    barcode = st.text_input("Barcode", key="create_bar")
    location = st.text_input(
        "Storage Location (e.g., Shelf A-1)", key="create_loc"
    )

  with col2:
    dosage_form = st.selectbox(
        "Dosage Form",
        [
            "TABLET",
            "CAPSULE",
            "SYRUP",
            "INJECTION",
            "OINTMENT",
            "DROPS",
            "CREAM",
            "POWDER",
            "OTHER",
        ],
        key="create_dosage",
    )

    selected_category_name = st.selectbox(
        "Category",
        options=category_options
        if category_options
        else ["No Categories Available"],
        key="create_cat",
    )

    selected_manufacturer_name = st.selectbox(
        "Manufacturer",
        options=manufacturer_options
        if manufacturer_options
        else ["No Manufacturers Available"],
        key="create_man",
    )

    price = st.number_input(
        "Selling Price", min_value=0.0, step=1.0, key="create_price"
    )
    min_stock_level = st.number_input(
        "Min Stock Level", min_value=0, value=5, step=1, key="create_min_stock"
    )
    requires_prescription = st.checkbox(
        "Requires Prescription", key="create_prescription"
    )

  if st.button("Create Medicine", type="primary"):
    if not category_options:
      st.error(
          "❌ Please add at least one category first in the Categories page."
      )
    elif not manufacturer_options:
      st.error(
          "❌ Please add at least one manufacturer first in the Manufacturers"
          " page."
      )
    else:
      category_id = categories_map.get(selected_category_name)
      manufacturer_id = manufacturers_map.get(selected_manufacturer_name)

      data = {
          "scientific_name": scientific_name.strip(),
          "commercial_name": commercial_name.strip(),
          "strength": strength.strip() if strength else "",
          "barcode": barcode.strip(),
          "dosage_form": dosage_form,
          "selling_price": float(price),
          "requires_prescription": requires_prescription,
          "location": location.strip() if location else "",
          "min_stock_level": int(min_stock_level),
          "category_id": int(category_id) if category_id else None,
          "manufacturer_id": int(manufacturer_id) if manufacturer_id else None,
      }

      response = post("/medicines/", data, token)

      if response.status_code == 201:
        st.success(
            "✅ Medicine and its inventory location created successfully."
        )
        st.rerun()
      else:
        try:
          error = response.json()["error"]
        except Exception:
          error = response.text

        if error == "Medicine exists but is inactive.":
          st.session_state.restore_barcode = barcode
          st.warning("⚠️ This medicine already exists but is inactive.")
        else:
          st.error(error)


# ==================================================
# RESTORE MEDICINE
# ==================================================
if st.session_state.restore_barcode:
  st.info(f"Restore medicine with barcode: {st.session_state.restore_barcode}")

  if st.button("♻️ Restore Medicine"):
    response = put(
        f"/medicines/restore/{st.session_state.restore_barcode}", {}, token
    )

    if response.status_code == 200:
      st.success("✅ Medicine restored successfully.")
      st.session_state.restore_barcode = None
      st.rerun()
    else:
      try:
        error = response.json()["error"]
      except Exception:
        error = response.text
      st.error(error)


# ==================================================
# EDIT MEDICINE
# ==================================================
if st.session_state.edit_medicine:
  medicine = st.session_state.edit_medicine

  st.divider()
  st.subheader("✏️ Edit Medicine")

  scientific_name = st.text_input(
      "Scientific Name",
      value=medicine.get("scientific_name", ""),
      key="edit_scientific",
  )
  commercial_name = st.text_input(
      "Commercial Name",
      value=medicine.get("commercial_name", ""),
      key="edit_commercial",
  )
  strength = st.text_input(
      "Strength / Dosage",
      value=medicine.get("strength", ""),
      key="edit_strength",
  )
  barcode = st.text_input(
      "Barcode", value=medicine.get("barcode", ""), key="edit_barcode"
  )
  location = st.text_input(
      "Storage Location",
      value=medicine.get("location", ""),
      key="edit_location",
  )

  dosage_form = st.selectbox(
      "Dosage Form",
      [
          "TABLET",
          "CAPSULE",
          "SYRUP",
          "INJECTION",
          "OINTMENT",
          "DROPS",
          "CREAM",
          "POWDER",
          "OTHER",
      ],
      key="edit_dosage",
  )

  current_cat_id = medicine.get("category_id")
  current_cat_name = next(
      (name for name, cid in categories_map.items() if cid == current_cat_id),
      category_options[0] if category_options else None,
  )

  edit_selected_category = st.selectbox(
      "Category",
      options=category_options
      if category_options
      else ["No Categories Available"],
      index=category_options.index(current_cat_name)
      if current_cat_name in category_options
      else 0,
      key="edit_category_select",
  )

  current_man_id = medicine.get("manufacturer_id")
  current_man_name = next(
      (name for name, mid in manufacturers_map.items() if mid == current_man_id),
      manufacturer_options[0] if manufacturer_options else None,
  )

  edit_selected_manufacturer = st.selectbox(
      "Manufacturer",
      options=manufacturer_options
      if manufacturer_options
      else ["No Manufacturers Available"],
      index=manufacturer_options.index(current_man_name)
      if current_man_name in manufacturer_options
      else 0,
      key="edit_manufacturer_select",
  )

  selling_price = st.number_input(
      "Selling Price",
      value=float(medicine.get("selling_price", 0.0)),
      min_value=0.0,
      key="edit_price",
  )

  col1, col2 = st.columns(2)

  with col1:
    if st.button("💾 Save Changes"):
      category_id = categories_map.get(edit_selected_category)
      manufacturer_id = manufacturers_map.get(edit_selected_manufacturer)

      data = {
          "scientific_name": scientific_name,
          "commercial_name": commercial_name,
          "strength": strength,
          "barcode": barcode,
          "dosage_form": dosage_form,
          "selling_price": selling_price,
          "location": location,
          "category_id": int(category_id) if category_id else None,
          "manufacturer_id": int(manufacturer_id) if manufacturer_id else None,
      }

      response = put(f"/medicines/{medicine['id']}", data, token)

      if response.status_code == 200:
        st.success("Medicine updated successfully.")
        st.session_state.edit_medicine = None
        st.rerun()
      else:
        try:
          error = response.json()["error"]
        except Exception:
          error = response.text
        st.error(error)

  with col2:
    if st.button("❌ Cancel"):
      st.session_state.edit_medicine = None
      st.rerun()


# ==================================================
# SEARCH & LIST
# ==================================================
st.divider()
search = st.text_input("🔍 Search by Name, Scientific Name, or Barcode")

if st.button("🔄 Refresh"):
  st.rerun()

response = get("/medicines/", token)

if response.status_code == 200:
  medicines = response.json()

  if search:
    query = search.lower()
    medicines = [
        medicine
        for medicine in medicines
        if query in str(medicine["commercial_name"]).lower()
        or query in str(medicine["scientific_name"]).lower()
        or query in str(medicine["barcode"]).lower()
        or query in str(medicine.get("strength", "")).lower()
    ]

  st.subheader(f"Medicines ({len(medicines)})")

  if medicines:
    for medicine in medicines:
      col1, col2, col3, col4, col5 = st.columns([5, 2, 2, 1, 1])

      with col1:
        str_val = f" ({medicine['strength']})" if medicine.get("strength") else ""
        st.write(f"💊 **{medicine['commercial_name']}{str_val}**")
        st.caption(medicine["scientific_name"])
        if medicine.get("location"):
          st.caption(f"📍 Location: {medicine['location']}")

      with col2:
        st.write(f"Barcode: {medicine['barcode']}")

      with col3:
        st.write(f"{medicine['selling_price']} JOD")

      with col4:
        if st.button("✏️", key=f"edit_{medicine['id']}"):
          detail_res = get(f"/medicines/{medicine['id']}", token)
          if detail_res.status_code == 200:
            st.session_state.edit_medicine = detail_res.json()
          else:
            st.session_state.edit_medicine = medicine
          st.rerun()

      with col5:
        if st.button("🗑️", key=f"delete_{medicine['id']}"):
          response = delete(f"/medicines/{medicine['id']}", token)

          if response.status_code == 200:
            st.success("Medicine deleted successfully.")
            st.rerun()
          else:
            try:
              error = response.json()["error"]
            except Exception:
              error = response.text
            st.error(error)

      st.divider()

  else:
    st.info("No medicines found.")

else:
  st.error("Failed to load medicines.")