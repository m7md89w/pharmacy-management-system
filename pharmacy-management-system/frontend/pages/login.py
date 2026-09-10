import streamlit as st
from services.auth import login_user, is_authenticated
from components.sidebar import render_sidebar

# ==================================================
# PAGE CONFIGURATION
# ==================================================
st.set_page_config(
    page_title="Login - Pharmacy ERP",
    page_icon="🔑",
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

# إذا كان المستخدم مسجلاً دخوله بالفعل، عرض القائمة الجانبية وتوجيهه بسلاسة
if is_authenticated():
    render_sidebar()
    st.success("You are already logged in!")
    if st.button("Go to Dashboard"):
        st.switch_page("app.py")
    st.stop()

# ==================================================
# LOGIN FORM UI (إذا لم يكن مسجل دخول، نخفي القائمة الجانبية الخاصة بالتنقل ونعرض شاشة الدخول)
# ==================================================
st.markdown(
    """
    <style>
        [data-testid="stSidebar"] {
            display: none;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    st.title("💊 Pharmacy ERP")
    st.subheader("System Login")

    with st.form(key="independent_login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        
        submit_btn = st.form_submit_button(
            "Login",
            use_container_width=True,
            type="primary"
        )

        if submit_btn:
            if not username or not password:
                st.warning("Please enter both username and password.")
            else:
                with st.spinner("Authenticating..."):
                    # استدعاء دالة الخدمة للمصادقة وتوحيد تخزين التوكن
                    success, message = login_user(username, password)
                    
                    if success:
                        token_val = st.session_state.get("token") or st.session_state.get("access_token")
                        if token_val:
                            st.session_state["token"] = token_val
                            st.session_state["access_token"] = token_val

                        st.success("Login successful! Redirecting...")
                        st.switch_page("app.py")
                    else:
                        st.error(message)