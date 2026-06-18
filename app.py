import streamlit as st

# MUST be the first Streamlit command
st.set_page_config(
    page_title="Cardify Marketing",
    page_icon=":material/campaign:",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 1. State Initialization
st.session_state.setdefault('user', None)

# Import tabs
from tabs import (
    login_tab,
    admin_dashboard_tab,
    schedule_tab,
    day_details_tab,
    campaigns_tab,
    data_gathering_tab,
    template_tab,
    image_gen_tab,
    carousel_studio_tab,
    create_content_tab,
    edit_content_tab
)

def main():
    # If not logged in, show only the login page
    if st.session_state.get('user') is None:
        login_pg = st.navigation([st.Page(login_tab.render, title="Login", icon=":material/login:", url_path="login")])
        login_pg.run()
        return

    # If logged in, set up the sidebar and navigation
    st.sidebar.title("Cardify Marketing")
    
    user = st.session_state['user']
    role = user.get('role', 'company_user')
    company_name = user.get('company_name')
    company_id = user.get('company_id')
    
    st.sidebar.caption(f"Logged in as: {user['username']} ({role})")
    
    if company_id:
        st.sidebar.subheader(f":material/business: {company_name or 'Selected Company'}")
        if role == 'admin':
            if st.sidebar.button("Deselect Company", icon=":material/close:", key="sidebar_deselect"):
                st.session_state['user']['company_id'] = None
                st.session_state['user']['company_name'] = None
                st.rerun()
                
    st.sidebar.divider()
    
    if st.sidebar.button("Logout", icon=":material/logout:"):
        st.session_state['user'] = None
        st.rerun()
    
    # Initialize pages dictionary
    pages = {}
    
    # Pre-create all Page objects to allow safe programmatic navigation
    page_admin_dashboard = st.Page(admin_dashboard_tab.render, title="Companies Dashboard", icon=":material/admin_panel_settings:", url_path="admin_dashboard")
    page_schedule = st.Page(schedule_tab.render, title="Schedule", icon=":material/calendar_month:", url_path="schedule")
    page_day_details = st.Page(day_details_tab.render, title="Day Details", icon=":material/view_day:", url_path="day_details")
    page_create_content = st.Page(create_content_tab.render, title="Create Content", icon=":material/add_circle:", url_path="create_content")
    page_edit_content = st.Page(edit_content_tab.render, title="Edit Content", icon=":material/edit_note:", url_path="edit_content")
    page_campaigns = st.Page(campaigns_tab.render, title="Campaigns", icon=":material/rocket_launch:", url_path="campaigns")
    page_image_gen = st.Page(image_gen_tab.render, title="Image Gen", icon=":material/image:", url_path="image_gen")
    page_carousel_studio = st.Page(carousel_studio_tab.render, title="Carousel Studio", icon=":material/view_carousel:", url_path="carousel_studio")
    page_templates = st.Page(template_tab.render, title="Templates", icon=":material/design_services:", url_path="templates")
    page_data_gathering = st.Page(data_gathering_tab.render, title="Data Gathering", icon=":material/database:", url_path="data_gathering")
    
    st.session_state['pages_dict'] = {
        'admin_dashboard': page_admin_dashboard,
        'schedule': page_schedule,
        'day_details': page_day_details,
        'create_content': page_create_content,
        'edit_content': page_edit_content,
        'campaigns': page_campaigns,
        'image_gen': page_image_gen,
        'carousel_studio': page_carousel_studio,
        'templates': page_templates,
        'data_gathering': page_data_gathering
    }
    
    if role == 'admin':
        pages["Admin"] = [page_admin_dashboard]
        
    pages["Planner"] = [
        page_schedule,
        page_day_details,
        page_create_content,
        page_edit_content,
    ]
    pages["Creation"] = [
        page_campaigns,
    ]
    pages["Studio"] = [
        page_image_gen,
        page_carousel_studio,
        page_templates,
    ]
    pages["Settings"] = [
        page_data_gathering,
    ]
    
    pg = st.navigation(pages)
    pg.run()


if __name__ == "__main__":
    main()
