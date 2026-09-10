import streamlit as st
from services.api_client import post

def login_user(username, password):
    """
    Sends credentials to the backend API to authenticate the user.
    If successful, stores the token and user data in Streamlit's session state.
    """
    payload = {
        "username": username,
        "password": password
    }
    
    try:
        response = post("/auth/login", data=payload)
        
        if response.status_code == 200:
            data = response.json()
            
            # التقاط التتوكن بأمان سواء أتى باسم access_token أو token لضمان الاستقرار
            token_val = data.get("access_token") or data.get("token")
            
            # تخزين التفاصيل في الجلسة بالمفاتيح الشائعة لجميع الصفحات
            st.session_state["token"] = token_val
            st.session_state["access_token"] = token_val
            st.session_state["user"] = data.get("user")
            
            return True, "Login successful"
        else:
            try:
                error_msg = response.json().get("error", "Invalid credentials provided.")
            except Exception:
                error_msg = "Invalid credentials provided."
                
            return False, error_msg
            
    except Exception as e:
        return False, f"Connection error: {str(e)}"

def logout_user():
    """
    Clears all stored session data, effectively logging the user out.
    """
    for key in list(st.session_state.keys()):
        del st.session_state[key]

def is_authenticated():
    """
    Helper function to check if a user is currently logged in.
    """
    return (
        ("token" in st.session_state and st.session_state["token"]) or 
        ("access_token" in st.session_state and st.session_state["access_token"])
    ) and "user" in st.session_state