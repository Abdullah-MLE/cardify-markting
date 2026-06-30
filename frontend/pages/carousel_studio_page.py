"""Carousel Studio Page."""
import streamlit as st
from frontend.components.guards import require_company

def render():
    st.title("Carousel Studio")
    
    company_id = require_company()
    if not company_id:
        return
        
    st.info(
        "Carousel creation is now fully integrated into the **Create Content** flow. "
        "Simply type 'Carousel' in the notes or select it when generating a daily plan.",
        icon=":material/info:"
    )

    if st.button("Go to Create Content", icon=":material/add_circle:", type="primary"):
        st.switch_page(st.session_state['pages_dict']['create_content'])

render()
