import streamlit as st
from services.auth_service import authenticate_user

def render():
    st.title("Welcome to Cardify Marketing")
    st.subheader("Please Login")
    
    with st.container(border=True):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        
        if st.button("Login", icon=":material/login:"):
            if not username or not password:
                st.error("Please enter both username and password")
                return
                
            with st.spinner("Authenticating..."):
                result = authenticate_user(username, password)
                
            if "error" in result:
                st.error(result["error"])
            else:
                st.session_state['user'] = result["user"]
                st.success("Login successful!")
                st.rerun()
