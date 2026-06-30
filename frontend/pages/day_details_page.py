"""Day Details Page."""
import streamlit as st
import datetime
from frontend.api_client import APIClient
from frontend.components.guards import require_company
from frontend.components.content_card import render_mini_card

def render():
    company_id = require_company()
    if not company_id:
        return
        
    if 'selected_date' not in st.session_state:
        st.error("No date selected. Please select a date from the Schedule.")
        if st.button("Go to Schedule"):
            st.switch_page(st.session_state['pages_dict']['schedule'])
        return
        
    selected_date = st.session_state.selected_date
    st.title(f"Details for {selected_date}")
    
    col1, col2 = st.columns([4, 1])
    with col1:
        if st.button("← Back to Schedule"):
            st.switch_page(st.session_state['pages_dict']['schedule'])
    with col2:
        if st.button("New Post", type="primary", icon=":material/add:"):
            st.session_state.create_content_date = selected_date
            st.switch_page(st.session_state['pages_dict']['create_content'])
            
    st.divider()
    
    all_content = APIClient.get_scheduled_content(company_id)
    day_content = [c for c in all_content if c.get('publish_date') == str(selected_date)]
    
    if not day_content:
        st.info("No content scheduled for this day.")
        return
        
    day_content.sort(key=lambda x: x.get('publish_time', ''))
    
    for item in day_content:
        render_mini_card(item, on_view_key_suffix=f"day_{selected_date}")

render()
