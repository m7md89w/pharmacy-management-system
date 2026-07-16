
import streamlit as st
from services.api_client import (
    get,
    post,
    put,
    delete
)

st.title("🏢 Suppliers")

if "token" not in st.session_state:
    st.warning("Please login first.")
    st.stop()

if "edit_supplier" not in st.session_state:
    st.session_state.edit_supplier = None


# ==================================================
# CREATE SUPPLIER
# ==================================================
with st.expander("➕ Add New Supplier"):

    col1, col2 = st.columns(2)

    with col1:
        name = st.text_input("Supplier Name")
        phone = st.text_input("Phone")

    with col2:
        email = st.text_input("Email")
        address = st.text_area("Address")

    if st.button(
        "Create Supplier",
        type="primary"
    ):

        data = {
            "name": name.strip(),
            "phone": phone.strip(),
            "email": email.strip(),
            "address": address.strip()
        }

        response = post(
            "/suppliers/",
            data,
            st.session_state.token
        )

        if response.status_code == 201:
            st.success(
                "✅ Supplier created successfully."
            )
            st.rerun()
        else:
            try:
                error = response.json()["error"]
            except:
                error = response.text

            st.error(error)


# ==================================================
# EDIT SUPPLIER
# ==================================================
if st.session_state.edit_supplier:

    supplier = st.session_state.edit_supplier

    st.divider()
    st.subheader("✏️ Edit Supplier")

    name = st.text_input(
        "Supplier Name",
        value=supplier.get("name", ""),
        key="edit_name"
    )

    phone = st.text_input(
        "Phone",
        value=supplier.get("phone", ""),
        key="edit_phone"
    )

    email = st.text_input(
        "Email",
        value=supplier.get("email", ""),
        key="edit_email"
    )

    address = st.text_area(
        "Address",
        value=supplier.get("address", ""),
        key="edit_address"
    )

    col1, col2 = st.columns(2)

    with col1:
        if st.button("💾 Save Changes"):

            data = {
                "name": name.strip(),
                "phone": phone.strip(),
                "email": email.strip(),
                "address": address.strip()
            }

            response = put(
                f"/suppliers/{supplier['id']}",
                data,
                st.session_state.token
            )

            if response.status_code == 200:
                st.success(
                    "Supplier updated successfully."
                )
                st.session_state.edit_supplier = None
                st.rerun()
            else:
                st.error(response.text)

    with col2:
        if st.button("❌ Cancel"):
            st.session_state.edit_supplier = None
            st.rerun()


# ==================================================
# SEARCH
# ==================================================
st.divider()

search = st.text_input(
    "🔍 Search Supplier"
)


# ==================================================
# LOAD SUPPLIERS
# ==================================================
response = get(
    "/suppliers/",
    st.session_state.token
)

if response.status_code == 200:

    suppliers = response.json()

    if search:
        query = search.lower()

        suppliers = [
            s for s in suppliers
            if (
                query in str(
                    s.get("name", "")
                ).lower()
                or
                query in str(
                    s.get("phone", "")
                ).lower()
                or
                query in str(
                    s.get("email", "")
                ).lower()
            )
        ]

    st.subheader(
        f"Suppliers ({len(suppliers)})"
    )

    if suppliers:

        for supplier in suppliers:

            col1, col2, col3, col4 = st.columns(
                [5, 3, 1, 1]
            )

            with col1:
                st.write(
                    f"🏢 **{supplier['name']}**"
                )
                st.caption(
                    supplier.get(
                        "email",
                        "No Email"
                    )
                )

            with col2:
                st.write(
                    supplier.get(
                        "phone",
                        "-"
                    )
                )

            with col3:
                if st.button(
                    "✏️",
                    key=f"edit_{supplier['id']}"
                ):

                    response = get(
                        f"/suppliers/{supplier['id']}",
                        st.session_state.token
                    )

                    if response.status_code == 200:
                        st.session_state.edit_supplier = (
                            response.json()
                        )
                        st.rerun()
                    else:
                        st.error(
                            "Failed to load supplier."
                        )

            with col4:
                if st.button(
                    "🗑️",
                    key=f"delete_{supplier['id']}"
                ):

                    response = delete(
                        f"/suppliers/{supplier['id']}",
                        st.session_state.token
                    )

                    if response.status_code == 200:
                        st.success(
                            "Supplier deleted."
                        )
                        st.rerun()
                    else:
                        st.error(
                            response.text
                        )

            st.divider()

    else:
        st.info(
            "No suppliers found."
        )

else:
    st.error(
        "Failed to load suppliers."
    )

