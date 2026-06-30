"""Create Content Page."""
import streamlit as st
import datetime
from frontend.api_client import APIClient
from frontend.components.guards import require_company

def render():
    st.title("Create Content")
    
    company_id = require_company()
    if not company_id:
        return
        
    st.write("Generate a new post, story, or carousel using AI.")
    
    default_date = st.session_state.get('create_content_date', datetime.date.today())
    
    with st.form("create_content_form"):
        col1, col2 = st.columns(2)
        with col1:
            publish_date = st.date_input("Publish Date", value=default_date)
        with col2:
            publish_time = st.text_input("Publish Time (HH:MM)", value="12:00")
            
        headline = st.text_input("Headline or Main Idea", placeholder="E.g., 5 Tips for Summer Skincare")
        notes = st.text_area("Instructions / Notes", placeholder="Specify if it's a carousel, or if you want a specific tone...")
        
        campaigns = APIClient.get_campaigns(company_id)
        camp_options = {c['id']: c['plan_title'] for c in campaigns}
        camp_options[None] = "Standalone (No Campaign)"
        selected_campaign = st.selectbox(
            "Link to Campaign", 
            options=list(camp_options.keys()), 
            format_func=lambda x: camp_options[x]
        )
        
        submit = st.form_submit_button("Generate Content", type="primary", width="stretch")
        
        if submit:
            if not headline:
                st.error("Headline/Idea is required.")
            else:
                with st.spinner("Generating text content..."):
                    content_obj = APIClient.create_single_post(
                        company_id, 
                        headline, 
                        notes,
                        campaign_id=selected_campaign,
                        publish_date=publish_date,
                        publish_time=publish_time
                    )
                    if content_obj and "id" in content_obj:
                        st.success("Content generated successfully!")
                        st.session_state.selected_content_id = content_obj['id']
                        st.switch_page(st.session_state['pages_dict']['content_details'])
                    else:
                        st.error("Failed to generate content.")

render()
