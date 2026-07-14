"""Login Page."""
import streamlit as st
from libs.SupabaseClient.supabase_client import SupabaseManager

def render():
    st.title("Cardify Marketing Login")
    
    with st.container(border=True):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        
        if st.button("Login", type="primary", use_container_width=True):
            if username and password:
                with st.spinner("Authenticating..."):
                    client = SupabaseManager.get_client()
                    if not client:
                        st.error("Database not connected")
                        return
                    
                    try:
                        response = client.table("users").select("*").eq("username", username).execute()
                        users = response.data
                        if not users:
                            st.error("User not found")
                        else:
                            user = users[0]
                            if user["password"] == password:
                                st.session_state["user"] = user
                                st.success("Login successful!")
                                st.rerun()
                            else:
                                st.error("Invalid password")
                    except Exception as e:
                        st.error(f"Database error: {str(e)}")
            else:
                st.error("Please enter both username and password")

render()

