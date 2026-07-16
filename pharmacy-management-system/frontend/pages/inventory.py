import streamlit as st
import pandas as pd

from services.api_client import get

st.title("📦 Inventory")

if "token" not in st.session_state:
    st.warning("Please login first")
    st.stop()

response = get(
    "/inventory/",
    st.session_state.token
)

if response.status_code == 200:

    inventory = response.json()

    if inventory:

        df = pd.DataFrame(
            inventory
        )

        st.dataframe(
            df,
            use_container_width=True
        )

    else:
        st.info(
            "No inventory records found."
        )

else:
    st.error(
        "Failed to load inventory."
    )