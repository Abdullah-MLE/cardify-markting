"""Schedule Page (Calendar)."""
import streamlit as st
import datetime
from frontend.api_client import APIClient
from frontend.components.guards import require_company
from frontend.components.calendar_view import render_calendar_view

def render():
    st.title("Content Schedule")
    
    company_id = require_company()
    if not company_id:
        return
        
    if 'view_date' not in st.session_state:
        st.session_state.view_date = datetime.date.today()
        
    all_content = APIClient.get_scheduled_content(company_id)
    
    render_calendar_view(all_content, company_id)

render()
