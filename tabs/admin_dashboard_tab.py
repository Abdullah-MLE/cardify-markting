import streamlit as st
import time
from services import db_services
from services.ai_service import get_ai_service
from schemas.ai_models import CompanyExtraction

@st.dialog("Add New Company")
def add_company_dialog():
    tab1, tab2 = st.tabs(["🤖 AI Extraction", "✍️ Manual Entry"])
    
    with tab1:
        st.write("Extract company details from a website or text description.")
        source_text = st.text_area("Website URL or Company Description")
        
        if st.button("Extract with AI", type="primary", key="ai_extract_btn"):
            if not source_text:
                st.error("Please provide a URL or description.")
            else:
                with st.spinner("Analyzing with AI..."):
                    ai = get_ai_service()
                    context = {"source_text": source_text}
                    result = ai.execute_text_skill("analyze_company", context=context, response_schema=CompanyExtraction)
                    
                    if result.get("success"):
                        data = result["content"]
                        if hasattr(data, 'model_dump'):
                            data = data.model_dump()
                        st.session_state['ai_extracted_company'] = data
                        st.rerun()
                    else:
                        st.error(f"Failed to extract details: {result.get('error')}")
                        
        if 'ai_extracted_company' in st.session_state:
            data = st.session_state['ai_extracted_company']
            st.success("Extraction complete! Review and save below.")
            with st.form("ai_save_comp_form"):
                name = st.text_input("Company Name*", value=data.get('company_name') or '')
                industry = st.text_input("Industry", value=data.get('industry') or '')
                website = st.text_input("Website URL", value=data.get('website_url') or '')
                desc = st.text_area("Description", value=data.get('description') or '')
                
                st.subheader("Brand / AI Settings")
                mission = st.text_area("Mission & Goal", value=data.get('mission_and_goal') or '')
                tone = st.text_input("Brand Tone", value=data.get('brand_tone') or '')
                audience = st.text_input("Target Audience", value=data.get('target_audience') or '')
                locale = st.text_input("Language & Locale", value=data.get('language_and_locale') or 'ar-EG')
                
                if st.form_submit_button("Save Company"):
                    if not name:
                        st.error("Company Name is required.")
                    else:
                        company_data = {
                            "company_name": name,
                            "industry": industry,
                            "website_url": website,
                            "description": desc,
                            "mission_and_goal": mission,
                            "brand_tone": tone,
                            "target_audience": audience,
                            "language_and_locale": locale
                        }
                        res = db_services.create_company(company_data)
                        if res:
                            del st.session_state['ai_extracted_company']
                            st.success("Company created successfully!")
                            time.sleep(0.5)
                            st.rerun()
                        else:
                            st.error("Failed to create company.")

    with tab2:
        with st.form("manual_comp_form"):
            st.subheader("Company Details")
            name = st.text_input("Company Name*")
            industry = st.text_input("Industry")
            website = st.text_input("Website URL")
            desc = st.text_area("Description")
            
            st.subheader("Brand / AI Settings")
            mission = st.text_area("Mission & Goal")
            tone = st.text_input("Brand Tone")
            audience = st.text_input("Target Audience")
            locale = st.text_input("Language & Locale", value="ar-EG")
            
            if st.form_submit_button("Save Company"):
                if not name:
                    st.error("Company Name is required.")
                else:
                    company_data = {
                        "company_name": name,
                        "industry": industry,
                        "website_url": website,
                        "description": desc,
                        "mission_and_goal": mission,
                        "brand_tone": tone,
                        "target_audience": audience,
                        "language_and_locale": locale
                    }
                    res = db_services.create_company(company_data)
                    if res:
                        st.success("Company created successfully!")
                        time.sleep(0.5)
                        st.rerun()
                    else:
                        st.error("Failed to create company.")


@st.dialog("Edit Company")
def edit_company_dialog(comp):
    st.subheader(f"Edit {comp.get('company_name')}")
    name = st.text_input("Company Name*", value=comp.get('company_name', ''))
    industry = st.text_input("Industry", value=comp.get('industry', ''))
    website = st.text_input("Website URL", value=comp.get('website_url', ''))
    desc = st.text_area("Description", value=comp.get('description', ''))
    
    st.subheader("Brand / AI Settings")
    mission = st.text_area("Mission & Goal", value=comp.get('mission_and_goal', ''))
    tone = st.text_input("Brand Tone", value=comp.get('brand_tone', ''))
    audience = st.text_input("Target Audience", value=comp.get('target_audience', ''))
    locale = st.text_input("Language & Locale", value=comp.get('language_and_locale', ''))
    
    if st.button("Update Company", type="primary"):
        if not name:
            st.error("Company Name is required.")
            return
        
        update_data = {
            "company_name": name,
            "industry": industry,
            "website_url": website,
            "description": desc,
            "mission_and_goal": mission,
            "brand_tone": tone,
            "target_audience": audience,
            "language_and_locale": locale
        }
        res = db_services.update_company(comp['id'], update_data)
        if res is not None:
            st.success("Company updated successfully!")
            time.sleep(0.5)
            st.rerun()
        else:
            st.error("Failed to update company.")

