import streamlit as st
import pandas as pd

def render_standard_table(df: pd.DataFrame, empty_message: str = "No records found."):
    """
    Renders a standardized, full-width interactive table.
    Ensures the index is hidden and handles empty DataFrames gracefully.
    """
    if df is None or df.empty:
        st.info(f"ℹ️ {empty_message}")
        return

    # Render the dataframe with standard configuration
    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True
    )

def render_status_badge(status: str) -> str:
    """
    Returns an emoji badge based on common system statuses.
    Useful for formatting columns before passing them to the table.
    """
    status_upper = str(status).strip().upper()
    
    if status_upper == "COMPLETED":
        return f"✅ {status_upper}"
    elif status_upper == "PENDING":
        return f"⏳ {status_upper}"
    elif status_upper == "CANCELLED":
        return f"❌ {status_upper}"
    elif status_upper == "DRAFT":
        return f"📝 {status_upper}"
    elif status_upper == "RECEIVED":
        return f"📦 {status_upper}"
    
    return status_upper

def format_currency_column(df: pd.DataFrame, column_name: str) -> pd.DataFrame:
    """
    Formats a numeric column as currency (JOD).
    Modifies the dataframe safely.
    """
    if column_name in df.columns:
        df[column_name] = pd.to_numeric(df[column_name], errors='coerce').fillna(0.0)
        df[column_name] = df[column_name].apply(lambda x: f"{x:.2f} JOD")
    return df