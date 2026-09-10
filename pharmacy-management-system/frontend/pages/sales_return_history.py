import streamlit as st
from services.api_client import get, put
from components.sidebar import render_sidebar

st.set_page_config(
    page_title="Sales Return History",
    page_icon="📜",
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

st.title("📜 Sales Return History")

token = st.session_state.get("token") or st.session_state.get("access_token")

if not token:
    st.warning("Please login first.")
    if st.button("Go to Login / Main Page"):
        st.switch_page("app.py")
    st.stop()

invoice_id = st.session_state.get("selected_return_invoice")

if not invoice_id:
    st.warning("No invoice selected.")
    if st.button("⬅️ Back to Sales Returns"):
        st.switch_page("pages/sales_return.py")
    st.stop()

if st.button("⬅️ Back to Sales Returns"):
    st.switch_page("pages/sales_return.py")

st.divider()

# ==================================================
# LOAD RETURNS FOR INVOICE
# ==================================================
response = get(
    f"/sales-returns/invoice/{invoice_id}",
    token=token
)

if response.status_code != 200:
    st.error("Failed to load return history.")
    st.stop()

returns = response.json()

if not returns:
    st.info("No returns found for this invoice.")
    st.stop()

st.subheader(f"Returns for Invoice #{invoice_id}")

for ret in returns:
    return_id = ret.get("return_id")
    status = ret.get("status")
    total_amount = ret.get("total_amount", 0.0)
    created_at = ret.get("created_at", "")

    with st.container():
        col1, col2, col3, col4 = st.columns([2, 2, 2, 2])

        with col1:
            st.write(f"**Return ID:** #{return_id}")
            st.caption(f"Date: {created_at}")

        with col2:
            st.write(f"**Amount:** {float(total_amount):.2f} JOD")

        with col3:
            if status == "COMPLETED":
                st.success(f"Status: {status}")
            elif status == "CANCELLED":
                st.error(f"Status: {status}")
            else:
                st.warning(f"Status: {status}")

        with col4:
            # زر الإلغاء يظهر فقط إذا كانت الحالة COMPLETED
            if status == "COMPLETED":
                if st.button("❌ Cancel Return", key=f"cancel_{return_id}", type="secondary", use_container_width=True):
                    
                    # استدعاء الـ API الخاص بالإلغاء مع تمرير التوكن صراحة
                    cancel_response = put(
                        f"/sales-returns/{return_id}/cancel",
                        {},
                        token=token
                    )

                    if cancel_response.status_code == 200:
                        st.success(f"✅ Sales Return #{return_id} cancelled successfully.")
                        st.rerun()
                    else:
                        try:
                            error_msg = cancel_response.json()["error"]
                        except Exception:
                            error_msg = cancel_response.text
                        st.error(f"Failed to cancel: {error_msg}")

        st.divider()