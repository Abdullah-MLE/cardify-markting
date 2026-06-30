import streamlit as st

st.set_page_config(
    page_title="Cardify Marketing",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize Session State
if 'user' not in st.session_state:
    st.session_state['user'] = None

# Define Pages
pages = {
    "login": st.Page("frontend/pages/login_page.py", title="Login", icon=":material/login:"),
    "admin_dashboard": st.Page("frontend/pages/admin_dashboard_page.py", title="Admin Dashboard", icon=":material/admin_panel_settings:"),
    "data_gathering": st.Page("frontend/pages/data_gathering_page.py", title="Data Gathering", icon=":material/dataset:"),
    "campaigns": st.Page("frontend/pages/campaigns_page.py", title="Campaigns", icon=":material/campaign:"),
    "schedule": st.Page("frontend/pages/schedule_page.py", title="Schedule", icon=":material/calendar_month:"),
    "day_details": st.Page("frontend/pages/day_details_page.py", title="Day Details", icon=":material/view_day:"),
    "create_content": st.Page("frontend/pages/create_content_page.py", title="Create Content", icon=":material/add_box:"),
    "content_details": st.Page("frontend/pages/content_details_page.py", title="Content Details", icon=":material/article:"),
    "templates": st.Page("frontend/pages/template_page.py", title="Templates", icon=":material/dashboard_customize:"),
    "edit_template": st.Page("frontend/pages/edit_template_page.py", title="Edit Template", icon=":material/edit:"),
    "image_gen": st.Page("frontend/pages/image_gen_page.py", title="Standalone Image", icon=":material/image:"),
    "carousel_studio": st.Page("frontend/pages/carousel_studio_page.py", title="Carousel Studio", icon=":material/view_carousel:"),
}

# Keep dictionary for easy switching
st.session_state['pages_dict'] = pages

# Navigation Logic
if not st.session_state.get('user'):
    pg = st.navigation([pages["login"]])
else:
    user = st.session_state['user']
    role = user.get('role', 'user')
    company_id = user.get('company_id')
    
    # Setup Navigation Menu based on Role
    nav_structure = {}
    
    if role == 'admin':
        nav_structure["Admin"] = [pages["admin_dashboard"]]
        
    nav_structure["Marketing"] = [pages["campaigns"], pages["schedule"], pages["create_content"]]
    nav_structure["Assets"] = [pages["templates"], pages["image_gen"], pages["carousel_studio"]]
    
    # Hidden pages (accessible via st.switch_page but not in sidebar)
    hidden_pages = [
        pages["day_details"], 
        pages["content_details"], 
        pages["edit_template"],
        pages["data_gathering"]
    ]
    
    pg = st.navigation(nav_structure | {"Hidden": hidden_pages})
    
    # Sidebar Info
    with st.sidebar:
        st.divider()
        st.markdown(f"**Logged in as:** {user.get('username')}")
        if role == 'admin':
            st.caption("Admin Mode")
            
        if company_id:
            from frontend.api_client import APIClient
            comp = APIClient.get_company(company_id)
            if comp:
                st.info(f"**Active Company:**\n{comp.get('company_name')}")
            else:
                st.warning("Selected company not found.")
                
        if st.button("Logout", use_container_width=True):
            st.session_state.clear()
            st.rerun()

# Run the page
pg.run()
