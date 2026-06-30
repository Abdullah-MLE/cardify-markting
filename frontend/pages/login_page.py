"""Login Page."""
import streamlit as st
from frontend.api_client import APIClient

def render():
    st.title("Cardify Marketing Login")
    
    with st.container(border=True):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        
        if st.button("Login", type="primary", width="stretch"):
            if username and password:
                with st.spinner("Authenticating..."):
                    result = APIClient.login(username, password)
                    
                    if "error" in result:
                        st.error(result["error"])
                    else:
                        st.session_state["user"] = result["user"]
                        st.success("Login successful!")
                        st.rerun()
            else:
                st.error("Please enter both username and password")

render()
