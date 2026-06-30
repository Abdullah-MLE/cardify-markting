"""Data Gathering Page."""
import streamlit as st
from frontend.api_client import APIClient

def render():
    st.title("Data Gathering")
    
    comp_id = st.session_state.get('data_gathering_company_id')
    if not comp_id:
        st.error("No company selected for data gathering.")
        if st.button("Go to Admin Dashboard"):
            st.switch_page(st.session_state['pages_dict']['admin_dashboard'])
        return
        
    comp = APIClient.get_company(comp_id)
    if not comp:
        st.error("Company not found.")
        return
        
    st.subheader(f"Gather Data for {comp.get('company_name')}")
    
    tab1, tab2 = st.tabs(["Web Scraping", "Manual / AI Edit"])
    
    with tab1:
        st.write("Extract company details from their website.")
        url = st.text_input("Website URL", value=comp.get("website_url", ""))
        
        if st.button("Scrape & Analyze", type="primary"):
            if not url:
                st.error("Please enter a URL.")
            else:
                with st.spinner("Scraping website..."):
                    res = APIClient.scrape_company(url, comp_id)
                    if res and res.get("success"):
                        st.success("Company profile updated successfully!")
                        st.rerun()
                    else:
                        st.error("Failed to scrape or update company.")
                            
    with tab2:
        st.write("Edit company details manually or via AI instructions.")
        
        with st.form("manual_edit_form"):
            notes = st.text_area("AI Instructions (e.g., 'Change tone to professional')")
            
            st.json(comp)
            
            if st.form_submit_button("Update via AI", type="primary"):
                if not notes:
                    st.error("Please provide instructions.")
                else:
                    with st.spinner("Updating..."):
                        res = APIClient.edit_company_profile(comp, notes, comp_id)
                        if res and res.get("success"):
                            st.success("Profile updated!")
                            st.rerun()
                        else:
                            st.error("Failed to update profile.")

render()
