import streamlit as st

from services.api_client import (
    get,
    post,
    put,
    delete
)

st.title("💊 Medicines")

if "token" not in st.session_state:
    st.warning("Please login first.")
    st.stop()

if "restore_barcode" not in st.session_state:
    st.session_state.restore_barcode = None

if "edit_medicine" not in st.session_state:
    st.session_state.edit_medicine = None


# ==================================================
# CREATE MEDICINE
# ==================================================
with st.expander("➕ Add New Medicine"):

    col1, col2 = st.columns(2)

    with col1:
        scientific_name = st.text_input(
            "Scientific Name"
        )

        commercial_name = st.text_input(
            "Commercial Name"
        )

        barcode = st.text_input(
            "Barcode"
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
                "OTHER"
            ]
        )

        price = st.number_input(
            "Selling Price",
            min_value=0.0,
            step=1.0
        )

        requires_prescription = st.checkbox(
            "Requires Prescription"
        )

    if st.button(
        "Create Medicine",
        type="primary"
    ):

        data = {
            "scientific_name":
            scientific_name.strip(),

            "commercial_name":
            commercial_name.strip(),

            "barcode":
            barcode.strip(),

            "dosage_form":
            dosage_form,

            "selling_price":
            float(price),

            "requires_prescription":
            requires_prescription,

            "category_id": 1,
            "manufacturer_id": 1
        }

        response = post(
            "/medicines/",
            data,
            st.session_state.token
        )

        if response.status_code == 201:

            st.success(
                "✅ Medicine created successfully."
            )

            st.rerun()

        else:

            try:
                error = response.json()["error"]
            except:
                error = response.text

            if error == "Medicine exists but is inactive.":

                st.session_state.restore_barcode = (
                    barcode
                )

                st.warning(
                    "⚠️ This medicine already exists but is inactive."
                )

            else:
                st.error(error)


# ==================================================
# RESTORE MEDICINE
# ==================================================
if st.session_state.restore_barcode:

    st.info(
        f"Restore medicine with barcode: "
        f"{st.session_state.restore_barcode}"
    )

    if st.button(
        "♻️ Restore Medicine"
    ):

        response = put(
            f"/medicines/restore/{st.session_state.restore_barcode}",
            {},
            st.session_state.token
        )

        if response.status_code == 200:

            st.success(
                "✅ Medicine restored successfully."
            )

            st.session_state.restore_barcode = None
            st.rerun()

        else:

            try:
                error = response.json()["error"]
            except:
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
        value=medicine["scientific_name"],
        key="edit_scientific"
    )

    commercial_name = st.text_input(
        "Commercial Name",
        value=medicine["commercial_name"],
        key="edit_commercial"
    )

    barcode = st.text_input(
        "Barcode",
        value=medicine["barcode"],
        key="edit_barcode"
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
            "OTHER"
        ],
        key="edit_dosage"
    )

    selling_price = st.number_input(
        "Selling Price",
        value=float(medicine["selling_price"]),
        min_value=0.0,
        key="edit_price"
    )

    col1, col2 = st.columns(2)

    with col1:
        if st.button(
            "💾 Save Changes"
        ):

            data = {
                "scientific_name":
                scientific_name,

                "commercial_name":
                commercial_name,

                "barcode":
                barcode,

                "dosage_form":
                dosage_form,

                "selling_price":
                selling_price
            }

            response = put(
                f"/medicines/{medicine['id']}",
                data,
                st.session_state.token
            )

            if response.status_code == 200:

                st.success(
                    "Medicine updated successfully."
                )

                st.session_state.edit_medicine = None
                st.rerun()

            else:

                try:
                    error = response.json()["error"]
                except:
                    error = response.text

                st.error(error)

    with col2:
        if st.button(
            "❌ Cancel"
        ):
            st.session_state.edit_medicine = None
            st.rerun()


# ==================================================
# SEARCH
# ==================================================
st.divider()

search = st.text_input(
    "🔍 Search by Name, Scientific Name, or Barcode"
)

if st.button("🔄 Refresh"):
    st.rerun()


# ==================================================
# LOAD MEDICINES
# ==================================================
response = get(
    "/medicines/",
    st.session_state.token
)

if response.status_code == 200:

    medicines = response.json()

    if search:

        query = search.lower()

        medicines = [
            medicine
            for medicine in medicines
            if (
                query in str(
                    medicine["commercial_name"]
                ).lower()
                or
                query in str(
                    medicine["scientific_name"]
                ).lower()
                or
                query in str(
                    medicine["barcode"]
                ).lower()
            )
        ]

    st.subheader(
        f"Medicines ({len(medicines)})"
    )

    if medicines:

        for medicine in medicines:

            col1, col2, col3, col4, col5 = st.columns(
                [5, 2, 2, 1, 1]
            )

            with col1:
                st.write(
                    f"💊 **{medicine['commercial_name']}**"
                )
                st.caption(
                    medicine["scientific_name"]
                )

            with col2:
                st.write(
                    f"Barcode: {medicine['barcode']}"
                )

            with col3:
                st.write(
                    f"{medicine['selling_price']} JOD"
                )

            with col4:
                if st.button(
                    "✏️",
                    key=f"edit_{medicine['id']}"
                ):
                    st.session_state.edit_medicine = medicine
                    st.rerun()

            with col5:
                if st.button(
                    "🗑️",
                    key=f"delete_{medicine['id']}"
                ):

                    response = delete(
                        f"/medicines/{medicine['id']}",
                        st.session_state.token
                    )

                    if response.status_code == 200:

                        st.success(
                            "Medicine deleted successfully."
                        )

                        st.rerun()

                    else:

                        try:
                            error = response.json()["error"]
                        except:
                            error = response.text

                        st.error(error)

            st.divider()

    else:
        st.info(
            "No medicines found."
        )

else:
    st.error(
        "Failed to load medicines."
    )