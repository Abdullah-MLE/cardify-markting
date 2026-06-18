import streamlit as st
import datetime
from services import db_services
from components import campaign_item_card

def render():
    st.title("Day Details")
    user = st.session_state.get('user', {})
    
    if user.get('role') == 'admin' and not user.get('company_id'):
        st.info("Admins must select a company to view details.")
        if st.button("Go to Companies Dashboard", icon=":material/arrow_forward:"):
            st.switch_page(st.session_state['pages_dict']['admin_dashboard'])
        return
        
    # Get default date from session state or use today
    if "selected_date" not in st.session_state:
        st.session_state.selected_date = datetime.date.today()
        
    # Ensure it's a date object
    if isinstance(st.session_state.selected_date, str):
        try:
            st.session_state.selected_date = datetime.date.fromisoformat(st.session_state.selected_date)
        except ValueError:
            st.session_state.selected_date = datetime.date.today()
            
    date = st.date_input("Select Date", value=st.session_state.selected_date)
    st.session_state.selected_date = date
    
    content = db_services.get_scheduled_content(user.get('company_id'))
    
    # Filter for this date
    day_content = [c for c in content if c.get('publish_date') == str(date)]
    
    if not day_content:
        if date >= datetime.date.today():
            st.info("No scheduled posts for this date.")
            if st.button("Create Content", icon=":material/add_circle:"):
                st.switch_page(st.session_state['pages_dict']['create_content'])
        else:
            st.info("No posts were scheduled for this date.")
        return
        
    # Fetch campaigns to pass to the card renderer
    campaigns = db_services.get_campaigns(user.get('company_id'))
    
    st.write(f"### Posts for {date}:")
    for item in day_content:
        campaign_item_card.render_item_card(item, campaigns)