@st.dialog("Manage Users")
def manage_users_dialog(comp):
    st.subheader(f"Users for {comp.get('company_name')}")
    
    users = db_services.get_company_users(comp['id'])
    if not users:
        st.info("No users registered for this company.")
    else:
        for u in users:
            st.text(f"👤 {u['username']} ({u['role']})")
    
    st.divider()
    st.subheader("Add New User")
    username = st.text_input("Username*")
    password = st.text_input("Password*", type="password")
    role = st.selectbox("Role", ["company_user", "admin"])
    
    if st.button("Create User", type="primary"):
        if not username or not password:
            st.error("Username and password are required.")
            return
        
        user_data = {
            "username": username,
            "password": password,
            "role": role,
            "company_id": comp['id']
        }
        res = db_services.create_user(user_data)
        if res:
            st.success(f"User '{username}' created successfully!")
            time.sleep(0.5)
            st.rerun()
        else:
            st.error("Failed to create user (username might already be taken).")

@st.dialog("Delete Company")
def delete_company_dialog(comp):
    st.warning(f"Are you sure you want to delete '{comp.get('company_name')}'? This action cannot be undone and will delete all associated users, campaigns, templates, and content.")
    confirm_name = st.text_input("Type the company name to confirm:")
    
    if st.button("Delete Permanently", type="primary"):
        if confirm_name != comp.get('company_name'):
            st.error("Company name does not match.")
            return
            
        with st.spinner("Deleting company..."):
            res = db_services.delete_company(comp['id'])
            if res:
                # If deleted company was the active one, clear selection
                user = st.session_state.get('user', {})
                if user.get('company_id') == comp['id']:
                    st.session_state['user']['company_id'] = None
                    st.session_state['user']['company_name'] = None
                st.success("Company deleted successfully!")
                time.sleep(0.5)
                st.rerun()
            else:
                st.error("Failed to delete company.")

def render():
    st.title("Admin Dashboard - Companies")
    
    user = st.session_state.get('user', {})
    if user.get('role') != 'admin':
        st.error("Unauthorized access")
        return
        
    companies = db_services.get_companies()
    
    with st.container():
        if st.button("Add New Company", icon=":material/add_business:", type="primary"):
            add_company_dialog()
        
    if not companies:
        st.info("No companies found in the database.")
        return
        
    current_company_id = user.get('company_id')
    
    for comp in companies:
        with st.container(border=True):
            cols = st.columns([3, 1])
            with cols[0]:
                st.subheader(comp.get('company_name', 'Unnamed'))
                st.write(f"**Industry:** {comp.get('industry', 'N/A')}")
                if comp.get('website_url'):
                    st.write(f"**Website:** {comp.get('website_url')}")
                if comp.get('description'):
                    st.write(f"**Description:** {comp.get('description')}")
            
            with cols[1]:
                # Edit Company
                if st.button("Edit", key=f"edit_comp_{comp['id']}", icon=":material/edit:"):
                    edit_company_dialog(comp)
                    
                # Manage Users
                if st.button("Manage Users", key=f"users_comp_{comp['id']}", icon=":material/group:"):
                    manage_users_dialog(comp)
                
                # Delete Company
                if st.button("Delete", key=f"del_comp_{comp['id']}", icon=":material/delete:", type="secondary"):
                    delete_company_dialog(comp)
                
                # Select Company
                is_selected = (current_company_id == comp['id'])
                if is_selected:
                    st.success("Selected", icon="✅")
                    if st.button("Deselect", key=f"desel_comp_{comp['id']}", type="secondary"):
                        st.session_state['user']['company_id'] = None
                        st.session_state['user']['company_name'] = None
                        st.rerun()
                else:
                    if st.button("Select Company", key=f"sel_comp_{comp['id']}", type="secondary"):
                        st.session_state['user']['company_id'] = comp['id']
                        st.session_state['user']['company_name'] = comp.get('company_name')
                        st.success(f"Selected {comp.get('company_name')}!")
                        time.sleep(0.5)
                        st.rerun()
