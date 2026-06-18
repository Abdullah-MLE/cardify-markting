import streamlit as st
from services import db_services

def render():
    st.title("Data Gathering")
    user = st.session_state.get('user', {})
    
    if user.get('role') == 'admin' and not user.get('company_id'):
        st.info("Admins must select a company to edit data.")
        if st.button("Go to Companies Dashboard", icon=":material/arrow_forward:"):
            st.switch_page(st.session_state['pages_dict']['admin_dashboard'])
        return
        
    company = db_services.get_company_data(user.get('company_id'))
    
    if not company:
        st.error("Company not found or you don't have access.")
        return
    
    with st.form("company_form"):
        st.subheader("Company Context (Used for AI Logic)")
        name = st.text_input("Company Name", value=company.get('company_name', ''))
        industry = st.text_input("Industry", value=company.get('industry', ''))
        website = st.text_input("Website", value=company.get('website_url', ''))
        desc = st.text_area("Description", value=company.get('description', ''))
        
        st.subheader("AI Campaign Settings")
        mission = st.text_area("Mission & Goal", value=company.get('mission_and_goal', ''))
        tone = st.text_input("Brand Tone", value=company.get('brand_tone', ''))
        audience = st.text_input("Target Audience", value=company.get('target_audience', ''))
        locale = st.text_input("Language & Locale", value=company.get('language_and_locale', ''))
        
        if st.form_submit_button("Save Details"):
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
            res = db_services.update_company(company['id'], update_data)
            if res is not None:
                st.success("Company details saved to database!")
            else:
                st.error("Failed to save to database.")
