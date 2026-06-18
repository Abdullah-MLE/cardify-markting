import streamlit as st
from datetime import datetime
from services import db_services
from components import calendar_view

def render():
    user = st.session_state.get('user', {})
    
    if user.get('role') == 'admin' and not user.get('company_id'):
        st.title("Content Schedule")
        st.info("Admins must select a company to view the schedule.")
        if st.button("Go to Companies Dashboard", icon=":material/arrow_forward:"):
            st.switch_page(st.session_state['pages_dict']['admin_dashboard'])
        return
        
    # Initialize view_date in session state
    if "view_date" not in st.session_state:
        st.session_state.view_date = datetime.now().date()
        
    # Header & Refresh column layout
    col_title, col_refresh = st.columns([5, 1])
    with col_title:
        st.title("📅 Content Schedule")
    with col_refresh:
        if st.button("🔄 Refresh", help="Refresh data from the database"):
            st.rerun()
            
    content = db_services.get_scheduled_content(user.get('company_id'))
    calendar_view.render_calendar_view(content, user.get('company_id'))
