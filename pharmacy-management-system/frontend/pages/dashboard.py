import streamlit as st
import pandas as pd
from services.api_client import get

st.title("📊 Pharmacy Dashboard")

if "token" not in st.session_state:
    st.warning("Please login first.")
    st.stop()


col1, col2, col3 = st.columns(3)

# Medicines
medicines = get(
    "/medicines/",
    st.session_state.token
).json()

# Suppliers
suppliers = get(
    "/suppliers/",
    st.session_state.token
).json()

# Inventory
inventory = get(
    "/inventory/",
    st.session_state.token
).json()


with col1:
    st.metric(
        "💊 Medicines",
        len(medicines)
    )

with col2:
    st.metric(
        "🏢 Suppliers",
        len(suppliers)
    )

with col3:
    st.metric(
        "📦 Inventory Records",
        len(inventory)
    )


st.divider()

st.subheader("📦 Inventory")

if inventory:
    df = pd.DataFrame(
        inventory
    )

    st.dataframe(
        df,
        use_container_width=True
    )